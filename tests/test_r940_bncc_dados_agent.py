"""R940: clone local e perfil read-only para análise de BNCC Dados."""

import configparser
import json
from pathlib import Path

import pytest

from agents.lifecycle import AgentLifecycleService, _metadata


ROOT = Path(__file__).resolve().parents[1]
AGENT_ID = "bncc-dados-specialist"
EXPECTED_REMOTE = "https://github.com/bncc-dev/bncc-dados"


def test_clone_is_local_and_tracks_expected_upstream():
    clone = ROOT / "AO"
    git_config = clone / ".git" / "config"
    if not clone.exists():
        pytest.skip("AO/ é clone local não versionado; checkout deve ser verificado no ambiente de entrega")
    assert (clone / ".git" / "HEAD").is_file(), "AO/ precisa ser checkout Git"
    assert git_config.is_file(), "config Git local não encontrado"

    config = configparser.ConfigParser()
    config.read(git_config, encoding="utf-8")
    remote = config['remote "origin"']["url"].removesuffix(".git")
    assert remote.rstrip("/") == EXPECTED_REMOTE


def test_profile_is_registered_and_read_only():
    report = AgentLifecycleService(ROOT).validate(AGENT_ID)
    assert report["definition_validated"] is True
    assert report["mode"] == "managed-v1"
    assert report["executed"] is False
    assert report["source_file"] == f"agents/catalog/{AGENT_ID}.md"

    meta = report["profile"]
    assert meta["parent"] == "marceloclaro"
    assert meta["spec_file"] == "specs/SPEC-935-R940-bncc-dados-specialist.md"
    assert meta["test_file"] == "tests/test_r940_bncc_dados_agent.py"
    assert meta["allow_edit"] is False
    assert {"bncc_repository_analysis", "bncc_data_provenance"}.issubset(meta["tags"])
    assert meta["permission"]["edit"] == "deny"
    assert meta["permission"]["webfetch"] == "deny"
    assert meta["permission"]["task"] == "deny"
    assert meta["permission"]["bash"]["*"] == "deny"
    assert meta["tools"]["edit"] is False
    assert meta["tools"]["write"] is False
    assert meta["output_contract"]["required_fields"] == [
        "status", "findings", "evidence", "limitations"
    ]


def test_opencode_has_the_new_specialist_without_replacing_other_config():
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    agent = config["agent"][AGENT_ID]
    assert agent["mode"] == "subagent"
    assert agent["prompt"] == "{file:./agents/catalog/bncc-dados-specialist.md}"
    assert agent["permission"]["edit"] == "deny"
    assert agent["permission"]["bash"]["*"] == "deny"
    # Configurações do worktree do operador devem sobreviver ao registro do agente.
    assert "biblioteca" in config["command"]


def test_prompt_requires_provenance_and_treats_upstream_as_untrusted():
    path = ROOT / "agents/catalog" / f"{AGENT_ID}.md"
    meta, prompt = _metadata(path.read_bytes())
    text = f"{meta['description']}\n{prompt}".casefold()

    for required in (
        "bncc-dev/bncc-dados",
        "ao/",
        "sha-256",
        "não execute",
        "fonte primária",
        "limitações",
    ):
        assert required in text, f"instrução obrigatória ausente: {required}"
