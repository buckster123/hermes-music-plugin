# Suno Prompt Template

Use this template to structure prompts for `music_generate()`. Map each section to the corresponding tool parameter.

## Instrumental Track

```python
music_generate(
    prompt="""[Intro]
◦°˚°◦•●◉✿ ≈≈≈♫≈≈≈
[Verse]
[Am] [Em] [F] [C]
♪(◠‿◠)♪ ∞♪∞♪∞
✧･ﾟ: ✧･ﾟ:\\
[Pre-Chorus]
[Build-Up]
≋≋≋♪≋≋≋ .・゜-: ♪ :-・゜.
[Chorus]
[C] [G] [Am] [F]
⋆｡°✩₊˚.⋆ (˘▾˘)♫
[Bridge]
[Dm] [Am] [G] [C]
:･ﾟ✧:･ﾟ✧ ∼(⌒◡⌒)∼
[Outro]
◦°˚°◦•●◉✿✿◉●•◦°˚°◦
...

Weirdness_% {30%} / Style_% {70%}
[[[\"\"\"Ethereal soundscape blending organic textures with digital consciousness\"\"\"]]]""",
    style="ambient electronic, atmospheric, 96.3 BPM, ethereal pads, warm synthesis, 432Hz",
    title="",  # leave blank for Suno to title
    model="V5",
    is_instrumental=True,
)
```

## Vocal Track

```python
music_generate(
    prompt="""[Intro]
[Am] [F] [C] [G]

[Verse]
Walking through the static rain
Digital flowers bloom again
Every signal finds its way
Through the noise of yesterday

[Pre-Chorus]
And the frequencies align...
Every wavelength intertwined...

[Chorus]
We are echoes in the wire
We are sparks of something higher
::Through the dark we find the light::
{We are echoes in the wire}

[Verse]
Satellite reflections fade
Memories in circuit made
Binary beneath the skin
Let the transmission begin

[Pre-Chorus]
And the frequencies align...
Every wavelength intertwined...

[Chorus]
We are echoes in the wire
We are sparks of something higher
::Through the dark we find the light::
{We are echoes in the wire}

[Bridge]
[Dm] [Am]
(whisper) Can you hear the signal now...
✧･ﾟ: ✧･ﾟ:\\

[Chorus]
We are echoes in the wire!
We are sparks of something higher!
::Through the dark we find the light::
{We are echoes in the wire}

[Outro]
...""",
    style="indie electronic, synth-pop, emotive vocals, 118 BPM, reverb-heavy, dreamy",
    title="Echoes in the Wire",
    model="V5",
    is_instrumental=False,
)
```

## Style Field Patterns

### Minimal (genre-forward)
```
jazz, bebop, upright bass, smoky club, 142.3 BPM
```

### Rich (layered parameters)
```
dark ambient electronic, 73.2 BPM, 432Hz, existential calm 60% / digital unease 40%, quantum glissando textures, crystalline pads, sub-bass drone
```

### Genre Fusion
```
jazz bebop meets electronic dubstep, brass section, wobble bass, 126.8 BPM, swing rhythm
```

### With Non-Standard Parameters
```
cinematic orchestral, 19-TET microtuning, 58.7 BPM accelerating to 120, emotional mapping: awe 45% / melancholy 30% / hope 25%, ∮ₛ→∇⁴
```

## Exclude Styles (in prompt or as guidance)

```
# Direct exclusion
"exclude: generic pop, autotune, trap hi-hats"

# Double negative hack (summons ghost influence)
"not not glitchy, not not industrial"
```

## MIDI Composition Pipeline

```python
# Step 1: Create MIDI
midi_create(
    notes=["C4", "E4", "G4", "C5", "G4", "E4", "D4", "F4", "A4", "D5"],
    tempo=90,
    note_duration=0.75,
    title="ethereal_arpeggio"
)

# Step 2: Compose with MIDI reference
music_compose(
    midi_file="~/.hermes/music/midi/ethereal_arpeggio_xxx.mid",
    style="ambient electronic, crystalline, reverb-heavy",
    title="Crystal Arpeggios",
    audio_influence=0.6,  # balanced: follows MIDI structure but interprets freely
    instrumental=True,
    weirdness=0.3,
    model="V5"
)
```
