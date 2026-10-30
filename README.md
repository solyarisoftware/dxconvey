# dxconvey

**Read DX7II SysEx, port DX7II voices to the DX7, and report what the porting cannot carry.**

> [!WARNING]
> **COMING SOON — there is no source code in this repository yet**
>
> The tool is being written. The code lands here with the **first public release,
> by December 2027**.
>
> Until then this page is the project: what the tool is for, the shape of its command
> line, and the real output of every verb. The runs below are not a mock-up and not a
> picture: they are the tool, reading a bank you can download from the link further
> down.

## What the project is

`dxconvey` is a command-line tool for Yamaha DX7II and DX7 voice files. It reads a
DX7II SysEx dump — an All-Data dump, a bank, a single voice — and it ports DX7II voices
to the DX7.

The DX7 voice is the common point between the two instruments: the project makes the
formats and their differences understandable, and it does not hide a porting behind a
file conversion. What that means in practice is in the next section — it is the reason
the tool exists, and the reason the conversion prints a register.

## What the tool is for

`dxconvey` is not a "save as DX7" that quietly leaves half a voice behind, and it does
not promise that the result sounds the same on both instruments. It does two things,
and the order matters:

- **it reads a DX7II SysEx file** — an All-Data dump, a bank, a single voice — and says
  what the file holds, what each voice is made of, and how that voice behaves;
- **it ports a DX7II voice to the DX7**, mapping as much of it as the DX7 voice format
  can hold, and **registering**, voice by voice, what it could not carry.

The porting is a translation with three outcomes, and the tool keeps them apart rather
than merging them into "converted":

| what can happen to a DX7II parameter | which ones | how it is treated |
| --- | --- | --- |
| **remap** it into the 128 bytes of a DX7 voice | the amplitude modulation sensitivity (0-7 → 0-3), the four pitch EG levels (rescaled from the range the DX7II voice declares) | rewritten by a named rule, so the voice arrives as close as the format allows |
| **declare** it, because a DX7 has no place for it | unison detune, portamento, the controller ranges, the fractional key scaling, the LFO key trigger, the performances | listed in the register beside the bank, per voice, with what is lost |
| **silence** it | — | never: nothing is dropped without a line in the register |

So the claim is not *lossless*, and it is not even *declared against silent*: it is
**remapped and declared** — the closest the DX7 format allows, under a rule that is
written down and citable, with the residue in writing. The result is not a verified
acoustic copy of the DX7II voice, and the register says so in its own words.

Two equations hold the whole of it, and the rest of this page is their consequence:

```text
DX7II voice       = DX7 voice (128 bytes) + 35 bytes a DX7 cannot hold
DX7II performance = Voice A + Voice B + performance data
```

The DX7II keeps additional parameters beside the DX7 voice data. Some settings
already fit the DX7, some need adaptation, and others cannot be stored in its
voice file. The verdict is **exact**, **close** or **lossy**, voice by voice;
carrying additional settings does not automatically mean losing them. The performance layer —
single, dual or split, the detune, the balance, the split point, the slider
assignment, the tuning — is a third object that a DX7 does not have, and it points to
its two voices by slot number: extract both voices, drop their thirty-five bytes, and
what is left is two voices **both truncated**, plus nothing of the layer.

## The command line, in three layers

The **verb** says what you want; the **kind** says which answer; the **options** say how
that answer is varied. The verb alone answers with the shortest useful answer; a kind is
a different answer — never a flag — and the options come after both, because an option
never changes the subject.

The verbs answer five kinds of question: what is in a dump (`show`, `search`), what the
machine does with no file at all (`instrument`), what a porting to the DX7 costs
(`convert`), how a software target plays a performance (`recipe`), and how the tool
itself works (`about`, `help`, `docs`). The map is a command, not this table — `help map` lists
every verb and every kind, and `--tree` draws it (the next block).

Two shortcuts, because they are the two questions asked most: `dxconvey FILE.syx` is
`show summary FILE.syx`, and `dxconvey convert FILE.syx` writes the DX7 banks in a folder
beside the dump. `converse`, a natural-language interface to instrument data, is a later
goal; it is **not** part of the current CLI.

For reading a dump, each question has one answer:

| command | what it answers |
| --- | --- |
| `show FILE` | the summary, without listing entities |
| `show all FILE` | the performance and voice lists, instrument data and SysEx messages |
| `show voice FILE` / `show performance FILE` | one filtered list of voices or performances |
| `show voice FILE --sheet` / `show performance FILE --sheet` | the selected entity's construction and stored settings |
| `show portability FILE` | what a DX7 voice file preserves, adapts or omits |

The lists have one shape, and the sheets are complete: no extra depth flag is
needed. A performance sheet describes the performance, not an appendix of voice
sheets; follow its voice slots to read those voices individually. `-q`, before
the verb, omits headings and explanations.

### The shape of the command line

Every verb and every kind, one line each: this is the map the tool prints about
itself, so it cannot describe a command that does not exist.

```console
$ dxconvey help map --tree
the map of the command line

A verb says what you want, a kind says which answer, and the options come after
both.  `dxconvey VERB -h` is the page of a verb, `dxconvey VERB KIND -h` the
page of a kind, and `dxconvey help VERB KIND` prints the same one.

a dump (takes one .syx file)
└─ show             read a dump: the numbers of it, or the sheets of one kind of entity
   ├─ summary       the numbers: what the file is, what it holds and what it lacks
   ├─ all           the complete inventory: performances, voices, instrument data and SysEx messages
   ├─ voice         one line per voice: slot, name, sound type, algorithm, usage, what a DX7 keeps
                    and duplicate slots
   ├─ portability   what a DX7 voice file keeps, changes or cannot carry from each voice
   ├─ performance   one line per performance: slot, name, key mode, the two voices, detune, balance
                    and note shift
   ├─ sysex         the SysEx messages of one dump: one box per message, with offsets
   ├─ counts        one count per dump, for a list of them: how much a set of banks holds
   ├─ micro-tuning  list the records of micro-tuning in a dump
   ├─ key-scaling   list the records of key-scaling in a dump
   ├─ system        list the records of system in a dump
   └─ other         list the records of other in a dump

the instrument (no dump needed)
└─ instrument       what the machine does, and how a sound is named: memory, algorithm, tuning,
                    envelope, scaling, lfo, description, behaviour, sound-type
   ├─ memory        what a voice, a performance and a file are made of
   ├─ algorithm     print the reference sheet of the 32 DX7 algorithms
   ├─ tuning        the intonations a performance can select, or the intonation of one voice
   │  ├─ presets    [DX7II only] the thirteen intonations, with their cent values
   │  └─ voice      how far the carriers of one voice are from equal temperament
   ├─ envelope      how long an envelope lasts, in seconds, and what it looks like
   ├─ scaling       how loud an operator is along the keyboard (keyboard level scaling)
   ├─ lfo           the LFO: its six waveforms, what a speed is worth, and the delay
   │  ├─ waves      the six waveforms of the voice byte, at a speed and a delay
   │  ├─ rates      the speed 0-99 against its frequency
   │  ├─ ramps      the delay against its two phases
   │  └─ voice      the LFO of one voice of a dump
   ├─ description   how a voice is described, in words: the tag, the behaviour, the confidence
   ├─ behaviour     the fourteen axes of behaviour, and the rule behind every word
   └─ sound-type    how the tag is decided: the cells, the neighbourhood, the name

the output (writes files)
└─ convert          convert DX7II voices for a DX7 and report what changes or cannot be carried over
   ├─ banks         one or two 32-voice DX7 banks, loadable by a DX7 or Dexed as a cartridge: the
                    everyday answer, and what `convert FILE` does
   ├─ package       the same two banks in the tree to hand over: DX7/ with the banks and their
                    reports, DX7II/ with the source and its own, README.txt, all in a folder named
                    after the dump
   ├─ voices        one DX7 voice file per source voice, named after the voice, with its supplement
                    when present; two voices of one name and one content share a file; also a
                    register of the run
   └─ performances  one folder per performance: the voices it plays, and how to play it on a DX7

a software target (takes one .syx file)
└─ recipe           how a software target plays a performance: the instances, the controllers, the
                    host, and what no target models
   ├─ dexed         the recipe for Dexed: one instance per voice: the four controllers as one depth
                    and three switches each, and the layer in the host
   └─ ops7          the recipe for OPS7: one instrument with two layers: one matrix row per
                    controller and destination, so the three ranges of a wheel stay three

a search over many dumps (takes a list)
└─ search           which voices of a set of dumps answer a query: a tag, a name, the words of the
                    behaviour

the reference (help, the generated documents and the tool itself)
├─ help             the help of the tool, of one command, or the map of all of them
├─ about            who wrote this tool, where it lives, and how to support it
└─ docs             print a generated reference document (markdown, to stdout)
   ├─ cli           the whole command line (docs/tool/cli.md)
   ├─ algorithms    the 32 algorithms (docs/instrument/dx7-algorithms.md)
   ├─ tuning        the intonations (docs/instrument/microtuning.md)
   └─ check         check the three generated documents against their files (exit 1 if stale)
```

## What it prints

Every run below is real: the command line, then what `dxconvey` wrote, copied from a
terminal. The code is not in this repository yet — it lands with the first release — but
the numbers are not a mock-up: they are the tool reading one dump, `alienazi.syx`, the
DX7II All-Data of the package published here
([alienazi.zip](https://solyaris.altervista.org/dx7iipatches/alienazi.zip)): 64 voices,
32 performances, and 60 programmed voices among the 64 voice slots. That is the same bank
the downloadable package was built from, so every answer below is about a file the
reader can hold.

**A figure is drawn so that it reads on a page.** The tool's default alphabet for a
curve is the Braille patterns (`U+2800`–`U+28FF`, a 2×4 dot grid per character cell), the
finest grid a terminal can hold — and one a code block here would show as a row of boxes,
because a page cannot be told which font to use and the code font of a Windows browser has
none. Every run below that draws therefore asks for `--glyphs dot`: three thin marks per
cell, made of the punctuation and the box drawing the tables already use, so the figure
survives any font. In a terminal the default stays finer — `dxconvey instrument envelope
--plot` — and `--glyphs block`, a half block per cell, is the third alphabet, for a font
that has the block elements and not the dots.

### The dump, at a glance

One line per question: what the file is, what it holds, and how its programmed
voices transfer to a DX7 voice file.

```console
$ dxconvey show summary alienazi.syx
alienazi.syx  --  12,128 bytes
  DX7II All-Data dump
  contents: 64 voices (2 banks), each a DX7 voice plus its DX7II supplement, 1 performance bank (32)
  not in this dump: micro tuning, fractional key scaling, system set-up

  performances    32 programmed  (25 dual, 5 single, 2 split)
  voices          59 distinct  out of 64 slots: 60 programmed, 4 factory INIT, 1 duplicate content
  used            43 voices  are referenced by the performances (17 programmed voices are not)
  DX7II only      57 of 64 voice slots carry additional parameters
  on a DX7        54 lossy · 1 close · 5 exact, of the 60 programmed voices
  tuning           5 leave equal temperament
```

### The dump, as it is laid out

Every SysEx message of the file is a box: the block's own name, its size, and the
offset where it starts.

```console
$ dxconvey show sysex alienazi.syx
  alienazi.syx  ·  12,128 bytes  ·  DX7II All-Data dump

  ┌─────────────────────────┬─────────────────────────┬────────────┐
  │ DATA-CHG                │ AMEM                    │ VMEM       │
  │ the device and the type │ 32 Voice Effect records │ 32 voices  │
  │ 7 B                     │ 1,128 B                 │ 4,104 B    │
  │ 19 4D 00                │ 32 × 35 B               │ 32 × 128 B │
  └─────────────────────────┴─────────────────────────┴────────────┘
   @0                        @7                        @1,135

  ┌─────────────────────────┬─────────────────────────┬────────────┐
  │ DATA-CHG                │ AMEM                    │ VMEM       │
  │ the device and the type │ 32 Voice Effect records │ 32 voices  │
  │ 7 B                     │ 1,128 B                 │ 4,104 B    │
  │ 19 4D 01                │ 32 × 35 B               │ 32 × 128 B │
  └─────────────────────────┴─────────────────────────┴────────────┘
   @5,239                    @5,246                    @6,374

  ┌──────────────────┐
  │ PMEM             │
  │ 32 performances  │
  │ 1,650 B          │
  │ 32 × 51 B + name │
  └──────────────────┘
   @10,478
  (AMEM and VMEM of a half pair slot by slot: `instrument memory map`)
```

### A voice, in full

One voice is six operators: the sheet says the routing, the touch, the controllers
and what a DX7 keeps, the four rates and levels of each operator, and its timing.
`--plots` draws the six envelopes on one time axis. This is the first voice of
`alienazi.syx`.

```console
$ dxconvey show voice alienazi.syx --slot 1 --sheet
VOICE 1 · Tabla-3
────────────────────────────────────────────────────────────────────
SOUND TYPE percussion/drum · name-only
BEHAVIOUR  decays, no end, harmonic, bright, two layers, pitch falling

algorithm  10 · a 3-operator stack with feedback plus two summed modulators
carriers   OP1 OP4 · 2 of 6 reach the output
feedback   OP3 on itself

           ┌─────┐
           │ OP3 │◀─╮
           └──┬──┴──╯
              │
           ┌──▼──┐     ┌─────┐  ┌─────┐
           │ OP2 │     │ OP5 │  │ OP6 │
           └──┬──┘     └──┬──┘  └──┬──┘
              │           ├────────┘
           ┌──▼──┐     ┌──▼──┐
           │ OP1 │     │ OP4 │
           └──┬──┘     └──┬──┘
              └─────┬─────┘
                    ▼
                 OUTPUT

MIDI response
           velocity OP1 OP4 KVS 1 (carriers louder), OP2 KVS 5 (modulators
           brighter), OP3 KVS 6 (modulators brighter)
           mod wheel: EG bias 64
           after touch: pitch 5, pitch bias 24

timing     key up one second after the slowest carrier reaches its sustain
           level; programmed levels only, live velocity/controller offsets
           not applied
           note-on to silence

           ─ key held · ╌ release · ↓ key-up · ┤ silence · ∞ no silence
           intervals, not amplitude; times on the right are from note-on
           positions rounded to the nearest cell

carriers   C4 · key up 2.66 s
           0       1       2       3       4       5 s
           ├───────┼───────┼───────┼───────┼───────┤
       OP1 ─────────────────────↓╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌∞  does not reach silence
       OP4 ─────────────┤                             1.66 s

envelopes  R = rates 0-99 (0 = slowest) · L = levels 0-99 (0 = silence)
op   role          ratio  det  level vel  R1 R2 R3 R4    L1 L2 L3 L4  RS
OP6  modulator d1   5.00   +4     66   0  69  0 49  0    99 11 96  0   0
OP5  modulator d1   19Hz   -5     70   0  95 24 46  0    99 99 87  0   0
OP4  carrier        5.00   +7     99   1  89 98 47 50    99 99  0  0   0
OP3  modulator d2   4.00   -7     60   6  99 47 40 75    93 66  0  0   7
OP2  modulator d1  257Hz   +0     96   5  75 14 69 35    99 99 91  0   2
OP1  carrier      1.00Hz   -1     98   1  75 55 50 34    99 99 31 13   2

volume     the amplitude envelope of the voice is that of OP1, the carrier
           that lives longest
keyboard   rate scaling OP1 2, OP2 2, OP3 7. A scaled envelope runs faster
           in the treble and slower in the bass, so the rates above are not
           one time
EG bias    mod wheel can offset the levels live: the table is the rest
           position
portability lossy · remapped AMS; 4 settings not in DX7 voice file (after
            touch, mod wheel, pitch bend)

operator timing at C4; programmed levels, one key-up at 2.66 s for all six
op          R1         R2         R3         R4  after key up
OP6     5.8 ms     2.66 s          - 3 min 48 s  silence in 3 min 48 s
OP5     0.4 ms     0.0 ms     200 ms 3 min 30 s  silence in 3 min 30 s
OP4     1.9 ms     0.0 ms     1.66 s     0.0 ms  silent at key up
OP3     0.1 ms      54 ms     253 ms     0.0 ms  silent at key up
OP2     5.0 ms     0.0 ms     6.0 ms     3.62 s  silence in 3.62 s
OP1     5.4 ms     0.0 ms     405 ms     918 ms  does not reach silence
```

### What changes on a DX7

The voice list gives a verdict; `show portability` explains it. Settings that
already fit are kept apart from adapted values and settings missing from the
DX7 voice file. Controller settings may need separate DX7 function settings;
loading the converted voice alone does not restore them.

```console
$ dxconvey show portability alienazi.syx --slot 1
VOICE 1 · Tabla-3
DX7II → DX7 voice file

portability lossy

unchanged
  amplitude modulation sensitivity (AMS)
    How strongly each operator responds to LFO amplitude modulation.
    OP1: 1 · OP2: 2 · OP3: 2
    These settings already fit the DX7's range; no change is needed.

not included in the DX7 voice file
  pitch bend
    The DX7II uses pitch bend mode high.

  mod wheel
    The wheel controls EG bias, changing envelope levels.
    EG bias range  64

  after touch
    Key pressure controls pitch modulation and pitch bias.
    pitch modulation range   5
    pitch bias range        24

Loading the converted voice alone will not restore these settings or
controller responses. The values above are parameter settings, not measured
changes in volume or pitch.
```

### What a sound is called

A voice carries no word for what it is, so the tool says what it **imitates**: one
of seventeen tags, from `piano` to `synth`, never a claim about the sound itself.
Beside the tag it writes one phrase of **behaviour**, computed from the bytes on
fourteen axes — attack, body, release, spectrum, brightness, density, lfo_motion,
pitch_arc, lfo_shape, lfo_arrival, feedback, timbre, layering, touch — each a
threshold over the operators, the envelopes and the ratios. No model, no network,
no listening: the same file gives the same phrase every time.

The order is the argument. **The bytes** give the axes, **the axes** give the
behaviour, and **the phrase with the name of the voice** together give the tag — a
name may confirm the reading the bytes allow, or pick another one, but it never
decides against them. The confidence line says who decided: `certain`, `plausible`,
`name-only`, or `-` for a slot that still holds the factory voice.

The law of every axis is one command away (`instrument behaviour`), and so is the
table of the cells that give each tag (`instrument sound-type`, with `--verbose` for
the same table read the other way). This page shows the answer, not the law:

```console
$ dxconvey -q instrument description
SOUND TYPE · the tag the voice imitates, with its subtype and the confidence
BEHAVIOUR · one phrase of what the voice does, in the fourteen axes
rule · which reading of the cell table fired, in that reading's own words
why · the byte behind every adjective, one sentence per group
```

### Searching by the tag

Because the tag is a value and not a sentence, it can be searched: `--type` takes one
of the seventeen names, or one of the eight coarser words a sound library searches —
`--type struck` is the bells, the mallets and the percussion in one filter — and it
repeats. A word that is neither is refused (exit 2, with the page that lists both
levels), and a filter that matched nothing is a fact, not an error (exit 1).

`used` counts performances referring to that slot. `same as slot` identifies
identical voice and supplement contents, not merely identical names. A blank
duplicate-reference cell means no duplicate; zero usage counts stay explicit.

```console
$ dxconvey show voice alienazi.syx --type pad
31 voices  ·  31 lossy  ·  21 referenced by the performances

slot name        sound type    alg  used  on a DX7  same as slot
──── ──────────  ────────────  ───  ────  ────────  ────────────
   2 Respiri     pad            11     0  lossy
   4 Pulsazioni  pad            21     2  lossy
   5 Alien2000   pad            11     0  lossy
   6 SpacePig 3  pad            32     0  lossy
   9 Framura84   pad             2     1  lossy     24
  11 OpenSpace   pad             5     1  lossy
  13 Monique     pad             5     2  lossy
  17 NubiVacche  pad             5     1  lossy
  18 Gare 2000   pad            17     0  lossy
  19 BlackNoise  pad            27     0  lossy
  20 PazzaOrch1  pad            12     1  lossy
  21 Subatomo    pad            12     1  lossy
  22 PazzaOrch2  pad            12     1  lossy
  24 Framura84   pad             2     0  lossy     9
  26 RadioBot    pad             5     0  lossy
  27 Penombra    pad             5     0  lossy
  28 Incatata    pad            25     1  lossy
  29 Sabato20    pad             4     1  lossy
  30 VentiLenti  pad             6     0  lossy
  32 reversNois  pad            27     0  lossy
  33 carnivori   pad             9     1  lossy
  36 GiorgiCoro  pad             5     3  lossy
  37 ApiCattive  pad             1     1  lossy
  40 DownLife    pad             3     1  lossy
  44 De Chirico  pad            20     1  lossy
  45 moschini    pad             5     1  lossy
  49 lievottoni  pad             5     1  lossy
  54 Dedalo      pad            15     1  lossy
  55 AcquAfrica  pad             5     2  lossy
  57 choralarch  pad             5     2  lossy
  60 scherzavo   pad             5     1  lossy
```

### The envelopes of that voice, drawn

Four rates and four levels per operator are all a DX7 envelope is, and the tool turns
them into seconds. `--plots` adds the six operators to the sheet above, on one time
axis and one key-up: the sheet is repeated so that the figures travel with the
numbers they came from. The figure names the level of every segment, the note-on is
at the left edge and the key-up is the dashed column; a curve with a `▸` is cut there
because its release outlasts the voice — OP5 rings for three minutes.

```console
$ dxconvey show voice alienazi.syx --slot 1 --plots --glyphs dot
VOICE 1 · Tabla-3
────────────────────────────────────────────────────────────────────
SOUND TYPE percussion/drum · name-only
BEHAVIOUR  decays, no end, harmonic, bright, two layers, pitch falling

algorithm  10 · a 3-operator stack with feedback plus two summed modulators
carriers   OP1 OP4 · 2 of 6 reach the output
feedback   OP3 on itself

           ┌─────┐
           │ OP3 │◀─╮
           └──┬──┴──╯
              │
           ┌──▼──┐     ┌─────┐  ┌─────┐
           │ OP2 │     │ OP5 │  │ OP6 │
           └──┬──┘     └──┬──┘  └──┬──┘
              │           ├────────┘
           ┌──▼──┐     ┌──▼──┐
           │ OP1 │     │ OP4 │
           └──┬──┘     └──┬──┘
              └─────┬─────┘
                    ▼
                 OUTPUT

MIDI response
           velocity OP1 OP4 KVS 1 (carriers louder), OP2 KVS 5 (modulators
           brighter), OP3 KVS 6 (modulators brighter)
           mod wheel: EG bias 64
           after touch: pitch 5, pitch bias 24

timing     key up one second after the slowest carrier reaches its sustain
           level; programmed levels only, live velocity/controller offsets
           not applied
           note-on to silence

           ─ key held · ╌ release · ↓ key-up · ┤ silence · ∞ no silence
           intervals, not amplitude; times on the right are from note-on
           positions rounded to the nearest cell

carriers   C4 · key up 2.66 s
           0       1       2       3       4       5 s
           ├───────┼───────┼───────┼───────┼───────┤
       OP1 ─────────────────────↓╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌∞  does not reach silence
       OP4 ─────────────┤                             1.66 s

envelopes  R = rates 0-99 (0 = slowest) · L = levels 0-99 (0 = silence)
op   role          ratio  det  level vel  R1 R2 R3 R4    L1 L2 L3 L4  RS
OP6  modulator d1   5.00   +4     66   0  69  0 49  0    99 11 96  0   0
OP5  modulator d1   19Hz   -5     70   0  95 24 46  0    99 99 87  0   0
OP4  carrier        5.00   +7     99   1  89 98 47 50    99 99  0  0   0
OP3  modulator d2   4.00   -7     60   6  99 47 40 75    93 66  0  0   7
OP2  modulator d1  257Hz   +0     96   5  75 14 69 35    99 99 91  0   2
OP1  carrier      1.00Hz   -1     98   1  75 55 50 34    99 99 31 13   2

volume     the amplitude envelope of the voice is that of OP1, the carrier
           that lives longest
keyboard   rate scaling OP1 2, OP2 2, OP3 7. A scaled envelope runs faster
           in the treble and slower in the bass, so the rates above are not
           one time
EG bias    mod wheel can offset the levels live: the table is the rest
           position
portability lossy · remapped AMS; 4 settings not in DX7 voice file (after
            touch, mod wheel, pitch bend)

figures    the six operator envelopes at C4, one figure each; the six
           figures share one time axis and one key-up, one second after the
           slowest carrier reaches its sustain level
────────────────────────────────────────────────────────────────────────────────────────────────────
OP1 carrier                                         OP2 modulator · depth 1
  dB
   0┤..                              -               │.................................
 -20┤.'.                             -               │. L1=99                         -''--..
    │. '.                            -               │. L3=91                         -      ''--.▸
 -40┤.  '. L3=31                     -               │.                               -
    │.    ----------------------------..             │.                               -
 -60┤.                               -  '''---..     │.                               -
 -80┤.                               -          ''   │.                               -
    │.                               -               │.                               -
    └↑────┴──────────────────────────↓──────────┴─   └↑───────────────────────────────↓───────────┴
     0   0.5 s  1 s  1.5 s  2 s  2.5 s  3 s  3.5 s
OP3 modulator · depth 2                             OP4 carrier
  dB
   0┤                                -               │.-.                             -
 -20┤                                -               │.  '.                           -
    │ L1=93                          -               │.    '-.                        -
 -40┤. L2=66                         -               │. L1=99 '-.                     -
    │..                              -               │.         '-.                   -
 -60┤.'.                             -               │.            '-.                -
 -80┤. -. L3=0                       -               │.               -.   L3=0       -
    │.  '.........................................   │.                 '-.........................
    └↑┴──┴───────────────────────────↓────────────   └↑───────────────────┴───────────↓────────────
     0   0.5 s  1 s  1.5 s  2 s  2.5 s  3 s  3.5 s
OP5 modulator · depth 1                             OP6 modulator · depth 1
  dB
   0┤                                -               │                                -
 -20┤ L1=99                          -               │ L1=99                          - L2=11
    │.-..........................................▸   │.''''''''''''''''''''''''-------------------▸
 -40┤.  L3=87                        -               │.                               -
    │.                               -               │.                               -
 -60┤.                               -               │.                               -
 -80┤.                               -               │.                               -
    │.                               -               │.                               -
    └↑─┴─────────────────────────────↓───────────┴   └↑───────────────────────────────↓───────────┴
     0   0.5 s  1 s  1.5 s  2 s  2.5 s  3 s  3.5 s

     depth: number of modulation links to a carrier (longest path), not modulation amount
     ↑ note-on (key down) at 0; ↓ note-off (key up) at 2.66 s; same columns in every panel
     display window 3.69 s; one time axis for the six
     programmed carrier envelopes: OP1 does not reach silence
     ▸ cut at the edge, because their releases outlast it: OP2 (3.62 s), OP5 (3 min 30 s),
       OP6 (3 min 48 s)

operator timing at C4; programmed levels, one key-up at 2.66 s for all six
op          R1         R2         R3         R4  after key up
OP6     5.8 ms     2.66 s          - 3 min 48 s  silence in 3 min 48 s
OP5     0.4 ms     0.0 ms     200 ms 3 min 30 s  silence in 3 min 30 s
OP4     1.9 ms     0.0 ms     1.66 s     0.0 ms  silent at key up
OP3     0.1 ms      54 ms     253 ms     0.0 ms  silent at key up
OP2     5.0 ms     0.0 ms     6.0 ms     3.62 s  silence in 3.62 s
OP1     5.4 ms     0.0 ms     405 ms     918 ms  does not reach silence
```

### The performances

A performance combines one or two voices across the keyboard. The list shows
their slots and names, key mode, detune, stored balance and note shift. Active
alternate tunings appear below their rows; `--sheet` explains the full setup.
Neutral detune, balance and note shifts are left blank to highlight changes;
partial shifts such as `0/+24` retain both values. Sheets keep explicit settings.

```console
$ dxconvey show performance alienazi.syx
32 slots · 32 programmed · 25 dual, 5 single, 2 split

slot name                  mode      voice A        voice B        detune  balance  shift A/B
──── ────────────────────  ────────  ─────────────  ─────────────  ──────  ───────  ─────────
   1 PitecantropusErectus  dual      31 Orca Troia  23 Carlo Levi
   2 Antropos spaces       dual       4 Pulsazioni  34 soft wave                        0/+24
   3 sideral space bytes   split C4   7 SpacePig 2  10 SpacePig 5       3               +12/0
   4 carnivori stupendi    dual      38 stupenda    33 carnivori        6       +1      +12/0
   5 Particelle Subatomo   dual      21 Subatomo    21 Subatomo         6               0/+12
   6 Stati Alterati        dual      35 TIMEWARP    35 TIMEWARP         7             -24/-12
   7 Random crazy sinfony  dual      20 PazzaOrch1  22 PazzaOrch2       4       +6      -2/+2
     tuning 1/4 tone preset 10 · root G · voice B
   8 DeChiricoGialloeNero  dual      44 De Chirico  13 Monique
   9 non morto non vivo    dual      64 OrzoWay     60 scherzavo
  10 Apocalipse noise      single    59 apocalipse  -
  11 Black woman walk      dual       4 Pulsazioni  55 AcquAfrica       4       +3
  12 voci dal sottosuolo   dual      36 GiorgiCoro  40 DownLife         2       +2      -24/0
  13 Lamenti della Terra   dual      15 Laments 3   14 Laments 2        2
     tuning 1/4 tone preset 10 · root C · voices A+B
  14 choralarch Entropia   dual      57 choralarch  36 GiorgiCoro       2               0/-16
  15 extrasensorial act    dual      29 Sabato20    54 Dedalo                   +1      -12/0
     tuning 1/4 tone preset 10 · root C · voices A+B
  16 nubivacche percosse   dual      17 NubiVacche   1 Tabla-3
  17 Time Warp             dual      42 TimeWarp1   42 TimeWarp1                        0/-12
  18 Nuvole serene         split C4  16 Nuvole 2    63 Nuvole 3
     tuning 1/4 tone preset 10 · root C · voices A+B
  19 Incantata, non scema  single    28 Incatata    -                          -14
  20 lieviottoni           single    49 lievottoni  -
  21 architetti cosmici    single    57 choralarch  -                           +2
     tuning 1/4 tone preset 10 · root C · voice A
  22 Fabrizia a Framura    dual      13 Monique      9 Framura84               +10
  23 Tanganika Free        dual      55 AcquAfrica  10 SpacePig 5       5       +7
  24 sono solo insetti     dual      45 moschini    43 Bordone..        5       -3
  25 Enterprise Messages   dual      48 Mr. Spock   10 SpacePig 5       3       -5
  26 pesci del mar salato  dual      34 soft wave    7 SpacePig 2               +7
  27 Colossal sinphony     dual      31 Orca Troia  61 Orca Vacca       3       -5      0/-12
  28 P. Gabriel cymbals    dual      51 CrashPiano  36 GiorgiCoro               +2
  29 Terzo mondo           dual      46 TerzoMondo  46 TerzoMondo       1             +19/+12
  30 TESTOII by Tsukamoto  dual      11 OpenSpace   37 ApiCattive       7               0/+24
  31 Tsukamoto I           dual      56 B.Maderna   52 FidatiDiMe               -6
  32 Tsukamoto II          single    56 B.Maderna   -

detune: dual detune between voice A and voice B (0-7) · balance: volume of
voice A against voice B (-50..+50) · shift A/B: note shift of each voice in
semitones · blank setting: zero, or detune not applicable in single mode ·
split C4: voice B starts at that key · a single plays voice A alone, so it
has no voice B and no detune
```

### A performance, drawn

`--sheet` stops pointing and draws: which voice plays which keys, the sound of each
in words, the panning, the polyphony, the tuning, the switches — and the algorithm of
each voice as a block diagram. This one, the eighteenth, is a split, so the keyboard
is drawn too, band by band.

```console
$ dxconvey show performance alienazi.syx --slot 18 --sheet
PERFORMANCE 18 · Nuvole serene
LAYOUT     split at C4 · Voice A below · Voice B from C4 up
SOUND A    strings · plausible
SOUND B    strings · plausible
BEHAVIOUR  A: slow swell, no end, harmonic, dark, rich, drift, pitch gliding
           B: slow swell, no end, harmonic, dark, rich, drift, no velocity

voice A    16 Nuvole 2             algorithm  5  OP6 on itself
voice B    63 Nuvole 3             algorithm  5  OP6 on itself

MIDI response
  A        mod wheel: pitch 32, amplitude 31, EG bias 99
           after touch: pitch 21, amplitude 45, EG bias 38

timing     each voice's key comes up one second after its slowest carrier
           reaches its sustain level; programmed levels only, live
           velocity/controller offsets not applied
           note-on to silence · same scale for A and B

           ─ key held · ╌ release · ↓ key-up · ┤ silence · ∞ no silence
           intervals, not amplitude; times on the right are from note-on
           positions rounded to the nearest cell

timing A   C3 · key up 48.78 s
           0       10      20      30      40     50 s
           ├───────┼───────┼───────┼───────┼───────┤
       OP1 ───────────────────────────────────────↓∞  does not reach silence
       OP3 ───────────────────────────────────────↓∞  does not reach silence
       OP5 ───────────────────────────────────────↓∞  does not reach silence

timing B   C5 · key up 48.78 s
           0       10      20      30      40     50 s
           ├───────┼───────┼───────┼───────┼───────┤
       OP1 ───────────────────────────────────────↓∞  does not reach silence
       OP3 ───────────────────────────────────────↓∞  does not reach silence
       OP5 ───────────────────────────────────────↓∞  does not reach silence

settings   balance +0 · split C4 · shift +0/+0
volume     total 99
sliders    CS1 Pitch EG Level 4 (86) on A+B · CS2 OP2 Key velocity (17) on A
switches   EG forced damping off · sustain foot switch A+B · foot switch
           portamento A+B · soft pedal range 0
polyphony  16 notes · 8 + 8, at most 8 per side · 2 + 2 in unison poly
pan        on-on · separated, moves both levels · control off
tuning     1/4 tone preset 10 · root C · voice A + voice B · not published

keys       61 keys, C2 to C7, one column per semitone
               C2          C3          C4          C5          C6         C7
           A   ████████████████████████│
           B                           │████████████████████████████████████
                                       ▲ split at C4

pan EG     flat: levels 50/50/50/50, the centre (nothing moves)

algorithms A three 2-operator pairs + B three 2-operator pairs
           both voices use algorithm 5: 22 of 128 voice bytes differ

           A+B · algorithm 5
           ┌─────┐  ┌─────┐  ┌─────┐
           │ OP2 │  │ OP4 │  │ OP6 │◀─╮
           └──┬──┘  └──┬──┘  └──┬──┴──╯
              │        │        │
           ┌──▼──┐  ┌──▼──┐  ┌──▼──┐
           │ OP1 │  │ OP3 │  │ OP5 │
           └──┬──┘  └──┬──┘  └──┬──┘
              └────────┼────────┘
                       ▼
                    OUTPUT
```

### A performance, read

`--describe` says what it sounds like instead of drawing it: the tag of each voice and
how sure it is, one phrase of behaviour, and the bytes behind every axis of that
answer, with what the file cannot say.

```console
$ dxconvey show performance alienazi.syx --slot 1 --describe
PERFORMANCE 1 · PitecantropusErectus

layout     two voices on every key: Orca Troia and Carlo Levi
           performance detune 0

voice A    strings · plausible
           slow swell, no end, harmonic, one layer, drift with a pitch blip

voice B    brass · plausible
           held note, long tail, inharmonic, dark, rich, opening

why A
  envelope attack slow (carrier R1 33 of 99), body swell, a slow attack that
           dies away (L3 0 of 99), release infinite (R4 32, L4 9).
  spectrum carriers at 1.00 times the key. The highest modulator reaches
           4.00 times the key, so balanced.
  density  thin, 1 carrier (OP1) and 5 modulators.
  LFO      a triangle at speed 43 with a delay of 32 — drift, smooth, late.
  pitch    the pitch EG levels (52, 49, 50, 50) at rates (73, 67, 99, 99) —
           blip.
  timbre   static, the modulators ending at L3 28 against the carriers' 0.
  feedback strong (5 of 7).
  layering detuned within this voice.
  touch    after touch, mod wheel, velocity.

why B
  envelope attack instant (carrier R1 67 of 99), body held (L3 99 of 99),
           release long (R4 21, L4 0).
  spectrum carriers at 2 Hz, 105 Hz, 1 Hz fixed (not the key). The highest
           modulator reaches 1.71 times the key, so dark.
  density  rich, 3 carriers (OP5, OP3, OP1) and 3 modulators.
  LFO      a triangle at speed 30 with a delay of 21 — drift, smooth,
           delayed.
  pitch    the pitch EG levels (52, 57, 50, 50) at rates (99, 34, 39, 0) —
           blip.
  timbre   opening, the modulators ending at L3 50 against the carriers' 96.
  feedback strong (5 of 7).
  layering detuned within this voice.
  touch    after touch, mod wheel, velocity.

limits     parameter-based description, not a listening test.
           Controller EG bias has not been measured in level steps.
           Brightness and density are parameter proxies, not acoustic
           measurements; no brightness-in-dB result is available.
```

### The porting, and its register

Two banks land next to the dump, each with the register that names, voice by voice,
what a DX7 keeps and what it does not — the three outcomes of the preamble, one line
per voice. This is `alienazi.syx` itself.

```console
$ dxconvey convert alienazi.syx -o out/
CONVERT  alienazi.syx → out
  2 banks · 64 voices · 9 exact, 1 close, 54 lossy
  pitch EG proportional · 50, 25, 6.25, 3.125

  alienazi_1-32.syx   32 voices · slots 1-32 · the register: alienazi_1-32.txt
  alienazi_33-64.syx  32 voices · slots 33-64 · the register: alienazi_33-64.txt
```

The register opens by saying what it does not claim, and then goes through the
settings voice by voice. These are its first twenty lines — the file the command
above wrote:

```text
alienazi_1-32 — DX7 bank 1 of 2
===============================

- source dump — alienazi.syx
- positions in this bank — 1-32 (DX7II slots 1-32)
- pitch EG table — proportional · 50, 25, 6.25, 3.125
- a voice is identified by its position inside this bank, which is what Dexed, a
  DX7 and any librarian show
- the DX7II slot in parentheses is where it came from: provenance, not position
- what this does not claim
  Only the AMS bits and the four pitch EG levels are rewritten; parameters a
  DX7 has no place for are listed per voice and are lost; the fractional
  scaling and the performance layer are not exported at all. The result is
  not a verified acoustic copy of the DX7II voice.

- DX7 function parameters
  A DX7 keeps one set of function parameters for the whole instrument, while
  a DX7II keeps them per voice: the register names each setting once and
  lists the voices that ask for it. No parameter change file is written: the
  values are recorded here, not sent.
```

### A reference sheet, and no file needed

The 32 algorithms are the same on every six-operator machine: `instrument algorithm
5` draws one, names its carriers and its feedback, and tells how it sounds.

```console
$ dxconvey instrument algorithm 5
the six-operator line · [both]
  the factory voices named in these notes are the 32 of Yamaha's DX7 ROM1A cartridge; the DX7II's
  VRC banks reuse several of those names with other contents

  algorithm 5  ·  three 2-operator pairs
    carriers    OP1 OP3 OP5
    modulators  OP2 → OP1 · OP4 → OP3 · OP6 → OP5
    feedback    OP6 on itself
    structure   3 stacks of 2: OP2 → OP1, OP4 → OP3, OP6 → OP5

    ┌─────┐  ┌─────┐  ┌─────┐
    │ OP2 │  │ OP4 │  │ OP6 │◀─╮
    └──┬──┘  └──┬──┘  └──┬──┴──╯
       │        │        │
    ┌──▼──┐  ┌──▼──┐  ┌──▼──┐
    │ OP1 │  │ OP3 │  │ OP5 │
    └──┬──┘  └──┬──┘  └──┬──┘
       └────────┼────────┘
                ▼
             OUTPUT

    how it sounds
      Three independent pairs, each a modulator onto its own carrier. Nothing is shared, so the
      result is close to additive synthesis with three coloured partials: each pair can be tuned to
      its own ratio and given its own envelope, and the feedback on OP6 makes the third pair the
      'sawtooth' one. It is the most used and the most forgiving algorithm of the DX7: almost any
      harmonic recipe can be built here, and one pair can be left as a pure sine for the
      fundamental.

    typical sounds
      · organs and flutes with several registrations
      · tubular bells, glockenspiel, celesta: the factory ORCH-CHIME and TUB BELLS use it
      · electric piano: the factory E.PIANO 1 is this algorithm with the third pair at ratio 14.00
        for the tine and the other two at 1.00
      · two- and three-part additive pads, choirs

    programming it
      Set the pairs to harmonic ratios of the fundamental (1, 2, 3, 4, 6, 8) and shape them with
      their own envelopes; OP2, OP4, OP6 control the brightness of their own pair only. Feedback on
      OP6 turns that pair into a near-sawtooth, which is the fastest route to a rich 'analogue'
      sound on the DX7.

    note
      The DX9 (4 operators) borrowed this one as its algorithm 5.
```

### One envelope, timed

The model turns four rates and four levels into seconds; the figure carries the
note-on, the key-up and the sustain, and the table under it gives every segment:

```console
$ dxconvey instrument envelope --rates 95,60,40,50 --levels 99,85,60,0 --plot --glyphs dot
the six-operator line · [both]
  dB
   0┤.'L1=99           '                                        -
    │.. L2=85          '                                        -
    │.''--..           '                                        -
 -20┤.'     ''-..      '                                        -
    │.'          ''--. 'L3=60                                   -
    │.'               ''''''''''''''''''''''''''''''''''''''''''-.
    │.'                '                                        - '.
 -40┤.'                '                                        -   -.
    │.'                '                                        -    '.
    │.'                '                                        -      -.
 -60┤.'                '                                        -        -.
    │.'                '                                        -         '.
    │.'                '                                        -           -.
    │.'                '                                        -             -.
 -80┤.'                '                                        -              '.
    │.'                '                                        -                -...
    └┴┴────────────────┴────────────────────────────────────────┴─────────────────┴──
             R3                         sustain                         R4
     R1 R2
     0       0.5 s       1 s      1.5 s      2 s       2.5 s      3 s       3.5 s
     ↑ note-on (key down)                                       ↓ note-off (key up)

segment  rate  goes to   distance  duration
R1         95  L1 99   +  50.0 dB  1.2 ms
R2         60  L2 85   -  10.5 dB  49 ms
R3         40  L3 60   -  18.1 dB  801 ms
sustain     -  (held)              2.00 s
R4         50  L4  0   -  61.3 dB  850 ms
note-on: the level jumps at once to -50 dB, where the first rise starts
total 3.70 s (key up at 2.85 s)

  the times are the chip's envelope model (Dexed / msfa), not a measurement of this instrument
  docs/instrument/envelope-generator.md §9
```


## A conversion with a register of losses

DX7II and DX7 voices do not support exactly the same settings. Every porting
therefore ends with a register beside the bank it wrote: one line per voice, saying
what was remapped into the 128 bytes of a DX7 voice, what was declared and lost, and
what the result does not claim to be.

An earlier conversion example is available [as a downloadable package](https://solyaris.altervista.org/dx7iipatches/alienazi.zip)
— the bank the runs above read. That package predates the current project name and its
internal credit uses an earlier working name. For instrument and patch information, see
the [DX7 collection page](https://solyaris.altervista.org/dx7.html).

## Project principles

- **Explain the result:** report the choices of a porting and what it costs,
  voice by voice, instead of leaving the loss to be discovered on the instrument.
- **Trace claims:** base format descriptions on Yamaha documentation and on
  inspected data, and write down the rule when a value has to be rescaled.
- **Read first:** never rewrite a source file; write output only where asked, and
  never over an existing one.
- **Keep the tool distinct from sound libraries:** this repository is for the
  software, not a patch collection — and no dump is shipped here, because the
  licence of the sounds forbids redistribution. The examples above read a bank
  that is published as a package, and they link it.

## Status and release

This repository is a **coming soon**: it describes the project and shows what the
tool prints, and it holds no code yet. The source code lands with the **first public
release, by December 2027**. The sample
package linked above is an earlier conversion example, not a source code release.

What the first release carries is the reading of DX7II dumps, the porting to the DX7
with its register, and the reference sheets of the instrument; the natural-language
interface named `converse` is a later goal, not part of it.

The public repository is licensed under [MIT](LICENSE). That license applies to
the project software, not to separately published sound files.

## What comes next

The tool answers today what a dump holds, what the machine does, what a porting costs and
how a target plays a performance. What follows is not conversion, and none of it changes
the shape of the command line:

- **a library, not a list of files** — `search` answers over the dumps named on the command
  line, one query at a time. What is missing is the index that remembers them, so that a
  collection of banks becomes a catalogue to browse instead of a folder to read again.
- **`lint fix`** — finding a programming error or an anomalous setting inside a voice (a
  carrier silent, an envelope that never comes back, a scaling that cancels its operator)
  and correcting it at the desk instead of discovering it on the instrument. The verb is
  `lint`, the correction is its `fix` kind, because a verb says what you want and a kind
  says which answer.
- **a `recipe` for more targets** — `recipe` writes down today how Dexed and OPS7 play a
  performance: one instance per voice with the controllers spread over the host, or one
  instrument with two layers. The programs that read these files are compared, one by one,
  on [the DX7 emulators page](https://solyaris.altervista.org/dx7-emulators.html).
- **`randomizer`** — a voice is a set of numbers that a hand can only reach so far: the plan
  is a verb that makes variations of one voice around its own behaviour and names what it
  changed, so the result is a patch to audition, not a lottery.

Nothing here carries a date. What the first release brings is written above: the reading of
DX7II dumps, the porting with its register, the reference sheets of the instrument, and the
recipes for the two targets.

## The questions a DX7 owner asks

**Can my DX7 load the bank as it is?** No. A DX7 reads a DX7 voice or a bank of thirty-two;
an All-Data dump is what a DX7II writes, and a DX7 has no way to take it. Inside the dump,
though, the two voice banks are already exactly what a DX7 sends when it dumps its memory —
two standard messages, header and checksum included — so the export is a lift, not a
rebuild. This tool is not the first to do it; it is the one that writes the register beside
the banks.

**Will the converted voice sound the same?** No, and the tool does not claim it will. What
survives is the whole DX7 voice, byte for byte. What changes is everything that leaned on the
thirty-five bytes: the amplitude modulation sensitivity is mapped from the eight values a
DX7II sets onto the four a DX7 has, the pitch envelope is rescaled into the single range the
DX7 offers, and the rest cannot be played on a DX7 at all. The register says, voice by
voice, what was remapped and what was left behind.

**Is there a lossless "save as DX7"?** No, and a tool that offers one is dropping the
thirty-five bytes without saying so: the DX7 voice format has no room for them, which is a
property of the machine Yamaha shipped in 1983, not of the converter. What a converter can
choose is whether the loss is declared — remapped where a rule exists, declared where it
does not, never silent.

## Supporting the work

The tool is MIT-licensed and stays free. If you want to support the work
around it — these pages, the notes on the instrument, the open-source
tools — there is a donate button in the **Sponsor** menu of this repository:

- **[Donate with PayPal](https://www.paypal.com/donate/?hosted_button_id=AEV3EVJEUFM32)**

It is a donation, not a purchase: nothing is unlocked, nothing changes in the
license, and no support is promised in exchange. The minimum is 5 EUR, for a
practical reason — below that the PayPal fee takes most of it. The same button
is on the [dxconvey page](https://solyaris.altervista.org/dxconvey.html) and on
the [DX7 collection page](https://solyaris.altervista.org/mesmerism.html).

Buying the DX7II patch banks is a separate thing: those are sound files sold on
the collection page, not funding for this software.

## Questions and corrections

Questions, corrections and objections belong in
[Discussions](https://github.com/solyarisoftware/dxconvey/discussions), in the
**Q&A** category — there the answer that settled it can be marked, and the next
reader finds it instead of asking again. Issues stay closed until there is code
to run: on a repository with no source, an issue is only a slower Q&A.

There is no contact address here on purpose. A thread in the open is the same
conversation as a private letter, except that it stays readable.

DX7, DX7II and TX802 are Yamaha trademarks. This project is not affiliated with
Yamaha.
