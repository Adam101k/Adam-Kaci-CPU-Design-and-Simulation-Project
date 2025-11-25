import unittest
from memory import Bit
from registers import Reg, RegisterFile32, FPRegisterFile32, make_initial_state

def _bits32(u: int):
    u &= 0xFFFFFFFF
    return tuple(Bit(bool((u >> i) & 1)) for i in range(31, -1, -1))

def _u32(bits):
    v=0
    for b in bits: v=(v<<1)|(1 if b else 0)
    return v & 0xFFFFFFFF

class TestReg(unittest.TestCase):
    def test_reg_load_and_clear(self):
        r = Reg(32)
        self.assertEqual(_u32(r.read()), 0)
        r.tick(load=True, d=_bits32(0xDEADBEEF), clear=False)
        self.assertEqual(_u32(r.read()), 0xDEADBEEF)
        r.tick(load=False, d=_bits32(0), clear=True)
        self.assertEqual(_u32(r.read()), 0x00000000)

class TestRegisterFile32(unittest.TestCase):
    def test_x0_is_hardwired_zero(self):
        rf = RegisterFile32()
        rf.write(0, _bits32(0xFFFFFFFF), True)
        self.assertEqual(_u32(rf.read(0)), 0x00000000)

    def test_read_write(self):
        rf = RegisterFile32()
        rf.write(5, _bits32(0x12345678), True)
        self.assertEqual(_u32(rf.read(5)), 0x12345678)
        rf.write(5, _bits32(0xAABBCCDD), True)
        self.assertEqual(_u32(rf.read(5)), 0xAABBCCDD)

class TestFPRegisterFile32(unittest.TestCase):
    def test_fp_write_read(self):
        fr = FPRegisterFile32()
        fr.write(3, _bits32(0x3F800000), True)  # 1.0f
        self.assertEqual(_u32(fr.read(3)), 0x3F800000)

class TestMakeState(unittest.TestCase):
    def test_state_constructs(self):
        st = make_initial_state()
        self.assertEqual(_u32(st.regs.read(0)), 0)
        self.assertEqual(_u32(st.fregs.read(0)), 0)
        # fcsr defaults:
        self.assertEqual((st.fcsr.frm, st.fcsr.nv, st.fcsr.dz, st.fcsr.of, st.fcsr.uf, st.fcsr.nx), (0,0,0,0,0,0))
