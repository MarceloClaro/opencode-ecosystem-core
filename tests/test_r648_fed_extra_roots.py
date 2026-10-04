# -*- coding: utf-8 -*-
"""Testes TDD das raízes opt-in de federação (SPEC-935-R648)."""

import os
import sys

sys.path.insert(0, ".")

from integrations.harness_federation.harvest import HarnessHarvester  # noqa: E402


def _skill_dir(tmp_path, name="demo-skill"):
    d = tmp_path / name
    d.mkdir()
    (d / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Habilidade de demonstracao.\n---\n\nCorpo.\n",
        encoding="utf-8",
    )
    return str(d)


def test_sem_env_comportamento_padrao(monkeypatch, tmp_path):
    monkeypatch.delenv("HARNESS_FED_EXTRA_ROOTS", raising=False)
    specs = HarnessHarvester(repo_root=str(tmp_path))._root_specs()
    assert all("demo" not in s["label"] for s in specs)


def test_extra_root_valida_aparece(monkeypatch, tmp_path):
    _skill_dir(tmp_path)
    monkeypatch.setenv(
        "HARNESS_FED_EXTRA_ROOTS",
        f"claude|audit-harness|third_party|{tmp_path}",
    )
    specs = HarnessHarvester(repo_root=str(tmp_path))._root_specs()
    extra = [s for s in specs if s["label"] == "audit-harness"]
    assert len(extra) == 1 and extra[0]["ecosystem"] == "claude"


def test_entradas_ruins_ignoradas(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "HARNESS_FED_EXTRA_ROOTS",
        os.pathsep.join([
            "sem-pipes",
            "a|b|c",
            "invalido|lbl|third_party|" + str(tmp_path),
            "claude|lbl|third_party|/caminho/inexistente/xyz",
            "",
        ]),
    )
    specs = HarnessHarvester(repo_root=str(tmp_path))._root_specs()
    assert all(s["label"] != "lbl" for s in specs)


def test_origem_vazia_vira_third_party(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "HARNESS_FED_EXTRA_ROOTS", f"codex|audit-codex||{tmp_path}"
    )
    specs = HarnessHarvester(repo_root=str(tmp_path))._root_specs()
    extra = [s for s in specs if s["label"] == "audit-codex"]
    assert extra and extra[0]["origin"] == "third_party"


def test_discover_inclui_raiz_extra(monkeypatch, tmp_path):
    _skill_dir(tmp_path)
    monkeypatch.setenv(
        "HARNESS_FED_EXTRA_ROOTS",
        f"claude|audit-disc|third_party|{tmp_path}",
    )
    found = HarnessHarvester(repo_root=str(tmp_path)).discover()
    assert any(
        a.source_root == "audit-disc" and a.name == "demo-skill" for a in found
    )
