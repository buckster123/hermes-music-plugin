# Hermes Music Plugin v0.2.0 — Dual Track + Playback

## Goal

Suno always generates 2 tracks per request. Currently only track 1 is indexed.
Both tracks should be first-class citizens: auditioned by the human, then kept or
archived. Also add local audio playback via mpg123/similar and a new `music_delete`
tool for cleanup.

## Current State

- `tasks.py` `run_task()` downloads ALL tracks but only stores track 1 as `task.audio_file`
- `audio_files` list is returned in the result dict but never persisted
- `library.py` / `play_song()` only knows about the single `audio_file`
- No local playback — `music_play` just returns the file path
- No delete/archive capability

## Proposed Changes

### 1. Data Model — Track-level storage (tasks.py)

**MusicTask changes:**
- Replace single `audio_file` / `audio_url` / `duration` / `clip_id` with a
  `tracks: List[TrackInfo]` field
- New `TrackInfo` dataclass:
  ```
  @dataclass
  class TrackInfo:
      file: str            # local path to mp3
      audio_url: str       # suno URL
      duration: float
      clip_id: str
      favorite: bool = False
      archived: bool = False
      play_count: int = 0
  ```
- Keep `audio_file` as a computed property → returns first non-archived track's file
  (backward compat for existing code that reads task.audio_file)
- `to_dict()` / `from_dict()` serialize the tracks list
- Migration: on `_load_tasks()`, if old-format task has `audio_file` but no `tracks`,
  auto-convert to single-track `tracks` list. Then scan disk for sibling `_2.mp3`
  file and add it as track 2 if found (catches Ghost in the Wire situation)

### 2. Download pipeline — index both tracks (tasks.py)

**`run_task()` changes:**
- Already downloads all tracks in the loop — just store them in `task.tracks`
  as `TrackInfo` objects instead of only keeping track 1
- Update progress/completion to reflect actual track count

### 3. Library & tools — track-level operations (__init__.py, library.py)

**`music_play` rework:**
- Add optional `track` param (1-indexed, default=1)
- Attempt local playback via mpg123/aplay/ffplay (in preference order)
- Run player in background (non-blocking) so the agent isn't stuck
- Return which track is playing, duration, file path

**`music_result` / `music_list` / `music_search` / `music_library`:**
- Include `tracks` array with per-track info (file, duration, archived, favorite, play_count)
- `track_count` field so the agent knows there are variants

**`music_favorite`:**
- Add optional `track` param to favorite a specific track (default: all tracks)

**New tool: `music_delete`**
- Params: `task_id`, optional `track` (1-indexed)
- If `track` specified: mark that track as `archived=True` (soft delete),
  optionally move file to `~/.hermes/music/archive/`
- If no `track`: archive the entire task (all tracks)
- Hard delete option: `permanent=True` actually removes files from disk
- Confirmation in response: show what was archived/deleted

### 4. Audio player detection (__init__.py or new player.py)

**New module `player.py`:**
```python
def find_player() -> Optional[str]:
    """Find available audio player: mpg123 > ffplay > aplay > paplay"""
    for cmd in ["mpg123", "ffplay", "aplay", "paplay"]:
        if shutil.which(cmd):
            return cmd
    return None

def play_audio(file_path: str, player: str = None) -> dict:
    """Play audio file in background, return pid for potential stop"""
    ...
```
- Player runs as subprocess, non-blocking
- Store current playback pid so we could add `music_stop` later
- If no player found: return helpful error with install instructions
  ("sudo apt install mpg123" / "brew install mpg123")

### 5. New tool: `music_stop`
- Kill the currently playing audio subprocess
- Simple but useful for "stop the music" commands

### 6. Version bump + README

- Bump to v0.2.0
- Update README with new tools and track model
- Update tool schemas for new params

## Files to Change

```
hermes_music/
├── __init__.py      # tool schemas, handlers for new params/tools
├── tasks.py         # TrackInfo dataclass, MusicTask.tracks, migration
├── library.py       # track-aware browse/search/play/favorite
├── player.py        # NEW — audio player detection + playback
└── suno.py          # no changes needed
tests/
├── test_tasks.py    # TrackInfo serialization, migration from v1 format
├── test_library.py  # track-level operations
├── test_player.py   # NEW — player detection, mock subprocess
pyproject.toml       # version bump
README.md            # updated docs
```

## Migration / Backward Compat

- Old tasks.json with `audio_file` string → auto-migrated to `tracks` list on load
- Disk scan for `_2.mp3` siblings → auto-discovered and added
- `task.audio_file` property still works (returns track 1 file)
- Existing `music_play` calls without `track` param still work (defaults to track 1)

## Testing Strategy

- Unit tests for TrackInfo serialization roundtrip
- Unit test for v1→v2 migration (old format with audio_file string)
- Unit test for disk scan finding _2.mp3 sibling
- Mock subprocess tests for player detection
- Integration: test full run_task stores both tracks

## Risks / Open Questions

- **Player on headless systems**: Pi might not have audio out configured.
  Detection should gracefully handle this.
- **Archive vs delete UX**: Soft delete (archive) by default is safer.
  Permanent delete as opt-in. Does archiving to a subfolder work for you,
  or just a boolean flag in the metadata?
- **Stop playback**: If mpg123 is running and we start another track,
  should we auto-stop the previous one? (Probably yes)
