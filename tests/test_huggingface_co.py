#!/usr/bin/env python3
# Testes do huggingface.co (SPEC-935-R1123)

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

# Caminho absoluto para a skill
SKILL_DIR = Path(__file__).resolve().parents[1] / ".opencode" / "skills" / "huggingface-co"

def test_skill_smk_has_license():
    """skill tem metadata de license."""
    skill_path = SKILL_DIR / "SKILL.md"
    assert skill_path.is_file(), f"SKILL.md nao encontrado em {skill_path}"
    content = skill_path.read_text(encoding="utf-8")
    assert "license:" in content.lower() or "license" in content.lower()

def test_skill_tem_version():
    """skill tem version definida."""
    skill_path = SKILL_DIR / "SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    assert "version:" in content

def test_skill_tem_spec_id():
    """skill tem spec_id definido."""
    skill_path = SKILL_DIR / "SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    assert "spec_id:" in content

def test_test_file_existe():
    """test file existe."""
    test_path = Path(__file__).resolve().parents[1] / "tests" / "test_huggingface_co.py"
    assert test_path.is_file()
