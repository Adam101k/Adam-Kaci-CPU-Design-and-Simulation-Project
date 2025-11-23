from __future__ import annotations
from typing import Tuple, Dict, List
from memory import Bit, Bitx32, bits_zero, xor_bits, and_bits, or_bits, not_bits, concat
import gates as g

Bits = Tuple[Bit, ...]

def _assert_32(v: Bits) -> Bits:
    if len(v) != 32:
        # zero-extend or trim to 32 (MSB-first)
        if len(v) < 32:
            pad = tuple(Bit(False) for _ in range(32 - len(v)))
            return pad + tuple(v)
        return tuple(v[-32:])
    return tuple(v)


def _ripple_add(a: Bits, b: Bits, cin: Bit = Bit(False)) -> Tuple[Bits, Bit]:
    # Add two equal-width bit vectors (MSB-first). Returns (sum, carry_out).
    assert len(a) == len(b)
    n = len(a)
    out: List[Bit] = [Bit(False)] * n
    carry = cin
    for i in range(n - 1, -1, -1):  # LSB -> MSB
        s, carry = g.full_adder(a[i], b[i], carry)
        out[i] = s
    return tuple(out), carry

def _twos_negate(b: Bits) -> Bits:
    inv = not_bits(b)
    one = tuple(Bit(False) for _ in range(len(b) - 1)) + (Bit(True),)
    s, _ = _ripple_add(inv, one)
    return s

def _is_zero(v: Bits) -> bool:
    acc = Bit(False)
    for bit in v:
        acc = g.or_gate(acc, bit)
    return not bool(acc)
