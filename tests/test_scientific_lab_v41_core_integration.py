from __future__ import annotations

import json
from pathlib import Path

from scientific_lab import runtime
from marceloclaro import scientific_lab as bridge

ROOT = Path(__file__).resolve().parents[1]


def _fake_skill(tmp_path: Path) -> Path:
    root = tmp_path / "skill"
    (root / "scripts").mkdir(parents=True)
    (root / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    (root / "VERSION.json").write_text(json.dumps({"version": "4.1.0", "edition": "core-test"}), encoding="utf-8")
    (root / "scripts/validate_contracts.py").write_text("print('ok')\n", encoding="utf-8")
    return root


def test_skill_registered():
    assert (ROOT / ".opencode/skills/pesquisador-universal-marcelo-claro/SKILL.md").is_file()


def test_environment_override_has_priority(tmp_path, monkeypatch):
    skill = _fake_skill(tmp_path)
    monkeypatch.setenv("PESQUISADOR_UNIVERSAL_HOME", str(skill))
    assert runtime.discover() == skill.resolve()


def test_invalid_skill_is_not_discovered(tmp_path, monkeypatch):
    invalid = tmp_path / "invalid"
    invalid.mkdir()
    monkeypatch.setenv("PESQUISADOR_UNIVERSAL_HOME", str(invalid))
    monkeypatch.setenv("HOME", str(tmp_path / "empty-home"))
    assert runtime.discover() is None


def test_status_reports_installed(tmp_path):
    skill = _fake_skill(tmp_path)
    status = runtime.installed_status(skill)
    assert status["status"] == "installed"
    assert status["version"] == "4.1.0"


def test_core_compatibility_current_layout():
    report = runtime.core_compatibility(ROOT)
    assert report["compatible"] is True
    assert report["baseline_audited_commit"].startswith("a5478054")


def test_bridge_help_returns_zero(capsys):
    assert bridge.main(["--help"]) == 0
    assert "Pesquisador Universal v4.1" in capsys.readouterr().out


def test_bridge_status_without_install_is_not_overclaim(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("PESQUISADOR_UNIVERSAL_HOME", raising=False)
    monkeypatch.delenv("PU_PREFIX", raising=False)
    monkeypatch.setattr(runtime.Path, "home", classmethod(lambda cls: tmp_path))
    assert bridge.main(["status"]) == 0
    out = capsys.readouterr().out
    assert "not_installed" in out
