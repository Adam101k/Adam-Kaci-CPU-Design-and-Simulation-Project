from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Iterable, List

class Bit:
    # Bit is gonna do bit stuff 
    __slots__ = ("_v",)

    def __init__(self, value: bool = False):
        self._v = bool(value)

    def __bool__(self) -> bool:
        return self._v

    # Small helpers for nicer prints
    def __repr__(self) -> str:
        return "1" if self._v else "0"

    def as_bool(self) -> bool:
        return self._v
    
BitVec = Tuple[Bit, ...]
Bitx12 = BitVec
Bitx32 = BitVec

# Bit Vector helpers (no num arithmetic here)

def bits_zero(n: int) -> BitVec:
    # n zeros
    return tuple(Bit(False) for _ in range(n))

def bits_one_hot_lsb(n: int) -> BitVec:
    # ...0001 (LSB = 1)
    if n <= 0:
        return tuple()
    return tuple(Bit(False) for _ in range(n-1)) + (Bit(True),)

def concat(*vecs: Iterable[Bit]) -> BitVec:
    out: List[Bit] = []
    for v in vecs:
        out.extend(v)
    return tuple(out)

def msb(v: BitVec) -> Bit:
    return v[0] if v else Bit(False)

def lsb(v: BitVec) -> Bit:
    return v[-1] if v else Bit(False)

def slice_bits(v: BitVec, start: int, end: int) -> BitVec:
    return tuple(v[start:end])

def zero_extend(v: BitVec, new_width: int) -> BitVec:
    if len(v) >= new_width:
        return tuple(v[-new_width:])
    pad = bits_zero(new_width - len(v))
    return concat(pad, v)

def sign_extend(v: BitVec, new_width: int) -> BitVec:
    s = msb(v)
    if len(v) >= new_width:
        return tuple(v[-new_width:])
    pad = tuple(s for _ in range(new_width - len(v)))
    return concat(pad, v)

def not_bits(v: BitVec) -> BitVec:
    return tuple(Bit(not b.as_bool()) for b in v)

def and_bits(a: BitVec, b: BitVec) -> BitVec:
    return tuple(Bit(bool(x) and bool(y)) for x, y in zip(a, b))

def or_bits(a: BitVec, b: BitVec) -> BitVec:
    return tuple(Bit(bool(x) or bool(y)) for x, y in zip(a, b))

def xor_bits(a: BitVec, b: BitVec) -> BitVec:
    return tuple(Bit(bool(x) ^ bool(y)) for x, y in zip(a, b))

# Bit-vector helpers (no num math)

def bits_zero(n: int) -> BitVec:
    # n zeros
    return tuple(Bit(False) for _ in range(n))

def bits_one_hot_lsb(n: int) -> BitVec:
    # ..0001 (LSB = 1)
    if n <= 0:
        return tuple()
    return tuple(Bit(False) for _ in range(n-1)) + (Bit(True),)

def concat(*vecs: Iterable[Bit]) -> BitVec:
    out: List[Bit] = []
    for v in vecs:
        out.extend(v)
    return tuple(out)