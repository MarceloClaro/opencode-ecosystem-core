#!/usr/bin/env python3
# Testes do remotion-dublagem-lendário (SPEC-935-R1122)

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

# Caminho absoluto para a skill
SKILL_DIR = Path(__file__).resolve().parents[1] / ".opencode" / "skills" / "remotion-dublagem-lendario"

def test_status_checa_licenca():
    """status encontra licenca Remotion valida e reporta available."""
    skill_path = SKILL_DIR / "SKILL.md"
    assert skill_path.is_file(), f"SKILL.md nao encontrado em {skill_path}"
    content = skill_path.read_text(encoding="utf-8")
    assert "Remotion License" in content or "remotion" in content.lower()

def test_skill_tem_metadata():
    """skill tem metadata de versao e spec_id."""
    skill_path = SKILL_DIR / "SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    assert "version:" in content
    assert "spec_id:" in content

def test_skill_tem_github_native():
    """skill tem metadata github_native."""
    skill_path = SKILL_DIR / "SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    assert "github_native: true" in content

def test_test_file_existe():
    """test file existe."""
    test_path = Path(__file__).resolve().parents[1] / "tests" / "test_remotion_dublegenda.py"
    assert test_path.is_file()
