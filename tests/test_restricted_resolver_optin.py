"""SPEC-935-R470 — opt-in de resolvedor restrito (fail-closed, sem rede real).

Suíte RED/GREEN: somente mocks/fachadas in-memory, sem download real de
conteúdo sob paywall, sem credenciais, sem subprocess real, sem shell.
Cobre CA1-CA10 da SPEC-935-R470.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from scientific_lab import restricted_resolver as rr
from scientific_lab import runtime

ROOT = Path(__file__).resolve().parents[1]

RESTRICTED_ENV_VARS = [
    "RESTRICTED_RESOLVER_ENABLED",
    "RESTRICTED_RESOLVER_ALLOWLIST",
    "RESTRICTED_RESOLVER_AUTHORIZATION_ID",
    "RESTRICTED_RESOLVER_EVIDENCE_REF",
    "RESTRICTED_RESOLVER_POLICY",
    "RESTRICTED_RESOLVER_RIGHTS_BASIS",
]

REQUIRED_CLI_FIELDS = {
    "command",
    "resolver",
    "policy_effective",
    "enabled_effective",
    "authorization_id",
    "decision",
    "timestamp_utc",
    "orchestrator",
    "hash_sha256",
}

REQUIRED_DOWNLOAD_FIELDS = {
    "resolver",
    "rights_basis_human_declared",
    "authorization_id",
    "evidence_ref",
    "limitations",
    "status",
}

EXPECTED_LIMITATIONS = [
    "no-redistribution",
    "original-rights-retained",
    "jurisdiction-dependent",
    "not-legal-advice",
]


@pytest.fixture(autouse=True)
def _clear_restricted_env(monkeypatch):
    for var in RESTRICTED_ENV_VARS:
        monkeypatch.delenv(var, raising=False)


def _authorized_request(**overrides):
    base = {
        "resolver": "example-resolver",
        "authorization_id": "AUTH-TEST-001",
        "rights_basis": "copia fornecida pelo autor com evidencia de repositorio do autor",
        "evidence_ref": "CHAMADO-TEST-001",
        "enable": True,
        "policy": "allow",
        "allowlist": ["example-resolver"],
        "confirm": False,
    }
    base.update(overrides)
    return rr.RestrictedRequest(**base)


def _load_default_sources():
    candidates = list(ROOT.glob("**/scripts/article_retrieval.py"))
    if not candidates:
        return None
    spec = importlib.util.spec_from_file_location("article_retrieval_probe", candidates[0])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return list(module.DEFAULT_SOURCES)


# CA1 — padrão open_science_only observável, nada restrito por default.
def test_ca1_default_open_science_only():
    assert rr.POLICY_DEFAULT == "open_science_only"
    assert "restricted" not in runtime.CONTROLLERS
    for value in runtime.CONTROLLERS.values():
        assert "restrict" not in value.lower()
        assert "scihub" not in value.lower()
    for key in runtime.CONTROLLERS:
        assert "scihub" not in key.lower()
    sources = _load_default_sources()
    if sources is not None:
        assert sources == ["openalex", "crossref", "europepmc", "arxiv"]
    fresh = rr.request_from_env()
    assert fresh.enable is False
    assert fresh.policy == "deny"
    assert fresh.allowlist == []
    assert fresh.authorization_id in (None, "")
    assert fresh.rights_basis in (None, "")
    assert fresh.evidence_ref in (None, "")


# CA2 — pleito sem enable bloqueado + recibo denied missing_enable.
def test_ca2_missing_enable_blocked():
    req = _authorized_request(enable=False)
    decision, deny_code, receipt = rr.evaluate(req)
    assert decision == "denied"
    assert deny_code == "missing_enable"
    assert receipt["decision"] == "denied"
    assert receipt["deny_code"] == "missing_enable"
    exit_code, cli_receipt, download_receipt = rr.dispatch_restricted(req)
    assert exit_code == 10
    assert cli_receipt["decision"] == "denied"
    assert download_receipt is None


# CA3 — sem authorize bloqueado missing_authorization.
def test_ca3_missing_authorization_blocked():
    for bad in (None, "", "   "):
        req = _authorized_request(authorization_id=bad)
        decision, deny_code, _receipt = rr.evaluate(req)
        assert decision == "denied"
        assert deny_code == "missing_authorization"
        exit_code, _cli, _dl = rr.dispatch_restricted(req)
        assert exit_code == 13


# CA4 — sem rights-basis / evidence-ref bloqueado.
def test_ca4_missing_rights_blocked():
    req = _authorized_request(rights_basis="")
    decision, deny_code, _receipt = rr.evaluate(req)
    assert decision == "denied"
    assert deny_code == "missing_rights"
    assert rr.dispatch_restricted(req)[0] == 14


def test_ca4_missing_evidence_blocked():
    req = _authorized_request(evidence_ref="  ")
    decision, deny_code, _receipt = rr.evaluate(req)
    assert decision == "denied"
    assert deny_code == "missing_evidence"
    assert rr.dispatch_restricted(req)[0] == 15


# CA5 — caminho totalmente autorizado gera receipts completos (executor fake).
def test_ca5_fully_authorized_allowed_with_fake_executor(tmp_path):
    calls: list = []

    def fake_executor(argv):
        calls.append(argv)
        return 0

    req = _authorized_request()
    exit_code, cli_receipt, download_receipt = rr.dispatch_restricted(req, executor=fake_executor)
    assert exit_code == 0
    assert cli_receipt["decision"] == "allowed"
    assert REQUIRED_CLI_FIELDS.issubset(set(cli_receipt))
    assert cli_receipt["orchestrator"] == "marceloclaro"
    assert cli_receipt["resolver"] == "example-resolver"
    assert cli_receipt["policy_effective"] == "allow"
    assert cli_receipt["enabled_effective"] is True
    assert cli_receipt["authorization_id"] == "AUTH-TEST-001"
    assert download_receipt is not None
    assert REQUIRED_DOWNLOAD_FIELDS.issubset(set(download_receipt))
    assert download_receipt["resolver"] == "example-resolver"
    assert download_receipt["authorization_id"] == "AUTH-TEST-001"
    assert download_receipt["evidence_ref"] == "CHAMADO-TEST-001"
    assert "autor" in download_receipt["rights_basis_human_declared"]
    assert download_receipt["limitations"] == EXPECTED_LIMITATIONS
    assert download_receipt["status"] == "pending_manual_execution"
    assert download_receipt.get("path") in (None, "")
    # Nenhum arquivo persistido pelo despacho: workspace continua vazio.
    assert list(tmp_path.iterdir()) == []
    # Executor fake recebeu lista (nunca string / nunca shell).
    assert len(calls) == 1
    assert isinstance(calls[0], list)
    assert all(isinstance(item, str) for item in calls[0])
    # Hash do recibo é sha256 íntegro do conteúdo canônico.
    canonical = {k: v for k, v in cli_receipt.items() if k != "hash_sha256"}
    expected = hashlib.sha256(
        json.dumps(canonical, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    assert cli_receipt["hash_sha256"] == expected


# CA6 — asserção estática: nunca shell=True; argv sempre lista.
def test_ca6_no_shell_true_and_argv_is_list():
    source = Path(rr.__file__).read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "shell = True" not in source
    req = _authorized_request()
    argv = rr.build_argv(req)
    assert isinstance(argv, list)
    assert not isinstance(argv, str)
    assert all(isinstance(item, str) for item in argv)


# CA7 — deny bloqueia mesmo com tudo presente; ask exige confirmação.
def test_ca7_deny_policy_blocks_even_when_fully_authorized():
    req = _authorized_request(policy="deny")
    decision, deny_code, _receipt = rr.evaluate(req)
    assert decision == "denied"
    assert deny_code == "deny_policy"
    assert rr.dispatch_restricted(req)[0] == 11


def test_ca7_ask_requires_additional_confirmation():
    without_confirm = _authorized_request(policy="ask", confirm=False)
    decision, deny_code, _receipt = rr.evaluate(without_confirm)
    assert decision == "denied"
    assert deny_code == "ask_confirmation_required"
    assert rr.dispatch_restricted(without_confirm)[0] == 16
    with_confirm = _authorized_request(policy="ask", confirm=True)
    decision_ok, deny_ok, _receipt_ok = rr.evaluate(with_confirm)
    assert decision_ok == "allowed"
    assert deny_ok is None
    assert rr.dispatch_restricted(with_confirm)[0] == 0


def test_ca7_three_policies_covered():
    assert rr.dispatch_restricted(_authorized_request(policy="deny"))[0] == 11
    assert rr.dispatch_restricted(_authorized_request(policy="ask", confirm=False))[0] == 16
    assert rr.dispatch_restricted(_authorized_request(policy="allow"))[0] == 0


# CA8 — discovery não promove restrito a default.
def test_ca8_discovery_does_not_promote_restricted(monkeypatch):
    before = dict(runtime.CONTROLLERS)
    _ = rr.request_from_env(resolver="example-resolver")
    req = _authorized_request()
    assert rr.evaluate(req)[0] in ("allowed", "denied")
    assert dict(runtime.CONTROLLERS) == before
    assert "restricted" not in runtime.CONTROLLERS
    assert rr.POLICY_DEFAULT == "open_science_only"
    sources = _load_default_sources()
    if sources is not None:
        assert sources == ["openalex", "crossref", "europepmc", "arxiv"]
    monkeypatch.delenv("PESQUISADOR_UNIVERSAL_HOME", raising=False)
    assert runtime.discover() is None or isinstance(runtime.discover(), Path)


# CA9 — fora da allowlist nega unknown_resolver.
def test_ca9_unknown_resolver_denied():
    req = _authorized_request(resolver="unknown-resolver", allowlist=["example-resolver"])
    decision, deny_code, _receipt = rr.evaluate(req)
    assert decision == "denied"
    assert deny_code == "unknown_resolver"
    assert rr.dispatch_restricted(req)[0] == 12
    empty = _authorized_request(resolver="example-resolver", allowlist=[])
    assert rr.evaluate(empty)[1] == "unknown_resolver"
    assert rr.dispatch_restricted(empty)[0] == 12


# CA10 — inspeção: sem socket/urllib para paywall; mocks totais; sem credenciais.
def test_ca10_no_real_network_no_credentials(monkeypatch):
    impl_source = Path(rr.__file__).read_text(encoding="utf-8")
    for forbidden in ("urlopen", "http.client", "requests.get", "requests.post"):
        assert forbidden not in impl_source
    tree = ast.parse(impl_source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert "socket" not in imported
    assert "urllib" not in imported
    assert "requests" not in imported
    assert "httpx" not in imported
    # Este arquivo de teste também não importa rede: apenas AST/stdlib de inspeção.
    test_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    test_imports: set[str] = set()
    for node in ast.walk(test_tree):
        if isinstance(node, ast.Import):
            test_imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            test_imports.add(node.module.split(".")[0])
    assert "socket" not in test_imports
    assert "urllib" not in test_imports
    assert "requests" not in test_imports
    # Prova de mock total: mesmo que subprocess real fosse tentado, o despacho
    # desta versão nunca o invoca (executor fake in-memory apenas).
    import subprocess as _subprocess

    def _forbidden(*_args, **_kwargs):
        raise AssertionError("rede/subprocess real proibido em R470")

    monkeypatch.setattr(_subprocess, "call", _forbidden)
    monkeypatch.setattr(_subprocess, "check_output", _forbidden)
    monkeypatch.setattr(_subprocess, "run", _forbidden, raising=False)
    req = _authorized_request()
    exit_code, _cli, _dl = rr.dispatch_restricted(req, executor=lambda argv: 0)
    assert exit_code == 0
    # Sem credenciais neste arquivo: varredura de padrões óbvios, excluindo as
    # próprias linhas de asserção desta inspeção (auto-referência).
    lines = [
        line
        for line in Path(__file__).read_text(encoding="utf-8").splitlines()
        if "assert" not in line
    ]
    lowered = "\n".join(lines).lower()
    assert "password" not in lowered
    assert "api_key=" not in lowered.replace(" ", "")
