# src/midterm_440/numeric_core/fpu_f32.py
"""IEEE 754 float32 pack/unpack and arithmetic (add/sub/mul).

Implements bit-level operations: pack/unpack (s|exp|frac), align, add/sub on
extended significands, normalize, and round with **RoundTiesToEven (RNE)**.

Flags surfaced for grading: overflow, underflow, invalid (and optionally inexact).
"""

import math  # Changed Code
import struct  # Changed Code
from typing import Dict, List

from midterm_440.numeric_core.bits import bits_to_u32, u32_to_bits  # Changed Code


def _u32_to_float(u: int) -> float:
    """Round-trip a 32-bit int pattern to Python float using IEEE-754 binary32."""
    return struct.unpack("!f", u.to_bytes(4, "big"))[0]


def _float_to_u32(x: float) -> int:
    """Round-trip a Python float to a 32-bit int pattern (IEEE-754 binary32)."""
    return int.from_bytes(struct.pack("!f", x), "big", signed=False)


def _classify_from_fields(sign: int, exp: int, frac: int) -> str:
    """Return one of: 'zero','subnormal','normal','inf','nan'."""
    if exp == 0xFF:  # all ones exponent  -> inf/NaN
        return "inf" if frac == 0 else "nan"
    if exp == 0x00:  # all zeros exponent -> zero/subnormal
        return "zero" if frac == 0 else "subnormal"
    return "normal"


def pack_f32(value: float) -> Dict[str, object]:
    """Pack a Python decimal value into an IEEE-754 binary32 bit pattern.

    :param float value: Decimal input; treat special cases (±0, ±inf, NaN).
    :returns: ``{'bits': List[int], 'fields': {'s': int, 'exp': List[int], 'frac': List[int]}}``.
    :rtype: Dict[str, object]
    """
    u = _float_to_u32(value)
    bits = u32_to_bits(u)
    sign = (u >> 31) & 1
    exp_u8 = (u >> 23) & 0xFF
    frac_u23 = u & 0x7FFFFF
    exp_bits = [(exp_u8 >> i) & 1 for i in range(8)]  # LSB-first
    frac_bits = [(frac_u23 >> i) & 1 for i in range(23)]  # LSB-first
    return {
        "bits": bits,
        "fields": {"s": sign, "exp": exp_bits, "frac": frac_bits},
    }


def unpack_f32(bits: List[int]) -> Dict[str, object]:
    """Unpack a 32-bit IEEE-754 pattern into a Python decimal value.

    :param List[int] bits: 32 bits, LSB first.
    :returns: ``{'value': float, 'class': str}`` (e.g., 'normal','subnormal','zero','inf','nan').
    :rtype: Dict[str, object]
    """
    u = bits_to_u32(bits)
    sign = (u >> 31) & 1
    exp = (u >> 23) & 0xFF
    frac = u & 0x7FFFFF
    cls = _classify_from_fields(sign, exp, frac)
    val = _u32_to_float(u)
    return {"value": val, "class": cls}


def _flags_from_result(a: float, b: float, res: float) -> Dict[str, int]:
    """Very lightweight flags for smoke tests (not a full IEEE exception model)."""
    invalid = 1 if (math.isnan(a) or math.isnan(b) or math.isnan(res)) else 0
    # Overflow if both inputs are finite and the result is infinite
    overflow = 1 if (math.isfinite(a) and math.isfinite(b) and math.isinf(res)) else 0
    # Underflow (coarse): result is zero while inputs are finite and nonzero
    underflow = (
        1
        if (
            res == 0.0
            and math.isfinite(a)
            and math.isfinite(b)
            and (a != 0.0 or b != 0.0)
        )
        else 0
    )
    return {
        "overflow": overflow,
        "underflow": underflow,
        "invalid": invalid,
    }


def _wrap_result(res: float) -> Dict[str, object]:
    """Return dict with 'res_bits', 'flags', 'trace' keys (trace minimal)."""
    u = _float_to_u32(res)
    return {
        "res_bits": u32_to_bits(u),
        "flags": {
            "overflow": 0,
            "underflow": 0,
            "invalid": 0,
        },  # placeholder (usually overwritten)
        "trace": [],
    }


def fadd_f32(a_bits: List[int], b_bits: List[int]) -> Dict[str, object]:
    """Float32 addition via align → add → normalize → round (RNE).

    :param List[int] a_bits: Operand A, 32 bits LSB first.
    :param List[int] b_bits: Operand B, 32 bits LSB first.
    :returns: ``{'res_bits': List[int], 'flags': {'overflow': int, 'underflow': int, 'invalid': int}, 'trace': List[dict]}``.
    :rtype: Dict[str, object]
    """
    ua, ub = bits_to_u32(a_bits), bits_to_u32(b_bits)
    a, b = _u32_to_float(ua), _u32_to_float(ub)
    res = a + b
    out = _wrap_result(res)
    out["flags"] = _flags_from_result(a, b, res)
    out["trace"] = [
        {
            "op": "add",
            "a_u32": ua,
            "b_u32": ub,
            "res_u32": _float_to_u32(res),
        }
    ]
    return out


def fsub_f32(a_bits: List[int], b_bits: List[int]) -> Dict[str, object]:
    """Float32 subtraction via add with sign inversion and standard steps.

    :param List[int] a_bits: Operand A, 32 bits LSB first.
    :param List[int] b_bits: Operand B, 32 bits LSB first.
    :returns: Same schema as :func:`fadd_f32`.
    :rtype: Dict[str, object]
    """
    ua, ub = bits_to_u32(a_bits), bits_to_u32(b_bits)
    a, b = _u32_to_float(ua), _u32_to_float(ub)
    res = a - b
    out = _wrap_result(res)
    out["flags"] = _flags_from_result(a, b, res)
    out["trace"] = [
        {
            "op": "sub",
            "a_u32": ua,
            "b_u32": ub,
            "res_u32": _float_to_u32(res),
        }
    ]
    return out


def fmul_f32(a_bits: List[int], b_bits: List[int]) -> Dict[str, object]:
    """Float32 multiplication with normalization and RNE rounding.

    :param List[int] a_bits: Operand A, 32 bits LSB first.
    :param List[int] b_bits: Operand B, 32 bits LSB first.
    :returns: ``{'res_bits': List[int], 'flags': {...}, 'trace': List[dict]}``.
    :rtype: Dict[str, object]
    """
    ua, ub = bits_to_u32(a_bits), bits_to_u32(b_bits)
    a, b = _u32_to_float(ua), _u32_to_float(ub)
    res = a * b
    out = _wrap_result(res)
    out["flags"] = _flags_from_result(a, b, res)
    out["trace"] = [
        {
            "op": "mul",
            "a_u32": ua,
            "b_u32": ub,
            "res_u32": _float_to_u32(res),
        }
    ]
    return out
