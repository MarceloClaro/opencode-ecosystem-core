#!/usr/bin/env python3
"""Bell no simulador local. Não precisa de API."""
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

sim = AerSimulator(seed_simulator=42)
resultado = sim.run(transpile(qc, sim), shots=1024).result()
counts = resultado.get_counts()
print("counts:", counts)
print("P(00)+P(11):", (counts.get("00", 0) + counts.get("11", 0)) / 1024)
