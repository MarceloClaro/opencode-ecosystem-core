from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scientific_lab import runtime
from marceloclaro import scientific_lab as bridge

ROOT = Path(__file__).resolve().parents[1]


def _fake_skill(tmp_path: Path, verified: bool = False) -> Path:
    root = tmp_path / "skill"
    (root / "scripts").mkdir(parents=True)
    (root / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    (root / "VERSION.json").write_text(json.dumps({"version": "4.1.0", "edition": "core-test"}), encoding="utf-8")
    (root / "scripts/validate_contracts.py").write_text("print('ok')\n", encoding="utf-8")
    if verified:
        payload = b"manifest-test"
        (root / "PACKAGE_MANIFEST.sha256").write_bytes(payload)
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


def test_unverified_install_is_fail_closed(tmp_path):
    skill = _fake_skill(tmp_path)
    status = runtime.installed_status(skill)
    assert status["status"] == "installed_unverified"
    assert status["verified_release"] is False


def test_release_constants_match_upstream_record():
    record = json.loads((ROOT / "scientific_lab/UPSTREAM_RELEASE.json").read_text(encoding="utf-8"))
    assert record["version"] == runtime.EXPECTED_VERSION
    assert record["package_manifest_sha256"] == runtime.EXPECTED_PACKAGE_MANIFEST_SHA256
    assert record["skill_archive"]["sha256"] == runtime.EXPECTED_SKILL_ARCHIVE_SHA256


def test_core_compatibility_current_layout():
    report = runtime.core_compatibility(ROOT)
    assert report["compatible"] is True
    assert report["baseline_audited_commit"].startswith("a5478054")


def test_bridge_help_returns_zero(capsys):
    assert bridge.main(["--help"]) == 0
    assert "Pesquisador Universal v4.1" in capsys.readouterr().out


def test_dispatch_refuses_unverified_skill(tmp_path):
    skill = _fake_skill(tmp_path)
    assert runtime.dispatch("research", [], home=skill) == 5
