# src/midterm_440/numeric_core/shifter.py
"""Logical and arithmetic shifters implemented without ``<<``/``>>``.

Implements SLL, SRL, SRA using either iterative shift-register style
or a barrel shifter built from stages (powers of two).
"""

from typing import List


def sll_bits(bits: List[int], shamt: int) -> List[int]:
    """Shift left logical by ``shamt`` (insert zeros on the right).

    :param List[int] bits: 32-bit list, LSB first.
    :param int shamt: Shift amount in [0, 31].
    :returns: New 32-bit list after SLL.
    :rtype: List[int]
    """
    raise NotImplementedError("sll_bits not implemented")


def srl_bits(bits: List[int], shamt: int) -> List[int]:
    """Shift right logical by ``shamt`` (insert zeros on the left).

    :param List[int] bits: 32-bit list, LSB first.
    :param int shamt: Shift amount in [0, 31].
    :returns: New 32-bit list after SRL.
    :rtype: List[int]
    """
    raise NotImplementedError("srl_bits not implemented")


def sra_bits(bits: List[int], shamt: int) -> List[int]:
    """Shift right arithmetic by ``shamt`` (replicate original sign bit).

    :param List[int] bits: 32-bit list, LSB first.
    :param int shamt: Shift amount in [0, 31].
    :returns: New 32-bit list after SRA.
    :rtype: List[int]
    """
    raise NotImplementedError("sra_bits not implemented")
