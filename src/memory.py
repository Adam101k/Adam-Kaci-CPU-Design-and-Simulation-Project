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