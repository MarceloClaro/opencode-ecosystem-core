"""CB inspirado em CZ: paridade, decaimentos condicionais e gate de posto.

R1125 corrige o protótipo P00/log(p). NÃO é implementação experimental completa
do protocolo SPAM-robusto de Erhard et al. Portas locais ideais, ruído Pauli
estacionário e SPAM multiplicativo são hipóteses, não resultados de hardware.
Comprimentos pares identificam 9 combinações, NÃO as 15 taxas individuais.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import numbers
import re
from collections.abc import Mapping

import numpy as np
from qiskit import QuantumCircuit, qasm2
from qiskit.quantum_info import DensityMatrix, Pauli
from scipy.optimize import least_squares
from scipy.stats import chi2

from .randomized_compiling import pauli_frame_pass

PAULIS_2Q = ["".join(p) for p in itertools.product("IXYZ", repeat=2) if p != ("I", "I")]
DEPTHS = (0, 2, 4, 8, 16)
_XZ = {"I": (0, 0), "X": (1, 0), "Y": (1, 1), "Z": (0, 1)}
_CHAR = {v: k for k, v in _XZ.items()}
LIMITS = (
    "Piloto offline condicionado a canal Pauli estacionário e SPAM multiplicativo. "
    "Twirls finitos não comprovam tailoring; portas locais e compilação física "
    "não auditadas. IC de shots não cobre drift, seeds ou erro de modelo. "
    "CZ par tem posto 9 para 15 taxas; PEC 2q permanece bloqueado."
)


def _integer(value, name: str, minimum: int = 0, maximum: int = 1000000) -> int:
    if isinstance(value, bool) or not isinstance(value, numbers.Integral):
        raise ValueError(f"{name}: inteiro exigido")
    value = int(value)
    if not minimum <= value <= maximum:
        raise ValueError(f"{name}: fora de [{minimum}, {maximum}]")
    return value


def _pauli(pauli: str) -> str:
    if not isinstance(pauli, str) or pauli not in PAULIS_2Q:
        raise ValueError("Pauli não identidade de 2 qubits exigido, sem fase")
    return pauli


def _depth(depth: int) -> int:
    depth = _integer(depth, "depth", maximum=256)
    if depth % 2:
        raise ValueError("CZ exige depth par; recuperação ímpar não é silenciosa")
    return depth


def _count_key(key) -> str:
    if not isinstance(key, str):
        raise ValueError("rótulo de counts deve ser string binária/hexadecimal")
    text = key.strip().lower()
    if re.fullmatch(r"0x[0-9a-f]+", text):
        value = int(text, 16)
    else:
        if text.startswith("0b"):
            text = text[2:]
        if not re.fullmatch(r"[01]{1,2}", text):
            raise ValueError("counts fora da largura c1c0")
        value = int(text, 2)
    if value > 3:
        raise ValueError("counts fora da largura c1c0")
    return f"{value:02b}"


def pauli_expectation(counts: dict, pauli: str) -> dict:
    """Paridade após mudança de base; ignora bits de fatores identidade."""
    _pauli(pauli)
    if not isinstance(counts, Mapping) or not counts:
        raise ValueError("counts vazios/inválidos")
    plus = minus = 0
    for key, value in counts.items():
        bits = _count_key(key)
        value = _integer(value, "count", maximum=10**12)
        parity = sum(int(bit) for bit, char in zip(bits, pauli) if char != "I") % 2
        if parity:
            minus += value
        else:
            plus += value
    shots = plus + minus
    if not shots:
        raise ValueError("counts sem shots")
    expectation = (plus - minus) / shots
    return {"expectation": expectation, "plus": plus, "minus": minus, "shots": shots,
            "standard_error_plugin": math.sqrt(max(0., 1-expectation**2)/shots)}


def cycle_benchmarking_circuit(pauli: str, depth: int, *, seed: int,
                               qubits: tuple[int, int] = (0, 1)) -> QuantumCircuit:
    """Piloto de paridade +1, sem inversão adicional. Qubits são lógicos."""
    _pauli(pauli)
    depth = _depth(depth)
    seed = _integer(seed, "seed", maximum=2**32-1)
    if tuple(qubits) != (0, 1):
        raise ValueError("apenas layout lógico (0,1); embedding físico deve ser auditado")
    circuit = QuantumCircuit(2, 2)
    for qubit, char in enumerate(reversed(pauli)):
        if char in "XY":
            circuit.h(qubit)
        if char == "Y":
            circuit.s(qubit)
    circuit.barrier()
    rng = np.random.default_rng(seed)
    for _ in range(depth):
        cycle = QuantumCircuit(2)
        cycle.cz(0, 1)
        circuit.compose(pauli_frame_pass(cycle, rng=rng)["circuit"], inplace=True)
        circuit.barrier()
    for qubit, char in enumerate(reversed(pauli)):
        if char == "Y":
            circuit.sdg(qubit)
        if char in "XY":
            circuit.h(qubit)
    circuit.measure([0, 1], [0, 1])
    return circuit


def cz_conjugate_label(pauli: str) -> str:
    """Conjugação simplética sem fase; o sinal cancela em profundidade par."""
    _pauli(pauli)
    (x1, z1), (x0, z0) = [_XZ[c] for c in pauli]
    return _CHAR[x1, z1 ^ x0] + _CHAR[x0, z0 ^ x1]


def _anticommutes(p: str, q: str) -> int:
    return sum(_XZ[a][0]*_XZ[b][1] + _XZ[a][1]*_XZ[b][0]
               for a, b in zip(p, q)) % 2


def decay_design_matrix(design: str) -> np.ndarray:
    """y=-log(f_eff)/2=D gamma. Sem pseudoinversa de desenho deficiente."""
    matrix = np.array([[_anticommutes(p, q) for q in PAULIS_2Q] for p in PAULIS_2Q], float)
    if design == "full_pauli_spectrum":
        return matrix
    if design == "cz_even":
        permuted = [PAULIS_2Q.index(cz_conjugate_label(p)) for p in PAULIS_2Q]
        return (matrix + matrix[permuted])/2
    raise ValueError("design deve ser full_pauli_spectrum ou cz_even")


def identifiability_audit(design: str = "cz_even") -> dict:
    matrix = decay_design_matrix(design)
    rank = int(np.linalg.matrix_rank(matrix))
    orbits = sorted({tuple(sorted({p, cz_conjugate_label(p)})) for p in PAULIS_2Q})
    return {"design": design, "rank": rank, "n_unknowns": 15, "nullity": 15-rank,
            "identifiable": rank == 15, "orbits": [list(o) for o in orbits] if design == "cz_even" else [[p] for p in PAULIS_2Q],
            "equation": "-log(f_eff)/2 = D @ gamma", "matrix": matrix.tolist()}


def pauli_lindblad_rates(fidelities: dict, *, design: str, eigenvalue_samples=None) -> dict:
    """Inversão de espectro COMPLETO, não de probabilidades nem órbitas CZ.

    IC pontual por parâmetro: transformação de amostras conjuntas na ordem
    PAULIS_2Q, sem descartar taxas negativas e sem impor positividade ao IC.
    Origem/validade experimental do espectro não é certificada aqui.
    """
    audit = identifiability_audit(design)
    out = {"status": "blocked_nonidentifiable", "rates": None, "uncertainty": None,
           "audit": audit, "pec_hardware_allowed": False}
    if set(fidelities) != set(PAULIS_2Q):
        raise ValueError("exatamente 15 fidelidades ordenadas por rótulo exigidas")
    f = np.array([fidelities[p] for p in PAULIS_2Q], float)
    if not np.all(np.isfinite(f)) or np.any(f <= 0) or np.any(f > 1):
        raise ValueError("espectro deve ser finito em (0,1]")
    if not audit["identifiable"]:
        return out
    matrix = decay_design_matrix(design)
    candidates = np.linalg.solve(matrix, -np.log(f)/2)
    out["unconstrained_rates"] = dict(zip(PAULIS_2Q, candidates.tolist()))
    out["nonnegative_exactly"] = bool(np.all(candidates >= 0))
    out["nonnegative_with_tolerance"] = bool(np.all(candidates >= -1e-10))
    out["design_condition_number"] = float(np.linalg.cond(matrix))
    out["spectrum_provenance_verified"] = False
    # Canal Pauli finito: probabilidades não são taxas do gerador.
    labels = ["II", *PAULIS_2Q]
    probs = {q: float((1+sum((1-2*_anticommutes(p, q))*v for p, v in zip(PAULIS_2Q, f)))/16)
             for q in labels}
    out["channel_probabilities"] = probs
    if min(probs.values()) < -1e-10:
        out["status"] = "blocked_non_cp"
    elif min(candidates) < -1e-10:
        out["status"] = "blocked_non_lindblad"
    else:
        out["status"] = "model_compatible"
        out["rates"] = out["unconstrained_rates"].copy()
    out["numerical_tolerance"] = 1e-10
    if eigenvalue_samples is not None:
        samples = np.asarray(eigenvalue_samples, float)
        if samples.ndim != 2 or samples.shape[1] != 15 or len(samples) < 100:
            raise ValueError("IC exige >=100 amostras conjuntas de 15 eigenvalues")
        if not np.all(np.isfinite(samples)) or np.any(samples <= 0):
            raise ValueError("amostras não positivas/não finitas não podem ser descartadas")
        gs = np.linalg.solve(matrix, (-np.log(samples)/2).T).T
        cis = np.quantile(gs, [.025, .975], axis=0).T
        out["uncertainty"] = {
            "ci95": dict(zip(PAULIS_2Q, cis.tolist())), "n_samples": len(samples),
            "negative_rate_draw_fraction": float(np.mean(np.any(gs < -1e-10, axis=1))),
            "scope": "pontual, condicional às amostras fornecidas; não simultâneo; sem projeção",
        }
    return out


def _decay_fit(depths, observed, shots):
    # Estabilização de variância de Jeffreys para evitar peso infinito nos extremos.
    plus = shots*(observed+1)/2
    p = (plus+.5)/(shots+1)
    sigma = np.sqrt(4*p*(1-p)/shots)

    def residual(x):
        return (x[0]*np.exp(-x[1]*depths)-observed)/sigma

    def jacobian(x):
        decay = np.exp(-x[1]*depths)
        return np.column_stack([decay, -depths*x[0]*decay])/sigma[:, None]

    return least_squares(residual, [.9, .02], jac=jacobian,
                         bounds=([0., 0.], [1., 10.]), max_nfev=500,
                         ftol=1e-10, xtol=1e-10, gtol=1e-10)


def fit_pauli_decay(points: list[tuple[int, float, int]], *, n_bootstrap: int = 200,
                    seed: int = 1125) -> dict:
    """Ajusta E=A*f_eff**m, não log(P00). IC paramétrico de shots fixos.

    Não remove offsets arbitrários de SPAM, nem identifica taxas Lindblad.
    Diagnóstico chi2 é aproximação; não mede validade do canal real.
    """
    _integer(n_bootstrap, "n_bootstrap", minimum=100, maximum=10000)
    _integer(seed, "seed", maximum=2**32-1)
    if len(points) < 4:
        raise ValueError("pelo menos quatro profundidades distintas exigidas")
    ds = [_depth(p[0]) for p in points]
    ns = [_integer(p[2], "shots", minimum=1, maximum=10**12) for p in points]
    if len(set(ds)) < 4 or 0 not in ds:
        raise ValueError("quatro profundidades distintas incluindo m=0 exigidas")
    observed = np.array([p[1] for p in points], float)
    if not np.all(np.isfinite(observed)) or np.any(np.abs(observed) > 1):
        raise ValueError("expectativas finitas em [-1,1] exigidas")
    depths, shots = np.array(ds, float), np.array(ns, np.int64)
    result = _decay_fit(depths, observed, shots)
    amplitude, rate = result.x
    predicted = amplitude*np.exp(-rate*depths)
    statistic, dof = float(np.sum(result.fun**2)), len(points)-2
    p_value = float(chi2.sf(statistic, dof))
    jac_rank = int(np.linalg.matrix_rank(result.jac))
    reasons = []
    if not result.success or jac_rank != 2 or np.linalg.cond(result.jac) > 1e8:
        reasons.append("ajuste sem informação/condicionamento suficiente")
    if amplitude < max(.05, 3/math.sqrt(int(np.sum(shots[depths == 0])))):
        reasons.append("contraste insuficiente")
    if p_value < .01:
        reasons.append("inadequação ao modelo de paridade sem offset (p<0,01)")
    output = {"status": "blocked_fit" if reasons else "conditional_fit", "reasons": reasons,
              "effective_eigenvalue": float(math.exp(-rate)), "amplitude": float(amplitude),
              "chi2": statistic, "dof": dof, "chi2_p_approx": p_value,
              "n_points": len(points), "ci95": None, "n_bootstrap": n_bootstrap, "seed": seed,
              "inference_validated": False,
              "goodness_of_fit_gate": "heuristic_chi2_not_calibrated",
              "ci_scope": "pointwise_conditional_shots_not_simultaneous",
              "boundary_estimate": bool(amplitude > 1-1e-6 or rate < 1e-6),
              "limits": "IC paramétrico condicional de shots; não cobre drift/seeds/SPAM fora do modelo. Limites de parâmetro podem prejudicar cobertura."}
    if reasons:
        return output
    rng = np.random.default_rng(seed)
    estimates = []
    for _ in range(n_bootstrap):
        sampled = 2*rng.binomial(shots, (1+predicted)/2)/shots-1
        boot = _decay_fit(depths, sampled, shots)
        if boot.success and np.all(np.isfinite(boot.x)):
            estimates.append(float(math.exp(-boot.x[1])))
    output["bootstrap_successes"] = len(estimates)
    if len(estimates) != n_bootstrap:
        output["status"] = "blocked_bootstrap"
        output["reasons"] = ["réplicas falharam; não descartar seletivamente"]
    else:
        output["ci95"] = np.quantile(estimates, [.025, .975]).tolist()
    return output


def _hash(payload) -> str:
    text = json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


def build_manifest(*, shots: int = 4096, seed: int = 1125) -> dict:
    """Manifesto congelável; proposta corrigida, NÃO autorização de execução."""
    shots = _integer(shots, "shots", minimum=1, maximum=100000)
    seed = _integer(seed, "seed", maximum=2**32-1)
    rng = np.random.default_rng(seed)
    plan = {}
    for set_index in (1, 2):
        for pauli in PAULIS_2Q:
            for depth in DEPTHS:
                job_seed = int(rng.integers(0, 2**32))
                circuit = cycle_benchmarking_circuit(pauli, depth, seed=job_seed)
                qasm = qasm2.dumps(circuit)
                key = f"cb_{pauli}_{depth}_s{set_index}"
                plan[key] = {"pauli": pauli, "depth": depth, "set": set_index,
                             "seed": job_seed, "shots": shots, "qasm": qasm,
                             "qasm_sha256": hashlib.sha256(qasm.encode()).hexdigest()}
    # Ordem aleatorizada por conjunto; não confundir com dois tempos independentes.
    order = []
    for set_index in (1, 2):
        keys = [k for k, v in plan.items() if v["set"] == set_index]
        order.extend(rng.permutation(keys).tolist())
    out = {"schema_version": 2, "protocol": "r1125-cz-even-conditional-pilot",
           "settings": {"shots": shots, "seed": seed, "depths": list(DEPTHS), "sets": 2,
                        "logical_qubits": [0, 1]},
           "budget": {"jobs": len(plan), "shots_per_job": shots, "total_shots": len(plan)*shots},
           "plan": plan, "order": order, "identifiability": identifiability_audit(),
           "hardware_submission_allowed": False,
           "blockers": ["posto 9/15", "SPAM e randomizações não validados", "compilação e layout físico não auditados"],
           "limits": LIMITS}
    out["manifest_sha256"] = _hash(out)
    return out


def validate_manifest(manifest: dict) -> None:
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 2:
        raise ValueError("manifesto v2 exigido; plano legado não identifica taxas")
    try:
        expected = build_manifest(shots=manifest["settings"]["shots"], seed=manifest["settings"]["seed"])
    except (KeyError, TypeError) as exc:
        raise ValueError("manifesto incompleto") from exc
    if manifest != expected:
        raise ValueError("manifesto/hash/QASM alterado ou protocolo divergente")


def simulate_pauli_probabilities(circuit: QuantumCircuit, rates: dict) -> dict:
    """Matriz densidade; exp(L) após CADA CZ. Demais operações são ideais.

    Cada termo exp(gamma*(Q.rho.Q-rho))=(1-p)*rho+p*Q.rho.Q,
    p=(1-exp(-2*gamma))/2. Esses superoperadores Pauli comutam.
    """
    if circuit.num_qubits != 2 or set(rates) != set(PAULIS_2Q):
        raise ValueError("simulador exige circuito 2q e 15 taxas explícitas")
    gs = np.asarray([rates[p] for p in PAULIS_2Q], float)
    if not np.all(np.isfinite(gs)) or np.any(gs < 0):
        raise ValueError("gerador exige taxas finitas não negativas")
    rho = DensityMatrix.from_label("00")
    operators = [(Pauli(p).to_matrix(), -math.expm1(-2*g)/2) for p, g in zip(PAULIS_2Q, gs) if g > 0]
    clean = circuit.remove_final_measurements(inplace=False)
    for instruction in clean.data:
        op = instruction.operation
        if op.name == "barrier":
            continue
        if op.name in ("measure", "reset"):
            raise ValueError("medição intermediária/reset fora do simulador")
        qargs = [clean.find_bit(q).index for q in instruction.qubits]
        rho = rho.evolve(op, qargs=qargs)
        if op.name == "cz":
            data = rho.data
            for matrix, probability in operators:
                data = (1-probability)*data + probability*(matrix @ data @ matrix.conj().T)
            rho = DensityMatrix(data)
    values = np.real(np.diag(rho.data))
    if np.min(values) < -1e-10 or not np.isclose(values.sum(), 1):
        raise ValueError("estado numérico inválido")
    values = np.maximum(values, 0)
    values /= values.sum()  # apenas arredondamento da matriz densidade
    return dict(zip(("00", "01", "10", "11"), values.tolist()))


def simulate_manifest(manifest: dict, rates: dict, *, seed: int = 1126) -> dict:
    validate_manifest(manifest)
    _integer(seed, "seed", maximum=2**32-1)
    rng = np.random.default_rng(seed)
    jobs = {}
    for key in manifest["order"]:
        item = manifest["plan"][key]
        circuit = cycle_benchmarking_circuit(item["pauli"], item["depth"], seed=item["seed"])
        probs = simulate_pauli_probabilities(circuit, rates)
        counts = rng.multinomial(item["shots"], list(probs.values()))
        jobs[key] = {"counts": dict(zip(probs, counts.tolist())), "qasm_sha256": item["qasm_sha256"]}
    return {"schema_version": 2, "manifest_sha256": manifest["manifest_sha256"],
            "origin": {"kind": "simulation", "model": "density_matrix_pauli_after_cz", "seed": seed,
                       "injected_rates": rates}, "jobs": jobs, "hardware_executed": False}


def analyze_cycle_benchmarking(manifest: dict, data: dict, *, n_bootstrap: int = 200,
                               seed: int = 1125) -> dict:
    """Análise local estrita. Counts importados não certificam execução real."""
    validate_manifest(manifest)
    if data.get("schema_version") != 2 or data.get("manifest_sha256") != manifest["manifest_sha256"]:
        raise ValueError("dados v2 vinculados ao manifesto exigidos")
    kind = data.get("origin", {}).get("kind")
    if kind not in ("simulation", "imported_hardware_counts"):
        raise ValueError("origem explícita exigida")
    jobs = data.get("jobs", {})
    if set(jobs) != set(manifest["plan"]):
        raise ValueError("jobs ausentes ou extras; não analisar aquisição parcial")
    grouped = {p: [] for p in PAULIS_2Q}
    task_ids = []
    per_set = {"1": {}, "2": {}}
    for key, item in manifest["plan"].items():
        job = jobs[key]
        if job.get("qasm_sha256") != item["qasm_sha256"]:
            raise ValueError("QASM não vinculado ao job")
        measured = pauli_expectation(job.get("counts"), item["pauli"])
        if measured["shots"] != item["shots"]:
            raise ValueError("shots divergentes do manifesto")
        if kind == "imported_hardware_counts":
            task_id = job.get("task_id")
            if not isinstance(task_id, str) or not task_id.strip():
                raise ValueError("task_id obrigatório para counts declarados de hardware")
            task_ids.append(task_id)
        point = (item["depth"], measured["expectation"], measured["shots"])
        grouped[item["pauli"]].append(point)
        per_set[str(item["set"])].setdefault(item["pauli"], []).append(list(point))
    if len(set(task_ids)) != len(task_ids):
        raise ValueError("task_id duplicado; não tratar o mesmo job como replicação")
    fits = {p: fit_pauli_decay(grouped[p], n_bootstrap=n_bootstrap, seed=seed+i)
            for i, p in enumerate(PAULIS_2Q)}
    return {"schema_version": 2, "status": "partial_characterization",
            "manifest_sha256": manifest["manifest_sha256"], "data_sha256": _hash(data),
            "data_origin_declared": kind, "per_set_parity": per_set, "fits": fits,
            "conditional_fits": sum(v["status"] == "conditional_fit" for v in fits.values()),
            "identifiability": identifiability_audit(), "rates": None, "rates_measured": False,
            "pec_hardware_allowed": False, "hardware_executed": False, "limits": LIMITS}
