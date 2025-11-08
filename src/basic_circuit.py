# Simple quantum circuit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

# Function to create a basic quantum circuit
def create_basic_circuit():
    qc = QuantumCircuit(1, 1) # 1 qubit, 1 classical bit
    qc.measure(0, 0) # Measure qubit 0 into classical bit 0
    return qc

# Function to create a quantum circuit with superposition
def super_position_circuit():
    qc = QuantumCircuit(1, 1)
    qc.h(0) # Apply Hadamard gate to put qubit in superposition
    qc.measure(0, 0)
    return qc

# Run the circuit
def run_circuit(circuit, shots=1024): # Run the circuit 1024 times
    simulator = AerSimulator()
    job = simulator.run(circuit, shots=shots)
    result = job.result() # Collect results
    counts = result.get_counts(circuit) # Store results as dictionary
    return counts

# Make the print result looks better
def print_results(name, circuit, counts):
    print(f"\n{'='*40}")
    print(f"Circuit: {name}")
    print(f"\n{'='*40}")
    print(circuit) # Draw the circuit
    total = sum(counts.values()) # adds up all the counts

    for results, count in counts.items():
        percentage = (count / total) * 100
        
        print(f"Result: {results}, Count: {count:4d}, Percentage: {percentage:5.1f}%")

if __name__ == "__main__":
    # Create Basic Circuit and Superposition Circuit
    circuit_1 = create_basic_circuit() # Create the circuit
    circuit_2 = super_position_circuit() # Create the circuit

    results_1 = run_circuit(circuit_1) # Run it 1024 times
    results_2 = run_circuit(circuit_2) # Run it 1024 times

    print_results("Basic Circuit", circuit_1, results_1) # Print the results
    print_results("Superposition Circuit", circuit_2, results_2) # Print the results