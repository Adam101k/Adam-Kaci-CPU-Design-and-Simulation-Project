from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List
from memory import Bit

Bits = Tuple[Bit, ...]

def _zeros(n: int) -> Bits:
    return tuple(Bit(False) for _ in range(n))

def _assert_w(v: Bits, w: int) -> Bits:
    if len(v) == w:
        return v
    if len(v) < w:
        return (_zeros(w - len(v)) + v)
    return v[-w:]

@dataclass
class Reg:
    width: int
    value: Bits = None

    def __post_init__(self):
        if self.value is None:
            self.value = _zeros(self.width)
        else:
            self.value = _assert_w(self.value, self.width)

    def read(self) -> Bits:
        return self.value

    def tick(self, load: bool, d: Bits, clear: bool = False):
        if clear:
            self.value = _zeros(self.width)
        elif load:
            self.value = _assert_w(d, self.width)

class RegisterFile32:
    def __init__(self):
        self._regs: List[Bits] = [ _zeros(32) for _ in range(32) ]

    def read(self, idx: int) -> Bits:
        idx &= 31
        if idx == 0:
            return _zeros(32)
        return self._regs[idx]

    def write(self, idx: int, data: Bits, we: bool):
        idx &= 31
        if not we or idx == 0:
            return
        self._regs[idx] = _assert_w(data, 32)

    def dump_hex(self) -> List[str]:
        out = []
        for i in range(32):
            v = 0
            for b in (self._regs[i] if i != 0 else _zeros(32)):
                v = (v << 1) | (1 if b else 0)
            out.append(f"x{i}=0x{v:08X}")
        return out

class FPRegisterFile32:
    def __init__(self):
        self._regs: List[Bits] = [ _zeros(32) for _ in range(32) ]

    def read(self, idx: int) -> Bits:
        idx &= 31
        return self._regs[idx]

    def write(self, idx: int, data: Bits, we: bool):
        idx &= 31
        if we:
            self._regs[idx] = _assert_w(data, 32)

@dataclass
class FCSR:
    frm: int = 0
    nv: int = 0
    dz: int = 0
    of: int = 0
    uf: int = 0
    nx: int = 0

    def clear(self):
        self.nv = self.dz = self.of = self.uf = self.nx = 0

    def set_from_flags(self, flags: dict):
        self.nv = 1 if flags.get("invalid") else 0
        self.dz = 1 if flags.get("divide_by_zero") else 0
        self.of = 1 if flags.get("overflow") else 0
        self.uf = 1 if flags.get("underflow") else 0
        self.nx = 1 if flags.get("inexact") else 0

@dataclass
class State:
    regs: RegisterFile32
    fregs: FPRegisterFile32
    fcsr: FCSR

def make_initial_state() -> State:
    return State(regs=RegisterFile32(), fregs=FPRegisterFile32(), fcsr=FCSR())