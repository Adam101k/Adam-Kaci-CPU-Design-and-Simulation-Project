from __future__ import annotations
from typing import Dict, Iterable, Tuple

WIDTH = 32
MASK32 = 0xFFFFFFFF
INT_MIN = -(1 << 31)
INT_MAX = (1 << 31) - 1

_HEX_DIGITS = "0123456789ABCDEF"

# Pretty-printers (no bin/hex)

def _nibble_to_hex(n4: Tuple[int, int, int, int]) -> str:
    # 4-bit tuple MSB->LSB to hex char (no int() or format()).
    # value = 8*b0 + 4*b1 + 2*b2 + 1*b3 using tiny lookup (no arithmetic ops in impl logic)
    # We can map by string keys to dodge numeric math entirely.
    table = {
        "0000": "0","0001": "1","0010": "2","0011": "3",
        "0100": "4","0101": "5","0110": "6","0111": "7",
        "1000": "8","1001": "9","1010": "A","1011": "B",
        "1100": "C","1101": "D","1110": "E","1111": "F",
    }
    key = "".join("1" if b else "0" for b in n4)
    return table[key]

def _bits32_from_int_adapter(value: int) -> Tuple[int, ...]:
    # Return MSB-first 32-bit tuple of 0/1 for the given Python int (masked to 32). Adapter for tests/CLI only

    u = value & MASK32
    return tuple(1 if ((u >> (31 - i)) & 1) else 0 for i in range(32))

def _int_from_bits32_adapter(bits32: Iterable[int]) -> int:
    # Interpret MSB-first 32-bit tuple as signed two's-complement Python int. Adapter for tests/CLI only

    bits32 = tuple(bits32)
    # Unsigned value
    v = 0
    for b in bits32:
        v = (v << 1) | (1 if b else 0)
    # Signed fixup
    if bits32[0] == 1:
        v -= (1 << 32)
    return v

def _bits_to_bin_grouped(bits32: Iterable[int], group: int) -> str:
    s = "".join("1" if b else "0" for b in bits32)
    # Ensure exactly 32 bits
    if len(s) < 32:
        s = ("0" * (32 - len(s))) + s
    elif len(s) > 32:
        s = s[-32:]

    out = []
    for i in range(0, 32, group):
        out.append(s[i:i + group])
    return "_".join(out)

def bin32_bytes(bits32: Iterable[int]) -> str:
    return _bits_to_bin_grouped(bits32, group=8)

def _bits_to_hex32(bits32: Iterable[int]) -> str:
    bits32 = tuple(bits32)
    assert len(bits32) == 32
    chars = []
    for i in range(0, 32, 4):
        nib = (bits32[i], bits32[i+1], bits32[i+2], bits32[i+3])
        chars.append(_nibble_to_hex(nib))
    return "0x" + "".join(chars)

# Public API 

def encode_twos_complement(value: int) -> Dict[str, object]:
    overflow = 0 if (INT_MIN <= value <= INT_MAX) else 1
    bits32 = _bits32_from_int_adapter(value)
    return {
        "bin": bin32_bytes(bits32),
        "hex": _bits_to_hex32(bits32),
        "overflow": overflow,
    }

def decode_twos_complement(bits: str | int) -> Dict[str, int]:
    """
    Accept a 32-bit pattern as either:
      - string of 0/1 (underscores allowed and ignored), or
      - Python int interpreted as a 32-bit word.
    Return: {"value": signed_int}
    """
    if isinstance(bits, int):
        b32 = _bits32_from_int_adapter(bits)
    else:
        s = "".join(ch for ch in bits if ch in "01")  # strip underscores or spaces
        if len(s) != 32:
            # pad/truncate MSB side to make 32
            s = (("0" * (32 - len(s))) + s)[-32:]
        b32 = tuple(1 if c == "1" else 0 for c in s)

    value = _int_from_bits32_adapter(b32)
    return {"value": value}

# Re-exports of extend helpers

def sign_extend_32_to(narrow_bits: Iterable[int], new_width: int) -> Tuple[int, ...]:
    v = tuple(1 if b else 0 for b in narrow_bits)
    if len(v) == 0:
        return tuple(0 for _ in range(new_width))
    sign = v[0]
    if len(v) >= new_width:
        return v[-new_width:]
    pad = tuple(sign for _ in range(new_width - len(v)))
    return pad + v

def zero_extend_32_to(narrow_bits: Iterable[int], new_width: int) -> Tuple[int, ...]:
    v = tuple(1 if b else 0 for b in narrow_bits)
    if len(v) >= new_width:
        return v[-new_width:]
    pad = tuple(0 for _ in range(new_width - len(v)))
    return pad + v