"""Contraprovas do transporte, separadas da prova externa com modelo real."""
from __future__ import annotations

import importlib
import json

import pytest


def api():
    return importlib.import_module("integrations.live_scientific_runtime")


def config(tmp_path, **changes):
    value = {"runtime": "hermes", "prompt": "Explique a diferença entre simulação e observação.",
             "model": "llama3.2:latest", "output_dir": str(tmp_path / "result")}
    value.update(changes)
    return value


@pytest.mark.parametrize("change", [
    {"runtime": "bash"}, {"command": ["rm", "-rf", "/"]}, {"env": {"API_KEY": "x"}},
    {"base_url": "https://example.org/v1"}, {"base_url": "http://user:password@localhost:11434/v1"},
    {"base_url": "http://127.0.0.1:11434/v1?token=x"}, {"prompt": ""},
    {"timeout_seconds": 601}, {"timeout_seconds": True}, {"model": "--execute"},
    {"prompt": "x" * 12001},
])
def test_invalid_configuration_precedes_effects(tmp_path, change):
    with pytest.raises(ValueError):
        api().validate_runtime_config(config(tmp_path, **change))
    assert not (tmp_path / "result").exists()


def test_configuration_is_copied_and_local(tmp_path):
    value = config(tmp_path)
    result = api().validate_runtime_config(value)
    result["prompt"] = "changed"
    assert value["prompt"] != "changed"
    assert result["base_url"] == "http://127.0.0.1:11434/v1"


@pytest.mark.parametrize("returncode, receipts, artifact, expected", [
    (0, [], True, False), (1, [{"generated_tokens": 5, "generated": True, "http_status": 200}], True, False),
    (0, [{"generated_tokens": 0, "generated": False, "http_status": 200}], True, False),
    (0, [{"generated_tokens": 5, "generated": True, "http_status": 200}], False, False),
    (0, [{"generated_tokens": 5, "generated": True, "http_status": 200}], True, True),
])
def test_process_exit_and_health_are_insufficient(returncode, receipts, artifact, expected):
    result = api().classify_execution(returncode, receipts, artifact)
    assert (result["status"] == "completed") is expected
    assert result["externally_validated"] is False
    assert result["human_peer_review"] is False


def test_missing_runtime_is_blocked_with_no_claim_of_inference(tmp_path):
    result = api().LiveScientificRuntime().run(config(tmp_path, runtime_dir=str(tmp_path / "missing")))
    assert result["status"] == "blocked"
    assert result["inference_executed"] is False
    assert result["external_process_executed"] is False


def test_existing_output_is_never_overwritten(tmp_path):
    output = tmp_path / "result"
    output.mkdir()
    sentinel = output / "author.txt"
    sentinel.write_text("preserve")
    result = api().LiveScientificRuntime().run(config(tmp_path))
    assert result["status"] == "blocked"
    assert sentinel.read_text() == "preserve"


def test_response_receipt_rejects_health_only_and_empty_generation():
    assert api().response_receipt({"status": "ok"}, b"{}", b"{}", 200)["generated"] is False
    assert api().response_receipt({"choices": [{"message": {"content": ""}}], "usage": {"completion_tokens": 0}}, b"{}", b"{}", 200)["generated"] is False


def test_response_receipt_has_hashes_but_no_credentials():
    body = json.dumps({"choices": [{"message": {"content": "Resposta"}}], "usage": {"completion_tokens": 3}}).encode()
    receipt = api().response_receipt(json.loads(body), b"{\"model\":\"local\"}", body, 200)
    assert receipt["generated"] is True
    assert len(receipt["response_sha256"]) == 64
    assert "authorization" not in json.dumps(receipt).lower()


def test_foreign_checkout_not_executed(tmp_path):
    repo = tmp_path / "foreign"
    repo.mkdir()
    (repo / "hermes_cli").mkdir()
    (repo / "hermes_cli/main.py").write_text("raise RuntimeError('must never execute')")
    result = api().LiveScientificRuntime().run(config(tmp_path, runtime_dir=str(repo)))
    assert result["status"] == "blocked"
    assert result["external_process_executed"] is False


def test_manifest_hash_detects_artifact_changes(tmp_path):
    output = tmp_path / "result"
    output.mkdir()
    item = output / "result.txt"
    item.write_text("original")
    artifacts = api().artifact_manifest(output)
    original = artifacts["result.txt"]["sha256"]
    item.write_text("altered")
    assert api().artifact_manifest(output)["result.txt"]["sha256"] != original
def test_large_hermes_dependency_is_hashed_without_becoming_analysis(tmp_path):
    from integrations.live_scientific_runtime import artifact_manifest
    binary = tmp_path / "hermes_home/bin/tirith"
    binary.parent.mkdir(parents=True)
    with binary.open("wb") as stream:
        stream.truncate(17 * 1024 * 1024)
    report = artifact_manifest(tmp_path)
    assert report["hermes_home/bin/tirith"]["role"] == "runtime_dependency"
    assert report["hermes_home/bin/tirith"]["sha256"]
def test_hermes_configuration_uses_nonstreaming_and_no_auto_scanner(tmp_path):
    import json
    from integrations.live_scientific_runtime import LiveScientificRuntime
    config = {"runtime": "hermes", "model": "model-local", "timeout_seconds": 60}
    LiveScientificRuntime()._command(config, {"python": "python"}, tmp_path, "http://127.0.0.1:9999/v1")
    settings = json.loads((tmp_path / "hermes_home/config.yaml").read_text())
    assert settings["model"]["streaming"] is False
    assert settings["security"]["tirith_enabled"] is False
