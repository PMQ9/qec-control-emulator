"""
Quantum Error Models

This module provides various quantum error models that can be applied to
quantum circuits for testing quantum error correction codes.

Error models included:
1. Depolarizing channel - Random Pauli errors (X, Y, Z)
2. Bit-flip channel - Only X errors
3. Phase-flip channel - Only Z errors
4. Amplitude damping - Energy loss (|1> to |0>)
5. Phase damping - Dephasing without energy loss
6. Combined error models - Multiple error types

These error models can be used with any of the QEC codes in this repository.
"""

from qiskit import QuantumCircuit
from qiskit_aer.noise import (
    NoiseModel,
    depolarizing_error,
    pauli_error,
    amplitude_damping_error,
    phase_damping_error,
    thermal_relaxation_error
)
import numpy as np


class QuantumErrorModels:
    """Class containing various quantum error models."""

    @staticmethod
    def depolarizing_channel(p):
        """
        Create a depolarizing error channel.

        With probability p, applies one of X, Y, Z with equal probability.
        With probability (1-p), applies identity (no error).

        Args:
            p (float): Error probability (0 <= p <= 1)

        Returns:
            NoiseModel: Qiskit noise model for depolarizing channel
        """
        error = depolarizing_error(p, 1)
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, ['id', 'x', 'y', 'z', 'h', 'cx'])
        return noise_model

    @staticmethod
    def bit_flip_channel(p):
        """
        Create a bit-flip error channel.

        With probability p, applies X (bit-flip).
        With probability (1-p), applies identity (no error).

        Args:
            p (float): Bit-flip probability (0 <= p <= 1)

        Returns:
            NoiseModel: Qiskit noise model for bit-flip channel
        """
        error = pauli_error([('X', p), ('I', 1 - p)])
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, ['id', 'x', 'y', 'z', 'h', 'cx'])
        return noise_model

    @staticmethod
    def phase_flip_channel(p):
        """
        Create a phase-flip error channel.

        With probability p, applies Z (phase-flip).
        With probability (1-p), applies identity (no error).

        Args:
            p (float): Phase-flip probability (0 <= p <= 1)

        Returns:
            NoiseModel: Qiskit noise model for phase-flip channel
        """
        error = pauli_error([('Z', p), ('I', 1 - p)])
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, ['id', 'x', 'y', 'z', 'h', 'cx'])
        return noise_model

    @staticmethod
    def bit_phase_flip_channel(p):
        """
        Create a bit-phase-flip error channel.

        With probability p, applies Y (both bit and phase flip).
        With probability (1-p), applies identity (no error).

        Args:
            p (float): Bit-phase-flip probability (0 <= p <= 1)

        Returns:
            NoiseModel: Qiskit noise model for bit-phase-flip channel
        """
        error = pauli_error([('Y', p), ('I', 1 - p)])
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, ['id', 'x', 'y', 'z', 'h', 'cx'])
        return noise_model

    @staticmethod
    def amplitude_damping_channel(gamma):
        """
        Create an amplitude damping error channel.

        Models energy dissipation: |1> to |0> with probability gamma.
        This represents T1 (energy relaxation) processes.

        Args:
            gamma (float): Damping probability (0 <= gamma <= 1)

        Returns:
            NoiseModel: Qiskit noise model for amplitude damping
        """
        error = amplitude_damping_error(gamma)
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, ['id', 'x', 'y', 'z', 'h', 'cx'])
        return noise_model

    @staticmethod
    def phase_damping_channel(gamma):
        """
        Create a phase damping error channel.

        Models phase information loss without energy loss.
        This represents T2 (dephasing) processes.

        Args:
            gamma (float): Damping probability (0 <= gamma <= 1)

        Returns:
            NoiseModel: Qiskit noise model for phase damping
        """
        error = phase_damping_error(gamma)
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, ['id', 'x', 'y', 'z', 'h', 'cx'])
        return noise_model

    @staticmethod
    def thermal_relaxation_channel(t1, t2, gate_time):
        """
        Create a thermal relaxation error channel.

        Models realistic quantum hardware with T1 (energy relaxation) and
        T2 (dephasing) times.

        Args:
            t1 (float): T1 relaxation time (microseconds)
            t2 (float): T2 dephasing time (microseconds), must be <= 2*T1
            gate_time (float): Gate operation time (microseconds)

        Returns:
            NoiseModel: Qiskit noise model for thermal relaxation
        """
        error = thermal_relaxation_error(t1, t2, gate_time)
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, ['id', 'x', 'y', 'z', 'h'])
        return noise_model

    @staticmethod
    def custom_pauli_channel(px, py, pz):
        """
        Create a custom Pauli error channel with specified probabilities.

        Args:
            px (float): Probability of X error
            py (float): Probability of Y error
            pz (float): Probability of Z error

        Returns:
            NoiseModel: Qiskit noise model for custom Pauli errors

        Note:
            px + py + pz should be <= 1. The remaining probability is for identity.
        """
        if px + py + pz > 1:
            raise ValueError("Sum of error probabilities must be <= 1")

        pi = 1 - (px + py + pz)  # Probability of no error
        error = pauli_error([('X', px), ('Y', py), ('Z', pz), ('I', pi)])
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(error, ['id', 'x', 'y', 'z', 'h', 'cx'])
        return noise_model


def apply_random_errors(circuit, num_qubits, error_rate=0.01, error_types=['X', 'Y', 'Z']):
    """
    Apply random errors to a quantum circuit.

    This is a utility function to inject random errors for testing QEC codes.

    Args:
        circuit (QuantumCircuit): The quantum circuit to modify
        num_qubits (int): Number of qubits in the circuit
        error_rate (float): Probability of error per qubit (0 <= error_rate <= 1)
        error_types (list): List of error types to apply ['X', 'Y', 'Z']

    Returns:
        QuantumCircuit: Modified circuit with random errors
        list: List of (qubit_index, error_type) tuples showing which errors were applied
    """
    errors_applied = []

    for qubit in range(num_qubits):
        if np.random.random() < error_rate:
            error_type = np.random.choice(error_types)
            errors_applied.append((qubit, error_type))

            if error_type == 'X':
                circuit.x(qubit)
            elif error_type == 'Y':
                circuit.y(qubit)
            elif error_type == 'Z':
                circuit.z(qubit)

    return circuit, errors_applied


def create_noisy_qec_test(qec_code_function, noise_model, input_value=0, shots=1024):
    """
    Test a QEC code with a specified noise model.

    Args:
        qec_code_function (callable): Function that creates the QEC circuit
        noise_model (NoiseModel): Qiskit noise model to apply
        input_value: Input value for the QEC code
        shots (int): Number of measurement shots

    Returns:
        dict: Results from running the noisy circuit
    """
    from qiskit_aer import AerSimulator

    # Create the QEC circuit
    circuit_data = qec_code_function(input_value)

    # Extract circuit (different QEC codes may return different formats)
    if isinstance(circuit_data, tuple):
        circuit = circuit_data[0]
    elif isinstance(circuit_data, dict):
        circuit = circuit_data['circuit']
    else:
        circuit = circuit_data

    # Run with noise model
    simulator = AerSimulator(noise_model=noise_model)
    job = simulator.run(circuit, shots=shots)
    result = job.result()

    return {
        'counts': result.get_counts(),
        'circuit': circuit,
        'noise_model': noise_model
    }


# Example usage and demonstrations
if __name__ == '__main__':
    print("Quantum Error Models")
    print("=" * 60)
    print()

    models = QuantumErrorModels()

    # 1. Depolarizing Channel
    print("1. Depolarizing Channel (p=0.1)")
    print("   Applies X, Y, or Z with equal probability")
    depol_model = models.depolarizing_channel(0.1)
    print(f"   Created: {depol_model}")
    print()

    # 2. Bit-Flip Channel
    print("2. Bit-Flip Channel (p=0.05)")
    print("   Applies X (bit-flip) errors")
    bitflip_model = models.bit_flip_channel(0.05)
    print(f"   Created: {bitflip_model}")
    print()

    # 3. Phase-Flip Channel
    print("3. Phase-Flip Channel (p=0.05)")
    print("   Applies Z (phase-flip) errors")
    phaseflip_model = models.phase_flip_channel(0.05)
    print(f"   Created: {phaseflip_model}")
    print()

    # 4. Amplitude Damping
    print("4. Amplitude Damping Channel (�=0.1)")
    print("   Models energy dissipation (T1 process)")
    amp_damp_model = models.amplitude_damping_channel(0.1)
    print(f"   Created: {amp_damp_model}")
    print()

    # 5. Phase Damping
    print("5. Phase Damping Channel (�=0.1)")
    print("   Models dephasing (T2 process)")
    phase_damp_model = models.phase_damping_channel(0.1)
    print(f"   Created: {phase_damp_model}")
    print()

    # 6. Thermal Relaxation
    print("6. Thermal Relaxation Channel")
    print("   T1=50�s, T2=70�s, gate_time=0.1�s")
    print("   Models realistic quantum hardware")
    thermal_model = models.thermal_relaxation_channel(50, 70, 0.1)
    print(f"   Created: {thermal_model}")
    print()

    # 7. Custom Pauli Channel
    print("7. Custom Pauli Channel")
    print("   pX=0.05, pY=0.02, pZ=0.03")
    custom_model = models.custom_pauli_channel(0.05, 0.02, 0.03)
    print(f"   Created: {custom_model}")
    print()

    # 8. Random Error Application
    print("8. Random Error Application")
    print("   Example: Apply random errors to a 5-qubit circuit")
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

    qr = QuantumRegister(5, 'q')
    cr = ClassicalRegister(5, 'c')
    test_circuit = QuantumCircuit(qr, cr)

    test_circuit, errors = apply_random_errors(test_circuit, 5, error_rate=0.3)
    print(f"   Errors applied: {errors}")
    print()

    print("=" * 60)
    print("All error models created successfully!")
    print()
    print("To use these models with QEC codes:")
    print("  1. Import the QuantumErrorModels class")
    print("  2. Create a noise model (e.g., models.depolarizing_channel(0.1))")
    print("  3. Run your QEC circuit with the noise model")
    print("  4. Or use create_noisy_qec_test() for automated testing")
