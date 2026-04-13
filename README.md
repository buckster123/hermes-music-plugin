# 🎵 Hermes Music Plugin

Music generation plugin for [Hermes Agent](https://github.com/NousResearch/hermes-agent) — powered by Suno AI.

Generate music, compose from MIDI, search & curate your library — all from your agent's toolbox.

## Features

- **AI Music Generation** — Generate songs via Suno AI with style tags, prompts, and model selection (V3.5–V5)
- **MIDI Composition** — Create MIDI files from note names/numbers, then use them as references for AI generation
- **Music Library** — Browse, search, favorite, and track play counts across all generated songs
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

## Setup

Add your Suno API key to `~/.hermes/.env`:

```
SUNO_API_KEY=your_key_here
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
| `music_result` | Get completed audio file |
| `music_list` | List recent generation tasks |
| `music_favorite` | Toggle favorite on a song |
| `music_library` | Browse library with filters |
| `music_search` | Search by title, prompt, or style |
| `music_play` | Mark played, get file path |
| `midi_create` | Create MIDI from notes (no API key needed) |
| `music_compose` | Generate music from MIDI reference |

## Examples

```
# In a Hermes chat session:
"Generate an ambient electronic track for coding"
"Create a MIDI melody with C4 E4 G4 C5 and compose it into jazz piano"
"Search my music library for ambient tracks"
"Favorite that last track"
```

## Data Storage

All data lives in `~/.hermes/music/`:
```
~/.hermes/music/
├── audio/          # Downloaded MP3 files
├── midi/           # Generated MIDI files
└── tasks.json      # Task state & library metadata
```

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
