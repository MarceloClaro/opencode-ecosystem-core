"""SPEC-984 — a interface científica roteia para o Core nativo sem execução externa."""
from __future__ import annotations

import json


def test_native_command_inventory_excludes_v41_fallbacks():
    from scientific_lab.runtime import NATIVE_COMMANDS

    assert NATIVE_COMMANDS == {
        "research", "articles", "review", "evidence", "native-status",
    }


def test_native_status_is_available_without_external_superlayer(monkeypatch, capsys):
    from marceloclaro import scientific_lab as cli
    from scientific_lab.runtime import native_status

    monkeypatch.setattr(cli, "installed_status", lambda: (_ for _ in ()).throw(AssertionError("external status called")))
    assert cli.main(["native-status"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["mode"] == "native"
    assert set(result["commands"]) == {"research", "articles", "review", "evidence", "native-status"}
    assert set(result["external_fallback_commands"]) == {
        "mesh", "mission", "living", "synthesis", "grade", "causal", "federation", "production",
    }
    assert native_status()["mode"] == "native"


def test_native_cli_routes_without_calling_external_dispatch(monkeypatch):
    from marceloclaro import scientific_lab as cli
    from scientific_lab.native import cli as native_cli

    seen = []
    monkeypatch.setattr(native_cli, "dispatch", lambda command, argv: seen.append((command, argv)) or 0)
    monkeypatch.setattr(cli, "dispatch", lambda *args: (_ for _ in ()).throw(AssertionError("v4.1 fallback called")))

    assert cli.main(["research", "search", "termo", "--workspace", "/tmp/w"]) == 0
    assert seen == [("research", ["search", "termo", "--workspace", "/tmp/w"]) ]


def test_review_and_evidence_are_native_without_network(monkeypatch):
    from marceloclaro import scientific_lab as cli
    from scientific_lab.native import cli as native_cli

    calls = []
    monkeypatch.setattr(native_cli, "dispatch", lambda command, argv: calls.append((command, argv)) or 0)
    monkeypatch.setattr(cli, "dispatch", lambda *args: (_ for _ in ()).throw(AssertionError("external dispatch called")))

    assert cli.main(["review", "init", "--project-id", "P", "--title", "T", "--question", "Q"]) == 0
    assert cli.main(["evidence", "build", "--project-id", "P"]) == 0
    assert calls == [
        ("review", ["init", "--project-id", "P", "--title", "T", "--question", "Q"]),
        ("evidence", ["build", "--project-id", "P"]),
    ]


def test_unmigrated_advanced_command_remains_explicit_external_fallback(monkeypatch):
    from marceloclaro import scientific_lab as cli
    from scientific_lab.native import cli as native_cli

    calls = []
    monkeypatch.setattr(native_cli, "dispatch", lambda *args: (_ for _ in ()).throw(AssertionError("native dispatch called")))
    monkeypatch.setattr(cli, "dispatch", lambda command, argv: calls.append((command, argv)) or 7)

    assert cli.main(["grade", "--workspace", "/tmp/w"]) == 7
    assert calls == [("grade", ["--workspace", "/tmp/w"])]


def test_doctor_separates_native_and_external_readiness(monkeypatch, capsys):
    from marceloclaro import scientific_lab as cli

    monkeypatch.setattr(cli, "core_compatibility", lambda root: {"compatible": True, "checks": []})
    monkeypatch.setattr(cli, "installed_status", lambda: {
        "status": "installed_verified", "home": "/opt/pu", "verified_release": True,
    })
    monkeypatch.setattr(cli, "native_status", lambda: {"mode": "native"})
    monkeypatch.setattr(cli, "_run_validation", lambda home: {
        "status": "failed",
        "executed": True,
        "validators": [
            {"name": "validate_contracts.py", "exit_code": 0, "status": "passed"},
            {"name": "validate_ecosystem.py", "exit_code": 1, "status": "failed"},
        ],
    })

    assert cli.main(["doctor"]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["native_layer"]["mode"] == "native"
    assert result["scientific_layer"]["verified_release"] is True
    assert result["package_validation"]["status"] == "failed"
    assert result["doctor_status"] == "degraded"
