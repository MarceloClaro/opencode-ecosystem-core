# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R370 — RigorousEmpiricalValidator."""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mci.rigorous_validation import (  # noqa: E402
    convergent_validity_report,
    k_fold_cross_validate,
    permutation_counter_proof,
    two_sample_hypothesis_test,
)

# Grupos com grande separação (efeito claro): médias ~11 vs ~20
BIG_EFFECT_A = [9, 10, 11, 10, 11, 12, 13, 9, 10, 12]
BIG_EFFECT_B = [18, 20, 21, 19, 22, 20, 18, 21, 20, 19]

# Grupos sem efeito: mesma distribuição, apenas reordenada
NO_EFFECT_A = [10, 12, 9, 11, 13, 10, 12, 9]
NO_EFFECT_B = [11, 9, 12, 10, 9, 13, 11, 12]


def _welch_t_stat(a, b):
    mean_a, mean_b = statistics.mean(a), statistics.mean(b)
    var_a, var_b = statistics.variance(a), statistics.variance(b)
    n_a, n_b = len(a), len(b)
    denom = ((var_a / n_a) + (var_b / n_b)) ** 0.5
    return (mean_a - mean_b) / denom if denom > 0 else 0.0


# ═══════════════════════════════════════════════════════════════════════
# 1. permutation_counter_proof — o motor de contraprova
# ═══════════════════════════════════════════════════════════════════════

class TestPermutationCounterProof:
    def test_determinismo_mesmo_seed(self):
        r1 = permutation_counter_proof(
            BIG_EFFECT_A, BIG_EFFECT_B, _welch_t_stat, n_permutations=500, seed=42
        )
        r2 = permutation_counter_proof(
            BIG_EFFECT_A, BIG_EFFECT_B, _welch_t_stat, n_permutations=500, seed=42
        )
        assert r1 == r2

    def test_seeds_diferentes_podem_diferir(self):
        r1 = permutation_counter_proof(
            BIG_EFFECT_A, BIG_EFFECT_B, _welch_t_stat, n_permutations=500, seed=1
        )
        r2 = permutation_counter_proof(
            BIG_EFFECT_A, BIG_EFFECT_B, _welch_t_stat, n_permutations=500, seed=2
        )
        # Mesma estatística observada, mas distribuição nula pode variar
        assert r1["observed_statistic"] == r2["observed_statistic"]

    def test_grande_separacao_p_baixo(self):
        r = permutation_counter_proof(
            BIG_EFFECT_A, BIG_EFFECT_B, _welch_t_stat, n_permutations=2000, seed=935370
        )
        assert r["p_value"] < 0.01

    def test_sem_efeito_p_alto(self):
        r = permutation_counter_proof(
            NO_EFFECT_A, NO_EFFECT_B, _welch_t_stat, n_permutations=2000, seed=935370
        )
        assert r["p_value"] > 0.20

    def test_p_value_nunca_zero(self):
        r = permutation_counter_proof(
            BIG_EFFECT_A, BIG_EFFECT_B, _welch_t_stat, n_permutations=100, seed=935370
        )
        assert r["p_value"] > 0.0

    def test_estrutura_do_retorno(self):
        r = permutation_counter_proof(
            BIG_EFFECT_A, BIG_EFFECT_B, _welch_t_stat, n_permutations=200, seed=935370
        )
        assert set(r.keys()) >= {
            "observed_statistic", "p_value", "n_permutations", "seed",
            "null_distribution_summary",
        }
        summary = r["null_distribution_summary"]
        assert set(summary.keys()) == {"min", "max", "mean", "stdev"}


# ═══════════════════════════════════════════════════════════════════════
# 2. two_sample_hypothesis_test — duas lentes independentes
# ═══════════════════════════════════════════════════════════════════════

class TestTwoSampleHypothesisTest:
    def test_ambos_testes_concordam_em_sinal(self):
        out = two_sample_hypothesis_test(BIG_EFFECT_A, BIG_EFFECT_B, seed=935370)
        assert out["welch_t"]["observed_statistic"] < 0  # A < B
        assert out["mann_whitney"]["observed_statistic"] >= 0  # U_a baixo (A menor)

    def test_amostra_pequena_falha_fechado(self):
        with pytest.raises(ValueError):
            two_sample_hypothesis_test([1, 2], [3, 4, 5], seed=935370)
        with pytest.raises(ValueError):
            two_sample_hypothesis_test([1, 2, 3], [4, 5], seed=935370)

    def test_effect_size_e_ic_bootstrap(self):
        out = two_sample_hypothesis_test(BIG_EFFECT_A, BIG_EFFECT_B, seed=935370)
        assert out["cohens_d"] < 0  # A menor que B
        ci_low, ci_high = out["cohens_d_ci_95"]
        assert ci_low < ci_high
        # Efeito grande e claro: CI não deve conter zero
        assert ci_high < 0

    def test_determinismo(self):
        out1 = two_sample_hypothesis_test(BIG_EFFECT_A, BIG_EFFECT_B, seed=7)
        out2 = two_sample_hypothesis_test(BIG_EFFECT_A, BIG_EFFECT_B, seed=7)
        assert out1 == out2


# ═══════════════════════════════════════════════════════════════════════
# 3. k_fold_cross_validate — validação cruzada genérica
# ═══════════════════════════════════════════════════════════════════════

class TestKFoldCrossValidate:
    def test_particao_exaustiva_e_disjunta(self):
        data = list(range(20))
        seen_test_indices = []

        def scorer(train_idx, test_idx):
            seen_test_indices.append(set(test_idx))
            return 1.0

        k_fold_cross_validate(data, k=4, scorer_fn=scorer, seed=935370)
        union = set()
        for s in seen_test_indices:
            assert not (union & s), "índice apareceu em mais de um fold de teste"
            union |= s
        assert union == set(range(len(data)))

    def test_k_invalido_falha_fechado(self):
        with pytest.raises(ValueError):
            k_fold_cross_validate([1, 2, 3], k=1, scorer_fn=lambda tr, te: 1.0)
        with pytest.raises(ValueError):
            k_fold_cross_validate([1, 2, 3], k=10, scorer_fn=lambda tr, te: 1.0)
        with pytest.raises(ValueError):
            k_fold_cross_validate([], k=2, scorer_fn=lambda tr, te: 1.0)

    def test_scorer_estavel_marca_stable_true(self):
        data = list(range(30))

        def scorer(train_idx, test_idx):
            return 0.85  # score idêntico em todos os folds

        result = k_fold_cross_validate(data, k=5, scorer_fn=scorer, seed=935370)
        assert result["stable"] is True
        assert result["mean"] == 0.85
        assert result["stdev"] == 0.0

    def test_scorer_instavel_marca_stable_false(self):
        data = list(range(30))
        scores = iter([0.9, 0.1, 0.95, 0.05, 0.9])

        def scorer(train_idx, test_idx):
            return next(scores)

        result = k_fold_cross_validate(data, k=5, scorer_fn=scorer, seed=935370)
        assert result["stable"] is False

    def test_mean_proximo_de_zero_nao_lanca_excecao(self):
        data = list(range(10))
        scores = iter([0.01, -0.01, 0.02, -0.02, 0.0])

        def scorer(train_idx, test_idx):
            return next(scores)

        result = k_fold_cross_validate(data, k=5, scorer_fn=scorer, seed=935370)
        assert result["low_mean_denominator"] is True


# ═══════════════════════════════════════════════════════════════════════
# 4. convergent_validity_report — a peça central
# ═══════════════════════════════════════════════════════════════════════

class TestConvergentValidityReport:
    def test_efeito_claro_converge(self):
        report = convergent_validity_report(BIG_EFFECT_A, BIG_EFFECT_B, seed=935370)
        assert report["convergent"] is True
        assert report["human_gate"] is True
        assert "disclaimer" in report and len(report["disclaimer"]) > 20

    def test_sem_efeito_nao_converge(self):
        report = convergent_validity_report(NO_EFFECT_A, NO_EFFECT_B, seed=935370)
        assert report["convergent"] is False

    def test_reaproveita_validate_statistics_existente(self):
        report = convergent_validity_report(BIG_EFFECT_A, BIG_EFFECT_B, seed=935370)
        assert "verdict" in report
        assert "final_verdict" in report["verdict"]
        assert "bayes_factor" in report["verdict"]

    def test_disclaimer_nao_afirma_prova(self):
        report = convergent_validity_report(BIG_EFFECT_A, BIG_EFFECT_B, seed=935370)
        low = report["disclaimer"].lower()
        assert "prova" not in low or "não prova" in low or "nao prova" in low

    def test_determinismo(self):
        r1 = convergent_validity_report(BIG_EFFECT_A, BIG_EFFECT_B, seed=99)
        r2 = convergent_validity_report(BIG_EFFECT_A, BIG_EFFECT_B, seed=99)
        assert r1 == r2


# ═══════════════════════════════════════════════════════════════════════
# 5. Sem dependência de numpy/scipy
# ═══════════════════════════════════════════════════════════════════════

class TestSemDependenciaPesada:
    def test_modulo_nao_importa_numpy_nem_scipy(self):
        source = (ROOT / "mci" / "rigorous_validation.py").read_text(encoding="utf-8")
        assert "import numpy" not in source
        assert "import scipy" not in source
        assert "from numpy" not in source
        assert "from scipy" not in source


# ═══════════════════════════════════════════════════════════════════════
# 6. Integração com o R103 (ReviewLedger)
# ═══════════════════════════════════════════════════════════════════════

class TestIntegracaoR103:
    def test_claim_convergente_e_verificada(self):
        from agentic_science_v2.review_agent import OrchestratorReviewer, ReviewLedger

        ledger = ReviewLedger()
        claim = ledger.extract_claim("O tratamento X aumenta a métrica Y.", section="results")
        orch = OrchestratorReviewer()
        result = orch.verify_statistical_claim(
            claim.id, BIG_EFFECT_A, BIG_EFFECT_B, ledger, seed=935370
        )
        assert result["convergent"] is True
        assert ledger.claims[claim.id].verified is True

    def test_claim_nao_convergente_fica_pendente_com_nota(self):
        from agentic_science_v2.review_agent import OrchestratorReviewer, ReviewLedger

        ledger = ReviewLedger()
        claim = ledger.extract_claim(
            "Novel breakthrough no resultado Z.", section="results"
        )
        orch = OrchestratorReviewer()
        result = orch.verify_statistical_claim(
            claim.id, NO_EFFECT_A, NO_EFFECT_B, ledger, seed=935370
        )
        assert result["convergent"] is False
        assert ledger.claims[claim.id].verified is False
        pending_ids = {item["claim_id"] for item in ledger.get_pending_verifications()}
        assert claim.id in pending_ids
