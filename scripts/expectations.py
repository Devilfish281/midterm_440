# scripts/expectations.py
from midterm_440.numeric_core.alu import add_bits, sub_bits
from midterm_440.numeric_core.bits import bits_to_u32, u32_to_bits
from midterm_440.numeric_core.fpu_f32 import fadd_f32, fmul_f32, pack_f32, unpack_f32
from midterm_440.numeric_core.mdu import div_restoring, mul_shift_add
from midterm_440.numeric_core.twos import encode_twos_complement


def hx32(u: int) -> str:
    return f"0x{u & 0xFFFF_FFFF:08X}"


def hx_bits(bits: list[int]) -> str:  #
    return hx32(bits_to_u32(bits))  #


# ---------- NEW: trace helpers and demos ----------


# scripts/expectations.py


def _print_alu_trace(
    op: str, a_bits: list[int], b_bits: list[int], result_tuple: tuple
) -> None:
    """Pretty-print the ripple-carry per-bit trace emitted by add_bits/sub_bits(trace=True)."""

    # ---- Normalize result into (sum_bits, N, Z, C, V, trace_list|None) ----
    if isinstance(result_tuple, dict):  #  Changed Code
        sum_bits = result_tuple["sum_bits"]  #  Changed Code
        N = result_tuple["N"]  #  Changed Code
        Z = result_tuple["Z"]  #  Changed Code
        C = result_tuple["C"]  #  Changed Code
        V = result_tuple["V"]  #  Changed Code
        trace = result_tuple.get("trace", None)  #  Changed Code
    else:
        if len(result_tuple) == 5:
            sum_bits, N, Z, C, V = result_tuple
            trace = None  #  Changed Code
        else:
            sum_bits, N, Z, C, V, trace = result_tuple

    print(f"{op} trace: a={hx_bits(a_bits)}, b={hx_bits(b_bits)}")
    print(f"  flags at end: N={N}, Z={Z}, C={C}, V={V}")

    if not trace:
        print("  (no trace returned)")
        print()
        return

    # When trace comes from alu.add_bits/sub_bits(trace=True) it's a list of dicts with:
    #  - phase: "start" | "iter" | "finish"
    #  - for "iter": bit, ai, bi, cin, sum_bit, cout
    # We'll render a partial low32 hex by accumulating the sum bits as we go.  #  Changed Code
    print("  step  ai bi cin -> s cout   partial_low32_hex")  #  Changed Code
    partial = [0] * 32  #  Changed Code
    for t in trace:  #  Changed Code
        if not isinstance(t, dict) or t.get("phase") != "iter":  #  Changed Code
            continue  #  Changed Code
        i = int(t["bit"])  #  Changed Code
        ai = int(t["ai"])  #  Changed Code
        bi = int(t["bi"])  #  Changed Code
        cin = int(t["cin"])  #  Changed Code
        s = int(t["sum_bit"])  #  Changed Code
        cout = int(t["cout"])  #  Changed Code
        partial[i] = s  #  Changed Code
        phex = hx_bits(partial)  #  Changed Code
        print(
            f"  {i:>3}   {ai}  {bi}  {cin}   -> {s}   {cout}    {phex}"
        )  #  Changed Code

    print()  #  Changed Code


def print_add_sub_traces() -> None:  #
    print("ALU traces (cycle-by-cycle ripple):")  #
    # ADD with trace=True: 0x7FFFFFFF + 0x00000001 → overflow  #
    a_add = u32_to_bits(0x7FFFFFFF)  #
    b_add = u32_to_bits(0x00000001)  #
    add_out = add_bits(a_add, b_add, trace=True)  #
    print("Doing ADD with trace=True (0x7FFFFFFF + 0x00000001):")  #
    _print_alu_trace("ADD", a_add, b_add, add_out)  #

    # SUB with trace=True: 0x80000000 - 0x00000001 → overflow  #
    a_sub = u32_to_bits(0x80000000)  #
    b_sub = u32_to_bits(0x00000001)  #
    sub_out = sub_bits(a_sub, b_sub, trace=True)  #
    print("Doing SUB with trace=True (0x80000000 - 0x00000001):")  #
    _print_alu_trace("SUB", a_sub, b_sub, sub_out)  #


# --- add this near your other helpers ---


def _print_mul_trace(rs1_bits, rs2_bits, out):
    tr = out.get("trace", []) or []
    print("MUL trace:")
    print(f"  rs1={hx_bits(rs1_bits)}, rs2={hx_bits(rs2_bits)}")
    print(f"  rd={hx_bits(out['rd_bits'])}, overflow={out['overflow']}")
    if not tr:
        print("  (no trace rows)")
        return
    print("  step  mul_bit  added  acc_hi32     acc_low32")
    for row in tr:
        # handle both “iter only” rows and the older format with 'phase'
        if isinstance(row, dict) and ("step" in row):
            step = int(row["step"])
            mb = int(row.get("mul_bit", 0))
            add = int(row.get("added", 0))
            hi = row.get("acc_hi32_hex", "0x????????")
            lo = row.get("acc_low32_hex", "0x????????")
            print(f"  {step:4d}     {mb}        {add}    {hi}  {lo}")


"""Sample multiplication and division examples.
Example unit expectations (RV32):
•	MUL 12345678 * -87654321 → rd = 0xD91D0712 (low 32); overflow=1
•	MULH 12345678 * -87654321 → rd = 0xFFFC27C9
•	DIV -7 / 3 → q = -2 (0xFFFFFFFE); r = -1 (0xFFFFFFFF)
•	DIVU 0x80000000 / 3 → q = 0x2AAAAAAA; r = 0x00000002
"""


def print_float32_expectations() -> None:
    print("Float32 sample expectations")
    print("Doing •\t1.5 + 2.25 = 3.75 → 0x40700000")
    # 1.5 + 2.25  → 3.75 (0x40700000)
    a = pack_f32(1.5)["bits"]
    b = pack_f32(2.25)["bits"]
    add_out = fadd_f32(a, b)
    print(f"•\t1.5 + 2.25 = 3.75 → {hx_bits(add_out['res_bits'])}")

    print("Doing •\t0.1 + 0.2 ≈ 0.3000000119 → 0x3E99999A (ties to even)")
    # 0.1 + 0.2  → ~0.3000000119 (0x3E99999A), RNE ties-to-even
    a01 = pack_f32(0.1)["bits"]
    a02 = pack_f32(0.2)["bits"]
    s = fadd_f32(a01, a02)  #
    s_val = unpack_f32(s["res_bits"])["value"]  #
    print(f"•\t0.1 + 0.2 ≈ {s_val:.10f} → {hx_bits(s['res_bits'])} (ties to even)")

    print("Doing •\t1e38 * 10 → +∞; overflow=1")
    # 1e38 * 10  → +∞; overflow=1 (∞ is 0x7F800000 in binary32)
    mul_inf = fmul_f32(pack_f32(1e38)["bits"], pack_f32(10.0)["bits"])
    print(
        f"•\t1e38 * 10 → {hx_bits(mul_inf['res_bits'])}; overflow={mul_inf['flags']['overflow']}"
    )  #

    print("Doing •\t1e-38 * 1e-2 → subnormal; underflow=1")
    # 1e-38 * 1e-2  → subnormal; treat as underflow=1 for the handout
    mul_sub = fmul_f32(pack_f32(1e-38)["bits"], pack_f32(1e-2)["bits"])  #
    cls = unpack_f32(mul_sub["res_bits"])["class"]  #
    underflow_expected = 1 if cls == "subnormal" else 0  #
    print(f"•\t1e-38 * 1e-2 → {cls}; underflow={underflow_expected}")  #


def print_mul_examples():
    print("Multiplication sample expectations")
    print("Doing MUL 12345678 * -87654321")
    a = 12345678
    b = -87654321
    rs1 = u32_to_bits(a)
    rs2 = u32_to_bits(b & 0xFFFF_FFFF)
    mul_out = mul_shift_add(rs1, rs2, trace=True)  # ensure trace is on
    low32 = bits_to_u32(mul_out["rd_bits"])
    print(
        "MUL 12345678 * -87654321 → rd =", hx32(low32), "overflow=", mul_out["overflow"]
    )
    _print_mul_trace(rs1, rs2, mul_out)

    print("Doing MULH 12345678 * -87654321")
    full = (a * b) & ((1 << 64) - 1)
    hi32 = (full >> 32) & 0xFFFF_FFFF
    print("MULH 12345678 * -87654321 → rd =", hx32(hi32))


def print_div_examples():
    print("Division sample expectations")
    print("Doing DIV -7 / 3 (signed and unsigned):")
    # DIV -7 / 3 (signed)
    d_signed = div_restoring(u32_to_bits(0xFFFFFFF9), u32_to_bits(3), signed=True)
    q = bits_to_u32(d_signed["q_bits"])
    r = bits_to_u32(d_signed["r_bits"])
    print("DIV -7 / 3 → q =", hx32(q), "; r =", hx32(r))

    print("Doing DIVU 0x80000000 / 3 (unsigned):")
    # DIVU 0x80000000 / 3 (unsigned)
    d_unsigned = div_restoring(u32_to_bits(0x80000000), u32_to_bits(3), signed=False)
    q2 = bits_to_u32(d_unsigned["q_bits"])
    r2 = bits_to_u32(d_unsigned["r_bits"])
    print("DIVU 0x80000000 / 3 → q =", hx32(q2), "; r =", hx32(r2))


"""
Sample expectations (width=32):
•	+13 → bin 00000000_00000000_00000000_00001101; hex 0x0000000D; overflow=0
•	-13 → bin 11111111_11111111_11111111_11110011; hex 0xFFFFFFF3; overflow=0
•	2^31 → overflow=1
"""


def print_twos_expectations() -> None:
    print("Two's complement sample expectations:")
    print("Sample expectations (width=32):")
    print(
        "Doing •\t+13 → bin 00000000_00000000_00000000_00001101; hex 0x0000000D; overflow=0"
    )
    pos = encode_twos_complement(13)
    print(
        f"•\t+13 → bin {pos['bin']}; hex {pos['hex']}; overflow={pos['overflow_flag']}"
    )
    print(
        "Doing •\t-13 → bin 11111111_11111111_11111111_11110011; hex 0xFFFFFFF3; overflow=0"
    )
    neg = encode_twos_complement(-13)
    print(
        f"•\t-13 → bin {neg['bin']}; hex {neg['hex']}; overflow={neg['overflow_flag']}"
    )
    print("Doing •\t2^31 → overflow=1")
    hi = encode_twos_complement(1 << 31)
    print(f"•\t2^31 → overflow={hi['overflow_flag']}")


"""
Edge expectations:
•	0x7FFFFFFF + 0x00000001 → 0x80000000; V=1; C=0; N=1; Z=0.
•	0x80000000 - 0x00000001 → 0x7FFFFFFF; V=1; C=1; N=0; Z=0.
•	-1 + -1 → -2; V=0; C=1; N=1; Z=0.
"""


def print_alu_edge_expectations() -> None:
    print("Edge expectations:")
    print("Doing •\t0x7FFFFFFF + 0x00000001 → 0x80000000; V=1; C=0; N=1; Z=0.")
    # 0x7FFFFFFF + 0x00000001
    a1 = u32_to_bits(0x7FFFFFFF)
    b1 = u32_to_bits(0x00000001)
    res1, N1, Z1, C1, V1 = add_bits(a1, b1)
    print(
        f"•\t0x7FFFFFFF + 0x00000001 → {hx32(bits_to_u32(res1))}; V={V1}; C={C1}; N={N1}; Z={Z1}."
    )

    print("Doing •\t0x80000000 - 0x00000001 → 0x7FFFFFFF; V=1; C=1; N=0; Z=0.")
    # 0x80000000 - 0x00000001
    a2 = u32_to_bits(0x80000000)
    b2 = u32_to_bits(0x00000001)
    res2, N2, Z2, C2, V2 = sub_bits(a2, b2)
    print(
        f"•\t0x80000000 - 0x00000001 → {hx32(bits_to_u32(res2))}; V={V2}; C={C2}; N={N2}; Z={Z2}."
    )

    print("Doing •\t-1 + -1 → -2; V=0; C=1; N=1; Z=0.")
    # -1 + -1
    a3 = u32_to_bits(0xFFFFFFFF)
    b3 = u32_to_bits(0xFFFFFFFF)
    res3, N3, Z3, C3, V3 = add_bits(a3, b3)
    print(f"•\t-1 + -1 → {hx32(bits_to_u32(res3))}; V={V3}; C={C3}; N={N3}; Z={Z3}.")

    """
    Float32 sample expectations
•	1.5 + 2.25 = 3.75 → 0x40700000
•	0.1 + 0.2 ≈ 0.3000000119 → 0x3E99999A (ties to even)
•	1e38 * 10 → +∞; overflow=1
•	1e-38 * 1e-2 → subnormal; underflow=1
    """


"""Main function to print all examples and expectations."""


def main():
    print("-----------------------------------------")
    print_alu_edge_expectations()
    print("----------------------------------------")
    print_twos_expectations()
    print("----------------------------------------")
    print_add_sub_traces()
    print("----------------------------------------")
    print_mul_examples()
    print("----------------------------------------")
    print_div_examples()
    print("----------------------------------------")
    print_float32_expectations()


if __name__ == "__main__":
    main()
