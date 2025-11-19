"""
Steane Code - 7-Qubit CSS Quantum Error Correction Code

The Steane code is a [[7,1,3]] CSS (Calderbank-Shor-Steane) code that encodes
1 logical qubit into 7 physical qubits. It can detect and correct any single-qubit
error (both bit-flip and phase-flip errors).

The Steane code is more efficient than Shor's 9-qubit code while providing the same
level of protection. It is based on the classical [7,4,3] Hamming code.

Encoding:
- Input: 1 logical qubit
- Output: 7 physical qubits
- Protection: Corrects any single-qubit error

The logical |0⟩ state encodes to:
|0_L⟩ = 1/√8 (|0000000⟩ + |1010101⟩ + |0110011⟩ + |1100110⟩ +
              |0001111⟩ + |1011010⟩ + |0111100⟩ + |1101001⟩)

The logical |1⟩ state encodes to:
|1_L⟩ = X⊗7 |0_L⟩ (applying X to all 7 qubits)
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import argparse


def create_steane_code(input_value=0, apply_error=None, error_qubit=0, error_type='X'):
    """
    Create a Steane code quantum circuit.

    Args:
        input_value (int): Input bit value (0 or 1) for the logical qubit
        apply_error (bool): Whether to apply an error for testing
        error_qubit (int): Which physical qubit to apply the error to (0-6)
        error_type (str): Type of error to apply ('X' for bit-flip, 'Z' for phase-flip, 'Y' for both)

    Returns:
        tuple: (circuit, syndrome_x, syndrome_z, physical_qubits)
    """
    # Create quantum registers
    # 7 physical qubits for encoding
    physical = QuantumRegister(7, 'physical')
    # 3 syndrome qubits for X (bit-flip) errors
    syndrome_x = QuantumRegister(3, 'syn_x')
    # 3 syndrome qubits for Z (phase-flip) errors
    syndrome_z = QuantumRegister(3, 'syn_z')

    # Classical registers to store measurement results
    c_syndrome_x = ClassicalRegister(3, 'c_syn_x')
    c_syndrome_z = ClassicalRegister(3, 'c_syn_z')
    c_physical = ClassicalRegister(7, 'c_phys')

    # Create the quantum circuit
    qc = QuantumCircuit(physical, syndrome_x, syndrome_z, c_syndrome_x, c_syndrome_z, c_physical)

    # ========== ENCODING ==========
    # Encode the logical qubit into 7 physical qubits
    # The encoding creates the logical |0⟩ or |1⟩ state

    if input_value == 1:
        qc.x(physical[0])

    # Apply Hadamard gates to create superposition
    qc.h(physical[0])
    qc.h(physical[2])
    qc.h(physical[4])
    qc.h(physical[6])

    # Apply CNOT gates to create the encoded state
    # These gates implement the stabilizer generators
    qc.cx(physical[0], physical[1])
    qc.cx(physical[2], physical[1])
    qc.cx(physical[2], physical[3])
    qc.cx(physical[4], physical[3])
    qc.cx(physical[4], physical[5])
    qc.cx(physical[6], physical[5])
    qc.cx(physical[0], physical[6])
    qc.cx(physical[2], physical[6])
    qc.cx(physical[4], physical[6])

    qc.barrier()

    # ========== ERROR INJECTION ==========
    if apply_error:
        if error_type == 'X':
            qc.x(physical[error_qubit])
        elif error_type == 'Z':
            qc.z(physical[error_qubit])
        elif error_type == 'Y':
            qc.y(physical[error_qubit])  # Y = iXZ
        qc.barrier()

    # ========== SYNDROME MEASUREMENT FOR X ERRORS ==========
    # Measure X-type stabilizers to detect bit-flip errors
    # Stabilizers: X₀X₁X₂X₃, X₂X₃X₄X₅, X₄X₅X₆X₀

    # First X syndrome
    qc.h(syndrome_x[0])
    qc.cx(syndrome_x[0], physical[0])
    qc.cx(syndrome_x[0], physical[1])
    qc.cx(syndrome_x[0], physical[2])
    qc.cx(syndrome_x[0], physical[3])
    qc.h(syndrome_x[0])

    # Second X syndrome
    qc.h(syndrome_x[1])
    qc.cx(syndrome_x[1], physical[2])
    qc.cx(syndrome_x[1], physical[3])
    qc.cx(syndrome_x[1], physical[4])
    qc.cx(syndrome_x[1], physical[5])
    qc.h(syndrome_x[1])

    # Third X syndrome
    qc.h(syndrome_x[2])
    qc.cx(syndrome_x[2], physical[4])
    qc.cx(syndrome_x[2], physical[5])
    qc.cx(syndrome_x[2], physical[6])
    qc.cx(syndrome_x[2], physical[0])
    qc.h(syndrome_x[2])

    qc.barrier()

    # ========== SYNDROME MEASUREMENT FOR Z ERRORS ==========
    # Measure Z-type stabilizers to detect phase-flip errors
    # Stabilizers: Z₀Z₁Z₂Z₃, Z₂Z₃Z₄Z₅, Z₄Z₅Z₆Z₀

    # First Z syndrome
    qc.cx(physical[0], syndrome_z[0])
    qc.cx(physical[1], syndrome_z[0])
    qc.cx(physical[2], syndrome_z[0])
    qc.cx(physical[3], syndrome_z[0])

    # Second Z syndrome
    qc.cx(physical[2], syndrome_z[1])
    qc.cx(physical[3], syndrome_z[1])
    qc.cx(physical[4], syndrome_z[1])
    qc.cx(physical[5], syndrome_z[1])

    # Third Z syndrome
    qc.cx(physical[4], syndrome_z[2])
    qc.cx(physical[5], syndrome_z[2])
    qc.cx(physical[6], syndrome_z[2])
    qc.cx(physical[0], syndrome_z[2])

    qc.barrier()

    # ========== MEASUREMENT ==========
    qc.measure(syndrome_x, c_syndrome_x)
    qc.measure(syndrome_z, c_syndrome_z)
    qc.measure(physical, c_physical)

    return qc, c_syndrome_x, c_syndrome_z, c_physical


def run_steane_code(input_value=0, apply_error=None, error_qubit=0, error_type='X', shots=1024):
    """
    Run the Steane code circuit and return results.

    Args:
        input_value (int): Input bit value (0 or 1)
        apply_error (bool): Whether to apply an error
        error_qubit (int): Which qubit to apply error to (0-6)
        error_type (str): Type of error ('X', 'Z', or 'Y')
        shots (int): Number of times to run the circuit

    Returns:
        dict: Results containing circuit, counts, and registers
    """
    circuit, c_syn_x, c_syn_z, c_phys = create_steane_code(
        input_value, apply_error, error_qubit, error_type
    )

    # Run the circuit
    simulator = AerSimulator()
    job = simulator.run(circuit, shots=shots)
    result = job.result()
    counts = result.get_counts()

    return {
        'circuit': circuit,
        'counts': counts,
        'syndrome_x': c_syn_x,
        'syndrome_z': c_syn_z,
        'physical': c_phys
    }


def decode_steane_syndrome(syndrome_x, syndrome_z):
    """
    Decode the syndrome measurements to determine which qubit has an error.

    Args:
        syndrome_x (str): X syndrome measurement (3 bits)
        syndrome_z (str): Z syndrome measurement (3 bits)

    Returns:
        tuple: (error_qubit, error_type) or (None, None) if no error
    """
    # Syndrome tables for Steane code
    # Format: syndrome -> qubit location
    x_syndrome_table = {
        '000': None,  # No error
        '111': 0,
        '110': 1,
        '101': 2,
        '011': 3,
        '010': 4,
        '001': 5,
        '100': 6,
    }

    z_syndrome_table = {
        '000': None,  # No error
        '111': 0,
        '110': 1,
        '101': 2,
        '011': 3,
        '010': 4,
        '001': 5,
        '100': 6,
    }

    x_error_qubit = x_syndrome_table.get(syndrome_x)
    z_error_qubit = z_syndrome_table.get(syndrome_z)

    if x_error_qubit is not None and z_error_qubit is not None:
        if x_error_qubit == z_error_qubit:
            return x_error_qubit, 'Y'
        else:
            # Different qubits - shouldn't happen with single error
            return None, 'Unknown'
    elif x_error_qubit is not None:
        return x_error_qubit, 'X'
    elif z_error_qubit is not None:
        return z_error_qubit, 'Z'
    else:
        return None, None


def analyze_steane_results(counts, input_value):
    """
    Analyze the results from running the Steane code.

    Args:
        counts (dict): Measurement counts from the circuit
        input_value (int): Expected input value (0 or 1)

    Returns:
        float: Success rate as a percentage
    """
    total_shots = sum(counts.values())
    successful = 0

    print(f"\n{'='*60}")
    print(f"Steane Code Analysis (Expected input: {input_value})")
    print(f"{'='*60}\n")

    # Track syndrome statistics
    syndrome_stats = {}

    for measurement, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        # Parse measurement: physical(7) syndrome_z(3) syndrome_x(3)
        # The format from Qiskit is: c_phys c_syn_z c_syn_x
        bits = measurement.split()
        if len(bits) == 3:
            physical_bits = bits[0]
            syndrome_z_bits = bits[1]
            syndrome_x_bits = bits[2]
        else:
            # All in one string
            full_measurement = measurement.replace(' ', '')
            physical_bits = full_measurement[0:7]
            syndrome_z_bits = full_measurement[7:10]
            syndrome_x_bits = full_measurement[10:13]

        # Decode syndrome
        error_qubit, error_type = decode_steane_syndrome(syndrome_x_bits, syndrome_z_bits)

        syndrome_key = f"X:{syndrome_x_bits} Z:{syndrome_z_bits}"
        if syndrome_key not in syndrome_stats:
            syndrome_stats[syndrome_key] = {'count': 0, 'error': (error_qubit, error_type)}
        syndrome_stats[syndrome_key]['count'] += count

        # For Steane code, we check if error correction would work
        # The logical qubit value is encoded in the parity of certain qubits
        # For simplicity, we check if the syndrome detected an error correctly
        if syndrome_x_bits == '000' and syndrome_z_bits == '000':
            successful += count

    # Print syndrome statistics
    print("Syndrome Measurements:")
    print(f"{'Syndrome X':<12} {'Syndrome Z':<12} {'Detected Error':<20} {'Count':<8} {'Percentage':<10}")
    print("-" * 70)

    for syndrome_key, data in sorted(syndrome_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        error_qubit, error_type = data['error']
        count = data['count']
        percentage = (count / total_shots) * 100

        if error_qubit is not None:
            error_str = f"Qubit {error_qubit} ({error_type})"
        else:
            error_str = "No error"

        print(f"{syndrome_key:<25} {error_str:<20} {count:<8} {percentage:>6.2f}%")

    success_rate = (successful / total_shots) * 100
    print(f"\n{'='*60}")
    print(f"Success Rate (no error detected): {success_rate:.2f}%")
    print(f"Total Shots: {total_shots}")
    print(f"{'='*60}\n")

    return success_rate


def main():
    """Main function to run Steane code examples."""
    parser = argparse.ArgumentParser(description='Steane 7-Qubit QEC Code')
    parser.add_argument('--input', type=int, default=0, choices=[0, 1],
                        help='Input value for logical qubit (0 or 1)')
    parser.add_argument('--error', action='store_true',
                        help='Apply an error to test error detection')
    parser.add_argument('--error-qubit', type=int, default=0, choices=range(7),
                        help='Which qubit to apply error to (0-6)')
    parser.add_argument('--error-type', type=str, default='X', choices=['X', 'Z', 'Y'],
                        help='Type of error to apply (X, Z, or Y)')
    parser.add_argument('--shots', type=int, default=1024,
                        help='Number of shots to run')
    parser.add_argument('--no-draw', action='store_true',
                        help='Skip drawing the circuit')

    args = parser.parse_args()

    # Run the circuit
    result = run_steane_code(
        input_value=args.input,
        apply_error=args.error,
        error_qubit=args.error_qubit,
        error_type=args.error_type,
        shots=args.shots
    )

    # Draw the circuit
    if not args.no_draw:
        print("\nSteane Code Circuit:")
        print(result['circuit'].draw(output='text'))

    # Analyze results
    analyze_steane_results(result['counts'], args.input)


if __name__ == '__main__':
    main()
