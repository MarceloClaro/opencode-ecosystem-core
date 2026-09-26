"""Testes RED/GREEN da SPEC-971 — Integração da CLI Gemini Notebook (nlm) no doctor.

A CLI `nlm` (pacote PyPI `notebooklm-mcp-cli`, MIT, v0.11.6) dá acesso
programático ao Gemini Notebook (ex-NotebookLM) do Google. Decisão R548:
ADOTAR como CLI externa opt-in (uso do operador, sem acoplamento ao pipeline
automático de pesquisa — APIs internas não documentadas; ver veredito R474).

Suíte hermética: nenhuma chamada real a subprocess, rede ou LLM.
"""
import importlib

import pytest


def _load_doctor():
    doctor_mod = importlib.import_module("marceloclaro.doctor")
    return doctor_mod


# ── 1. Registro no dicionário EXTERNAL_CLIS ───────────────────────────

class TestNlmRegisteredInExternalClis:
    def test_nlm_registered_in_external_clis(self):
        doctor_mod = _load_doctor()
        assert "nlm" in doctor_mod.EXTERNAL_CLIS

    def test_nlm_install_command_is_pip(self):
        doctor_mod = _load_doctor()
        assert doctor_mod.EXTERNAL_CLIS["nlm"] == "pip install notebooklm-mcp-cli"

    def test_nlm_upstream_is_mit_and_not_core(self):
        # A integração é opt-in (CLI externa opcional), consistente com as
        # demais ferramentas de primeira classe — nunca no caminho crítico.
        doctor_mod = _load_doctor()
        assert "notebooklm-mcp-cli" in doctor_mod.EXTERNAL_CLIS["nlm"]


# ── 2. Comportamento do check external_clis ───────────────────────────

class TestCheckExternalClisNlm:
    def test_check_external_clis_warns_when_nlm_missing(self, monkeypatch):
        doctor_mod = _load_doctor()
        monkeypatch.setattr(doctor_mod.shutil, "which", lambda name: None)
        check = doctor_mod._check_external_clis()
        assert check.status == "warn"
        assert "nlm" in check.detail
        assert "pip install notebooklm-mcp-cli" in check.detail

    def test_check_external_clis_passes_when_nlm_present(self, monkeypatch):
        doctor_mod = _load_doctor()
        monkeypatch.setattr(doctor_mod.shutil, "which", lambda name: f"/usr/bin/{name}")
        check = doctor_mod._check_external_clis()
        assert check.status == "pass"
        assert "nlm" in check.detail

    def test_check_external_clis_missing_only_nlm(self, monkeypatch):
        doctor_mod = _load_doctor()
        present = set(doctor_mod.EXTERNAL_CLIS) - {"nlm"}
        monkeypatch.setattr(
            doctor_mod.shutil,
            "which",
            lambda name: f"/usr/bin/{name}" if name in present else None,
        )
        check = doctor_mod._check_external_clis()
        assert check.status == "warn"
        assert "1/" in check.detail
        assert "nlm -> pip install notebooklm-mcp-cli" in check.detail


# ── 3. Helpdesk: sugestão continua válida com nlm ─────────────────────

class TestHelpdeskWithNlm:
    def test_helpdesk_guidance_references_nlm_when_missing(self, monkeypatch):
        helpdesk_mod = importlib.import_module("marceloclaro.helpdesk")
        doctor_mod = _load_doctor()
        monkeypatch.setattr(doctor_mod.shutil, "which", lambda name: None)  # qualificador global restaurado no teardown
        fake_report = {
            "overall": "degraded",
            "checks": [doctor_mod._check_external_clis().to_dict()],
            "checks_total": 1,
            "checks_passed": 0,
            "checks_warned": 1,
            "checks_failed": 0,
            "duration_seconds": 0.0,
        }
        monkeypatch.setattr(helpdesk_mod, "run_doctor", lambda: fake_report)
        report = helpdesk_mod.run_helpdesk()
        assert len(report["guidance"]) == 1
        assert "nlm" in report["guidance"][0]["suggestion"]
        assert "notebooklm-mcp-cli" in report["guidance"][0]["suggestion"]