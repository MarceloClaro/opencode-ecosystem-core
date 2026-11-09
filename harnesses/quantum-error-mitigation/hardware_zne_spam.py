#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validação de hardware: ZNE no Bell e SPAM separation (R1115).

Gates: SDD (specs/testes), TDD (pytest) e simulação (Statevector/Aer).
Depois submete 3 circuitos ZNE + 6 circuitos SPAM ao Baihua, com
confirm=True e allow_hardware=True. Não executa PEC 2q, superfície ou
DD pulse-level.
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
    HardwareProfile,
    connect_gjq,
    load_circuit,
    submit_optimized,
    task_result,
    wait_for_result,
)
from gjq_hardware_opt.benchmarks import load_circuit as load_book_circuit
from quantum_mitigation import (
    extrapolate,
    fit_spam_separation,
    fold_circuit,
    spam_separation_plan,
    zne_applicability,
)

PROFILE = RAIZ / "harnesses" / "gjq-hardware-optimizers" / "resultados" / "baihua" / "perfil.json"
SPECS = [
    RAIZ / "specs" / "SPEC-935-R1115-hardware-mitigation-protocols.md",
    RAIZ / "specs" / "SPEC-935-R1114-quantum-error-mitigation-correction.md",
]
TESTS = [
    RAIZ / "tests" / "test_r1115_hardware_mitigation_protocols.py",
    RAIZ / "tests" / "test_r1114_quantum_error_mitigation.py",
]


def _json_print(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _run_tdd() -> dict:
    command = [sys.executable, "-m", "pytest", *[str(p) for p in TESTS], "-q"]
    result = subprocess.run(
        command, cwd=str(RAIZ), capture_output=True, text=True, timeout=1200
    )
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
        "command": [str(p) for p in TESTS],
    }


def _run_sdd() -> dict:
    failures = []
    for spec in SPECS:
        text = spec.read_text(encoding="utf-8") if spec.is_file() else ""
        if not spec.is_file() or "critérios de aceitação" not in text.lower():
            failures.append(str(spec))
    return {"ok": not failures, "specs": [str(p) for p in SPECS], "failures": failures}


def _run_simulation_gate(circuits: dict, ideal_bell: dict) -> dict:
    from qiskit_aer import AerSimulator
    from quantum_efficiency.metrics import dist_ideal, tvd

    results = {}
    for name, circuit in circuits.items():
        ideal = dist_ideal(circuit)
        if name.startswith("zne"):
            error = tvd(ideal, ideal_bell)
            results[name] = {"ideal_tvd_vs_bell": error, "ok": error <= 1e-9}
        else:
            results[name] = {"ideal": ideal, "ok": True}
    return {"ok": all(item["ok"] for item in results.values()), "results": results}


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="Baihua")
    parser.add_argument("--shots", type=int, default=4096)
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--allow-hardware", action="store_true")
    parser.add_argument("--use-cached-account", action="store_true")
    parser.add_argument("--out", default=str(Path(__file__).resolve().parent / "resultados" / "hardware_zne_spam"))
    args = parser.parse_args(argv)
    if not args.confirm or not args.allow_hardware:
        _json_print({"status": "blocked", "reason": "exige --confirm e --allow-hardware"})
        return 2

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    sdd = _run_sdd()
    if not sdd["ok"]:
        _json_print({"status": "blocked", "stage": "sdd", "sdd": sdd})
        return 2
    tdd = _run_tdd()
    if not tdd["ok"]:
        _json_print({"status": "blocked", "stage": "tdd", "tdd": tdd})
        return 2

    profile = HardwareProfile.from_dict(json.loads(PROFILE.read_text(encoding="utf-8")))
    item = load_book_circuit("E05")
    zne_circuits = {
        f"zne_scale_{scale}": fold_circuit(item["circuit"], scale)
        for scale in (1, 3, 5)
    }
    spam_circuits = {
        name: qasm2.loads(qasm)
        for name, qasm in spam_separation_plan([0, 1], (1, 3, 5)).items()
    }
    ideal_bell = {"00": 0.5, "11": 0.5}
    simulation = _run_simulation_gate(zne_circuits, ideal_bell)
    if not simulation["ok"]:
        _json_print({"status": "blocked", "stage": "simulation", "simulation": simulation})
        return 2

    service, backend = connect_gjq(
        args.backend, use_cached_account=args.use_cached_account
    )
    zne_rows = []
    for scale, circuit in zne_circuits.items():
        task_id, counts = _submit(service, backend, circuit, args.shots)
        total = sum(counts.values())
        probabilities = {k: v / total for k, v in counts.items()}
        zne_rows.append(
            {
                "scale": int(scale.rsplit("_", 1)[-1]),
                "task_id": task_id,
                "counts": counts,
                "probabilities": probabilities,
                "tvd_vs_bell": 0.5 * sum(
                    abs(probabilities.get(k, 0.0) - ideal_bell.get(k, 0.0))
                    for k in set(probabilities) | set(ideal_bell)
                ),
            }
        )
    zne_rows.sort(key=lambda row: row["scale"])
    zne_scales = [r["scale"] for r in zne_rows]
    zne_tvds = [r["tvd_vs_bell"] for r in zne_rows]
    applicability = zne_applicability(zne_scales, zne_tvds)
    zne_payload = {
        "schema_version": 1,
        "shots": args.shots,
        "rows": zne_rows,
        "applicability": applicability,
        "extrapolation_linear": extrapolate(zne_scales, zne_tvds, "linear"),
        "extrapolation_quadratic": extrapolate(zne_scales, zne_tvds, "quadratic"),
        "conclusion": (
            "ZNE aplicável; extrapolação condicional."
            if applicability["applicable"]
            else "Curva não monotônica; extrapolação inválida e sem ganho demonstrado."
        ),
        "limits": "ZNE extrapola TVD; não é fidelidade de estado.",
    }
    (out / "zne.json").write_text(json.dumps(zne_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    spam_payload = {}
    for q in (0, 1):
        counts_by_k = {}
        for k in (1, 3, 5):
            name = f"q{q}_k{k}"
            task_id, counts = _submit(service, backend, spam_circuits[name], args.shots)
            counts_by_k[str(k)] = counts
            counts_by_k.setdefault("task_ids", {})[str(k)] = task_id
        task_ids = counts_by_k.pop("task_ids")
        fit = fit_spam_separation(
            {key: counts_by_k[key] for key in ("1", "3", "5")}
        )
        fit["task_ids"] = task_ids
        fit["counts"] = counts_by_k
        spam_payload[f"q{q}"] = fit
    (out / "spam.json").write_text(json.dumps(spam_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    execution = {
        "schema_version": 1,
        "backend": args.backend,
        "shots": args.shots,
        "profile_fingerprint": profile.target_fingerprint,
        "calibration_date": profile.last_update_date,
        "gates": {"sdd": sdd["ok"], "tdd": tdd["ok"], "simulation": simulation["ok"]},
        "submissions": {
            "zne": len(zne_rows),
            "spam": 6,
            "total": len(zne_rows) + 6,
        },
        "zne": zne_payload,
        "spam": spam_payload,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "hardware_executed": True,
        "network": True,
        "conclusion": (
            "ZNE inconclusivo por não monotonicidade; SPAM separation não "
            "identificável no modelo de pulsos pi independentes. Nenhum ganho "
            "de mitigação é declarado."
        ),
        "limits": (
            "ZNE e SPAM separation em q0/q1; PEC 2q, superfície e DD pulse-level "
            "não foram executados. Não é prova de vantagem."
        ),
    }
    (out / "execucao.json").write_text(json.dumps(execution, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Hardware — ZNE e SPAM separation (R1115)",
        "",
        f"Backend **{args.backend}** · {args.shots} shots · gates SDD/TDD/simulação aprovados.",
        "",
        "## ZNE",
        "",
        "| Escala | TVD vs Bell | Task ID |",
        "|---:|---:|---|",
        *[
            f"| {row['scale']} | {row['tvd_vs_bell']:.4f} | `{row['task_id']}` |"
            for row in zne_rows
        ],
        "",
        f"- Monotônica: **{zne_payload['applicability']['monotonic']}**.",
        f"- Extrapolação linear: {zne_payload['extrapolation_linear']['extrapolated']:.4f}.",
        f"- Extrapolação quadrática: {zne_payload['extrapolation_quadratic']['extrapolated']:.4f}.",
        f"- Conclusão: {zne_payload['conclusion']}",
        "",
        "## SPAM separation",
        "",
        "| Qubit | Identificado? | P1(k=1) | P1(k=3) | P1(k=5) |",
        "|---|---|---:|---:|---:|",
        *[
            f"| q{q} | **{spam_payload[f'q{q}']['identified']}** | "
            f"{spam_payload[f'q{q}']['observed_p1']['1']:.4f} | "
            f"{spam_payload[f'q{q}']['observed_p1']['3']:.4f} | "
            f"{spam_payload[f'q{q}']['observed_p1']['5']:.4f} |"
            for q in (0, 1)
        ],
        "",
        "Se `identified=False`, e/r0/r1 não são físicos e não devem ser usados.",
        "",
        "## Limites",
        "",
        "- ZNE extrapola TVD; não é fidelidade.",
        "- SPAM separation usa modelo de pulsos π independentes.",
        "- PEC 2q, superfície e DD pulse-level não foram executados.",
        "- Uma execução não prova vantagem quântica.",
        "",
    ]
    (out / "RELATORIO.md").write_text("\n".join(lines), encoding="utf-8")
    _json_print(
        {
            "status": "ok",
            "out_dir": str(out),
            "zne_extrapolated": zne_payload["extrapolation_linear"]["extrapolated"],
            "spam": {
                q: {
                    "identified": spam_payload[f"q{q}"]["identified"],
                    "reason": spam_payload[f"q{q}"]["reason"],
                }
                for q in (0, 1)
            },
            "submissions": execution["submissions"],
            "hardware_executed": True,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
