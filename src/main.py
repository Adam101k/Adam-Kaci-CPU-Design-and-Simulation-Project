import argparse
from memory import Bit
from twos import encode_twos_complement
from alu import ALU32, alu32
from fpu import fadd_f32, fsub_f32, fmul_f32
from mdu import mdu_mul, mdu_div
from loader import load_hex_file
from runner import run_hex
from registers import FCSR

def _bits32_from_int(v: int):
    u = v & 0xFFFFFFFF
    return tuple(Bit(bool((u>>i)&1)) for i in range(31,-1,-1))

def auto_int(s: str) -> int:
    # accepts decimal or prefixed bases: 0x..., 0b..., 0o...
    return int(s, 0)

def main():
    p = argparse.ArgumentParser(prog="SD-sim")
    sub = p.add_subparsers(dest="cmd")

    # if no cmd is given, default to printing help
    p.set_defaults(cmd=None)

    pa = sub.add_parser("add");  pa.add_argument("a"); pa.add_argument("b")
    ps = sub.add_parser("sub");  ps.add_argument("a"); ps.add_argument("b")
    pf = sub.add_parser("fadd"); pf.add_argument("ahex"); pf.add_argument("bhex")
    pfs= sub.add_parser("fsub"); pfs.add_argument("ahex"); pfs.add_argument("bhex")
    pfm= sub.add_parser("fmul"); pfm.add_argument("ahex"); pfm.add_argument("bhex")
    pm = sub.add_parser("mul"); pm.add_argument("a", type=auto_int); pm.add_argument("b", type=auto_int); pm.add_argument("--trace", action="store_true") 
    pd = sub.add_parser("div"); pd.add_argument("a", type=auto_int); pd.add_argument("b", type=auto_int); pd.add_argument("--unsigned", action="store_true"); pd.add_argument("--trace", action="store_true");
    pl = sub.add_parser("loadhex"); pl.add_argument("path")
    pr = sub.add_parser("runhex"); pr.add_argument("path"); pr.add_argument("--trace", action="store_true"); pr.add_argument("--steps", type=int, default=200)

    args = p.parse_args()

    if args.cmd is None:
        p.print_help()
        return
    if args.cmd in ("add","sub"):
        a = int(args.a, 0); b = int(args.b, 0)
        A = _bits32_from_int(a); B = _bits32_from_int(b)
        op = "ADD" if args.cmd=="add" else "SUB"
        out = ALU32().exec(A,B,op)
        v = 0
        for bit in out["result"]: v=(v<<1)|(1 if bit else 0)
        print(f"{op}: result=0x{v:08X} flags={out['flags']}")
    elif args.cmd in ("fadd","fsub","fmul"):
        def hx(s: str):
            s = s.strip().lower().replace("0x", "")
            v = int(s, 16) & 0xFFFFFFFF
            return tuple(Bit(bool((v >> i) & 1)) for i in range(31, -1, -1))

        A = hx(args.ahex)
        B = hx(args.bhex)

        fn = {
            "fadd": fadd_f32,
            "fsub": fsub_f32,
            "fmul": fmul_f32,
        }[args.cmd]

        out = fn(A, B)

        fcsr = FCSR()  # frm defaults to 0 (RNE), which matches our FPU
        fcsr.set_from_flags(out["flags"])

        # Pack result bits into hex for display
        v = 0
        for bit in out["res_bits"]:
            v = (v << 1) | (1 if bit else 0)

        # Compose fflags as 5-bit integer: NV DZ OF UF NX => bits [4:0]
        fflags_int = (fcsr.nv << 4) | (fcsr.dz << 3) | (fcsr.of << 2) | (fcsr.uf << 1) | (fcsr.nx << 0)

        print(
            f"{args.cmd}: res=0x{v:08X} "
            f"flags={out['flags']} "
            f"FCSR(frm={fcsr.frm}, fflags=0b{fflags_int:05b} [NV:{fcsr.nv} DZ:{fcsr.dz} OF:{fcsr.of} UF:{fcsr.uf} NX:{fcsr.nx}])"
        )

        # Print trace if present
        if "trace" in out:
            for t in out["trace"]:
                print(t)

    elif args.cmd=="mul":
        A=_bits32_from_int(args.a); B=_bits32_from_int(args.b)
        out = mdu_mul("MUL", A, B)
        v=0
        for bit in out["rd_bits"]: v=(v<<1)|(1 if bit else 0)
        print(f"MUL: rd=0x{v:08X} overflow={out['flags']['overflow']}")
        if args.trace:
            for t in out["trace"]: print(t)
    elif args.cmd=="div":
        A=_bits32_from_int(args.a); B=_bits32_from_int(args.b)
        op = "DIVU" if args.unsigned else "DIV"
        out = mdu_div(op, A, B)
        q=r=0
        for bit in out["q_bits"]: q=(q<<1)|(1 if bit else 0)
        for bit in out["r_bits"]: r=(r<<1)|(1 if bit else 0)
        print(f"{op}: q=0x{q:08X} r=0x{r:08X} overflow={out['flags']['overflow']}")
        if args.trace:
            for t in out["trace"]: print(t)
    elif args.cmd=="loadhex":
        prog = load_hex_file(args.path)
        print(f"Loaded {len(prog)} words from {args.path}")
    elif args.cmd == "runhex":
        out = run_hex(args.path, max_steps=args.steps, trace=args.trace)
        regs = out["regs"]; mem = out["mem"]
        print(f"Completed in {out['steps']} steps, PC=0x{out['pc']:08X}")
        # show a few interesting regs the sample touches
        for i in (1,2,3,4,5,6):
            print(f"x{i} = 0x{regs[i]:08X}")
        # sample stores at 0x0001_0000
        addr = 0x00010000
        if addr in mem:
            print(f"mem[0x{addr:08X}] = 0x{mem[addr]:08X}")

if __name__ == "__main__":
    main()
