from __future__ import annotations
from typing import Dict, Iterable, Tuple

WIDTH = 32
MASK32 = 0xFFFFFFFF
INT_MIN = -(1 << 31)
INT_MAX = (1 << 31) - 1

_HEX_DIGITS = "0123456789ABCDEF"

# Pretty-printers (no bin/hex)

def _nibble_to_hex(n4: Tuple[int, int, int, int]) -> str:

def _bits32_from_int_adapter(value: int) -> Tuple[int, ...]:

def _int_from_bits32_adapter(bits32: Iterable[int]) -> int:

def _bits_to_bin_grouped(bits32: Iterable[int], group: int = 4, sep: str = "_") -> str:

def _bits_to_hex32(bits32: Iterable[int]) -> str:

def encode_twos_complement(value: int) -> Dict[str, object]:

def decode_twos_complement(bits: str | int) -> Dict[str, int]:

def sign_extend_32_to(narrow_bits: Iterable[int], new_width: int) -> Tuple[int, ...]:

def zero_extend_32_to(narrow_bits: Iterable[int], new_width: int) -> Tuple[int, ...]:
