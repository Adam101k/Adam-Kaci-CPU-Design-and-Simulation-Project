from dataclasses import dataclass

@dataclass
class FCSR:
    frm: int = 0    # rounding mode (RNE)
    nv: int = 0     # invalid
    dz: int = 0     # divide-by-zero (unused for add/sub/mul)
    of: int = 0     # overflow
    uf: int = 0     # underflow
    nx: int = 0     # inexact

    def clear_flags(self):
        self.nv = self.dz = self.of = self.uf = self.nx = 0
