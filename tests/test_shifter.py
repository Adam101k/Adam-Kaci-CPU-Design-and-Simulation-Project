import unittest
from memory import Bit
from shifter import shift32

def _bits32(x):
    # Accept int (e.g., 0xDEADBEEF) or hex string ("0xDEADBEEF" or "DEADBEEF")
    if isinstance(x, int):
        v = x & 0xFFFFFFFF
    else:
        s = str(x).strip().lower().replace("0x", "")
        v = int(s, 16) & 0xFFFFFFFF
    return tuple(Bit(bool((v >> i) & 1)) for i in range(31, -1, -1))

def _hex32(b):
    v=0
    for x in b: v=(v<<1)|(1 if x else 0)
    return f"0x{v:08X}"

class TestShifter(unittest.TestCase):
    def test_sll(self):
        a=_bits32(0x00000003)
        s=_bits32(0x00000004)
        self.assertEqual(_hex32(shift32(a,s,"SLL")), "0x00000030")
    def test_srl(self):
        a=_bits32(0x80000001)
        s=_bits32(0x00000001)
        self.assertEqual(_hex32(shift32(a,s,"SRL")), "0x40000000")
    def test_sra(self):
        a=_bits32(0x80000001)
        s=_bits32(0x00000001)
        self.assertEqual(_hex32(shift32(a,s,"SRA")), "0xC0000000")
