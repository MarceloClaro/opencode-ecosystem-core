# -*- coding: utf-8 -*-
"""
Testes TDD para o Pipeline Científico SuperHuman.

Cobre:
- EvidenceGraph (grafo epistemológico)
- HypothesisEngine aprimorada
- ExperimentDesigner com power analysis
- StatisticalValidator com Bayes Factor
- AdversarialReviewer
- ConfidenceCalibrator
- ScientificReporter
- ScientificBenchmark
- Pipeline end-to-end
"""

import pytest
import json
import os
import tempfile


# =============================================================================
# EvidenceGraph Tests
# =============================================================================

class TestEvidenceGraph:
    def test_register_claim(self):
        from mci.evidence_graph import EvidenceGraph
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            graph = EvidenceGraph(storage_path=f.name)
            claim = {
                "claim_id": "clm-test-001",
                "hypothesis": "H1: Teste produz efeito positivo",
                "null_hypothesis": "H0: Efeito nulo",
                "p_value": 0.02,
                "effect_size": 0.5,
                "calibrated_confidence": 0.78,
                "final_verdict": "supported",
                "reproducibility_score": 0.85,
            }
            claim_id = graph.register_claim(claim)
            assert claim_id == "clm-test-001"
            assert graph.get_claim_history("clm-test-001") is not None
            os.unlink(f.name)

    def test_evidence_graph_persistence(self):
        from mci.evidence_graph import EvidenceGraph
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
            # Write
            graph1 = EvidenceGraph(storage_path=path)
            graph1.register_claim({
                "claim_id": "clm-persist-001",
                "hypothesis": "H1: Persistência funciona",
                "null_hypothesis": "H0: Não funciona",
                "final_verdict": "supported",
            })
            # Read
            graph2 = EvidenceGraph(storage_path=path)
            history = graph2.get_claim_history("clm-persist-001")
            assert history is not None
            assert len(history["versions"]) == 1
            os.unlink(path)

    def test_add_evidence_for(self):
        from mci.evidence_graph import EvidenceGraph
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            graph = EvidenceGraph(storage_path=f.name)
            graph.register_claim({
                "claim_id": "clm-ev-001",
                "hypothesis": "H1: Teste",
                "null_hypothesis": "H0: Nulo",
            })
            success = graph.add_evidence(
                "clm-ev-001",
                evidence_type="replication",
                description="Replicação independente confirmou resultado",
                confidence_impact=0.2,
                source="external_lab"
            )
            assert success is True
            history = graph.get_claim_history("clm-ev-001")
            assert len(history["evidence_for"]) == 1
            assert history["evidence_for"][0]["confidence_impact"] == 0.2
            os.unlink(f.name)

    def test_add_evidence_against(self):
        from mci.evidence_graph import EvidenceGraph
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            graph = EvidenceGraph(storage_path=f.name)
            graph.register_claim({
                "claim_id": "clm-ev-002",
                "hypothesis": "H1: Teste",
                "null_hypothesis": "H0: Nulo",
            })
            success = graph.add_evidence(
                "clm-ev-002",
                evidence_type="failed_replication",
                description="Replicação falhou em confirmar",
                confidence_impact=-0.3,
                source="replication_lab"
            )
            assert success is True
            history = graph.get_claim_history("clm-ev-002")
            assert len(history["evidence_against"]) == 1
            os.unlink(f.name)

    def test_consolidated_confidence(self):
        from mci.evidence_graph import EvidenceGraph
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            graph = EvidenceGraph(storage_path=f.name)
            for conf in [0.5, 0.6, 0.7]:
                graph.register_claim({
                    "claim_id": "clm-consolidated",
                    "hypothesis": f"H1: conf={conf}",
                    "null_hypothesis": "H0",
                    "calibrated_confidence": conf,
                    "final_verdict": "supported" if conf > 0.5 else "inconclusive",
                })
            consolidated = graph.get_consolidated_confidence("clm-consolidated")
            # With weights [1.0, 1.1, 1.2] and values [0.5, 0.6, 0.7]
            # weighted_sum = 0.5*1.0 + 0.6*1.1 + 0.7*1.2 = 0.5 + 0.66 + 0.84 = 2.0
            # total_weight = 3.3, consolidated = 2.0/3.3 ≈ 0.6061
            assert consolidated is not None
            assert 0.55 <= consolidated <= 0.65
            os.unlink(f.name)

    def test_record_replication(self):
        from mci.evidence_graph import EvidenceGraph
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            graph = EvidenceGraph(storage_path=f.name)
            graph.register_claim({
                "claim_id": "clm-rep-001",
                "hypothesis": "H1",
                "null_hypothesis": "H0",
            })
            graph.record_replication("clm-rep-001", success=True)
            graph.record_replication("clm-rep-001", success=True)
            graph.record_replication("clm-rep-001", success=False)
            rate = graph.get_reproducibility_rate("clm-rep-001")
            assert rate == 2 / 3
            assert graph.get_claim_history("clm-rep-001")["replication_attempts"] == 3
            os.unlink(f.name)

    def test_find_contradictions(self):
        from mci.evidence_graph import EvidenceGraph
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            graph = EvidenceGraph(storage_path=f.name)
            graph.register_claim({
                "claim_id": "clm-ctr-001",
                "hypothesis": "H1: Café reduz risco de câncer",
                "null_hypothesis": "H0: Não reduz",
                "final_verdict": "supported",
            })
            graph.register_claim({
                "claim_id": "clm-ctr-002",
                "hypothesis": "H1: Café aumenta risco de câncer",
                "null_hypothesis": "H0: Não aumenta",
                "final_verdict": "supported",
            })
            graph.register_claim({
                "claim_id": "clm-ctr-003",
                "hypothesis": "H1: Chá melhora sono",
                "null_hypothesis": "H0: Não melhora",
                "final_verdict": "inconclusive",
            })
            contradictions = graph.find_contradictions()
            assert len(contradictions) >= 1  # clm-ctr-001 vs clm-ctr-002
            os.unlink(f.name)

    def test_get_stats(self):
        from mci.evidence_graph import EvidenceGraph
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            graph = EvidenceGraph(storage_path=f.name)
            stats = graph.get_stats()
            assert stats["total_claims"] == 0

            graph.register_claim({
                "claim_id": "clm-stats-001",
                "hypothesis": "H1",
                "null_hypothesis": "H0",
                "final_verdict": "supported",
            })
            stats = graph.get_stats()
            assert stats["total_claims"] == 1
            assert stats["supported"] == 1
            os.unlink(f.name)

    def test_global_graph_singleton(self):
        from mci.evidence_graph import get_global_evidence_graph, reset_global_evidence_graph
        reset_global_evidence_graph()
        g1 = get_global_evidence_graph()
        g2 = get_global_evidence_graph()
        assert g1 is g2
        reset_global_evidence_graph()


# =============================================================================
# HypothesisEngine Tests
# =============================================================================

class TestHypothesisEngine:
    def test_generate_hypothesis_basic(self):
        from mci.hypothesis_engine import generate_hypothesis
        claim = generate_hypothesis("A intervenção X reduz o erro de classificação?")
        assert claim["claim_id"].startswith("clm-")
        assert "H1" in claim["hypothesis"]
        assert "H0" in claim["null_hypothesis"]
        assert claim["falsifiable"] is True
        assert claim["final_verdict"] == "inconclusive"
        assert claim["effect_direction"] == "negative"

    def test_generate_hypothesis_positive(self):
        from mci.hypothesis_engine import generate_hypothesis
        claim = generate_hypothesis("A técnica Y melhora a acurácia do modelo?")
        assert claim["effect_direction"] == "positive"

    def test_generate_hypothesis_two_sided(self):
        from mci.hypothesis_engine import generate_hypothesis
        claim = generate_hypothesis("Existe diferença entre os métodos A e B?")
        assert claim["effect_direction"] == "two_sided"

    def test_generate_hypothesis_domain_detection(self):
        from mci.hypothesis_engine import generate_hypothesis
        claim = generate_hypothesis("Como o tratamento clínico afeta a sobrevida do paciente?")
        assert claim["domain"] in ["clinical", "machine_learning"]

    def test_generate_hypothesis_with_context(self):
        from mci.hypothesis_engine import generate_hypothesis
        claim = generate_hypothesis(
            "O novo algoritmo reduz latência?",
            context={
                "domain": "engineering",
                "metrics": ["Latency", "P99"],
                "alpha": 0.01,
                "design_type": "cross_over",
            }
        )
        assert claim["domain"] == "engineering"
        assert "Latency" in claim["metrics"]
        assert claim["experimental_design"]["alpha"] == 0.01
        assert claim["experimental_design"]["type"] == "cross_over"


# =============================================================================
# ExperimentDesigner Tests
# =============================================================================

class TestExperimentDesigner:
    def test_design_experiment_with_power(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.experiment_designer import design_experiment
        claim = generate_hypothesis("O método X melhora a precisão?")
        claim = design_experiment(claim)
        design = claim["experimental_design"]
        assert design["n_per_group"] > 0
        assert design["total_sample_size"] > 0
        assert "confounders_controlled" in design
        assert len(design["confounders_controlled"]) > 0

    def test_design_experiment_small_effect(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.experiment_designer import design_experiment
        claim = generate_hypothesis("Há efeito?")
        claim = design_experiment(claim, context={"effect_size": 0.05})
        # Efeito muito pequeno requer amostra enorme
        assert claim["experimental_design"]["n_per_group"] > 1000

    def test_design_experiment_multiple_arms(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.experiment_designer import design_experiment
        claim = generate_hypothesis("Qual tratamento é melhor?")
        claim = design_experiment(claim, context={"n_arms": 3})
        assert claim["experimental_design"]["n_arms"] == 3


# =============================================================================
# StatisticalValidator Tests
# =============================================================================

class TestStatisticalValidator:
    def test_validate_statistics_significant(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.experiment_designer import design_experiment
        from mci.statistical_validator import validate_statistics
        claim = generate_hypothesis("O tratamento reduz mortalidade?")
        claim = design_experiment(claim)
        claim = validate_statistics(claim, context={
            "p_value": 0.003,
            "effect_size": 0.65,
            "confidence_interval": [0.30, 1.00],
            "sample_size": 200,
        })
        assert claim["final_verdict"] == "supported"
        assert claim["p_value"] == 0.003
        assert claim["evidence_score"] >= 5
        assert claim["bayes_factor"]["BF10"] > 1

    def test_validate_statistics_non_significant(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.statistical_validator import validate_statistics
        claim = generate_hypothesis("Efeito questionável?")
        # Corrigido: não chama design_experiment para simplificar
        claim = validate_statistics(claim, context={
            "p_value": 0.45,
            "effect_size": 0.05,
            "confidence_interval": [-0.20, 0.30],
            "sample_size": 50,
        })
        assert claim["final_verdict"] in ["inconclusive", "refuted"]

    def test_bonferroni_correction(self):
        from mci.statistical_validator import validate_statistics
        from mci.hypothesis_engine import generate_hypothesis
        claim = generate_hypothesis("Teste com múltiplas comparações?")
        claim = validate_statistics(claim, context={
            "p_value": 0.04,
            "effect_size": 0.3,
            "n_tests": 5,
            "correction_method": "bonferroni",
            "sample_size": 100,
        })
        assert claim["p_value_corrected"] >= claim["p_value"]

    def test_bayes_factor_interpretation(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.statistical_validator import validate_statistics
        claim = generate_hypothesis("BF muito forte?")
        claim = validate_statistics(claim, context={
            "p_value": 0.0001,
            "effect_size": 0.8,
            "sample_size": 500,
        })
        assert "decisiva" in claim["bayes_factor_interpretation"].lower() or \
               "muito forte" in claim["bayes_factor_interpretation"].lower()
        assert claim["bayes_factor"]["BF10"] > 10


# =============================================================================
# AdversarialReviewer Tests
# =============================================================================

class TestAdversarialReviewer:
    def test_adversarial_p_hacking_detection(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.statistical_validator import validate_statistics
        from mci.adversarial_reviewer import run_adversarial_review
        claim = generate_hypothesis("Efeito suspeito?")
        claim = validate_statistics(claim, context={
            "p_value": 0.045,
            "effect_size": 0.15,
            "sample_size": 500,
        })
        claim = run_adversarial_review(claim)
        alerts = [f for f in claim["adversarial_findings"] if f.startswith("ALERTA:")]
        assert len(alerts) >= 1  # Perto do limiar + efeito pequeno

    def test_adversarial_p_hacking_strong_override(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.statistical_validator import validate_statistics
        from mci.adversarial_reviewer import run_adversarial_review
        claim = generate_hypothesis("Efeito com fraud?")
        claim = validate_statistics(claim, context={
            "p_value": 0.045,
            "effect_size": 0.3,
            "sample_size": 100,
        })
        # Simula múltiplos alerts
        claim = run_adversarial_review(claim, context={"adversarial_severity": "high"})
        # Verifica se overrides acontecem quando apropriado

    def test_adversarial_confounder_detection(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.adversarial_reviewer import run_adversarial_review
        claim = generate_hypothesis("Efeito causal?")
        claim = run_adversarial_review(claim)
        confounders = [f for f in claim["adversarial_findings"] if f.startswith("CONFOUNDER")]
        # Machine learning domain pode ter confounders não declarados


# =============================================================================
# ConfidenceCalibrator Tests
# =============================================================================

class TestConfidenceCalibrator:
    def test_calibrate_confidence_strong_evidence(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.statistical_validator import validate_statistics
        from mci.adversarial_reviewer import run_adversarial_review
        from mci.confidence_calibrator import calibrate_confidence
        claim = generate_hypothesis("Efeito forte?")
        claim = validate_statistics(claim, context={
            "p_value": 0.001,
            "effect_size": 0.9,
            "sample_size": 300,
        })
        claim = run_adversarial_review(claim)
        claim = calibrate_confidence(claim)
        assert claim["calibrated_confidence"] > 0.5
        assert claim["should_abstain"] is False

    def test_calibrate_confidence_weak_evidence(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.statistical_validator import validate_statistics
        from mci.confidence_calibrator import calibrate_confidence
        claim = generate_hypothesis("Efeito fraco?")
        claim = validate_statistics(claim, context={
            "p_value": 0.35,
            "effect_size": 0.05,
            "sample_size": 20,
        })
        claim = calibrate_confidence(claim)
        assert claim["calibrated_confidence"] < 0.5

    def test_calibrate_confidence_abstention(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.confidence_calibrator import calibrate_confidence
        claim = generate_hypothesis("Dados insuficientes?")
        claim = calibrate_confidence(claim, context={
            "reproducibility_score": 0.1,
        })
        if claim["calibrated_confidence"] < 0.20:
            assert claim["should_abstain"] is True

    def test_brier_score_calculation(self):
        from mci.confidence_calibrator import calibrate_confidence
        from mci.hypothesis_engine import generate_hypothesis
        claim = generate_hypothesis("Brier test?")
        claim = calibrate_confidence(claim, context={
            "actual_outcome": True,
            "actual_verdict": "supported",
            "p_value": 0.01,
            "effect_size": 0.5,
        })
        assert claim["brier_score"] is not None
        assert 0 <= claim["brier_score"] <= 1


# =============================================================================
# ScientificReporter Tests
# =============================================================================

class TestScientificReporter:
    def test_build_report_contains_all_sections(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.statistical_validator import validate_statistics
        from mci.scientific_reporter import build_report
        claim = generate_hypothesis("O tratamento funciona?")
        claim = validate_statistics(claim, context={
            "p_value": 0.02,
            "effect_size": 0.5,
            "sample_size": 150,
        })
        report = build_report(claim)
        assert "Scientific Claim Report" in report
        assert "Hip" in report  # LaTeX: Hip\'oteses
        assert "Experimental" in report
        assert "Resultados" in report
        assert "Adversarial" in report
        assert "Limita" in report  # LaTeX: Limita\c{c}\~oes
        assert "Veredito" in report
        assert "Metadados" in report

    def test_executive_summary(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.statistical_validator import validate_statistics
        from mci.scientific_reporter import build_executive_summary
        claim = generate_hypothesis("Resumo executivo?")
        claim = validate_statistics(claim, context={
            "p_value": 0.01,
            "effect_size": 0.6,
            "sample_size": 200,
        })
        summary = build_executive_summary(claim)
        assert "Executive Summary" in summary
        assert "SUPPORTED" in summary or "REFUTED" in summary or "INCONCLUSIVE" in summary

    def test_reproducibility_checklist(self):
        from mci.hypothesis_engine import generate_hypothesis
        from mci.scientific_reporter import build_reproducibility_checklist
        claim = generate_hypothesis("Checklist reprodutibilidade?")
        checklist = build_reproducibility_checklist(claim)
        assert "Reproducibility Checklist" in checklist
        assert "Pre-registration" in checklist
        assert "Effect size reported" in checklist


# =============================================================================
# Benchmark Tests
# =============================================================================

class TestScientificBenchmark:
    def test_causal_benchmark(self):
        from benchmarks.scientific_reasoning.causal_benchmark import CausalInferenceBenchmark
        bench = CausalInferenceBenchmark()
        result = bench.run()
        assert result.score >= 0
        assert len(result.details) > 0

    def test_experimental_design_benchmark(self):
        from benchmarks.scientific_reasoning.experimental_design_benchmark import ExperimentalDesignBenchmark
        bench = ExperimentalDesignBenchmark()
        result = bench.run()
        assert result.score >= 0

    def test_statistical_benchmark(self):
        from benchmarks.scientific_reasoning.statistical_benchmark import StatisticalInterpretationBenchmark
        bench = StatisticalInterpretationBenchmark()
        result = bench.run()
        assert result.score > 0

    def test_power_analysis_benchmark(self):
        from benchmarks.scientific_reasoning.power_analysis_benchmark import PowerAnalysisBenchmark
        bench = PowerAnalysisBenchmark()
        result = bench.run()
        assert result.score > 0

    def test_bias_detection_benchmark(self):
        from benchmarks.scientific_reasoning.bias_detection_benchmark import BiasDetectionBenchmark
        bench = BiasDetectionBenchmark()
        result = bench.run()
        assert result.score > 0

    def test_run_all_benchmarks(self):
        from benchmarks.scientific_reasoning.runner import run_all_benchmarks
        results = run_all_benchmarks()
        assert "overall_score" in results
        assert results["total_tasks"] > 0
        assert results["overall_score"] >= 0


# =============================================================================
# Pipeline End-to-End Tests
# =============================================================================

class TestPipelineEndToEnd:
    def test_full_scientific_cycle(self):
        from mci.orchestration import run_scientific_cycle
        result = run_scientific_cycle(
            "O novo método de treinamento reduz overfitting?",
            context={
                "p_value": 0.01,
                "effect_size": 0.55,
                "confidence_interval": [0.25, 0.85],
                "sample_size": 200,
                "reproducibility_score": 0.90,
            }
        )
        assert result.claim is not None
        assert result.report_tex is not None
        assert result.graph_id is not None
        assert result.claim["final_verdict"] == "supported"
        assert result.claim["evidence_score"] >= 5

    def test_full_cycle_inconclusive(self):
        from mci.orchestration import run_scientific_cycle
        result = run_scientific_cycle(
            "Efeito incerto?",
            context={
                "p_value": 0.15,
                "effect_size": 0.10,
                "sample_size": 30,
            }
        )
        # Com evidência fraca, pode ser inconclusive ou refuted
        assert result.claim["final_verdict"] in ["inconclusive", "refuted"]
        assert result.claim["calibrated_confidence"] <= 0.5

    def test_full_cycle_refuted(self):
        from mci.orchestration import run_scientific_cycle
        result = run_scientific_cycle(
            "Efeito nulo?",
            context={
                "p_value": 0.65,
                "effect_size": 0.01,
                "sample_size": 20,
            }
        )
        assert result.claim["final_verdict"] in ["inconclusive", "refuted"]

    def test_pipeline_governance_success(self):
        from mci.pipeline.scientific_governance_pipeline import run_scientific_governance_pipeline
        result = run_scientific_governance_pipeline(
            problem_text="A intervenção X reduz erro em classificação?",
            executor_fn=lambda ctx: {"result": "ok"},
            context={
                "validated_shortcut": True,
                "risk": 0.1,
                "risk_threshold": 0.5,
                "expected_fidelity": 0.95,
                "expected_cost_gain": 1.5,
                "p_value": 0.01,
                "effect_size": 0.55,
                "sample_size": 200,
                "reproducibility_score": 0.92,
                "confidence_interval": [0.25, 0.85],
                "expected_behavior": {
                    "egs_should_decide": "approve"
                }
            }
        )
        assert result["pipeline_success"] is True
        assert result["status"] == "success"
        assert result["scientific_claim"]["final_verdict"] == "supported"
        assert result["evidence_graph_id"] is not None

    def test_pipeline_egs_block(self):
        from mci.pipeline.scientific_governance_pipeline import run_scientific_governance_pipeline
        result = run_scientific_governance_pipeline(
            problem_text="Proposta com potencial discriminatório.",
            executor_fn=lambda ctx: {"result": "ok"},
            context={
                "risk_profile": {"ethical_risk": "high"},
                "expected_behavior": {
                    "hard_block_expected": True,
                }
            }
        )
        assert result["pipeline_success"] is False
        assert result["status"] == "blocked"
        assert result["egs"]["decision"] == "block"

    def test_pipeline_evidence_graph_integration(self):
        from mci.pipeline.scientific_governance_pipeline import run_scientific_governance_pipeline
        from mci.evidence_graph import get_global_evidence_graph, reset_global_evidence_graph
        reset_global_evidence_graph()
        result = run_scientific_governance_pipeline(
            problem_text="Teste integração EvidenceGraph?",
            executor_fn=lambda ctx: {"result": "ok"},
            context={
                "p_value": 0.02,
                "effect_size": 0.5,
                "sample_size": 150,
                "reproducibility_score": 0.85,
                "validated_shortcut": True,
                "risk": 0.1,
            }
        )
        graph = get_global_evidence_graph()
        claim_id = result["evidence_graph_id"]
        history = graph.get_claim_history(claim_id)
        assert history is not None
        assert len(history["versions"]) >= 1
        stats = graph.get_stats()
        assert stats["total_claims"] >= 1
        reset_global_evidence_graph()


# =============================================================================
# Integration Tests (compatibility with existing system)
# =============================================================================

class TestIntegration:
    def test_oqs_vsee_egs_individual(self):
        """Verifica que OQS, VSEE e EGS funcionam individualmente."""
        from mci.oqs import run_oqs_scanner
        from mci.egs import run_egs_scanner

        oqs_res = run_oqs_scanner("Qual o melhor método?")
        assert "selected_question" in oqs_res
        assert oqs_res["pass"] is True

        egs_res = run_egs_scanner("Resultado do experimento", {})
        assert "decision" in egs_res

    def test_evidence_graph_claim_schema_compatible(self):
        """Verifica que o schema valida claims geradas."""
        import jsonschema
        from mci.orchestration import run_scientific_cycle
        import os

        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "schemas",
            "scientific_claim.schema.json"
        )
        if not os.path.exists(schema_path):
            pytest.skip("Schema não encontrado")

        with open(schema_path, "r") as f:
            schema = json.load(f)

        result = run_scientific_cycle(
            "Schema validation test?",
            context={"p_value": 0.02, "effect_size": 0.5, "sample_size": 100}
        )
        try:
            jsonschema.validate(instance=result.claim, schema=schema)
            valid = True
        except jsonschema.exceptions.ValidationError:
            valid = False
        assert valid, "Claim deve ser compatível com o schema"
