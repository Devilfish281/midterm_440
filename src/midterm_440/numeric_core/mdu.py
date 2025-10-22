# src/midterm_440/numeric_core/mdu.py
"""Multiply/Divide Unit (MDU) for RV32M using bit-level algorithms.

We do classic **shift-add** for MUL and **restoring division** for DIV.
Everything uses 0/1 lists (LSB first) and ripple-carry adders.

RISC-V DIV rules to cover in flags/edges (summarized):
- DIV/DIVU by zero => quotient all 1s (0xFFFFFFFF), remainder = dividend.
- Signed DIV of INT_MIN by -1 => quotient INT_MIN, remainder 0 (saturates).
These match the M extension semantics.
(See RISC-V M docs and guides.)
"""

from typing import Dict, List, Tuple

# Reuse our ALU and shifter helpers so we stay pure bit-level.
from midterm_440.numeric_core.alu import add_bits, sub_bits
from midterm_440.numeric_core.bits import bits_to_u32, u32_to_bits
from midterm_440.numeric_core.shifter import sll_bits, srl_bits

# to run smoke tests, use:
# poetry run python tests\unit\smoke_mdu.py
# poetry run pytest -q tests\unit\test_mdu.py

MASK32 = 0xFFFF_FFFF
INT32_MIN = 0x80000000


# -------------------- small bit helpers --------------------
def _check32(bits: List[int]) -> None:
    if not isinstance(bits, list) or len(bits) != 32:
        raise ValueError("need 32 bits")
    for b in bits:
        if b not in (0, 1):
            raise ValueError("bits must be 0/1")


def _not_bits(bits: List[int]) -> List[int]:
    return [0 if b == 1 else 1 for b in bits]


def _add_n(a: List[int], b: List[int]) -> Tuple[List[int], int]:
    """Add same-length bit lists, return (sum_bits, carry_out)."""
    if len(a) != len(b):
        raise ValueError("lengths must match")
    out = [0] * len(a)
    cin = 0
    for i in range(len(a)):
        ai, bi = a[i], b[i]
        axb = ai ^ bi
        s = axb ^ cin
        cout = (ai & bi) | (cin & axb)
        out[i] = s
        cin = cout
    return out, cin


def _sub_n(a: List[int], b: List[int]) -> Tuple[List[int], int]:
    """Compute a - b as a + (~b + 1); returns (diff, borrow_flag_like)."""
    nb = _not_bits(b)
    tmp, cin = _add_n(a, nb)
    diff, cin2 = _add_n(tmp, [1] + [0] * (len(a) - 1))
    # For two's complement, final carry-out 1 => no borrow.
    borrow = 0 if cin2 == 1 else 1
    return diff, borrow


def _sll_n(bits: List[int], k: int) -> List[int]:
    out = bits[:]
    stages = (1, 2, 4, 8, 16, 32, 64)
    for idx, st in enumerate(stages):
        if (k >> idx) & 1:
            tmp = [0] * len(out)
            for i in range(len(out)):
                if i >= st:
                    tmp[i] = out[i - st]
            out = tmp
    return out


def _srl_n(bits: List[int], k: int, fill: int = 0) -> List[int]:
    out = bits[:]
    stages = (1, 2, 4, 8, 16, 32, 64)
    for idx, st in enumerate(stages):
        if (k >> idx) & 1:
            tmp = [fill] * len(out)
            for i in range(len(out)):
                j = i + st
                if j < len(out):
                    tmp[i] = out[j]
            out = tmp
    return out


def _sign_extend_to_64(x: List[int]) -> List[int]:
    sign = x[31]
    return x[:] + [sign] * 32


def _zero_extend_to_64(x: List[int]) -> List[int]:
    return x[:] + [0] * 32


def _twos_neg(bits: List[int]) -> List[int]:
    inv = _not_bits(bits)
    res, _ = _add_n(inv, [1] + [0] * (len(bits) - 1))
    return res


def _is_zero(bits: List[int]) -> bool:
    return all(b == 0 for b in bits)


# -------------------- MUL (shift-add) --------------------
def mul_shift_add(rs1_bits: List[int], rs2_bits: List[int]) -> Dict[str, object]:
    """Signed 32×32 → low32 product using classic shift-add with trace.
    Trace shows step#, add?, acc_low32, acc_hi32, mul_bit.
    Overflow flag = 1 when the true 64-bit signed product doesn't fit in 32-bit signed.
    (Shift–add idea: add shifted multiplicand when current multiplier bit is 1.)
    """
    _check32(rs1_bits)
    _check32(rs2_bits)
    trace: List[dict] = []
    # Make signed 64-bit versions so negatives work naturally via two's complement.
    a64 = _sign_extend_to_64(rs1_bits)
    b32 = rs2_bits[:]
    acc = [0] * 64
    # Loop over 32 bits of the multiplier (LSB first).
    for i in range(32):
        add_now = 1 if b32[i] == 1 else 0
        if add_now:
            addend = _sll_n(a64, i)
            acc, _ = _add_n(acc, addend)
        # Save a small snapshot each step (not too spammy).
        low32 = acc[:32]
        hi32 = acc[32:]
        trace.append(
            {
                "step": i,
                "mul_bit": int(b32[i]),
                "added": add_now,
                "acc_low32_hex": f"0x{bits_to_u32(low32):08X}",
                "acc_hi32_hex": f"0x{bits_to_u32(hi32):08X}",
            }
        )
    # Result low 32 bits is MUL rd.
    rd_bits = acc[:32]
    # Overflow check: does the full 64-bit signed product fit in 32-bit signed?
    # That means upper 33 bits must all equal bit31 of rd (sign).
    sign32 = rd_bits[31]
    # Build the true 64-bit sign: acc[63] is sign of product.
    overflow = 0
    # If any high bit (bits 32..63) differs from sign32, it won't fit.
    for j in range(32, 64):
        if acc[j] != sign32:
            overflow = 1
            break
    return {"rd_bits": rd_bits, "overflow": overflow, "trace": trace}


# -------------------- DIV (restoring division) --------------------
def _cmp_unsigned(a: List[int], b: List[int]) -> int:
    """Compare same-length unsigned bit lists (MSB first compare)."""
    assert len(a) == len(b)
    for i in range(len(a) - 1, -1, -1):
        if a[i] != b[i]:
            return 1 if a[i] > b[i] else -1
    return 0


def _abs_sign(bits: List[int]) -> Tuple[List[int], int]:
    """Return (abs_bits, sign) for 32-bit two's complement input."""
    if bits[31] == 1:
        return _twos_neg(bits), 1
    else:
        return bits[:], 0


def _clip32(x: List[int]) -> List[int]:
    return x[:32]


def div_restoring(
    dividend_bits: List[int], divisor_bits: List[int], signed: bool = True
) -> Dict[str, object]:
    """Binary restoring division with 32 iterations and a simple trace.
    - If signed=True: handle signs like RISC-V DIV/REM (quot trunc toward 0; rem same sign as dividend).
    - Edge cases: div-by-zero and INT_MIN/-1 per RISC-V M.
    """
    _check32(dividend_bits)
    _check32(divisor_bits)
    flags = {"div_by_zero": 0, "overflow": 0}
    trace: List[dict] = []

    # ---- Handle divide-by-zero per RISC-V M rules ----
    if _is_zero(divisor_bits):
        flags["div_by_zero"] = 1
        q_bits = [1] * 32  # 0xFFFFFFFF
        r_bits = dividend_bits[:]  # remainder = dividend
        return {
            "q_bits": q_bits,
            "r_bits": r_bits,
            "flags": flags,
            "trace": trace,
        }

    # Signed path: map to unsigned by taking absolute values, but remember signs.
    if signed:
        # INT_MIN / -1 special: quotient = INT_MIN, remainder = 0 (overflow flag just for grading visibility).
        if (
            bits_to_u32(dividend_bits) == INT32_MIN
            and bits_to_u32(divisor_bits) == MASK32
        ):
            q_bits = u32_to_bits(INT32_MIN)
            r_bits = u32_to_bits(0)
            flags["overflow"] = 1
            return {
                "q_bits": q_bits,
                "r_bits": r_bits,
                "flags": flags,
                "trace": trace,
            }
        dvd_abs, dvd_sign = _abs_sign(dividend_bits)
        dvs_abs, dvs_sign = _abs_sign(divisor_bits)
        q_sign = dvd_sign ^ dvs_sign
    else:  # unsigned mode
        dvd_abs, dvs_abs = dividend_bits[:], divisor_bits[:]
        q_sign = 0

    # ---- Restoring division (unsigned core) ----
    # We keep remainder as 33 bits so it can go negative during subtract.
    R = [0] * 33  # remainder
    Q = dvd_abs[:]  # quotient register starts as dividend
    D = dvs_abs[:]  # divisor (32)
    # Turn D into 33-bit with leading 0 so widths match R during subtract.
    D33 = D[:] + [0]

    for step in range(32):
        # Left shift (R,Q) as one 65-bit register by 1:
        # new R = (R << 1) | Q[31]; new Q = (Q << 1).
        # Do it manually in LSB-first form.
        msb_q = Q[31]
        R = [msb_q] + R[:32]  # shift left R by 1 and bring in top bit of Q
        Q = [0] + Q[:31]  # shift left Q by 1 (insert 0)
        # Try subtract: R = R - D33
        R_try, borrow = _sub_n(R, D33)
        if R_try[32] == 1:  # if R became negative (MSB of 33 is sign)
            # restore (undo subtract), quotient bit = 0
            qb = 0
            # R stays as previous value (already in R), so keep R not R_try
        else:
            # keep the subtraction, quotient bit = 1
            R = R_try
            qb = 1
        Q[0] = qb  # write the new low bit of Q
        # Record a small trace row.
        trace.append(
            {
                "step": step,
                "qb": qb,
                "R_top_hex": f"0x{bits_to_u32(R[1:33]):08X}",  # 32 LSBs of R
                "Q_hex": f"0x{bits_to_u32(Q):08X}",
            }
        )

    q_bits_unsigned = Q
    r_bits_unsigned = R[0:32]  # low 32 of remainder

    # ---- Fix signs back for signed mode ----
    if signed and q_sign == 1:
        q_bits_unsigned = _twos_neg(q_bits_unsigned)
    if signed and (dividend_bits[31] == 1):  # remainder has same sign as dividend
        if not _is_zero(r_bits_unsigned):
            r_bits_unsigned = _twos_neg(r_bits_unsigned)

    q_bits = _clip32(q_bits_unsigned)
    r_bits = _clip32(r_bits_unsigned)
    return {
        "q_bits": q_bits,
        "r_bits": r_bits,
        "flags": flags,
        "trace": trace,
    }
