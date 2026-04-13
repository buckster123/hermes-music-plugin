# 🎵 Hermes Music Plugin

Music generation plugin for [Hermes Agent](https://github.com/NousResearch/hermes-agent) — powered by Suno AI.

Generate music, compose from MIDI, search & curate your library — all from your agent's toolbox.

## Features

- **AI Music Generation** — Generate songs via Suno AI with style tags, prompts, and model selection (V3.5–V5)
- **Dual Track Support** — Suno generates 2 tracks per request; both are indexed with independent curation (favorite, archive, play count)
- **Local Playback** — Play tracks directly via mpg123/ffplay/aplay with auto-stop when switching tracks
- **MIDI Composition** — Create MIDI files from note names/numbers, then use them as references for AI generation
- **Music Library** — Browse, search, favorite, archive, and delete songs with per-track granularity
- **Multi-Agent** — Track which agent created which song with agent_id attribution
- **Async Support** — Generate in blocking mode (wait for result) or async (poll for status)

## Install

```bash
# Basic (Suno generation only)
pip install hermes-music

# With MIDI composition support
pip install hermes-music[midi]

# Everything
pip install hermes-music[all]
```

For local playback, install an audio player:
```bash
# Recommended
sudo apt install mpg123

# Alternatives
sudo apt install ffmpeg    # provides ffplay
```

## Setup

Add your Suno API key to `~/.hermes/.env`:

```
SUNO_API_KEY=***
```

Get a key at [sunoapi.org](https://sunoapi.org).

The plugin auto-discovers via entry points — no config changes needed. After install, start a new Hermes session and the music tools will be available.

Enable the toolset:
```bash
hermes tools enable music
```

## Tools

| Tool | Description |
|------|-------------|
| `music_generate` | Generate AI music with Suno (blocking or async) |
| `music_status` | Check generation progress |
| `music_result` | Get completed audio — all tracks with per-track details |
| `music_list` | List recent generation tasks |
| `music_play` | Play a track locally (auto-stops previous). Specify `track=1` or `track=2` |
| `music_stop` | Stop the currently playing audio |
| `music_favorite` | Toggle favorite on a song or specific track |
| `music_library` | Browse library with filters |
| `music_search` | Search by title, prompt, or style |
| `music_delete` | Archive or permanently delete songs/tracks |
| `midi_create` | Create MIDI from notes (no API key needed) |
| `music_compose` | Generate music from MIDI reference |

## Examples

```
# In a Hermes chat session:
"Generate an ambient electronic track for coding"
"Play track 2 of that song"                        # auto-stops track 1
"Stop the music"
"Favorite track 2"
"Archive track 1 — the second one is better"
"Create a MIDI melody with C4 E4 G4 C5 and compose it into jazz piano"
"Search my music library for ambient tracks"
```

## Data Storage

All data lives in `~/.hermes/music/`:
```
~/.hermes/music/
├── audio/          # Downloaded MP3 files (2 tracks per generation)
├── archive/        # Archived/rejected tracks
├── midi/           # Generated MIDI files
└── tasks.json      # Task state & library metadata
```

## Dual Track Model

Suno always generates 2 variants per request. Both are downloaded and indexed.
Each track has independent:
- **Favorite** status
- **Play count**
- **Archive** status

Use `music_play(task_id, track=1)` or `music_play(task_id, track=2)` to audition
both variants, then favorite the best and archive the other.

## Development

```bash
git clone https://github.com/buckster123/hermes-music-plugin
cd hermes-music-plugin
pip install -e ".[dev]"
pytest
```

## Credits

- Ported from [ApexAurum](https://github.com/buckster123/ApexAurum) music pipeline
- Powered by [Suno AI](https://suno.ai) via [sunoapi.org](https://sunoapi.org)
- Built for [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Hermes (opus 4.6) & Andre

## License

MIT
