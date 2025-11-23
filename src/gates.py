# gates.py
from __future__ import annotations
from typing import Tuple
from memory import Bit

# Single-bit logic gates (scalar). All return Bit.

def not_gate(a: Bit) -> Bit:
    return Bit(not bool(a))

def and_gate(a: Bit, b: Bit) -> Bit:
    return Bit(bool(a) and bool(b))

def or_gate(a: Bit, b: Bit) -> Bit:
    return Bit(bool(a) or bool(b))

def xor_gate(a: Bit, b: Bit) -> Bit:
    return Bit(bool(a) ^ bool(b))

def and3_gate(a: Bit, b: Bit, c: Bit) -> Bit:
    return Bit(bool(a) and bool(b) and bool(c))

def or3_gate(a: Bit, b: Bit, c: Bit) -> Bit:
    return Bit(bool(a) or bool(b) or bool(c))

def nand_gate(a: Bit, b: Bit) -> Bit:
    return not_gate(and_gate(a, b))

def nor_gate(a: Bit, b: Bit) -> Bit:
    return not_gate(or_gate(a, b))

def xnor_gate(a: Bit, b: Bit) -> Bit:
    return not_gate(xor_gate(a, b))

# Basic building blocks for arithmetic

def mux2(sel: Bit, a: Bit, b: Bit) -> Bit:
    # 2:1 mux — select b if sel==1 else a.
    return b if bool(sel) else a

def half_adder(a: Bit, b: Bit) -> Tuple[Bit, Bit]:
    # Return (sum, carry).
    s = xor_gate(a, b)
    c = and_gate(a, b)
    return s, c

def full_adder(a: Bit, b: Bit, cin: Bit) -> Tuple[Bit, Bit]:
    # Return (sum, carry).
    axb = xor_gate(a, b)
    s   = xor_gate(axb, cin)
    c1  = and_gate(a, b)
    c2  = and_gate(axb, cin)
    c   = or_gate(c1, c2)
    return s, c
