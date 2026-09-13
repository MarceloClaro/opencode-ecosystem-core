# -*- coding: utf-8 -*-
"""Testes SPEC-935-R471 — dispatch de skills Reversa user/model-invoked."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from reversa_universal.skill_dispatch import ReversaSkillDispatcher, plan_skill_handoff


def _write_skill(root: Path, name: str, frontmatter: str = "", openai_policy: str | None = None) -> Path:
    skill_dir = root / ".agents" / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill = skill_dir / "SKILL.md"
    skill.write_text(
        f"---\nname: {name}\n{frontmatter}---\n\n# Skill\n\nExecute o trabalho.\n",
        encoding="utf-8",
    )
    if openai_policy is not None:
        policy_dir = skill_dir / "agents"
        policy_dir.mkdir(parents=True, exist_ok=True)
        (policy_dir / "openai.yaml").write_text(openai_policy, encoding="utf-8")
    return skill


def test_disable_model_invocation_forces_read_and_execute(tmp_path: Path) -> None:
    skill = _write_skill(
        tmp_path,
        "reversa-clarify",
        "disable-model-invocation: true\n",
    )
    decision = ReversaSkillDispatcher(tmp_path).plan("reversa-clarify")
    assert decision.found is True
    assert decision.user_invoked is True
    assert decision.execution_mode == "read-and-execute"
    assert decision.skill_path == str(skill.resolve())
    assert "disable-model-invocation=true" in decision.reason
    assert "NÃO invoque" in decision.instruction


def test_openai_policy_false_also_forces_read_and_execute(tmp_path: Path) -> None:
    _write_skill(
        tmp_path,
        "reversa-plan",
        openai_policy=(
            "interface:\n"
            "  display_name: Reversa Plan\n"
            "policy:\n"
            "  allow_implicit_invocation: false\n"
        ),
    )
    decision = ReversaSkillDispatcher(tmp_path).plan("reversa-plan")
    assert decision.user_invoked is True
    assert decision.execution_mode == "read-and-execute"
    assert "allow_implicit_invocation=false" in decision.reason
    assert decision.openai_policy_path is not None


def test_model_invoked_skill_can_use_native_or_read(tmp_path: Path) -> None:
    _write_skill(tmp_path, "reversa-forward")
    decision = ReversaSkillDispatcher(tmp_path).plan("reversa-forward")
    assert decision.found is True
    assert decision.user_invoked is False
    assert decision.execution_mode == "native-or-read"


def test_missing_skill_returns_safe_fallback(tmp_path: Path) -> None:
    decision = ReversaSkillDispatcher(tmp_path).plan("reversa-quality")
    assert decision.found is False
    assert decision.execution_mode == "native-or-read"
    assert decision.skill_path is None


@pytest.mark.parametrize("invalid", ["../reversa-clarify", "reversa/clarify", "", "reversa clarify"])
def test_invalid_skill_names_are_rejected(tmp_path: Path, invalid: str) -> None:
    with pytest.raises(ValueError):
        ReversaSkillDispatcher(tmp_path).plan(invalid)


def test_environment_skill_root_is_supported(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    external = tmp_path / "external-skills"
    skill_dir = external / "reversa-to-do"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: reversa-to-do\ndisable-model-invocation: true\n---\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("REVERSA_SKILLS_ROOT", str(external))
    decision = ReversaSkillDispatcher(tmp_path).plan("reversa-to-do")
    assert decision.found is True
    assert decision.execution_mode == "read-and-execute"


def test_functional_api_returns_plain_dict(tmp_path: Path) -> None:
    _write_skill(tmp_path, "reversa-sync", "disable-model-invocation: true\n")
    result = plan_skill_handoff("reversa-sync", tmp_path)
    assert result["skill_name"] == "reversa-sync"
    assert result["execution_mode"] == "read-and-execute"
    assert isinstance(result["instruction"], str)


def test_no_environment_leak_between_dispatchers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("REVERSA_SKILLS_ROOT", raising=False)
    dispatcher = ReversaSkillDispatcher(tmp_path)
    assert dispatcher.plan("reversa-clarify").found is False
    assert "REVERSA_SKILLS_ROOT" not in os.environ
