#!/usr/bin/env python3
"""Bell no hardware Guoji08. Exige GJQ_API_KEY no ambiente."""
import os
from qiskit import QuantumCircuit
from gjq_client import GJQRuntimeService, Sampler, generate_preset_pass_manager

chave = os.environ.get("GJQ_API_KEY", "").strip()
if not chave:
    raise SystemExit("Defina GJQ_API_KEY no ambiente.")

service = GJQRuntimeService(api_key=chave)
backend = service.backend("Guoji08")  # ou "Baihua"

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

pm = generate_preset_pass_manager(backend=backend, optimization_level=2, seed_transpiler=42)
isa = pm.run(qc)
job = Sampler(backend=backend).run(isa, shots=1024)
counts = {str(k): int(v) for k, v in job.result(timeout=900)["counts"].items()}
print("backend:", backend.name)
print("task_id:", getattr(job, "_job_id", None))
print("counts:", counts)
print("fidelidade proxy:", (counts.get("00", 0) + counts.get("11", 0)) / 1024)
