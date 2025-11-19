# qec-control-emulator
Quantum Error Correction Control Emulator project, mimics how a real QEC control system works.

## Setup

### Prerequisites
- Python 3.9 or higher
- pip

### Installation

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Activate virtual environment:**
   ```bash
   venv\Scripts\activate
   ```

### Learning Resources
- Qiskit documentation: https://qiskit.org/documentation/

## Quantum Error Correction Circuits

This repository implements a comprehensive collection of quantum error correction codes, from basic 3-qubit codes to advanced topological codes.

### Implemented QEC Codes

#### Basic Codes
1. **Bit-Flip Code (3-qubit)** - `src/bit_flip_codes.py`
   - Corrects single bit-flip (X) errors
   - Encoding: 1 logical → 3 physical qubits
   - Distance: d=1

2. **Phase-Flip Code (3-qubit)** - `src/phase_flip_codes.py`
   - Corrects single phase-flip (Z) errors
   - Encoding: 1 logical → 3 physical qubits
   - Distance: d=1

#### Advanced Stabilizer Codes
3. **Shor's 9-Qubit Code** - `src/shors_9qubit_code.py`
   - First code to correct arbitrary single-qubit errors
   - Encoding: 1 logical → 9 physical qubits
   - Corrects: X, Y, Z errors
   - Distance: d=3

4. **Five-Qubit Code [[5,1,3]]** - `src/five_qubit_code.py`
   - Smallest perfect code for arbitrary single-qubit errors
   - Encoding: 1 logical → 5 physical qubits
   - Corrects: X, Y, Z errors
   - Distance: d=3
   - Optimal efficiency

5. **Steane Code [[7,1,3]]** - `src/steane_code.py`
   - CSS code based on classical Hamming code
   - Encoding: 1 logical → 7 physical qubits
   - Corrects: X, Y, Z errors
   - Distance: d=3
   - Supports transversal gates

#### Topological Codes
6. **Surface Code (Distance-3)** - `src/surface_code.py`
   - Leading candidate for fault-tolerant quantum computing
   - Encoding: 1 logical → 9 physical qubits (distance-3)
   - 2D nearest-neighbor architecture
   - Scalable to arbitrary distances
   - High error threshold (~1%)

7. **Toric Code** - `src/toric_code.py`
   - Foundational topological code
   - Encoding: 2 logical qubits → 16 physical qubits
   - Periodic boundary conditions (torus topology)
   - Distance: d=4

#### Subsystem Codes
8. **Bacon-Shor Code [[9,1,3]]** - `src/bacon_shor_code.py`
   - Subsystem code with simplified syndrome measurement
   - Encoding: 1 logical → 9 physical qubits
   - Weight-2 stabilizer measurements
   - Simpler decoding than surface code

### Error Models

**Error Models Library** - `src/error_models.py`
- Depolarizing channel
- Bit-flip channel
- Phase-flip channel
- Amplitude damping (T1 process)
- Phase damping (T2 process)
- Thermal relaxation (realistic hardware)
- Custom Pauli channel

## Documentation

For a comprehensive guide to all QEC circuits, see:
**[QEC Circuits Guide](docs/QEC_CIRCUITS_GUIDE.md)**

This document includes:
- Detailed explanations of each code
- How they work
- Usage examples
- Comparison table
- Recommendations for learning and research

## Usage Examples

### Running QEC Codes

Each QEC code can be run from the command line:

```bash
# Bit-flip code
python src/bit_flip_codes.py --input 0 --error --error-qubit 1

# Shor's 9-qubit code
python src/shors_9qubit_code.py --input 1 --error --error-qubit 4 --error-type Y

# Five-qubit code
python src/five_qubit_code.py --input 0 --error --error-type Z

# Steane code
python src/steane_code.py --input 1 --error --shots 2048

# Surface code
python src/surface_code.py --input 0 --error --error-qubit 4

# Toric code (2 logical qubits)
python src/toric_code.py --input1 1 --input2 0 --error --error-qubit 7

# Bacon-Shor code
python src/bacon_shor_code.py --input 1 --error --error-type X
```

### Using Error Models

```bash
# Demonstrate all error models
python src/error_models.py
```

### Python API

```python
from src.steane_code import run_steane_code, analyze_steane_results

# Run the Steane code
result = run_steane_code(
    input_value=1,
    apply_error=True,
    error_qubit=3,
    error_type='X',
    shots=1024
)

# Analyze results
success_rate = analyze_steane_results(result['counts'], input_value=1)
```

## Quick Comparison

| Code | Qubits | Distance | Corrects | Scalable | Best For |
|------|--------|----------|----------|----------|----------|
| Bit-flip | 3 | 1 | X only | No | Learning |
| Phase-flip | 3 | 1 | Z only | No | Learning |
| Shor 9-qubit | 9 | 3 | X,Y,Z | No | Historical |
| Five-qubit | 5 | 3 | X,Y,Z | No | Optimal small |
| Steane | 7 | 3 | X,Y,Z | No | Transversal gates |
| Surface | 9+ | 3+ | X,Y,Z | Yes | **Practical QC** |
| Toric | 16+ | 4+ | X,Y,Z | Yes | Theory |
| Bacon-Shor | 9+ | 3+ | X,Y,Z | Yes | Simple decoder |

## Circuit Diagrams

### Bit-Flip Code
<img src="utils/docs/quantum_circuit_bit_flip_qec.png" width="80%">

### Phase-Flip Code
<img src="utils/docs/quantum_circuit_phase_flip_qec.png" width="80%">

## Features

- ✅ Complete implementation of 8 major QEC codes
- ✅ Comprehensive error model library
- ✅ Command-line interface for all codes
- ✅ Python API for integration
- ✅ Detailed documentation and examples
- ✅ Syndrome measurement and analysis
- ✅ Error detection and decoding

## References

1. Shor, P. W. (1995). "Scheme for reducing decoherence in quantum computer memory"
2. Steane, A. M. (1996). "Error correcting codes in quantum theory"
3. Kitaev, A. Y. (2003). "Fault-tolerant quantum computation by anyons"
4. Fowler, A. G., et al. (2012). "Surface codes: Towards practical large-scale quantum computation"
