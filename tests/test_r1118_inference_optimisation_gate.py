"""Testes RED/GREEN da SPEC-935-R1118.

A SPEC prevê um gate metodológico, não um benchmark: nenhum teste deve
executar inferência,rede, subprocess ou credenciais.
"""

from __future__ import annotations

import copy
import inspect
from pathlib import Path
from typing import Any

import pytest

from skills.tooling import inference_optimisation_gate as gate


def _valid_config() -> dict[str, Any]:
    return {
        "external_code_copied": False,
        "provenance": {
            "repo": "MarceloClaro/inference-optimisation-skill",
            "commit": "fda968e7fc1996aa23c67139c755fe541c9d4be0",
            "retrieved_at": "2026-11-17",
            "fork": True,
        },
        "methodology": {
            "baseline": "configuração atual do Core",
            "metric": "custo por tarefa auditável",
            "budget": "2 iterações locais",
            "holdout": "conjunto separado de 5 tarefas",
        },
        "validation": {
            "full_context_replay": True,
            "independent_review": False,
            "deterministic_seed": "r1118",
        },
        "limitations": [
            "Gate metodológico local; não comprova desempenho de inferência.",
        ],
    }


def test_provenance_constants_are_audit_ready() -> None:
    assert gate.SPEC_ID == "SPEC-935-R1118"
    assert set(gate.PROVENANCE["repositories"]) == {
        "MarceloClaro/skills",
        "MarceloClaro/paper-orchestra",
        "MarceloClaro/inference-optimisation-skill",
    }
    assert gate.PROVENANCE["external_code_copied"] is False
    for repo in gate.PROVENANCE["repositories"].values():
        assert repo["id"] > 0
        assert len(repo["tree_sha"]) == 40
        assert repo["fork"] is True


def test_evaluate_accepts_minimal_compliant_contract() -> None:
    result = gate.evaluate_adaptation_contract(_valid_config())
    assert result["status"] == "PASS"
    assert result["spec_id"] == "SPEC-935-R1118"
    assert result["summary"]["blocked"] == 0
    assert all(item["status"] == "PASS" for item in result["checks"])


def test_evaluate_blocks_copied_external_code() -> None:
    config = _valid_config()
    config["external_code_copied"] = True
    result = gate.evaluate_adaptation_contract(config)
    assert result["status"] == "BLOCKED"
    assert any(
        item["criterion"] == "external_code_copied"
        and item["status"] == "BLOCKED"
        for item in result["checks"]
    )


@pytest.mark.parametrize("missing", ["repo", "commit", "retrieved_at"])
def test_evaluate_blocks_incomplete_provenance(missing: str) -> None:
    config = _valid_config()
    del config["provenance"][missing]
    result = gate.evaluate_adaptation_contract(config)
    assert result["status"] == "BLOCKED"
    assert any(
        item["criterion"] == f"provenance.{missing}"
        and item["status"] == "BLOCKED"
        for item in result["checks"]
    )


@pytest.mark.parametrize("missing", ["baseline", "metric", "budget", "holdout"])
def test_evaluate_blocks_incomplete_methodology(missing: str) -> None:
    config = _valid_config()
    del config["methodology"][missing]
    result = gate.evaluate_adaptation_contract(config)
    assert result["status"] == "BLOCKED"
    assert any(
        item["criterion"] == f"methodology.{missing}"
        and item["status"] == "BLOCKED"
        for item in result["checks"]
    )


def test_evaluate_requires_full_context_replay() -> None:
    config = _valid_config()
    config["validation"]["full_context_replay"] = False
    result = gate.evaluate_adaptation_contract(config)
    assert result["status"] == "BLOCKED"
    assert any(
        item["criterion"] == "validation.full_context_replay"
        and item["status"] == "BLOCKED"
        for item in result["checks"]
    )


def test_evaluate_requires_effective_limitations() -> None:
    config = _valid_config()
    config["limitations"] = ["   "]
    result = gate.evaluate_adaptation_contract(config)
    assert result["status"] == "BLOCKED"
    assert any(
        item["criterion"] == "limitations" and item["status"] == "BLOCKED"
        for item in result["checks"]
    )


def test_evaluate_is_pure_without_mutating_input() -> None:
    config = _valid_config()
    snapshot = copy.deepcopy(config)
    gate.evaluate_adaptation_contract(config)
    assert config == snapshot


def test_report_is_deterministic_and_states_limitations() -> None:
    result = gate.evaluate_adaptation_contract(_valid_config())
    first = gate.render_gate_report(result)
    second = gate.render_gate_report(result)
    assert first == second
    assert "SPEC-935-R1118" in first
    assert "não comprova desempenho" in first
    assert "PASS" in first


def test_module_source_has_no_network_subprocess_or_credentials() -> None:
    source_path = Path(inspect.getsourcefile(gate) or "")
    source = source_path.read_text(encoding="utf-8")
    banned = [
        "requests",
        "urllib",
        "subprocess",
        "socket",
        "os.environ",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "ANTHROPIC_API_KEY",
    ]
    offenders = [token for token in banned if token in source]
    assert offenders == []
