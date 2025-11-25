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

### 2. Float32 FPU ops (hex bit patterns)

```bash
SD-sim fadd <hex32> <hex32>
SD-sim fsub <hex32> <hex32>
SD-sim fmul <hex32> <hex32>
```
- Operands are raw hex bit patterns (8 hex digits, with or without 0x).
- Output: result hex + detailed flags + FCSR view.
- Prints algorithm trace lines when relevant.

### Examples

```bash
SD-sim fadd 3FC00000 40100000          # 1.5 + 2.25 = 3.75
SD-sim fmul 7E967699 41200000          # ~1e38 * 10 -> +inf (OF,NX)
SD-sim fadd 7F800000 FF800000          # +inf + -inf -> qNaN (NV)
```

### Multiply/Divide Unit (RV32M)

```bash
SD-sim mul <a:int> <b:int> [--trace]
SD-sim div <a:int> <b:int> [--unsigned] [--trace]
```
- **mul** computes **MUL** (low 32) with an overflow visibility flag (if 64-bit product doesn’t fit a signed 32-bit).
- **div** supports **DIV** (signed) and **DIVU** (**--unsigned**). Remainder behavior matches RISC-V. Division by zero and **INT_MIN / -1** edges are handled.
- **--trace** shows per-step shift-add (mul) or restoring division iterations.

### Examples

```bash
SD-sim mul 12345678 -87654321 --trace
SD-sim div -7 3
SD-sim div 0x80000000 3 --unsigned --trace
```

### Program image (hex) loader & mini runner

```bash
SD-sim loadhex <path>
SD-sim runhex  <path> [--trace]
```
- **loadhex** just parses and reports how many 32-bit words were loaded.
- **runhex** executes a tiny demonstration over your core components (simple ALU/shifter/FPU/MDU demo path, not a full ISA interpreter), reporting final register/memory values consistent with the provided sample.

### Example

```bash

```
Smaple file (as provided): [test_base.hex](./text_base.hex)

## AI Usage

- Assisted creating initial file structure setup "I need to setup my initial file structure". The suggestion was used to setup the initial pyproject.toml.

- Assisted in creating test prompts for ALU, FPU, MDU files. Such prompts included "I want to test the following file to see if it's working as intended, give me a skeleton test file in python"

- Assisted in formating **README.md**, prompts included "This is what my program does: _, can you format this in a .md format similar to what I already have here: _"