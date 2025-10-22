README.md

# Midterm Project - ALU, MDU, FPU Implementations and Tests

---

Here’s a clean, ready-to-use `README.md` that matches your project and workflow on Windows with Poetry.

```markdown
# Midterm 440 — Numeric Core (ALU / MDU / FPU)

Pure bit-level implementations of common numeric units for a toy RV32 core:

- **ALU**: ripple-carry `ADD` / `SUB` with flags **N, Z, C, V**
- **MDU**: shift-add `MUL` (low 32) + restoring `DIV/DIVU` with RV32M edge cases
- **FPU (float32)**: pack/unpack + host-backed add/sub/mul for smoke-tests
- **Shifter**: logical/arithmetic shifts (`SLL`, `SRL`, `SRA`) without using `<<`/`>>` in core math

---

## Project layout
```

midterm_440/
├─ README.md
├─ pyproject.toml
├─ poetry.lock
├─ scripts/
│ └─ expectations.py
├─ src/
│ └─ midterm_440/
│ ├─ **init**.py
│ └─ numeric_core/
│ ├─ **init**.py
│ ├─ alu.py
│ ├─ bits.py
│ ├─ fpu_f32.py
│ ├─ interfaces.py
│ ├─ mdu.py
│ ├─ shifter.py
│ └─ twos.py
└─ tests/
├─ **init**.py
├─ conftest.py
└─ unit/
├─ test_alu.py
├─ test_bits.py
├─ test_fpu_f32.py
├─ test_mdu.py
├─ test_shifter.py
├─ test_twos.py
└─ smoke_mdu.py

````

---

## Requirements

- **Python** 3.12 (or compatible CPython)
- **Poetry** for environment and dependency management (recommended)

Install Poetry using the official method for your platform, then ensure `poetry` is on your `PATH`.


---

## Install

From the project root:

```powershell
# 1) Create the virtualenv and install deps
poetry --version
poetry install


# 2) Activate the venv (optional; you can also use `poetry run ...`)
poetry env activate
You'll see output like:
& "E:\Win11\Documents\Python\Projects\HelloWorld\.venv\Scripts\activate.ps1"
Copy and paste that in PowerShell,

````

> If you prefer not to enter a shell, prefix commands with `poetry run` as shown below.

---

## How to run

### 1) Run the full test suite

```powershell
poetry run pytest -q
```

Run a specific test file:

```powershell
poetry run pytest tests\unit\test_alu.py
poetry run pytest tests\unit\test_mdu.py
poetry run pytest tests\unit\test_fpu_f32.py
```

See the pytest docs for additional CLI options (e.g., `-q`, `-k <expr>`, `-x`). ([PyPI][1])

### 2) Print the expectations & traces demo

This script prints ALU edge cases, ripple-adder traces, MUL/DIV examples, and float32 sanity checks:

```powershell
poetry run python scripts\expectations.py
```

### 3) Quick MDU smoke run

```powershell
poetry run python tests\unit\smoke_mdu.py
```

You’ll see the low-32 results, flags, and (for MUL) a 32-step trace.

---

## What to expect (sanity outputs)

- **ALU**

  - `0x7FFFFFFF + 0x00000001 → 0x80000000` with `V=1, C=0, N=1, Z=0` (classic signed overflow)
  - `0x80000000 - 0x00000001 → 0x7FFFFFFF` with `V=1, C=1, N=0, Z=0`
  - Optional ripple-adder per-bit trace when `trace=True`

- **MDU**

  - `MUL 12345678 * -87654321 → rd = 0xD91D0712; overflow = 1`
  - `DIV -7 / 3 → q = 0xFFFFFFFE ; r = 0xFFFFFFFF`
  - `DIVU 0x80000000 / 3 → q = 0x2AAAAAAA ; r = 0x00000002`
  - Division by zero and `INT_MIN / -1` handled per RV32M rules

- **FPU (float32)**

  - `1.5 + 2.25 = 3.75 → 0x40700000`
  - `0.1 + 0.2 ≈ 0.3000000119 → 0x3E99999A` (ties-to-even)
  - Large products overflow to `±∞`; tiny products may be subnormal and indicate underflow

---

## Typical developer workflow

```powershell
# run all tests quietly
poetry run pytest -q

# print the expectations/traces
poetry run python scripts\expectations.py


# run selected tests while editing
poetry run pytest tests\unit\test_mdu.py -q -k "trace or overflow"
```

---

## Troubleshooting

---

## License

Educational use for course work. See repository for details.

````

# Example commands to run the tests and expectations script

```powershell
# Run all tests
poetry run pytest



----------------------------------------------------------------------

poetry run pytest

poetry run pytest tests\unit\test_fpu_f32.py
poetry run pytest tests\unit\test_alu.py
poetry run pytest tests\unit\test_mdu.py

## poetry run python scripts/expectations.py

### Quick sanity-check by section:

---

#### **ALU edges & traces**

- `0x7FFFFFFF + 0x00000001 → 0x80000000` with `V=1, C=0, N=1, Z=0` is the classic signed-overflow case for two’s-complement add: operands share the same sign and the result flips sign, so overflow is set; carry-out doesn’t indicate signed overflow.

- `0x80000000 - 0x00000001 → 0x7FFFFFFF` with `V=1, C=1, N=0, Z=0` is the symmetric edge for subtraction (implemented as `a + (~b + 1)`): again a sign flip implies signed overflow; the final carry (=1) means “no borrow” for two’s-complement subtraction.

- Your cycle-by-cycle ripple prints also make sense: the carry ripples through bit 0..30, then MSB resolves at bit 31. (Nothing to cite here; it’s the expected ripple-adder behavior and matches the numbers you printed.)

---

#### **MDU examples**

- **MUL (shift-add)**: low 32-bit product `0xD91D0712` for `12345678 * -87654321` is fine, and reporting `overflow=1` when the signed 64-bit product doesn’t fit in 32 bits is the usual convention.

- **DIV (restoring)**:

  - Signed `-7 / 3 → q = 0xFFFFFFFE (-2), r = 0xFFFFFFFF (-1)` (truncate toward zero; remainder keeps dividend’s sign).
  - Unsigned `0x80000000 / 3 → q = 0x2AAAAAAA, r = 0x00000002`.

These match RISC-V M semantics (round toward zero; div-by-zero special cases; remainder sign rules).

---

#### **Float32 (FPU)**

- `1.5 + 2.25 → 0x40700000` and `0.1 + 0.2 ≈ 0x3E99999A` are standard binary32 results (ties-to-even).

- `1e38 * 10 → +∞` with `overflow=1` is expected: the largest finite float32 is ~3.402823466e38; multiplying 1e38 by 10 exceeds that, so the correctly rounded result is ±∞ (exp=255, frac=0).

- `1e-38 * 1e-2 → subnormal` with `underflow=1` is reasonable: subnormals live below the smallest normal (≈1.17549435e-38) down to ≈1.40129846e-45; your product lands in that subnormal range.

---

Let me know if you'd like me to cross-check these values with official IEEE 754 test vectors or add illustrations for better understanding.
Please ask me any other questions you might have.
````
