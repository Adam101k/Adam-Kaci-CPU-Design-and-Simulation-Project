from __future__ import annotations
from typing import Tuple, Dict, List, Literal
from memory import Bit
import gates as g

Bits = Tuple[Bit, ...]
MulOp = Literal["MUL"] # (extend later: "MULH", "MULHU", "MULHSU")
DivOp = Literal["DIV", "DIVU", "REM", "REMU"]

def _zeros(n: int) -> Bits:
    return tuple(Bit(False) for _ in range(n))

def _one_hot_lsb(n: int) -> Bits:
    return tuple(Bit(False) for _ in range(n - 1)) + (Bit(True),)

def _assert_w(v: Bits, w: int) -> Bits:
    if len(v) == w:
        return v
    if len(v) < w:
        return (_zeros(w - len(v)) + v)
    return v[-w:]

def _is_zero(v: Bits) -> bool:
    acc = Bit(False)
    for b in v:
        acc = g.or_gate(acc, b)
    return not bool(acc)

def _not_vec(a: Bits) -> Bits:
    return tuple(g.not_gate(x) for x in a)

def _add_unsigned(a: Bits, b: Bits, cin: Bit = None) -> Tuple[Bits, Bit]:
    assert len(a) == len(b)
    if cin is None:
        cin = Bit(False)
    n = len(a)
    out = [Bit(False)] * n
    carry = cin
    for i in range(n - 1, -1, -1):
        axb = g.xor_gate(a[i], b[i])
        s = g.xor_gate(axb, carry)
        c1 = g.and_gate(a[i], b[i])
        c2 = g.and_gate(axb, carry)
        carry = g.or_gate(c1, c2)
        out[i] = s
    return tuple(out), carry

def _inc_unsigned(a: Bits) -> Tuple[Bits, Bit]:
    return _add_unsigned(a, _one_hot_lsb(len(a)))

def _sub_unsigned(a: Bits, b: Bits) -> Tuple[Bits, Bit]:
    nb = _not_vec(b)
    nb1, _ = _inc_unsigned(nb)
    s, carry = _add_unsigned(a, nb1)
    borrow = g.not_gate(carry)  # carry==1 -> no borrow
    return s, borrow

def _shl_logical(a: Bits, steps: int = 1) -> Bits:
    out = list(a)
    for _ in range(steps):
        for i in range(len(out) - 1):
            out[i] = out[i + 1]
        out[-1] = Bit(False)
    return tuple(out)

def _shr_logical(a: Bits, steps: int = 1) -> Bits:
    out = list(a)
    for _ in range(steps):
        for i in range(len(out) - 1, 0, -1):
            out[i] = out[i - 1]
        out[0] = Bit(False)
    return tuple(out)

def _unsigned_less_than(a: Bits, b: Bits) -> bool:
    for i in range(len(a)):
        ai, bi = bool(a[i]), bool(b[i])
        if ai != bi:
            return (not ai) and bi
    return False

def _twos_negate(a: Bits) -> Bits:
    inv = _not_vec(a)
    one = _one_hot_lsb(len(a))
    s, _ = _add_unsigned(inv, one)
    return s

def _abs_signed32(a: Bits) -> Tuple[Bits, Bit]:
    """Return (abs(a), is_negative). a is 32-bit two's complement."""
    neg = a[0]
    return (_twos_negate(a) if bool(neg) else a), neg

def _sign_extend(v: Bits, to_w: int) -> Bits:
    s = v[0] if v else Bit(False)
    if len(v) >= to_w:
        return v[-to_w:]
    return tuple(s for _ in range(to_w - len(v))) + v

def _pack64(hi: Bits, lo: Bits) -> Bits:
    return hi + lo

def _mul_u32x32_to_u64(rs1: Bits, rs2: Bits, trace: List[str]) -> Bits:
    # Unsigned 32x32 -> 64 via shift-add. rs1 multiplicand, rs2 multiplier
    A = [Bit(False) for _ in range(64)]  # accumulator/product
    multiplicand = _assert_w(rs1, 32)
    multiplier   = _assert_w(rs2, 32)

    for i in range(32):
        lsb = multiplier[-1]
        if bool(lsb):
            # add multiplicand aligned at bit i (from LSB)
            # align multiplicand in 64-bit space:
            # left 32 bits are zeros for this simple adder injection
            aligned = list(_zeros(32)) + list(multiplicand)
            # shift left by i (i times) within 64b
            for _ in range(i):
                for j in range(63):
                    aligned[j] = aligned[j + 1]
                aligned[63] = Bit(False)
            # A = A + aligned
            carry = Bit(False)
            for k in range(63, -1, -1):
                s, carry = g.full_adder(A[k], aligned[k], carry)
                A[k] = s
            trace.append(f"MUL step{i}: add")
        # shift multiplier >> 1 (logical)
        multiplier = _shr_logical(multiplier, 1)

    return tuple(A)

def _mul_overflow_signed32(low32: Bits, full64: Bits) -> Bit:
    # Overflow if 64-bit product doesn't fit signed 32:
    # i.e., top 32 bits must be all sign-bit copies of low32[0]
    sign32 = low32[0]
    hi32 = full64[0:32]
    diff = Bit(False)
    for b in hi32:
        diff = g.or_gate(diff, g.xor_gate(b, sign32))
    return diff  # True if any bit differs -> overflow

def mdu_mul(op: MulOp, rs1: Bits, rs2: Bits) -> Dict[str, object]:
    # Mul (low 32) via unsigned shift-add
    # Returns: {'rd_bits': 32b, 'flags': {'overflow': bool}, 'trace': [str,...]}
    trace: List[str] = []
    rs1 = _assert_w(rs1, 32)
    rs2 = _assert_w(rs2, 32)

    trace.append("MUL start: 32x32 -> 64 shift-add")
    prod64 = _mul_u32x32_to_u64(rs1, rs2, trace)
    rd_bits = prod64[32:] # Low 32 bits

    of = _mul_overflow_signed32(rd_bits, prod64)
    return {"rd_bits": rd_bits, "flags": {"overflow": bool(of)}, "trace": trace}

# Division / Remainder (RV32)

def _restoring_div_unsigned(dividend: Bits, divisor: Bits, trace: List[str]) -> Tuple[Bits, Bits]:
    # Unsigned restoring division: dividend/divisor -> (quotient, remainder)
    # Iterates 32 steps; uses 33-bit remainder
    n = 32
    Q = list(_assert_w(dividend, n))
    D = _assert_w(divisor, n)
    R = list(_zeros(n + 1))  # 33-bit remainder

    trace.append("DIV start: restoring unsigned")

    for i in range(n):
        # Left shift (R,Q) by 1
        # R: <<1; bring in Q[0] into R LSB
        msb_q = Q[0]
        # shift R << 1
        for j in range(0, n):
            R[j] = R[j + 1]
        R[n] = msb_q
        # shift Q << 1
        for j in range(0, n - 1):
            Q[j] = Q[j + 1]
        Q[n - 1] = Bit(False)

        # R = R - D
        R_before = tuple(R)
        R_sub, borrow = _sub_unsigned(tuple(R), _zeros(1) + D)  # align D under low n+1 bits
        R = list(R_sub)
        if bool(borrow):
            # restore and set Q LSB=0
            R = list(R_before)
            Q[-1] = Bit(False)
            trace.append(f"DIV step{i}: restore (R<D)")
        else:
            # keep and set Q LSB=1
            Q[-1] = Bit(True)
            trace.append(f"DIV step{i}: keep (R>=D)")

    return tuple(Q), tuple(R)[-32:]  # quotient, remainder (low 32 of 33-bit)

def _neg_if(bit: Bit, val: Bits) -> Bits:
    return _twos_negate(val) if bool(bit) else val

def _is_int_min(x: Bits) -> bool:
    return bool(x[0]) and all(not b for b in x[1:])

def mdu_div