"""
Surface Code - Topological Quantum Error Correction Code

The surface code is one of the most promising quantum error correction codes
for fault-tolerant quantum computing. It has several advantages:
- High error threshold (~1% per gate)
- 2D nearest-neighbor architecture (easy to implement in hardware)
- Scalable to large systems
- Well-understood decoding algorithms

This implementation demonstrates a distance-3 surface code, which encodes
1 logical qubit using 9 physical qubits arranged in a 2D grid.

Grid Layout (distance-3):
  Q0 - Q1 - Q2
  |    |    |
  Q3 - Q4 - Q5
  |    |    |
  Q6 - Q7 - Q8

The surface code uses two types of stabilizers:
- X-type (star) stabilizers: measure products of X operators
- Z-type (plaquette) stabilizers: measure products of Z operators

Properties:
- Encodes 1 logical qubit into 9 physical qubits
- Distance d=3 (can correct 1 error)
- 4 X-stabilizers and 4 Z-stabilizers
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import argparse


def create_surface_code(input_value=0, apply_error=None, error_qubit=0, error_type='X'):
    """
    Create a distance-3 surface code quantum circuit.

    Args:
        input_value (int): Input bit value (0 or 1) for the logical qubit
        apply_error (bool): Whether to apply an error for testing
        error_qubit (int): Which physical qubit to apply the error to (0-8)
        error_type (str): Type of error to apply ('X' for bit-flip, 'Z' for phase-flip, 'Y' for both)

    Returns:
        tuple: (circuit, x_syndrome_register, z_syndrome_register, physical_register)
    """
    # Create quantum registers
    # 9 physical qubits arranged in a 3x3 grid
    physical = QuantumRegister(9, 'data')

    # 4 syndrome qubits for X-type stabilizers (stars)
    syndrome_x = QuantumRegister(4, 'syn_x')

    # 4 syndrome qubits for Z-type stabilizers (plaquettes)
    syndrome_z = QuantumRegister(4, 'syn_z')

    # Classical registers
    c_syndrome_x = ClassicalRegister(4, 'c_syn_x')
    c_syndrome_z = ClassicalRegister(4, 'c_syn_z')
    c_physical = ClassicalRegister(9, 'c_data')

    # Create the quantum circuit
    qc = QuantumCircuit(physical, syndrome_x, syndrome_z,
                        c_syndrome_x, c_syndrome_z, c_physical)

    # ========== INITIALIZATION ==========
    # Initialize the logical qubit state
    # For surface code, logical |0⟩ is the +1 eigenstate of all Z-stabilizers
    # Logical |1⟩ can be created by applying a logical X operator

    if input_value == 1:
        # Apply logical X (acts on a string of qubits)
        # For this simple implementation, we apply X to the left column
        qc.x(physical[0])
        qc.x(physical[3])
        qc.x(physical[6])

    qc.barrier()

    # ========== ERROR INJECTION ==========
    if apply_error:
        if error_type == 'X':
            qc.x(physical[error_qubit])
        elif error_type == 'Z':
            qc.z(physical[error_qubit])
        elif error_type == 'Y':
            qc.y(physical[error_qubit])
        qc.barrier()

    # ========== X-TYPE STABILIZER MEASUREMENTS ==========
    # X-stabilizers (star operators) measure products of X on neighboring qubits

    # X-stabilizer 0: measures X on qubits 0, 1, 3
    qc.h(syndrome_x[0])
    qc.cx(syndrome_x[0], physical[0])
    qc.cx(syndrome_x[0], physical[1])
    qc.cx(syndrome_x[0], physical[3])
    qc.h(syndrome_x[0])

    # X-stabilizer 1: measures X on qubits 1, 2, 4
    qc.h(syndrome_x[1])
    qc.cx(syndrome_x[1], physical[1])
    qc.cx(syndrome_x[1], physical[2])
    qc.cx(syndrome_x[1], physical[4])
    qc.h(syndrome_x[1])

    # X-stabilizer 2: measures X on qubits 3, 4, 6
    qc.h(syndrome_x[2])
    qc.cx(syndrome_x[2], physical[3])
    qc.cx(syndrome_x[2], physical[4])
    qc.cx(syndrome_x[2], physical[6])
    qc.h(syndrome_x[2])

    # X-stabilizer 3: measures X on qubits 4, 5, 7
    qc.h(syndrome_x[3])
    qc.cx(syndrome_x[3], physical[4])
    qc.cx(syndrome_x[3], physical[5])
    qc.cx(syndrome_x[3], physical[7])
    qc.h(syndrome_x[3])

    qc.barrier()

    # ========== Z-TYPE STABILIZER MEASUREMENTS ==========
    # Z-stabilizers (plaquette operators) measure products of Z on neighboring qubits

    # Z-stabilizer 0: measures Z on qubits 0, 1, 3, 4
    qc.cx(physical[0], syndrome_z[0])
    qc.cx(physical[1], syndrome_z[0])
    qc.cx(physical[3], syndrome_z[0])
    qc.cx(physical[4], syndrome_z[0])

    # Z-stabilizer 1: measures Z on qubits 1, 2, 4, 5
    qc.cx(physical[1], syndrome_z[1])
    qc.cx(physical[2], syndrome_z[1])
    qc.cx(physical[4], syndrome_z[1])
    qc.cx(physical[5], syndrome_z[1])

    # Z-stabilizer 2: measures Z on qubits 3, 4, 6, 7
    qc.cx(physical[3], syndrome_z[2])
    qc.cx(physical[4], syndrome_z[2])
    qc.cx(physical[6], syndrome_z[2])
    qc.cx(physical[7], syndrome_z[2])

    # Z-stabilizer 3: measures Z on qubits 4, 5, 7, 8
    qc.cx(physical[4], syndrome_z[3])
    qc.cx(physical[5], syndrome_z[3])
    qc.cx(physical[7], syndrome_z[3])
    qc.cx(physical[8], syndrome_z[3])

    qc.barrier()

    # ========== MEASUREMENT ==========
    qc.measure(syndrome_x, c_syndrome_x)
    qc.measure(syndrome_z, c_syndrome_z)
    qc.measure(physical, c_physical)

    return qc, c_syndrome_x, c_syndrome_z, c_physical


def run_surface_code(input_value=0, apply_error=None, error_qubit=0, error_type='X', shots=1024):
    """
    Run the surface code circuit and return results.

    Args:
        input_value (int): Input bit value (0 or 1)
        apply_error (bool): Whether to apply an error
        error_qubit (int): Which qubit to apply error to (0-8)
        error_type (str): Type of error ('X', 'Z', or 'Y')
        shots (int): Number of times to run the circuit

    Returns:
        dict: Results containing circuit, counts, and registers
    """
    circuit, c_syn_x, c_syn_z, c_data = create_surface_code(
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
        'physical': c_data
    }


def decode_surface_syndrome(syndrome_x, syndrome_z):
    """
    Decode the syndrome measurements to identify errors.

    This is a simplified decoder for demonstration purposes.
    Real surface code decoders use minimum-weight perfect matching (MWPM).

    Args:
        syndrome_x (str): X syndrome measurement (4 bits)
        syndrome_z (str): Z syndrome measurement (4 bits)

    Returns:
        tuple: (error_location, error_type) or (None, None) if no error
    """
    # This is a simplified lookup table for single-qubit errors
    # In practice, surface codes use sophisticated decoding algorithms

    if syndrome_x == '0000' and syndrome_z == '0000':
        return None, None

    # X errors affect Z-stabilizers
    if syndrome_x == '0000' and syndrome_z != '0000':
        return 'X-error detected', 'X'

    # Z errors affect X-stabilizers
    if syndrome_x != '0000' and syndrome_z == '0000':
        return 'Z-error detected', 'Z'

    # Both syndromes triggered - could be Y error
    if syndrome_x != '0000' and syndrome_z != '0000':
        return 'Y-error or multiple errors', 'Y'

    return 'Unknown', 'Unknown'


def analyze_surface_results(counts, input_value):
    """
    Analyze the results from running the surface code.

    Args:
        counts (dict): Measurement counts from the circuit
        input_value (int): Expected input value (0 or 1)

    Returns:
        float: Success rate as a percentage
    """
    total_shots = sum(counts.values())
    successful = 0

    print(f"\n{'='*70}")
    print(f"Surface Code Analysis (Expected input: {input_value})")
    print(f"{'='*70}\n")

    # Track syndrome statistics
    syndrome_stats = {}

    for measurement, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        # Parse measurement: physical(9) syndrome_z(4) syndrome_x(4)
        bits = measurement.split()
        if len(bits) == 3:
            physical_bits = bits[0]
            syndrome_z_bits = bits[1]
            syndrome_x_bits = bits[2]
        else:
            full_measurement = measurement.replace(' ', '')
            physical_bits = full_measurement[0:9]
            syndrome_z_bits = full_measurement[9:13]
            syndrome_x_bits = full_measurement[13:17]

        # Decode syndrome
        error_location, error_type = decode_surface_syndrome(syndrome_x_bits, syndrome_z_bits)

        syndrome_key = f"X:{syndrome_x_bits} Z:{syndrome_z_bits}"
        if syndrome_key not in syndrome_stats:
            syndrome_stats[syndrome_key] = {
                'count': 0,
                'error': (error_location, error_type)
            }
        syndrome_stats[syndrome_key]['count'] += count

        # Count as successful if no error detected
        if syndrome_x_bits == '0000' and syndrome_z_bits == '0000':
            successful += count

    # Print syndrome statistics
    print("Syndrome Measurements:")
    print(f"{'Syndrome X':<12} {'Syndrome Z':<12} {'Detected Error':<25} {'Count':<8} {'%':<10}")
    print("-" * 70)

    for syndrome_key, data in sorted(syndrome_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        error_location, error_type = data['error']
        count = data['count']
        percentage = (count / total_shots) * 100

        if error_location is not None:
            error_str = f"{error_location} ({error_type})"
        else:
            error_str = "No error"

        print(f"{syndrome_key:<25} {error_str:<25} {count:<8} {percentage:>6.2f}%")

    success_rate = (successful / total_shots) * 100
    print(f"\n{'='*70}")
    print(f"Success Rate (no error detected): {success_rate:.2f}%")
    print(f"Total Shots: {total_shots}")
    print(f"{'='*70}\n")

    return success_rate


def main():
    """Main function to run surface code examples."""
    parser = argparse.ArgumentParser(description='Surface Code (Distance-3) QEC')
    parser.add_argument('--input', type=int, default=0, choices=[0, 1],
                        help='Input value for logical qubit (0 or 1)')
    parser.add_argument('--error', action='store_true',
                        help='Apply an error to test error detection')
    parser.add_argument('--error-qubit', type=int, default=0, choices=range(9),
                        help='Which qubit to apply error to (0-8)')
    parser.add_argument('--error-type', type=str, default='X', choices=['X', 'Z', 'Y'],
                        help='Type of error to apply (X, Z, or Y)')
    parser.add_argument('--shots', type=int, default=1024,
                        help='Number of shots to run')
    parser.add_argument('--no-draw', action='store_true',
                        help='Skip drawing the circuit')

    args = parser.parse_args()

    # Run the circuit
    result = run_surface_code(
        input_value=args.input,
        apply_error=args.error,
        error_qubit=args.error_qubit,
        error_type=args.error_type,
        shots=args.shots
    )

    # Draw the circuit
    if not args.no_draw:
        print("\nSurface Code Circuit:")
        print(result['circuit'].draw(output='text', fold=-1))

    # Analyze results
    analyze_surface_results(result['counts'], args.input)


if __name__ == '__main__':
    main()
