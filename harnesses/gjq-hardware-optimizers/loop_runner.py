#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runner de engenharia de loop GJQ (SPEC-935-R1112).

Estágios: plan -> simulate -> execute -> score.
O hardware só é chamado após SDD, TDD, simulação e com confirm/allow_hardware.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = Path(__file__).resolve().parent / "runner.py"
sys.path.insert(0, str(ROOT))

from gjq_hardware_opt import HardwareProfile  # noqa: E402
from gjq_hardware_opt.loop import (  # noqa: E402
    append_log,
    export_loop,
    load_state,
    new_state,
    now,
    run_sdd_gate,
    run_tdd_gate,
    save_state,
    score_comparison,
    simulation_gate,
)

SPECS = [
    str(ROOT / "specs" / "SPEC-935-R1112-gjq-loop-engineering.md"),
    str(ROOT / "specs" / "SPEC-935-R1110-gjq-readout-mitigation.md"),
]
TESTS = [
    str(ROOT / "tests" / "test_r1112_gjq_loop_engineering.py"),
    str(ROOT / "tests" / "test_r1110_gjq_readout_mitigation.py"),
]


def _json_print(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _run_runner(arguments: list[str], timeout: int = 1800):
    command = [sys.executable, str(RUNNER), *arguments]
    result = subprocess.run(
        command,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return command, result


def _load_simulation(state: dict) -> dict | None:
    path = Path(state["paths"].get("simulation", ""))
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("simulation"), dict):
        return payload["simulation"]
    return payload


def _load_comparison(state: dict) -> dict | None:
    path = Path(state["paths"].get("comparison", ""))
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def cmd_plan(args) -> int:
    if not args.backend and not args.profile:
        raise SystemExit("use --backend (ao vivo) ou --profile (offline)")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    plan_dir = out / "plan"
    plan_dir.mkdir(parents=True, exist_ok=True)
    compare_args = [
        "compare", "--plan",
        "--circuit", args.circuit,
        "--shots", str(args.shots),
        "--strategy", args.strategy,
        "--seed", str(args.seed),
        "--out", str(plan_dir),
    ]
    if args.quick:
        compare_args.append("--quick")
    compare_args.append("--calibrate" if args.calibrate else "--no-calibrate")
    if args.profile:
        compare_args.extend(["--profile", args.profile])
    if args.backend:
        compare_args.extend(["--backend", args.backend])
    if args.use_cached_account:
        compare_args.append("--use-cached-account")
    command, result = _run_runner(compare_args, timeout=args.timeout)
    if result.returncode != 0:
        _json_print(
            {
                "status": "blocked",
                "stage": "plan",
                "returncode": result.returncode,
                "stdout_tail": result.stdout[-2000:],
                "stderr_tail": result.stderr[-2000:],
                "command": command,
            }
        )
        return 2
    plan_path = plan_dir / "plano_comparacao.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    state = new_state(
        backend=args.backend,
        profile_file=args.profile,
        circuit=args.circuit,
        shots=args.shots,
        max_iterations=args.iterations,
        out_dir=out,
    )
    state["seed"] = int(args.seed)
    state["strategy"] = args.strategy
    state["quick"] = bool(args.quick)
    state["calibrate"] = bool(args.calibrate)
    state["submissions_estimated"] = int(plan.get("submissions_estimated", 0))
    state["status"] = "planned"
    save_state(state, out / "loop_state.json")
    append_log(out, {"event": "plan", "status": "ok", "at": now(), "plan": str(plan_path)})
    exported = export_loop(state, out)
    _json_print(
        {
            "status": "planned",
            "loop_id": state["loop_id"],
            "backend": state["backend"],
            "circuit": state["circuit"],
            "shots": state["shots"],
            "submissions_estimated": state["submissions_estimated"],
            "plan": str(plan_path),
            "state": exported["state"],
            "report": exported["report"],
            "hardware_executed": False,
        }
    )
    return 0


def cmd_simulate(args) -> int:
    state_path = Path(args.state)
    state = load_state(state_path)
    out = Path(state["paths"]["out_dir"])
    plan = json.loads(Path(state["paths"]["plan"]).read_text(encoding="utf-8"))
    profile_path = Path(state["paths"]["plan_dir"]) / "perfil.json"
    profile = HardwareProfile.from_dict(
        json.loads(profile_path.read_text(encoding="utf-8"))
    )
    tests = list(getattr(args, "tdd_test", None) or TESTS)
    sdd = run_sdd_gate(SPECS, tests)
    tdd = run_tdd_gate(tests, timeout=int(getattr(args, "tdd_timeout", 900)))
    simulation = simulation_gate(
        plan, profile, shots=state["shots"], seed=int(state.get("seed", 42))
    )
    state["gates"]["sdd"] = bool(sdd["ok"])
    state["gates"]["tdd"] = bool(tdd["ok"])
    state["gates"]["simulation"] = bool(simulation["gate_ok"])
    state["status"] = (
        "simulated"
        if all(state["gates"][key] for key in ("sdd", "tdd", "simulation"))
        else "blocked"
    )
    (out / "simulacao.json").write_text(
        json.dumps(
            {"sdd": sdd, "tdd": tdd, "simulation": simulation},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    save_state(state, state_path)
    append_log(
        out,
        {
            "event": "simulate",
            "status": state["status"],
            "at": now(),
            "gates": state["gates"],
            "simulated_winner": simulation.get("simulated_winner"),
        },
    )
    exported = export_loop(state, out, simulation=simulation)
    _json_print(
        {
            "status": state["status"],
            "gates": state["gates"],
            "sdd": sdd,
            "tdd_ok": tdd["ok"],
            "tdd_returncode": tdd.get("returncode"),
            "simulation_gate": simulation["gate_ok"],
            "ideal_equivalence_tvd": simulation["ideal_equivalence_tvd"],
            "simulated_winner": simulation["simulated_winner"],
            "baseline_tvd": simulation["baseline"]["tvd_noisy_vs_ideal"],
            "optimized_tvd": simulation["optimized"]["tvd_noisy_vs_ideal"],
            "state": str(state_path),
            "report": exported["report"],
        }
    )
    return 0 if state["status"] == "simulated" else 2


def cmd_execute(args) -> int:
    state_path = Path(args.state)
    state = load_state(state_path)
    out = Path(state["paths"]["out_dir"])
    gates = state.get("gates", {})
    if not all(gates.get(key) for key in ("sdd", "tdd", "simulation")):
        _json_print(
            {
                "status": "blocked",
                "reason": "gates SDD/TDD/simulação não passaram",
                "gates": gates,
            }
        )
        return 2
    if not args.confirm or not args.allow_hardware:
        _json_print(
            {
                "status": "blocked",
                "reason": "hardware exige --confirm e --allow-hardware",
                "gates": gates,
            }
        )
        return 2
    if not state.get("backend"):
        _json_print(
            {
                "status": "blocked",
                "reason": "execução de hardware exige backend ao vivo",
            }
        )
        return 2
    comparison_dir = out / "comparacao"
    compare_args = [
        "compare",
        "--backend", state["backend"],
        "--circuit", state["circuit"],
        "--shots", str(state["shots"]),
        "--strategy", state.get("strategy", "balanced"),
        "--seed", str(state.get("seed", 42)),
        "--out", str(comparison_dir),
    ]
    if state.get("quick"):
        compare_args.append("--quick")
    compare_args.append("--calibrate" if state.get("calibrate") else "--no-calibrate")
    compare_args.extend(["--confirm", "--allow-hardware"])
    if args.use_cached_account:
        compare_args.append("--use-cached-account")
    compare_args.extend(["--timeout", str(args.timeout), "--poll", str(args.poll)])
    command, result = _run_runner(compare_args, timeout=args.timeout * 7)
    if result.returncode != 0:
        state["status"] = "blocked"
        save_state(state, state_path)
        _json_print(
            {
                "status": "blocked",
                "stage": "execute",
                "returncode": result.returncode,
                "stdout_tail": result.stdout[-2000:],
                "stderr_tail": result.stderr[-2000:],
                "command": command,
            }
        )
        return 2
    comparison_path = comparison_dir / "comparacao.json"
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    state["gates"]["hardware"] = True
    state["status"] = "executed"
    state["submissions_used"] = int(state.get("submissions_estimated", 0))
    state["paths"]["comparison"] = str(comparison_path)
    save_state(state, state_path)
    append_log(
        out,
        {
            "event": "execute",
            "status": "ok",
            "at": now(),
            "baseline_task": comparison["baseline"].get("task_id"),
            "optimized_task": comparison["optimized"].get("task_id"),
        },
    )
    exported = export_loop(state, out, comparison=comparison)
    _json_print(
        {
            "status": "executed",
            "baseline_task": comparison["baseline"].get("task_id"),
            "optimized_task": comparison["optimized"].get("task_id"),
            "comparison": str(comparison_path),
            "state": str(state_path),
            "report": exported["report"],
            "hardware_executed": True,
        }
    )
    return 0


def cmd_score(args) -> int:
    state_path = Path(args.state)
    state = load_state(state_path)
    out = Path(state["paths"]["out_dir"])
    comparison = _load_comparison(state)
    if comparison is None:
        _json_print({"status": "blocked", "reason": "comparação ausente"})
        return 2
    score = score_comparison(comparison)
    state["status"] = "scored"
    state["history"].append(
        {
            "iteration": state.get("iteration", 1),
            "at": now(),
            "score": score,
            "baseline_task": comparison["baseline"].get("task_id"),
            "optimized_task": comparison["optimized"].get("task_id"),
            "comparison_path": state["paths"].get("comparison"),
        }
    )
    state["lessons"].append(score["lesson"])
    best_key = (
        score["optimized_mitigated_tvd"]
        if score.get("optimized_mitigated_tvd") is not None
        else score["optimized_raw_tvd"]
    )
    if state.get("best") is None or best_key < state["best"]["score"]:
        state["best"] = {
            "iteration": state.get("iteration", 1),
            "score": best_key,
            "winner": score["mitigated_winner"],
            "task_id": comparison["optimized"].get("task_id"),
        }
    simulation = _load_simulation(state)
    save_state(state, state_path)
    append_log(out, {"event": "score", "status": "ok", "at": now(), "score": score})
    exported = export_loop(
        state, out, simulation=simulation, comparison=comparison, score=score
    )
    _json_print(
        {
            "status": "scored",
            "score": score,
            "best": state["best"],
            "lessons": state["lessons"],
            "state": str(state_path),
            "report": exported["report"],
        }
    )
    return 0


def cmd_run(args) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    args.plan = True  # compatibilidade de namespace
    if cmd_plan(args) != 0:
        return 2
    args.state = str(out / "loop_state.json")
    if cmd_simulate(args) != 0:
        return 2
    if not (args.confirm and args.allow_hardware):
        _json_print(
            {
                "status": "simulated",
                "reason": "hardware não autorizado; plano e simulação concluídos",
                "state": args.state,
                "report": str(out / "RELATORIO_LOOP.md"),
                "hardware_executed": False,
            }
        )
        return 0
    if cmd_execute(args) != 0:
        return 2
    return cmd_score(args)


def cmd_status(args) -> int:
    state = load_state(Path(args.state))
    _json_print(state)
    return 0


def cmd_report(args) -> int:
    state = load_state(Path(args.state))
    out = Path(state["paths"]["out_dir"])
    simulation = _load_simulation(state)
    comparison = _load_comparison(state)
    score = state["history"][-1]["score"] if state.get("history") else None
    exported = export_loop(
        state, out, simulation=simulation, comparison=comparison, score=score
    )
    _json_print({"status": "ok", **exported})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Loop GJQ: SDD, TDD, simulação, hardware e mitigação."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_plan = sub.add_parser("plan", help="gera o plano sem submeter")
    p_plan.add_argument("--backend")
    p_plan.add_argument("--profile")
    p_plan.add_argument("--circuit", default="E05")
    p_plan.add_argument("--shots", type=int, default=4096)
    p_plan.add_argument("--strategy", default="balanced")
    p_plan.add_argument("--seed", type=int, default=42)
    p_plan.add_argument("--quick", action="store_true")
    p_plan.add_argument(
        "--calibrate", action=argparse.BooleanOptionalAction, default=True
    )
    p_plan.add_argument("--iterations", type=int, default=1)
    p_plan.add_argument("--timeout", type=float, default=900.0)
    p_plan.add_argument("--use-cached-account", action="store_true")
    p_plan.add_argument("--out", required=True)
    p_plan.set_defaults(func=cmd_plan)

    p_sim = sub.add_parser("simulate", help="roda SDD, TDD e simulação")
    p_sim.add_argument("--state", required=True)
    p_sim.add_argument("--tdd-timeout", type=int, default=900)
    p_sim.add_argument(
        "--tdd-test", action="append", default=None,
        help="teste(s) para o gate TDD; padrão R1112+R1110",
    )
    p_sim.set_defaults(func=cmd_simulate)

    p_exec = sub.add_parser("execute", help="executa hardware após os gates")
    p_exec.add_argument("--state", required=True)
    p_exec.add_argument("--confirm", action="store_true")
    p_exec.add_argument("--allow-hardware", action="store_true")
    p_exec.add_argument("--use-cached-account", action="store_true")
    p_exec.add_argument("--timeout", type=float, default=900.0)
    p_exec.add_argument("--poll", type=float, default=5.0)
    p_exec.set_defaults(func=cmd_execute)

    p_score = sub.add_parser("score", help="pontua e reflete sobre a comparação")
    p_score.add_argument("--state", required=True)
    p_score.set_defaults(func=cmd_score)

    p_run = sub.add_parser("run", help="plan -> simulate -> execute -> score")
    p_run.add_argument("--backend")
    p_run.add_argument("--profile")
    p_run.add_argument("--circuit", default="E05")
    p_run.add_argument("--shots", type=int, default=4096)
    p_run.add_argument("--strategy", default="balanced")
    p_run.add_argument("--seed", type=int, default=42)
    p_run.add_argument("--quick", action="store_true")
    p_run.add_argument(
        "--calibrate", action=argparse.BooleanOptionalAction, default=True
    )
    p_run.add_argument("--iterations", type=int, default=1)
    p_run.add_argument("--confirm", action="store_true")
    p_run.add_argument("--allow-hardware", action="store_true")
    p_run.add_argument("--use-cached-account", action="store_true")
    p_run.add_argument("--timeout", type=float, default=900.0)
    p_run.add_argument("--poll", type=float, default=5.0)
    p_run.add_argument("--tdd-timeout", type=int, default=900)
    p_run.add_argument(
        "--tdd-test", action="append", default=None,
        help="teste(s) para o gate TDD; padrão R1112+R1110",
    )
    p_run.add_argument("--out", required=True)
    p_run.set_defaults(func=cmd_run)

    p_status = sub.add_parser("status", help="mostra o estado do loop")
    p_status.add_argument("--state", required=True)
    p_status.set_defaults(func=cmd_status)

    p_report = sub.add_parser("report", help="regenera o relatório do loop")
    p_report.add_argument("--state", required=True)
    p_report.set_defaults(func=cmd_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
