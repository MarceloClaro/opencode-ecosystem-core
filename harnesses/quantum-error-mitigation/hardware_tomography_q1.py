#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tomografia SPAM de q1 em dois conjuntos + bootstrap (R1115).

Uso:
    hardware_tomography_q1.py --set 1 --confirm --allow-hardware --use-cached-account
    hardware_tomography_q1.py --set 2 --confirm --allow-hardware --use-cached-account
    hardware_tomography_q1.py --analyze

Cada conjunto tem 12 jobs (4 estados x 3 bases). A análise combina os dois
conjuntos de q1 e compara com q0 já medido.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from qiskit import qasm2
from qiskit.quantum_info import Statevector

from gjq_hardware_opt import (
    connect_gjq,
    submit_optimized,
    task_result,
    wait_for_result,
)
from quantum_mitigation import (
    bootstrap_spam_tomography,
    fit_spam_tomography,
    spam_tomography_plan,
)

OUT = Path(__file__).resolve().parent / "resultados" / "hardware_tomography_q1"
Q0 = Path(__file__).resolve().parent / "resultados" / "hardware_zne_tomography" / "tomography.json"
SPECS = [
    RAIZ / "specs" / "SPEC-935-R1115-hardware-mitigation-protocols.md",
    RAIZ / "specs" / "SPEC-935-R1114-quantum-error-mitigation-correction.md",
]
TESTS = [
    RAIZ / "tests" / "test_r1115_hardware_mitigation_protocols.py",
    RAIZ / "tests" / "test_r1114_quantum_error_mitigation.py",
]
IDEAL_P0 = {
    ("0", "Z"): 1.0, ("0", "X"): 0.5, ("0", "Y"): 0.5,
    ("1", "Z"): 0.0, ("1", "X"): 0.5, ("1", "Y"): 0.5,
    ("+", "Z"): 0.5, ("+", "X"): 1.0, ("+", "Y"): 0.5,
    ("+i", "Z"): 0.5, ("+i", "X"): 0.5, ("+i", "Y"): 1.0,
}


def _json_print(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _run_tdd() -> dict:
    command = [sys.executable, "-m", "pytest", *[str(p) for p in TESTS], "-q"]
    result = subprocess.run(
        command, cwd=str(RAIZ), capture_output=True, text=True, timeout=1200
    )
    return {"ok": result.returncode == 0, "returncode": result.returncode}


def _run_simulation(circuits: dict) -> dict:
    failures = []
    for state in ("0", "1", "+", "+i"):
        for basis in ("X", "Y", "Z"):
            circuit = circuits[f"q1_{state}_{basis}"]
            sv = Statevector.from_instruction(
                circuit.remove_final_measurements(inplace=False)
            )
            # qubit 1 é o medido; a probabilidade de 0 em q1
            p0 = float(sv.probabilities([1])[0])
            expected = IDEAL_P0[(state, basis)]
            if abs(p0 - expected) > 1e-9:
                failures.append(f"q1_{state}_{basis}: {p0} != {expected}")
    return {"ok": not failures, "failures": failures}


def _get_counts(service, task_id: str, shots: int) -> dict:
    wait = wait_for_result(service, task_id, timeout=900, poll_interval=5)
    counts = wait.get("result")
    if not counts and wait.get("task_status") == "DONE":
        counts = task_result(service, task_id).get("result")
    if not isinstance(counts, dict) or not counts:
        raise RuntimeError(f"counts indisponíveis para {task_id}: {wait.get('task_status')}")
    total = sum(int(v) for v in counts.values())
    if total != shots:
        raise RuntimeError(f"{task_id}: soma {total} != shots {shots}")
    return {str(k): int(v) for k, v in counts.items()}


def _submit(service, backend, circuit, shots: int) -> tuple[str, dict]:
    submission = submit_optimized(
        backend, circuit, shots=shots, confirm=True,
        allow_hardware=True, api_key_present=True,
    )
    task_id = submission["task_id"]
    return task_id, _get_counts(service, task_id, shots)


def run_set(args) -> int:
    if not args.confirm or not args.allow_hardware:
        _json_print({"status": "blocked", "reason": "exige --confirm e --allow-hardware"})
        return 2
    tdd = _run_tdd()
    if not tdd["ok"]:
        _json_print({"status": "blocked", "stage": "tdd", "tdd": tdd})
        return 2
    circuits = {
        key: qasm2.loads(qasm)
        for key, qasm in spam_tomography_plan(1).items()
    }
    simulation = _run_simulation(circuits)
    if not simulation["ok"]:
        _json_print({"status": "blocked", "stage": "simulation", "simulation": simulation})
        return 2
    service, backend = connect_gjq(
        args.backend, use_cached_account=args.use_cached_account
    )
    counts = {}
    task_ids = {}
    for key, circuit in circuits.items():
        task_id, result = _submit(service, backend, circuit, args.shots)
        counts[key] = result
        task_ids[key] = task_id
    fit = fit_spam_tomography(counts, prefix="q1")
    payload = {
        "schema_version": 1,
        "backend": args.backend,
        "set": int(args.set),
        "shots": args.shots,
        "qubit": 1,
        "gates": {"tdd": tdd["ok"], "simulation": simulation["ok"]},
        "task_ids": task_ids,
        "counts": counts,
        "fit": fit,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "limits": "Tomografia de q1; não é GST completa.",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"set{args.set}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    _json_print(
        {
            "status": "ok",
            "set": int(args.set),
            "shots": args.shots,
            "path": str(path),
            "prep_fidelity": fit["prep_fidelity"],
            "readout": {
                "r0": fit["readout_p1_given_prep0"],
                "r1": fit["readout_p0_given_prep1"],
            },
            "hardware_executed": True,
        }
    )
    return 0


def _combine(set1: dict, set2: dict) -> dict:
    combined = {}
    for key, counts in set1["counts"].items():
        other = set2["counts"][key]
        combined[key] = {
            "0": int(counts.get("0", 0)) + int(other.get("0", 0)),
            "1": int(counts.get("1", 0)) + int(other.get("1", 0)),
        }
    return combined


def analyze() -> int:
    path1, path2 = OUT / "set1.json", OUT / "set2.json"
    if not (path1.exists() and path2.exists()):
        _json_print({"status": "blocked", "reason": "set1/set2 ausentes"})
        return 2
    set1 = json.loads(path1.read_text(encoding="utf-8"))
    set2 = json.loads(path2.read_text(encoding="utf-8"))
    combined = _combine(set1, set2)
    fit_combined = fit_spam_tomography(combined, prefix="q1")
    bootstrap_q1 = bootstrap_spam_tomography(
        combined, prefix="q1", n_bootstrap=2000, seed=42
    )
    q0_payload = json.loads(Q0.read_text(encoding="utf-8")) if Q0.exists() else None
    q0_fit = None
    q0_bootstrap = None
    if q0_payload:
        q0_fit = q0_payload.get("fit", q0_payload)
        q0_bootstrap = bootstrap_spam_tomography(
            q0_payload["counts"], prefix="q0", n_bootstrap=2000, seed=42
        )
    comparison = {
        "schema_version": 1,
        "q0": {
            "fit": q0_fit,
            "bootstrap": q0_bootstrap,
        },
        "q1": {
            "fit_set1": set1["fit"],
            "fit_set2": set2["fit"],
            "fit_combined": fit_combined,
            "bootstrap_combined": bootstrap_q1,
        },
        "limits": (
            "q0 tem um conjunto e q1 tem dois; a comparação é descritiva, não "
            "um teste de hipótese. Bootstrap multinomial não captura drift."
        ),
    }
    (OUT / "comparison.json").write_text(
        json.dumps(comparison, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lines = [
        "# Tomografia SPAM — q0 vs q1",
        "",
        r"| Qubit | Fidelidade \|0> | \|1> | \|+> | \|+i> | r0 | r1 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for qubit, fit in (("q0", q0_fit), ("q1", fit_combined)):
        if fit is None:
            continue
        lines.append(
            f"| {qubit} | {fit['prep_fidelity']['0']:.4f} | "
            f"{fit['prep_fidelity']['1']:.4f} | {fit['prep_fidelity']['+']:.4f} | "
            f"{fit['prep_fidelity']['+i']:.4f} | "
            f"{fit['readout_p1_given_prep0']:.4f} | "
            f"{fit['readout_p0_given_prep1']:.4f} |"
        )
    lines += [
        "",
        "## Bootstrap q1 (2 conjuntos)",
        "",
        "| Estado | Média | IC 95% |",
        "|---|---:|---:|",
    ]
    for state in ("0", "1", "+", "+i"):
        item = bootstrap_q1["prep_fidelity"][state]
        lines.append(
            f"| {state} | {item['mean']:.4f} | [{item['low']:.4f}, {item['high']:.4f}] |"
        )
    lines += [
        "",
        f"r0: {bootstrap_q1['readout']['r0']['mean']:.4f} "
        f"[{bootstrap_q1['readout']['r0']['low']:.4f}, {bootstrap_q1['readout']['r0']['high']:.4f}].",
        f"r1: {bootstrap_q1['readout']['r1']['mean']:.4f} "
        f"[{bootstrap_q1['readout']['r1']['low']:.4f}, {bootstrap_q1['readout']['r1']['high']:.4f}].",
        "",
        "## Limites",
        "",
        "- q0 tem um conjunto; q1 tem dois; a comparação é descritiva.",
        "- Bootstrap não captura drift entre execuções.",
        "- A tomografia assume rotações de base ideais.",
        "",
    ]
    (OUT / "RELATORIO_Q1.md").write_text("\n".join(lines), encoding="utf-8")
    _json_print(
        {
            "status": "ok",
            "comparison": str(OUT / "comparison.json"),
            "report": str(OUT / "RELATORIO_Q1.md"),
            "q0": q0_fit,
            "q1": fit_combined,
            "q1_bootstrap": bootstrap_q1,
        }
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", type=int, choices=[1, 2])
    parser.add_argument("--analyze", action="store_true")
    parser.add_argument("--backend", default="Baihua")
    parser.add_argument("--shots", type=int, default=4096)
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--allow-hardware", action="store_true")
    parser.add_argument("--use-cached-account", action="store_true")
    args = parser.parse_args(argv)
    if args.analyze:
        return analyze()
    if args.set is None:
        raise SystemExit("use --set 1, --set 2 ou --analyze")
    return run_set(args)


if __name__ == "__main__":
    raise SystemExit(main())
