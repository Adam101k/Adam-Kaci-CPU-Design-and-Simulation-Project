from __future__ import annotations
from typing import Tuple, Dict, List
from memory import Bit, Bitx32, bits_zero, xor_bits, and_bits, or_bits, not_bits
from shifter import shift32
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

def _barrel_shift_left(v: Bits, shamt5: Bits) -> Bits:
    # SLL using 5-stage barrel shifter; shamt5 are the least-significant 5 bits of a 32b word
    out = list(v)
    # order low->high shift amounts: 1,2,4,8,16 (LSB is shamt bit 0)
    steps = [1, 2, 4, 8, 16]
    for i, amt in enumerate(steps, start=1):
        b = shamt5[-i]  # last bit is 2^0
        if bool(b):
            # shift left logical by amt (insert zeros at LSB)
            for _ in range(amt):
                for j in range(31):
                    out[j] = out[j + 1]
                out[31] = Bit(False)
    return tuple(out)

def _barrel_shift_right_logical(v: Bits, shamt5: Bits) -> Bits:
    out = list(v)
    steps = [1, 2, 4, 8, 16]
    for i, amt in enumerate(steps, start=1):
        b = shamt5[-i]
        if bool(b):
            for _ in range(amt):
                for j in range(31, 0, -1):
                    out[j] = out[j - 1]
                out[0] = Bit(False)
    return tuple(out)

def _barrel_shift_right_arith(v: Bits, shamt5: Bits) -> Bits:
    out = list(v)
    sign = v[0]
    steps = [1, 2, 4, 8, 16]
    for i, amt in enumerate(steps, start=1):
        b = shamt5[-i]
        if bool(b):
            for _ in range(amt):
                for j in range(31, 0, -1):
                    out[j] = out[j - 1]
                out[0] = sign  # replicate sign
    return tuple(out)


class ALU32:
    # RV32I-style ALU on explicit bit-vectors (MSB-first, 32 bits)

    def exec(self, rs1: Bits, rs2: Bits, op: str) -> Dict[str, object]:
        a = _assert_32(rs1)
        b = _assert_32(rs2)
        op = op.upper()

        if op == "ADD":
            s, carry = _ripple_add(a, b)
            res = s
            sa, sb, sr = a[0], b[0], res[0]
            V = Bit(bool(sa) == bool(sb) and bool(sr) != bool(sa))
            C = carry  # carry-out of MSB
        elif op == "SUB":
            nb = _twos_negate(b)  # a + (~b + 1)
            s, carry = _ripple_add(a, nb)
            res = s
            sa, sb, sr = a[0], b[0], res[0]
            V = Bit(bool(sa) != bool(sb) and bool(sr) != bool(sa))  # same as ADD rule with a + (-b)
            C = carry  # in two's-comp, C=1 implies no borrow
        elif op == "AND":
            res = and_bits(a, b)
            C = Bit(False); V = Bit(False)
        elif op == "OR":
            res = or_bits(a, b)
            C = Bit(False); V = Bit(False)
        elif op == "XOR":
            res = xor_bits(a, b)
            C = Bit(False); V = Bit(False)
        elif op == "SLL":
            res = shift32(a, b, "SLL")
            flags = {"N": bool(res[0]), "Z": all(not x for x in res), "C": False, "V": False}
            return {"result": res, "flags": flags}
        elif op == "SRL":
            res = shift32(a, b, "SRL")
            flags = {"N": bool(res[0]), "Z": all(not x for x in res), "C": False, "V": False}
            return {"result": res, "flags": flags}
        elif op == "SRA":
            res = shift32(a, b, "SRA")
            flags = {"N": bool(res[0]), "Z": all(not x for x in res), "C": False, "V": False}
            return {"result": res, "flags": flags}
        else:
            # NOP/unknown: return zeros
            res = bits_zero(32)
            C = Bit(False); V = Bit(False)

        N = res[0]
        Z = Bit(_is_zero(res))
        flags = {"N": bool(N), "Z": bool(Z), "C": bool(C), "V": bool(V)}
        return {"result": res, "flags": flags}


def alu32(rs1: Bits, rs2: Bits, op: str) -> Dict[str, object]:
    # Wrapper used for test
    return ALU32().exec(rs1, rs2, op)