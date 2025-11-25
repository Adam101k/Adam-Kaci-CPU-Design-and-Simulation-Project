import unittest
from memory import Bit
from mdu import mdu_div

def _bits(h):
    v=int(h,16)&0xFFFFFFFF
    return tuple(Bit(bool((v>>i)&1)) for i in range(31,-1,-1))

def _hex(bits):
    v=0
    for b in bits: v=(v<<1)|(1 if b else 0)
    return f"0x{v:08X}"

class TestMDU_Unsigned(unittest.TestCase):
    def test_divu_basic(self):
        a=_bits("80000000"); b=_bits("00000003")
        out=mdu_div("DIVU",a,b)
        self.assertEqual(_hex(out["q_bits"]), "0x2AAAAAAA")
        self.assertEqual(_hex(out["r_bits"]), "0x00000002")

    def test_divu_by_zero(self):
        a=_bits("DEADBEEF"); b=_bits("00000000")
        out=mdu_div("DIVU",a,b)
        self.assertEqual(_hex(out["q_bits"]), "0xFFFFFFFF")
        self.assertEqual(_hex(out["r_bits"]), "0xDEADBEEF")
