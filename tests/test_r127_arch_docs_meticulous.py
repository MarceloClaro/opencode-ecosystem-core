# -*- coding: utf-8 -*-
"""
Testes R127 — Documentação minuciosa da arquitetura (dupla-registro)
=====================================================================
TDD de documentação: verifica que o subsistema de Apresentações MIRA
(R123–R126) foi documentado com legenda (função de cada elemento) e
processo (os 6 estágios), em dupla-registro (Leigo + PhD), e que o
agente `mira-presenter` (R126) aparece nos diagramas e o mapa 3D reflete
as contagens reconciliadas.

Requisitos: SPEC-935-R127.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
ARCH = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
MAP = (ROOT / "docs" / "architecture_map.html").read_text(encoding="utf-8")

MIRA_STAGES = ["extract", "plan", "copywrite", "build", "animate", "validate"]


# ── CA-1: legenda do subsistema MIRA (elementos) ──────────────────
def test_readme_legenda_mira_nomeia_elementos():
    assert "MiraDeckPipeline" in README
    assert "MiraEngine" in README
    assert "mira-presenter" in README


def test_readme_legenda_mira_dupla_registro():
    # a legenda MIRA precisa endereçar leigo E phd — procuramos a seção
    # e a presença dos dois registros próximos ao termo MIRA
    idx = README.find("Apresentações MIRA")
    assert idx != -1, "seção de legenda MIRA ausente no README"
    janela = README[idx: idx + 2500].lower()
    assert "leigo" in janela
    assert "phd" in janela


# ── CA-2: processo dos 6 estágios ─────────────────────────────────
def test_readme_processo_seis_estagios():
    idx = README.lower().find("como funciona a apresentação mira")
    assert idx != -1, "seção de processo MIRA ausente no README"
    bloco = README[idx: idx + 6000].lower()
    for stage in MIRA_STAGES:
        assert stage in bloco, f"estágio '{stage}' não explicado no processo MIRA"


# ── CA-3: nó do agente nos diagramas ──────────────────────────────
def test_diagramas_incluem_mira_presenter():
    assert "mira-presenter" in README or "MiraAgent" in README
    assert "mira-presenter" in ARCH or "MiraAgent" in ARCH


# ── CA-4: tabela de specs em ARCHITECTURE ─────────────────────────
def test_architecture_tabela_specs_r126_r127():
    assert "SPEC-935-R126" in ARCH
    assert "SPEC-935-R127" in ARCH


# ── CA-5: mapa 3D menciona o agente e contagens ───────────────────
def test_mapa_menciona_mira_presenter():
    assert "mira-presenter" in MAP


def test_mapa_contagens_atualizadas():
    assert "R127" in MAP
    # a contagem de ciclos deve refletir 85 (R47–R127 = 81 na faixa, mas
    # o total documentado no cycles.json é 85)
    assert "85" in MAP


# ── CA-6: README reflete contagens reconciliadas ──────────────────
def test_readme_contagens_reconciliadas():
    assert "R47 a R127" in README or "R47–R127" in README
    assert "85" in README


# ── CA-7: blocos Mermaid balanceados (README/ARCHITECTURE) ────────
@pytest.mark.parametrize("texto,nome", [(README, "README"), (ARCH, "ARCHITECTURE")])
def test_mermaid_balanceado(texto, nome):
    for m in re.finditer(r"```mermaid\n(.*?)```", texto, re.DOTALL):
        b = m.group(1)
        assert b.count("[") == b.count("]"), f"colchetes desbalanceados em {nome}"
        assert b.count("(") == b.count(")"), f"parênteses desbalanceados em {nome}"
