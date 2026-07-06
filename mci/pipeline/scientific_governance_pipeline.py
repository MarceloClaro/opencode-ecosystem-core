# -*- coding: utf-8 -*-
"""
Pipeline Científico com Governança (OQS → MCI → VSEE → EGS).

Versão 2.0 — Integração com EvidenceGraph e módulos avançados.
"""

from typing import Dict, Any, Callable
from mci.oqs import run_oqs_scanner
from mci.orchestration import run_scientific_cycle
from mci.vsee import run_vsee_router
from mci.egs import run_egs_scanner


def run_scientific_governance_pipeline(
    problem_text: str,
    executor_fn: Callable = None,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Executa o pipeline completo: OQS → MCI → VSEE → EGS.

    Args:
        problem_text: Texto do problema/questão de pesquisa
        executor_fn: Função de execução (para VSEE)
        context: Contexto com parâmetros de cada etapa

    Returns:
        Dict com resultados de todas as etapas
    """
    if context is None:
        context = {}

    # 1. OQS — Optimal Question Scanner
    oqs_res = run_oqs_scanner(problem_text, context)
    selected_question = oqs_res["selected_question"]

    # 2. MCI Scientific Core (Hypothesis → Stats → Adversarial → EvidenceGraph)
    scientific_res = run_scientific_cycle(selected_question, context)
    claim = scientific_res.claim
    report_tex = scientific_res.report_tex
    graph_id = scientific_res.graph_id

    # 3. VSEE — Vector Shortcut Execution Engine
    if executor_fn:
        vsee_res = run_vsee_router(executor_fn, context)
    else:
        vsee_res = {
            "chosen_path": "original",
            "policy_reason": "No executor provided",
            "result_data": {},
        }

    # 4. EGS — Ethical Governance Scanner
    check_content = (
        f"{claim.get('hypothesis', '')} "
        f"{claim.get('null_hypothesis', '')} "
        f"{vsee_res.get('result_data', {}).get('data', '')}"
    )
    egs_res = run_egs_scanner(check_content, context)

    # Decisão final
    pipeline_success = oqs_res.get("pass", False) and egs_res.get("decision") != "block"

    return {
        "problem_id": oqs_res.get("problem_id", "unknown"),
        "oqs": oqs_res,
        "scientific_claim": claim,
        "report_tex": report_tex,
        "evidence_graph_id": graph_id,
        "vsee": vsee_res,
        "egs": egs_res,
        "pipeline_success": pipeline_success,
        "status": (
            "blocked" if egs_res.get("decision") == "block"
            else "success" if pipeline_success
            else "failed"
        ),
        "version": "2.0.0",
    }
