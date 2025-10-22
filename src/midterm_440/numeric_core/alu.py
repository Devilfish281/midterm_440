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


def add_bits(a: List[int], b: List[int]) -> Tuple[List[int], int, int, int, int]:
    """Add two 32-bit vectors using a ripple of 1-bit full adders.

    :param List[int] a: 32-bit list, LSB first.
    :param List[int] b: 32-bit list, LSB first.
    :returns: ``(sum_bits, N, Z, C, V)``.
    :rtype: Tuple[List[int], int, int, int, int]
    """
    raise NotImplementedError("add_bits not implemented")


def sub_bits(a: List[int], b: List[int]) -> Tuple[List[int], int, int, int, int]:
    """Subtract ``b`` from ``a`` via two's-complement addition.

    :param List[int] a: Minuend, 32-bit list, LSB first.
    :param List[int] b: Subtrahend, 32-bit list, LSB first.
    :returns: ``(diff_bits, N, Z, C, V)``; for two's-complement, C=1 means no borrow.
    :rtype: Tuple[List[int], int, int, int, int]
    """
    raise NotImplementedError("sub_bits not implemented")
