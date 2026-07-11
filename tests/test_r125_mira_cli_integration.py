# -*- coding: utf-8 -*-
"""
Testes R125 — MIRA como parte de primeira classe do ecossistema
=================================================================
Escritos ANTES da implementação (TDD). Verificam que o pipeline MIRA de
apresentações (R123, `orchestrator.present()`) fica alcançável pelo
usuário nas superfícies do ecossistema: comando direto do CLI, opção de
menu e textos de ajuda.

O `present()` é sempre mockado — os testes não geram deck real nem tocam
disco.

Requisitos: SPEC-935-R125.
"""
import json
import sys

import pytest

from marceloclaro import cli as cli_module
from marceloclaro.orchestrator import MarceloClaroOrchestrator

FAKE_RESULT = {
    "ok": True,
    "passed": True,
    "deck": "producao/apresentacao/deck.html",
    "conformidade": "producao/apresentacao/CONFORMIDADE.md",
    "violations": [],
}


@pytest.fixture
def fake_present(monkeypatch):
    calls = []

    def _fake(self, production_folder):
        calls.append(production_folder)
        return FAKE_RESULT

    monkeypatch.setattr(MarceloClaroOrchestrator, "present", _fake)
    return calls


# ── CA-1/CA-2: comando direto + aliases + uso sem pasta ───────────
class TestDirectCommandApresentacao:
    def test_apresentacao_calls_present_and_prints_json(
        self, monkeypatch, capsys, fake_present
    ):
        monkeypatch.setattr(sys, "argv", ["cli", "apresentacao", "producao/meu-livro"])
        cli_module.main()
        out = capsys.readouterr().out
        assert fake_present == ["producao/meu-livro"]
        parsed = json.loads(out)
        assert parsed["passed"] is True
        assert "deck" in parsed

    def test_present_alias_works(self, monkeypatch, capsys, fake_present):
        monkeypatch.setattr(sys, "argv", ["cli", "present", "pasta/x"])
        cli_module.main()
        assert fake_present == ["pasta/x"]

    def test_mira_alias_works(self, monkeypatch, capsys, fake_present):
        monkeypatch.setattr(sys, "argv", ["cli", "mira", "pasta/y"])
        cli_module.main()
        assert fake_present == ["pasta/y"]

    def test_apresentacao_without_folder_prints_usage_and_exits(
        self, monkeypatch, capsys, fake_present
    ):
        monkeypatch.setattr(sys, "argv", ["cli", "apresentacao"])
        with pytest.raises(SystemExit) as exc_info:
            cli_module.main()
        assert exc_info.value.code == 1
        assert "Uso:" in capsys.readouterr().out
        assert fake_present == []


# ── CA-3: opção de menu [10] ──────────────────────────────────────
class TestInteractiveMenuOption10:
    def test_choice_10_runs_present(self, monkeypatch, capsys, fake_present):
        monkeypatch.setattr(sys, "argv", ["cli"])
        inputs = iter(["10", "producao/livro-x", "0"])
        monkeypatch.setattr("builtins.input", lambda *_: next(inputs))
        cli_module.main()
        out = capsys.readouterr().out
        assert fake_present == ["producao/livro-x"]
        assert "deck" in out.lower() or "apresenta" in out.lower()

    def test_choice_10_empty_folder_is_cancelled(
        self, monkeypatch, capsys, fake_present
    ):
        monkeypatch.setattr(sys, "argv", ["cli"])
        inputs = iter(["10", "", "0"])
        monkeypatch.setattr("builtins.input", lambda *_: next(inputs))
        cli_module.main()
        assert fake_present == []
        assert "cancelad" in capsys.readouterr().out.lower()


# ── CA-4/CA-5: textos de menu, ajuda e dica ───────────────────────
class TestHelpTexts:
    def test_menu_lists_option_10(self):
        assert "[10]" in cli_module.MENU
        assert "MIRA" in cli_module.MENU or "presenta" in cli_module.MENU.lower()

    def test_ajuda_explains_apresentacao(self):
        low = cli_module.AJUDA_TEXT.lower()
        assert "apresenta" in low
        assert "deck" in low or "slide" in low
        # comando direto listado
        assert "apresentacao" in cli_module.AJUDA_TEXT

    def test_unknown_command_hint_mentions_apresentacao(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["cli", "comando-inexistente"])
        cli_module.main()
        assert "apresentacao" in capsys.readouterr().out
