# -*- coding: utf-8 -*-
"""
Testes R120 — Comando `pesquisa` no CLI do marceloclaro
=================================================================
Até o R120, `MarceloClaroOrchestrator.research()` (pipeline de busca em
11 fontes acadêmicas — SPEC-017/R111 — download de PDFs, fichamento e
resenha ABNT/APA) só era acessível programaticamente via Python; o CLI
interativo (`marceloclaro/cli.py`) não expunha nenhum comando para isso.

Requisitos (SPEC-935-R120):
  - Comando direto `python3 -m marceloclaro.cli pesquisa "<tema>"`
    (e alias `research`), com flags opcionais `--max-papers`,
    `--platforms`, `--no-download`
  - Opção `[9]` no menu interativo, chamando o mesmo pipeline
  - `scihub-cli` (fallback de download de PDF pago, já usado por
    `research/downloader.py`) passa a ser checado por `doctor()`/
    `helpdesk()`, como as demais CLIs externas opcionais
  - Nenhuma chamada de rede real nos testes — `orchestrator.research()`
    é sempre mockado
"""

import json
import sys

import pytest

from marceloclaro import cli as cli_module
from marceloclaro.orchestrator import MarceloClaroOrchestrator


FAKE_MANIFEST = {
    "resumo": {
        "artigos_selecionados": 5,
        "pdfs_baixados": 3,
        "convertidos_md": 3,
        "fichamentos": 3,
        "resenhas": 3,
    },
    "folder": "/tmp/pesquisa-fake/2026-07-10-tema",
}


@pytest.fixture
def fake_research(monkeypatch):
    calls = []

    def _fake(self, topic, **kwargs):
        calls.append({"topic": topic, **kwargs})
        return FAKE_MANIFEST

    monkeypatch.setattr(MarceloClaroOrchestrator, "research", _fake)
    return calls


class TestParsePesquisaFlags:
    def test_defaults(self):
        flags = cli_module._parse_pesquisa_flags([])
        assert flags == {"max_papers": 8, "platforms": None, "download": True}

    def test_max_papers_flag(self):
        flags = cli_module._parse_pesquisa_flags(["--max-papers", "3"])
        assert flags["max_papers"] == 3

    def test_platforms_flag_splits_on_comma(self):
        flags = cli_module._parse_pesquisa_flags(["--platforms", "arxiv,pubmed,core"])
        assert flags["platforms"] == ["arxiv", "pubmed", "core"]

    def test_no_download_flag(self):
        flags = cli_module._parse_pesquisa_flags(["--no-download"])
        assert flags["download"] is False

    def test_combined_flags(self):
        flags = cli_module._parse_pesquisa_flags(
            ["--max-papers", "5", "--platforms", "arxiv,core", "--no-download"]
        )
        assert flags == {"max_papers": 5, "platforms": ["arxiv", "core"], "download": False}


class TestDirectCommandPesquisa:
    def test_pesquisa_with_topic_calls_research_and_prints_json(
        self, monkeypatch, capsys, fake_research
    ):
        monkeypatch.setattr(sys, "argv", ["cli", "pesquisa", "IA em odontologia"])
        cli_module.main()
        out = capsys.readouterr().out
        assert fake_research == [
            {"topic": "IA em odontologia", "max_papers": 8, "platforms": None, "download": True}
        ]
        parsed = json.loads(out)
        assert parsed["resumo"]["artigos_selecionados"] == 5

    def test_research_alias_works_the_same(self, monkeypatch, capsys, fake_research):
        monkeypatch.setattr(sys, "argv", ["cli", "research", "tema qualquer"])
        cli_module.main()
        assert fake_research[0]["topic"] == "tema qualquer"

    def test_pesquisa_respects_flags(self, monkeypatch, capsys, fake_research):
        monkeypatch.setattr(
            sys, "argv",
            ["cli", "pesquisa", "tema", "--max-papers", "2", "--no-download"],
        )
        cli_module.main()
        assert fake_research[0]["max_papers"] == 2
        assert fake_research[0]["download"] is False

    def test_pesquisa_without_topic_prints_usage_and_exits(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["cli", "pesquisa"])
        with pytest.raises(SystemExit) as exc_info:
            cli_module.main()
        assert exc_info.value.code == 1
        assert "Uso:" in capsys.readouterr().out


class TestInteractiveMenuOption9:
    def test_choice_9_runs_research_and_prints_summary(self, monkeypatch, capsys, fake_research):
        monkeypatch.setattr(sys, "argv", ["cli"])
        inputs = iter(["9", "IA em odontologia", "", "s", "0"])
        monkeypatch.setattr("builtins.input", lambda *_: next(inputs))
        cli_module.main()
        out = capsys.readouterr().out
        assert fake_research[0]["topic"] == "IA em odontologia"
        assert fake_research[0]["max_papers"] == 8
        assert fake_research[0]["download"] is True
        assert "Pesquisa concluída" in out
        assert "5 artigos" in out

    def test_choice_9_empty_topic_is_cancelled_without_calling_research(
        self, monkeypatch, capsys, fake_research
    ):
        monkeypatch.setattr(sys, "argv", ["cli"])
        inputs = iter(["9", "", "0"])
        monkeypatch.setattr("builtins.input", lambda *_: next(inputs))
        cli_module.main()
        assert fake_research == []
        assert "cancelad" in capsys.readouterr().out.lower()


class TestDoctorScihubCheck:
    def test_scihub_cli_registered_in_external_clis(self):
        from marceloclaro.doctor import EXTERNAL_CLIS
        assert "scihub-cli" in EXTERNAL_CLIS

    def test_check_external_clis_never_fails_on_missing_scihub(self, monkeypatch):
        import shutil as shutil_mod
        from marceloclaro import doctor as doctor_module

        monkeypatch.setattr(shutil_mod, "which", lambda name: None)
        check = doctor_module._check_external_clis()
        assert check.status == "warn"
        assert "scihub-cli" in check.detail
