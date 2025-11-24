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
    
    # value-based equality so Bit(True) == Bit(True)
    def __eq__(self, other) -> bool:
        if isinstance(other, Bit):
            return self._v == other._v
        # allow comparison to plain bools/ints in a pinch
        try:
            return self._v == bool(other)
        except Exception:
            return NotImplemented
        
    # hash consistent with equality (lets Bits be used in sets/dicts)
    def __hash__(self) -> int:
        return 1 if self._v else 0
    
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

def msb(v: BitVec) -> Bit:
    return v[0] if v else Bit(False)

def lsb(v: BitVec) -> Bit:
    return v[-1] if v else Bit(False)

def slice_bits(v: BitVec, start: int, end: int) -> BitVec:
    # (start:end) MSB-indexed (0 is MSB)
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

class Reg:
    # Synchronous load/clear register storing a fixed-width bit vector.
    width: int
    _bits: BitVec = None # set in __post_init__

    def __post_init__(self):
        if self._bits is None:
            self._bits = bits_zero(self.width)
            
    def load(self, v: BitVec) -> None:
        # Keep right-most width bits (LSBs), MSB-first ordering kept
        v = tuple(v)[-self.width:]
        # If caller provides narrower, zero-extend on the left (MSB side)
        if len(v) < self.width:
            v = zero_extend(v, self.width)
        self._bits = v

    def clear(self) -> None:
        self._bits = bits_zero(self.width)

    def read(self) -> BitVec:
        return tuple(self._bits)
    
class RegFile:
    # Integer register file: 32 entries of width 32, x0 hard-wired to zero (writes ingnored)
    
    def __init__(self, count: int = 32, width: int = 32, hardwired_zero_idx: int | None = 0):
        self.count = count
        self.width = width
        self.zero_idx = hardwired_zero_idx
        self._regs = [Reg(width) for _ in range(count)]

        # Enforce x0 = 9
        if self.zero_idx is not None:
            self._regs[self.zero_idx].clear()

    def read(self, idx: int) -> BitVec:
        return self._regs[idx].read()
        
    def write(self, idx: int, v: BitVec) -> None:
        if self.zero_idx is not None and idx == self.zero_idx:
            return 
        self._regs[idx].load(v)

class FPRegFile:
    # Floating point register file: 32 entries (default width=32 for single-precsion)
    # For double-precision, construct with width=64
    def __init__(self, count: int = 32, width: int = 32):
        self.count = count
        self.width = width
        self._regs = [Reg(width) for _ in range(count)]

    def read(self, idx: int) -> BitVec:
        return self._regs[idx].read()

    def write(self, idx: int, v: BitVec) -> None:
        self._regs[idx].load(v)

# Canonical 32b zero and factories

ZERO32: Bitx32 = bits_zero(32)

def make_bitx32(bits: Iterable[Bit]) -> Bitx32:
    v = tuple(bits)
    return zero_extend(v, 32) if len(v) < 32 else tuple(v[-32:])

def make_bitx12(bits: Iterable[Bit]) -> Bitx12:
    v = tuple(bits)
    return zero_extend(v, 12) if len(v) < 12 else tuple(v[-12:])