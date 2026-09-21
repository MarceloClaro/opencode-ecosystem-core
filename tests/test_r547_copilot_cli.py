"""Testes RED/GREEN da SPEC-970 — Integração da CLI GitHub Copilot no doctor.

A CLI oficial `@github/copilot` (binário `copilot`, antiga `@github/copilot-cli`
que retorna E404 no registry) foi instalada globalmente via npm e agora é
monitorada pelo check `external_clis` do doctor, como as demais CLIs de
primeira classe (SPEC-935-R116, R120, R473).

Suíte hermética: nenhuma chamada real a subprocess, rede ou LLM.
"""
import importlib

import pytest


def _load_doctor():
    doctor_mod = importlib.import_module("marceloclaro.doctor")
    return doctor_mod


# ── 1. Registro no dicionário EXTERNAL_CLIS ───────────────────────────

class TestCopilotRegisteredInExternalClis:
    def test_copilot_registered_in_external_clis(self):
        doctor_mod = _load_doctor()
        assert "copilot" in doctor_mod.EXTERNAL_CLIS

    def test_copilot_install_command_is_npm_global(self):
        doctor_mod = _load_doctor()
        assert doctor_mod.EXTERNAL_CLIS["copilot"] == "npm install -g @github/copilot"

    def test_legacy_copilot_cli_name_not_expected(self):
        # O pacote legado @github/copilot-cli retorna E404 no registry; o nome
        # canônico do pacote atual é @github/copilot (binário `copilot`).
        doctor_mod = _load_doctor()
        assert "copilot-cli" not in doctor_mod.EXTERNAL_CLIS["copilot"]


# ── 2. Comportamento do check external_clis ───────────────────────────

class TestCheckExternalClisCopilot:
    def test_check_external_clis_warns_when_copilot_missing(self, monkeypatch):
        doctor_mod = _load_doctor()
        # Nenhuma CLI presente → warn (nunca fail); mensagem cita o copilot.
        monkeypatch.setattr(doctor_mod.shutil, "which", lambda name: None)
        check = doctor_mod._check_external_clis()
        assert check.status == "warn"
        assert "copilot" in check.detail
        assert "npm install -g @github/copilot" in check.detail

    def test_check_external_clis_passes_when_copilot_present(self, monkeypatch):
        doctor_mod = _load_doctor()
        # Todas as CLIs presentes (incluindo copilot) → pass.
        monkeypatch.setattr(doctor_mod.shutil, "which", lambda name: f"/usr/bin/{name}")
        check = doctor_mod._check_external_clis()
        assert check.status == "pass"
        assert "copilot" in check.detail

    def test_check_external_clis_missing_only_copilot(self, monkeypatch):
        doctor_mod = _load_doctor()
        # Apenas o copilot ausente → warn com somente o copilot na sugestão.
        present = set(doctor_mod.EXTERNAL_CLIS) - {"copilot"}
        monkeypatch.setattr(
            doctor_mod.shutil,
            "which",
            lambda name: f"/usr/bin/{name}" if name in present else None,
        )
        check = doctor_mod._check_external_clis()
        assert check.status == "warn"
        assert "1/" in check.detail
        assert "copilot -> npm install -g @github/copilot" in check.detail


# ── 3. Helpdesk: sugestão continua válida com copilot ─────────────────

class TestHelpdeskWithCopilot:
    def test_helpdesk_guidance_references_copilot_when_missing(self, monkeypatch):
        helpdesk_mod = importlib.import_module("marceloclaro.helpdesk")
        doctor_mod = _load_doctor()
        doctor_mod.shutil.which = lambda name: None  # type: ignore[assignment]
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
        assert "copilot" in report["guidance"][0]["suggestion"]