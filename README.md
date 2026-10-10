# dxconvey

**Carry a DX7II voice across to the DX7 — and say what was lost on the way.**

Today the tool does two things, in this order. It **reads** a DX7II dump — the
voices, the performances, the envelopes, the 32 algorithms, the micro tunings,
the byte-level anatomy of the file — and it **converts** those DX7II voices into
**DX7 voices**, reporting everything the conversion cannot carry. Today the scope
is DX7II and DX7; the rest of the DX/TX family is meant to follow.

The longer goal is bigger than the converter. The DX7 voice is the one structure
every FM system speaks, so the same knowledge is meant to become a language for
all of them: a reference for the format, and in time a way to program a
DX7-based instrument by talking to it.

> **Coming soon — placeholder, work in progress.** There is no release yet. This
> repository states what `dxconvey` will be, and why; the code, the tests and the
> documentation will be published here. **Watch or star the repository to be
> notified.**

---

## The idea: the DX7 voice is the common denominator

A DX7 voice is 128 bytes. A DX7II voice is those same 128 bytes **plus 35 bytes
that only a DX7II has**. That is not an approximation, it is how Yamaha built
the instrument — and it is visible in the bytes of any DX7II All Data dump:

| layer | Yamaha's own name | size | who speaks it |
| --- | --- | --- | --- |
| voice data | VCED / VMEM | 128 B per voice (155 B as a single message) | **everyone** |
| additional data | ACED / AMEM | 35 B per voice | the DX7II family only |

```
a DX7II All Data dump (12,128 B)
  ├── AMEM   1,120 B   the additional 35 B of 32 voices   ← only a DX7II reads this
  ├── VMEM   4,096 B   32 voices × 128 B, in the DX7's own packed format
  ├── ...    (twice: voices 1-32 and 33-64, plus performances and system data)
```

The DX7II does not replace the DX7 voice — **it wraps it**. The instrument Yamaha
sold in 1987 still carries the 1983 voice inside, unchanged, as its own layer.
That is why this project has a spine instead of a pile of converters:

```
Voice = VCED core (128 B, mandatory, universal)
      + supplements (ACED 35 B on a DX7II, and whatever the next machine adds)
```

And that same 128 bytes is what the whole field orbits: hardware and virtual
instruments, emulations, editors, librarians. The DX7 voice is the *lingua
franca* of FM synthesis — nothing else in this field reaches that far, and it is
the only thing every system agrees on.

**So that is the goal of this project: to be the reference for that voice** — its
bytes, its dialects, its losses — rather than yet another file translator.

## The name

`convey` is one word doing three jobs, and all three are this project. Latin
*convertere*, "to turn towards", is the root of the first two:

| sense | in `dxconvey` |
| --- | --- |
| **to carry across** — the conversion | `dxconvey convert`: a voice moved to another machine |
| **to make understood** — the conversation | `dxconvey converse`: the words turned towards the instrument |
| **to report what happened** — the register | the output is a file *and* the account of what it cost |

`CONV` sits at the front of the name because it sits at the front of both halves
of the work: nothing crosses over here without being accounted for.

## Three horizons

| # | horizon | what it is | state |
| --- | --- | --- | --- |
| 1 | **read** | An inventory and a sheet for everything a dump contains: the 32 algorithms, the 13 micro tunings, the envelopes, panning, polyphony, the 51-byte performance map, the byte-level anatomy of the file. | working prototype |
| 2 | **convert** | The first public deliverable: a DX7II All Data dump becomes DX7 voice banks — 32 voices per file, 4,104 bytes each — **with a register of everything that did not survive**. | prototype: `--banks` |
| 3 | **converse** | The ambition: the same knowledge exposed as tools an agent can call, so that a DX7 VCED-based system can be programmed in natural language — and later edited while the instrument is playing. | planned |

## The loss register: a conversion is a translation, and a translation betrays

The conversion is **lossy**. That is precisely why it deserves engineering.

A DX7 has only VCED and VMEM: no performances, no additional parameters, no
stereo, no micro tunings. Everything a DX7II voice carries beyond its 128 bytes
has to be remapped, clamped or dropped — amplitude modulation sensitivity, pitch
EG range and by-velocity, fractional key scaling, panning, unison detune,
micro tuning, the function parameters. Each of those is a **decision**, and in
this project every decision is measured, written down with the numbers that
justify it, and printed in the output:

- a **per-slot register** records the source slot of every exported voice, the
  provenance of each remapped AMS value, the pitch EG levels **before and
  after**, the portability of the voice, and the source fields that were not
  carried at all;
- a **decision register** in the documentation keeps the open choices with the
  measurements behind them, instead of hiding them behind a default;
- competing conventions are named, not silently adopted: where another converter
  uses a different pitch EG table, that table is available explicitly, and the
  register says which one produced the file.

A silent clip is the easy way out: it hands you a file and says nothing about
what it threw away. **`dxconvey` hands you the bill.**

## Already run once: the first result is downloadable

The conversion described above is not a promise. It has been run, it has been
published, and its reports are in the open:

**<https://solyaris.altervista.org/dx7iipatches/alienazi.zip>**

```
alienazi.zip
├── README.txt              what the package holds, and how the conversion works
├── LICENSE.txt             the license of the sounds (not the license of this tool)
├── DX7/                    the export: two DX7 banks, and the report of each
│   ├── alienazi_1-32.syx   a DX7 32-voice bank, 4,104 bytes
│   ├── alienazi_1-32.txt   the per-voice register for that half
│   ├── alienazi_33-64.syx
│   └── alienazi_33-64.txt
└── DX7II/                  the original dump, as it is, and its own report
    ├── alienazi.syx        the DX7II All Data dump
    └── alienazi.txt
```

Read `alienazi_1-32.txt` before believing anything on this page: it names, voice
by voice, what was remapped and what a DX7 has no room for. The register is the
product, and it already exists.

The state of that draft, in its own words: **"I have tried the DX7 banks in Dexed
myself, and they load and they play."** That is the whole of the claim. No
acoustic comparison against a DX7II has been made, so how close the export comes
to the instrument is still open — and the pitch EG table the conversion rests on
is a decision, not a measurement, which is why it is a named option
(`--peg-factors`) rather than a hidden default.

One detail of that package, so it is not a surprise: **it credits the tool under
an earlier working name**, not under `dxconvey`. That name has been retired. The
credit inside the downloadable package is the only place it survives, and no part
of this repository uses it.

The sounds carry their own license, written for them (free to use in music,
commercial projects included; not free to redistribute). That license covers the
patches; the [MIT license](LICENSE) of this repository covers the tool. No sounds
are
shipped here: the download lives on the author's page.

## Design principles

1. **The DX7 voice is the pivot.** Every other format is documented as a delta on
   it, never as a separate universe.
2. **Losses are measured, decided and printed** — never silent, never hidden
   behind a default.
3. **Every claim is traced.** A statement about the format either comes from a
   manual or is verified against the bytes themselves; where the two disagree,
   the bytes win and the disagreement is written down. Each statement in the
   documentation carries its status: *verified*, *sourced*, or still *open*.
4. **The documentation is part of the product**, not a by-product: the reference
   is written before the code that obeys it.
5. **No dependencies.** Python 3.9+, the standard library, and the file itself.
6. **Read-only by default.** The tool never rewrites your dumps; it writes only
   where you tell it to.
7. **One knowledge base, two audiences**: a human at a terminal, and an agent
   calling tools.

## The shape of the interface

The target interface, not a release:

```bash
dxconvey show <dump>.syx                     # what is in this file (the inventory)
dxconvey show <dump>.syx --diagram           # the layout: one box per SysEx message
dxconvey show performance <dump>.syx --brief  # the performance sheets
dxconvey show voice <dump>.syx --slot 16     # one voice, in full
dxconvey algorithm 5 --used --in <dir>       # a reference sheet, plus who uses it
dxconvey tuning 5                            # one of the 13 micro tunings
dxconvey convert <dump>.syx --banks -o out/  # the CONVersion
dxconvey converse "make the release shorter" # the CONVersation (later; the EG release, in words)
```

And because the conversion is a set of decisions, the decisions are on the
command line too:

```bash
dxconvey convert <dump>.syx --banks -o out/ --peg-factors halving
#                                                    ^ name the convention,
#                                                      do not inherit it
```

When it is released, the repository will ship:

- the package and the CLI above, with tests — including a corpus test that pins
  the bytes of every file it is given;
- **the reference documentation**: the SysEx formats byte by byte, with block
  diagrams; the operator and its pitch, level and touch; the envelopes; the
  keyboard scaling; the LFO and the feedback; the pitch EG and the glide; the
  controllers of both machines and the fourteen function parameters; MIDI as a
  cable — the channels, program change, the bulk dump and the parameter change;
  the 32 algorithms with routing and how each one sounds; the 13 micro tunings;
  panning; polyphony; the hardware of the two machines; the conversion spec and
  its decision register; and every source used, with links;
- worked examples: one command per sample, and the test that keeps the two in
  sync.

<!-- OPEN: the documentation corpus and the natural-language skill still need
     names. English, short, no Italian. -->

## What this project is not

- **Not a patch library.** It ships a tool, not a collection of sounds.
  Third-party ROM content stays out — for licensing reasons and out of respect
  for the people who made it; where a bank is needed for tests, only synthetic
  fixtures and provenance hashes are used.
<!-- OPEN: publish the authored example dump (a single DX7II All Data file, our own)
     as the worked example, with its provenance noted? -->
- **Not a librarian GUI.** The catalogue, the ratings and the playlists are a
  different program's job.
- **Not affiliated with Yamaha.** DX7, DX7II, TX802 and the rest are Yamaha
  trademarks; naming them is description, not affiliation.

## License

MIT — see [LICENSE](LICENSE). The license covers the tool. It does not cover any
patch bank, its reports or its documentation of provenance: those carry their own
license, wherever they are published.

## Placeholder, work in progress

**This repository is a placeholder.** Nothing is released, nothing can be
downloaded, and everything above describes what `dxconvey` is meant to do rather
than what it does today. No dates are promised.

The instrument data this tool was written for is the patch collection published
at <https://solyaris.altervista.org/dx7.html>. That page is the collection, this
repository is the tool: they are related, but no sounds are shipped here.

For any question, note, correction or request, write to
**solyarismusic@gmail.com**. A wrong byte is worth reporting: every claim in the
documentation carries its status precisely so that a wrong one can be found and
fixed.

Watch or star the repository and you will be told when the release lands; open an
issue to argue about a decision — the registers in the documentation are exactly
the places where an argument can still change the outcome.
