#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Harness de mitigação e correção de erro quântico (R1114).

Comandos offline/simulados: zne, dd, pec, qec, spam, crosstalk, drift,
uncertainty, lessons, audit. Nenhum job é submetido.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from gjq_hardware_opt import HardwareProfile, load_circuit  # noqa: E402
from quantum_mitigation import (  # noqa: E402
    crosstalk_metric,
    dd_plan,
    drift_detection,
    fit_spam,
    pec_plan,
    qec_plan,
    run_repetition_code,
    run_zne,
    uncertainty_report,
)

OUT_PADRAO = Path(__file__).resolve().parent / "resultados"


def _json_print(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write(out: Path, payload: dict, title: str, lines: list[str]) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    (out / "resultado.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    report = [
        f"# {title}",
        "",
        f"Gerado em {datetime.now().astimezone().isoformat(timespec='seconds')}.",
        "",
        *lines,
        "",
        "## Limites",
        "",
        "- Técnica de mitigação/correção local; não é prova de vantagem.",
        "- Não houve execução em hardware.",
        "- Nenhuma chave ou segredo é usado.",
        "",
    ]
    (out / "RELATORIO.md").write_text("\n".join(report), encoding="utf-8")
    return {
        "out_dir": str(out),
        "files": [str(out / "resultado.json"), str(out / "RELATORIO.md")],
    }


def cmd_zne(args) -> int:
    profile = HardwareProfile.from_dict(_read_json(args.profile))
    item = load_circuit(args.circuit)
    payload = run_zne(
        item["circuit"],
        profile,
        scales=tuple(args.scales),
        shots=args.shots,
        seed=args.seed,
        method=args.method,
    )
    payload["circuit"] = item["name"]
    payload["profile"] = profile.name
    rows = payload["scales"]
    lines = [
        "## Curva ZNE",
        "",
        "| Escala | TVD | Profundidade |",
        "|---:|---:|---:|",
        *[
            f"| {row['scale']} | {row['tvd']:.4e} | {row['depth']} |"
            for row in rows
        ],
        "",
        f"Extrapolação `{payload['extrapolation']['method']}`: "
        f"**{payload['extrapolation']['extrapolated']:.4e}**.",
    ]
    exported = _write(Path(args.out), payload, "ZNE — zero-noise extrapolation", lines)
    _json_print(
        {
            "status": "ok",
            "command": "zne",
            "circuit": item["name"],
            "extrapolated": payload["extrapolation"]["extrapolated"],
            **exported,
            "hardware_executed": False,
        }
    )
    return 0


def cmd_dd(args) -> int:
    item = load_circuit(args.circuit)
    payload = dd_plan(item["circuit"], args.qubits, args.sequence)
    payload["circuit"] = item["name"]
    lines = [
        "## Plano DD",
        "",
        f"- Sequência: `{payload['sequence']}`.",
        f"- Qubits: `{payload['qubits']}`.",
        f"- Fidelidade de identidade: {payload['identity_fidelity']:.6f}.",
        f"- Profundidade: {payload['base_depth']} → {payload['dd_depth']}.",
        f"- Tamanho: {payload['base_size']} → {payload['dd_size']}.",
    ]
    exported = _write(Path(args.out), payload, "DD — dynamical decoupling", lines)
    _json_print(
        {
            "status": "ok",
            "command": "dd",
            "identity_ok": payload["identity_ok"],
            **exported,
            "hardware_executed": False,
        }
    )
    return 0


def cmd_pec(args) -> int:
    profile = HardwareProfile.from_dict(_read_json(args.profile))
    item = load_circuit(args.circuit)
    payload = pec_plan(
        item["circuit"], profile, target_relative_error=args.target_relative_error
    )
    payload["circuit"] = item["name"]
    payload["profile"] = profile.name
    lines = [
        "## Plano PEC",
        "",
        f"- Gates 1q no plano: **{len(payload['gates_1q'])}**.",
        f"- Overhead γ total: **{payload['gamma_total']:.4f}**.",
        f"- Amostras estimadas para erro relativo "
        f"{payload['target_relative_error']:.0%}: **{payload['samples_required']:.3e}**.",
        f"- Avisos: {payload['warnings'] or 'nenhum'}.",
    ]
    exported = _write(Path(args.out), payload, "PEC — probabilistic error cancellation", lines)
    _json_print(
        {
            "status": "ok",
            "command": "pec",
            "gamma_total": payload["gamma_total"],
            "samples_required": payload["samples_required"],
            **exported,
            "hardware_executed": False,
        }
    )
    return 0


def cmd_qec(args) -> int:
    payload = run_repetition_code(args.p, shots=args.shots, seed=args.seed)
    lines = [
        "## Código de repetição",
        "",
        f"- Distância: {payload['distance']}.",
        f"- p físico: {payload['p']:.4f}.",
        f"- Erro lógico simulado: **{payload['logical_error_simulated']:.6f}**.",
        f"- Erro lógico teórico: **{payload['logical_error_theory']:.6f}**.",
        f"- Shots: {payload['shots']}.",
    ]
    exported = _write(Path(args.out), payload, "QEC — repetição de 3 qubits", lines)
    _json_print(
        {
            "status": "ok",
            "command": "qec",
            "logical_error_simulated": payload["logical_error_simulated"],
            "logical_error_theory": payload["logical_error_theory"],
            **exported,
            "hardware_executed": False,
        }
    )
    return 0


def cmd_spam(args) -> int:
    payload = fit_spam(_read_json(args.counts0), _read_json(args.counts1))
    lines = [
        "## SPAM",
        "",
        f"- p(1|prep0): {payload['p1_given_prep0']:.6f}.",
        f"- p(0|prep1): {payload['p0_given_prep1']:.6f}.",
        f"- readout simétrico: {payload['readout_error_symmetric']:.6f}.",
        "",
        f"> {payload['note']}",
    ]
    exported = _write(Path(args.out), payload, "SPAM — preparação e leitura", lines)
    _json_print({"status": "ok", "command": "spam", **exported, "hardware_executed": False})
    return 0


def cmd_crosstalk(args) -> int:
    payload = crosstalk_metric(args.isolated, args.simultaneous)
    lines = [
        "## Crosstalk",
        "",
        f"- Erro isolado: {payload['isolated_error']:.6f}.",
        f"- Erro simultâneo: {payload['simultaneous_error']:.6f}.",
        f"- Excesso: {payload['excess']:+.6f}.",
        f"- Razão: {payload['ratio']}.",
    ]
    exported = _write(Path(args.out), payload, "Crosstalk — isolado vs simultâneo", lines)
    _json_print({"status": "ok", "command": "crosstalk", **exported, "hardware_executed": False})
    return 0


def cmd_drift(args) -> int:
    payload = drift_detection(args.values)
    lines = [
        "## Drift",
        "",
        f"- n: {payload['n']}.",
        f"- Média: {payload['mean']:.6f}.",
        f"- Inclinação por passo: {payload['slope_per_step']:+.6e}.",
        f"- Deriva relativa: {payload['relative_drift']}.",
        f"- CUSUM máximo absoluto: {payload['cusum_max_abs']:.6f}.",
    ]
    exported = _write(Path(args.out), payload, "Drift — tendência e CUSUM", lines)
    _json_print({"status": "ok", "command": "drift", **exported, "hardware_executed": False})
    return 0


def cmd_uncertainty(args) -> int:
    payload = uncertainty_report(args.values)
    lines = [
        "## Incerteza",
        "",
        f"- n: {payload['n']}.",
        f"- Média: {payload['mean']:.6f}.",
        f"- Desvio: {payload['std']:.6f}.",
        f"- Mín./máx.: {payload['min']:.6f} / {payload['max']:.6f}.",
    ]
    if payload.get("bootstrap"):
        item = payload["bootstrap"]
        lines.append(
            f"- Bootstrap {item['confidence']:.0%}: "
            f"[{item['low']:.6f}, {item['high']:.6f}]."
        )
    exported = _write(Path(args.out), payload, "Incerteza — dispersão e bootstrap", lines)
    _json_print({"status": "ok", "command": "uncertainty", **exported, "hardware_executed": False})
    return 0


def cmd_lessons(args) -> int:
    state = _read_json(args.loop_state)
    lessons = state.get("lessons") or []
    history = state.get("history") or []
    payload = {
        "schema_version": 1,
        "loop_id": state.get("loop_id"),
        "status": state.get("status"),
        "lessons": lessons,
        "history": [
            {
                "iteration": item.get("iteration"),
                "score": item.get("score"),
                "baseline_task": item.get("baseline_task"),
                "optimized_task": item.get("optimized_task"),
            }
            for item in history
        ],
        "best": state.get("best"),
        "limits": "Lições locais do loop; não são prova universal.",
    }
    lesson_lines = [f"- {lesson}" for lesson in lessons] or [
        "- Nenhuma lição registrada."
    ]
    lines = [
        "## Lições do loop",
        "",
        *lesson_lines,
        "",
        "O loop não promove confiança automaticamente.",
    ]
    exported = _write(Path(args.out), payload, "Lições do loop GJQ", lines)
    _json_print({"status": "ok", "command": "lessons", **exported, "hardware_executed": False})
    return 0


def cmd_audit(args) -> int:
    text = Path(args.report).read_text(encoding="utf-8").lower()
    forbidden = (
        "fidelidade medida com sucesso",
        "vantagem quântica comprovada",
        "speedup garantido",
        "prova experimental de emaranhamento",
        "benchmark definitivo",
        "correção total de erro",
    )
    hits = [term for term in forbidden if term in text]
    payload = {
        "schema_version": 1,
        "report": str(args.report),
        "hits": hits,
        "ok": not hits,
        "limits": "Auditoria lexical; não substitui peer review.",
    }
    lines = [
        "## Auditoria lexical",
        "",
        f"- Termos proibidos encontrados: {hits or 'nenhum'}.",
        f"- Status: **{'ok' if not hits else 'blocked'}**.",
    ]
    exported = _write(Path(args.out), payload, "Auditoria de overclaim", lines)
    _json_print({"status": "ok" if not hits else "blocked", "command": "audit", **exported})
    return 0 if not hits else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mitigação e correção de erro quântico (R1114).")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("zne", help="zero-noise extrapolation")
    p.add_argument("--profile", required=True)
    p.add_argument("--circuit", default="E05")
    p.add_argument("--scales", nargs="+", type=int, default=[1, 3, 5])
    p.add_argument("--shots", type=int, default=2048)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--method", default="linear", choices=["linear", "quadratic", "exponential"])
    p.add_argument("--out", default=str(OUT_PADRAO / "zne"))
    p.set_defaults(func=cmd_zne)

    p = sub.add_parser("dd", help="dynamical decoupling")
    p.add_argument("--circuit", default="E05")
    p.add_argument("--qubits", nargs="+", type=int, default=[0, 1])
    p.add_argument("--sequence", default="xy4", choices=["xy4", "cpmg", "echo"])
    p.add_argument("--out", default=str(OUT_PADRAO / "dd"))
    p.set_defaults(func=cmd_dd)

    p = sub.add_parser("pec", help="planejador PEC 1q")
    p.add_argument("--profile", required=True)
    p.add_argument("--circuit", default="E05")
    p.add_argument("--target-relative-error", type=float, default=0.01)
    p.add_argument("--out", default=str(OUT_PADRAO / "pec"))
    p.set_defaults(func=cmd_pec)

    p = sub.add_parser("qec", help="código de repetição de 3 qubits")
    p.add_argument("--p", type=float, default=0.01)
    p.add_argument("--shots", type=int, default=20000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default=str(OUT_PADRAO / "qec"))
    p.set_defaults(func=cmd_qec)

    p = sub.add_parser("spam", help="SPAM |0>/|1>")
    p.add_argument("--counts0", required=True)
    p.add_argument("--counts1", required=True)
    p.add_argument("--out", default=str(OUT_PADRAO / "spam"))
    p.set_defaults(func=cmd_spam)

    p = sub.add_parser("crosstalk", help="métrica isolado vs simultâneo")
    p.add_argument("--isolated", type=float, required=True)
    p.add_argument("--simultaneous", type=float, required=True)
    p.add_argument("--out", default=str(OUT_PADRAO / "crosstalk"))
    p.set_defaults(func=cmd_crosstalk)

    p = sub.add_parser("drift", help="tendência e CUSUM")
    p.add_argument("--values", nargs="+", type=float, required=True)
    p.add_argument("--out", default=str(OUT_PADRAO / "drift"))
    p.set_defaults(func=cmd_drift)

    p = sub.add_parser("uncertainty", help="dispersão e bootstrap")
    p.add_argument("--values", nargs="+", type=float, required=True)
    p.add_argument("--out", default=str(OUT_PADRAO / "uncertainty"))
    p.set_defaults(func=cmd_uncertainty)

    p = sub.add_parser("lessons", help="extrai lições do loop")
    p.add_argument("--loop-state", required=True)
    p.add_argument("--out", default=str(OUT_PADRAO / "lessons"))
    p.set_defaults(func=cmd_lessons)

    p = sub.add_parser("audit", help="auditoria lexical de overclaim")
    p.add_argument("--report", required=True)
    p.add_argument("--out", default=str(OUT_PADRAO / "audit"))
    p.set_defaults(func=cmd_audit)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
