import unittest
from memory import Bit
from fpu import fadd_f32, fmul_f32
from registers import FCSR

def _bits(hex32):
    v = int(hex32,16)&0xFFFFFFFF
    return tuple(Bit(bool((v>>i)&1)) for i in range(31,-1,-1))

class TestFCSR(unittest.TestCase):
    def test_overflow_underflow_inexact(self):
        fcsr = FCSR()
        # overflow: ~1e38 * 10 -> +inf; OF+NX
        a = _bits("7E967699"); b = _bits("41200000")
        out = fmul_f32(a,b); fcsr.set_from_flags(out["flags"])
        self.assertEqual((fcsr.nv,fcsr.dz,fcsr.of,fcsr.uf,fcsr.nx), (0,0,1,0,1))

        # underflow: MIN_NORMAL * 0.5 -> subnormal; UF set (NX may be 0/1 depending on rounding)
        fcsr.clear()
        a = _bits("00800000"); b = _bits("3F000000")
        out = fmul_f32(a,b); fcsr.set_from_flags(out["flags"])
        self.assertEqual((fcsr.of,fcsr.uf), (0,1))

    def test_invalid_nan(self):
        fcsr = FCSR()
        # invalid: +inf + -inf
        pinf=_bits("7F800000"); ninf=_bits("FF800000")
        out = fadd_f32(pinf, ninf); fcsr.set_from_flags(out["flags"])
        self.assertEqual((fcsr.nv,fcsr.dz,fcsr.of,fcsr.uf,fcsr.nx), (1,0,0,0,0))
