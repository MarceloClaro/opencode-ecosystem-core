# -*- coding: utf-8 -*-
"""
Testes R113 — Detector de Falácias Lógicas e Vieses Cognitivos
=================================================================
Testa reasoning/fallacies.py: FallacyDetector com as 15 falácias
lógicas clássicas e os 4 vieses cognitivos catalogados.
"""

import pytest

from reasoning.fallacies import FallacyDetector, FALLACY_DEFINITIONS, BIAS_DEFINITIONS


@pytest.fixture
def detector():
    return FallacyDetector()


class TestCatalogSize:
    def test_fifteen_fallacies_catalogued(self):
        assert len(FALLACY_DEFINITIONS) == 15

    def test_four_biases_catalogued(self):
        assert len(BIAS_DEFINITIONS) == 4

    def test_every_fallacy_has_name_explanation_and_cues(self):
        for fid, definition in FALLACY_DEFINITIONS.items():
            assert definition["name"], fid
            assert definition["explanation"], fid
            assert len(definition["cues"]) >= 1, fid


class TestDetectFallacies:
    @pytest.mark.parametrize("fallacy_id,text", [
        ("ad_hominem", "Você é burro, seu argumento não vale nada."),
        ("straw_man", "Então você está dizendo que ninguém deveria trabalhar?"),
        ("false_dilemma", "Ou você está comigo ou está contra mim, não há meio termo."),
        ("slippery_slope", "Se isso acontecer, então vai levar ao caos total."),
        ("appeal_to_authority", "Um especialista disse que é assim, então é verdade."),
        ("bandwagon", "Todo mundo concorda que essa é a única solução."),
        ("appeal_to_emotion", "Pense nas crianças antes de discordar de mim."),
        ("circular_reasoning", "É verdade porque é verdade, simples assim."),
        ("hasty_generalization", "Vi isso uma vez, então sempre acontece."),
        ("post_hoc", "Aconteceu logo após, então deve ter sido causa."),
        ("red_herring", "Isso não importa, o que importa é outra coisa."),
        ("tu_quoque", "Você também faz isso, então não pode me criticar."),
        ("false_equivalence", "Isso é a mesma coisa que roubar um banco."),
        ("appeal_to_ignorance", "Ninguém provou que é falso, então deve ser verdade."),
        ("anecdotal_evidence", "Conheço uma pessoa que fez isso e deu certo."),
    ])
    def test_detects_each_fallacy(self, detector, fallacy_id, text):
        matches = detector.detect_fallacies(text)
        ids_found = [m.fallacy_id for m in matches]
        assert fallacy_id in ids_found, f"esperava detectar {fallacy_id} em: {text!r}"

    def test_clean_text_has_no_fallacies(self, detector):
        text = "Os dados mostram uma correlação de 0.8 com significância estatística p<0.01, replicada em 3 estudos independentes."
        matches = detector.detect_fallacies(text)
        assert matches == []

    def test_match_includes_confidence_and_explanation(self, detector):
        matches = detector.detect_fallacies("Você é burro.")
        assert matches
        m = matches[0]
        assert 0.0 < m.confidence <= 1.0
        assert m.explanation
        assert m.category == "fallacy"

    def test_confidence_increases_with_more_cue_hits(self, detector):
        single = detector.detect_fallacies("Você é burro.")
        double = detector.detect_fallacies("Você é burro. Que ridículo vindo de você.")
        assert double[0].confidence >= single[0].confidence


class TestDetectBiases:
    @pytest.mark.parametrize("bias_id,text", [
        ("confirmation_bias", "Só considero as evidências que confirmam minha teoria."),
        ("anchoring_bias", "Fiquei preso na primeira estimativa que vi."),
        ("availability_heuristic", "É a primeira coisa que me vem à mente, então deve ser comum."),
        ("overconfidence_bias", "Tenho certeza absoluta que estou certo."),
    ])
    def test_detects_each_bias(self, detector, bias_id, text):
        matches = detector.detect_biases(text)
        ids_found = [m.fallacy_id for m in matches]
        assert bias_id in ids_found

    def test_bias_category_label(self, detector):
        matches = detector.detect_biases("Tenho certeza absoluta que estou certo.")
        assert matches[0].category == "cognitive_bias"


class TestAnalyze:
    def test_analyze_aggregates_fallacies_and_biases(self, detector):
        text = "Você é burro. Tenho certeza absoluta que estou certo."
        report = detector.analyze(text)
        assert report["total_issues"] == 2
        assert report["clean"] is False
        assert report["fallacy_catalog_size"] == 15
        assert report["bias_catalog_size"] == 4

    def test_analyze_clean_text(self, detector):
        report = detector.analyze("A hipótese foi testada com n=200 e replicada.")
        assert report["clean"] is True
        assert report["total_issues"] == 0

    def test_singleton_available(self):
        from reasoning import fallacy_detector
        assert fallacy_detector.analyze("teste")["clean"] is True
