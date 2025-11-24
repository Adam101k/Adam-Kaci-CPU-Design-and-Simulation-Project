import unittest
from memory import Bit
from mdu import mdu_mul

def hex32_to_bits_msb(h: str):
    v = int(h, 16) & 0xFFFFFFFF
    return tuple(Bit(bool((v >> i) & 1)) for i in range(31, -1, -1))

def bits_to_hex32(bits):
    v = 0
    for b in bits:
        v = (v << 1) | (1 if b else 0)
    return f"0x{v:08X}"

class TestMDU_MULH(unittest.TestCase):
    def test_mulh_signed_signed(self):
        # 12345678 * -87654321
        a = hex32_to_bits_msb("00BC614E")   #  12345678
        b = hex32_to_bits_msb("FAC6804F")   # -87654321 (correct two's-comp)
        out = mdu_mul("MULH", a, b)
        self.assertEqual(bits_to_hex32(out["rd_bits"]), "0xFFFC27C9")  # expected from spec
        # Not asserting trace content here; shift-add steps are produced

    def test_mulhu_unsigned_unsigned(self):
        # 0x80000000 * 0x00000002 = 0x00000001_00000000 -> high = 0x00000001
        a = hex32_to_bits_msb("80000000")
        b = hex32_to_bits_msb("00000002")
        out = mdu_mul("MULHU", a, b)
        self.assertEqual(bits_to_hex32(out["rd_bits"]), "0x00000001")

    def test_mulhsu_signed_unsigned(self):
        # (-1) * 2 = -2 -> full64 = 0xFFFF_FFFF_FFFF_FFFE -> high = 0xFFFFFFFF
        a = hex32_to_bits_msb("FFFFFFFF")  # -1
        b = hex32_to_bits_msb("00000002")  #  2
        out = mdu_mul("MULHSU", a, b)
        self.assertEqual(bits_to_hex32(out["rd_bits"]), "0xFFFFFFFF")
