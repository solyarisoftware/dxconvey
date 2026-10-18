# dxconvey

**Read DX7II SysEx, convert voices for the DX7, and report what the conversion cannot carry.**

> **Placeholder — source code planned by December 2026, possibly as early as November.**
> This repository does not contain the tool source code yet. It describes the
> project and its intended scope; the code, tests and documentation will be added
> when the first public release is ready.

## What the project is

`dxconvey` is a command-line tool for working with Yamaha DX7II and DX7 voice
files. Its first release is intended to read and describe DX7II SysEx data,
convert DX7II voices into DX7 voices, and report which settings are changed or
cannot be carried over. The conversion is a translation, not a promise that the
result will sound identical on both instruments.

The DX7 voice is the common point between the two instruments. The project aims
to make the formats and the differences understandable, rather than hiding them
behind a file conversion.

## Command-line verbs

The CLI is organized around these verbs:

- `show` — inspect a dump;
- `algorithm`, `tuning`, `envelope`, `scaling` and `lfo` — explore instrument
  references and behavior;
- `convert` — create DX7 voices and report conversion losses;
- `help` and `docs` — the help of the command line, and the documents generated
  from it.

A verb says what you want; a **kind** — a word, never a flag — says which answer,
and the options come after it, because an option never changes the subject:

```bash
dxconvey show layout FILE.syx             # the file, one box per SysEx message
dxconvey show voice FILE.syx --slot 2     # one voice, in full
dxconvey convert banks FILE.syx -o OUT    # the conversion, and its register
```

The verb alone gives the shortest useful answer, and two shortcuts exist because
they are the questions asked most: `dxconvey FILE.syx` is `show summary FILE.syx`,
and `dxconvey convert FILE.syx` writes the DX7 banks in a folder beside the dump.

`converse`, a natural-language interface to instrument data, is a later goal; it
is **not** part of the current CLI or the first release.

## What it prints

Every run below is real, and every figure is drawn by the tool. The code is not in this
repository yet — it lands with the conversion — but the numbers are not a mock-up: they
come from `examples/example.syx`, a synthetic DX7II All-Data of 64 voices and 32
performances, with names that belong to nobody. That dump is in the repository, and so is
the script that writes it, so every capture here can be checked.

### The dump, at a glance

One line per question: what the file is, what it holds, and what a DX7
would lose.

```bash
$ dxconvey show summary example.syx
```

```text
example.syx  --  12,128 bytes
  DX7II All-Data dump
  contents: 64 voices (2 banks), each a DX7 voice plus its DX7II supplement, 1 performance bank (32)
  not in this dump: micro tuning, fractional key scaling, system set-up

  performances    32 programmed  (11 dual, 10 single, 11 split)
  voices          64 distinct  out of 64 slots: 64 programmed, 0 factory INIT, 0 duplicate content
  used            54 voices  are referenced by the performances (10 programmed voices are not)
  DX7II only      48 of 64 voice slots carry additional parameters: on a DX7 they lose something
```

### The dump, as it is laid out

Every SysEx message of the file is a box: the block's own name, its size, and the
offset where it starts.

```bash
$ dxconvey show layout example.syx
```

```text
  example.syx  ·  12,128 bytes  ·  DX7II All-Data dump

  ┌──────────┬─────────┬──────────┬──────────┬─────────┬──────────┬─────────┐
  │ DATA-CHG │ AMEM    │ VMEM     │ DATA-CHG │ AMEM    │ VMEM     │ PMEM    │
  │ 7 B      │ 1,128 B │ 4,104 B  │ 7 B      │ 1,128 B │ 4,104 B  │ 1,650 B │
  │ 19 4D 00 │ 32x35 B │ 32x128 B │ 19 4D 01 │ 32x35 B │ 32x128 B │ 32x51 B │
  └──────────┴─────────┴──────────┴──────────┴─────────┴──────────┴─────────┘
   @0         @7        @1,135     @5,239     @5,246    @6,374     @10,478
  (AMEM and VMEM of a half hold the same 32 voice slots: the DX7 half and its DX7II supplement)
```

### The conversion, and its bill

Two banks land next to the dump, each with the register that names, voice by voice,
what a DX7 keeps and what it does not.

```bash
$ dxconvey convert example.syx -o out/
```

```text
CONVERT  example.syx → out
  2 banks · 64 voices · 16 exact, 32 close, 16 lossy
  pitch EG proportional · 50, 25, 6.25, 3.125

  example_1-32.syx   32 voices · slots 1-32 · the register: example_1-32.txt
  example_33-64.syx  32 voices · slots 33-64 · the register: example_33-64.txt
```

### A reference sheet, and no file needed

The 32 algorithms are the same on every six-operator machine. `algorithm` draws one,
names its carriers and its feedback, and tells how it sounds and how to program it.

```bash
$ dxconvey algorithm 5
```

```text
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

<!-- optional: one of these two, the page is long with both -->

### Six waveforms, one figure

The LFO has six shapes and two depths; the figure is drawn at the resolution of a
Braille cell, so a cycle is legible as a line and not as a list of samples.

```bash
$ dxconvey lfo
```

```text
LFO  the six waveforms, the two depths, the key sync and the mode

waveforms  three bits of the voice pick one of six, in this order:
  0  triangle     rises over the first half cycle and falls over the second
  1  saw down     falls, starting from the middle of the cycle
  2  saw up       rises, starting from the middle of the cycle
  3  square       high for the first half cycle, low for the second
  4  sine         the DX7's own sine, centred on the rest position
  5  sample&hold  a new value at every cycle: the model's own generator

depths     PMD 0-99 × pitch modulation sensitivity 0-7 · the vibrato, on
           all six operators at once; AMD 0-99 × AMS 0-7 per operator ·
           the tremolo. Both are only as strong as that sensitivity, and 0
           there is silence (docs/instrument/operators.md §6.4)
key sync   one bit of the voice (byte 116): on, the LFO starts from the
           same point of its cycle at every key down; off, it runs free
mode       [DX7II only] one bit of the supplement: single, one LFO for every
           voice, as on a DX7; multi, one LFO per voice

  0  triangle                            1  saw down
  mod                                    mod
    1┤      ⣠⠞⢦            ⡴⠳⣄             1┤       ⢸⠲⢄⡀           ⡟⠲⣄⡀
  0.5┤    ⢀⡜⠁  ⠳⡄        ⢠⠞  ⠈⢣⡀         0.5┤       ⢸  ⠉⠳⢤⡀        ⡇  ⠙⠲⣄⡀
    0┤   ⣠⠋     ⠈⢦⡀    ⢀⡴⠁     ⠙⣄          0┤⠤⣀     ⢸     ⠉⠓⢤⣀     ⡇     ⠉⠲
      │ ⢀⠞⠁        ⠱⣄  ⣠⠎        ⠈⠳⡀         │ ⠈⠙⠦⣄  ⢸        ⠈⠓⢦⣀  ⡇
   -1┤⡴⠋           ⠈⢦⡴⠁           ⠙⢦      -1┤    ⠈⠙⠦⣼           ⠈⠑⠦⡇
      └┬────────────────────────────┬        └┬────────────────────────────┬
  2  saw up                              3  square
  mod                                    mod
    1┤    ⢀⣠⠖⢻           ⢀⡠⠖⡇              1┤⠉⠉⠉⠉⠉⠉⠉⢹       ⡏⠉⠉⠉⠉⠉⠉⡇      ⢸
  0.5┤ ⢀⣠⠖⠋  ⢸        ⢀⡤⠞⠉  ⡇            0.5┤       ⢸       ⡇      ⡇      ⢸
    0┤⠖⠉     ⢸     ⣀⡤⠞⠉     ⡇     ⣀⠤       0┤       ⢸      ⢠⠃      ⡇      ⢸
      │       ⢸  ⣀⡴⠚⠁        ⡇  ⣠⠴⠋⠁         │       ⢸      ⢸       ⡇      ⢸
   -1┤       ⢸⠴⠊⠁           ⣧⠴⠋⠁          -1┤       ⢸⣀⣀⣀⣀⣀⣀⣸       ⣇⣀⣀⣀⣀⣀⣀⣸
      └┬────────────────────────────┬        └┬────────────────────────────┬
  4  sine                                5  sample&hold
  mod                                    mod
    1┤ ⢀⡴⠋⠙⢦          ⢠⠞⠉⠑⢆                1┤
  0.5┤⢀⠎    ⢳⡀       ⢠⠋   ⠈⢧             0.5┤
    0┤⠎      ⢳⡀     ⢠⠇     ⠈⢧      ⡠       0┤⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠦⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⢤
      │        ⢳⡀   ⣠⠃       ⠈⢧    ⡰⠁        │                             ⢸
   -1┤         ⠱⢄⣀⡴⠃          ⠳⣄⣠⠞⠁       -1┤                             ⠈
      └┬────────────────────────────┬        └┬────────────────────────────┬
  6 shapes · 359 ms across

a voice    `dxconvey lfo voice FILE --slot N` reads the LFO of one
           voice of a dump: the only place a file can say what it
           does with it
more       `lfo rates` for a speed 0-99 in hertz and in seconds,
           `lfo ramps` for the delay; docs/instrument/lfo.md, and
           docs/instrument/operators.md §6.4 for the operator's side
```

### One envelope, timed

Four rates and four levels are all a DX7 envelope is. The model turns them into
seconds; the figure carries the note-on, the key-up and the sustain, and the table
under it gives every segment.

```bash
$ dxconvey envelope --rates 95,60,40,50 --levels 99,85,60,0 --plot
```

```text
  dB
   0┤⣧⠁L1=99          ⠈                                         ⠨
    │⡏⡇ L2=85         ⠈                                         ⠨
    │⡇⠉⠉⠒⠤⢄⡀          ⠈                                         ⠨
 -20┤⡇⠁    ⠈⠉⠒⠢⢄⣀     ⠈                                         ⠨
    │⡇⠁          ⠉⠑⠢⠤⣀⡈ L3=60                                   ⠨
    │⡇⠁               ⠈⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠩⢢
    │⡇⠁               ⠈                                         ⠨ ⠑⢄
 -40┤⡇⠁               ⠈                                         ⠨   ⠣⡀
    │⡇⠁               ⠈                                         ⠨    ⠈⢢
    │⡇⠁               ⠈                                         ⠨      ⠑⢄
 -60┤⡇⠁               ⠈                                         ⠨       ⠈⠢⡀
    │⡇⠁               ⠈                                         ⠨         ⠈⢆
    │⡇⠁               ⠈                                         ⠨           ⠑⢄
    │⡇⠁               ⠈                                         ⠨            ⠈⠢⡀
 -80┤⡇⠁               ⠈                                         ⠨              ⠈⢆
    │⡇⠁               ⠈                                         ⠨                ⠑⣄⣀⣀
    └┴┴───────────────┴─────────────────────────────────────────┴─────────────────┴──
             R3                        sustain                          R4
     R1 R2
     0       0.5 s       1 s      1.5 s      2 s       2.5 s      3 s       3.5 s
     ↑ note-on (key down)                                       ↓ note-off (key up)

segment  rate  goes to   distance  duration
R1         95  L1 99   +  50.0 dB  1.2 ms
R2         60  L2 85   -  10.5 dB  49 ms
R3         40  L3 60   -  18.1 dB  801 ms
sustain     -  (held)              2.00 s
R4         50  L4  0   -  61.3 dB  850 ms
note-on: the level starts at once 50.0 dB below the top, the first rise begins there
total 3.70 s (key up at 2.85 s)
```

## A conversion with a register of losses

DX7II and DX7 voices do not support exactly the same settings. `dxconvey` is
designed to make those differences visible: the conversion reports what it
remaps and what the DX7 voice format cannot preserve. The goal is to make each
conversion understandable, not to suggest that nothing was lost.

An earlier conversion example is available [as a downloadable package](https://solyaris.altervista.org/dx7iipatches/alienazi.zip).
That package predates the current project name and its internal credit uses an
earlier working name. For instrument and patch information, see the
[DX7 collection page](https://solyaris.altervista.org/dx7.html).

## Project principles

- **Explain the result:** report conversion choices and losses.
- **Trace claims:** base format descriptions on Yamaha documentation and
  inspected data.
- **Read first:** do not rewrite source files; write output only where requested.
- **Keep the tool distinct from sound libraries:** this repository is for the
  software, not a patch collection. The one dump here, `examples/example.syx`,
  is synthetic: `examples/make_example.py` writes it, a test checks the bytes,
  and its voices are the factory initialisation voice with names that belong to
  nobody.

## Status and release

The public repository is currently a placeholder. The source code is planned to
be added by **December 2026**, with a possible release in **November 2026**.
The sample package linked above is an earlier conversion example, not a source
code release.

The public repository is licensed under [MIT](LICENSE). That license applies to
the project software, not to separately published sound files.

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
