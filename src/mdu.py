from __future__ import annotations
from typing import Tuple, Dict, List, Literal
from memory import Bit
import gates as g

Bits = Tuple[Bit, ...]
MulOp = Literal["MUL"] # (extend later: "MULH", "MULHU", "MULHSU")
DivOp = Literal["DIV", "DIVU", "REM", "REMU"]

