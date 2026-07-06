# -*- coding: utf-8 -*-
"""
Auditoria determinística de inspirações → implementações.

Compara artefatos canônicos do diretório INSPIRAÇÕES/ com a codebase real
do OpenCode Ecosystem Core e classifica cada inspiração como:

- implemented
- partial
- absent
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class InspirationSpec:
    item_id: str
    title: str
    source_files: List[str]
    mandatory_paths: List[str]
    optional_evidence_paths: List[str] = field(default_factory=list)
    notes: str = ""


INSPIRATION_CATALOG: List[InspirationSpec] = [
    InspirationSpec(
        item_id="superhuman_scientific_core",
        title="Núcleo científico superhuman-like (INSPIRAÇÃO 1)",
        source_files=["INSPIRAÇÕES/INSPIRAÇÃO 1.txt"],
        mandatory_paths=[
            "specs/SPEC-021-superhuman-pipeline.md",
            "mci/evidence_graph.py",
            "mci/hypothesis_engine.py",
            "mci/experiment_designer.py",
            "mci/statistical_validator.py",
            "mci/adversarial_reviewer.py",
            "mci/confidence_calibrator.py",
            "mci/scientific_reporter.py",
            "benchmarks/scientific_reasoning/runner.py",
            "tests/test_scientific_superhuman.py",
        ],
        optional_evidence_paths=[
            "README.md",
            "mci/orchestration.py",
        ],
        notes="Blueprint de método científico completo, memória epistemológica e benchmark.",
    ),
    InspirationSpec(
        item_id="scientific_governance_pipeline_architecture",
        title="Arquitetura do Scientific Governance Pipeline (OQS→MCI→VSEE→EGS)",
        source_files=[
            "INSPIRAÇÕES/docs_SDD_scientific_governance_pipeline.md",
            "INSPIRAÇÕES/docs_SDD_pipeline_cientifico_governanca.md",
        ],
        mandatory_paths=[
            "mci/pipeline/scientific_governance_pipeline.py",
            "mci/oqs/__init__.py",
            "mci/vsee/router.py",
            "mci/egs/governance_analyzer.py",
            "schemas/optimal_question.schema.json",
            "schemas/vector_execution_decision.schema.json",
            "schemas/ethical_assessment.schema.json",
            "tests/test_scientific_governance_pipeline.py",
        ],
        optional_evidence_paths=[
            "README.md",
            "marceloclaro/orchestrator.py",
        ],
    ),
    InspirationSpec(
        item_id="scientific_governance_tdd_plan",
        title="Plano TDD do Scientific Governance Pipeline",
        source_files=[
            "INSPIRAÇÕES/docs_TDD_plan_scientific_governance_pipeline.md",
            "INSPIRAÇÕES/docs_TDD_plano_pipeline_cientifico_governanca.md",
        ],
        mandatory_paths=[
            "tests/test_scientific_governance_pipeline.py",
            "tests/test_scientific_superhuman.py",
            "tests/test_scientific_governance_contracts.py",
            "tests/fixtures/problems",
            "tests/fixtures/oqs_candidates",
            "tests/fixtures/vsee_routes",
            "tests/fixtures/egs_cases",
            "tests/fixtures/pipeline",
        ],
        optional_evidence_paths=[
            "schemas/optimal_question.schema.json",
            "schemas/vector_execution_decision.schema.json",
            "schemas/ethical_assessment.schema.json",
        ],
        notes="O plano TDD está refletido em testes, fixtures determinísticos e contract tests dos schemas centrais.",
    ),
    InspirationSpec(
        item_id="research_run_batch",
        title="Runner de lote de pesquisa (run_research_batch)",
        source_files=[
            "INSPIRAÇÕES/research_pipelines_run_research_batch.py",
            "INSPIRAÇÕES/research_pipelines_run_research_batch (1).py",
            "INSPIRAÇÕES/run_commands.sh",
        ],
        mandatory_paths=[
            "research/pipelines/run_research_batch.py",
            "research/experiments/scenario_matrix_v1.json",
            "tests/test_run_research_batch.py",
        ],
        optional_evidence_paths=[
            "README.md",
        ],
    ),
    InspirationSpec(
        item_id="research_analyze_batch",
        title="Análise estatística de lotes (analyze_research_batch)",
        source_files=["INSPIRAÇÕES/research_pipelines_analyze_research_batch.py"],
        mandatory_paths=[
            "research/pipelines/analyze_research_batch.py",
            "tests/test_analyze_research_batch.py",
        ],
        optional_evidence_paths=[
            "research/results",
        ],
        notes="O analisador estatístico de batch foi portado para o Core com scorecard de maturidade e comparação com baseline.",
    ),
    InspirationSpec(
        item_id="research_final_report_template",
        title="Template final de relatório de pesquisa integrado",
        source_files=["INSPIRAÇÕES/research_results_reports_final_report_template.md"],
        mandatory_paths=[
            "mci/scientific_reporter.py",
            "research/pipelines/run_research_batch.py",
            "research/pipelines/analyze_research_batch.py",
            "research/results/reports/final_report_template.md",
        ],
        optional_evidence_paths=[
            "README.md",
            "tests/test_run_research_batch.py",
        ],
        notes="O Core agora inclui template final integrado e gerador de relatório consolidado para a pipeline de research.",
    ),
    InspirationSpec(
        item_id="research_scenario_matrix",
        title="Matriz de cenários para pesquisa em lote",
        source_files=["INSPIRAÇÕES/research_experiments_scenario_matrix_v1.json"],
        mandatory_paths=[
            "research/experiments/scenario_matrix_v1.json",
            "research/pipelines/run_research_batch.py",
            "tests/test_run_research_batch.py",
        ],
        optional_evidence_paths=[
            "README.md",
        ],
    ),
    InspirationSpec(
        item_id="mira_presentation_system",
        title="Sistema MIRA / mira-animator / superfície de comandos",
        source_files=[
            "INSPIRAÇÕES/mira.md",
            "INSPIRAÇÕES/livro_mira.pdf",
            "INSPIRAÇÕES/livro_mira_branco.pdf",
        ],
        mandatory_paths=[
            "specs/SPEC-018-illustrations.md",
            "illustrations/mira_engine.py",
            "tests/test_illustrations.py",
            "agents/catalog/mira-new.md",
            "agents/catalog/mira-references.md",
            "agents/catalog/mira-animator.md",
            "agents/catalog/mira-animated-metaphor.md",
            "agents/catalog/mira-size-animator.md",
            "agents/catalog/mira-image.md",
            "agents/catalog/mira-get-videos.md",
            "agents/catalog/mira-extract.md",
            "agents/catalog/mira-planner.md",
            "agents/catalog/mira-copywriter.md",
            "agents/catalog/mira-builder.md",
            "agents/catalog/mira-validator.md",
            "agents/catalog/mira-visuals.md",
            "agents/catalog/mira-chart.md",
            "agents/catalog/mira-chart-race.md",
            "agents/catalog/mira-qrcode.md",
            "agents/catalog/mira-3d.md",
            "agents/catalog/mira-image-template.md",
            "agents/catalog/mira-survey.md",
            "agents/catalog/mira-squared.md",
            "agents/catalog/mira-vertical.md",
            "agents/catalog/mira-thirds.md",
        ],
        optional_evidence_paths=[
            "illustrations/mermaid_engine.py",
            "publishing/cover_designer.py",
            "README.md",
        ],
        notes="As regras centrais do MIRA e a superfície de comandos/agentes descrita no livro foram portadas para o catálogo do Core.",
    ),
]


def _rel_exists(rel_path: str) -> bool:
    return (ROOT / rel_path).exists()


def _dedup(values: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def audit_inspirations() -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []

    for spec in INSPIRATION_CATALOG:
        source_files = [p for p in spec.source_files if not p.endswith(":Zone.Identifier")]
        existing_mandatory = [p for p in spec.mandatory_paths if _rel_exists(p)]
        missing_mandatory = [p for p in spec.mandatory_paths if not _rel_exists(p)]
        optional_evidence = [p for p in spec.optional_evidence_paths if _rel_exists(p)]
        evidence_paths = _dedup(existing_mandatory + optional_evidence)

        mandatory_total = len(spec.mandatory_paths)
        mandatory_coverage_pct = round((len(existing_mandatory) / mandatory_total) * 100) if mandatory_total else 100

        if mandatory_total > 0 and len(existing_mandatory) == mandatory_total:
            status = "implemented"
        elif len(existing_mandatory) == 0:
            status = "absent"
        elif evidence_paths:
            status = "partial"
        else:
            status = "absent"

        if status == "implemented":
            observation = "Todos os caminhos mandatórios foram encontrados."
        elif status == "partial":
            observation = (
                f"Cobertura mandatória parcial: {len(existing_mandatory)}/{mandatory_total}."
            )
        else:
            observation = "Nenhum caminho mandatório correspondente foi encontrado."

        if spec.notes:
            observation = f"{observation} {spec.notes}".strip()

        items.append({
            "item_id": spec.item_id,
            "title": spec.title,
            "source_files": source_files,
            "mandatory_paths": list(spec.mandatory_paths),
            "evidence_paths": evidence_paths,
            "missing_paths": missing_mandatory,
            "mandatory_coverage_pct": mandatory_coverage_pct,
            "status": status,
            "observations": observation,
        })

    summary = {
        "total_items": len(items),
        "implemented": sum(1 for item in items if item["status"] == "implemented"),
        "partial": sum(1 for item in items if item["status"] == "partial"),
        "absent": sum(1 for item in items if item["status"] == "absent"),
    }
    summary["coverage_pct"] = round((summary["implemented"] / max(1, summary["total_items"])) * 100)

    return {
        "root": str(ROOT),
        "summary": summary,
        "items": items,
    }


def render_inspiration_audit_markdown(report: Dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Auditoria de Inspirações",
        "",
        f"- Total de itens: **{summary['total_items']}**",
        f"- Implementadas: **{summary['implemented']}**",
        f"- Parciais: **{summary['partial']}**",
        f"- Ausentes: **{summary['absent']}**",
        f"- Cobertura integral: **{summary['coverage_pct']}%**",
        "- Status válidos: `implemented`, `partial`, `absent`",
        "",
        "| item_id | status | cobertura mandatória | evidências | lacunas |",
        "|---|---|---:|---:|---:|",
    ]

    for item in report["items"]:
        lines.append(
            f"| {item['item_id']} | {item['status']} | {item['mandatory_coverage_pct']}% | "
            f"{len(item['evidence_paths'])} | {len(item['missing_paths'])} |"
        )

    lines.extend(["", "## Detalhamento", ""])
    for item in report["items"]:
        lines.append(f"### {item['item_id']} — {item['status']}")
        lines.append("")
        lines.append(f"**Título:** {item['title']}")
        lines.append("")
        if item["source_files"]:
            lines.append("**Fontes de inspiração:**")
            for path in item["source_files"]:
                lines.append(f"- `{path}`")
            lines.append("")
        if item["evidence_paths"]:
            lines.append("**Evidências encontradas:**")
            for path in item["evidence_paths"]:
                lines.append(f"- `{path}`")
            lines.append("")
        if item["missing_paths"]:
            lines.append("**Lacunas / ausências:**")
            for path in item["missing_paths"]:
                lines.append(f"- `{path}`")
            lines.append("")
        lines.append(f"**Observações:** {item['observations']}")
        lines.append("")

    return "\n".join(lines)


__all__ = [
    "InspirationSpec",
    "INSPIRATION_CATALOG",
    "audit_inspirations",
    "render_inspiration_audit_markdown",
]
