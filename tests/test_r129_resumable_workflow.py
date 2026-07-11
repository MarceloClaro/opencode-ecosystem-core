# -*- coding: utf-8 -*-
"""
Testes R129 — Fluxo de trabalho resiliente/resumível (checkpoints)
===================================================================
TDD de documentação: garante que existe um checkpoint vivo (PROGRESS.md)
com estrutura mínima e que o CLAUDE.md documenta a disciplina de retomada,
para que o trabalho sobreviva ao fim de uma sessão.

Requisitos: SPEC-935-R129.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_progress_md_existe():
    assert (ROOT / "PROGRESS.md").exists(), "PROGRESS.md ausente na raiz"


def test_progress_md_tem_secoes_esperadas():
    txt = (ROOT / "PROGRESS.md").read_text(encoding="utf-8").lower()
    assert "estado atual" in txt
    assert "próximos passos" in txt or "proximos passos" in txt
    assert "como retomar" in txt


def test_claude_md_documenta_retomada():
    txt = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "PROGRESS.md" in txt
    low = txt.lower()
    assert "retomada" in low or "retomar" in low or "checkpoint" in low
