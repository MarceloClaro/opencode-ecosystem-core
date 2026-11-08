#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Piloto sintético do protocolo de avaliação de eficácia (R920).

Não usa LLM, OASIS ou dados humanos. Produz perguntas e objeções para ajuste
do protocolo; não mede aprendizagem.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from academic.adversarial_research.simulation import (
    STAGES, SCENARIOS, plan_simulation, run_simulation, render_simulation_report,
)

PROTO = ROOT / "educacao_quantica_bohm" / "livro_pixel" / "AVALIACAO_EFICACIA.md"
TRILHAS = ROOT / "educacao_quantica_bohm" / "livro_pixel" / "TRILHAS_NIVEIS.md"
OUT = ROOT / "outputs" / "piloto-avaliacao"
OUT.mkdir(parents=True, exist_ok=True)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    fonte = {
        "source_id": "s1",
        "path": str(PROTO),
        "locator": "protocolo completo",
        "sha256": sha(PROTO),
        "verification": "not_checked",
    }
    fonte2 = {
        "source_id": "s2",
        "path": str(TRILHAS),
        "locator": "trilhas por nível",
        "sha256": sha(TRILHAS),
        "verification": "not_checked",
    }
    project = {
        "research_id": "avaliacao-eficacia-livro",
        "spec_id": "SPEC-BOHM-PIXEL-001",
        "artifact_path": str(PROTO),
        "problem": "O protocolo de avaliação de eficácia é executável, claro e analisável antes da coleta?",
        "objectives": [
            "Ensaiar o protocolo com perfis e cenários sintéticos.",
            "Identificar lacunas de método, instrumentos, ética e análise.",
            "Ajustar o protocolo antes do CEP; não medir aprendizagem.",
        ],
        "study_type": "protocol",
        "context": {
            "humans": False,
            "personal_data": False,
            "control_group": True,
            "synthetic": True,
        },
        "sources": [fonte, fonte2],
        "claims": [
            {
                "claim_id": "c1",
                "statement": "O protocolo é executável em 12 semanas, com instrumentos claros e análise pré-registrada.",
                "claim_type": "inferential",
                "source_refs": ["s1", "s2"],
                "evidence_status": "proposed",
                "limitations": ["Ainda não executado com estudantes reais; requer CEP."],
                "reviewer_agent_ids": [],
                "attributes": {},
            },
            {
                "claim_id": "c2",
                "statement": "O desenho com 440 estudantes detecta d=0,40 com poder de 80% e ICC=0,05.",
                "claim_type": "inferential",
                "source_refs": ["s1"],
                "evidence_status": "proposed",
                "limitations": ["Cálculo depende de ICC e taxa de atrito assumidos."],
                "reviewer_agent_ids": [],
                "attributes": {},
            },
            {
                "claim_id": "c3",
                "statement": "ANCOVA com pré-teste e erros cluster-robustos é adequada ao desenho por turma.",
                "claim_type": "inferential",
                "source_refs": ["s1"],
                "evidence_status": "proposed",
                "limitations": ["Requer verificação de pressupostos e dados faltantes."],
                "reviewer_agent_ids": [],
                "attributes": {},
            },
            {
                "claim_id": "c4",
                "statement": "O estudo exige CEP, consentimento dos responsáveis e assentimento dos estudantes.",
                "claim_type": "normative",
                "source_refs": ["s1"],
                "evidence_status": "reported",
                "limitations": [],
                "reviewer_agent_ids": [],
                "attributes": {},
            },
        ],
    }
    cases = []
    for stage in STAGES:
        grupo = (
            "cientistas_metodo" if stage == "metodologia"
            else "cientistas_resultados" if stage in {"analise", "resultados"}
            else "banca_interdisciplinar"
        )
        for scenario in SCENARIOS:
            cases.append({
                "case_id": f"{stage}-{scenario}",
                "stage": stage,
                "group": grupo,
                "scenario": scenario,
                "rounds": 2,
                "agents": 6,
            })
    plan = plan_simulation(project, cases=cases, seed=42,
                            limits={"max_rounds": 64, "max_actions": 512,
                                    "timeout_seconds": 30})
    result = run_simulation(plan)
    (OUT / "plano.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "resultado.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "RELATORIO_PILOTO.md").write_text(render_simulation_report(result), encoding="utf-8")
    resumo = {
        "status": result["status"],
        "usage": result["usage"],
        "review_status": result["base_review"]["review_status"],
        "unresolved_objections": len(result["unresolved_objection_ids"]),
        "unresolved_gaps": len(result["unresolved_gaps"]),
        "questions": sum(len(c["questions"]) for c in result["cases"]),
        "trajectory_sha256": result["trajectory_sha256"],
        "safeguards": result.get("safeguards"),
    }
    (OUT / "RESUMO.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
