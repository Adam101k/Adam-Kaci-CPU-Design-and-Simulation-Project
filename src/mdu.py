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

def _inc_unsigned(a: Bits) -> Tuple[Bits, Bit]:
    return _add_unsigned(a, _one_hot_lsb(len(a)))

def _sub_unsigned(a: Bits, b: Bits) -> Tuple[Bits, Bit]:
    nb = _not_vec(b)
    nb1, _ = _inc_unsigned(nb)
    s, carry = _add_unsigned(a, nb1)
    borrow = g.not_gate(carry)  # carry==1 -> no borrow
    return s, borrow

def _shl_logical(a: Bits, steps: int = 1) -> Bits:
    out = list(a)
    for _ in range(steps):
        for i in range(len(out) - 1):
            out[i] = out[i + 1]
        out[-1] = Bit(False)
    return tuple(out)

def _shr_logical(a: Bits, steps: int = 1) -> Bits:
    out = list(a)
    for _ in range(steps):
        for i in range(len(out) - 1, 0, -1):
            out[i] = out[i - 1]
        out[0] = Bit(False)
    return tuple(out)

def _unsigned_less_than(a: Bits, b: Bits) -> bool:
    for i in range(len(a)):
        ai, bi = bool(a[i]), bool(b[i])
        if ai != bi:
            return (not ai) and bi
    return False

def _twos_negate(a: Bits) -> Bits:
    inv = _not_vec(a)
    one = _one_hot_lsb(len(a))
    s, _ = _add_unsigned(inv, one)
    return s

def _abs_signed32(a: Bits) -> Tuple[Bits, Bit]:
    """Return (abs(a), is_negative). a is 32-bit two's complement."""
    neg = a[0]
    return (_twos_negate(a) if bool(neg) else a), neg

def _sign_extend(v: Bits, to_w: int) -> Bits:
    s = v[0] if v else Bit(False)
    if len(v) >= to_w:
        return v[-to_w:]
    return tuple(s for _ in range(to_w - len(v))) + v

def _pack64(hi: Bits, lo: Bits) -> Bits:
    return hi + lo