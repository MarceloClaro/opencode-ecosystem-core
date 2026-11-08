#!/usr/bin/env python3
"""CHSH no hardware. Exige GJQ_API_KEY."""
import os
import numpy as np
from qiskit import QuantumCircuit
from gjq_client import GJQRuntimeService, Sampler, generate_preset_pass_manager

chave = os.environ.get("GJQ_API_KEY", "").strip()
if not chave:
    raise SystemExit("Defina GJQ_API_KEY no ambiente.")

service = GJQRuntimeService(api_key=chave)
backend = service.backend("Guoji08")
pm = generate_preset_pass_manager(backend=backend, optimization_level=2, seed_transpiler=42)

E = {}
for nome, a1, angulo in [("E00", 0, -np.pi/4), ("E01", 0, np.pi/4),
                         ("E10", 1, -np.pi/4), ("E11", 1, np.pi/4)]:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    if a1:
        qc.h(0)
    qc.ry(float(angulo), 1)
    qc.measure([0, 1], [0, 1])
    isa = pm.run(qc)
    job = Sampler(backend=backend).run(isa, shots=1024)
    c = {str(k): int(v) for k, v in job.result(timeout=900)["counts"].items()}
    total = sum(c.values())
    E[nome] = (c.get("00", 0) + c.get("11", 0) - c.get("01", 0) - c.get("10", 0)) / total
    print(nome, c, "task:", getattr(job, "_job_id", None))

S = E["E00"] + E["E01"] + E["E10"] - E["E11"]
print("E:", {k: round(v, 4) for k, v in E.items()})
print("S:", round(S, 4), "(clássico ≤ 2; ideal 2,828)")
