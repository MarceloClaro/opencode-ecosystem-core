from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scientific_lab import runtime
from marceloclaro import scientific_lab as bridge


def _fake_skill(tmp_path: Path, scripts: dict[str, str] | None = None) -> Path:
    root = tmp_path / "skill"
    script_root = root / "scripts"
    script_root.mkdir(parents=True)
    (root / "SKILL.md").write_text("# local test fixture\n", encoding="utf-8")
    (root / "VERSION.json").write_text(
        json.dumps({"version": "4.1.1", "edition": "test fixture"}),
        encoding="utf-8",
    )
    for name, body in (scripts or {}).items():
        (script_root / name).write_text(body, encoding="utf-8")
    return root


def _verified_status(home: Path) -> dict:
    return {
        "status": "installed_verified",
        "home": str(home),
        "version": "4.1.1",
        "verified_release": True,
        "verification_scope": "version_and_package_manifest_hash_only",
    }


def test_installed_status_states_its_limited_verification_scope(tmp_path, monkeypatch):
    skill = _fake_skill(tmp_path)
    manifest = b"controlled test manifest"
    (skill / "PACKAGE_MANIFEST.sha256").write_bytes(manifest)
    monkeypatch.setattr(runtime, "EXPECTED_VERSION", "4.1.1")
    monkeypatch.setattr(runtime, "EXPECTED_PACKAGE_MANIFEST_SHA256", hashlib.sha256(manifest).hexdigest())

    status = runtime.installed_status(skill)

    assert status["status"] == "installed_verified"
    assert status["verified_release"] is True
    assert status["verification_scope"] == "version_and_package_manifest_hash_only"
    assert status["file_inventory_validated"] is False


def test_status_does_not_execute_package_validators(tmp_path, monkeypatch, capsys):
    skill = _fake_skill(tmp_path)
    monkeypatch.setattr(bridge, "installed_status", lambda: _verified_status(skill))

    def unexpected_validation(_home):
        raise AssertionError("status must not execute package validators")

    monkeypatch.setattr(bridge, "_run_validation", unexpected_validation)

    assert bridge.main(["status"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["verified_release"] is True


def test_run_validation_reports_each_script_and_suppresses_free_text(tmp_path):
    skill = _fake_skill(
        tmp_path,
        {
            "validate_contracts.py": "print('PRIVATE_VALIDATOR_OUTPUT')\n",
            "validate_ecosystem.py": "raise SystemExit(1)\n",
        },
    )

    result = bridge._run_validation(skill)

    assert result["status"] == "failed"
    assert result["executed"] is True
    assert result["validators"] == [
        {"name": "validate_contracts.py", "exit_code": 0, "status": "passed"},
        {"name": "validate_ecosystem.py", "exit_code": 1, "status": "failed"},
    ]
    assert "PRIVATE_VALIDATOR_OUTPUT" not in json.dumps(result)


def test_run_validation_reports_execution_error_without_free_text(tmp_path, monkeypatch):
    skill = _fake_skill(
        tmp_path,
        {
            "validate_contracts.py": "pass\n",
            "validate_ecosystem.py": "pass\n",
        },
    )

    def denied(*_args, **_kwargs):
        raise PermissionError("sensitive path must not be serialized")

    monkeypatch.setattr(bridge.subprocess, "run", denied)

    result = bridge._run_validation(skill)

    assert result["status"] == "failed"
    assert all(item["exit_code"] == 127 for item in result["validators"])
    assert all(item["error_type"] == "PermissionError" for item in result["validators"])
    assert "sensitive path" not in json.dumps(result)


def test_run_validation_marks_timeout_and_continues(tmp_path, monkeypatch):
    skill = _fake_skill(
        tmp_path,
        {
            "validate_contracts.py": "import time; time.sleep(2)\n",
            "validate_ecosystem.py": "pass\n",
        },
    )
    monkeypatch.setattr(bridge, "VALIDATOR_TIMEOUT_SECONDS", 0.5)

    result = bridge._run_validation(skill)

    assert result["status"] == "failed"
    assert result["validators"][0]["name"] == "validate_contracts.py"
    assert result["validators"][0]["status"] == "timeout"
    assert result["validators"][0]["error_type"] == "TimeoutExpired"
    assert result["validators"][1]["status"] == "passed"


def test_doctor_reports_validation_failure_even_when_manifest_is_verified(tmp_path, monkeypatch, capsys):
    skill = _fake_skill(tmp_path)
    monkeypatch.setattr(bridge, "core_compatibility", lambda _root: {"compatible": True})
    monkeypatch.setattr(bridge, "installed_status", lambda: _verified_status(skill))
    monkeypatch.setattr(bridge, "native_status", lambda: {"mode": "native"})
    monkeypatch.setattr(
        bridge,
        "_run_validation",
        lambda _home: {
            "status": "failed",
            "executed": True,
            "validators": [
                {"name": "validate_contracts.py", "exit_code": 0, "status": "passed"},
                {"name": "validate_ecosystem.py", "exit_code": 1, "status": "failed"},
            ],
        },
    )

    assert bridge.main(["doctor"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["scientific_layer"]["verified_release"] is True
    assert payload["package_validation"]["status"] == "failed"
    assert payload["doctor_status"] == "degraded"


def test_doctor_returns_zero_only_when_all_validators_pass(tmp_path, monkeypatch, capsys):
    skill = _fake_skill(tmp_path)
    monkeypatch.setattr(bridge, "core_compatibility", lambda _root: {"compatible": True})
    monkeypatch.setattr(bridge, "installed_status", lambda: _verified_status(skill))
    monkeypatch.setattr(bridge, "native_status", lambda: {"mode": "native"})
    monkeypatch.setattr(
        bridge,
        "_run_validation",
        lambda _home: {
            "status": "passed",
            "executed": True,
            "validators": [
                {"name": "validate_contracts.py", "exit_code": 0, "status": "passed"},
                {"name": "validate_ecosystem.py", "exit_code": 0, "status": "passed"},
            ],
        },
    )

    assert bridge.main(["doctor"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["package_validation"]["status"] == "passed"
    assert payload["doctor_status"] == "healthy"
