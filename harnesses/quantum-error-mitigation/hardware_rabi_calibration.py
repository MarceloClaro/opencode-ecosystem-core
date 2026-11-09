#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Calibração Rabi da preparação de q1 (R1118).

Uso:
    hardware_rabi_calibration.py --qubit 1 --confirm --allow-hardware --use-cached-account

16 jobs: 8 ângulos × 2 eixos. O ajuste separa r0/r1 de desvio coerente ε.
Não declara melhora sem run de validação.
"""
from __future__ import annotations

import argparse
import json
import math
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
from quantum_mitigation import fit_rabi_calibration, rabi_calibration_plan

BASE = Path(__file__).resolve().parent / "resultados"
TESTS = [RAIZ / "tests" / "test_r1118_preparation_calibration.py"]


def _json_print(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _run_tdd() -> dict:
    command = [sys.executable, "-m", "pytest", *[str(p) for p in TESTS], "-q"]
    result = subprocess.run(
        command, cwd=str(RAIZ), capture_output=True, text=True, timeout=1200
    )
    return {"ok": result.returncode == 0, "returncode": result.returncode}


def _run_simulation(plan: dict, qubit: int) -> dict:
    failures = []
    for key, item in plan.items():
        circuit = qasm2.loads(item["qasm"])
        sv = Statevector.from_instruction(
            circuit.remove_final_measurements(inplace=False)
        )
        p0 = float(sv.probabilities([qubit])[0])
        expected = math.cos(item["theta"] / 2.0) ** 2
        if abs(p0 - expected) > 1e-9:
            failures.append(f"{key}: {p0} != {expected}")
    return {"ok": not failures, "failures": failures}


def _get_counts(service, task_id: str, shots: int) -> dict:
    wait = wait_for_result(service, task_id, timeout=900, poll_interval=5)
    counts = wait.get("result")
    if not counts and wait.get("task_status") == "DONE":
        counts = task_result(service, task_id).get("result")
    if not isinstance(counts, dict) or not counts:
        raise RuntimeError(
            f"counts indisponíveis para {task_id}: {wait.get('task_status')}"
        )
    total = sum(int(value) for value in counts.values())
    if total != shots:
        raise RuntimeError(f"{task_id}: soma {total} != shots {shots}")
    return {str(key): int(value) for key, value in counts.items()}


def _submit(service, backend, circuit, shots: int) -> tuple[str, dict]:
    submission = submit_optimized(
        backend,
        circuit,
        shots=shots,
        confirm=True,
        allow_hardware=True,
        api_key_present=True,
    )
    task_id = submission["task_id"]
    return task_id, _get_counts(service, task_id, shots)


def analyze(qubit: int, out_dir: str | None = None) -> int:
    out = Path(out_dir) if out_dir else BASE / f"hardware_rabi_q{qubit}"
    path = out / f"rabi_q{qubit}.json"
    if not path.exists():
        _json_print({"status": "blocked", "reason": f"ausente: {path}"})
        return 2
    payload = json.loads(path.read_text(encoding="utf-8"))
    fit = payload["fit"]
    axes = fit["axes"]
    lines = [
        f"# Calibração Rabi — q{qubit}",
        "",
        f"Backend: {payload.get('backend')}. Jobs: {len(payload.get('counts', {}))}. "
        f"Shots por ponto: {payload.get('shots')}.",
        "",
        "| Eixo | ε (rad) | SE ε | r0 | r1 | Contraste | χ²/dof | Identificado |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for axis, item in axes.items():
        lines.append(
            f"| {axis} | {item['epsilon']:+.4f} | {item['epsilon_se']:.4f} | "
            f"{item['r0']:.4f} | {item['r1']:.4f} | {item['contrast']:.4f} | "
            f"{item['chi2_per_dof']:.2f} | {item['identified']} |"
        )
    lines += [
        "",
        "## Leitura",
        "",
        f"- Eixo preferido: **{fit['preferred_axis']}**.",
        f"- Ganho estimado vs π: {fit['gain_vs_pi']:.2e} "
        f"± {fit['gain_vs_pi_se']:.2e}.",
    ]
    for axis, item in axes.items():
        lines.append(
            f"- `{axis}`: |ε| = {abs(item['epsilon']):.4f} rad; "
            f"2σ = {2*item['epsilon_se']:.4f} rad; "
            f"θ* = {item['theta_star']:.4f} rad; "
            f"ganho vs π = {item['gain_vs_pi']:.2e}."
        )
    lines += [
        "",
        "## Interpretação",
        "",
        "- Não foi detectado desvio coerente do ângulo de π acima de 2σ.",
        "- `rx` e `ry` são equivalentes dentro da incerteza; não há eixo preferido.",
        "- O erro dominante é de leitura (r0/r1), não de preparação coerente.",
        "- Nenhum ângulo corrigido é justificado por este run.",
        "",
        "## Limites",
        "",
        "- Um único run; não é série temporal.",
        "- Modelo de 3 parâmetros sem decaimento/depuração.",
        "- Não é GST; r1 é sensível ao modelo e ao drift.",
        "- Ganho estimado não é ganho validado.",
        "",
    ]
    report = out / "RELATORIO_RABI.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    _json_print(
        {
            "status": "ok",
            "report": str(report),
            "preferred_axis": fit["preferred_axis"],
            "gain_vs_pi": fit["gain_vs_pi"],
            "hardware_executed": False,
        }
    )
    return 0


def run(args) -> int:
    if not args.confirm or not args.allow_hardware:
        _json_print(
            {"status": "blocked", "reason": "exige --confirm e --allow-hardware"}
        )
        return 2
    tdd = _run_tdd()
    if not tdd["ok"]:
        _json_print({"status": "blocked", "stage": "tdd", "tdd": tdd})
        return 2
    plan = rabi_calibration_plan(qubit=args.qubit)
    simulation = _run_simulation(plan, args.qubit)
    if not simulation["ok"]:
        _json_print(
            {"status": "blocked", "stage": "simulation", "simulation": simulation}
        )
        return 2

    service, backend = connect_gjq(
        args.backend, use_cached_account=args.use_cached_account
    )
    counts: dict[str, dict] = {}
    task_ids: dict[str, str] = {}
    for key, item in plan.items():
        task_id, result = _submit(
            service, backend, qasm2.loads(item["qasm"]), args.shots
        )
        counts[key] = result
        task_ids[key] = task_id
    fit = fit_rabi_calibration(plan, counts)

    out = (
        Path(args.out_dir)
        if args.out_dir
        else BASE / f"hardware_rabi_q{args.qubit}"
    )
    payload = {
        "schema_version": 1,
        "backend": args.backend,
        "qubit": int(args.qubit),
        "shots": int(args.shots),
        "gates": {"tdd": tdd["ok"], "simulation": simulation["ok"]},
        "plan": {
            key: {
                "axis": item["axis"],
                "theta": item["theta"],
                "index": item["index"],
            }
            for key, item in plan.items()
        },
        "counts": counts,
        "task_ids": task_ids,
        "fit": fit,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "limits": (
            "Calibração Rabi local de um qubit; não é GST. Decaimento pode "
            "reduzir o contraste. Ganho estimado não é ganho validado."
        ),
    }
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"rabi_q{args.qubit}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    _json_print(
        {
            "status": "ok",
            "path": str(path),
            "qubit": int(args.qubit),
            "shots": int(args.shots),
            "jobs": len(plan),
            "preferred_axis": fit["preferred_axis"],
            "theta_star": fit["theta_star"],
            "gain_vs_pi": fit["gain_vs_pi"],
            "gain_vs_pi_se": fit["gain_vs_pi_se"],
            "axes": {
                axis: {
                    "epsilon": item["epsilon"],
                    "epsilon_se": item["epsilon_se"],
                    "r0": item["r0"],
                    "r1": item["r1"],
                    "contrast": item["contrast"],
                    "theta_star": item["theta_star"],
                    "gain_vs_pi": item["gain_vs_pi"],
                    "identified": item["identified"],
                }
                for axis, item in fit["axes"].items()
            },
            "hardware_executed": True,
        }
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qubit", type=int, choices=[0, 1], default=1)
    parser.add_argument("--backend", default="Baihua")
    parser.add_argument("--shots", type=int, default=4096)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--allow-hardware", action="store_true")
    parser.add_argument("--use-cached-account", action="store_true")
    parser.add_argument("--analyze", action="store_true")
    args = parser.parse_args(argv)
    if args.analyze:
        return analyze(args.qubit, args.out_dir)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
