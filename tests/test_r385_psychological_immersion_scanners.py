# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R385: scanners de imersão psicológica (indução
hipnótica, ritmo frenético, imersão sensorial, manipulação narrativa) +
correção do TTR global para MSTTR em scanners/literary_scanners.py."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


EXPECTED_SCANNERS = {
    "hypnotic_induction",
    "frenetic_pacing",
    "sensory_immersion",
    "psychological_manipulation",
}

HYPNOTIC_TEXT = """
Sinta o peso do livro nas suas mãos. Agora, respire. Você já sabe que não
vai parar de ler. O ciclo recomeça. O ciclo continua. O ciclo não se fecha.
Não há tratamento. Não há cura. Não há como fechar o livro e esquecer.
Este livro sabe que você está lendo esta página agora, neste exato momento.
Seu coração acelera. Sua respiração falha. Um arrepio sobe pela sua pele.
O cheiro adocicado invade o quarto enquanto uma luz amarela pisca no escuro
e um som distante ecoa. Pare. Escute. Sinta o gosto metálico na boca.
Você voltou. Foi você quem escolheu continuar. Não importa o que você faça
agora — não há saída.
"""

FLAT_TEXT = "Um texto simples informa que alguém saiu, voltou e terminou."


def test_suite_exports_four_scanners():
    from scanners.psychological_immersion_scanners import (
        PSYCHOLOGICAL_IMMERSION_SCANNER_CLASSES,
    )

    assert len(PSYCHOLOGICAL_IMMERSION_SCANNER_CLASSES) == 4
    assert {cls.scanner_id for cls in PSYCHOLOGICAL_IMMERSION_SCANNER_CLASSES} == EXPECTED_SCANNERS


def test_each_scanner_returns_serializable_contract():
    from scanners.psychological_immersion_scanners import (
        PSYCHOLOGICAL_IMMERSION_SCANNER_CLASSES,
    )

    for scanner_cls in PSYCHOLOGICAL_IMMERSION_SCANNER_CLASSES:
        result = scanner_cls().scan(HYPNOTIC_TEXT)
        assert result["scanner_id"] == scanner_cls.scanner_id
        assert 0.0 <= result["score"] <= 100.0
        assert set(result["dimensions"]) == set(scanner_cls.dimension_names)
        for payload in result["dimensions"].values():
            assert 0.0 <= payload["score"] <= 100.0
            assert isinstance(payload["evidence"], list)


def test_empty_text_returns_insufficient_grade_not_crash():
    from scanners.psychological_immersion_scanners import (
        PSYCHOLOGICAL_IMMERSION_SCANNER_CLASSES,
    )

    for scanner_cls in PSYCHOLOGICAL_IMMERSION_SCANNER_CLASSES:
        result = scanner_cls().scan("")
        assert result["score"] == 0.0
        assert result["grade"] == "insuficiente"


def test_run_suite_aggregates_and_carries_overclaim_guard():
    from scanners.psychological_immersion_scanners import (
        run_psychological_immersion_scanner_suite,
    )

    result = run_psychological_immersion_scanner_suite(HYPNOTIC_TEXT)
    assert result["domain"] == "psychological_immersion"
    assert result["scanner_count"] == 4
    assert 0.0 <= result["psychological_immersion_score"] <= 100.0
    assert "NÃO medem efeito psicológico real" in result["overclaim_guard"]


class TestHypnoticInductionScanner:
    def test_detects_repetition_presupposition_and_temporal_anchor(self):
        from scanners.psychological_immersion_scanners import HypnoticInductionScanner

        result = HypnoticInductionScanner().scan(HYPNOTIC_TEXT)
        dims = result["dimensions"]
        assert dims["repeticao_ritmica"]["score"] > 0
        assert dims["pressuposicao"]["score"] > 0
        assert dims["ancoragem_temporal"]["score"] > 0

    def test_flat_text_scores_low_on_induction(self):
        from scanners.psychological_immersion_scanners import HypnoticInductionScanner

        result = HypnoticInductionScanner().scan(FLAT_TEXT)
        assert result["score"] < 30.0

    def test_warns_against_clinical_overclaim(self):
        from scanners.psychological_immersion_scanners import HypnoticInductionScanner

        result = HypnoticInductionScanner().scan(HYPNOTIC_TEXT)
        assert any("NÃO prova efeito hipnótico real" in w for w in result["warnings"])


class TestFreneticPacingScanner:
    def test_detects_short_sentence_bursts(self):
        from scanners.psychological_immersion_scanners import FreneticPacingScanner

        result = FreneticPacingScanner().scan(HYPNOTIC_TEXT)
        assert result["dimensions"]["fragmentacao_visceral"]["score"] > 0

    def test_detects_punctuation_escalation(self):
        from scanners.psychological_immersion_scanners import FreneticPacingScanner

        heavy = HYPNOTIC_TEXT + ("Não! " * 20) + ("... " * 20) + ("— " * 20)
        light = "Uma frase comum, sem nenhuma pontuação incomum, apenas prosa regular."
        heavy_result = FreneticPacingScanner().scan(heavy)
        light_result = FreneticPacingScanner().scan(light)
        assert (
            heavy_result["dimensions"]["escalada_pontuacao"]["score"]
            >= light_result["dimensions"]["escalada_pontuacao"]["score"]
        )


class TestSensoryImmersionScanner:
    def test_detects_multiple_channels_and_interoception(self):
        from scanners.psychological_immersion_scanners import SensoryImmersionScanner

        result = SensoryImmersionScanner().scan(HYPNOTIC_TEXT)
        dims = result["dimensions"]
        assert dims["amplitude_de_canais"]["score"] > 0
        assert dims["interocepcao_corporal"]["score"] > 0
        assert "coração" in dims["interocepcao_corporal"]["evidence"]

    def test_detects_sensory_crossover_in_same_sentence(self):
        from scanners.psychological_immersion_scanners import SensoryImmersionScanner

        crossover_text = (
            "O cheiro adocicado e a luz amarela invadiram o quarto enquanto "
            "seu coração acelerava e a pele ficava fria."
        )
        result = SensoryImmersionScanner().scan(crossover_text)
        assert result["dimensions"]["cruzamento_sensorial"]["score"] > 0


class TestPsychologicalManipulationScanner:
    def test_detects_double_bind_pattern_not_just_exact_phrases(self):
        from scanners.psychological_immersion_scanners import (
            PsychologicalManipulationScanner,
        )

        text = "Não há cura. Não há tratamento. É impossível escapar agora."
        result = PsychologicalManipulationScanner().scan(text)
        assert result["dimensions"]["dupla_vinculacao"]["score"] > 0

    def test_detects_fourth_wall_break(self):
        from scanners.psychological_immersion_scanners import (
            PsychologicalManipulationScanner,
        )

        result = PsychologicalManipulationScanner().scan(HYPNOTIC_TEXT)
        assert result["dimensions"]["quebra_da_quarta_parede"]["score"] > 0

    def test_detects_imperative_at_paragraph_start_not_only_after_punctuation(self):
        """Achado real ao editar fragmentos do Molambudos: parágrafos em
        LaTeX começam com \\noindent (não com pontuação), então um comando
        imperativo logo no início do parágrafo não era capturado pelo regex
        original (que só olhava início-de-string ou depois de .!?)."""
        from scanners.psychological_immersion_scanners import (
            PsychologicalManipulationScanner,
        )

        text = (
            "\\noindent Você apoiou o livro no colo. Sinta o peso.\n\n"
            "\\noindent Sinta o pulso na garganta. A respiração ficou curta."
        )
        result = PsychologicalManipulationScanner().scan(text)
        assert result["dimensions"]["comando_direto_2a_pessoa"]["score"] > 0
        assert "2 comandos imperativos" in (
            result["dimensions"]["comando_direto_2a_pessoa"]["evidence"][0]
        )

    def test_warns_it_is_technique_not_clinical_effect(self):
        from scanners.psychological_immersion_scanners import (
            PsychologicalManipulationScanner,
        )

        result = PsychologicalManipulationScanner().scan(HYPNOTIC_TEXT)
        assert any("TÉCNICA NARRATIVA" in w for w in result["warnings"])


class TestMSTTRFixesLengthBias:
    """Prova que a troca de TTR global por MSTTR corrige o viés contra
    textos longos (achado real: molambudos.md, ~40k palavras, tinha
    riqueza_lexical=30.27 'fraca' com TTR global, apesar de vocabulário
    rico e sem repetição excessiva)."""

    def test_long_text_with_stable_vocabulary_is_not_penalized(self):
        from scanners.literary_scanners import StyleVoiceScanner

        # 60 janelas de 1000 palavras cada, vocabulário local sempre variado
        # (a única coisa que se repete é o padrão gerado, não o vocabulário)
        chunk = " ".join(f"palavra{i}" for i in range(1000))
        long_text = (". ".join([chunk] * 1) + ". ") * 40
        result = StyleVoiceScanner().scan(long_text)
        assert result["dimensions"]["riqueza_lexical"]["score"] > 60.0

    def test_msttr_evidence_reports_windowed_metric(self):
        from scanners.literary_scanners import StyleVoiceScanner

        result = StyleVoiceScanner().scan(
            "Palavras diferentes aparecem aqui em grande variedade lexical " * 30
        )
        evidence = result["dimensions"]["riqueza_lexical"]["evidence"]
        assert any("MSTTR" in item for item in evidence)

    def test_molambudos_real_text_no_longer_flagged_as_fragile(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "projetos", "molambudos", "molambudos.md",
        )
        if not os.path.exists(path):
            import pytest
            pytest.skip("molambudos.md não presente neste checkout")

        from scanners.literary_scanners import StyleVoiceScanner

        text = open(path, encoding="utf-8").read()
        result = StyleVoiceScanner().scan(text)
        assert result["dimensions"]["riqueza_lexical"]["score"] >= 70.0
        assert "riqueza_lexical" not in " ".join(result["warnings"])
