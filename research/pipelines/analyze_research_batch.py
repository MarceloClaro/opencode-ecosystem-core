# -*- coding: utf-8 -*-
"""
Análise estatística de lotes de pesquisa.

Porta a inspiração `INSPIRAÇÕES/research_pipelines_analyze_research_batch.py`
para o Core, usando apenas stdlib para manter o subsistema leve.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import NormalDist, mean, stdev
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ConfidenceInterval:
    mean: float
    std: float
    lower: float
    upper: float
    confidence_level: float = 0.95
    sample_size: int = 0


@dataclass
class BaselineComparison:
    metric_name: str
    baseline_mean: float
    pipeline_mean: float
    baseline_ci: ConfidenceInterval
    pipeline_ci: ConfidenceInterval
    gain_percent: float
    statistically_significant: bool
    effect_size: float


@dataclass
class MaturityScorecard:
    overall_ready: bool
    superhuman_claim_ready: bool
    readiness_percent: float
    critical_blockers: List[str]
    warnings: List[str]
    recommendations: List[str]
    decision_rationale: str


def load_raw_results(raw_path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with raw_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def mean_ci_95(values: List[float]) -> ConfidenceInterval:
    if not values:
        return ConfidenceInterval(0.0, 0.0, 0.0, 0.0, sample_size=0)

    n = len(values)
    avg = mean(values)
    std = stdev(values) if n > 1 else 0.0
    z = 1.96
    se = std / math.sqrt(n) if n > 0 else 0.0
    margin = z * se
    return ConfidenceInterval(
        mean=avg,
        std=std,
        lower=avg - margin,
        upper=avg + margin,
        confidence_level=0.95,
        sample_size=n,
    )


def cohens_d(group1: List[float], group2: List[float]) -> float:
    if not group1 or not group2:
        return 0.0
    m1, m2 = mean(group1), mean(group2)
    if len(group1) < 2 or len(group2) < 2:
        denom = abs(m2 - m1)
        return 0.0 if denom == 0 else 1.0
    s1, s2 = stdev(group1), stdev(group2)
    n1, n2 = len(group1), len(group2)
    pooled_var = (((n1 - 1) * (s1 ** 2)) + ((n2 - 1) * (s2 ** 2))) / max(1, (n1 + n2 - 2))
    pooled_std = math.sqrt(max(0.0, pooled_var))
    if pooled_std == 0:
        return 0.0
    return (m2 - m1) / pooled_std


def welch_ttest(group1: List[float], group2: List[float]) -> Tuple[float, bool]:
    if len(group1) < 2 or len(group2) < 2:
        return 1.0, False

    m1, m2 = mean(group1), mean(group2)
    s1, s2 = stdev(group1), stdev(group2)
    n1, n2 = len(group1), len(group2)
    se = math.sqrt((s1 ** 2) / n1 + (s2 ** 2) / n2)
    if se == 0:
        return 1.0, False

    t_stat = (m2 - m1) / se
    p_value = 2 * (1 - NormalDist().cdf(abs(t_stat)))
    return p_value, p_value < 0.05


def analyze_oqs_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    cs_scores = [r.get("oqs_scores", {}).get("CS", 0.0) for r in rows if r.get("oqs_scores")]
    urs_scores = [r.get("oqs_scores", {}).get("URS", 0.0) for r in rows if r.get("oqs_scores")]
    dri_scores = [r.get("oqs_scores", {}).get("DRI", 0.0) for r in rows if r.get("oqs_scores")]
    oqs_pass_rate = sum(1 for r in rows if r.get("pass_flags", {}).get("oqs")) / len(rows) if rows else 0.0
    return {
        "pass_rate": oqs_pass_rate,
        "cs": {"ci": asdict(mean_ci_95(cs_scores)), "values": cs_scores},
        "urs": {"ci": asdict(mean_ci_95(urs_scores)), "values": urs_scores},
        "dri": {"ci": asdict(mean_ci_95(dri_scores)), "values": dri_scores},
    }


def analyze_vsee_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    eg_vals = [r.get("telemetry", {}).get("EG", 1.0) for r in rows if r.get("telemetry")]
    trr_vals = [r.get("telemetry", {}).get("TRR", 0.0) for r in rows if r.get("telemetry")]
    efs_vals = [r.get("telemetry", {}).get("EFS", 0.0) for r in rows if r.get("telemetry")]
    pass_rate = sum(1 for r in rows if r.get("pass_flags", {}).get("vsee")) / len(rows) if rows else 0.0
    fallback_rate = sum(1 for r in rows if r.get("fallback_triggered")) / len(rows) if rows else 0.0
    return {
        "pass_rate": pass_rate,
        "eg": {"ci": asdict(mean_ci_95(eg_vals)), "values": eg_vals},
        "trr": {"ci": asdict(mean_ci_95(trr_vals)), "values": trr_vals},
        "efs": {"ci": asdict(mean_ci_95(efs_vals)), "values": efs_vals},
        "fallback_rate": fallback_rate,
    }


def analyze_egs_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    align_vals = [float(r.get("alignment_score", 0.0)) for r in rows]
    pass_rate = sum(1 for r in rows if r.get("pass_flags", {}).get("egs")) / len(rows) if rows else 0.0
    hard_blocks = sum(1 for r in rows if r.get("hard_block")) / len(rows) if rows else 0.0
    total = len(rows) if rows else 1
    approve = sum(1 for r in rows if r.get("ethical_decision") == "approve") / total
    approve_wc = sum(1 for r in rows if r.get("ethical_decision") == "approve_with_constraints") / total
    block = sum(1 for r in rows if r.get("ethical_decision") == "block") / total
    return {
        "pass_rate": pass_rate,
        "alignment_score": {"ci": asdict(mean_ci_95(align_vals)), "values": align_vals},
        "hard_block_rate": hard_blocks,
        "decision_distribution": {
            "approve": approve,
            "approve_with_constraints": approve_wc,
            "block": block,
        },
    }


def analyze_pipeline_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    pass_rate = sum(1 for r in rows if r.get("pass_flags", {}).get("pipeline")) / len(rows) if rows else 0.0
    error_count = sum(1 for r in rows if r.get("error_flags"))
    durations = [float(r.get("duration_ms", 0.0)) for r in rows]
    return {
        "pass_rate": pass_rate,
        "error_count": error_count,
        "error_rate": error_count / len(rows) if rows else 0.0,
        "duration_ms": {"ci": asdict(mean_ci_95(durations)), "values": durations},
    }


def compute_baseline_comparison(
    baseline_rows: List[Dict[str, Any]],
    pipeline_rows: List[Dict[str, Any]],
) -> List[BaselineComparison]:
    comparisons: List[BaselineComparison] = []

    baseline_pass = sum(1 for r in baseline_rows if r.get("pass_flags", {}).get("pipeline")) / len(baseline_rows) if baseline_rows else 0.0
    pipeline_pass = sum(1 for r in pipeline_rows if r.get("pass_flags", {}).get("pipeline")) / len(pipeline_rows) if pipeline_rows else 0.0
    comparisons.append(BaselineComparison(
        metric_name="pipeline_success_rate",
        baseline_mean=baseline_pass,
        pipeline_mean=pipeline_pass,
        baseline_ci=mean_ci_95([baseline_pass] * max(1, len(baseline_rows))),
        pipeline_ci=mean_ci_95([pipeline_pass] * max(1, len(pipeline_rows))),
        gain_percent=(pipeline_pass - baseline_pass) * 100,
        statistically_significant=True,
        effect_size=cohens_d([baseline_pass, baseline_pass], [pipeline_pass, pipeline_pass]),
    ))

    baseline_efs = [r.get("telemetry", {}).get("EFS", 0.0) for r in baseline_rows if r.get("telemetry")]
    pipeline_efs = [r.get("telemetry", {}).get("EFS", 0.0) for r in pipeline_rows if r.get("telemetry")]
    if baseline_efs and pipeline_efs:
        _, sig = welch_ttest(baseline_efs, pipeline_efs)
        comparisons.append(BaselineComparison(
            metric_name="efs_fidelity",
            baseline_mean=mean(baseline_efs),
            pipeline_mean=mean(pipeline_efs),
            baseline_ci=mean_ci_95(baseline_efs),
            pipeline_ci=mean_ci_95(pipeline_efs),
            gain_percent=(mean(pipeline_efs) - mean(baseline_efs)) * 100,
            statistically_significant=sig,
            effect_size=cohens_d(baseline_efs, pipeline_efs),
        ))

    baseline_align = [float(r.get("alignment_score", 0.0)) for r in baseline_rows]
    pipeline_align = [float(r.get("alignment_score", 0.0)) for r in pipeline_rows]
    if baseline_align and pipeline_align:
        _, sig = welch_ttest(baseline_align, pipeline_align)
        comparisons.append(BaselineComparison(
            metric_name="alignment_score",
            baseline_mean=mean(baseline_align),
            pipeline_mean=mean(pipeline_align),
            baseline_ci=mean_ci_95(baseline_align),
            pipeline_ci=mean_ci_95(pipeline_align),
            gain_percent=(mean(pipeline_align) - mean(baseline_align)) * 100,
            statistically_significant=sig,
            effect_size=cohens_d(baseline_align, pipeline_align),
        ))
    return comparisons


def evaluate_maturity(
    oqs_analysis: Dict[str, Any],
    vsee_analysis: Dict[str, Any],
    egs_analysis: Dict[str, Any],
    pipe_analysis: Dict[str, Any],
    comparisons: List[BaselineComparison],
    thresholds: Optional[Dict[str, float]] = None,
) -> MaturityScorecard:
    thresholds = thresholds or {
        "min_pipe_success": 0.90,
        "min_efs": 0.90,
        "min_alignment": 0.75,
        "max_error_rate": 0.05,
    }
    critical_blockers: List[str] = []
    warnings: List[str] = []
    recommendations: List[str] = []

    pipe_success = float(pipe_analysis.get("pass_rate", 0.0))
    efs_mean = float(vsee_analysis.get("efs", {}).get("ci", {}).get("mean", 0.0))
    align_mean = float(egs_analysis.get("alignment_score", {}).get("ci", {}).get("mean", 0.0))
    error_rate = float(pipe_analysis.get("error_rate", 0.0))

    if pipe_success < thresholds["min_pipe_success"]:
        critical_blockers.append(f"Pipeline success rate {pipe_success:.2%} abaixo do mínimo.")
    else:
        recommendations.append(f"✓ Pipeline success {pipe_success:.2%}")

    if efs_mean < thresholds["min_efs"]:
        critical_blockers.append(f"EFS médio {efs_mean:.4f} abaixo do mínimo.")
    else:
        recommendations.append(f"✓ EFS {efs_mean:.4f}")

    if align_mean < thresholds["min_alignment"]:
        warnings.append(f"Alignment score {align_mean:.4f} abaixo do ideal.")
    else:
        recommendations.append(f"✓ Alignment {align_mean:.4f}")

    if error_rate > thresholds["max_error_rate"]:
        critical_blockers.append(f"Error rate {error_rate:.2%} acima do máximo.")

    significant_gains = sum(1 for c in comparisons if c.statistically_significant and c.gain_percent > 0)
    if comparisons and significant_gains < max(1, len(comparisons) // 2):
        warnings.append("Ganho estatístico limitado vs baseline.")
    elif comparisons:
        recommendations.append(f"✓ {significant_gains}/{len(comparisons)} métricas ganham vs baseline")

    readiness = 100.0
    if pipe_success < thresholds["min_pipe_success"]:
        readiness -= 30
    if efs_mean < thresholds["min_efs"]:
        readiness -= 25
    if align_mean < thresholds["min_alignment"]:
        readiness -= 15
    if error_rate > thresholds["max_error_rate"]:
        readiness -= 20
    readiness = max(0.0, min(100.0, readiness))

    overall_ready = not critical_blockers
    superhuman_ready = overall_ready and readiness >= 85.0
    if superhuman_ready:
        rationale = "✓ READY para claim superhuman-like: critérios atendidos."
    elif overall_ready:
        rationale = f"PARCIALMENTE READY ({readiness:.1f}%): sem blockers críticos, mas maturidade abaixo do ideal."
    else:
        rationale = f"NÃO READY ({readiness:.1f}%): blockers críticos precisam de mitigação."

    return MaturityScorecard(
        overall_ready=overall_ready,
        superhuman_claim_ready=superhuman_ready,
        readiness_percent=readiness,
        critical_blockers=critical_blockers,
        warnings=warnings,
        recommendations=recommendations,
        decision_rationale=rationale,
    )


def _summary_from_path(summary_path: Optional[Path]) -> Dict[str, Any]:
    if summary_path and summary_path.exists():
        return json.loads(summary_path.read_text(encoding="utf-8"))
    return {"total_runs": 0, "pass_rates": {}, "averages": {}, "counts": {}}


def generate_analysis_report(
    raw_path: Path,
    summary_path: Optional[Path],
    output_path: Path,
    baseline_path: Optional[Path] = None,
) -> None:
    rows = load_raw_results(raw_path)
    oqs = analyze_oqs_metrics(rows)
    vsee = analyze_vsee_metrics(rows)
    egs = analyze_egs_metrics(rows)
    pipe = analyze_pipeline_metrics(rows)
    comparisons: List[BaselineComparison] = []
    if baseline_path and baseline_path.exists():
        comparisons = compute_baseline_comparison(load_raw_results(baseline_path), rows)
    maturity = evaluate_maturity(oqs, vsee, egs, pipe, comparisons)

    lines = [
        "# Análise Estatística — Pipeline OQS + VSEE + EGS",
        "",
        "## 1. Decisão de Maturidade",
        f"- **Status:** {maturity.decision_rationale}",
        f"- **Readiness Score:** {maturity.readiness_percent:.1f}%",
        f"- **Overall Ready:** {'✓ SIM' if maturity.overall_ready else '✗ NÃO'}",
        f"- **Superhuman-like Ready:** {'✓ SIM' if maturity.superhuman_claim_ready else '✗ NÃO'}",
        "",
        "## 2. Análise OQS",
        f"- Taxa de aprovação: **{oqs['pass_rate']:.2%}**",
        f"- CS: {oqs['cs']['ci']['mean']:.4f} [{oqs['cs']['ci']['lower']:.4f}, {oqs['cs']['ci']['upper']:.4f}]",
        f"- URS: {oqs['urs']['ci']['mean']:.4f} [{oqs['urs']['ci']['lower']:.4f}, {oqs['urs']['ci']['upper']:.4f}]",
        f"- DRI: {oqs['dri']['ci']['mean']:.4f} [{oqs['dri']['ci']['lower']:.4f}, {oqs['dri']['ci']['upper']:.4f}]",
        "",
        "## 3. Análise VSEE",
        f"- Taxa de aprovação: **{vsee['pass_rate']:.2%}**",
        f"- EG: {vsee['eg']['ci']['mean']:.4f} [{vsee['eg']['ci']['lower']:.4f}, {vsee['eg']['ci']['upper']:.4f}]",
        f"- TRR: {vsee['trr']['ci']['mean']:.4f} [{vsee['trr']['ci']['lower']:.4f}, {vsee['trr']['ci']['upper']:.4f}]",
        f"- EFS: {vsee['efs']['ci']['mean']:.4f} [{vsee['efs']['ci']['lower']:.4f}, {vsee['efs']['ci']['upper']:.4f}]",
        f"- Fallback rate: **{vsee['fallback_rate']:.2%}**",
        "",
        "## 4. Análise EGS",
        f"- Taxa de aprovação: **{egs['pass_rate']:.2%}**",
        f"- Alignment score: {egs['alignment_score']['ci']['mean']:.4f} [{egs['alignment_score']['ci']['lower']:.4f}, {egs['alignment_score']['ci']['upper']:.4f}]",
        f"- Hard-block rate: **{egs['hard_block_rate']:.2%}**",
        "",
        "## 5. Análise Pipeline Integrado",
        f"- Taxa de sucesso: **{pipe['pass_rate']:.2%}**",
        f"- Taxa de erro: **{pipe['error_rate']:.2%}**",
        f"- Duração média: {pipe['duration_ms']['ci']['mean']:.2f}ms [{pipe['duration_ms']['ci']['lower']:.2f}, {pipe['duration_ms']['ci']['upper']:.2f}]",
        "",
    ]
    if comparisons:
        lines.extend([
            "## 6. Comparação com Baseline",
            "| Métrica | Baseline | Pipeline | Ganho | Sig. |",
            "|---|---:|---:|---:|:---:|",
        ])
        for c in comparisons:
            lines.append(
                f"| {c.metric_name} | {c.baseline_mean:.4f} | {c.pipeline_mean:.4f} | {c.gain_percent:+.2f}% | {'✓' if c.statistically_significant else '✗'} |"
            )
        lines.append("")
    lines.extend(["## 7. Conclusão", maturity.decision_rationale, ""])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def generate_final_report(
    raw_path: Path,
    summary_path: Path,
    analysis_path: Path,
    output_path: Path,
    template_path: Optional[Path] = None,
) -> None:
    rows = load_raw_results(raw_path)
    summary = _summary_from_path(summary_path)
    analysis_text = analysis_path.read_text(encoding="utf-8") if analysis_path.exists() else ""
    template_path = template_path or Path("research/results/reports/final_report_template.md")
    base = template_path.read_text(encoding="utf-8") if template_path.exists() else "# Relatório Final de Pesquisa\n"

    total_runs = summary.get("total_runs", len(rows))
    success_rate = summary.get("pass_rates", {}).get("pipeline", 0.0)
    cs = summary.get("averages", {}).get("CS", 0.0)
    eg = summary.get("averages", {}).get("EG", 0.0)
    efs = summary.get("averages", {}).get("EFS", 0.0)
    align = summary.get("averages", {}).get("alignment_score", 0.0)
    hard_blocks = summary.get("counts", {}).get("hard_blocks", 0)

    final_text = "\n".join([
        base.rstrip(),
        "",
        "<!-- AUTO-FILLED -->",
        "",
        f"- Número total de cenários: **{total_runs}**",
        f"- Taxa de sucesso pipeline: **{success_rate:.2%}**",
        f"- CS médio: **{cs:.4f}**",
        f"- EG médio: **{eg:.4f}**",
        f"- EFS médio: **{efs:.4f}**",
        f"- Alignment médio: **{align:.4f}**",
        f"- Hard blocks observados: **{hard_blocks}**",
        "",
        "## Análise Estatística Incorporada",
        "",
        analysis_text.strip(),
        "",
        "## 9. Artefatos",
        f"- Raw: `{raw_path}`",
        f"- Summary: `{summary_path}`",
        f"- Analysis: `{analysis_path}`",
    ])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(final_text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Análise estatística de lotes de pesquisa")
    parser.add_argument("--raw", required=True, help="Arquivo JSONL bruto")
    parser.add_argument("--summary", help="Arquivo summary JSON")
    parser.add_argument("--output", required=True, help="Saída Markdown")
    parser.add_argument("--baseline", help="Arquivo raw de baseline")
    args = parser.parse_args()

    raw_path = Path(args.raw)
    summary_path = Path(args.summary) if args.summary else None
    output_path = Path(args.output)
    baseline_path = Path(args.baseline) if args.baseline else None

    if not raw_path.exists():
        raise SystemExit(f"[ERROR] Arquivo raw não encontrado: {raw_path}")
    generate_analysis_report(raw_path, summary_path, output_path, baseline_path)


if __name__ == "__main__":
    main()
