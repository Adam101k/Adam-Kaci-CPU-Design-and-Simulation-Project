from __future__ import annotations
from typing import Tuple, Dict, List, Literal
from memory import Bit
import gates as g

Bits = Tuple[Bit, ...]
MulOp = Literal["MUL"] # (extend later: "MULH", "MULHU", "MULHSU")
DivOp = Literal["DIV", "DIVU", "REM", "REMU"]

def _zeros(n: int) -> Bits:
    return tuple(Bit(False) for _ in range(n))


def _one_hot_lsb(n: int) -> Bits:
    return tuple(Bit(False) for _ in range(n - 1)) + (Bit(True),)


def _assert_w(v: Bits, w: int) -> Bits:
    if len(v) == w:
        return v
    if len(v) < w:
        return (_zeros(w - len(v)) + v)
    return v[-w:]


def _is_zero(v: Bits) -> bool:
    acc = Bit(False)
    for b in v:
        acc = g.or_gate(acc, b)
    return not bool(acc)


def _not_vec(a: Bits) -> Bits:
    return tuple(g.not_gate(x) for x in a)


def _add_unsigned(a: Bits, b: Bits, cin: Bit = None) -> Tuple[Bits, Bit]:
    assert len(a) == len(b)
    if cin is None:
        cin = Bit(False)
    n = len(a)
    out = [Bit(False)] * n
    carry = cin
    for i in range(n - 1, -1, -1):
        axb = g.xor_gate(a[i], b[i])
        s = g.xor_gate(axb, carry)
        c1 = g.and_gate(a[i], b[i])
        c2 = g.and_gate(axb, carry)
        carry = g.or_gate(c1, c2)
        out[i] = s
    return tuple(out), carry