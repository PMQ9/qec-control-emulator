"""
Bacon-Shor Code - Subsystem Quantum Error Correction Code

The Bacon-Shor code is a subsystem code that combines features of both
the Shor code and the surface code. It is simpler to decode than the surface
code while maintaining good error correction properties.

Key Properties:
- Subsystem code (uses gauge qubits)
- Encodes 1 logical qubit
- Simpler syndrome measurement than surface codes
- Weight-2 stabilizer measurements (only involves 2 qubits at a time)
- No need for complex MWPM decoder

This implementation uses a [[9,1,3]] Bacon-Shor code arranged in a 3×3 grid:

Qubit Layout:
  Q0 - Q1 - Q2
  |    |    |
  Q3 - Q4 - Q5
  |    |    |
  Q6 - Q7 - Q8

Stabilizers:
- X-checks: ZZ on horizontal pairs
- Z-checks: XX on vertical pairs
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import argparse


def create_bacon_shor_code(input_value=0, apply_error=None, error_qubit=0, error_type='X'):
    """
    Create a Bacon-Shor code quantum circuit.

    Args:
        input_value (int): Input bit value (0 or 1) for the logical qubit
        apply_error (bool): Whether to apply an error for testing
        error_qubit (int): Which physical qubit to apply the error to (0-8)
        error_type (str): Type of error to apply ('X', 'Z', or 'Y')

    Returns:
        tuple: (circuit, x_syndrome, z_syndrome, physical_register)
    """
    # Create quantum registers
    # 9 physical qubits in a 3×3 grid
    data = QuantumRegister(9, 'data')

    # 6 syndrome qubits for X-checks (measuring ZZ)
    x_syndrome = QuantumRegister(6, 'x_syn')

    # 6 syndrome qubits for Z-checks (measuring XX)
    z_syndrome = QuantumRegister(6, 'z_syn')

    # Classical registers
    c_x_syn = ClassicalRegister(6, 'c_x_syn')
    c_z_syn = ClassicalRegister(6, 'c_z_syn')
    c_data = ClassicalRegister(9, 'c_data')

    # Create the quantum circuit
    qc = QuantumCircuit(data, x_syndrome, z_syndrome,
                        c_x_syn, c_z_syn, c_data)

    # ========== INITIALIZATION ==========
    # Initialize the logical qubit
    # Logical |0⟩ is the +1 eigenstate of all stabilizers
    # Logical |1⟩ is obtained by applying logical X

    if input_value == 1:
        # Apply logical X to all qubits in first row
        qc.x(data[0])
        qc.x(data[1])
        qc.x(data[2])

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

    # ========== X-STABILIZER MEASUREMENTS (ZZ checks) ==========
    # X-stabilizers detect bit-flip errors by measuring ZZ on horizontal pairs
    # These are weight-2 checks, making them easier to implement

    # Row 0: horizontal ZZ checks
    # Q0-Q1
    qc.cx(data[0], x_syndrome[0])
    qc.cx(data[1], x_syndrome[0])

    # Q1-Q2
    qc.cx(data[1], x_syndrome[1])
    qc.cx(data[2], x_syndrome[1])

    # Row 1: horizontal ZZ checks
    # Q3-Q4
    qc.cx(data[3], x_syndrome[2])
    qc.cx(data[4], x_syndrome[2])

    # Q4-Q5
    qc.cx(data[4], x_syndrome[3])
    qc.cx(data[5], x_syndrome[3])

    # Row 2: horizontal ZZ checks
    # Q6-Q7
    qc.cx(data[6], x_syndrome[4])
    qc.cx(data[7], x_syndrome[4])

    # Q7-Q8
    qc.cx(data[7], x_syndrome[5])
    qc.cx(data[8], x_syndrome[5])

    qc.barrier()

    # ========== Z-STABILIZER MEASUREMENTS (XX checks) ==========
    # Z-stabilizers detect phase-flip errors by measuring XX on vertical pairs

    # Column 0: vertical XX checks
    # Q0-Q3
    qc.h(z_syndrome[0])
    qc.cx(z_syndrome[0], data[0])
    qc.cx(z_syndrome[0], data[3])
    qc.h(z_syndrome[0])

    # Q3-Q6
    qc.h(z_syndrome[1])
    qc.cx(z_syndrome[1], data[3])
    qc.cx(z_syndrome[1], data[6])
    qc.h(z_syndrome[1])

    # Column 1: vertical XX checks
    # Q1-Q4
    qc.h(z_syndrome[2])
    qc.cx(z_syndrome[2], data[1])
    qc.cx(z_syndrome[2], data[4])
    qc.h(z_syndrome[2])

    # Q4-Q7
    qc.h(z_syndrome[3])
    qc.cx(z_syndrome[3], data[4])
    qc.cx(z_syndrome[3], data[7])
    qc.h(z_syndrome[3])

    # Column 2: vertical XX checks
    # Q2-Q5
    qc.h(z_syndrome[4])
    qc.cx(z_syndrome[4], data[2])
    qc.cx(z_syndrome[4], data[5])
    qc.h(z_syndrome[4])

    # Q5-Q8
    qc.h(z_syndrome[5])
    qc.cx(z_syndrome[5], data[5])
    qc.cx(z_syndrome[5], data[8])
    qc.h(z_syndrome[5])

    qc.barrier()

    # ========== MEASUREMENT ==========
    qc.measure(x_syndrome, c_x_syn)
    qc.measure(z_syndrome, c_z_syn)
    qc.measure(data, c_data)

    return qc, c_x_syn, c_z_syn, c_data


def run_bacon_shor_code(input_value=0, apply_error=None, error_qubit=0, error_type='X', shots=1024):
    """
    Run the Bacon-Shor code circuit and return results.

    Args:
        input_value (int): Input bit value (0 or 1)
        apply_error (bool): Whether to apply an error
        error_qubit (int): Which qubit to apply error to (0-8)
        error_type (str): Type of error ('X', 'Z', or 'Y')
        shots (int): Number of times to run the circuit

    Returns:
        dict: Results containing circuit, counts, and registers
    """
    circuit, c_x_syn, c_z_syn, c_data = create_bacon_shor_code(
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
        'x_syndrome': c_x_syn,
        'z_syndrome': c_z_syn,
        'data': c_data
    }


def decode_bacon_shor_syndrome(x_syndrome, z_syndrome):
    """
    Decode the syndrome measurements to identify errors.

    The Bacon-Shor code has a simple decoding procedure:
    - X-syndrome (ZZ checks) identifies the column of X errors
    - Z-syndrome (XX checks) identifies the row of Z errors

    Args:
        x_syndrome (str): X syndrome measurement (6 bits)
        z_syndrome (str): Z syndrome measurement (6 bits)

    Returns:
        tuple: (error_description, error_type) or (None, None) if no error
    """
    if x_syndrome == '000000' and z_syndrome == '000000':
        return None, None

    error_description = []

    # Decode X errors from Z-syndrome (XX checks on columns)
    if z_syndrome != '000000':
        # Identify which column has an error
        col_errors = []
        # Check column 0 (checks 0, 1)
        if z_syndrome[0] == '1' or z_syndrome[1] == '1':
            col_errors.append(0)
        # Check column 1 (checks 2, 3)
        if z_syndrome[2] == '1' or z_syndrome[3] == '1':
            col_errors.append(1)
        # Check column 2 (checks 4, 5)
        if z_syndrome[4] == '1' or z_syndrome[5] == '1':
            col_errors.append(2)

        if col_errors:
            error_description.append(f"Z-error in column(s) {col_errors}")

    # Decode Z errors from X-syndrome (ZZ checks on rows)
    if x_syndrome != '000000':
        # Identify which row has an error
        row_errors = []
        # Check row 0 (checks 0, 1)
        if x_syndrome[0] == '1' or x_syndrome[1] == '1':
            row_errors.append(0)
        # Check row 1 (checks 2, 3)
        if x_syndrome[2] == '1' or x_syndrome[3] == '1':
            row_errors.append(1)
        # Check row 2 (checks 4, 5)
        if x_syndrome[4] == '1' or x_syndrome[5] == '1':
            row_errors.append(2)

        if row_errors:
            error_description.append(f"X-error in row(s) {row_errors}")

    if not error_description:
        return 'Unknown error pattern', 'Unknown'

    # Determine error type
    if x_syndrome != '000000' and z_syndrome != '000000':
        error_type = 'Y or mixed'
    elif x_syndrome != '000000':
        error_type = 'X'
    else:
        error_type = 'Z'

    return '; '.join(error_description), error_type


def analyze_bacon_shor_results(counts, input_value):
    """
    Analyze the results from running the Bacon-Shor code.

    Args:
        counts (dict): Measurement counts from the circuit
        input_value (int): Expected input value (0 or 1)

    Returns:
        float: Success rate as a percentage
    """
    total_shots = sum(counts.values())
    successful = 0

    print(f"\n{'='*80}")
    print(f"Bacon-Shor Code Analysis (Expected input: {input_value})")
    print(f"{'='*80}\n")

    # Track syndrome statistics
    syndrome_stats = {}

    for measurement, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        # Parse measurement: data(9) z_syndrome(6) x_syndrome(6)
        bits = measurement.split()
        if len(bits) == 3:
            data_bits = bits[0]
            z_syndrome_bits = bits[1]
            x_syndrome_bits = bits[2]
        else:
            full_measurement = measurement.replace(' ', '')
            data_bits = full_measurement[0:9]
            z_syndrome_bits = full_measurement[9:15]
            x_syndrome_bits = full_measurement[15:21]

        # Decode syndrome
        error_desc, error_type = decode_bacon_shor_syndrome(x_syndrome_bits, z_syndrome_bits)

        syndrome_key = f"X:{x_syndrome_bits} Z:{z_syndrome_bits}"
        if syndrome_key not in syndrome_stats:
            syndrome_stats[syndrome_key] = {
                'count': 0,
                'error': (error_desc, error_type)
            }
        syndrome_stats[syndrome_key]['count'] += count

        # Count as successful if no error detected
        if x_syndrome_bits == '000000' and z_syndrome_bits == '000000':
            successful += count

    # Print syndrome statistics
    print("Syndrome Measurements:")
    print(f"{'X-Syndrome':<15} {'Z-Syndrome':<15} {'Error Description':<30} {'Count':<8} {'%':<10}")
    print("-" * 80)

    for syndrome_key, data in sorted(syndrome_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        error_desc, error_type = data['error']
        count = data['count']
        percentage = (count / total_shots) * 100

        if error_desc is not None:
            error_str = f"{error_desc} ({error_type})"
        else:
            error_str = "No error"

        print(f"{syndrome_key:<32} {error_str:<30} {count:<8} {percentage:>6.2f}%")

    success_rate = (successful / total_shots) * 100
    print(f"\n{'='*80}")
    print(f"Success Rate (no error detected): {success_rate:.2f}%")
    print(f"Total Shots: {total_shots}")
    print(f"{'='*80}\n")

    return success_rate


def main():
    """Main function to run Bacon-Shor code examples."""
    parser = argparse.ArgumentParser(description='Bacon-Shor [[9,1,3]] Subsystem QEC Code')
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
    result = run_bacon_shor_code(
        input_value=args.input,
        apply_error=args.error,
        error_qubit=args.error_qubit,
        error_type=args.error_type,
        shots=args.shots
    )

    # Draw the circuit
    if not args.no_draw:
        print("\nBacon-Shor Code Circuit:")
        print(result['circuit'].draw(output='text', fold=-1))

    # Analyze results
    analyze_bacon_shor_results(result['counts'], args.input)


if __name__ == '__main__':
    main()
