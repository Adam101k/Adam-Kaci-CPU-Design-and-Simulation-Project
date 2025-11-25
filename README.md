# Adam Kaci CPU Design and Simulation Project

In this project, I designed and simulated a simple 32-bit RISC-V CPU that implements a subset of the RV32I (32-bit base integer, little-endian) instruction set architecture (ISA). 

## Features

- **Two’s-Complement Toolkit (RV32 width)**
  - Encode/decode 32-bit two’s-complement
  - Sign/zero extend helpers
  - Pretty printers (hex, binary grouped by **bytes**)
- **ALU (RV32I subset)**
  - `ADD`, `SUB`, `AND`, `OR`, `XOR`, `SLL`, `SRL`, `SRA`
  - Flags: **N** (negative), **Z** (zero), **C** (carry), **V** (signed overflow)
- **Shifter**
  - 5-stage barrel shifter (1/2/4/8/16)
- **MDU (RV32M multiply/divide)**
  - Multiply: `MUL` (low 32), `MULH`, `MULHU`, `MULHSU`
  - Divide/Remain: `DIV`, `DIVU`, `REM`, `REMU` (restoring division)
  - RISC-V edge semantics (e.g., DIV by 0, INT_MIN / −1), plus step-by-step **traces**
- **FPU (IEEE-754 float32)**
  - Pack/unpack, `fadd`, `fsub`, `fmul`
  - Round-to-Nearest-Even (RNE)
  - Flags: **invalid**, **divide_by_zero**, **overflow**, **underflow**, **inexact**
  - Step-by-step **traces** (align, op, normalize, round)
- **FCSR**
  - `frm` (rounding mode; defaults to RNE=0)
  - `fflags`: NV, DZ, OF, UF, NX
  - CLI shows FCSR bits for FPU ops
- **Register Files**
  - Integer RF (x0 hard-wired to 0), FP RF, simple `Reg` primitive
- **Program Image Loader**
  - Reads standard `.hex` file (one 32-bit word per line)
- **Tiny “runner”**
  - Executes a minimal demo program image to show core pieces working

## Required Initial Setup

- Python **3.12+**
- Windows PowerShell, a POSIX shell, or some IDE Terminal

### Install (editable)
```bash
python -m venv .venv
# Windows PowerShell:
. .venv/Scripts/activate
# macOS/Linux:
# source .venv/bin/activate

pip install -e .
pytest
```
## How to run program

The project installs a console script named `SD-sim`.

### Command summary

```bash
SD-sim [-h] {add,sub,fadd,fsub,fmul,mul,div,loadhex,runhex} ...
```
### 1. Integer ALU ops (two’s-complement 32-bit)

```bash
SD-sim add <a> <b>
SD-sim sub <a> <b>
```
- `<a>`, `<b>`: Python int literals (accepts decimal like 5 or bases like 0xFF, 0b1010).
- Output: 32-bit result + ALU flags ```{N,Z,C,V}```.

### Examples

```bash
SD-sim add 0x7FFFFFFF 1
SD-sim sub 0x80000000 1
```

## AI Usage
AI was used for creating initial file structure setup "I need to setup my initial file structure". The suggestion was used to setup the initial pyproject.toml.