#!/usr/bin/env python3
"""Write `examples/example.syx` — a synthetic DX7II All-Data dump, authored here.

The examples in the README must be checkable and must quote nobody's patches, so the
dump they run on is built by this script instead of being taken from a collection. It
holds 64 voices, each a DX7 voice plus its DX7II supplement, and 32 performances, and it
is composed so that the conversion meets all three portability classes:

    16 voices exact    the supplement says nothing a DX7 lacks
    32 voices close    an AMS above 3 or a pitch EG range: remapped, not lost
    16 voices lossy    a mod wheel setting, a unison detune: no destination on a DX7

The names are `PAD 01` … `BRASS 64`, cycled; the voices themselves are the factory INIT
voice, so nothing here is anybody's patch.

This file depends on nothing but the standard library: it is the generator the public
repository ships, where `dxconvey` itself is not present yet.

    python3 examples/make_example.py examples/example.syx
"""

from __future__ import annotations

import sys

#: The factory initialisation voice (128 bytes, VCED order) — a documented default.
INIT_VOICE = bytes.fromhex(
    "6363636363636300270000003800000200636363636363630027000000380000020063636363"
    "6363630027000000380000020063636363636363002700000038000002006363636363636300"
    "2700000038000002006363636363636300270000003800630200636363633232323200082300"
    "00003118494e495420564f494345"
)
#: The DX7II supplement of the initialisation voice (35 bytes, AMEM order).
INIT_SUPPLEMENT = bytes.fromhex(
    "0000000000080000000000000000000000000032000000320000000000000000000000"
)
#: The ten bytes that open a performance bank (PMEM).
PERFORMANCE_BANK_SIGNATURE = b"LM  8973PM"

WORDS = ("PAD", "BELL", "ORGAN", "BRASS")


def checksum(data: bytes) -> int:
    """Yamaha's checksum: what to add to the data sum to reach a multiple of 128."""
    return (128 - (sum(data) % 128)) & 0x7F


def message(fmt: int, data: bytes, device: int = 0) -> bytes:
    """One SysEx message, with its 14-bit length and its checksum."""
    header = bytes([0xF0, 0x43, device, fmt, len(data) >> 7, len(data) & 0x7F])
    return header + data + bytes([checksum(data), 0xF7])


def data_change(half: int) -> bytes:
    """The three-byte message that announces a half of an All-Data dump."""
    return bytes([0xF0, 0x43, 0x10, 0x19, 0x4D, half, 0xF7])


def an_operator(
    level: int,
    coarse: int,
    *,
    detune: int = 7,
    rate_scaling: int = 0,
    kvs: int = 0,
    ams: int = 0,
    rates: tuple[int, int, int, int] = (99, 99, 99, 99),
    levels: tuple[int, int, int, int] = (99, 99, 99, 0),
    fine: int = 0,
) -> bytes:
    """The 17 bytes of one operator, in the order the voice record keeps them."""
    return bytes(
        [*rates, *levels, 0, 0, 0, 0, (detune << 3) | rate_scaling,
         (kvs << 2) | ams, level, coarse << 1, fine]
    )


#: Four voices, cycled by slot: six operators in record order (OP6 first), the
#: algorithm (0-based) and the feedback amount.  They are written to sound like what
#: their names say, so that the sheets and the envelope figures have something to
#: show that is not the init voice six times.
DESIGNS = (
    {   # PAD — three pairs, slow attack, long tail
        "algorithm": 4,        # algorithm 5
        "feedback": 4,
        "operators": (
            an_operator(85, 2, kvs=3, rates=(40, 30, 25, 50), levels=(99, 85, 75, 0)),
            an_operator(75, 3, rates=(32, 35, 28, 45), levels=(99, 90, 70, 0)),
            an_operator(78, 1, kvs=3, rates=(45, 35, 30, 50), levels=(99, 88, 78, 0)),
            an_operator(88, 2, rates=(30, 32, 26, 45), levels=(99, 92, 72, 0)),
            an_operator(72, 1, kvs=3, rates=(38, 30, 28, 55), levels=(99, 86, 76, 0)),
            an_operator(99, 1, rates=(28, 30, 24, 42), levels=(99, 95, 78, 0)),
        ),
    },
    {   # BELL — a four-operator chain with feedback, and a pair beside it
        "algorithm": 0,        # algorithm 1
        "feedback": 6,
        "operators": (
            an_operator(82, 11, rates=(99, 60, 40, 70), levels=(99, 80, 60, 0)),
            an_operator(78, 7, rates=(99, 55, 38, 70), levels=(99, 78, 55, 0)),
            an_operator(74, 3, rates=(99, 50, 35, 70), levels=(99, 75, 50, 0)),
            an_operator(99, 1, rates=(99, 45, 30, 65), levels=(99, 70, 0, 0)),
            an_operator(70, 14, rates=(99, 65, 45, 75), levels=(99, 85, 65, 0)),
            an_operator(92, 1, rates=(99, 42, 28, 62), levels=(99, 65, 0, 0)),
        ),
    },
    {   # ORGAN — six carriers added, one drawbar each
        "algorithm": 31,       # algorithm 32
        "feedback": 0,
        "operators": (
            an_operator(56, 8, rates=(99, 99, 99, 80), levels=(99, 99, 99, 0)),
            an_operator(64, 6, rates=(99, 99, 99, 80), levels=(99, 99, 99, 0)),
            an_operator(72, 4, rates=(99, 99, 99, 80), levels=(99, 99, 99, 0)),
            an_operator(80, 3, rates=(99, 99, 99, 80), levels=(99, 99, 99, 0)),
            an_operator(88, 2, rates=(99, 99, 99, 80), levels=(99, 99, 99, 0)),
            an_operator(99, 1, rates=(99, 99, 99, 80), levels=(99, 99, 99, 0)),
        ),
    },
    {   # BRASS — one modulator onto three carriers, the classic swell
        "algorithm": 21,       # algorithm 22
        "feedback": 5,
        "operators": (
            an_operator(88, 1, kvs=5, rates=(95, 45, 30, 60), levels=(99, 80, 60, 0)),
            an_operator(94, 1, rates=(90, 40, 28, 55), levels=(99, 90, 70, 0)),
            an_operator(0, 1, rates=(99, 99, 99, 99), levels=(99, 99, 99, 0)),
            an_operator(92, 2, rates=(88, 42, 26, 58), levels=(99, 88, 68, 0)),
            an_operator(99, 1, rates=(85, 38, 25, 55), levels=(99, 92, 72, 0)),
            an_operator(0, 1, rates=(99, 99, 99, 99), levels=(99, 99, 99, 0)),
        ),
    },
)


def a_voice(slot: int) -> bytes:
    """One DX7 voice: a design of its own, and a name of its own."""
    design = DESIGNS[slot % 4]
    voice = bytearray(INIT_VOICE)
    for index, operator in enumerate(design["operators"]):
        voice[index * 17 : (index + 1) * 17] = operator
    voice[110] = design["algorithm"]
    voice[111] = design["feedback"]
    name = f"{WORDS[slot % 4]} {slot + 1:02d}"
    voice[118:128] = name.encode("latin-1").ljust(10, b" ")[:10]
    return bytes(voice)


def a_supplement(slot: int) -> bytes:
    """The supplement of one voice, in the shape its portability class asks for."""
    amem = bytearray(INIT_SUPPLEMENT)
    kind = slot % 4
    if kind == 1:
        amem[1] = 7      # AMS of OP6 above 3: remapped 0-7 -> 0-3 on a DX7
    elif kind == 2:
        amem[4] = 1      # pitch EG range: the levels are rescaled, not lost
    elif kind == 3:
        amem[11] = 64    # mod wheel EG bias: a function parameter, no DX7 destination
        amem[34] = 3     # unison detune depth: no DX7 destination
    return bytes(amem)


def a_performance(index: int) -> bytes:
    """One 51-byte performance record: dual, split or single, with its two voices."""
    record = bytearray(51)
    mode = (1, 2, 0)[index % 3]
    record[0] = mode
    record[1] = index * 2 % 64
    record[2] = (index * 2 + 1) % 64
    record[6] = 3            # detune
    record[7] = 60           # split point
    record[13] = record[14] = 24  # note shift of the two voices
    record[15] = 56          # balance
    label = ("PAIR", "SPLIT", "SINGLE")[index % 3] + f" {index + 1:02d}"
    record[31:51] = label.encode("latin-1").ljust(20, b" ")[:20]
    return bytes(record)


def build() -> bytes:
    """The whole dump: two halves of AMEM+VMEM, then the performance bank."""
    blob = b""
    for half in range(2):
        slots = range(half * 32, half * 32 + 32)
        blob += data_change(half)
        blob += message(0x06, b"".join(a_supplement(s) for s in slots))   # AMEM
        blob += message(0x09, b"".join(a_voice(s) for s in slots))        # VMEM
    performances = b"".join(a_performance(i) for i in range(32))
    blob += message(0x7E, PERFORMANCE_BANK_SIGNATURE + performances)      # PMEM
    return blob


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    blob = build()
    with open(argv[1], "wb") as handle:
        handle.write(blob)
    print(f"{argv[1]}: {len(blob):,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
