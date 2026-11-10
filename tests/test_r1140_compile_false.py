"""Teste controlado compile=False (R1140), sem rede/hardware."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "harnesses/quantum-error-mitigation/hardware_compile_false_test.py"


def _module():
    spec = importlib.util.spec_from_file_location("compile_false_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_manifest_is_single_job_and_compile_false():
    manifest = _module().build_manifest()
    assert manifest["jobs"] == 1
    assert manifest["shots"] == 4096
    assert manifest["compile"] is False
    assert manifest["backend"] == "Baihua"
    assert manifest["pair"] == [106, 107]
    assert manifest["num_qubits"] == 108
    assert len(manifest["qasm_sha256"]) == 64
    assert manifest["hardware_submission_allowed"] is False


def test_plan_and_gate_fail_closed(tmp_path, monkeypatch):
    module = _module()
    out = tmp_path / "run"
    assert module.main(["plan", "--out", str(out)]) == 0
    assert (out / "preregistration.json").exists()
    assert module.main(["run", "--out", str(out)]) == 2
    assert module.main(["run", "--out", str(out), "--confirm", "--allow-hardware"]) == 2
    monkeypatch.setenv("GJQ_HARDWARE_ENABLED", "1")
    assert module.main(["run", "--out", str(out), "--confirm", "--allow-hardware"]) == 2


def test_run_success_with_mocks(tmp_path, monkeypatch):
    module = _module()
    out = tmp_path / "run"
    assert module.main(["plan", "--out", str(out)]) == 0
    monkeypatch.setenv("GJQ_HARDWARE_ENABLED", "1")
    monkeypatch.setattr(
        module.provider,
        "compilation_audit",
        lambda *args, **kwargs: {"status": "success", "audit": {"identity_preserved": True}},
    )
    monkeypatch.setattr(
        module.provider,
        "submit",
        lambda *args, **kwargs: {"status": "submitted", "task_id": "task-1", "executed": True},
    )
    assert module.main(
        ["run", "--out", str(out), "--confirm", "--allow-hardware", "--use-cached-account"]
    ) == 0
    payload = json.loads((out / "run.json").read_text(encoding="utf-8"))
    assert payload["task_id"] == "task-1"
    assert json.loads((out / "layout_audit.json").read_text(encoding="utf-8"))["audit"][
        "identity_preserved"
    ] is True
