# dxconvey

**Read DX7II SysEx, port DX7II voices to the DX7, and report what the porting cannot carry.**

> [!WARNING]
> **COMING SOON — there is no source code in this repository yet**
>
> The tool is being written. The code lands here with the **first public release,
> by December 2027** — the previous plan said November 2026.
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

The DX7II kept the voice of its predecessor untouched and put its own parameters
beside it: on a DX7 those thirty-five bytes have nowhere to go, so a porting gives
something up **voice by voice**, and the register says which. The performance layer —
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
itself works (`help`, `docs`). The map is a command, not this table — `help map` lists
every verb and every kind, and `--tree` draws it (the next block).

Two shortcuts, because they are the two questions asked most: `dxconvey FILE.syx` is
`show summary FILE.syx`, and `dxconvey convert FILE.syx` writes the DX7 banks in a folder
beside the dump. `converse`, a natural-language interface to instrument data, is a later
goal; it is **not** part of the current CLI.

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
   ├─ all           the numbers and one line per entity: every performance and every voice
   ├─ voice         one line per voice: slot, name, sound type, algorithm, carriers, release, and
                    what a DX7 keeps
   ├─ performance   one line per performance: slot, name, key mode, and the two voices with their
                    algorithms
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

the reference (help and the generated documents)
├─ help             the help of the tool, of one command, or the map of all of them
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
32 performances, and the 60 DX7 voices the porting makes of them. That is the same bank
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

One line per question: what the file is, what it holds, and what a DX7 would
lose.

```console
$ dxconvey show summary alienazi.syx
alienazi.syx  --  12,128 bytes
  DX7II All-Data dump
  contents: 64 voices (2 banks), each a DX7 voice plus its DX7II supplement, 1 performance bank (32)
  not in this dump: micro tuning, fractional key scaling, system set-up

  performances    32 programmed  (25 dual, 5 single, 2 split)
  tuning           5 leave equal temperament
  voices          59 distinct  out of 64 slots: 60 programmed, 4 factory INIT, 1 duplicate content
  used            43 voices  are referenced by the performances (17 programmed voices are not)
  DX7II only      57 of 64 voice slots carry additional parameters: on a DX7 they lose something
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
and what a DX7 keeps, then the timing of every operator. `--details` adds the four
rates and four levels of each, and `--plots` draws the six envelopes on one time
axis. This is the first voice of `alienazi.syx`.

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

TOUCH      MIDI velocity OP1 OP4 KVS 1 (carriers louder), OP2 KVS 5
           (modulators brighter), OP3 KVS 6 (modulators brighter)
CONTROLS   mod wheel: EG bias 64
CONTROLS   after touch: pitch 5, pitch bias 24
timing     C4 · key up at 2.66 s, one second after the slowest carrier
           reaches its sustain level; programmed levels only, live
           velocity/controller offsets not applied
carrier EG OP1 at C4: key up 2.66 s, does not reach silence
carrier EG OP4 at C4: key up 2.66 s, silent at key up
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

```console
$ dxconvey -q show voice alienazi.syx --type pad
2   Respiri          pad         alg 11  carriers 2  R4 20 (OP4)  on a DX7: lossy
4   Pulsazioni       pad         alg 21  carriers 4  R4 18 (OP5)  on a DX7: lossy
5   Alien2000        pad         alg 11  carriers 2  R4 22 (OP4)  on a DX7: lossy
6   SpacePig 3       pad         alg 32  carriers 6  R4 25 (OP1)  on a DX7: lossy
9   Framura84        pad         alg  2  carriers 2  R4 35 (OP3)  on a DX7: lossy
11  OpenSpace        pad         alg  5  carriers 3  R4 23 (OP1)  on a DX7: lossy
13  Monique          pad         alg  5  carriers 3  R4 35 (OP5)  on a DX7: lossy
17  NubiVacche       pad         alg  5  carriers 3  R4  0 (OP5)  on a DX7: lossy
18  Gare 2000        pad         alg 17  carriers 1  R4 20 (OP1)  on a DX7: lossy
19  BlackNoise       pad         alg 27  carriers 3  R4 23 (OP2)  on a DX7: lossy
20  PazzaOrch1       pad         alg 12  carriers 2  R4  0 (OP3)  on a DX7: lossy
21  Subatomo         pad         alg 12  carriers 2  R4  0 (OP3)  on a DX7: lossy
22  PazzaOrch2       pad         alg 12  carriers 2  R4 10 (OP3)  on a DX7: lossy
24  Framura84        pad         alg  2  carriers 2  R4 35 (OP3)  on a DX7: lossy
26  RadioBot         pad         alg  5  carriers 3  R4 32 (OP5)  on a DX7: lossy
27  Penombra         pad         alg  5  carriers 3  R4  8 (OP1)  on a DX7: lossy
28  Incatata         pad         alg 25  carriers 5  R4  0 (OP1)  on a DX7: lossy
29  Sabato20         pad         alg  4  carriers 2  R4 17 (OP1)  on a DX7: lossy
30  VentiLenti       pad         alg  6  carriers 3  R4 27 (OP5)  on a DX7: lossy
32  reversNois       pad         alg 27  carriers 3  R4 23 (OP2)  on a DX7: lossy
33  carnivori        pad         alg  9  carriers 2  R4  8 (OP3)  on a DX7: lossy
36  GiorgiCoro       pad         alg  5  carriers 3  R4 30 (OP1)  on a DX7: lossy
37  ApiCattive       pad         alg  1  carriers 2  R4 15 (OP3)  on a DX7: lossy
40  DownLife         pad         alg  3  carriers 2  R4  0 (OP4)  on a DX7: lossy
44  De Chirico       pad         alg 20  carriers 3  R4 24 (OP4)  on a DX7: lossy
45  moschini         pad         alg  5  carriers 3  R4  0 (OP5)  on a DX7: lossy
49  lievottoni       pad         alg  5  carriers 3  R4  0 (OP1)  on a DX7: lossy
54  Dedalo           pad         alg 15  carriers 2  R4  8 (OP1)  on a DX7: lossy
55  AcquAfrica       pad         alg  5  carriers 3  R4 17 (OP3)  on a DX7: lossy
57  choralarch       pad         alg  5  carriers 3  R4 11 (OP1)  on a DX7: lossy
60  scherzavo        pad         alg  5  carriers 3  R4  7 (OP1)  on a DX7: lossy
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

TOUCH      MIDI velocity OP1 OP4 KVS 1 (carriers louder), OP2 KVS 5
           (modulators brighter), OP3 KVS 6 (modulators brighter)
CONTROLS   mod wheel: EG bias 64
CONTROLS   after touch: pitch 5, pitch bias 24
timing     C4 · key up at 2.66 s, one second after the slowest carrier
           reaches its sustain level; programmed levels only, live
           velocity/controller offsets not applied
carrier EG OP1 at C4: key up 2.66 s, does not reach silence
carrier EG OP4 at C4: key up 2.66 s, silent at key up
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
OP1 carrier                                         OP2 modulator d1
  dB
   0┤..                              -               │.................................
 -20┤.'.                             -               │. L1=99                         -''--..
    │. '.                            -               │. L3=91                         -      ''--.▸
 -40┤.  '. L3=31                     -               │.                               -
    │.    ----------------------------..             │.                               -
 -60┤.                               -  '''---..     │.                               -
 -80┤.                               -          ''   │.                               -
    │.                               -               │.                               -
    └┴────┴──────────────────────────┴──────────┴─   └┴───────────────────────────────┴───────────┴
     0   0.5 s  1 s  1.5 s  2 s  2.5 s  3 s  3.5 s
OP3 modulator d2                                    OP4 carrier
  dB
   0┤                                -               │.-.                             -
 -20┤                                -               │.  '.                           -
    │ L1=93                          -               │.    '-.                        -
 -40┤. L2=66                         -               │. L1=99 '-.                     -
    │..                              -               │.         '-.                   -
 -60┤.'.                             -               │.            '-.                -
 -80┤. -. L3=0                       -               │.               -.   L3=0       -
    │.  '.........................................   │.                 '-.........................
    └┴┴──┴───────────────────────────┴────────────   └┴───────────────────┴───────────┴────────────
     0   0.5 s  1 s  1.5 s  2 s  2.5 s  3 s  3.5 s
OP5 modulator d1                                    OP6 modulator d1
  dB
   0┤                                -               │                                -
 -20┤ L1=99                          -               │ L1=99                          - L2=11
    │.-..........................................▸   │.''''''''''''''''''''''''-------------------▸
 -40┤.  L3=87                        -               │.                               -
    │.                               -               │.                               -
 -60┤.                               -               │.                               -
 -80┤.                               -               │.                               -
    │.                               -               │.                               -
    └┴─┴─────────────────────────────┴───────────┴   └┴───────────────────────────────┴───────────┴
     0   0.5 s  1 s  1.5 s  2 s  2.5 s  3 s  3.5 s

     ↑ note-on at once and ↓ note-off in the same column of every panel:
     one time axis for the six, 3.69 s, the life of the voice
     ▸ cut at the edge, because their releases outlast it: OP2 (3.62 s), OP5 (3 min 30 s),
       OP6 (3 min 48 s)
```

### The performances

A performance is a pointer: two voices, a key mode, a split point, a tuning. One line
each, and the first line counts what the bank holds.

```console
$ dxconvey show performance alienazi.syx
32 performances  ·  25 dual, 5 single, 2 split  ·  5 with an intonation
1    PitecantropusErectus     dual    A  31 Orca Troia   alg 16  B  23 Carlo Levi   alg  6  detune 0
2    Antropos spaces          dual    A   4 Pulsazioni   alg 21  B  34 soft wave    alg  5  detune 0
3    sideral space bytes      split   A   7 SpacePig 2   alg 32  B  10 SpacePig 5   alg 32  split C4
4    carnivori stupendi       dual    A  38 stupenda     alg  4  B  33 carnivori    alg  9  detune 6
5    Particelle Subatomo      dual    A  21 Subatomo     alg 12  B  21 Subatomo     alg 12  detune 6
6    Stati Alterati           dual    A  35 TIMEWARP     alg  5  B  35 TIMEWARP     alg  5  detune 7
7    Random crazy sinfony     dual    A  20 PazzaOrch1   alg 12  B  22 PazzaOrch2   alg 12  detune 4
     tuning 1/4 tone preset 10 · root G · voice B
8    DeChiricoGialloeNero     dual    A  44 De Chirico   alg 20  B  13 Monique      alg  5  detune 0
9    non morto non vivo       dual    A  64 OrzoWay      alg 10  B  60 scherzavo    alg  5  detune 0
10   Apocalipse noise         single  A  59 apocalipse   alg 18  --
11   Black woman walk         dual    A   4 Pulsazioni   alg 21  B  55 AcquAfrica   alg  5  detune 4
12   voci dal sottosuolo      dual    A  36 GiorgiCoro   alg  5  B  40 DownLife     alg  3  detune 2
13   Lamenti della Terra      dual    A  15 Laments 3    alg  3  B  14 Laments 2    alg  3  detune 2
     tuning 1/4 tone preset 10 · root C · voices A+B
14   choralarch Entropia      dual    A  57 choralarch   alg  5  B  36 GiorgiCoro   alg  5  detune 2
15   extrasensorial act       dual    A  29 Sabato20     alg  4  B  54 Dedalo       alg 15  detune 0
     tuning 1/4 tone preset 10 · root C · voices A+B
16   nubivacche percosse      dual    A  17 NubiVacche   alg  5  B   1 Tabla-3      alg 10  detune 0
17   Time Warp                dual    A  42 TimeWarp1    alg  5  B  42 TimeWarp1    alg  5  detune 0
18   Nuvole serene            split   A  16 Nuvole 2     alg  5  B  63 Nuvole 3     alg  5  split C4
     tuning 1/4 tone preset 10 · root C · voices A+B
19   Incantata, non scema     single  A  28 Incatata     alg 25  --
20   lieviottoni              single  A  49 lievottoni   alg  5  --
21   architetti cosmici       single  A  57 choralarch   alg  5  --
     tuning 1/4 tone preset 10 · root C · voice A
22   Fabrizia a Framura       dual    A  13 Monique      alg  5  B   9 Framura84    alg  2  detune 0
23   Tanganika Free           dual    A  55 AcquAfrica   alg  5  B  10 SpacePig 5   alg 32  detune 5
24   sono solo insetti        dual    A  45 moschini     alg  5  B  43 Bordone..    alg 11  detune 5
25   Enterprise Messages      dual    A  48 Mr. Spock    alg 16  B  10 SpacePig 5   alg 32  detune 3
26   pesci del mar salato     dual    A  34 soft wave    alg  5  B   7 SpacePig 2   alg 32  detune 0
27   Colossal sinphony        dual    A  31 Orca Troia   alg 16  B  61 Orca Vacca   alg 17  detune 3
28   P. Gabriel cymbals       dual    A  51 CrashPiano   alg 12  B  36 GiorgiCoro   alg  5  detune 0
29   Terzo mondo              dual    A  46 TerzoMondo   alg 21  B  46 TerzoMondo   alg 21  detune 1
30   TESTOII by Tsukamoto     dual    A  11 OpenSpace    alg  5  B  37 ApiCattive   alg  1  detune 7
31   Tsukamoto I              dual    A  56 B.Maderna    alg 17  B  52 FidatiDiMe   alg  2  detune 0
32   Tsukamoto II             single  A  56 B.Maderna    alg 17  --
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
MIDI response A mod wheel: pitch 32, amplitude 31, EG bias 99
MIDI response A after touch: pitch 21, amplitude 45, EG bias 38
timing     each voice's key comes up one second after its slowest carrier
           reaches its sustain level; programmed levels only, live
           velocity/controller offsets not applied
timing A   OP1 at C3: key up 48.78 s, does not reach silence
timing A   OP3 at C3: key up 48.78 s, does not reach silence
timing A   OP5 at C3: key up 48.78 s, does not reach silence
timing B   OP1 at C5: key up 48.78 s, does not reach silence
timing B   OP3 at C5: key up 48.78 s, does not reach silence
timing B   OP5 at C5: key up 48.78 s, does not reach silence
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

layout     two voices on every key: Orca Troia and Carlo Levi, not detuned
           against each other
voice A    strings · plausible
           slow swell, no end, harmonic, one layer, drift with a pitch blip
voice B    brass · plausible
           held note, long tail, inharmonic, dark, rich, opening
why A      the envelope: attack slow (carrier R1 33 of 99), body swell, a
           slow attack that dies away (L3 0 of 99), release infinite (R4 32,
           L4 9).
           the spectrum: carriers at 1.00 times the key. The highest
           modulator reaches 4.00 times the key, so balanced.
           the density: thin, 1 carrier (OP1) and 5 modulators.
           the LFO: a triangle at speed 43 with a delay of 32 — drift,
           smooth, late.
           the pitch arc: the pitch EG levels (52, 49, 50, 50) at rates (73,
           67, 99, 99) — blip.
           the timbre path: static, the modulators ending at L3 28 against
           the carriers' 0.
           the feedback: strong (5 of 7), the layering detuned.
           the touch: after touch, mod wheel, velocity.
why B      the envelope: attack instant (carrier R1 67 of 99), body held (L3
           99 of 99), release long (R4 21, L4 0).
           the spectrum: carriers at 2 Hz, 105 Hz, 1 Hz fixed (not the key).
           The highest modulator reaches 1.71 times the key, so dark.
           the density: rich, 3 carriers (OP5, OP3, OP1) and 3 modulators.
           the LFO: a triangle at speed 30 with a delay of 21 — drift,
           smooth, delayed.
           the pitch arc: the pitch EG levels (52, 57, 50, 50) at rates (99,
           34, 39, 0) — blip.
           the timbre path: opening, the modulators ending at L3 50 against
           the carriers' 96.
           the feedback: strong (5 of 7), the layering detuned.
           the touch: after touch, mod wheel, velocity.
note       what this cannot say: what a controller's EG bias is worth in
           level steps (not measured), how bright it is in dB (no
           level-to-dB curve), or how it really sounds (no recording was
           heard).  Brightness and density are proxies of the parameters,
           not measurements.
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
