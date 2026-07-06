# -*- coding: utf-8 -*-
"""
Orquestração do Ciclo Científico com EvidenceGraph.

Fluxo:
  Hypothesis → Experiment → Statistics → Adversarial Review → Calibration → Report → EvidenceGraph
"""

import os
import json
from typing import Dict, Any, Optional

from .hypothesis_engine import generate_hypothesis
from .experiment_designer import design_experiment
from .statistical_validator import validate_statistics
from .adversarial_reviewer import run_adversarial_review
from .confidence_calibrator import calibrate_confidence
from .scientific_reporter import build_report
from .evidence_graph import get_global_evidence_graph

SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "schemas",
    "scientific_claim.schema.json"
)


class ScientificRunResult:
    """Resultado do ciclo científico completo."""

    def __init__(
        self,
        claim: Dict[str, Any],
        report_tex: str,
        graph_id: Optional[str] = None
    ):
        self.claim = claim
        self.report_tex = report_tex
        self.graph_id = graph_id


def run_scientific_cycle(
    question: str,
    context: Dict[str, Any] = None
) -> ScientificRunResult:
    """
    Executa o ciclo científico completo com integração ao EvidenceGraph.

    Pipeline:
    1. HypothesisEngine → gera hipóteses falsificáveis
    2. ExperimentDesigner → power analysis + confounders
    3. StatisticalValidator → testes + Bayes Factor + correções
    4. AdversarialReviewer → tenta refutar
    5. ConfidenceCalibrator → Brier + ECE + abstention
    6. ScientificReporter → LaTeX Qualis A1
    7. EvidenceGraph → registra histórico epistemológico
    """
    if context is None:
        context = {}

    # 1. Hipóteses
    claim = generate_hypothesis(question=question, context=context)

    # 2. Desenho experimental
    claim = design_experiment(claim=claim, context=context)

    # 3. Validação estatística
    claim = validate_statistics(claim=claim, context=context)

    # 4. Revisão adversarial
    claim = run_adversarial_review(claim=claim, context=context)

    # 5. Calibração de confiança
    claim = calibrate_confidence(claim=claim, context=context)

    # 6. Relatório
    report_tex = build_report(claim=claim, context=context)

    # 7. Registro no EvidenceGraph (memória epistemológica)
    graph = get_global_evidence_graph()
    graph_id = graph.register_claim(claim)

    # Adiciona evidências baseadas no veredito
    if claim["final_verdict"] == "supported":
        graph.add_evidence(
            graph_id,
            evidence_type="statistical_support",
            description=(
                f"Evidência estatística: p={claim.get('p_value')}, "
                f"d={claim.get('effect_size')}, "
                f"BF10={claim.get('bayes_factor', {}).get('BF10', 'N/A')}"
            ),
            confidence_impact=0.3,
            source="StatisticalValidator"
        )
    elif claim["final_verdict"] == "refuted":
        graph.add_evidence(
            graph_id,
            evidence_type="statistical_refutation",
            description=(
                f"Refutação estatística: p={claim.get('p_value')}, "
                f"d={claim.get('effect_size')}"
            ),
            confidence_impact=-0.3,
            source="StatisticalValidator"
        )

    # Adiciona achados adversariais como evidência contra
    for finding in claim.get("adversarial_findings", []):
        if finding.startswith("ALERTA:"):
            graph.add_evidence(
                graph_id,
                evidence_type="adversarial_warning",
                description=finding,
                confidence_impact=-0.15,
                source="AdversarialReviewer"
            )

    # Validação do schema (se existir)
    if os.path.exists(SCHEMA_PATH):
        try:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema = json.load(f)
            import jsonschema
            jsonschema.validate(instance=claim, schema=schema)
        except Exception:
            pass  # Schema validation não bloqueia

    return ScientificRunResult(
        claim=claim,
        report_tex=report_tex,
        graph_id=graph_id
    )
