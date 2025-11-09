import argparse
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

def create_phase_flip_code(input_value=0, apply_error=False, error_qubit=0):
    """
    Create a 3-qubit phase-flip error correction circuit.

    Args:
        input_value: 0 or 1 (the logical qubit to protect)
        apply_error: If True, inject a phase-flip error
        error_qubit: Which physical qubit gets the error (0, 1, or 2)

    Returns:
        qc: The complete circuit
        syndrome_c: Classical register for syndrome measurements
        physical_c: Classical register for physical qubit measurements
    """

    # ===== STEP 1: CREATE QUANTUM AND CLASSICAL REGISTERS =====
    logical_q = QuantumRegister(1, 'logical')          # Input qubit (1 qubit)
    physical_q = QuantumRegister(3, 'physical')        # 3 physical qubits (encoded)
    syndrome_q = QuantumRegister(2, 'syndrome')        # 2 syndrome qubits (detect error)
    syndrome_c = ClassicalRegister(2, 'syndrome_bits') # Store syndrome measurement
    physical_c = ClassicalRegister(3, 'physical_bits') # Store physical qubit measurement

    qc = QuantumCircuit(logical_q, physical_q, syndrome_q, syndrome_c, physical_c)

    # ===== STEP 2: INITIALIZE INPUT =====
    # If input_value is 1, apply X gate to flip logical qubit to |1⟩
    if input_value == 1:
        qc.x(logical_q[0])

    qc.barrier(label='Input')

    # ===== STEP 3: ENCODE (1 qubit → 3 qubits) =====
    # For phase-flip code: encode in phase basis
    # Step A: First encode in computational basis (like bit-flip)
    qc.cx(logical_q[0], physical_q[0])  # CNOT: copy logical to physical[0]
    qc.cx(logical_q[0], physical_q[1])  # CNOT: copy logical to physical[1]
    qc.cx(logical_q[0], physical_q[2])  # CNOT: copy logical to physical[2]

    # Step B: Apply Hadamard to convert to phase basis |+++⟩ or |---⟩
    qc.h(physical_q[0])
    qc.h(physical_q[1])
    qc.h(physical_q[2])

    qc.barrier(label='Encoded')

    # ===== STEP 4: ERROR (OPTIONAL) =====
    # Simulate a real-world phase-flip error on one qubit
    if apply_error:
        qc.z(physical_q[error_qubit])
        qc.barrier(label=f'Error on qubit {error_qubit}')

    # ===== STEP 5: SYNDROME MEASUREMENT (ERROR DETECTION) =====
    # Phase-flip errors are now bit-flips in computational basis
    # Check parity (agreement) between pairs of physical qubits
    # This tells us WHERE the phase error was WITHOUT revealing the data value

    # Hadamards convert phase-basis back to computational basis
    # (where phase errors have become bit-flip errors)
    qc.h(physical_q[0])
    qc.h(physical_q[1])
    qc.h(physical_q[2])

    # Syndrome bit 0: Check if physical[0] == physical[1]
    # CNOT from physical[0] to syndrome[0]: if they differ, syndrome[0] flips
    # CNOT from physical[1] to syndrome[0]: if they differ, syndrome[0] flips again
    qc.cx(physical_q[0], syndrome_q[0])
    qc.cx(physical_q[1], syndrome_q[0])

    # Syndrome bit 1: Check if physical[1] == physical[2]
    qc.cx(physical_q[1], syndrome_q[1])
    qc.cx(physical_q[2], syndrome_q[1])

    qc.barrier(label='Syndrome Measured')

    # ===== STEP 6: MEASURE SYNDROME =====
    # Store the syndrome qubits into classical bits
    # Syndrome tells us: which qubit had the phase error?
    qc.measure(syndrome_q, syndrome_c)

    # ===== STEP 7: MEASURE PHYSICAL QUBITS =====
    # Measure all 3 physical qubits to get the final result
    # We're already in computational basis (after the H gates in step 5)
    # Use majority voting: if 2+ are 1, result is 1; else 0
    qc.measure(physical_q, physical_c)

    return qc, syndrome_c, physical_c


def run_qec_circuit(input_value=0, apply_error=False, error_qubit=0, shots=1024):
    """
    Run the phase-flip error correction circuit on a simulator.

    Args:
        input_value: 0 or 1 (logical qubit)
        apply_error: Whether to inject an error
        error_qubit: Which qubit to error (0, 1, 2)
        shots: Number of times to run the circuit

    Returns:
        Dictionary with circuit, measurement results, and registers
    """
    qc, syndrome_c, physical_c = create_phase_flip_code(input_value, apply_error, error_qubit)

    # Run on simulator
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
    Analyze QEC results using majority voting.

    Args:
        results: Dictionary from run_qec_circuit
        input_value: Expected output (0 or 1)

    Returns:
        Success rate percentage
    """
    counts = results['counts']

    print(f"\nExpected output: {input_value}")
    print("=" * 70)

    success = 0
    failure = 0

    for bitstring, count in sorted(counts.items()):
        # Bitstring format: 'physical_bits syndrome_bits'
        # Example: '101 10' means physical_qubits=101, syndrome=10
        parts = bitstring.split()

        if len(parts) == 2:
            physical_bits = parts[0]  # First 3 bits are physical qubits
        else:
            physical_bits = bitstring[:3]  # Fallback: first 3 chars

        # MAJORITY VOTING: count 0s and 1s
        zeros = physical_bits.count('0')
        ones = physical_bits.count('1')

        # If more 1s than 0s, result is 1; else 0
        result = 1 if ones > zeros else 0

        # Count successes and failures
        if result == input_value:
            success += count
        else:
            failure += count

        percentage = (count / sum(counts.values())) * 100
        print(f"Bitstring: {bitstring:20s} | Count: {count:4d} ({percentage:5.1f}%) | Result: {result}")

    total = success + failure
    success_rate = (success / total) * 100 if total > 0 else 0

    print("=" * 70)
    print(f"Correct results: {success}/{total} ({success_rate:.1f}%)")
    print()

    return success_rate


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Phase-flip error correction code demonstration")
    parser.add_argument(
        "--print-circuit",
        type=lambda x: x.lower() in ('true', '1', 'yes'),
        default=True,
        help="Print quantum circuit diagrams (default: True, use --print-circuit=False to disable)"
    )
    args = parser.parse_args()

    print("\n" + "="*70)
    print("PHASE-FLIP ERROR CORRECTION CODE - DEMONSTRATION")
    print("="*70)

    # TEST 1: Input 0, No Error
    print("\nTEST 1: Input = 0, No Error (Expected: Always correct)")
    print("-" * 70)
    result1 = run_qec_circuit(input_value=0, apply_error=False)
    if args.print_circuit:
        print(result1['circuit'])
    analyze_results(result1, input_value=0)

    # TEST 2: Input 1, No Error
    print("\nTEST 2: Input = 1, No Error (Expected: Always correct)")
    print("-" * 70)
    result2 = run_qec_circuit(input_value=1, apply_error=False)
    if args.print_circuit:
        print(result2['circuit'])
    analyze_results(result2, input_value=1)

    # TEST 3: Input 0, Error on qubit 0
    print("\nTEST 3: Input = 0, Error on qubit 0 (Expected: Should correct and output 0)")
    print("-" * 70)
    result3 = run_qec_circuit(input_value=0, apply_error=True, error_qubit=0)
    if args.print_circuit:
        print(result3['circuit'])
    analyze_results(result3, input_value=0)

    # TEST 4: Input 1, Error on qubit 1
    print("\nTEST 4: Input = 1, Error on qubit 1 (Expected: Should correct and output 1)")
    print("-" * 70)
    result4 = run_qec_circuit(input_value=1, apply_error=True, error_qubit=1)
    if args.print_circuit:
        print(result4['circuit'])
    analyze_results(result4, input_value=1)

    # TEST 5: Input 1, Error on qubit 2
    print("\nTEST 5: Input = 1, Error on qubit 2 (Expected: Should correct and output 1)")
    print("-" * 70)
    result5 = run_qec_circuit(input_value=1, apply_error=True, error_qubit=2)
    if args.print_circuit:
        print(result5['circuit'])
    analyze_results(result5, input_value=1)