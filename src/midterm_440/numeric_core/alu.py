# src/midterm_440/numeric_core/alu.py
"""Ripple-carry ALU for ADD/SUB with flags N,Z,C,V (RV32).

The ALU operates on 32-bit bit arrays (LSB first) using 1-bit full adders.
No host ``+``/``-`` or shifts are used in the final implementation.

Overflow (V) rules (two's complement):
- ADD: overflow iff operands share sign and result sign differs.
- SUB: implement as ``a + (~b + 1)`` and apply ADD rule.

Flags:
- N: msb(result)
- Z: 1 if all result bits are 0
- C: carry out of MSB (for subtraction via a + (~b + 1), C=1 implies no borrow)
- V: signed overflow as above
"""

from typing import List, Tuple


def _validate_bits_32(a: List[int], b: List[int]) -> None:  # Added Code
    """Quick checks: lists, 32 bits, only 0/1."""  # Added Code
    if not (isinstance(a, list) and isinstance(b, list)):  # Added Code
        raise ValueError("a and b must be lists")  # Added Code
    if len(a) != 32 or len(b) != 32:  # Added Code
        raise ValueError("a and b must be 32 bits long")  # Added Code
    for x in a + b:  # Added Code
        if x not in (0, 1):  # Added Code
            raise ValueError("bits must be 0/1")  # Added Code


def _add_bits_with_cin(
    a: List[int], b: List[int], cin0: int
) -> Tuple[List[int], int, int, int, int]:  # Added Code
    """Full-adder ripple with selectable initial carry-in (0 or 1)."""  # Added Code
    _validate_bits_32(a, b)  # Added Code
    out = [0] * 32  # Added Code
    cin = cin0  # Added Code
    carry_into_msb = 0  # Added Code
    for i in range(32):  # Added Code
        ai = a[i]
        bi = b[i]  # Added Code
        axb = ai ^ bi  # a XOR b  # Added Code
        s = axb ^ cin  # sum = a XOR b XOR cin  # Added Code
        cout = (ai & bi) | (cin & axb)  # cout = a·b OR cin·(a XOR b)  # Added Code
        out[i] = s  # Added Code
        if i == 31:  # capture carries around MSB for V  # Added Code
            carry_into_msb = cin  # Added Code
            carry_out_msb = cout  # Added Code
        cin = cout  # ripple  # Added Code
    N = out[31]  # Added Code
    Z = 1 if all(bit == 0 for bit in out) else 0  # Added Code
    C = cin  # Added Code
    V = 1 if carry_into_msb != carry_out_msb else 0  # Added Code
    return out, N, Z, C, V  # Added Code


def add_bits(a: List[int], b: List[int]) -> Tuple[List[int], int, int, int, int]:
    """Add two 32-bit vectors using a ripple of 1-bit full adders.

    :param List[int] a: 32-bit list, LSB first.
    :param List[int] b: 32-bit list, LSB first.
    :returns: ``(sum_bits, N, Z, C, V)``.
    :rtype: Tuple[List[int], int, int, int, int]
    """
    return _add_bits_with_cin(a, b, 0)  # Added Code


def _invert_bits(bits: List[int]) -> List[int]:  # Added Code
    """Bitwise NOT for 0/1 lists."""  # Added Code
    return [0 if b == 1 else 1 for b in bits]  # Added Code


def sub_bits(a: List[int], b: List[int]) -> Tuple[List[int], int, int, int, int]:
    """Subtract ``b`` from ``a`` via two's-complement addition.

    :param List[int] a: Minuend, 32-bit list, LSB first.
    :param List[int] b: Subtrahend, 32-bit list, LSB first.
    :returns: ``(diff_bits, N, Z, C, V)``; for two's-complement, C=1 means no borrow.
    :rtype: Tuple[List[int], int, int, int, int]
    """
    _validate_bits_32(a, b)  # Added Code
    b_inv = _invert_bits(b)  # Added Code
    # Single-pass ripple with cin=1 computes a + (~b) + 1, so carry-into/out of MSB are from the SAME addition.  # Added Code
    diff, N, Z, C, V = _add_bits_with_cin(a, b_inv, 1)  # Added Code
    return diff, N, Z, C, V  # Added Code
