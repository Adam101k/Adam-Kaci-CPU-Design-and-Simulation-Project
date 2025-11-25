import unittest
from memory import Bit
from mdu import mdu_mul, mdu_div

def hex32_to_bits_msb(h: str):
    v = int(h, 16) & 0xFFFFFFFF
    return tuple(Bit(bool((v >> i) & 1)) for i in range(31, -1, -1))

def bits_to_hex32(bits):
    v = 0
    for b in bits:
        v = (v << 1) | (1 if b else 0)
    return f"0x{v:08X}"

class TestMDU(unittest.TestCase):

    # AI-BEGIN
    def test_mul_low32_and_overflow_flag(self):
        # 12345678 * -87654321
        a = hex32_to_bits_msb("00BC614E")   # 12345678
        b = hex32_to_bits_msb("FAC6804F")   # -87654321 two's-comp
        out = mdu_mul("MUL", a, b)
        self.assertEqual(bits_to_hex32(out["rd_bits"]), "0xD91D0712")
        self.assertTrue(out["flags"]["overflow"])
        self.assertTrue(any("MUL step" in t for t in out["trace"]))

    def test_div_signed_basic(self):
        # -7 / 3 => q = -2, r = -1
        a = hex32_to_bits_msb("FFFFFFF9")   # -7
        b = hex32_to_bits_msb("00000003")   # 3
        out = mdu_div("DIV", a, b)
        self.assertEqual(bits_to_hex32(out["q_bits"]), "0xFFFFFFFE")
        self.assertEqual(bits_to_hex32(out["r_bits"]), "0xFFFFFFFF")
        self.assertTrue(any("DIV step" in t for t in out["trace"]))

    def test_divu_basic(self):
        a = hex32_to_bits_msb("80000000")
        b = hex32_to_bits_msb("00000003")
        out = mdu_div("DIVU", a, b)
        self.assertEqual(bits_to_hex32(out["q_bits"]), "0x2AAAAAAA")
        self.assertEqual(bits_to_hex32(out["r_bits"]), "0x00000002")

    def test_divide_by_zero_semantics(self):
        a = hex32_to_bits_msb("12345678")
        b = hex32_to_bits_msb("00000000")
        sdiv = mdu_div("DIV", a, b)
        udiv = mdu_div("DIVU", a, b)
        self.assertEqual(bits_to_hex32(sdiv["q_bits"]), "0xFFFFFFFF")
        self.assertEqual(bits_to_hex32(sdiv["r_bits"]), "0x12345678")
        self.assertEqual(bits_to_hex32(udiv["q_bits"]), "0xFFFFFFFF")
        self.assertEqual(bits_to_hex32(udiv["r_bits"]), "0x12345678")

    def test_signed_intmin_div_neg1(self):
        a = hex32_to_bits_msb("80000000")  # INT_MIN
        b = hex32_to_bits_msb("FFFFFFFF")  # -1
        out = mdu_div("DIV", a, b)
        self.assertEqual(bits_to_hex32(out["q_bits"]), "0x80000000")
        self.assertEqual(bits_to_hex32(out["r_bits"]), "0x00000000")
        # Overflow flag is for grading visibility per spec
        self.assertTrue(out["flags"]["overflow"])
    ## AI-END