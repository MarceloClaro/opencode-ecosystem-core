#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tomografia SPAM de q0/q1 em dois conjuntos + bootstrap (R1115/R1117).

Uso:
    hardware_tomography_q1.py --qubit 1 --set 1 --confirm --allow-hardware --use-cached-account
    hardware_tomography_q1.py --qubit 1 --set 2 --confirm --allow-hardware --use-cached-account
    hardware_tomography_q1.py --qubit 0 --set 2 --out-dir .../hardware_tomography_q0
    hardware_tomography_q1.py --analyze

Cada conjunto tem 12 jobs (4 estados x 3 bases). A análise combina os dois
conjuntos de cada qubit, roda bootstrap e produz comparação descritiva q0/q1.
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

BASE = Path(__file__).resolve().parent / "resultados"
OUT = BASE / "hardware_tomography_q1"
Q0_DIR = BASE / "hardware_tomography_q0"
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


def _run_simulation(circuits: dict, prefix: str = "q1") -> dict:
    failures = []
    for state in ("0", "1", "+", "+i"):
        for basis in ("X", "Y", "Z"):
            circuit = circuits[f"{prefix}_{state}_{basis}"]
            sv = Statevector.from_instruction(
                circuit.remove_final_measurements(inplace=False)
            )
            measured = 1 if prefix == "q1" else 0
            p0 = float(sv.probabilities([measured])[0])
            expected = IDEAL_P0[(state, basis)]
            if abs(p0 - expected) > 1e-9:
                failures.append(f"{prefix}_{state}_{basis}: {p0} != {expected}")
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
    prefix = f"q{args.qubit}"
    out = Path(args.out_dir) if args.out_dir else OUT
    circuits = {
        key: qasm2.loads(qasm)
        for key, qasm in spam_tomography_plan(args.qubit).items()
    }
    simulation = _run_simulation(circuits, prefix=prefix)
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
    fit = fit_spam_tomography(counts, prefix=prefix)
    payload = {
        "schema_version": 1,
        "backend": args.backend,
        "set": int(args.set),
        "shots": args.shots,
        "qubit": int(args.qubit),
        "gates": {"tdd": tdd["ok"], "simulation": simulation["ok"]},
        "task_ids": task_ids,
        "counts": counts,
        "fit": fit,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "limits": f"Tomografia de q{args.qubit}; não é GST completa.",
    }
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"set{args.set}.json"
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


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _analyze_qubit(
    out_dir: Path,
    prefix: str,
    *,
    n_bootstrap: int = 2000,
    seed: int = 42,
) -> dict | None:
    """Combina os conjuntos disponíveis de um qubit e calcula bootstrap."""
    path1 = out_dir / "set1.json"
    path2 = out_dir / "set2.json"
    if not path1.exists():
        return None
    set1 = _load_json(path1)
    sets = {"set1": set1}
    counts = dict(set1["counts"])
    if path2.exists():
        set2 = _load_json(path2)
        sets["set2"] = set2
        counts = _combine(set1, set2)
    fit = fit_spam_tomography(counts, prefix=prefix)
    bootstrap = bootstrap_spam_tomography(
        counts, prefix=prefix, n_bootstrap=n_bootstrap, seed=seed
    )
    per_set = {}
    for name, payload in sets.items():
        per_set[name] = {
            "fit": payload["fit"],
            "task_ids": payload.get("task_ids"),
        }
    payload = {
        "schema_version": 1,
        "prefix": prefix,
        "n_sets": len(sets),
        "shots_per_set": sets["set1"].get("shots"),
        "fit_combined": fit,
        "bootstrap_combined": bootstrap,
        "sets": per_set,
        "limits": (
            "Bootstrap multinomial dos counts combinados; não captura drift entre "
            "conjuntos. A tomografia assume rotações de base ideais e ausência de "
            "crosstalk; não é GST completa."
        ),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "comparison.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lines = [
        f"# Tomografia SPAM — {prefix}",
        "",
        f"Conjuntos: **{len(sets)}**. Shots por conjunto: {sets['set1'].get('shots')}.",
        "",
        r"| Conjunto | Prep \|0> | Prep \|1> | Prep \|+> | Prep \|+i> | r0 | r1 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, item in per_set.items():
        fit_item = item["fit"]
        lines.append(
            f"| {name} | {fit_item['prep_fidelity']['0']:.4f} | "
            f"{fit_item['prep_fidelity']['1']:.4f} | "
            f"{fit_item['prep_fidelity']['+']:.4f} | "
            f"{fit_item['prep_fidelity']['+i']:.4f} | "
            f"{fit_item['readout_p1_given_prep0']:.4f} | "
            f"{fit_item['readout_p0_given_prep1']:.4f} |"
        )
    lines += [
        "",
        "## Combinado + bootstrap",
        "",
        "| Métrica | Valor | IC 95% |",
        "|---|---:|---:|",
    ]
    for state in ("0", "1", "+", "+i"):
        item = bootstrap["prep_fidelity"][state]
        lines.append(
            f"| Prep \\|{state}> | {fit['prep_fidelity'][state]:.4f} | "
            f"[{item['low']:.4f}, {item['high']:.4f}] |"
        )
    for key, label in (
        ("r0", "r0"),
        ("r1", "r1"),
    ):
        item = bootstrap["readout"][key]
        lines.append(
            f"| {label} | {item['mean']:.4f} | [{item['low']:.4f}, {item['high']:.4f}] |"
        )
    lines += [
        "",
        "## Redundância do desenho",
        "",
        "- Neste desenho, `prep \\|0>` = 1 − r0 e `prep \\|1>` = 1 − r1:",
        "  são a mesma contagem Z, não duas evidências independentes.",
        "- A preparação coerente independente de readout é medida por `\\|+>` e `\\|+i>`.",
        "",
        "## Limites",
        "",
        "- Bootstrap multinomial não captura drift entre conjuntos.",
        "- A tomografia assume rotações de base ideais.",
        "- Não é GST completa.",
        "",
    ]
    (out_dir / f"RELATORIO_{prefix.upper()}.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    return payload


def _set_spread(payload: dict, key: str) -> float | None:
    values = []
    for item in payload.get("sets", {}).values():
        fit_item = item.get("fit") or {}
        if key.startswith("prep_"):
            value = (fit_item.get("prep_fidelity") or {}).get(key.split("_", 1)[1])
        else:
            value = fit_item.get(
                "readout_p1_given_prep0" if key == "r0" else "readout_p0_given_prep1"
            )
        if value is not None:
            values.append(float(value))
    if len(values) < 2:
        return None
    return max(values) - min(values)


def _delta(q0: dict, q1: dict, key: str) -> dict:
    if key.startswith("prep_"):
        state = key.split("_", 1)[1]
        a = float(q0["fit_combined"]["prep_fidelity"][state])
        b = float(q1["fit_combined"]["prep_fidelity"][state])
        a_ci = q0["bootstrap_combined"]["prep_fidelity"][state]
        b_ci = q1["bootstrap_combined"]["prep_fidelity"][state]
    else:
        field = "readout_p1_given_prep0" if key == "r0" else "readout_p0_given_prep1"
        a = float(q0["fit_combined"][field])
        b = float(q1["fit_combined"][field])
        a_ci = q0["bootstrap_combined"]["readout"][key]
        b_ci = q1["bootstrap_combined"]["readout"][key]
    return {
        "q0": a,
        "q1": b,
        "delta_q1_minus_q0": b - a,
        "q0_ci": [float(a_ci["low"]), float(a_ci["high"])],
        "q1_ci": [float(b_ci["low"]), float(b_ci["high"])],
        "ci_overlap": not (
            float(a_ci["high"]) < float(b_ci["low"])
            or float(b_ci["high"]) < float(a_ci["low"])
        ),
        "q0_set_spread": _set_spread(q0, key),
        "q1_set_spread": _set_spread(q1, key),
    }


def analyze() -> int:
    q0 = _analyze_qubit(Q0_DIR, "q0")
    q1 = _analyze_qubit(OUT, "q1")
    if q0 is None or q1 is None:
        _json_print(
            {
                "status": "blocked",
                "reason": "conjuntos ausentes",
                "q0_sets": bool(q0),
                "q1_sets": bool(q1),
            }
        )
        return 2

    metrics = [
        "prep_0", "prep_1", "prep_+", "prep_+i", "r0", "r1",
    ]
    deltas = {key: _delta(q0, q1, key) for key in metrics}
    payload = {
        "schema_version": 1,
        "q0": {
            "n_sets": q0["n_sets"],
            "fit_combined": q0["fit_combined"],
            "bootstrap_combined": q0["bootstrap_combined"],
        },
        "q1": {
            "n_sets": q1["n_sets"],
            "fit_combined": q1["fit_combined"],
            "bootstrap_combined": q1["bootstrap_combined"],
        },
        "deltas": deltas,
        "limits": (
            "Comparação descritiva entre q0 e q1, cada um com dois conjuntos. "
            "Os ICs bootstrap são multinomiais e não incluem drift entre conjuntos. "
            "Sobreposição de IC não é teste de hipótese."
        ),
    }
    (BASE / "comparison_q0_q1.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    lines = [
        "# Comparação simétrica q0 vs q1 — tomografia SPAM",
        "",
        "Cada qubit tem dois conjuntos de 12 jobs. A comparação é descritiva.",
        "",
        r"| Métrica | q0 | q1 | Δ (q1−q0) | IC q0 | IC q1 | Spread q0 | Spread q1 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    labels = {
        "prep_0": r"Prep \|0>", "prep_1": r"Prep \|1>",
        "prep_+": r"Prep \|+>", "prep_+i": r"Prep \|+i>",
        "r0": "r0", "r1": "r1",
    }
    for key in metrics:
        item = deltas[key]
        spread0 = "-" if item["q0_set_spread"] is None else f"{item['q0_set_spread']:.4f}"
        spread1 = "-" if item["q1_set_spread"] is None else f"{item['q1_set_spread']:.4f}"
        lines.append(
            f"| {labels[key]} | {item['q0']:.4f} | {item['q1']:.4f} | "
            f"{item['delta_q1_minus_q0']:+.4f} | "
            f"[{item['q0_ci'][0]:.4f}, {item['q0_ci'][1]:.4f}] | "
            f"[{item['q1_ci'][0]:.4f}, {item['q1_ci'][1]:.4f}] | "
            f"{spread0} | {spread1} |"
        )
    lines += [
        "",
        "## Leitura",
        "",
        "- Δ negativo em fidelidade de preparação significa q1 pior que q0.",
        "- Δ positivo em r0/r1 significa mais erro de leitura em q1.",
        "- Sobreposição de IC não equivale a equivalência estatística.",
        "- Spread entre conjuntos maior que a largura do IC indica drift/variação",
        "  não capturada pelo bootstrap multinomial.",
        "- `prep \\|0>` = 1 − r0 e `prep \\|1>` = 1 − r1 neste desenho:",
        "  as linhas de prep |0>/|1> e r0/r1 não são evidências independentes.",
        "  A comparação de q1 vs q0 nesses pares é uma única medida, não duas.",
        "",
        "## Limites",
        "",
        "- Dois conjuntos por qubit; não é série temporal.",
        "- Sem GST completa, sem crosstalk caracterizado.",
        "- Nenhuma vantagem quântica é declarada.",
        "",
    ]
    (BASE / "RELATORIO_Q0_Q1.md").write_text("\n".join(lines), encoding="utf-8")
    _json_print(
        {
            "status": "ok",
            "comparison": str(BASE / "comparison_q0_q1.json"),
            "report": str(BASE / "RELATORIO_Q0_Q1.md"),
            "q0": q0["fit_combined"],
            "q1": q1["fit_combined"],
            "deltas": {
                key: {
                    "delta": item["delta_q1_minus_q0"],
                    "ci_overlap": item["ci_overlap"],
                }
                for key, item in deltas.items()
            },
        }
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", type=int, choices=[1, 2])
    parser.add_argument("--qubit", type=int, choices=[0, 1], default=1)
    parser.add_argument("--out-dir", default=None)
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
