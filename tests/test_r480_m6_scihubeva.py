# -*- coding: utf-8 -*-
"""Testes da Fase 4 da SPEC-935-R471 (subspec SPEC-935-R480):
M6 — Frontend de download opt-in (SciHubEVA).

Cobertura: CA7 (sem habilitação R470 nenhum caminho aciona SciHubEVA; com
habilitação completa o despacho gera CLIExecutionReceipt com todos os campos
obrigatórios), CA8 (hermético: sem rede/binário/credenciais reais), invariantes
1/3 (GUI nunca altera política open_science_only e os gates fail-closed da
R470), 4 (argv como lista, nunca shell), 5 (sem credenciais em recibos).
"""

from __future__ import annotations

import inspect
import os
from pathlib import Path

import pytest

from workbench.scihubeva_frontend import (
    SCIHUBEVA_RESOLVER,
    SciHubEVARequest,
    SciHubEVAFrontend,
    launch_argv,
    validate_target,
)

REQUIRED_RECEIPT_FIELDS = {
    "command",
    "resolver",
    "policy_effective",
    "enabled_effective",
    "authorization_id",
    "decision",
    "deny_code",
    "timestamp_utc",
    "orchestrator",
    "hash_sha256",
}


def _frontend(monkeypatch, **env) -> SciHubEVAFrontend:
    defaults = {
        "RESTRICTED_RESOLVER_ENABLED": "0",
        "RESTRICTED_RESOLVER_POLICY": "deny",
        "RESTRICTED_RESOLVER_ALLOWLIST": "",
        "RESTRICTED_RESOLVER_AUTHORIZATION_ID": "",
        "RESTRICTED_RESOLVER_RIGHTS_BASIS": "",
        "RESTRICTED_RESOLVER_EVIDENCE_REF": "",
    }
    defaults.update(env)
    for key, value in defaults.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    return SciHubEVAFrontend()


def _full_env() -> dict:
    return {
        "RESTRICTED_RESOLVER_ENABLED": "1",
        "RESTRICTED_RESOLVER_POLICY": "allow",
        "RESTRICTED_RESOLVER_ALLOWLIST": SCIHUBEVA_RESOLVER,
        "RESTRICTED_RESOLVER_AUTHORIZATION_ID": "auth-1",
        "RESTRICTED_RESOLVER_RIGHTS_BASIS": "contractual",
        "RESTRICTED_RESOLVER_EVIDENCE_REF": "ev-1",
    }


class TestSciHubEVADefaultDeny:
    def test_gui_inactive_without_r470_enable(self, monkeypatch) -> None:
        """CA7 A: sem habilitação R470, nenhum caminho aciona SciHubEVA."""
        frontend = _frontend(monkeypatch)
        exit_code, receipt, download = frontend.submit(
            SciHubEVARequest(target_type="doi", target_value="10.1234/example")
        )
        assert receipt["decision"] == "denied"
        assert receipt["deny_code"] == "missing_enable"
        assert download is None

    def test_no_executor_called_when_denied(self, monkeypatch) -> None:
        calls: list = []

        def executor(argv):
            calls.append(argv)

        frontend = _frontend(monkeypatch)
        frontend.submit(
            SciHubEVARequest(target_type="doi", target_value="10.1234/example"),
            executor=executor,
        )
        assert calls == []

    def test_gui_never_alters_policy(self, monkeypatch) -> None:
        """Invariante: GUI não pode mudar a política efetiva da R470."""
        frontend = _frontend(monkeypatch, RESTRICTED_RESOLVER_ENABLED="1",
                             RESTRICTED_RESOLVER_POLICY="deny",
                             RESTRICTED_RESOLVER_ALLOWLIST=SCIHUBEVA_RESOLVER,
                             RESTRICTED_RESOLVER_AUTHORIZATION_ID="auth-1",
                             RESTRICTED_RESOLVER_RIGHTS_BASIS="contractual",
                             RESTRICTED_RESOLVER_EVIDENCE_REF="ev-1")
        exit_code, receipt, download = frontend.submit(
            SciHubEVARequest(target_type="doi", target_value="10.1234/example"),
            requested_policy="allow",  # tentativa da GUI — deve ser ignorada
        )
        assert receipt["decision"] == "denied"
        assert receipt["deny_code"] == "deny_policy"
        assert receipt["policy_effective"] == "deny"

    def test_resolver_outside_allowlist_denied(self, monkeypatch) -> None:
        frontend = _frontend(monkeypatch, RESTRICTED_RESOLVER_ENABLED="1",
                             RESTRICTED_RESOLVER_POLICY="allow",
                             RESTRICTED_RESOLVER_ALLOWLIST="other-resolver",
                             RESTRICTED_RESOLVER_AUTHORIZATION_ID="auth-1",
                             RESTRICTED_RESOLVER_RIGHTS_BASIS="contractual",
                             RESTRICTED_RESOLVER_EVIDENCE_REF="ev-1")
        exit_code, receipt, download = frontend.submit(
            SciHubEVARequest(target_type="doi", target_value="10.1234/example")
        )
        assert receipt["deny_code"] == "unknown_resolver"
        assert download is None

    def test_missing_authorization_denied(self, monkeypatch) -> None:
        env = _full_env()
        env["RESTRICTED_RESOLVER_AUTHORIZATION_ID"] = ""
        frontend = _frontend(monkeypatch, **env)
        exit_code, receipt, download = frontend.submit(
            SciHubEVARequest(target_type="doi", target_value="10.1234/example")
        )
        assert receipt["deny_code"] == "missing_authorization"

    def test_missing_rights_denied(self, monkeypatch) -> None:
        env = _full_env()
        env["RESTRICTED_RESOLVER_RIGHTS_BASIS"] = ""
        frontend = _frontend(monkeypatch, **env)
        exit_code, receipt, download = frontend.submit(
            SciHubEVARequest(target_type="doi", target_value="10.1234/example")
        )
        assert receipt["deny_code"] == "missing_rights"

    def test_missing_evidence_denied(self, monkeypatch) -> None:
        env = _full_env()
        env["RESTRICTED_RESOLVER_EVIDENCE_REF"] = ""
        frontend = _frontend(monkeypatch, **env)
        exit_code, receipt, download = frontend.submit(
            SciHubEVARequest(target_type="doi", target_value="10.1234/example")
        )
        assert receipt["deny_code"] == "missing_evidence"

    def test_ask_policy_requires_confirmation(self, monkeypatch) -> None:
        env = _full_env()
        env["RESTRICTED_RESOLVER_POLICY"] = "ask"
        frontend = _frontend(monkeypatch, **env)
        exit_code, receipt, download = frontend.submit(
            SciHubEVARequest(target_type="doi", target_value="10.1234/example"),
            confirm=False,
        )
        assert receipt["deny_code"] == "ask_confirmation_required"
        assert download is None


class TestSciHubEVAFullAuthorization:
    def test_full_authorization_produces_cli_execution_receipt(self, monkeypatch) -> None:
        """CA7 B: com habilitação completa, o despacho gera CLIExecutionReceipt
        com todos os campos obrigatórios."""
        frontend = _frontend(monkeypatch, **_full_env())
        exit_code, receipt, download = frontend.submit(
            SciHubEVARequest(target_type="doi", target_value="10.1234/example"),
            confirm=True,
        )
        assert exit_code == 0
        assert set(receipt.keys()) >= REQUIRED_RECEIPT_FIELDS
        assert receipt["decision"] == "allowed"
        assert receipt["resolver"] == SCIHUBEVA_RESOLVER
        assert receipt["orchestrator"] == "marceloclaro"
        assert receipt["hash_sha256"]

    def test_download_receipt_pending_manual(self, monkeypatch) -> None:
        """A GUI nunca baixa de verdade nesta versão: pendente execução manual,
        sem arquivo, sem bytes, sem sha256 e com limitações fixas."""
        frontend = _frontend(monkeypatch, **_full_env())
        exit_code, receipt, download = frontend.submit(
            SciHubEVARequest(target_type="doi", target_value="10.1234/example"),
            confirm=True,
        )
        assert download is not None
        assert download["status"] == "pending_manual_execution"
        assert download["path"] is None
        assert download["bytes"] == 0
        assert download["sha256"] is None
        assert "no-redistribution" in download["limitations"]
        assert "not-legal-advice" in download["limitations"]

    def test_no_credentials_in_receipts(self, monkeypatch) -> None:
        frontend = _frontend(monkeypatch, **_full_env())
        exit_code, receipt, download = frontend.submit(
            SciHubEVARequest(target_type="doi", target_value="10.1234/example"),
            confirm=True,
        )
        joined = " ".join(str(v) for v in list(receipt.values()) + list(download.values())).lower()
        assert "sk-" not in joined and "api_key" not in joined and "token" not in joined

    def test_module_does_not_import_subprocess_or_socket(self) -> None:
        """CA8: módulo sem capacidade real de rede/execução de binário."""
        import workbench.scihubeva_frontend as module

        source = inspect.getsource(module)
        assert "subprocess" not in source
        assert "socket" not in source
        assert "urllib.request" not in source


class TestSciHubEVATargetValidation:
    def test_validate_doi(self) -> None:
        assert validate_target(SciHubEVARequest("doi", "10.1234/example")) is True

    def test_validate_doi_rejects_non_doi(self) -> None:
        assert validate_target(SciHubEVARequest("doi", "not-a-doi")) is False

    def test_validate_pmid_and_query(self) -> None:
        assert validate_target(SciHubEVARequest("pmid", "12345678")) is True
        assert validate_target(SciHubEVARequest("query", "diabetes machine learning")) is True

    def test_validate_url_requires_http_scheme(self) -> None:
        assert validate_target(SciHubEVARequest("url", "https://doi.org/10.1234/example")) is True
        assert validate_target(SciHubEVARequest("url", "ftp://example.com/x")) is False
        assert validate_target(SciHubEVARequest("url", "example.com/x")) is False

    def test_unknown_type_rejected(self) -> None:
        assert validate_target(SciHubEVARequest("other", "x")) is False

    def test_empty_value_rejected(self) -> None:
        assert validate_target(SciHubEVARequest("doi", "")) is False


class TestSciHubEVALaunchArgv:
    def test_argv_is_list_not_shell(self) -> None:
        argv = launch_argv(SciHubEVARequest("doi", "10.1234/example"))
        assert isinstance(argv, list)
        assert all(isinstance(a, str) for a in argv)
        assert SCIHUBEVA_RESOLVER in argv
        assert "10.1234/example" in argv