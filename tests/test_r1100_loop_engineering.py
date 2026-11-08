"""R1100: Loop Engineering no Core — auditoria, skill, agente e gates."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _complete() -> dict:
    return {
        "name": "demo",
        "purpose": "Manter o repositório saudável.",
        "non_goals": ["não alterar produção", "não fazer merge"],
        "trigger": "cron diário às 8h",
        "action": "triagem read-only",
        "architecture": "maker_checker",
        "stop_condition": "sem itens acionáveis ou máximo de 3 iterações",
        "hard_max_iterations": 3,
        "verification": {
            "kind": "test",
            "command": "pytest -q",
            "independent": True,
        },
        "maker": "agent-a",
        "checker": "agent-b",
        "checker_read_only": True,
        "state": {"path": "STATE.md", "schema": "itens[]", "prune": True},
        "budget": {
            "max_tokens_per_run": 100000,
            "max_runs_per_day": 4,
            "kill_switch": "loop-pause",
        },
        "observability": {"run_log": "loop-run-log.md", "metrics": ["runs", "failures"]},
        "safety": {
            "denylist": ["secrets", "infra"],
            "auto_merge": False,
            "allowlist": [],
            "human_gate": "aprovação",
        },
        "requested_level": "L3",
        "observed_days": 14,
    }


def test_complete_loop_is_l3():
    from loops.loop_engineering import audit_loop

    result = audit_loop(_complete())
    assert result["score"] == 10.0
    assert result["computed_level"] == "L3"
    assert result["allowed_level"] == "L3"
    assert result["critical_failures"] == []
    assert result["red_flags"] == []
    assert result["human_review_required"] is True
    assert result["scientifically_validated"] is False


def test_self_verification_and_auto_merge_block():
    from loops.loop_engineering import audit_loop

    bad = _complete()
    bad.update({
        "maker": "same",
        "checker": "same",
        "checker_read_only": False,
        "stop_condition": "",
        "hard_max_iterations": None,
        "state": {},
        "safety": {"auto_merge": True, "allowlist": []},
        "requested_level": "L3",
    })
    result = audit_loop(bad)
    assert result["score"] < 7.0
    assert result["computed_level"] == "L1"
    assert result["allowed_level"] == "L1"
    assert set(result["critical_failures"]) == {"stop", "maker_checker", "state", "safety"}
    texto = " ".join(result["red_flags"]).lower()
    assert "mesmo agente" in texto
    assert "auto-merge" in texto
    assert "hard stop" in texto
    assert "estado durável" in texto


def test_l3_requires_l1_week():
    from loops.loop_engineering import audit_loop

    result = audit_loop({**_complete(), "observed_days": 0, "requested_level": "L3"})
    assert result["computed_level"] == "L3"
    assert result["allowed_level"] == "L1"
    assert any("1 dia" in flag for flag in result["red_flags"])

    result = audit_loop({**_complete(), "observed_days": 3, "requested_level": "L3"})
    assert result["allowed_level"] == "L2"
    assert any("7 dias" in flag for flag in result["red_flags"])


def test_parser_and_existing_spec_are_not_promoted_to_l3():
    from loops.loop_engineering import audit_loop_file, parse_loop_markdown

    path = ROOT / "specs" / "loops" / "harness-reasoning-97.md"
    parsed = parse_loop_markdown(path.read_text(encoding="utf-8"))
    assert parsed["name"] == "harness-reasoning-97"
    assert "manual" in parsed["trigger"].lower()
    assert parsed["hard_max_iterations"] == 3
    assert parsed["verification"]["check"].startswith("confidence_calibrator")
    assert "maker_checker" in parsed["architecture"].lower()

    result = audit_loop_file(path)
    assert result["source"].endswith("harness-reasoning-97.md")
    assert len(result["sha256"]) == 64
    assert result["score"] < 9.5
    assert result["computed_level"] in ("L1", "L2")
    assert result["allowed_level"] == "L1"  # observed_days = 0 no parse
    assert result["human_review_required"] is True
    assert result["scientifically_validated"] is False
    assert "observability" in result["missing"]
    assert "state" in result["missing"]


def test_cli_outputs_json():
    result = subprocess.run(
        [sys.executable, "-m", "loops.loop_engineering",
         str(ROOT / "specs" / "loops" / "harness-reasoning-97.md")],
        cwd=ROOT, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stderr[-800:]
    data = json.loads(result.stdout)
    assert data["score"] > 0
    assert "allowed_level" in data


def test_module_has_no_network_or_shell():
    source = (ROOT / "loops" / "loop_engineering.py").read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "socket" not in source
    assert "requests" not in source
    assert re.search(r"\bexec\s*\(", source) is None
    assert re.search(r"\beval\s*\(", source) is None


def test_agent_skill_and_harness_validate():
    from agents.lifecycle import AgentLifecycleService

    service = AgentLifecycleService(ROOT)
    assert service.validate("loop-engineering-architect").get("definition_validated") is True
    skill = ROOT / ".opencode" / "skills" / "loop-engineering" / "SKILL.md"
    harness = ROOT / "harnesses" / "loop-engineering" / "HARNESS.md"
    assert skill.is_file()
    assert harness.is_file()
    texto = skill.read_text(encoding="utf-8")
    for termo in ("trigger", "stop", "maker", "checker", "L3", "auto-merge", "observabilidade"):
        assert termo.lower() in texto.lower()
    assert "HARNESS.md" in texto or "harness" in texto.lower()


def test_opencode_registers_loop_agent():
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    assert "loop-engineering-architect" in config.get("agent", {})
