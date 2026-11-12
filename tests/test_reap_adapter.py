# -*- coding: utf-8 -*-
"""Testes do adaptador REAP para OpenCode (SPEC-935-R1113)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from integrations.reap_adapter import (
    AdapterError,
    apply_install,
    discover_packs,
    plan_install,
    rollback,
    validate_manifest,
)


def _make_source(tmp_path: Path) -> Path:
    skills = tmp_path / "source" / "Skills"
    for name, body in {
        "reap-01-alpha": "---\nname: reap-01-alpha\n---\n# Alpha\n",
        "reap-02-beta": "---\nname: reap-02-beta\n---\n# Beta\n",
    }.items():
        directory = skills / name
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text(body, encoding="utf-8")
    return tmp_path / "source"


def _roots(tmp_path: Path) -> list[Path]:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    return [allowed]


def test_discover_packs(tmp_path: Path) -> None:
    packs = discover_packs(_make_source(tmp_path))
    assert [pack.name for pack in packs] == ["reap-01-alpha", "reap-02-beta"]


def test_plan_does_not_write(tmp_path: Path) -> None:
    source = _make_source(tmp_path)
    target = tmp_path / "allowed"
    plan = plan_install(source, target, allowed_roots=_roots(tmp_path))
    assert plan["summary"]["create"] == 2
    assert not (target / "reap-01-alpha").exists()


def test_install_layout_skills(tmp_path: Path) -> None:
    source = _make_source(tmp_path)
    target = tmp_path / "allowed"
    plan = plan_install(source, target, layout="skills", allowed_roots=_roots(tmp_path))
    result = apply_install(plan, dry_run=False)
    assert result["applied"] is True
    assert (target / "reap-01-alpha" / "SKILL.md").is_file()
    manifest = json.loads((target / ".reap-manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["entries"]) == 2
    assert validate_manifest(target / ".reap-manifest.json")["ok"] is True


def test_install_layout_references(tmp_path: Path) -> None:
    source = _make_source(tmp_path)
    target = tmp_path / "allowed" / "reap-prompts"
    plan = plan_install(
        source, target, layout="references", allowed_roots=_roots(tmp_path)
    )
    apply_install(plan, dry_run=False)
    assert (target / "references" / "packs" / "reap-01-alpha.md").is_file()
    assert (target / "references" / "packs" / "reap-02-beta.md").is_file()


def test_install_is_idempotent(tmp_path: Path) -> None:
    source = _make_source(tmp_path)
    target = tmp_path / "allowed"
    roots = _roots(tmp_path)
    apply_install(
        plan_install(source, target, allowed_roots=roots), dry_run=False
    )
    second = plan_install(source, target, allowed_roots=roots)
    assert second["summary"]["identical"] == 2
    assert second["summary"]["create"] == 0


def test_rollback_restores_backup(tmp_path: Path) -> None:
    source = _make_source(tmp_path)
    target = tmp_path / "allowed"
    roots = _roots(tmp_path)
    destination = target / "reap-01-alpha" / "SKILL.md"
    destination.parent.mkdir(parents=True)
    destination.write_text("conteudo antigo\n", encoding="utf-8")

    plan = plan_install(source, target, allowed_roots=roots)
    apply_install(plan, dry_run=False)
    assert destination.read_text(encoding="utf-8") != "conteudo antigo\n"

    report = rollback(target / ".reap-manifest.json", dry_run=False)
    assert report["ok"] is True
    assert destination.read_text(encoding="utf-8") == "conteudo antigo\n"


def test_rollback_preserves_modified_file(tmp_path: Path) -> None:
    source = _make_source(tmp_path)
    target = tmp_path / "allowed"
    roots = _roots(tmp_path)
    plan = plan_install(source, target, allowed_roots=roots)
    apply_install(plan, dry_run=False)
    destination = target / "reap-01-alpha" / "SKILL.md"
    destination.write_text("modificado pelo usuario\n", encoding="utf-8")

    report = rollback(target / ".reap-manifest.json", dry_run=False)
    assert destination.read_text(encoding="utf-8") == "modificado pelo usuario\n"
    assert str(destination) in report["preserved"]


def test_rejects_path_traversal(tmp_path: Path) -> None:
    skills = tmp_path / "source" / "Skills"
    evil = skills / "reap-evil"
    evil.mkdir(parents=True)
    (evil / "SKILL.md").write_text("# evil\n", encoding="utf-8")
    # O nome do diretório é válido; o teste força um pack inválido via plan.
    with pytest.raises(AdapterError):
        plan_install(
            tmp_path / "source",
            tmp_path / "allowed",
            packs=["../escape"],
            allowed_roots=_roots(tmp_path),
        )


def test_rejects_target_outside_allowed_roots(tmp_path: Path) -> None:
    source = _make_source(tmp_path)
    outside = tmp_path / "outside"
    with pytest.raises(AdapterError):
        plan_install(source, outside, allowed_roots=_roots(tmp_path))
