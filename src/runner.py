from __future__ import annotations
from typing import Tuple
from memory import Bit
from loader import load_hex_file

# Simple host-side interpreter for a small RV32I subset:
# addi, add, sub, lui, lw, sw, beq, jal

def _bits_to_u32(bits: Tuple[Bit, ...]) -> int:
    v = 0
    for b in bits:
        v = (v << 1) | (1 if b else 0)
    return v & 0xFFFFFFFF

def _sign_extend(val: int, bits: int) -> int:
    m = 1 << (bits - 1)
    val = val & ((1 << bits) - 1)
    return (val ^ m) - m

def _u32(x: int) -> int:
    return x & 0xFFFFFFFF

def _read_u32(mem: dict, addr: int) -> int:
    # word-aligned simple memory (word-addressed for the sample)
    return mem.get(addr, 0)

def _write_u32(mem: dict, addr: int, val: int):
    mem[addr] = _u32(val)

def run_hex(path: str, max_steps: int = 1000, trace: bool = False):
    # Load program: each line is a 32-bit word (one instruction)
    words = load_hex_file(path)  # -> list[Tuple[Bit,...]]
    prog = [_bits_to_u32(w) for w in words]

    # Simple state
    regs = [0] * 32  # x0..x31
    pc = 0
    mem = {}         # word-addressed RAM (for sample’s 0x0001_0000)

    def x(i): return regs[i] & 0xFFFFFFFF
    def setx(i, v):
        if i != 0:
            regs[i] = _u32(v)

    steps = 0
    while steps < max_steps:
        if pc // 4 < 0 or pc // 4 >= len(prog):
            if trace: print(f"PC out of range: 0x{pc:08X}")
            break
        inst = prog[pc // 4]
        if trace: print(f"PC=0x{pc:08X} INST=0x{inst:08X}")

        opcode = inst & 0x7F
        rd     = (inst >> 7) & 0x1F
        funct3 = (inst >> 12) & 0x7
        rs1    = (inst >> 15) & 0x1F
        rs2    = (inst >> 20) & 0x1F
        funct7 = (inst >> 25) & 0x7F

        next_pc = pc + 4

        if opcode == 0x13:  # OP-IMM (ADDI)
            imm = _sign_extend(inst >> 20, 12)
            if funct3 == 0x0:  # ADDI
                setx(rd, x(rs1) + imm)
                if trace: print(f"  addi x{rd}, x{rs1}, {imm} -> x{rd}=0x{regs[rd]:08X}")

        elif opcode == 0x33:  # OP
            if funct3 == 0x0 and funct7 == 0x00:  # ADD
                setx(rd, x(rs1) + x(rs2))
                if trace: print(f"  add x{rd}, x{rs1}, x{rs2} -> x{rd}=0x{regs[rd]:08X}")
            elif funct3 == 0x0 and funct7 == 0x20:  # SUB
                setx(rd, x(rs1) - x(rs2))
                if trace: print(f"  sub x{rd}, x{rs1}, x{rs2} -> x{rd}=0x{regs[rd]:08X}")

        elif opcode == 0x37:  # LUI
            imm_u = inst & 0xFFFFF000
            setx(rd, imm_u)
            if trace: print(f"  lui x{rd}, 0x{imm_u>>12:05X} -> x{rd}=0x{regs[rd]:08X}")

        elif opcode == 0x23:  # STORE (SW)
            imm = ((inst >> 7) & 0x1F) | (((inst >> 25) & 0x7F) << 5)
            imm = _sign_extend(imm, 12)
            if funct3 == 0x2:  # SW
                addr = _u32(x(rs1) + imm)
                _write_u32(mem, addr, x(rs2))
                if trace: print(f"  sw x{rs2}, {imm}(x{rs1}) -> mem[0x{addr:08X}]=0x{_read_u32(mem,addr):08X}")

        elif opcode == 0x03:  # LOAD (LW)
            imm = _sign_extend(inst >> 20, 12)
            if funct3 == 0x2:  # LW
                addr = _u32(x(rs1) + imm)
                setx(rd, _read_u32(mem, addr))
                if trace: print(f"  lw x{rd}, {imm}(x{rs1}) -> x{rd}=0x{regs[rd]:08X}")

        elif opcode == 0x63:  # BRANCH (BEQ)
            imm = (
                ((inst >> 7) & 0x1) << 11 |
                ((inst >> 8) & 0xF) << 1  |
                ((inst >> 25) & 0x3F) << 5 |
                ((inst >> 31) & 0x1) << 12
            )
            imm = _sign_extend(imm, 13)
            if funct3 == 0x0:  # BEQ
                if x(rs1) == x(rs2):
                    next_pc = _u32(pc + imm)
                if trace: print(f"  beq x{rs1}, x{rs2}, {imm} -> pc=0x{next_pc:08X}")

        elif opcode == 0x6F:  # JAL
            imm = (
                ((inst >> 21) & 0x3FF) << 1 |
                ((inst >> 20) & 0x1) << 11  |
                ((inst >> 12) & 0xFF) << 12 |
                ((inst >> 31) & 0x1) << 20
            )
            imm = _sign_extend(imm, 21)
            setx(rd, pc + 4)
            next_pc = _u32(pc + imm)
            if trace: print(f"  jal x{rd}, {imm} -> pc=0x{next_pc:08X}")

        else:
            if trace: print(f"  (unimplemented opcode 0x{opcode:02X})")
            break

        pc = next_pc
        regs[0] = 0
        steps += 1

        # Safety stop if we detect the infinite loop (JAL x0, 0)
        if opcode == 0x6F and rd == 0 and next_pc == pc:
            if trace: print("  halt (jal x0, 0)")
            break

    return {
        "regs": [r & 0xFFFFFFFF for r in regs],
        "mem": mem,
        "pc": pc,
        "steps": steps
    }