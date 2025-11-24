from __future__ import annotations
from typing import Tuple, Literal
from memory import Bit
import gates as g

Bits = Tuple[Bit, ...]
Op = Literal["SLL", "SRL", "SRA"]

def _zeros(n: int) -> Bits:
    return tuple(Bit(False) for _ in range(n))

def _stage_sll(a: Bits, k: int) -> Bits:
    if k == 0: return a
    n = len(a)
    out = list(a)
    for _ in range(k):
        for i in range(n - 1):
            out[i] = out[i + 1]
        out[-1] = Bit(False)
    return tuple(out)

def _stage_srl(a: Bits, k: int) -> Bits:
    if k == 0: return a
    n = len(a)
    out = list(a)
    for _ in range(k):
        for i in range(n - 1, 0, -1):
            out[i] = out[i - 1]
        out[0] = Bit(False)
    return tuple(out)

def _stage_sra(a: Bits, k: int) -> Bits:
    if k == 0: return a
    n = len(a)
    sign = a[0] if n > 0 else Bit(False)
    out = list(a)
    for _ in range(k):
        for i in range(n - 1, 0, -1):
            out[i] = out[i - 1]
        out[0] = sign
    return tuple(out)

def _shamt5_to_bools(shamt5: Bits) -> Tuple[bool, bool, bool, bool, bool]:
    # MSB-first 32b input; we only look at the **last 5** bits (LSB .. LSB-4)
    # e.g., for ...0001_1010, we read b0=0,b1=1,b2=0,b3=1,b4=1 (1+2+8+16)
    b0 = bool(shamt5[-1])
    b1 = bool(shamt5[-2])
    b2 = bool(shamt5[-3])
    b3 = bool(shamt5[-4])
    b4 = bool(shamt5[-5])
    return b0, b1, b2, b3, b4

def shift32(a: Bits, shamt5: Bits, op: Op) -> Bits:
    a = a[-32:] if len(a) >= 32 else (_zeros(32 - len(a)) + a)
    s0, s1, s2, s3, s4 = _shamt5_to_bools(shamt5)
    out = a
    if op == "SLL":
        if s0: out = _stage_sll(out, 1)
        if s1: out = _stage_sll(out, 2)
        if s2: out = _stage_sll(out, 4)
        if s3: out = _stage_sll(out, 8)
        if s4: out = _stage_sll(out, 16)
    elif op == "SRL":
        if s0: out = _stage_srl(out, 1)
        if s1: out = _stage_srl(out, 2)
        if s2: out = _stage_srl(out, 4)
        if s3: out = _stage_srl(out, 8)
        if s4: out = _stage_srl(out, 16)
    elif op == "SRA":
        if s0: out = _stage_sra(out, 1)
        if s1: out = _stage_sra(out, 2)
        if s2: out = _stage_sra(out, 4)
        if s3: out = _stage_sra(out, 8)
        if s4: out = _stage_sra(out, 16)
    else:
        raise ValueError(f"unknown shift op {op}")
    return out
