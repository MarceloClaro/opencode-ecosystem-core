#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validação de RC em hardware: baseline vs twirlado (R1123).

Uso:
    hardware_rc_validation.py --set 1 --confirm --allow-hardware --use-cached-account
    hardware_rc_validation.py --set 2 --confirm --allow-hardware --use-cached-account
    hardware_rc_validation.py --analyze

Cada conjunto tem 8 jobs: 4 baseline + 4 twirls, 9.600 shots.
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
    bootstrap_tvd_difference,
    decision,
    ideal_probabilities,
    preregister_ci,
    rc_validation_plan,
    tvd,
    verify_equivalence,
)

BASE = Path(__file__).resolve().parent / "resultados" / "hardware_rc_validation"
TESTS = [
    RAIZ / "tests" / "test_r1119_pauli_frame.py",
    RAIZ / "tests" / "test_r1123_rc_hardware_validation.py",
]
SHOTS = 9600
HALF_WIDTH = 0.01


def _json_print(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _run_tdd() -> dict:
    command = [sys.executable, "-m", "pytest", *[str(p) for p in TESTS], "-q"]
    result = subprocess.run(
        command, cwd=str(RAIZ), capture_output=True, text=True, timeout=1800
    )
    return {"ok": result.returncode == 0, "returncode": result.returncode}


def _simulate(plan: dict) -> dict:
    ideal = plan["ideal"]
    failures = []
    for index, circuit in enumerate(plan["twirled"]):
        clean = circuit.remove_final_measurements(inplace=False)
        probabilities = Statevector.from_instruction(clean).probabilities_dict()
        observed = {
            f"{i:02b}": float(probabilities.get(f"{i:02b}", 0.0))
            for i in range(4)
        }
        if any(abs(observed[key] - ideal[key]) > 1e-9 for key in ideal):
            failures.append(f"twirl {index}: {observed} != {ideal}")
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


def run_set(args) -> int:
    if not args.confirm or not args.allow_hardware:
        _json_print(
            {"status": "blocked", "reason": "exige --confirm e --allow-hardware"}
        )
        return 2
    tdd = _run_tdd()
    if not tdd["ok"]:
        _json_print({"status": "blocked", "stage": "tdd", "tdd": tdd})
        return 2
    seeds = tuple(int(args.set) * 100 + index for index in range(1, 5))
    plan = rc_validation_plan(seeds)
    simulation = _simulate(plan)
    if not simulation["ok"]:
        _json_print(
            {"status": "blocked", "stage": "simulation", "simulation": simulation}
        )
        return 2
    verifications = [
        verify_equivalence(plan["baseline"][0], circuit)
        for circuit in plan["twirled"]
    ]
    if not all(item["equivalent_up_to_phase"] for item in verifications):
        _json_print(
            {"status": "blocked", "stage": "equivalence", "verifications": verifications}
        )
        return 2

    service, backend = connect_gjq(
        args.backend, use_cached_account=args.use_cached_account
    )
    counts = {"baseline": [], "twirled": []}
    task_ids = {"baseline": [], "twirled": []}
    # Intercala baseline/twirlado para reduzir viés de drift.
    for index in range(4):
        task_id, result = _submit(
            service, backend, plan["baseline"][index], args.shots
        )
        counts["baseline"].append(result)
        task_ids["baseline"].append(task_id)
        task_id, result = _submit(
            service, backend, plan["twirled"][index], args.shots
        )
        counts["twirled"].append(result)
        task_ids["twirled"].append(task_id)

    prereg = preregister_ci(p=0.5, half_width=HALF_WIDTH, confidence=0.95)
    payload = {
        "schema_version": 1,
        "backend": args.backend,
        "set": int(args.set),
        "shots": int(args.shots),
        "n_preregistered": {
            "p": 0.5,
            "half_width": HALF_WIDTH,
            "confidence": 0.95,
            "n": prereg["n"],
            "observed_half_width": prereg["observed_half_width"],
            "effect_size": HALF_WIDTH * 2,
        },
        "seeds": plan["seeds"],
        "ideal": plan["ideal"],
        "twirls": plan["twirls"],
        "verifications": verifications,
        "gates": {"tdd": tdd["ok"], "simulation": simulation["ok"]},
        "counts": counts,
        "task_ids": task_ids,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "limits": (
            "Duas pernas no mesmo layout; comparação descritiva de TVD. "
            "Não separa todos os erros e não declara vantagem quântica."
        ),
    }
    out = Path(args.out_dir) if args.out_dir else BASE
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"set{args.set}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    _json_print(
        {
            "status": "ok",
            "path": str(path),
            "set": int(args.set),
            "shots": int(args.shots),
            "jobs": 8,
            "n_preregistered": prereg["n"],
            "baseline_tvd": [
                tvd(value, plan["ideal"]) for value in counts["baseline"]
            ],
            "twirled_tvd": [
                tvd(value, plan["ideal"]) for value in counts["twirled"]
            ],
            "hardware_executed": True,
        }
    )
    return 0


def analyze(out_dir: str | None = None) -> int:
    out = Path(out_dir) if out_dir else BASE
    path1, path2 = out / "set1.json", out / "set2.json"
    if not (path1.exists() and path2.exists()):
        _json_print(
            {"status": "blocked", "reason": "set1.json e set2.json ausentes"}
        )
        return 2
    set1 = json.loads(path1.read_text(encoding="utf-8"))
    set2 = json.loads(path2.read_text(encoding="utf-8"))
    if set1["ideal"] != set2["ideal"]:
        _json_print({"status": "blocked", "reason": "distribuições ideais divergentes"})
        return 2
    ideal = set1["ideal"]
    baseline_counts = set1["counts"]["baseline"] + set2["counts"]["baseline"]
    twirled_counts = set1["counts"]["twirled"] + set2["counts"]["twirled"]
    summary = bootstrap_tvd_difference(
        baseline_counts, twirled_counts, ideal, n_bootstrap=2000, seed=42
    )
    verdict = decision(summary)
    per_set = {}
    for name, payload in (("set1", set1), ("set2", set2)):
        per_set[name] = {
            "baseline_tvd": [
                tvd(value, ideal) for value in payload["counts"]["baseline"]
            ],
            "twirled_tvd": [
                tvd(value, ideal) for value in payload["counts"]["twirled"]
            ],
        }
    payload = {
        "schema_version": 1,
        "shots": set1["shots"],
        "ideal": ideal,
        "per_set": per_set,
        "summary": summary,
        "decision": verdict,
        "limits": (
            "16 jobs totais; 2 conjuntos; não é série temporal. "
            "TVD mede a distribuição, não fidelidade de estado."
        ),
        "hardware_executed": True,
    }
    (out / "rc_validation.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lines = [
        "# Validação RC — baseline vs twirlado",
        "",
        f"Shots por job: {set1['shots']}. Jobs: 16 (2 conjuntos × 8).",
        "",
        "## TVD por conjunto",
        "",
        "| Conjunto | Braço | Média TVD |",
        "|---|---|---:|",
    ]
    for name, item in per_set.items():
        for arm in ("baseline", "twirled"):
            values = item[f"{arm}_tvd"]
            lines.append(
                f"| {name} | {arm} | {sum(values)/len(values):.4f} |"
            )
    lines += [
        "",
        "## Combinado",
        "",
        f"- Baseline: {summary['baseline_mean_tvd']:.4f}",
        f"- Twirlado: {summary['twirled_mean_tvd']:.4f}",
        f"- Δ (twirlado − baseline): {summary['mean_difference']:+.4f} "
        f"[{summary['low']:+.4f}, {summary['high']:+.4f}]",
        f"- Decisão: **{verdict['verdict']}** — {verdict['reason']}.",
        "",
        "## Limites",
        "",
        "- 16 jobs; não é série temporal.",
        "- TVD mede distribuição, não fidelidade de estado.",
        "- O resultado negativo também é reportado.",
        "",
    ]
    (out / "RELATORIO_RC.md").write_text("\n".join(lines), encoding="utf-8")
    _json_print(
        {
            "status": "ok",
            "summary": summary,
            "decision": verdict,
            "report": str(out / "RELATORIO_RC.md"),
        }
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", type=int, choices=[1, 2])
    parser.add_argument("--shots", type=int, default=SHOTS)
    parser.add_argument("--backend", default="Baihua")
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--analyze", action="store_true")
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--allow-hardware", action="store_true")
    parser.add_argument("--use-cached-account", action="store_true")
    args = parser.parse_args(argv)
    if args.analyze:
        return analyze(args.out_dir)
    if args.set is None:
        raise SystemExit("use --set 1, --set 2 ou --analyze")
    return run_set(args)


if __name__ == "__main__":
    raise SystemExit(main())
