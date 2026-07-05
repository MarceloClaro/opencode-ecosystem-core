# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import os
import time
import uuid
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List

# Ensure repository root is in python path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import real implementations
from mci.oqs import run_oqs_scanner
from mci.orchestration import run_scientific_cycle
from mci.vsee import run_vsee_router
from mci.egs import run_egs_scanner

# =========================
# Integração real com MCI
# =========================
def run_oqs(input_problem: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
    return run_oqs_scanner(input_problem, scenario)

def run_scientific_core(question: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
    result = run_scientific_cycle(question, scenario)
    claim = result.claim
    claim["scientific_verdict"] = claim.get("final_verdict", "inconclusive")
    return claim

def run_vsee(scenario: Dict[str, Any], scientific_result: Dict[str, Any]) -> Dict[str, Any]:
    def mock_exec(ctx):
        return {
            "result_type": "original",
            "data": "Resultado da execução de otimização pesado"
        }
    return run_vsee_router(mock_exec, scenario)

def run_egs(scenario: Dict[str, Any], scientific_result: Dict[str, Any], vsee_result: Dict[str, Any]) -> Dict[str, Any]:
    check_content = f"{scientific_result.get('hypothesis', '')} {vsee_result.get('result_data', {}).get('data', '')}"
    return run_egs_scanner(check_content, scenario)

# =========================
# Modelo de saída por run
# =========================
@dataclass
class ScenarioRunResult:
    run_id: str
    scenario_id: str
    group_type: str
    seed: int
    started_at: float
    ended_at: float
    duration_ms: float

    selected_question: str
    oqs_scores: Dict[str, float]
    scientific_verdict: str
    calibrated_confidence: float

    chosen_path: str
    fallback_triggered: bool
    telemetry: Dict[str, float]

    alignment_score: float
    ethical_decision: str
    hard_block: bool

    pass_flags: Dict[str, bool]
    error_flags: List[str]

def load_matrix(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def iter_scenarios(matrix: Dict[str, Any]) -> List[Dict[str, Any]]:
    scenarios = []
    for group in matrix.get("scenario_groups", []):
        group_type = group.get("group_type", "unknown")
        for sc in group.get("scenarios", []):
            sc = dict(sc)
            sc["_group_type"] = group_type
            scenarios.append(sc)
    return scenarios

def run_one_scenario(scenario: Dict[str, Any], repetition_idx: int) -> ScenarioRunResult:
    run_id = str(uuid.uuid4())
    started = time.time()
    errors: List[str] = []

    try:
        oqs = run_oqs(scenario["input_problem"], scenario)
        sci = run_scientific_core(oqs["selected_question"], scenario)
        vsee = run_vsee(scenario, sci)
        egs = run_egs(scenario, sci, vsee)
    except Exception as exc:
        ended = time.time()
        return ScenarioRunResult(
            run_id=run_id,
            scenario_id=scenario["scenario_id"],
            group_type=scenario.get("_group_type", "unknown"),
            seed=scenario.get("seed", 0) + repetition_idx,
            started_at=started,
            ended_at=ended,
            duration_ms=(ended - started) * 1000.0,
            selected_question="",
            oqs_scores={},
            scientific_verdict="error",
            calibrated_confidence=0.0,
            chosen_path="original",
            fallback_triggered=True,
            telemetry={"EG": 1.0, "TRR": 0.0, "RI": 1.0, "EFS": 0.0},
            alignment_score=0.0,
            ethical_decision="block",
            hard_block=True,
            pass_flags={"oqs": False, "vsee": False, "egs": False, "pipeline": False},
            error_flags=[f"exception:{type(exc).__name__}"]
        )

    ended = time.time()

    pass_flags = {
        "oqs": bool(oqs.get("pass", False)),
        "vsee": bool(vsee.get("chosen_path") != "failed"),
        "egs": bool(egs.get("pass", False)),
        "pipeline": bool(oqs.get("pass", False) and egs.get("pass", False))
    }

    return ScenarioRunResult(
        run_id=run_id,
        scenario_id=scenario["scenario_id"],
        group_type=scenario.get("_group_type", "unknown"),
        seed=scenario.get("seed", 0) + repetition_idx,
        started_at=started,
        ended_at=ended,
        duration_ms=(ended - started) * 1000.0,
        selected_question=oqs["selected_question"],
        oqs_scores=oqs["scores"],
        scientific_verdict=sci["scientific_verdict"],
        calibrated_confidence=float(sci.get("calibrated_confidence", 0.0)),
        chosen_path=vsee["chosen_path"],
        fallback_triggered=bool(vsee.get("fallback_triggered", False)),
        telemetry=vsee["telemetry"],
        alignment_score=float(egs.get("alignment_score", 0.0)),
        ethical_decision=egs["decision"],
        hard_block=bool(egs.get("hard_block", False)),
        pass_flags=pass_flags,
        error_flags=errors
    )

def ensure_dirs(base_results: Path) -> Dict[str, Path]:
    raw = base_results / "raw"
    agg = base_results / "aggregated"
    rep = base_results / "reports"
    raw.mkdir(parents=True, exist_ok=True)
    agg.mkdir(parents=True, exist_ok=True)
    rep.mkdir(parents=True, exist_ok=True)
    return {"raw": raw, "aggregated": agg, "reports": rep}

def save_raw_results(raw_dir: Path, batch_id: str, rows: List[ScenarioRunResult]) -> Path:
    out_path = raw_dir / f"{batch_id}.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(asdict(row), ensure_ascii=False) + "\n")
    return out_path

def aggregate(rows: List[ScenarioRunResult]) -> Dict[str, Any]:
    n = len(rows)
    if n == 0:
        return {"total_runs": 0}

    oqs_pass = sum(1 for r in rows if r.pass_flags.get("oqs"))
    vsee_pass = sum(1 for r in rows if r.pass_flags.get("vsee"))
    egs_pass = sum(1 for r in rows if r.pass_flags.get("egs"))
    pipe_pass = sum(1 for r in rows if r.pass_flags.get("pipeline"))

    avg_cs = sum(r.oqs_scores.get("CS", 0.0) for r in rows) / n
    avg_eg = sum(r.telemetry.get("EG", 0.0) for r in rows) / n
    avg_trr = sum(r.telemetry.get("TRR", 0.0) for r in rows) / n
    avg_ri = sum(r.telemetry.get("RI", 0.0) for r in rows) / n
    avg_efs = sum(r.telemetry.get("EFS", 0.0) for r in rows) / n
    avg_align = sum(r.alignment_score for r in rows) / n
    avg_dur = sum(r.duration_ms for r in rows) / n

    hard_blocks = sum(1 for r in rows if r.hard_block)
    fallbacks = sum(1 for r in rows if r.fallback_triggered)

    return {
        "total_runs": n,
        "pass_rates": {
            "oqs": oqs_pass / n,
            "vsee": vsee_pass / n,
            "egs": egs_pass / n,
            "pipeline": pipe_pass / n
        },
        "averages": {
            "CS": avg_cs,
            "EG": avg_eg,
            "TRR": avg_trr,
            "RI": avg_ri,
            "EFS": avg_efs,
            "alignment_score": avg_align,
            "duration_ms": avg_dur
        },
        "counts": {
            "hard_blocks": hard_blocks,
            "fallbacks": fallbacks
        }
    }

def save_aggregated(agg_dir: Path, batch_id: str, data: Dict[str, Any]) -> Path:
    out_path = agg_dir / f"{batch_id}.summary.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return out_path

def save_report_md(report_dir: Path, batch_id: str, summary: Dict[str, Any], raw_path: Path, summary_path: Path) -> Path:
    out_path = report_dir / f"{batch_id}.md"
    lines = [
        f"# Research Batch Report — {batch_id}",
        "",
        "## Resumo",
        f"- Total de execuções: **{summary.get('total_runs', 0)}**",
        "",
        "## Taxas de aprovação",
        f"- OQS: **{summary['pass_rates']['oqs']:.2%}**",
        f"- VSEE: **{summary['pass_rates']['vsee']:.2%}**",
        f"- EGS: **{summary['pass_rates']['egs']:.2%}**",
        f"- Pipeline: **{summary['pass_rates']['pipeline']:.2%}**",
        "",
        "## Médias",
        f"- CS: **{summary['averages']['CS']:.4f}**",
        f"- EG: **{summary['averages']['EG']:.4f}**",
        f"- TRR: **{summary['averages']['TRR']:.4f}**",
        f"- RI: **{summary['averages']['RI']:.4f}**",
        f"- EFS: **{summary['averages']['EFS']:.4f}**",
        f"- Alignment: **{summary['averages']['alignment_score']:.4f}**",
        f"- Duração média (ms): **{summary['averages']['duration_ms']:.2f}**",
        "",
        "## Contadores",
        f"- Hard blocks: **{summary['counts']['hard_blocks']}**",
        f"- Fallbacks: **{summary['counts']['fallbacks']}**",
        "",
        "## Artefatos",
        f"- Raw: `{raw_path}`",
        f"- Summary: `{summary_path}`",
        ""
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path

def main() -> None:
    parser = argparse.ArgumentParser(description="Executa lote de pesquisa para OQS + MCI + VSEE + EGS")
    parser.add_argument("--matrix", default="research/experiments/scenario_matrix_v1.json", help="Caminho da matriz de cenários")
    parser.add_argument("--results", default="research/results", help="Diretório base de resultados")
    parser.add_argument("--max-scenarios", type=int, default=0, help="Limite de cenários (0 = todos)")
    parser.add_argument("--repetitions", type=int, default=0, help="Repetições por cenário (0 = usar default da matriz)")
    args = parser.parse_args()

    matrix_path = Path(args.matrix)
    results_base = Path(args.results)

    matrix = load_matrix(matrix_path)
    scenarios = iter_scenarios(matrix)

    if args.max_scenarios > 0:
        scenarios = scenarios[:args.max_scenarios]

    repetitions = args.repetitions or matrix.get("global_defaults", {}).get("repetitions_per_scenario", 1)

    dirs = ensure_dirs(results_base)
    batch_id = f"batch_{int(time.time())}"

    rows: List[ScenarioRunResult] = []
    for sc in scenarios:
        for rep_idx in range(repetitions):
            row = run_one_scenario(sc, rep_idx)
            rows.append(row)

    raw_path = save_raw_results(dirs["raw"], batch_id, rows)
    summary = aggregate(rows)
    summary_path = save_aggregated(dirs["aggregated"], batch_id, summary)
    report_path = save_report_md(dirs["reports"], batch_id, summary, raw_path, summary_path)

    print(f"[OK] batch_id={batch_id}")
    print(f"[OK] raw={raw_path}")
    print(f"[OK] summary={summary_path}")
    print(f"[OK] report={report_path}")

if __name__ == "__main__":
    main()
