"""
Five-Qubit Code - [[5,1,3]] Perfect Quantum Error Correction Code

The five-qubit code is the smallest quantum error correction code that can
protect against arbitrary single-qubit errors. It encodes 1 logical qubit
into 5 physical qubits.

This code is "perfect" because it achieves the quantum Hamming bound with
equality - it uses the minimum number of physical qubits needed to correct
one error.

Key Properties:
- Encodes 1 logical qubit into 5 physical qubits
- Can correct any single-qubit error (X, Y, Z)
- Uses 4 stabilizer generators
- Most efficient single-error correcting code

The code is defined by four stabilizers:
S₁ = XZZXI
S₂ = IXZZX
S₃ = XIXZZ
S₄ = ZXIXZ

Logical operators:
X̄ = XXXXX (logical X)
Z̄ = ZZZZZ (logical Z)
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import argparse


def create_five_qubit_code(input_value=0, apply_error=None, error_qubit=0, error_type='X'):
    """
    Create a five-qubit code quantum circuit.

    Args:
        input_value (int): Input bit value (0 or 1) for the logical qubit
        apply_error (bool): Whether to apply an error for testing
        error_qubit (int): Which physical qubit to apply the error to (0-4)
        error_type (str): Type of error to apply ('X' for bit-flip, 'Z' for phase-flip, 'Y' for both)

    Returns:
        tuple: (circuit, syndrome_register, physical_register)
    """
    # Create quantum registers
    # 5 physical qubits for encoding
    physical = QuantumRegister(5, 'physical')
    # 4 syndrome qubits for stabilizer measurements
    syndrome = QuantumRegister(4, 'syndrome')

    # Classical registers to store measurement results
    c_syndrome = ClassicalRegister(4, 'c_syn')
    c_physical = ClassicalRegister(5, 'c_phys')

    # Create the quantum circuit
    qc = QuantumCircuit(physical, syndrome, c_syndrome, c_physical)

    # ========== ENCODING ==========
    # Encode the logical qubit into 5 physical qubits
    # Start with the logical qubit state in physical[0]

    if input_value == 1:
        qc.x(physical[0])

    # The encoding circuit transforms |ψ⟩|0000⟩ into the encoded state
    # This encoding creates a state protected by the four stabilizers

    # First layer: Create entanglement
    qc.h(physical[1])
    qc.h(physical[2])
    qc.h(physical[3])
    qc.h(physical[4])

    # Second layer: CNOT gates to create the encoded state
    qc.cx(physical[0], physical[1])
    qc.cx(physical[0], physical[2])
    qc.cx(physical[1], physical[3])
    qc.cx(physical[2], physical[4])

    # Third layer: Additional gates for proper encoding
    qc.cx(physical[3], physical[0])
    qc.cx(physical[4], physical[0])
    qc.cx(physical[3], physical[1])
    qc.cx(physical[4], physical[2])

    # Fourth layer: Z rotations
    qc.cz(physical[0], physical[3])
    qc.cz(physical[1], physical[4])

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

    # ========== STABILIZER MEASUREMENTS ==========
    # Measure the four stabilizers to detect errors
    # S₁ = XZZXI, S₂ = IXZZX, S₃ = XIXZZ, S₄ = ZXIXZ

    # Stabilizer 1: XZZXI
    qc.h(syndrome[0])
    qc.cx(syndrome[0], physical[0])  # X on qubit 0
    qc.cz(syndrome[0], physical[1])  # Z on qubit 1
    qc.cz(syndrome[0], physical[2])  # Z on qubit 2
    qc.cx(syndrome[0], physical[3])  # X on qubit 3
    # I on qubit 4
    qc.h(syndrome[0])

    # Stabilizer 2: IXZZX
    qc.h(syndrome[1])
    # I on qubit 0
    qc.cx(syndrome[1], physical[1])  # X on qubit 1
    qc.cz(syndrome[1], physical[2])  # Z on qubit 2
    qc.cz(syndrome[1], physical[3])  # Z on qubit 3
    qc.cx(syndrome[1], physical[4])  # X on qubit 4
    qc.h(syndrome[1])

    # Stabilizer 3: XIXZZ
    qc.h(syndrome[2])
    qc.cx(syndrome[2], physical[0])  # X on qubit 0
    # I on qubit 1
    qc.cx(syndrome[2], physical[2])  # X on qubit 2
    qc.cz(syndrome[2], physical[3])  # Z on qubit 3
    qc.cz(syndrome[2], physical[4])  # Z on qubit 4
    qc.h(syndrome[2])

    # Stabilizer 4: ZXIXZ
    qc.h(syndrome[3])
    qc.cz(syndrome[3], physical[0])  # Z on qubit 0
    qc.cx(syndrome[3], physical[1])  # X on qubit 1
    # I on qubit 2
    qc.cx(syndrome[3], physical[3])  # X on qubit 3
    qc.cz(syndrome[3], physical[4])  # Z on qubit 4
    qc.h(syndrome[3])

    qc.barrier()

    # ========== MEASUREMENT ==========
    qc.measure(syndrome, c_syndrome)
    qc.measure(physical, c_physical)

    return qc, c_syndrome, c_physical


def run_five_qubit_code(input_value=0, apply_error=None, error_qubit=0, error_type='X', shots=1024):
    """
    Run the five-qubit code circuit and return results.

    Args:
        input_value (int): Input bit value (0 or 1)
        apply_error (bool): Whether to apply an error
        error_qubit (int): Which qubit to apply error to (0-4)
        error_type (str): Type of error ('X', 'Z', or 'Y')
        shots (int): Number of times to run the circuit

    Returns:
        dict: Results containing circuit, counts, and registers
    """
    circuit, c_syn, c_phys = create_five_qubit_code(
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
        'syndrome': c_syn,
        'physical': c_phys
    }


def decode_five_qubit_syndrome(syndrome):
    """
    Decode the syndrome measurement to determine the error.

    Args:
        syndrome (str): Syndrome measurement (4 bits)

    Returns:
        tuple: (error_qubit, error_type) or (None, None) if no error
    """
    # Syndrome table for five-qubit code
    # Format: syndrome (S4 S3 S2 S1) -> (error_qubit, error_type)
    # This is a simplified lookup table for common single-qubit errors

    syndrome_table = {
        '0000': (None, None),  # No error

        # X errors on each qubit
        '1011': (0, 'X'),
        '0111': (1, 'X'),
        '1101': (2, 'X'),
        '1110': (3, 'X'),
        '0110': (4, 'X'),

        # Z errors on each qubit
        '0101': (0, 'Z'),
        '1010': (1, 'Z'),
        '0011': (2, 'Z'),
        '1100': (3, 'Z'),
        '1001': (4, 'Z'),

        # Y errors on each qubit
        '1110': (0, 'Y'),
        '1101': (1, 'Y'),
        '1110': (2, 'Y'),
        '0010': (3, 'Y'),
        '1111': (4, 'Y'),
    }

    return syndrome_table.get(syndrome, (None, 'Unknown'))


def analyze_five_qubit_results(counts, input_value):
    """
    Analyze the results from running the five-qubit code.

    Args:
        counts (dict): Measurement counts from the circuit
        input_value (int): Expected input value (0 or 1)

    Returns:
        float: Success rate as a percentage
    """
    total_shots = sum(counts.values())
    successful = 0

    print(f"\n{'='*60}")
    print(f"Five-Qubit Code Analysis (Expected input: {input_value})")
    print(f"{'='*60}\n")

    # Track syndrome statistics
    syndrome_stats = {}

    for measurement, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        # Parse measurement: physical(5) syndrome(4)
        # The format from Qiskit is: c_phys c_syn
        bits = measurement.split()
        if len(bits) == 2:
            physical_bits = bits[0]
            syndrome_bits = bits[1]
        else:
            # All in one string
            full_measurement = measurement.replace(' ', '')
            physical_bits = full_measurement[0:5]
            syndrome_bits = full_measurement[5:9]

        # Decode syndrome
        error_qubit, error_type = decode_five_qubit_syndrome(syndrome_bits)

        if syndrome_bits not in syndrome_stats:
            syndrome_stats[syndrome_bits] = {
                'count': 0,
                'error': (error_qubit, error_type)
            }
        syndrome_stats[syndrome_bits]['count'] += count

        # No error detected
        if syndrome_bits == '0000':
            successful += count

    # Print syndrome statistics
    print("Syndrome Measurements:")
    print(f"{'Syndrome':<12} {'Detected Error':<20} {'Count':<8} {'Percentage':<10}")
    print("-" * 60)

    for syndrome_bits, data in sorted(syndrome_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        error_qubit, error_type = data['error']
        count = data['count']
        percentage = (count / total_shots) * 100

        if error_qubit is not None:
            if error_type == 'Unknown':
                error_str = "Unknown error"
            else:
                error_str = f"Qubit {error_qubit} ({error_type})"
        else:
            error_str = "No error"

        print(f"{syndrome_bits:<12} {error_str:<20} {count:<8} {percentage:>6.2f}%")

    success_rate = (successful / total_shots) * 100
    print(f"\n{'='*60}")
    print(f"Success Rate (no error detected): {success_rate:.2f}%")
    print(f"Total Shots: {total_shots}")
    print(f"{'='*60}\n")

    return success_rate


def main():
    """Main function to run five-qubit code examples."""
    parser = argparse.ArgumentParser(description='Five-Qubit [[5,1,3]] Perfect QEC Code')
    parser.add_argument('--input', type=int, default=0, choices=[0, 1],
                        help='Input value for logical qubit (0 or 1)')
    parser.add_argument('--error', action='store_true',
                        help='Apply an error to test error detection')
    parser.add_argument('--error-qubit', type=int, default=0, choices=range(5),
                        help='Which qubit to apply error to (0-4)')
    parser.add_argument('--error-type', type=str, default='X', choices=['X', 'Z', 'Y'],
                        help='Type of error to apply (X, Z, or Y)')
    parser.add_argument('--shots', type=int, default=1024,
                        help='Number of shots to run')
    parser.add_argument('--no-draw', action='store_true',
                        help='Skip drawing the circuit')

    args = parser.parse_args()

    # Run the circuit
    result = run_five_qubit_code(
        input_value=args.input,
        apply_error=args.error,
        error_qubit=args.error_qubit,
        error_type=args.error_type,
        shots=args.shots
    )

    # Draw the circuit
    if not args.no_draw:
        print("\nFive-Qubit Code Circuit:")
        print(result['circuit'].draw(output='text'))

    # Analyze results
    analyze_five_qubit_results(result['counts'], args.input)


if __name__ == '__main__':
    main()
