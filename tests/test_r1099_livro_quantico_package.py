"""R1099: fábrica do livro quântico — agentes, skills, hooks, harness e MCP."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ["livro-quantico-orchestrator", "quantum-experiment-auditor",
          "quantum-lean-verifier", "quantum-tools-coach", "repetition-editor"]
SKILLS = ["producao-livro-quantico", "auditoria-experimentos-quanticos",
          "verificacao-lean-quantum", "trilhas-ferramentas-quanticas",
          "edicao-antirrepeticao", "pacote-publicacao-cientifica"]


def test_agent_cards_validate():
    from agents.lifecycle import AgentLifecycleService

    service = AgentLifecycleService(ROOT)
    for agent in AGENTS:
        result = service.validate(agent)
        assert result.get("definition_validated") is True, (agent, result)


def test_skills_have_contract():
    for skill in SKILLS:
        path = ROOT / ".opencode" / "skills" / skill / "SKILL.md"
        assert path.is_file(), skill
        texto = path.read_text(encoding="utf-8")
        assert texto.startswith("---")
        assert f"name: {skill}" in texto
        assert "description:" in texto


def test_secret_guard_grants_clean_tree():
    script = ROOT / ".opencode" / "hooks" / "quantum_secret_guard.sh"
    assert script.is_file()
    assert os.access(script, os.X_OK)
    r = subprocess.run([str(script), "educacao_quantica_bohm/livro_pixel"],
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr[-1000:]


def test_quantum_guards_block_hardware_without_sim(tmp_path):
    from hooks.quantum_guards import check_hardware_without_sim, find_hardcoded_api_key

    fake_key = "x" * 32
    assert find_hardcoded_api_key(f'GJQ_API_KEY = "{fake_key}"')
    result = check_hardware_without_sim("python 08_experimentos_18.py --real --only E09", data_dir=tmp_path)
    assert result["allow"] is False
    assert "JSON simulado" in result["reason"]


def test_harness_and_handoff_exist():
    harness = ROOT / "harnesses" / "livro-quantico" / "HARNESS.md"
    handoff = ROOT / "handoffs" / "livro-quantico" / "HANDOFF.md"
    assert harness.is_file()
    assert handoff.is_file()
    assert "Gate" in harness.read_text(encoding="utf-8")
    assert "Perguntas abertas" in handoff.read_text(encoding="utf-8")


def test_mcp_audit_counts():
    pytest.importorskip("mcp")
    from integrations.livro_quantico_mcp import audit_counts

    ok = audit_counts({"0": 530, "1": 494}, 1024)
    assert ok["ok"] is True
    bad = audit_counts({"0": 530, "1": 494}, 1000)
    assert bad["ok"] is False
    assert bad["blocos"][0]["alertas"]


def test_gjq_agent_and_skill():
    from agents.lifecycle import AgentLifecycleService

    result = AgentLifecycleService(ROOT).validate("gjq-experiment-runner")
    assert result.get("definition_validated") is True
    skill = ROOT / ".opencode" / "skills" / "gjq-experimentos-quanticos" / "SKILL.md"
    assert skill.is_file()
    texto = skill.read_text(encoding="utf-8")
    assert "GJQ_API_KEY" in texto
    assert "gjq_run" in texto


def test_gjq_mcp_status_catalog_and_guard():
    pytest.importorskip("mcp")
    from integrations.gjq_experiments_mcp import create_server

    server = create_server()
    tools = server._tool_manager._tools
    assert set(tools) >= {"gjq_status", "gjq_catalog", "gjq_prepare", "gjq_sim", "gjq_run", "gjq_result", "gjq_audit"}
    status = tools["gjq_status"].fn()
    assert isinstance(status["api_key_present"], bool)
    assert "api_key" not in status  # não devolve o valor
    catalog = tools["gjq_catalog"].fn()
    assert len(catalog["experiments"]) == 18
    with pytest.raises(ValueError):
        tools["gjq_run"].fn("E09", "Guoji08", 1024, 900, False)
    audit = tools["gjq_audit"].fn("E09")
    assert audit["exp_id"] == "E09"
    assert "audit" in audit
    assert "limit" in audit


def test_bohm_feynman_agents_and_panel():
    from agents.lifecycle import AgentLifecycleService
    from academic.bohm_feynman_panel import panel, questions

    service = AgentLifecycleService(ROOT)
    for agent in ("david-bohm-wholeness", "richard-feynman-explainer"):
        assert service.validate(agent).get("definition_validated") is True
    p = panel()
    assert p["total"] == 20
    ids = {r["id"] for r in p["reviewers"]}
    assert {"bohm", "feynman", "logician", "complexity-theorist",
            "bayesian-statistician", "missing-data-auditor",
            "open-science-auditor", "dual-use-security", "science-translator"} <= ids
    q = questions("O livro mede aprendizagem?", rounds=2)
    assert q["total"] == 40
    assert q["answers_generated"] is False
    assert q["human_review_required"] is True


def test_bohm_scanner_is_lexical_not_truth():
    from scanners.bohm_scanner import bohm_scanner

    r = bohm_scanner.scan_text("Totalidade, diálogo, suspensão de suposições e fragmentação.")
    assert r["score"] > 0
    assert r["scientific_quality_assessed"] is False
    assert "limitations" in r


def test_mirofish_13_reviewers_group():
    from academic.adversarial_research.simulation import GROUPS
    from academic.adversarial_research.registry import BY_NUMBER

    grupo = GROUPS["revisores_20"]
    assert len(grupo) == 20
    assert {"A35", "A36"} <= set(grupo)
    assert len(GROUPS["revisores_13"]) == 13
    assert BY_NUMBER["A35"]["agent_id"] == "david-bohm-wholeness"
    assert BY_NUMBER["A36"]["agent_id"] == "richard-feynman-explainer"
