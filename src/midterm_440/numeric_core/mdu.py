# src/midterm_440/numeric_core/mdu.py
"""Multiply/Divide Unit (MDU) for RV32M using bit-level algorithms.

**Multiply (shift-add)** and **Divide (restoring or non-restoring)** are implemented
as multi-step algorithms that expose per-iteration traces.

Division edge cases (per RISC-V M):
- DIV x/0 → q = -1 (0xFFFFFFFF), r = dividend (for signed DIV).
- DIVU x/0 → q = 0xFFFFFFFF, r = dividend (for unsigned DIVU).
- DIV INT_MIN / -1 → q = INT_MIN (0x80000000), r = 0.

Overflow grading hint: set an overflow flag when the true 64-bit product
is not representable as a signed 32-bit result (even though RV32M truncates).
"""

from typing import Dict, List, Tuple


def mul_shift_add(rs1_bits: List[int], rs2_bits: List[int]) -> Dict[str, object]:
    """Signed 32×32 → low32 product via classic shift-add with trace.

    :param List[int] rs1_bits: Multiplicand, 32-bit LSB-first.
    :param List[int] rs2_bits: Multiplier, 32-bit LSB-first.
    :returns: ``{'rd_bits': List[int], 'overflow': int, 'trace': List[dict]}``.
    :rtype: Dict[str, object]
    """
    raise NotImplementedError("mul_shift_add not implemented")


def div_restoring(
    dividend_bits: List[int], divisor_bits: List[int], signed: bool = True
) -> Dict[str, object]:
    """Restoring division with per-iteration remainder/quotient trace.

    :param List[int] dividend_bits: 32-bit dividend, LSB first.
    :param List[int] divisor_bits: 32-bit divisor, LSB first.
    :param bool signed: If True perform signed DIV/REM; else DIVU/REMU.
    :returns: ``{'q_bits': List[int], 'r_bits': List[int], 'flags': dict, 'trace': List[dict]}``.
    :rtype: Dict[str, object]
    :raises ZeroDivisionError: For divisor==0 (you may intercept to match RV32M).
    """
    raise NotImplementedError("div_restoring not implemented")
