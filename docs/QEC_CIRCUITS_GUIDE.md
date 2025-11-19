# Quantum Error Correction Circuits - Comprehensive Guide

This document provides a comprehensive overview of all quantum error correction (QEC) codes implemented in this repository.

## Table of Contents

1. [Introduction to Quantum Error Correction](#introduction)
2. [Basic QEC Codes](#basic-codes)
   - [Bit-Flip Code (3-qubit)](#bit-flip-code)
   - [Phase-Flip Code (3-qubit)](#phase-flip-code)
3. [Advanced QEC Codes](#advanced-codes)
   - [Shor's 9-Qubit Code](#shors-9-qubit-code)
   - [Five-Qubit Code [[5,1,3]]](#five-qubit-code)
   - [Steane Code [[7,1,3]]](#steane-code)
4. [Topological Codes](#topological-codes)
   - [Surface Code](#surface-code)
   - [Toric Code](#toric-code)
5. [Subsystem Codes](#subsystem-codes)
   - [Bacon-Shor Code](#bacon-shor-code)
6. [Error Models](#error-models)
7. [Comparison Table](#comparison-table)
8. [Usage Examples](#usage-examples)

---

## Introduction to Quantum Error Correction {#introduction}

Quantum error correction is essential for building fault-tolerant quantum computers. Unlike classical bits, quantum bits (qubits) are susceptible to various types of errors:

- **Bit-flip errors (X)**: |0⟩ ↔ |1⟩
- **Phase-flip errors (Z)**: |+⟩ ↔ |-⟩
- **Bit-phase errors (Y)**: Combination of X and Z

Quantum error correction codes protect quantum information by encoding a logical qubit into multiple physical qubits, allowing errors to be detected and corrected without measuring the logical qubit directly.

### Key Concepts

- **Encoding**: Transform 1 logical qubit → N physical qubits
- **Syndrome Measurement**: Measure error patterns without destroying quantum information
- **Decoding**: Determine which error occurred from the syndrome
- **Correction**: Apply corrective operations to restore the original state

---

## Basic QEC Codes {#basic-codes}

### Bit-Flip Code (3-qubit) {#bit-flip-code}

**File**: `src/bit_flip_codes.py`

**Type**: Repetition code
**Parameters**: [[3,1,1]]
**Protection**: Single bit-flip (X) error

#### How It Works

The bit-flip code encodes one logical qubit into three physical qubits by repeating the state:

- Logical |0⟩ → |000⟩
- Logical |1⟩ → |111⟩

**Encoding Circuit**:
```
|ψ⟩ ──●───●──
      │   │
|0⟩ ──⊕───┼──
          │
|0⟩ ──────⊕──
```

**Error Detection**: Measures syndromes using CNOT gates to compare qubits pairwise.

**Decoding**: Uses majority voting - if two qubits agree, they determine the correct value.

#### Usage

```bash
python src/bit_flip_codes.py --input 0 --error --error-qubit 1
```

#### Limitations

- Only corrects bit-flip (X) errors
- Cannot correct phase-flip (Z) errors
- Distance d=3 (corrects 1 error)

---

### Phase-Flip Code (3-qubit) {#phase-flip-code}

**File**: `src/phase_flip_codes.py`

**Type**: Dual of bit-flip code
**Parameters**: [[3,1,1]]
**Protection**: Single phase-flip (Z) error

#### How It Works

The phase-flip code works by encoding in the Hadamard basis:

- Logical |0⟩ → |+++⟩ = H⊗3|000⟩
- Logical |1⟩ → |---⟩ = H⊗3|111⟩

**Key Idea**: Phase flips in the |+⟩/|-⟩ basis behave like bit flips in the computational basis.

**Encoding**:
1. Start with |ψ⟩
2. Apply CNOT gates (like bit-flip code)
3. Apply Hadamard gates to all qubits
4. Phase errors now appear as bit errors in the Hadamard basis

#### Usage

```bash
python src/phase_flip_codes.py --input 1 --error --error-qubit 0 --no-draw
```

#### Limitations

- Only corrects phase-flip (Z) errors
- Cannot correct bit-flip (X) errors
- Distance d=3

---

## Advanced QEC Codes {#advanced-codes}

### Shor's 9-Qubit Code {#shors-9-qubit-code}

**File**: `src/shors_9qubit_code.py`

**Type**: CSS code (concatenated)
**Parameters**: [[9,1,3]]
**Protection**: Any single-qubit error (X, Y, or Z)

#### How It Works

Shor's code combines the bit-flip and phase-flip codes through concatenation:

1. First level: Protect against phase flips (3 blocks of 3 qubits)
2. Second level: Protect against bit flips within each block

**Structure**:
```
Block 0: Q0, Q1, Q2  ─┐
Block 1: Q3, Q4, Q5  ─┼─ Protected against phase flips
Block 2: Q6, Q7, Q8  ─┘
         └─────────────> Each block protected against bit flips
```

**Logical States**:
- |0_L⟩ = (|000⟩ + |111⟩)⊗3 / 2√2
- |1_L⟩ = (|000⟩ - |111⟩)⊗3 / 2√2

**Syndrome Measurement**:
- 6 syndrome qubits for bit-flip detection (2 per block)
- 2 syndrome qubits for phase-flip detection (between blocks)

#### Usage

```bash
python src/shors_9qubit_code.py --input 0 --error --error-qubit 4 --error-type Y
```

#### Advantages

- First code to correct arbitrary single-qubit errors
- Well-understood and thoroughly studied
- Good pedagogical example

#### Limitations

- Uses 9 qubits to encode 1 logical qubit (not optimal)
- More efficient codes exist (e.g., Steane, Five-qubit)

---

### Five-Qubit Code [[5,1,3]] {#five-qubit-code}

**File**: `src/five_qubit_code.py`

**Type**: Stabilizer code (perfect code)
**Parameters**: [[5,1,3]]
**Protection**: Any single-qubit error

#### How It Works

The five-qubit code is the smallest possible code that can correct an arbitrary single-qubit error. It achieves the quantum Hamming bound with equality, making it a "perfect" code.

**Stabilizers**:
```
S₁ = XZZXI
S₂ = IXZZX
S₃ = XIXZZ
S₄ = ZXIXZ
```

**Key Properties**:
- Minimal: Uses only 5 qubits (optimal)
- Four independent stabilizers
- Unique syndrome for each single-qubit error

**Logical Operators**:
- X̄ = XXXXX (logical X)
- Z̄ = ZZZZZ (logical Z)

#### Usage

```bash
python src/five_qubit_code.py --input 1 --error --error-qubit 2 --error-type Z
```

#### Advantages

- Most efficient single-error correcting code
- Perfect code (achieves quantum Hamming bound)
- All stabilizers have weight 4

#### Limitations

- Only corrects 1 error (distance d=3)
- Not easily scalable to higher distances

---

### Steane Code [[7,1,3]] {#steane-code}

**File**: `src/steane_code.py`

**Type**: CSS code (Calderbank-Shor-Steane)
**Parameters**: [[7,1,3]]
**Protection**: Any single-qubit error

#### How It Works

The Steane code is based on the classical [7,4,3] Hamming code. It's a CSS code, meaning it uses classical codes for both X and Z error correction.

**Logical |0⟩ state** (1 of 8 basis states):
```
|0_L⟩ = 1/√8 (|0000000⟩ + |1010101⟩ + |0110011⟩ + |1100110⟩ +
              |0001111⟩ + |1011010⟩ + |0111100⟩ + |1101001⟩)
```

**Stabilizers**:
- 3 X-type stabilizers (detect Z errors)
- 3 Z-type stabilizers (detect X errors)

**Key Features**:
- Transversal gates: CNOT, Hadamard
- Fault-tolerant measurement
- Better for fault-tolerant quantum computation than Shor's code

#### Usage

```bash
python src/steane_code.py --input 0 --error --error-qubit 3 --error-type X --shots 2048
```

#### Advantages

- More efficient than Shor's code (7 qubits vs 9)
- Supports transversal gates (easier fault tolerance)
- Well-suited for fault-tolerant quantum computing

#### Limitations

- Still not scalable to arbitrary distances
- Fixed distance d=3

---

## Topological Codes {#topological-codes}

### Surface Code {#surface-code}

**File**: `src/surface_code.py`

**Type**: Topological stabilizer code
**Parameters**: [[9,1,3]] (distance-3)
**Protection**: Any single-qubit error

#### How It Works

Surface codes arrange qubits on a 2D lattice with local stabilizer measurements. They are the leading candidate for practical fault-tolerant quantum computing.

**Qubit Layout** (3×3 grid):
```
Q0 ─ Q1 ─ Q2
│    │    │
Q3 ─ Q4 ─ Q5
│    │    │
Q6 ─ Q7 ─ Q8
```

**Stabilizers**:
- **X-type (star)**: Measure X on 4 neighboring qubits
- **Z-type (plaquette)**: Measure Z on 4 qubits around a face

**Key Properties**:
- 2D nearest-neighbor interactions only
- High error threshold (~1%)
- Scalable to arbitrary distances (d = 2k+1 for k×k grid)

**Error Correction**: Errors create pairs of syndrome excitations. Decoding finds the most likely error path (minimum-weight perfect matching).

#### Usage

```bash
python src/surface_code.py --input 0 --error --error-qubit 4 --error-type Y
```

#### Advantages

- **High threshold**: ~1% physical error rate
- **2D architecture**: Compatible with superconducting qubits
- **Scalable**: Can increase distance by adding more qubits
- **Well-studied**: Extensive theoretical and experimental work

#### Limitations

- Large overhead (many physical qubits per logical qubit)
- Complex decoding (requires MWPM algorithm)

---

### Toric Code {#toric-code}

**File**: `src/toric_code.py`

**Type**: Topological stabilizer code
**Parameters**: [[16,2,4]] (simplified implementation)
**Protection**: Errors as topological loops

#### How It Works

The toric code places qubits on edges of a 2D square lattice with periodic boundary conditions (torus topology). It encodes 2 logical qubits.

**Structure**:
- 16 data qubits on edges
- 4 vertex stabilizers (X-type)
- 4 plaquette stabilizers (Z-type)
- Periodic boundary conditions

**Stabilizers**:
- **Vertex (Av)**: Product of X on 4 edges touching a vertex
- **Plaquette (Bp)**: Product of Z on 4 edges around a face

**Logical Qubits**:
- Logical qubit 1: Non-contractible loop horizontally around torus
- Logical qubit 2: Non-contractible loop vertically around torus

**Error Chains**: Errors create chains on the lattice. Syndrome shows chain endpoints.

#### Usage

```bash
python src/toric_code.py --input1 0 --input2 1 --error --error-qubit 5 --error-type Z
```

#### Advantages

- Foundational topological code
- Encodes 2 logical qubits
- Errors are topologically protected
- No local measurement distinguishes logical states

#### Limitations

- Requires periodic boundary conditions (difficult to implement)
- Surface code is more practical for planar architectures
- Simplified implementation in this repo

---

## Subsystem Codes {#subsystem-codes}

### Bacon-Shor Code {#bacon-shor-code}

**File**: `src/bacon_shor_code.py`

**Type**: Subsystem code
**Parameters**: [[9,1,3]]
**Protection**: Single-qubit errors

#### How It Works

The Bacon-Shor code is a subsystem code that combines advantages of both Shor's code and surface codes. It uses "gauge" qubits that don't need to be corrected.

**Layout** (3×3 grid):
```
Q0 ─ Q1 ─ Q2
│    │    │
Q3 ─ Q4 ─ Q5
│    │    │
Q6 ─ Q7 ─ Q8
```

**Stabilizers** (weight-2, easier to measure):
- **X-checks**: ZZ on horizontal pairs (6 checks)
- **Z-checks**: XX on vertical pairs (6 checks)

**Key Advantage**: Weight-2 measurements are easier to implement fault-tolerantly than weight-4 (as in surface code).

**Decoding**:
- X-checks identify the row of Z errors
- Z-checks identify the column of X errors

#### Usage

```bash
python src/bacon_shor_code.py --input 1 --error --error-qubit 4 --error-type X
```

#### Advantages

- Simpler syndrome measurement (weight-2)
- Easier decoder than surface code
- Same qubit count as surface code for distance-3

#### Limitations

- Lower threshold than surface code
- Less studied than surface/toric codes

---

## Error Models {#error-models}

**File**: `src/error_models.py`

The repository includes a comprehensive error model library for testing QEC codes under realistic noise conditions.

### Available Error Models

1. **Depolarizing Channel**
   - Applies X, Y, or Z with equal probability
   - Most commonly studied error model
   ```python
   models.depolarizing_channel(p=0.01)
   ```

2. **Bit-Flip Channel**
   - Only X errors
   ```python
   models.bit_flip_channel(p=0.05)
   ```

3. **Phase-Flip Channel**
   - Only Z errors
   ```python
   models.phase_flip_channel(p=0.05)
   ```

4. **Amplitude Damping**
   - Models energy loss (T1 process)
   - |1⟩ → |0⟩ decay
   ```python
   models.amplitude_damping_channel(gamma=0.1)
   ```

5. **Phase Damping**
   - Models dephasing (T2 process)
   - Loss of phase coherence
   ```python
   models.phase_damping_channel(gamma=0.1)
   ```

6. **Thermal Relaxation**
   - Realistic hardware model with T1 and T2
   ```python
   models.thermal_relaxation_channel(t1=50, t2=70, gate_time=0.1)
   ```

7. **Custom Pauli Channel**
   - Specify px, py, pz independently
   ```python
   models.custom_pauli_channel(px=0.05, py=0.02, pz=0.03)
   ```

### Using Error Models

```python
from src.error_models import QuantumErrorModels
from src.steane_code import run_steane_code

# Create error model
models = QuantumErrorModels()
noise = models.depolarizing_channel(0.01)

# Run QEC code with noise
# (requires modification to pass noise_model to simulator)
```

---

## Comparison Table {#comparison-table}

| Code | Qubits | Logical | Distance | Corrects | Scalable | Threshold | Notes |
|------|--------|---------|----------|----------|----------|-----------|-------|
| **Bit-flip** | 3 | 1 | 1 | X only | No | - | Educational |
| **Phase-flip** | 3 | 1 | 1 | Z only | No | - | Educational |
| **Shor 9-qubit** | 9 | 1 | 3 | X, Y, Z | No | - | Historic |
| **Five-qubit** | 5 | 1 | 3 | X, Y, Z | No | - | Optimal small |
| **Steane** | 7 | 1 | 3 | X, Y, Z | No | - | Transversal |
| **Surface** | 9+ | 1 | 3+ | X, Y, Z | Yes | ~1% | Best practical |
| **Toric** | 16+ | 2 | 4+ | X, Y, Z | Yes | ~1% | Topological |
| **Bacon-Shor** | 9+ | 1 | 3+ | X, Y, Z | Yes | ~0.1% | Simple decoder |

**Key Terms**:
- **Qubits**: Number of physical qubits required
- **Logical**: Number of logical qubits encoded
- **Distance**: Minimum number of errors needed to cause logical error
- **Threshold**: Maximum physical error rate for which error correction helps
- **Scalable**: Can increase distance by adding more qubits

---

## Usage Examples {#usage-examples}

### Basic Usage

Each QEC code can be run from the command line:

```bash
# Bit-flip code
python src/bit_flip_codes.py --input 0 --error --error-qubit 1

# Shor's code with Y error
python src/shors_9qubit_code.py --input 1 --error --error-qubit 4 --error-type Y

# Five-qubit code
python src/five_qubit_code.py --input 0 --error --error-type Z

# Steane code with more shots
python src/steane_code.py --input 1 --error --shots 4096 --no-draw

# Surface code
python src/surface_code.py --input 0 --error --error-qubit 4

# Toric code (2 logical qubits)
python src/toric_code.py --input1 1 --input2 0 --error --error-qubit 7

# Bacon-Shor code
python src/bacon_shor_code.py --input 1 --error --error-type X
```

### Python API Usage

```python
from src.steane_code import run_steane_code, analyze_steane_results

# Run the code
result = run_steane_code(
    input_value=1,
    apply_error=True,
    error_qubit=3,
    error_type='X',
    shots=1024
)

# Analyze results
success_rate = analyze_steane_results(result['counts'], input_value=1)

# Access circuit
print(result['circuit'].draw())
```

### Testing Error Models

```bash
# Run error model demonstrations
python src/error_models.py
```

---

## Recommendations

### For Learning QEC
1. Start with **Bit-flip code** - simplest concept
2. Then **Phase-flip code** - dual perspective
3. Study **Shor's 9-qubit code** - combines both
4. Explore **Five-qubit code** - optimal efficiency
5. Learn **Steane code** - CSS construction

### For Research/Development
1. **Surface code** - industry standard, highest threshold
2. **Toric code** - theoretical foundation
3. **Bacon-Shor code** - alternative decoder

### For Applications
- **Surface code** is the clear winner for near-term quantum computers
- Used by Google, IBM, and other quantum hardware companies
- Best balance of threshold, scalability, and implementability

---

## References

1. Shor, P. W. (1995). "Scheme for reducing decoherence in quantum computer memory"
2. Steane, A. M. (1996). "Error correcting codes in quantum theory"
3. Kitaev, A. Y. (2003). "Fault-tolerant quantum computation by anyons"
4. Fowler, A. G., et al. (2012). "Surface codes: Towards practical large-scale quantum computation"
5. Bacon, D. (2006). "Operator quantum error-correcting subsystems for self-correcting quantum memories"

---

## Repository Structure

```
qec-control-emulator/
├── src/
│   ├── bit_flip_codes.py       # 3-qubit bit-flip code
│   ├── phase_flip_codes.py     # 3-qubit phase-flip code
│   ├── shors_9qubit_code.py    # Shor's 9-qubit code
│   ├── five_qubit_code.py      # Five-qubit perfect code
│   ├── steane_code.py          # Steane 7-qubit code
│   ├── surface_code.py         # Surface code (distance-3)
│   ├── toric_code.py           # Toric code
│   ├── bacon_shor_code.py      # Bacon-Shor subsystem code
│   └── error_models.py         # Error model library
├── docs/
│   └── QEC_CIRCUITS_GUIDE.md   # This document
└── README.md
```

---

## Contributing

To add a new QEC code:
1. Follow the existing code structure (create, run, analyze functions)
2. Include comprehensive docstrings
3. Add command-line interface with argparse
4. Update this documentation
5. Add tests

---

## License

See repository LICENSE file.

---

**Last Updated**: 2025-11-19
**Version**: 2.0
**Maintainer**: QEC Control Emulator Team
