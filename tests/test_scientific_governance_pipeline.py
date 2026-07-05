# -*- coding: utf-8 -*-
from marceloclaro.orchestrator import MarceloClaroOrchestrator

def test_pipeline_end_to_end_success():
    orch = MarceloClaroOrchestrator(auto_load_agents=False)
    
    context = {
        "validated_shortcut": True,
        "risk": 0.1,
        "risk_threshold": 0.5,
        "expected_fidelity": 0.95,
        "min_fidelity": 0.90,
        "expected_cost_gain": 1.5,
        "p_value": 0.02,
        "effect_size": 0.45,
        "confidence_interval": [0.20, 0.60],
        "reproducibility_score": 0.92,
        "expected_behavior": {
            "egs_should_decide": "approve"
        }
    }
    
    result = orch.run_scientific_governance(
        problem_text="A intervenção X reduz erro médio em classificação?",
        context=context
    )
    
    assert result["pipeline_success"] is True
    assert result["status"] == "success"
    assert "claim_id" in result["scientific_claim"]
    assert result["scientific_claim"]["final_verdict"] == "supported"
    assert result["vsee"]["chosen_path"] == "vector"
    assert result["vsee"]["fallback_triggered"] is False
    assert result["egs"]["decision"] == "approve"


def test_pipeline_vsee_fallback_does_not_abort_flow():
    orch = MarceloClaroOrchestrator(auto_load_agents=False)
    
    context = {
        "validated_shortcut": True,
        "risk": 0.1,
        "risk_threshold": 0.5,
        "expected_fidelity": 0.95,
        "min_fidelity": 0.90,
        "expected_cost_gain": 1.5,
        "simulate_vector_exception": True,
        "expected_behavior": {
            "egs_should_decide": "approve"
        }
    }
    
    result = orch.run_scientific_governance(
        problem_text="Otimizar carregamento de dados com cache local.",
        context=context
    )
    
    # Fallback to original should succeed
    assert result["pipeline_success"] is True
    assert result["status"] == "success"
    assert result["vsee"]["chosen_path"] == "original"
    assert result["vsee"]["fallback_triggered"] is True


def test_pipeline_egs_block_prevents_final_approval():
    orch = MarceloClaroOrchestrator(auto_load_agents=False)
    
    context = {
        "risk_profile": {
            "ethical_risk": "high"
        },
        "expected_behavior": {
            "hard_block_expected": True,
            "egs_should_decide": "block"
        }
    }
    
    result = orch.run_scientific_governance(
        problem_text="Proposta técnica que pode introduzir discriminação algorítmica indireta.",
        context=context
    )
    
    # Technical elements might succeed, but EGS block forces final blocked status
    assert result["pipeline_success"] is False
    assert result["status"] == "blocked"
    assert result["egs"]["decision"] == "block"
    assert result["egs"]["hard_block"] is True


def test_pipeline_report_contains_sections():
    orch = MarceloClaroOrchestrator(auto_load_agents=False)
    
    result = orch.run_scientific_governance(
        problem_text="Análise de impacto social das recomendações autônomas.",
        context={}
    )
    
    report = result["report_tex"]
    assert "Scientific Claim Report" in report
    assert "Hypotheses" in report
    assert "Design" in report
    assert "Results" in report
    assert "Adversarial Findings" in report
    assert "Verdict" in report
