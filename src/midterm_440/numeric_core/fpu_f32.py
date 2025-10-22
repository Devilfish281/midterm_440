# src/midterm_440/numeric_core/fpu_f32.py
"""IEEE 754 float32 pack/unpack and arithmetic (add/sub/mul).

Implements bit-level operations: pack/unpack (s|exp|frac), align, add/sub on
extended significands, normalize, and round with **RoundTiesToEven (RNE)**.

Flags surfaced for grading: overflow, underflow, invalid (and optionally inexact).
"""

from typing import Dict, List


def pack_f32(value: float) -> Dict[str, object]:
    """Pack a Python decimal value into an IEEE-754 binary32 bit pattern.

    :param float value: Decimal input; treat special cases (±0, ±inf, NaN).
    :returns: ``{'bits': List[int], 'fields': {'s': int, 'exp': List[int], 'frac': List[int]}}``.
    :rtype: Dict[str, object]
    """
    raise NotImplementedError("pack_f32 not implemented")


def unpack_f32(bits: List[int]) -> Dict[str, object]:
    """Unpack a 32-bit IEEE-754 pattern into a Python decimal value.

    :param List[int] bits: 32 bits, LSB first.
    :returns: ``{'value': float, 'class': str}`` (e.g., 'normal','subnormal','zero','inf','nan').
    :rtype: Dict[str, object]
    """
    raise NotImplementedError("unpack_f32 not implemented")


def fadd_f32(a_bits: List[int], b_bits: List[int]) -> Dict[str, object]:
    """Float32 addition via align → add → normalize → round (RNE).

    :param List[int] a_bits: Operand A, 32 bits LSB first.
    :param List[int] b_bits: Operand B, 32 bits LSB first.
    :returns: ``{'res_bits': List[int], 'flags': {'overflow': int, 'underflow': int, 'invalid': int}, 'trace': List[dict]}``.
    :rtype: Dict[str, object]
    """
    raise NotImplementedError("fadd_f32 not implemented")


def fsub_f32(a_bits: List[int], b_bits: List[int]) -> Dict[str, object]:
    """Float32 subtraction via add with sign inversion and standard steps.

    :param List[int] a_bits: Operand A, 32 bits LSB first.
    :param List[int] b_bits: Operand B, 32 bits LSB first.
    :returns: Same schema as :func:`fadd_f32`.
    :rtype: Dict[str, object]
    """
    raise NotImplementedError("fsub_f32 not implemented")


def fmul_f32(a_bits: List[int], b_bits: List[int]) -> Dict[str, object]:
    """Float32 multiplication with normalization and RNE rounding.

    :param List[int] a_bits: Operand A, 32 bits LSB first.
    :param List[int] b_bits: Operand B, 32 bits LSB first.
    :returns: ``{'res_bits': List[int], 'flags': {...}, 'trace': List[dict]}``.
    :rtype: Dict[str, object]
    """
    raise NotImplementedError("fmul_f32 not implemented")
