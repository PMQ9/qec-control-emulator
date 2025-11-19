"""
Toric Code - Topological Quantum Error Correction Code

The toric code is a foundational topological quantum error correction code
proposed by Alexei Kitaev. It encodes quantum information in the global topology
of a 2D lattice of qubits arranged on a torus.

Key Properties:
- Qubits are placed on the edges of a 2D square lattice with periodic boundary conditions
- Two types of stabilizers: vertex (star) and plaquette (face) operators
- Encodes 2 logical qubits for an L×L lattice
- Errors correspond to loops on the torus
- No local measurement can distinguish the logical states

This implementation uses a simplified 4×4 lattice (16 qubits) which encodes
2 logical qubits with periodic boundary conditions.

Lattice Structure:
- 16 data qubits on edges
- 4 vertex stabilizers (X-type)
- 4 plaquette stabilizers (Z-type)
- Periodic boundary conditions (torus topology)
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import argparse


def create_toric_code(input_values=(0, 0), apply_error=None, error_qubit=0, error_type='X'):
    """
    Create a toric code quantum circuit.

    Args:
        input_values (tuple): Tuple of two bits (logical qubit 1, logical qubit 2)
        apply_error (bool): Whether to apply an error for testing
        error_qubit (int): Which physical qubit to apply the error to (0-15)
        error_type (str): Type of error to apply ('X' for bit-flip, 'Z' for phase-flip, 'Y' for both)

    Returns:
        tuple: (circuit, vertex_syndrome, plaquette_syndrome, physical_register)
    """
    # Create quantum registers
    # 16 physical qubits arranged on a 4x4 toric lattice
    data = QuantumRegister(16, 'data')

    # 4 syndrome qubits for vertex (X-type) stabilizers
    vertex_syn = QuantumRegister(4, 'vertex')

    # 4 syndrome qubits for plaquette (Z-type) stabilizers
    plaquette_syn = QuantumRegister(4, 'plaquette')

    # Classical registers
    c_vertex = ClassicalRegister(4, 'c_vertex')
    c_plaquette = ClassicalRegister(4, 'c_plaq')
    c_data = ClassicalRegister(16, 'c_data')

    # Create the quantum circuit
    qc = QuantumCircuit(data, vertex_syn, plaquette_syn,
                        c_vertex, c_plaquette, c_data)

    # ========== INITIALIZATION ==========
    # Initialize the logical qubits
    # Logical qubit 1: encoded in horizontal loops
    # Logical qubit 2: encoded in vertical loops

    if input_values[0] == 1:
        # Apply logical X₁ (horizontal loop)
        qc.x(data[0])
        qc.x(data[1])
        qc.x(data[2])
        qc.x(data[3])

    if input_values[1] == 1:
        # Apply logical X₂ (vertical loop)
        qc.x(data[0])
        qc.x(data[4])
        qc.x(data[8])
        qc.x(data[12])

    qc.barrier()

    # ========== ERROR INJECTION ==========
    if apply_error:
        if error_type == 'X':
            qc.x(data[error_qubit])
        elif error_type == 'Z':
            qc.z(data[error_qubit])
        elif error_type == 'Y':
            qc.y(data[error_qubit])
        qc.barrier()

    # ========== VERTEX STABILIZER MEASUREMENTS (X-TYPE) ==========
    # Vertex stabilizers measure products of X operators on 4 adjacent edges
    # Each vertex is surrounded by 4 edges in the toric lattice

    # Vertex 0: qubits 0, 3, 12, 15 (top-left, with periodic BC)
    qc.h(vertex_syn[0])
    qc.cx(vertex_syn[0], data[0])
    qc.cx(vertex_syn[0], data[3])
    qc.cx(vertex_syn[0], data[12])
    qc.cx(vertex_syn[0], data[15])
    qc.h(vertex_syn[0])

    # Vertex 1: qubits 1, 4, 0, 7 (top-right area)
    qc.h(vertex_syn[1])
    qc.cx(vertex_syn[1], data[1])
    qc.cx(vertex_syn[1], data[4])
    qc.cx(vertex_syn[1], data[0])
    qc.cx(vertex_syn[1], data[7])
    qc.h(vertex_syn[1])

    # Vertex 2: qubits 8, 11, 4, 7 (bottom-left area)
    qc.h(vertex_syn[2])
    qc.cx(vertex_syn[2], data[8])
    qc.cx(vertex_syn[2], data[11])
    qc.cx(vertex_syn[2], data[4])
    qc.cx(vertex_syn[2], data[7])
    qc.h(vertex_syn[2])

    # Vertex 3: qubits 9, 12, 5, 8 (center area)
    qc.h(vertex_syn[3])
    qc.cx(vertex_syn[3], data[9])
    qc.cx(vertex_syn[3], data[12])
    qc.cx(vertex_syn[3], data[5])
    qc.cx(vertex_syn[3], data[8])
    qc.h(vertex_syn[3])

    qc.barrier()

    # ========== PLAQUETTE STABILIZER MEASUREMENTS (Z-TYPE) ==========
    # Plaquette stabilizers measure products of Z operators on 4 edges around a face

    # Plaquette 0: qubits 0, 1, 4, 5
    qc.cx(data[0], plaquette_syn[0])
    qc.cx(data[1], plaquette_syn[0])
    qc.cx(data[4], plaquette_syn[0])
    qc.cx(data[5], plaquette_syn[0])

    # Plaquette 1: qubits 2, 3, 6, 7
    qc.cx(data[2], plaquette_syn[1])
    qc.cx(data[3], plaquette_syn[1])
    qc.cx(data[6], plaquette_syn[1])
    qc.cx(data[7], plaquette_syn[1])

    # Plaquette 2: qubits 8, 9, 12, 13
    qc.cx(data[8], plaquette_syn[2])
    qc.cx(data[9], plaquette_syn[2])
    qc.cx(data[12], plaquette_syn[2])
    qc.cx(data[13], plaquette_syn[2])

    # Plaquette 3: qubits 10, 11, 14, 15
    qc.cx(data[10], plaquette_syn[3])
    qc.cx(data[11], plaquette_syn[3])
    qc.cx(data[14], plaquette_syn[3])
    qc.cx(data[15], plaquette_syn[3])

    qc.barrier()

    # ========== MEASUREMENT ==========
    qc.measure(vertex_syn, c_vertex)
    qc.measure(plaquette_syn, c_plaquette)
    qc.measure(data, c_data)

    return qc, c_vertex, c_plaquette, c_data


def run_toric_code(input_values=(0, 0), apply_error=None, error_qubit=0, error_type='X', shots=1024):
    """
    Run the toric code circuit and return results.

    Args:
        input_values (tuple): Tuple of two bits for the two logical qubits
        apply_error (bool): Whether to apply an error
        error_qubit (int): Which qubit to apply error to (0-15)
        error_type (str): Type of error ('X', 'Z', or 'Y')
        shots (int): Number of times to run the circuit

    Returns:
        dict: Results containing circuit, counts, and registers
    """
    circuit, c_vertex, c_plaq, c_data = create_toric_code(
        input_values, apply_error, error_qubit, error_type
    )

    # Run the circuit
    simulator = AerSimulator()
    job = simulator.run(circuit, shots=shots)
    result = job.result()
    counts = result.get_counts()

    return {
        'circuit': circuit,
        'counts': counts,
        'vertex_syndrome': c_vertex,
        'plaquette_syndrome': c_plaq,
        'data': c_data
    }


def decode_toric_syndrome(vertex_syndrome, plaquette_syndrome):
    """
    Decode the syndrome measurements to identify errors.

    In toric code, errors form chains (paths) on the lattice. The syndrome
    indicates the endpoints of these chains. This is a simplified decoder.

    Args:
        vertex_syndrome (str): Vertex syndrome measurement (4 bits)
        plaquette_syndrome (str): Plaquette syndrome measurement (4 bits)

    Returns:
        tuple: (error_description, error_type) or (None, None) if no error
    """
    if vertex_syndrome == '0000' and plaquette_syndrome == '0000':
        return None, None

    # X errors create excitations at plaquettes (Z-stabilizers violated)
    if vertex_syndrome == '0000' and plaquette_syndrome != '0000':
        num_excitations = plaquette_syndrome.count('1')
        return f"X-error chain (plaquette excitations: {num_excitations})", 'X'

    # Z errors create excitations at vertices (X-stabilizers violated)
    if vertex_syndrome != '0000' and plaquette_syndrome == '0000':
        num_excitations = vertex_syndrome.count('1')
        return f"Z-error chain (vertex excitations: {num_excitations})", 'Z'

    # Both syndromes triggered
    if vertex_syndrome != '0000' and plaquette_syndrome != '0000':
        v_exc = vertex_syndrome.count('1')
        p_exc = plaquette_syndrome.count('1')
        return f"Mixed errors (V:{v_exc}, P:{p_exc})", 'Y'

    return 'Unknown', 'Unknown'


def analyze_toric_results(counts, input_values):
    """
    Analyze the results from running the toric code.

    Args:
        counts (dict): Measurement counts from the circuit
        input_values (tuple): Expected input values (logical1, logical2)

    Returns:
        float: Success rate as a percentage
    """
    total_shots = sum(counts.values())
    successful = 0

    print(f"\n{'='*75}")
    print(f"Toric Code Analysis (Expected: Logical1={input_values[0]}, Logical2={input_values[1]})")
    print(f"{'='*75}\n")

    # Track syndrome statistics
    syndrome_stats = {}

    for measurement, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        # Parse measurement: data(16) plaquette(4) vertex(4)
        bits = measurement.split()
        if len(bits) == 3:
            data_bits = bits[0]
            plaquette_bits = bits[1]
            vertex_bits = bits[2]
        else:
            full_measurement = measurement.replace(' ', '')
            data_bits = full_measurement[0:16]
            plaquette_bits = full_measurement[16:20]
            vertex_bits = full_measurement[20:24]

        # Decode syndrome
        error_desc, error_type = decode_toric_syndrome(vertex_bits, plaquette_bits)

        syndrome_key = f"V:{vertex_bits} P:{plaquette_bits}"
        if syndrome_key not in syndrome_stats:
            syndrome_stats[syndrome_key] = {
                'count': 0,
                'error': (error_desc, error_type)
            }
        syndrome_stats[syndrome_key]['count'] += count

        # Count as successful if no error detected
        if vertex_bits == '0000' and plaquette_bits == '0000':
            successful += count

    # Print syndrome statistics
    print("Syndrome Measurements:")
    print(f"{'Vertex':<10} {'Plaquette':<10} {'Detected Error':<35} {'Count':<8} {'%':<10}")
    print("-" * 75)

    for syndrome_key, data in sorted(syndrome_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        error_desc, error_type = data['error']
        count = data['count']
        percentage = (count / total_shots) * 100

        if error_desc is not None:
            error_str = f"{error_desc} ({error_type})"
        else:
            error_str = "No error"

        print(f"{syndrome_key:<21} {error_str:<35} {count:<8} {percentage:>6.2f}%")

    success_rate = (successful / total_shots) * 100
    print(f"\n{'='*75}")
    print(f"Success Rate (no error detected): {success_rate:.2f}%")
    print(f"Total Shots: {total_shots}")
    print(f"{'='*75}\n")

    return success_rate


def main():
    """Main function to run toric code examples."""
    parser = argparse.ArgumentParser(description='Toric Code Topological QEC')
    parser.add_argument('--input1', type=int, default=0, choices=[0, 1],
                        help='Input value for first logical qubit (0 or 1)')
    parser.add_argument('--input2', type=int, default=0, choices=[0, 1],
                        help='Input value for second logical qubit (0 or 1)')
    parser.add_argument('--error', action='store_true',
                        help='Apply an error to test error detection')
    parser.add_argument('--error-qubit', type=int, default=0, choices=range(16),
                        help='Which qubit to apply error to (0-15)')
    parser.add_argument('--error-type', type=str, default='X', choices=['X', 'Z', 'Y'],
                        help='Type of error to apply (X, Z, or Y)')
    parser.add_argument('--shots', type=int, default=1024,
                        help='Number of shots to run')
    parser.add_argument('--no-draw', action='store_true',
                        help='Skip drawing the circuit')

    args = parser.parse_args()

    # Run the circuit
    result = run_toric_code(
        input_values=(args.input1, args.input2),
        apply_error=args.error,
        error_qubit=args.error_qubit,
        error_type=args.error_type,
        shots=args.shots
    )

    # Draw the circuit
    if not args.no_draw:
        print("\nToric Code Circuit:")
        print(result['circuit'].draw(output='text', fold=-1))

    # Analyze results
    analyze_toric_results(result['counts'], (args.input1, args.input2))


if __name__ == '__main__':
    main()
