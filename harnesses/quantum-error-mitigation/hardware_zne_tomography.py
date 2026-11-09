#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hardware: ZNE com mais escalas e tomografia SPAM multi-base (R1115).

16 jobs: 4 ZNE (escalas 1,3,5,7) + 12 tomografia (4 estados x 3 bases) em q0.
Gates SDD/TDD/simulação antes da submissão. PEC 2q, superfície e DD
pulse-level não são executados.
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
    submit_optimized,
    task_result,
    wait_for_result,
)
from gjq_hardware_opt.benchmarks import load_circuit
from quantum_mitigation import (
    extrapolate,
    fit_spam_tomography,
    fold_circuit,
    spam_tomography_plan,
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
IDEAL_P0 = {
    ("0", "Z"): 1.0, ("0", "X"): 0.5, ("0", "Y"): 0.5,
    ("1", "Z"): 0.0, ("1", "X"): 0.5, ("1", "Y"): 0.5,
    ("+", "Z"): 0.5, ("+", "X"): 1.0, ("+", "Y"): 0.5,
    ("+i", "Z"): 0.5, ("+i", "X"): 0.5, ("+i", "Y"): 1.0,
}


def _json_print(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _run_sdd() -> dict:
    failures = []
    for spec in SPECS:
        text = spec.read_text(encoding="utf-8") if spec.is_file() else ""
        if not spec.is_file() or "critérios de aceitação" not in text.lower():
            failures.append(str(spec))
    return {"ok": not failures, "failures": failures}


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
    }


def _run_simulation_gate(zne: dict, tomography: dict) -> dict:
    failures = []
    ideal_bell = {"00": 0.5, "11": 0.5}
    for name, circuit in zne.items():
        sv = Statevector.from_instruction(
            circuit.remove_final_measurements(inplace=False)
        )
        probs = sv.probabilities_dict()
        # folded circuit should preserve Bell up to phase
        ideal = {k: probs.get(k, 0.0) for k in ideal_bell}
        if abs(sum(ideal.values()) - 1.0) > 1e-9:
            failures.append(name)
    for state in ("0", "1", "+", "+i"):
        for basis in ("X", "Y", "Z"):
            circuit = tomography[f"q0_{state}_{basis}"]
            sv = Statevector.from_instruction(
                circuit.remove_final_measurements(inplace=False)
            )
            p0 = float(sv.probabilities([0])[0])
            expected = IDEAL_P0[(state, basis)]
            if abs(p0 - expected) > 1e-9:
                failures.append(f"q0_{state}_{basis}: {p0} != {expected}")
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="Baihua")
    parser.add_argument("--shots", type=int, default=4096)
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--allow-hardware", action="store_true")
    parser.add_argument("--use-cached-account", action="store_true")
    parser.add_argument("--out", default=str(Path(__file__).resolve().parent / "resultados" / "hardware_zne_tomography"))
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
    item = load_circuit("E05")
    zne_circuits = {
        f"zne_scale_{scale}": fold_circuit(item["circuit"], scale)
        for scale in (1, 3, 5, 7)
    }
    tomography = {
        key: qasm2.loads(qasm)
        for key, qasm in spam_tomography_plan(0).items()
    }
    simulation = _run_simulation_gate(zne_circuits, tomography)
    if not simulation["ok"]:
        _json_print({"status": "blocked", "stage": "simulation", "simulation": simulation})
        return 2

    service, backend = connect_gjq(
        args.backend, use_cached_account=args.use_cached_account
    )
    zne_rows = []
    ideal_bell = {"00": 0.5, "11": 0.5}
    for name, circuit in zne_circuits.items():
        task_id, counts = _submit(service, backend, circuit, args.shots)
        total = sum(counts.values())
        probabilities = {k: v / total for k, v in counts.items()}
        zne_rows.append(
            {
                "scale": int(name.rsplit("_", 1)[-1]),
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
    scales = [r["scale"] for r in zne_rows]
    tvds = [r["tvd_vs_bell"] for r in zne_rows]
    applicability = zne_applicability(scales, tvds)
    zne_payload = {
        "schema_version": 1,
        "shots": args.shots,
        "rows": zne_rows,
        "applicability": applicability,
        "extrapolation_linear": extrapolate(scales, tvds, "linear"),
        "extrapolation_quadratic": extrapolate(scales, tvds, "quadratic"),
        "conclusion": (
            "ZNE aplicável; extrapolação condicional."
            if applicability["applicable"]
            else "Curva não monotônica; extrapolação inválida e sem ganho demonstrado."
        ),
        "limits": "ZNE extrapola TVD; não é fidelidade de estado.",
    }
    (out / "zne.json").write_text(json.dumps(zne_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    tomography_counts = {}
    tomography_tasks = {}
    for key, circuit in tomography.items():
        task_id, counts = _submit(service, backend, circuit, args.shots)
        tomography_counts[key] = counts
        tomography_tasks[key] = task_id
    tomography_fit = fit_spam_tomography(tomography_counts)
    tomography_fit["task_ids"] = tomography_tasks
    tomography_fit["counts"] = tomography_counts
    (out / "tomography.json").write_text(json.dumps(tomography_fit, indent=2, ensure_ascii=False), encoding="utf-8")

    execution = {
        "schema_version": 1,
        "backend": args.backend,
        "shots": args.shots,
        "profile_fingerprint": profile.target_fingerprint,
        "calibration_date": profile.last_update_date,
        "gates": {"sdd": sdd["ok"], "tdd": tdd["ok"], "simulation": simulation["ok"]},
        "submissions": {"zne": len(zne_rows), "tomography": len(tomography), "total": len(zne_rows) + len(tomography)},
        "preregistration": {
            "shots": args.shots,
            "confidence": 0.95,
            "method": "Wilson por probabilidade",
            "note": "n fixado antes da execução; não ajustar após ver os dados.",
        },
        "zne": zne_payload,
        "tomography": tomography_fit,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "hardware_executed": True,
        "network": True,
        "limits": (
            "ZNE e tomografia SPAM em q0; PEC 2q, superfície e DD pulse-level "
            "não foram executados. Não é prova de vantagem."
        ),
    }
    (out / "execucao.json").write_text(json.dumps(execution, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Hardware — ZNE 4 escalas e tomografia SPAM (R1115)",
        "",
        f"Backend **{args.backend}** · {args.shots} shots · 16 jobs · gates SDD/TDD/simulação aprovados.",
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
        f"- Monotônica: **{applicability['monotonic']}**.",
        f"- Linear: {zne_payload['extrapolation_linear']['extrapolated']:.4f}.",
        f"- Quadrática: {zne_payload['extrapolation_quadratic']['extrapolated']:.4f}.",
        f"- Conclusão: {zne_payload['conclusion']}",
        "",
        "## Tomografia SPAM",
        "",
        "| Estado | Fidelidade de preparação | Comprimento de Bloch |",
        "|---|---:|---:|",
        *[
            f"| {state} | {tomography_fit['prep_fidelity'][state]:.4f} | "
            f"{tomography_fit['states'][state]['length']:.4f} |"
            for state in ("0", "1", "+", "+i")
        ],
        "",
        f"- r0 = P(1|prep0): {tomography_fit['readout_p1_given_prep0']}.",
        f"- r1 = P(0|prep1): {tomography_fit['readout_p0_given_prep1']}.",
        "",
        "## Pré-registro",
        "",
        f"- {args.shots} shots · confiança 95% · método Wilson.",
        "- O n foi fixado antes da execução; não foi ajustado após ver os dados.",
        "",
        "## Limites",
        "",
        "- ZNE extrapola TVD; não é fidelidade.",
        "- Tomografia assume rotações de base ideais e ausência de crosstalk.",
        "- PEC 2q, superfície e DD pulse-level não foram executados.",
        "- Uma execução não prova vantagem quântica.",
        "",
    ]
    (out / "RELATORIO.md").write_text("\n".join(lines), encoding="utf-8")
    _json_print(
        {
            "status": "ok",
            "out_dir": str(out),
            "zne": {
                "monotonic": applicability["monotonic"],
                "linear": zne_payload["extrapolation_linear"]["extrapolated"],
                "quadratic": zne_payload["extrapolation_quadratic"]["extrapolated"],
            },
            "tomography": {
                "prep_fidelity": tomography_fit["prep_fidelity"],
                "readout": {
                    "r0": tomography_fit["readout_p1_given_prep0"],
                    "r1": tomography_fit["readout_p0_given_prep1"],
                },
            },
            "submissions": execution["submissions"],
            "hardware_executed": True,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
