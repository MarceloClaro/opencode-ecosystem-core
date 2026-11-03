# -*- coding: utf-8 -*-
"""SPEC-935-R1012 — federação universal de plugins, MCPs e agentes.

Testes offline: nenhuma rede, nenhum clone, nenhuma execução de artefato.
As fontes são fixtures temporárias que reproduzem a forma real dos arquivos.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from integrations.federation_sync import apply as apply_module
from integrations.federation_sync.cli import run as cli_run
from integrations.federation_sync.model import FederatedItem, digest_items
from integrations.federation_sync.route import route
from integrations.federation_sync.sources import collect
from integrations.federation_sync.store import load_items, load_registry, sync, verify


# ── fixtures ────────────────────────────────────────────────────────────────
@pytest.fixture()
def sandbox(tmp_path: Path) -> dict:
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    (repo / "federation").mkdir(parents=True)
    (home / ".claude" / "plugins").mkdir(parents=True)

    (repo / "opencode.json").write_text(json.dumps({
        "default_agent": "marceloclaro",
        "agent": {"marceloclaro": {"description": "primário"}},
        "mcp": {"existente": {"type": "local", "command": ["x"], "enabled": True}},
    }, indent=2), encoding="utf-8")

    (repo / "federation" / "github_sources.json").write_text(json.dumps({
        "repositories": [
            {
                "repo": "exemplo/mcp-mit",
                "license": "MIT",
                "description": "Servidor de exemplo.",
                "kind": "mcp",
                "installable": True,
                "servers": [{"name": "exemplo-mcp", "command": "npx",
                             "args": ["-y", "exemplo-mcp"], "installable": True}],
            },
            {
                "repo": "exemplo/sem-licenca",
                "license": "",
                "description": "Licença não verificada.",
                "kind": "mcp",
                "servers": [{"name": "sem-licenca-mcp", "command": "uvx",
                             "args": ["sem-licenca"], "installable": True}],
            },
        ]
    }), encoding="utf-8")
    (repo / "federation" / "chatgpt_sources.json").write_text(json.dumps({
        "connectors": [{"name": "chatgpt-github", "vendor": "OpenAI",
                        "description": "Conector hospedado.", "url": "https://chatgpt.com/apps"}]
    }), encoding="utf-8")

    plugins = home / ".claude" / "plugins"
    marketplace = plugins / "marketplaces" / "mkt"
    (marketplace / "plugins" / "alpha").mkdir(parents=True)
    (marketplace / "LICENSE").write_text("Apache License\nVersion 2.0, January 2004\n",
                                         encoding="utf-8")
    (marketplace / "plugins" / "alpha" / "mcp.json").write_text(json.dumps({
        "mcpServers": {
            "alpha-mcp": {"command": "npx", "args": ["-y", "alpha"]},
            "secure-mcp": {"command": "npx", "args": ["-y", "secure"],
                           "env": {"API_TOKEN": "sk-nao-deve-vazar"}},
        }
    }), encoding="utf-8")
    skill_body = marketplace / "plugins" / "alpha" / "skills" / "pdf-extraction"
    skill_body.mkdir(parents=True)
    (skill_body / "SKILL.md").write_text("---\nname: pdf-extraction\n---\n\n# Corpo\n",
                                         encoding="utf-8")
    catalog = {
        "catalog": {
            "plugins": {
                "alpha@mkt": {
                    "plugin": "alpha", "version": "1.0.0",
                    "components": {
                        "skills": [{"name": "pdf-extraction"}],
                        "agents": [{"name": "alpha-agent"}],
                        "commands": [{"name": "alpha-cmd"}],
                        "hooks": [{"name": "alpha-hook"}],
                        "mcpServers": ["alpha-mcp", "secure-mcp"],
                        "lspServers": [],
                    },
                    "marketplace_entry": {"name": "alpha", "description": "Plugin alfa",
                                          "category": "desenvolvimento"},
                },
                "beta@mkt": {
                    "plugin": "beta", "version": "0.1.0",
                    "components": {"skills": [], "agents": [], "commands": [],
                                   "hooks": [], "mcpServers": [], "lspServers": []},
                    "marketplace_entry": {"name": "beta", "description": "Plugin beta"},
                },
            }
        }
    }
    (plugins / "plugin-catalog-cache.json").write_text(json.dumps(catalog), encoding="utf-8")
    (plugins / "installed_plugins.json").write_text(json.dumps({
        "version": 2,
        "plugins": {"alpha@mkt": [{"installPath": str(marketplace / "plugins" / "alpha")}]},
    }), encoding="utf-8")

    skill_dir = home / ".gemini" / "antigravity-cli" / "builtin" / "skills" / "pdf"
    skill_dir.mkdir(parents=True)
    (skill_dir / "LICENSE").write_text("MIT License\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "---\nname: pdf-extraction\ndescription: Extrai texto de PDF.\n---\n\n# PDF\n",
        encoding="utf-8",
    )
    (home / ".gemini" / "antigravity-cli" / "settings.json").write_text(json.dumps({
        "mcpServers": {
            "nativo": {"command": "python3", "args": [str(repo / "mci" / "mcp_server.py")]},
            "externo": {"command": "uvx", "args": ["externo-mcp"]},
        }
    }), encoding="utf-8")
    return {"repo": repo, "home": home}


def _by_id(items):
    return {item.item_id: item for item in items}


# ── R1012-1/2: coleta e registro ────────────────────────────────────────────
def test_sync_produces_registry_and_digest(sandbox):
    result = sync(sandbox["repo"], home=sandbox["home"], write=True)
    assert result["status"] == "ok"
    assert len(result["digest"]) == 64
    registry = load_registry(sandbox["repo"])
    assert registry["schema"] == "federation-registry/v1"
    assert registry["total"] == result["total"] > 0
    for name in ("registry.json", "mcp_candidates.json", "report.md", "audit.jsonl"):
        assert (sandbox["repo"] / "federation" / name).is_file()


def test_counts_come_from_disk(sandbox):
    items = collect(sandbox["repo"], home=sandbox["home"])
    ecosystems = {item.ecosystem for item in items}
    assert ecosystems == {"claude", "antigravity", "chatgpt", "github"}
    assert len(items) == len({item.item_id for item in items})


def test_sync_is_idempotent(sandbox):
    first = sync(sandbox["repo"], home=sandbox["home"], write=False)
    second = sync(sandbox["repo"], home=sandbox["home"], write=False)
    assert first["digest"] == second["digest"]


# ── R1012-3: licença ────────────────────────────────────────────────────────
def test_marketplace_license_is_inherited(sandbox):
    items = _by_id(collect(sandbox["repo"], home=sandbox["home"]))
    alpha = items["claude:plugin:alpha"]
    assert alpha.license == "Apache-2.0"
    assert alpha.license_scope == "marketplace"
    assert alpha.status == "admitted"


def test_missing_license_degrades(sandbox):
    items = _by_id(collect(sandbox["repo"], home=sandbox["home"]))
    beta = items["claude:plugin:beta"]
    assert beta.status == "degraded"
    assert "license_undeclared" in beta.reasons
    assert not beta.installable


def test_unverified_github_license_degrades(sandbox):
    items = _by_id(collect(sandbox["repo"], home=sandbox["home"]))
    item = items["github:mcp:sem-licenca-mcp@exemplo-sem-licenca"]
    assert item.status == "degraded"
    assert "license_undeclared" in item.reasons


def test_component_without_body_is_not_installable(sandbox):
    items = _by_id(collect(sandbox["repo"], home=sandbox["home"]))
    agent = items["claude:agent:alpha-agent@alpha"]
    assert agent.install_mode == "metadata"
    assert not agent.installable
    skill = items["claude:skill:pdf-extraction@alpha"]
    assert skill.install_mode == "materialize"
    assert skill.installable
    assert skill.source_path.endswith("SKILL.md")


# ── R1012-4: execução de terceiro bloqueada ─────────────────────────────────
def test_hooks_are_blocked_not_materialized(sandbox):
    items = _by_id(collect(sandbox["repo"], home=sandbox["home"]))
    hook = items["claude:hook:alpha-hook@alpha"]
    assert hook.status == "blocked"
    assert hook.reasons == ("third_party_execution",)
    assert not hook.admitted


# ── R1012-7: segredos ───────────────────────────────────────────────────────
def test_mcp_secrets_are_scrubbed(sandbox):
    items = _by_id(collect(sandbox["repo"], home=sandbox["home"]))
    secure = items["claude:mcp:secure-mcp@alpha"]
    assert secure.status == "quarantined"
    assert "auth_required" in secure.reasons
    dumped = json.dumps(secure.to_dict(), ensure_ascii=False)
    assert "sk-nao-deve-vazar" not in dumped
    assert secure.metadata["server"]["env_keys"] == ["API_TOKEN"]


# ── R1012-5: candidatos nascem desativados ──────────────────────────────────
def test_candidates_are_disabled(sandbox):
    sync(sandbox["repo"], home=sandbox["home"], write=True)
    document = json.loads((sandbox["repo"] / "federation" / "mcp_candidates.json").read_text())
    assert document["servers"]["alpha-mcp"]["enabled"] is False
    assert "secure-mcp" not in document["servers"]
    assert document["provenance"]["alpha-mcp"]["ecosystem"] == "claude"


# ── R1012-5/6: apply ────────────────────────────────────────────────────────
def test_apply_dry_run_does_not_write(sandbox):
    sync(sandbox["repo"], home=sandbox["home"], write=True)
    before = (sandbox["repo"] / "opencode.json").read_text()
    result = apply_module.apply_mcp(sandbox["repo"], dry_run=True)
    assert result["status"] == "dry_run"
    assert result["staged"]
    assert (sandbox["repo"] / "opencode.json").read_text() == before
    assert not (sandbox["repo"] / "federation" / "mcp_patch.json").exists()


def test_apply_stages_patch_without_touching_config(sandbox):
    sync(sandbox["repo"], home=sandbox["home"], write=True)
    before = (sandbox["repo"] / "opencode.json").read_text()
    result = apply_module.apply_mcp(sandbox["repo"], dry_run=False)
    assert result["status"] == "staged"
    assert result["config_untouched"] is True
    assert (sandbox["repo"] / "opencode.json").read_text() == before
    patch = json.loads((sandbox["repo"] / "federation" / "mcp_patch.json").read_text())
    assert patch["schema"] == "federation-mcp-patch/v1"
    assert patch["servers"]["alpha-mcp"]["enabled"] is False
    assert patch["preflight"]["alpha-mcp"]["package_verified"] is False


def test_apply_skips_key_already_in_config(sandbox):
    sync(sandbox["repo"], home=sandbox["home"], write=True)
    config_path = sandbox["repo"] / "opencode.json"
    config = json.loads(config_path.read_text())
    config["mcp"]["alpha-mcp"] = {"type": "local", "command": ["npx", "alpha"], "enabled": True}
    config_path.write_text(json.dumps(config), encoding="utf-8")
    result = apply_module.apply_mcp(sandbox["repo"], dry_run=False)
    assert "alpha-mcp" in result["skipped_existing"]
    assert "alpha-mcp" not in result["staged"]


# ── R1012-8: roteamento ─────────────────────────────────────────────────────
def test_route_prefers_matching_artifact(sandbox):
    sync(sandbox["repo"], home=sandbox["home"], write=True)
    result = route(sandbox["repo"], "pdf extraction", ["pdf"])
    assert result["status"] == "ok"
    assert result["ranking"][0]["name"] == "pdf-extraction"
    assert 0.0 <= result["ranking"][0]["score"] <= 1.0


def test_route_excludes_non_admitted_by_default(sandbox):
    sync(sandbox["repo"], home=sandbox["home"], write=True)
    result = route(sandbox["repo"], "beta", ["beta"])
    assert all("beta" not in entry["item_id"] for entry in result["ranking"])


# ── R1012-9: integridade ────────────────────────────────────────────────────
def test_verify_detects_tampering(sandbox):
    sync(sandbox["repo"], home=sandbox["home"], write=True)
    assert verify(sandbox["repo"])["ok"] is True
    path = sandbox["repo"] / "federation" / "registry.json"
    registry = json.loads(path.read_text())
    registry["items"][0]["name"] = "adulterado"
    path.write_text(json.dumps(registry), encoding="utf-8")
    assert verify(sandbox["repo"])["ok"] is False


def test_digest_is_order_independent():
    a = FederatedItem(ecosystem="github", kind="mcp", name="a", license="MIT")
    b = FederatedItem(ecosystem="github", kind="mcp", name="b", license="MIT")
    assert digest_items([a, b]) == digest_items([b, a])


# ── R1012-10: CLI ───────────────────────────────────────────────────────────
def test_cli_sync_and_status(sandbox, capsys):
    code = cli_run(["sync", "--repo", str(sandbox["repo"]), "--home", str(sandbox["home"])])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["total"] > 0
    assert cli_run(["status", "--repo", str(sandbox["repo"])]) == 0


def test_cli_apply_stages_patch(sandbox, capsys):
    sync(sandbox["repo"], home=sandbox["home"], write=True)
    before = (sandbox["repo"] / "opencode.json").read_text()
    code = cli_run(["apply", "--repo", str(sandbox["repo"]), "--stage"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "staged"
    assert (sandbox["repo"] / "opencode.json").read_text() == before
    assert (sandbox["repo"] / "federation" / "mcp_patch.json").is_file()


def test_cli_module_entrypoint_reads_sys_argv(sandbox, monkeypatch, capsys):
    import sys

    monkeypatch.setattr(sys, "argv", ["federacao", "status", "--repo", str(sandbox["repo"])])
    assert cli_run() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] in {"ok", "missing"}
