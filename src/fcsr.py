from dataclasses import dataclass

@dataclass
class FCSR:
    frm: int = 0  # 0=RNE; (extra credit: support others)
    nv: int = 0   # invalid
    dz: int = 0   # divide-by-zero
    of: int = 0   # overflow
    uf: int = 0   # underflow
    nx: int = 0   # inexact

    def set_from_flags(self, flags: dict):
        self.nv = 1 if flags.get("invalid") else 0
        self.dz = 1 if flags.get("divide_by_zero") else 0
        self.of = 1 if flags.get("overflow") else 0
        self.uf = 1 if flags.get("underflow") else 0
        self.nx = 1 if flags.get("inexact") else 0

    def clear(self):
        self.nv = self.dz = self.of = self.uf = self.nx = 0
