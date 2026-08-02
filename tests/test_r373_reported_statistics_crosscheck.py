# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R373 — Contraverificação de Estatísticas Reportadas."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mci.rigorous_validation import (  # noqa: E402
    ContractError,
    crosscheck_reported_correlation,
    pearson_naive_significance,
)

# Valores de referência computados com scipy.stats.t.cdf durante o
# desenvolvimento (não importado no módulo entregue) — diff <= 1e-12.
REFERENCE_CASES = [
    (0.8644, 8, 0.00561658),
    (0.9523, 8, 0.00026171),
    (0.6569, 12, 0.02029904),
    (-0.9462, 6, 0.00426380),
    (0.6617, 11, 0.02657984),
    (0.7084, 11, 0.01469194),
    (0.3000, 20, 0.19875772),
    (0.9900, 4, 0.01000000),
]


# ═══════════════════════════════════════════════════════════════════════
# 1. pearson_naive_significance — validado contra referências scipy
# ═══════════════════════════════════════════════════════════════════════

class TestPearsonNaiveSignificance:
    @pytest.mark.parametrize("r,n,expected", REFERENCE_CASES)
    def test_bate_com_referencia_scipy(self, r, n, expected):
        p = pearson_naive_significance(r, n)
        assert abs(p - expected) < 1e-6

    def test_n_menor_que_3_falha(self):
        with pytest.raises(ContractError):
            pearson_naive_significance(0.5, 2)

    def test_r_fora_do_intervalo_falha(self):
        with pytest.raises(ContractError):
            pearson_naive_significance(1.0, 10)
        with pytest.raises(ContractError):
            pearson_naive_significance(-1.5, 10)

    def test_determinismo(self):
        assert pearson_naive_significance(0.7, 15) == pearson_naive_significance(0.7, 15)


# ═══════════════════════════════════════════════════════════════════════
# 2. crosscheck_reported_correlation — assimétrico
# ═══════════════════════════════════════════════════════════════════════

class TestCrosscheckAssimetrico:
    def test_p_reportado_igual_ao_ingenuo_sem_achado(self):
        # PISA x GDP cross-country do manuscrito real: bate quase exato
        result = crosscheck_reported_correlation(r=0.6617, n=11, reported_p=0.026572)
        assert result["overstated"] is False
        assert result["findings"] == []

    def test_p_reportado_mais_conservador_sem_achado(self):
        # GDP x Escolaridade do manuscrito real: p reportado (0.026) é MAIS
        # conservador que o ingênuo (0.0056) -- correção legítima de série
        # temporal, não deve ser sinalizada.
        result = crosscheck_reported_correlation(r=0.8644, n=8, reported_p=0.026337)
        assert result["overstated"] is False
        assert result["findings"] == []

    def test_p_reportado_mais_forte_que_o_ingenuo_e_sinalizado(self):
        # r=0.5, n=10 -> p ingênuo bem maior que 0.001; reportar p=0.001
        # alega mais significância do que r,n sozinhos sustentam.
        naive = pearson_naive_significance(0.5, 10)
        assert naive > 0.05  # confirma que o cenário de teste é válido
        result = crosscheck_reported_correlation(r=0.5, n=10, reported_p=0.001)
        assert result["overstated"] is True
        codes = [f["code"] for f in result["findings"]]
        assert "OVERSTATED_SIGNIFICANCE" in codes
        assert result["human_gate"] == "required"

    def test_dentro_da_tolerancia_nao_e_falso_positivo(self):
        naive = pearson_naive_significance(0.6569, 12)
        result = crosscheck_reported_correlation(
            r=0.6569, n=12, reported_p=naive - 5e-4, tolerance=1e-3
        )
        assert result["overstated"] is False

    def test_disclaimer_presente_e_nao_valida_correcao(self):
        result = crosscheck_reported_correlation(r=0.86, n=8, reported_p=0.03)
        low = result["disclaimer"].lower()
        assert "não valida" in low or "nao valida" in low

    def test_determinismo(self):
        r1 = crosscheck_reported_correlation(r=0.7, n=15, reported_p=0.02)
        r2 = crosscheck_reported_correlation(r=0.7, n=15, reported_p=0.02)
        assert r1 == r2


# ═══════════════════════════════════════════════════════════════════════
# 3. Aplicação às correlações reais do manuscrito
# ═══════════════════════════════════════════════════════════════════════

class TestManuscritoReal:
    """As 5 correlações do manuscrito real com n declarado no texto não
    devem reportar overstated=True -- o artigo não infla significância."""

    @pytest.mark.parametrize("r,n,reported_p", [
        (0.8644, 8, 0.026337),
        (0.6569, 12, 0.020297),
        (-0.9462, 6, 0.014874),
        (0.6617, 11, 0.026572),
        (0.7084, 11, 0.014699),
    ])
    def test_correlacoes_reais_nao_sao_overstated(self, r, n, reported_p):
        result = crosscheck_reported_correlation(r=r, n=n, reported_p=reported_p)
        assert result["overstated"] is False


# ═══════════════════════════════════════════════════════════════════════
# 4. Regressão do bug do R369 (falso positivo em "primeiras diferenças")
# ═══════════════════════════════════════════════════════════════════════

class TestRegressaoR369:
    def test_primeiras_diferencas_nao_e_falso_positivo(self):
        from reasoning.production_scaffolds import audit_scientific_manuscript

        sections = {
            "problema": "O problema de pesquisa é claro.",
            "lacuna": "Há uma lacuna na literatura sobre o tema.",
            "hipotese": "A hipótese é testável.",
            "metodo": "O método usa amostra e grupo de controle.",
            "evidencia": "Os resultados mostram evidência na tabela.",
            "contra_argumento": "Entretanto, uma alternativa considerada.",
            "limitacao": (
                "Primeiras diferenças ou modelos VECM reduziriam as "
                "magnitudes observadas neste primeiro trimestre da série."
            ),
            "contribuicao": "A contribuição é um arcabouço auditável.",
        }
        out = audit_scientific_manuscript(sections)
        codes = {f["code"] for f in out["findings"]}
        assert "UNSUPPORTED_NOVELTY_CLAIM" not in codes


# ═══════════════════════════════════════════════════════════════════════
# 5. Integração no R103
# ═══════════════════════════════════════════════════════════════════════

class TestIntegracaoR103:
    def test_correlacao_nao_inflada_e_verificada(self):
        from agentic_science_v2.review_agent import OrchestratorReviewer, ReviewLedger

        ledger = ReviewLedger()
        claim = ledger.extract_claim("GDP x escolaridade correlacionados.", section="resultados")
        orch = OrchestratorReviewer()
        result = orch.verify_reported_correlation(
            claim.id, r=0.8644, n=8, reported_p=0.026337, ledger=ledger
        )
        assert result["overstated"] is False
        assert ledger.claims[claim.id].verified is True

    def test_correlacao_inflada_fica_pendente(self):
        from agentic_science_v2.review_agent import OrchestratorReviewer, ReviewLedger

        ledger = ReviewLedger()
        claim = ledger.extract_claim("Correlação suspeita.", section="resultados")
        orch = OrchestratorReviewer()
        result = orch.verify_reported_correlation(
            claim.id, r=0.5, n=10, reported_p=0.001, ledger=ledger
        )
        assert result["overstated"] is True
        assert ledger.claims[claim.id].verified is False
        pending_ids = {item["claim_id"] for item in ledger.get_pending_verifications()}
        assert claim.id in pending_ids
