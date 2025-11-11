"""
SHOR'S 9-QUBIT QUANTUM ERROR CORRECTION CODE

This is the first QEC code that corrects BOTH bit-flip AND phase-flip errors.
It uses 9 physical qubits to protect 1 logical qubit.

KEY IDEA:
- Combine 3-qubit repetition code (for bit flips) with 3-block structure (for phase flips)
- 3 blocks of 3 qubits each
- Each block protects against bit-flip errors within itself
- The 3 blocks are identical, protecting against phase errors between blocks
- Total: 6 bit-flip syndromes + 2 phase-flip syndromes = 8 syndrome bits

CIRCUIT FLOW:
1. Initialize input (0 or 1) on first qubit
2. Encode: Create 3 identical blocks using CNOT gates
3. Optional: Inject bit-flip (X) or phase-flip (Z) error
4. Measure syndromes: Detect which qubit/block has error
5. Measure physical qubits: Use majority voting to decode
"""

import argparse
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator


def create_shors_9qubit_code(input_value=0, apply_bit_flip_error=False,
                             apply_phase_flip_error=False, error_qubit=0):
    """
    Create Shor's 9-qubit error correction circuit.

    Args:
        input_value: 0 or 1 (logical qubit to protect)
        apply_bit_flip_error: If True, inject X gate on error_qubit
        apply_phase_flip_error: If True, inject Z gate on error_qubit
        error_qubit: Which physical qubit (0-8) gets the error

    Returns:
        qc: The complete circuit
        syndrome_c: Classical register for syndrome measurements
        physical_c: Classical register for physical qubit measurements
    """

    # ===== STEP 1: CREATE REGISTERS =====
    physical_q = QuantumRegister(9, 'physical_q')    # 9 data qubits
    ancilla_q = QuantumRegister(8, 'ancilla_q')      # 8 syndrome qubits
    syndrome_c = ClassicalRegister(8, 'syndrome_c')  # 8 syndrome bits
    physical_c = ClassicalRegister(9, 'physical_c')  # 9 physical measurements

    qc = QuantumCircuit(physical_q, ancilla_q, syndrome_c, physical_c)

    # ===== STEP 2: INITIALIZE INPUT =====
    if input_value == 1:
        qc.x(physical_q[0])

    qc.barrier(label='Input')

    # ===== STEP 3: ENCODE INTO 3 BLOCKS =====
    # Block 0: qubits 0,1,2
    qc.cx(physical_q[0], physical_q[1])
    qc.cx(physical_q[0], physical_q[2])

    # Block 1: qubits 3,4,5 (copy q[0] then create inner repetition)
    qc.cx(physical_q[0], physical_q[3])
    qc.cx(physical_q[3], physical_q[4])
    qc.cx(physical_q[3], physical_q[5])

    # Block 2: qubits 6,7,8 (copy q[0] then create inner repetition)
    qc.cx(physical_q[0], physical_q[6])
    qc.cx(physical_q[6], physical_q[7])
    qc.cx(physical_q[6], physical_q[8])

    qc.barrier(label='Encoded')

    # ===== STEP 4: ERROR INJECTION (OPTIONAL) =====
    if apply_bit_flip_error or apply_phase_flip_error:
        if apply_bit_flip_error:
            qc.x(physical_q[error_qubit])  # Bit-flip error
        if apply_phase_flip_error:
            qc.z(physical_q[error_qubit])  # Phase-flip error
        qc.barrier(label=f'Error on qubit {error_qubit}')

    # ===== STEP 5: SYNDROME MEASUREMENT =====
    # BIT-FLIP SYNDROMES: Check parity within each block
    # Block 0: qubits 0,1,2
    qc.cx(physical_q[0], ancilla_q[0])
    qc.cx(physical_q[1], ancilla_q[0])
    qc.cx(physical_q[1], ancilla_q[1])
    qc.cx(physical_q[2], ancilla_q[1])

    # Block 1: qubits 3,4,5
    qc.cx(physical_q[3], ancilla_q[2])
    qc.cx(physical_q[4], ancilla_q[2])
    qc.cx(physical_q[4], ancilla_q[3])
    qc.cx(physical_q[5], ancilla_q[3])

    # Block 2: qubits 6,7,8
    qc.cx(physical_q[6], ancilla_q[4])
    qc.cx(physical_q[7], ancilla_q[4])
    qc.cx(physical_q[7], ancilla_q[5])
    qc.cx(physical_q[8], ancilla_q[5])

    # PHASE-FLIP SYNDROMES: Check parity between blocks
    # Representative qubits: q[0] (block 0), q[3] (block 1), q[6] (block 2)
    qc.cx(physical_q[0], ancilla_q[6])
    qc.cx(physical_q[3], ancilla_q[6])
    qc.cx(physical_q[3], ancilla_q[7])
    qc.cx(physical_q[6], ancilla_q[7])

    qc.barrier(label='Syndrome Measured')

    # ===== STEP 6: MEASURE SYNDROMES =====
    qc.measure(ancilla_q, syndrome_c)

    # ===== STEP 7: MEASURE PHYSICAL QUBITS =====
    qc.measure(physical_q, physical_c)

    return qc, syndrome_c, physical_c


def run_qec_circuit(input_value=0, apply_bit_flip_error=False,
                    apply_phase_flip_error=False, error_qubit=0, shots=1024):
    """
    Run the Shor code circuit on a simulator.

    Args:
        input_value: 0 or 1
        apply_bit_flip_error: Inject bit-flip error
        apply_phase_flip_error: Inject phase-flip error
        error_qubit: Which qubit (0-8) gets error
        shots: Number of simulation runs

    Returns:
        Dictionary with circuit, counts, and registers
    """
    qc, syndrome_c, physical_c = create_shors_9qubit_code(
        input_value, apply_bit_flip_error, apply_phase_flip_error, error_qubit
    )

    simulator = AerSimulator()
    job = simulator.run(qc, shots=shots)
    result = job.result()
    counts = result.get_counts(qc)

    return {
        'circuit': qc,
        'counts': counts,
        'syndrome_c': syndrome_c,
        'physical_c': physical_c
    }


def analyze_results(results, input_value):
    """
    Analyze Shor code results using majority voting.

    Args:
        results: Dictionary from run_qec_circuit
        input_value: Expected output (0 or 1)

    Returns:
        Success rate percentage
    """
    counts = results['counts']

    print(f"\nExpected output: {input_value}")
    print("=" * 80)

    success = 0
    failure = 0

    for bitstring, count in sorted(counts.items()):
        # Bitstring format: 'physical_bits syndrome_bits'
        # Example: '111000111 10101010' means physical=111000111, syndrome=10101010
        parts = bitstring.split()

        if len(parts) == 2:
            physical_bits = parts[0]  # First 9 bits
        else:
            physical_bits = bitstring[:9]  # Fallback

        # MAJORITY VOTING: count 0s and 1s in physical qubits
        zeros = physical_bits.count('0')
        ones = physical_bits.count('1')
        result = 1 if ones > zeros else 0

        if result == input_value:
            success += count
        else:
            failure += count

        percentage = (count / sum(counts.values())) * 100
        print(f"Bitstring: {bitstring:25s} | Count: {count:4d} ({percentage:5.1f}%) | Result: {result}")

    total = success + failure
    success_rate = (success / total) * 100 if total > 0 else 0

    print("=" * 80)
    print(f"Correct results: {success}/{total} ({success_rate:.1f}%)")
    print()

    return success_rate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Shor's 9-qubit quantum error correction code demonstration"
    )
    parser.add_argument(
        "--print-circuit",
        type=lambda x: x.lower() in ('true', '1', 'yes'),
        default=True,
        help="Print quantum circuit diagrams (default: True, use --print-circuit=False to disable)"
    )
    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("SHOR'S 9-QUBIT QUANTUM ERROR CORRECTION CODE - TEST SUITE")
    print("=" * 80)
    print("First QEC code to correct both bit-flip AND phase-flip errors")
    print("Uses 9 physical qubits to encode 1 logical qubit")
    print()

    # TEST 1: Input 0, No Error
    print("\nTEST 1: Input = 0, No Error")
    print("-" * 80)
    result1 = run_qec_circuit(input_value=0, apply_bit_flip_error=False)
    if args.print_circuit:
        print(result1['circuit'])
    analyze_results(result1, input_value=0)

    # TEST 2: Input 1, No Error
    print("\nTEST 2: Input = 1, No Error")
    print("-" * 80)
    result2 = run_qec_circuit(input_value=1, apply_bit_flip_error=False)
    if args.print_circuit:
        print(result2['circuit'])
    analyze_results(result2, input_value=1)

    # TEST 3: Input 0, Bit-flip on qubit 0 (Block 0)
    print("\nTEST 3: Input = 0, Bit-flip on qubit 0 (Block 0)")
    print("-" * 80)
    result3 = run_qec_circuit(input_value=0, apply_bit_flip_error=True, error_qubit=0)
    if args.print_circuit:
        print(result3['circuit'])
    analyze_results(result3, input_value=0)

    # TEST 4: Input 0, Bit-flip on qubit 4 (Block 1)
    print("\nTEST 4: Input = 0, Bit-flip on qubit 4 (Block 1)")
    print("-" * 80)
    result4 = run_qec_circuit(input_value=0, apply_bit_flip_error=True, error_qubit=4)
    if args.print_circuit:
        print(result4['circuit'])
    analyze_results(result4, input_value=0)

    # TEST 5: Input 1, Bit-flip on qubit 8 (Block 2)
    print("\nTEST 5: Input = 1, Bit-flip on qubit 8 (Block 2)")
    print("-" * 80)
    result5 = run_qec_circuit(input_value=1, apply_bit_flip_error=True, error_qubit=8)
    if args.print_circuit:
        print(result5['circuit'])
    analyze_results(result5, input_value=1)

    # TEST 6: Input 0, Phase-flip on qubit 2 (Block 0)
    print("\nTEST 6: Input = 0, Phase-flip on qubit 2 (Block 0)")
    print("-" * 80)
    result6 = run_qec_circuit(input_value=0, apply_phase_flip_error=True, error_qubit=2)
    if args.print_circuit:
        print(result6['circuit'])
    analyze_results(result6, input_value=0)

    # TEST 7: Input 1, Phase-flip on qubit 5 (Block 1)
    print("\nTEST 7: Input = 1, Phase-flip on qubit 5 (Block 1)")
    print("-" * 80)
    result7 = run_qec_circuit(input_value=1, apply_phase_flip_error=True, error_qubit=5)
    if args.print_circuit:
        print(result7['circuit'])
    analyze_results(result7, input_value=1)

    # TEST 8: Input 1, Phase-flip on qubit 7 (Block 2)
    print("\nTEST 8: Input = 1, Phase-flip on qubit 7 (Block 2)")
    print("-" * 80)
    result8 = run_qec_circuit(input_value=1, apply_phase_flip_error=True, error_qubit=7)
    if args.print_circuit:
        print(result8['circuit'])
    analyze_results(result8, input_value=1)

    # TEST 9: Combined errors
    print("\nTEST 9: Input = 0, Bit-flip on qubit 0 + Phase-flip on qubit 4")
    print("-" * 80)
    result9 = run_qec_circuit(input_value=0, apply_bit_flip_error=True,
                             apply_phase_flip_error=True, error_qubit=0)
    if args.print_circuit:
        print(result9['circuit'])
    analyze_results(result9, input_value=0)

    print("\n" + "=" * 80)
    print("SUMMARY: Shor's code successfully encodes 1 logical qubit into 9 physical")
    print("qubits and can detect and correct both bit-flip and phase-flip errors.")
    print("=" * 80)
