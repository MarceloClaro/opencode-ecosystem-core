#!/usr/bin/env python3
"""GHZ de 4 qubits no hardware. Exige GJQ_API_KEY."""
import os
from qiskit import QuantumCircuit
from gjq_client import GJQRuntimeService, Sampler, generate_preset_pass_manager

chave = os.environ.get("GJQ_API_KEY", "").strip()
if not chave:
    raise SystemExit("Defina GJQ_API_KEY no ambiente.")

service = GJQRuntimeService(api_key=chave)
backend = service.backend("Guoji08")

qc = QuantumCircuit(4, 4)
qc.h(0)
for alvo in (1, 2, 3):
    qc.cx(0, alvo)
qc.measure([0, 1, 2, 3], [0, 1, 2, 3])

pm = generate_preset_pass_manager(backend=backend, optimization_level=2, seed_transpiler=42)
isa = pm.run(qc)
job = Sampler(backend=backend).run(isa, shots=1024)
counts = {str(k): int(v) for k, v in job.result(timeout=900)["counts"].items()}
print("backend:", backend.name)
print("depth:", isa.depth())
print("task_id:", getattr(job, "_job_id", None))
print("counts:", counts)
print("P(0000)+P(1111):", (counts.get("0000", 0) + counts.get("1111", 0)) / 1024)
