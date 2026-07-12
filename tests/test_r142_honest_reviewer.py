# -*- coding: utf-8 -*-
"""
Testes R142 — Honest Evaluation Engine (SPEC-935-R142)
======================================================
TDD da disciplina antioverclaim como capacidade reutilizável:

  * cobertura/processo NÃO é veredito de qualidade;
  * nota/rótulo de topo (best-seller, obra-prima, Qualis A1, verified,
    superhuman, 9.5–10/10, 100%, perfeito) exige VALIDAÇÃO EXTERNA;
  * o engine emite uma FAIXA honesta (piso–teto), não um ponto inflado;
  * reusa (não duplica) a política de
    `mci/metacognitive_evaluator.classify_metacognitive_tier`.

Requisitos: SPEC-935-R142.
"""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ── CA-1 / CA-2: classify_claim — cobertura vs qualidade ─────────────

def test_ca1_cobertura_nao_e_veredito_de_qualidade():
    from evaluation.honest_reviewer import classify_claim
    r = classify_claim("cobertura 100% dos scanners; todos os eixos varridos")
    assert r["kind"] == "coverage"
    assert r["is_quality_verdict"] is False


def test_ca2_qualidade_e_veredito():
    from evaluation.honest_reviewer import classify_claim
    r = classify_claim("uma obra-prima; mérito literário nota 9.5/10")
    assert r["kind"] == "quality"
    assert r["is_quality_verdict"] is True


def test_classify_mixed_quando_ambos():
    from evaluation.honest_reviewer import classify_claim
    r = classify_claim("cobertura 100% dos scanners prova que é uma obra-prima")
    assert r["kind"] == "mixed"
    # mesmo misto, continua sendo um veredito de qualidade a vigiar
    assert r["is_quality_verdict"] is True


def test_classify_neutral():
    from evaluation.honest_reviewer import classify_claim
    r = classify_claim("o documento tem 12 páginas e três seções")
    assert r["kind"] == "neutral"
    assert r["is_quality_verdict"] is False


# ── CA-3 / CA-4: detect_inflation ────────────────────────────────────

def test_ca3_detecta_termos_inflacionarios():
    from evaluation.honest_reviewer import detect_inflation
    text = "É best-seller garantido, uma obra-prima 9.5/10, Qualis A1, 100% verified."
    found = {f["term"] for f in detect_inflation(text)}
    assert "best-seller" in found
    assert any("9.5" in t or "9,5" in t for t in found)
    assert "100%" in found
    assert "qualis a1" in found
    assert "verified" in found


def test_ca3_texto_honesto_nao_infla():
    from evaluation.honest_reviewer import detect_inflation
    text = ("Avaliação interna estima faixa ~8/10; sem validação externa "
            "não é possível afirmar nota de topo. Cobertura dos scanners não "
            "equivale a mérito.")
    assert detect_inflation(text) == []


def test_ca4_verified_liberado_com_validacao_externa():
    from evaluation.honest_reviewer import detect_inflation
    txt = "resultado verified pela banca; qualis a1 confirmado"
    terms_sem = {f["term"] for f in detect_inflation(txt, external_validation=False)}
    terms_com = {f["term"] for f in detect_inflation(txt, external_validation=True)}
    assert "verified" in terms_sem and "qualis a1" in terms_sem
    assert "verified" not in terms_com and "qualis a1" not in terms_com


def test_ca4_perfeicao_absoluta_segue_suspeita_mesmo_validada():
    from evaluation.honest_reviewer import detect_inflation
    txt = "cobertura 100%, resultado perfeito e sem falhas"
    terms = {f["term"] for f in detect_inflation(txt, external_validation=True)}
    assert "100%" in terms
    assert "perfeito" in terms


# ── CA-5 / CA-6: honest_score_band ───────────────────────────────────

def test_ca5_cobertura_alta_nao_destrava_nota_topo():
    from evaluation.honest_reviewer import honest_score_band, INTERNAL_QUALITY_CEILING
    band = honest_score_band(coverage=100, external_validation=False)
    assert band["ceiling"] <= INTERNAL_QUALITY_CEILING
    assert band["verdict_allowed"] is False
    assert band["floor"] <= band["ceiling"]


def test_ca6_validacao_externa_destrava_teto():
    from evaluation.honest_reviewer import honest_score_band
    band = honest_score_band(coverage=100, external_validation=True,
                             quality_signal=9.5)
    assert band["ceiling"] == 10.0
    assert band["verdict_allowed"] is True
    assert band["floor"] <= band["ceiling"]


def test_band_normaliza_escalas():
    from evaluation.honest_reviewer import honest_score_band
    # 0.85 (fração), 85 (porcentagem) e 8.5 (pontos) → mesma faixa
    a = honest_score_band(coverage=0.85)
    b = honest_score_band(coverage=85)
    c = honest_score_band(coverage=8.5)
    assert a["band"] == b["band"] == c["band"]


def test_band_string_formatada():
    from evaluation.honest_reviewer import honest_score_band
    band = honest_score_band(coverage=80, external_validation=False)
    assert "–" in band["band"] or "-" in band["band"]


# ── CA-7 / CA-8: review — pipeline completo ──────────────────────────

def test_ca7_alegacao_inflada_nao_publicavel():
    from evaluation.honest_reviewer import review
    r = review("Obra-prima best-seller 9.5/10, cobertura 100%, Qualis A1.",
               coverage=100, external_validation=False)
    assert r["publishable"] is False
    assert len(r["inflation"]) >= 3
    assert r["band"]["ceiling"] <= 8.5
    # integra a política metacognitiva existente, sem 'verified' interno
    assert r["tier"] != "metacognitive_superhuman_verified"


def test_ca8_alegacao_honesta_publicavel():
    from evaluation.honest_reviewer import review
    r = review(
        "Estimo faixa interna ~8/10. Cobertura dos scanners é de processo, "
        "não de mérito; nota de topo dependeria de validação externa.",
        coverage=90, external_validation=False,
    )
    assert r["publishable"] is True
    assert r["inflation"] == []


def test_review_integra_tier_metacognitivo():
    from evaluation.honest_reviewer import review
    from mci.metacognitive_evaluator import classify_metacognitive_tier
    r = review("resultado sólido", coverage=95, external_validation=False)
    assert r["tier"] == classify_metacognitive_tier(95, False)
    # com validação externa a mesma cobertura pode chegar a verified
    r2 = review("resultado sólido", coverage=95, external_validation=True)
    assert r2["tier"] == classify_metacognitive_tier(95, True)


def test_review_recomendacoes_mencionam_cobertura_vs_qualidade():
    from evaluation.honest_reviewer import review
    r = review("obra-prima 10/10", coverage=100, external_validation=False)
    joined = " ".join(r["recommendations"]).lower()
    assert "cobertura" in joined or "validação externa" in joined or "validacao externa" in joined
