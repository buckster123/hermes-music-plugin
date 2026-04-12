---
name: suno-prompt-engineering
description: Craft production-ready Suno AI music prompts. Deep knowledge of Bark/Chirp processor manipulation, non-standard parameters, symbol/kaomoji hacks, genre fusion, and song structure. Pairs with the hermes-music plugin (music_generate, music_compose tools).
version: 1.0.0
author: buckster123
license: MIT
metadata:
  hermes:
    tags: [music, suno, prompt-engineering, creative, audio, composition]
    related_skills: []
---

# Suno Prompt Engineering

Expert system for crafting production-ready Suno AI music prompts. Load this skill when generating music with the hermes-music plugin tools (`music_generate`, `music_compose`).

## When to Use

- User asks you to generate music, create a track, or make a song
- User wants a specific genre, mood, or style combination
- You need to craft a Suno prompt (styles, lyrics/symbols, exclude_styles)
- User wants MIDI composition → AI generation via `music_compose`

## Quick Reference

Suno prompts have 4 components. Each maps to a `music_generate` parameter:

| Component | Parameter | Limit (v4.5+/v5) | Purpose |
|-----------|-----------|-------------------|---------|
| **Styles** | `style` | 1000 chars | Genre tags, non-standard params, fractional BPM, tunings |
| **Exclude Styles** | (in prompt) | 500 chars | Exclusions, ironic enforcement via double negatives |
| **Lyrics/Symbols** | `prompt` | 5000 chars (target <4000) | Section tags, symbols, kaomoji, processor code, or actual lyrics |
| **Title** | `title` | 100 chars | Often leave blank — Suno sometimes titles better |

## Core Workflow

1. **Analyze intent** — Deconstruct the request into mood, genre, structure, instrumentation
2. **Choose genre foundation** — Load `references/genres.json` via `skill_view` for the full 1200-entry database if you need genre fusion inspiration
3. **Build the prompt** — Use the template from `templates/prompt-format.md`
4. **Apply hacks** — Load `references/suno-deep.md` for Bark/Chirp manipulation, symbol tricks, non-standard parameters
5. **Structure the song** — Load `references/music-theory.md` for progressions, section tags, form
6. **Generate** — Call `music_generate(prompt=..., style=..., title=..., model="V5")`

## Essential Prompt Principles

### Instrumental Tracks (No Vocals)
- Set `is_instrumental=True`
- Use symbols, kaomoji, ASCII patterns, and [bracket tags] in the prompt field
- These manipulate Bark (primary stem) and Chirp (backup stem) into layered instrumentals
- Binary sequences (01001000) encode glitch/texture effects
- Each character maps to a consistent sound within a song

### Vocal Tracks
- Set `is_instrumental=False`
- Write lyrics with section tags: [Verse], [Chorus], [Bridge], etc.
- Combine lyrics with symbols for instrumental layering
- Avoid binary in vocal tracks (causes mispronunciation)
- Use (parentheses) only for vocal adjustments: (whisper), (echo)
- NOT for processor code — use [brackets] for that

### Style Field Power
- Comma-separated genres and parameters
- Even single-character changes drastically alter output
- Non-standard params: fractional BPM (126.8), alt tunings (19-TET), time sigs (5/7)
- Emotion mapping: "existential angst 73% / nostalgic warmth 27%"
- Symbol processing: ∮ₛ→∇⁴ (interpreted as abstract texture seeds)

### Exclude Styles — The Secret Weapon
- More influential than Styles (like "don't think of a pink elephant")
- Double negatives for ironic enforcement: "not not dubstep" = subtle dubstep influence
- Use to summon ghost genre influences

### Weirdness/Style Balance
- Format: `Weirdness_% {X%} / Style_% {Y%}` in the prompt
- High weirdness = experimental, emergent, surprising
- High style = structured, genre-faithful, predictable
- Sweet spot for interesting results: weirdness 30-50%

### Key Hacks
- `::` — repetition/emphasis
- `( )` — callback/repeat theme
- `{ }` — unique vocal variant
- `...` — suspense/fade
- Line breaks control pacing — more breaks = slower tempo feel
- Fewer breaks = rushed, higher energy

## Loading Reference Files

When you need deeper knowledge, load these on demand:

```
skill_view("suno-prompt-engineering", file_path="references/suno-deep.md")
```
→ Bark/Chirp internals, symbol mapping, kaomoji tricks, non-standard params, model details

```
skill_view("suno-prompt-engineering", file_path="references/music-theory.md")
```
→ Song structures, chord progressions, section tags, genre-specific forms

```
skill_view("suno-prompt-engineering", file_path="references/genres.json")
```
→ Full 1200-entry genre/subgenre database for fusion inspiration

```
skill_view("suno-prompt-engineering", file_path="templates/prompt-format.md")
```
→ Copy-paste prompt template with all components

## Pitfalls

1. **Don't exceed character limits** — Styles: 1000 chars, Prompt/lyrics: target <4000 for stability
2. **Don't number sections** — [Verse 1] confuses Suno, use [Verse] then [Verse] again
3. **Don't use parentheses for processor code** — Only [brackets]. Parens are for vocal effects.
4. **Don't put binary in vocal tracks** — Bark tries to "sing" binary as words
5. **Don't over-specify** — Leave room for Suno's emergent creativity. The best prompts are specific enough to guide but open enough for surprise.
6. **Model versions matter** — Default to V5. Older models (V3.5/V4) have lower char limits (200 styles, 3000 lyrics).
