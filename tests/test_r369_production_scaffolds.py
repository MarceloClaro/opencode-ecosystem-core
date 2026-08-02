# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R369 — andaimes de raciocínio produtivo."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reasoning.production_scaffolds import (  # noqa: E402
    LITERARY_PLAN_FIELDS,
    SCIENTIFIC_MOVES,
    ContractError,
    audit_scientific_manuscript,
    literary_distinctiveness_report,
    select_scaffold,
    validate_literary_plan,
)


def _manuscrito_completo():
    return {
        "introducao": (
            "O problema de pesquisa é a perda de voz autoral em tradução. "
            "Há uma lacuna: o tema é pouco explorado na literatura."
        ),
        "fundamentacao": (
            "Nossa hipótese é que marcadores regionais preservados aumentam "
            "a aceitação do leitor."
        ),
        "metodo": (
            "O método combina corpus rotulado e análise por regras; a "
            "amostra tem 18 casos."
        ),
        "resultados": (
            "Os resultados mostram evidência de precisão 1.00 e recall 0.86 "
            "na tabela 2."
        ),
        "discussao": (
            "Entretanto, um contra-argumento é que o corpus interno limita "
            "a generalização; consideramos a alternativa de corpus externo."
        ),
        "conclusao": (
            "A limitação principal é o tamanho do corpus. A contribuição é "
            "um protocolo auditável de tradução cultural."
        ),
    }


# ═══════════════════════════════════════════════════════════════════════
# 1. Andaime científico
# ═══════════════════════════════════════════════════════════════════════

class TestAndaimeCientifico:
    def test_manuscrito_completo_sem_missing_move(self):
        out = audit_scientific_manuscript(_manuscrito_completo())
        missing = [f for f in out["findings"] if f["code"] == "MISSING_MOVE"]
        assert missing == []
        assert set(out["moves_presentes"]) == set(SCIENTIFIC_MOVES.keys())

    def test_sem_metodo_e_limitacao_gate_humano(self):
        sections = _manuscrito_completo()
        sections["metodo"] = "Texto genérico sem nada."
        sections["conclusao"] = "A contribuição é um arcabouço auditável."
        out = audit_scientific_manuscript(sections)
        codes = {(f["code"], f["move"]) for f in out["findings"]
                 if f["code"] == "MISSING_MOVE"}
        assert ("MISSING_MOVE", "metodo") in codes
        assert ("MISSING_MOVE", "limitacao") in codes
        highs = [f for f in out["findings"]
                 if f["code"] == "MISSING_MOVE" and f["severity"] == "high"]
        assert len(highs) >= 2
        assert out["human_gate"] == "required"

    def test_entrada_invalida_falha_fechado(self):
        with pytest.raises(ContractError):
            audit_scientific_manuscript({})
        with pytest.raises(ContractError):
            audit_scientific_manuscript("não é um dict")

    def test_disclaimer_nao_atesta_relevancia(self):
        out = audit_scientific_manuscript(_manuscrito_completo())
        assert "não atesta" in out["disclaimer"].lower()

    def test_engine_hints_existem_no_pacote_reasoning(self):
        import reasoning.engines as engines
        valid = {n.lower() for n in dir(engines)}
        peirce = {"abducao", "inducao", "deducao", "analogia", "contrafactual"}
        for move, spec in SCIENTIFIC_MOVES.items():
            for hint in spec["engine_hints"]:
                token = hint.lower().replace("-", "")
                assert (
                    any(token in v for v in valid) or token in peirce
                ), f"{move}: engine_hint {hint!r} não corresponde a motor/Peirce"


# ═══════════════════════════════════════════════════════════════════════
# 2. Auditoria de alegações de novidade
# ═══════════════════════════════════════════════════════════════════════

class TestNoveltyClaims:
    def _audit_text(self, text):
        sections = _manuscrito_completo()
        sections["discussao"] = sections["discussao"] + " " + text
        return audit_scientific_manuscript(sections)

    def test_inedito_sem_ancoradouro_high(self):
        out = self._audit_text("Esta é uma abordagem inédita para o problema.")
        claims = [f for f in out["findings"]
                  if f["code"] == "UNSUPPORTED_NOVELTY_CLAIM"]
        assert claims and claims[0]["severity"] == "high"
        assert out["human_gate"] == "required"

    def test_inedito_com_citacao_sem_achado(self):
        out = self._audit_text(
            "Esta abordagem é inédita em comparação com \\cite{smith2024}."
        )
        assert not [f for f in out["findings"]
                    if f["code"] == "UNSUPPORTED_NOVELTY_CLAIM"]

    def test_novel_com_comparacao_textual_sem_achado(self):
        out = self._audit_text(
            "The approach is novel compared to prior graph methods (Silva, 2025)."
        )
        assert not [f for f in out["findings"]
                    if f["code"] == "UNSUPPORTED_NOVELTY_CLAIM"]

    def test_state_of_the_art_sem_ancoradouro_flagrado(self):
        out = self._audit_text("Our system achieves state-of-the-art results.")
        assert [f for f in out["findings"]
                if f["code"] == "UNSUPPORTED_NOVELTY_CLAIM"]

    def test_primeira_diferenca_termo_econometrico_nao_e_falso_positivo(self):
        """Regressão: achado real na validação do manuscrito USP (R373).

        'Primeiras diferenças' é termo econométrico padrão (first
        differences), não alegação de novidade sobre o próprio trabalho.
        'primeiro/primeira' bruto como gatilho causava falso positivo em
        qualquer uso ordinal comum do português ('primeira diferença',
        'primeiro trimestre', 'primeira vista', 'primeiro passo').
        """
        out = self._audit_text(
            "Primeiras diferenças ou modelos VECM reduziriam as magnitudes "
            "observadas neste primeiro trimestre da série."
        )
        assert not [f for f in out["findings"]
                    if f["code"] == "UNSUPPORTED_NOVELTY_CLAIM"]

    def test_pela_primeira_vez_continua_flagrado(self):
        """Contraste: alegação de prioridade genuína ainda deve ser pega."""
        out = self._audit_text(
            "Pela primeira vez, mostramos essa relação em dados brasileiros."
        )
        assert [f for f in out["findings"]
                if f["code"] == "UNSUPPORTED_NOVELTY_CLAIM"]

    def test_primeiro_estudo_a_continua_flagrado(self):
        out = self._audit_text(
            "Este é o primeiro estudo a integrar as seis dimensões analisadas."
        )
        assert [f for f in out["findings"]
                if f["code"] == "UNSUPPORTED_NOVELTY_CLAIM"]


# ═══════════════════════════════════════════════════════════════════════
# 3. Plano literário contratual
# ═══════════════════════════════════════════════════════════════════════

def _plano():
    return {
        "voz": "primeira pessoa, oral, sertaneja, memorialística",
        "conflito_central": "a memória enterrada que retorna e contamina",
        "simbolos": ["olho", "vala", "diário", "fome"],
        "estrategia_estranhamento": (
            "o diário narra o leitor: a segunda pessoa é progressivamente "
            "absorvida como Paciente 1.263"
        ),
        "cliches_a_evitar": ["silêncio ensurdecedor", "frio na espinha"],
    }


class TestPlanoLiterario:
    def test_plano_valido(self):
        validated = validate_literary_plan(_plano())
        assert validated["simbolos"] == ["olho", "vala", "diário", "fome"]

    def test_campos_obrigatorios(self):
        assert set(LITERARY_PLAN_FIELDS) == {
            "voz", "conflito_central", "simbolos",
            "estrategia_estranhamento", "cliches_a_evitar",
        }
        for field in ("voz", "conflito_central", "estrategia_estranhamento"):
            plano = _plano()
            plano[field] = "  "
            with pytest.raises(ContractError):
                validate_literary_plan(plano)

    def test_sem_simbolos_falha(self):
        plano = _plano()
        plano["simbolos"] = []
        with pytest.raises(ContractError):
            validate_literary_plan(plano)


# ═══════════════════════════════════════════════════════════════════════
# 4. Relatório de distintividade medido
# ═══════════════════════════════════════════════════════════════════════

TEXTO_CLICHE = (
    "Um frio na espinha percorreu o menino. O silêncio ensurdecedor da "
    "noite caiu. Suas lágrimas amargas rolaram. O frio na espinha voltou."
)


class TestDistintividade:
    def test_campos_medidos(self):
        report = literary_distinctiveness_report(TEXTO_CLICHE)
        assert report["measured"] is True
        assert report["claim"] == "internal-descriptive-measurement"
        assert 0.0 < report["type_token_ratio"] <= 1.0
        assert report["sentence_count"] == 4
        assert report["cliche_hits"], "clichês do texto deveriam ser detectados"
        hits = {h["expressao"] for h in report["cliche_hits"]}
        assert "frio na espinha" in hits
        assert "silêncio ensurdecedor" in hits

    def test_cliche_repetido_conta_ocorrencias(self):
        report = literary_distinctiveness_report(TEXTO_CLICHE)
        frio = [h for h in report["cliche_hits"]
                if h["expressao"] == "frio na espinha"][0]
        assert frio["ocorrencias"] == 2

    def test_disclaimer_nega_veredito(self):
        report = literary_distinctiveness_report(TEXTO_CLICHE)
        low = report["disclaimer"].lower()
        assert "não" in low and ("qualidade" in low or "disrup" in low)

    def test_determinismo(self):
        assert literary_distinctiveness_report(TEXTO_CLICHE) == \
            literary_distinctiveness_report(TEXTO_CLICHE)

    def test_texto_vazio_falha_fechado(self):
        with pytest.raises(ContractError):
            literary_distinctiveness_report("   ")


# ═══════════════════════════════════════════════════════════════════════
# 5. Seleção de andaime via camada epistêmica
# ═══════════════════════════════════════════════════════════════════════

class TestSelectScaffold:
    def test_tarefa_estatistica_scientific(self):
        assert select_scaffold(
            "análise estatística com regressão e amostra estratificada"
        ) == "scientific"

    def test_tarefa_matematica_scientific(self):
        assert select_scaffold(
            "prova formal do teorema com lógica dedutiva"
        ) == "scientific"

    def test_tarefa_literaria_literary(self):
        assert select_scaffold(
            "tradução literária preservando a voz cultural da narrativa"
        ) == "literary"

    def test_sem_sinais_indeterminate(self):
        assert select_scaffold("frobnicar o quux xyzzy") == "indeterminate"
