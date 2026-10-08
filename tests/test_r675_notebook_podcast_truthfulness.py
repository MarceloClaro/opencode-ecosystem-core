"""Contraprovas R675: transporte não comprova negócio nem artefato de áudio."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import agent_runners.nlm_executor as module
from agent_runners.nlm_executor import NlmPodcastExecutor, NlmPodcastReceipt


def proc(payload=None, code=0, stderr=b""):
    return SimpleNamespace(returncode=code,
                           stdout=json.dumps(payload or {}).encode(), stderr=stderr)


def test_core_venv_binary_is_resolved_without_path(monkeypatch, tmp_path):
    binary = tmp_path / ".venv/bin/nlm"
    binary.parent.mkdir(parents=True)
    binary.write_text("#!/bin/sh\n")
    binary.chmod(0o755)
    monkeypatch.setattr(module, "_REPO_ROOT", tmp_path, raising=False)
    monkeypatch.setattr(module.shutil, "which", lambda name: None)
    executor = NlmPodcastExecutor(env={})
    assert executor.bin_path == str(binary)


def test_explicit_empty_binary_disables_fallback(monkeypatch):
    monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/nlm")
    assert NlmPodcastExecutor(bin_path="", env={}).available() is False


@pytest.mark.parametrize("payload", [
    {"status": "error", "id": "nb-1", "error": "auth failed"},
    {"status": "failed", "id": "nb-1"},
    {"status": "expired", "id": "nb-1"},
    {"status": "partial", "id": "nb-1"},
    {"data": {"status": "error", "id": "nb-1"}},
    {"error": "business failure", "id": "nb-1"},
    {"success": False, "id": "nb-1"},
    {"ok": False, "id": "nb-1"},
])
def test_business_failure_cannot_be_success_with_exit_zero(payload):
    executor = NlmPodcastExecutor(bin_path="/fake/nlm", runner=lambda *a, **k: proc(payload))
    receipt = executor.create_notebook("Título")
    assert receipt.success is False
    assert receipt.result_id is None


def test_audio_creation_uses_artifact_id_instead_of_notebook_id():
    executor = NlmPodcastExecutor(bin_path="/fake/nlm", runner=lambda *a, **k:
                                 proc({"notebook_id": "nb-1", "artifact_id": "art-1"}))
    receipt = executor.create_audio("nb-1")
    assert receipt.success is True
    assert receipt.result_id == "art-1"


@pytest.mark.parametrize("content", [None, b""])
def test_download_requires_nonempty_real_file(tmp_path, content):
    def runner(cmd, **kwargs):
        if content is not None:
            Path(cmd[-1]).write_bytes(content)
        return proc({"status": "success"})
    executor = NlmPodcastExecutor(bin_path="/fake/nlm", runner=runner)
    receipt = executor.download_audio("nb", "art", str(tmp_path), retries=1)
    assert receipt.success is False


def test_download_records_file_and_hash(tmp_path):
    payload = b"actual downloaded audio bytes"
    def runner(cmd, **kwargs):
        Path(cmd[-1]).write_bytes(payload)
        return proc({"status": "success"})
    executor = NlmPodcastExecutor(bin_path="/fake/nlm", runner=runner)
    receipt = executor.download_audio("nb", "art", str(tmp_path), retries=1)
    assert receipt.success is True
    assert receipt.artifact_path == str(tmp_path / "podcast_nb.m4a")
    assert receipt.artifact_sha256 == hashlib.sha256(payload).hexdigest()
    assert receipt.artifact_bytes == len(payload)


def test_download_rejects_preexisting_file_before_process(tmp_path):
    target = tmp_path / "podcast_nb.m4a"
    target.write_bytes(b"previous unrelated audio")
    calls = []
    executor = NlmPodcastExecutor(bin_path="/fake/nlm", runner=lambda *a, **k: calls.append(a) or proc())
    receipt = executor.download_audio("nb", "art", str(tmp_path), retries=1)
    assert receipt.success is False
    assert calls == []


@pytest.mark.parametrize("stderr", [
    b"HTTP 401 Authentication failed token=SENSITIVE_TEST",
    b"403 Permission denied",
    b"Invalid option --profile",
    b"404 Notebook not found",
    b"Unknown server failure",
])
def test_permanent_or_unclassified_failure_is_not_retried(monkeypatch, tmp_path, stderr):
    calls = []
    monkeypatch.setattr(module.time, "sleep", lambda value: None)
    executor = NlmPodcastExecutor(bin_path="/fake/nlm",
                                 runner=lambda *a, **k: calls.append(a) or proc(code=1, stderr=stderr))
    receipt = executor.download_audio("nb", "art", str(tmp_path), retries=4, wait=0)
    assert receipt.success is False
    assert len(calls) == 1
    assert "SENSITIVE_TEST" not in receipt.reason


def test_artifact_propagation_retry_finishes_only_after_file(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(module.time, "sleep", lambda value: None)
    def runner(cmd, **kwargs):
        calls.append(cmd)
        if len(calls) < 3:
            return proc(code=1, stderr=b"404 artifact not ready")
        Path(cmd[-1]).write_bytes(b"audio")
        return proc({"status": "success"})
    executor = NlmPodcastExecutor(bin_path="/fake/nlm", runner=runner)
    receipt = executor.download_audio("nb", "art", str(tmp_path), retries=4, wait=0)
    assert receipt.success and len(calls) == 3


@pytest.mark.parametrize("kwargs", [
    {"retries": 0}, {"retries": True}, {"retries": 1000},
    {"wait": float("nan")}, {"wait": -1}, {"filename": "../escape.m4a"},
    {"artifact_id": ""}, {"timeout": 0},
])
def test_bad_download_parameters_rejected_before_process(tmp_path, kwargs):
    calls = []
    options = {"notebook_id": "nb", "artifact_id": "art", "output_dir": str(tmp_path), "retries": 1}
    options.update(kwargs)
    executor = NlmPodcastExecutor(bin_path="/fake/nlm", runner=lambda *a, **k: calls.append(a) or proc())
    receipt = executor.download_audio(**options)
    assert receipt.success is False
    assert calls == []


class PipelineExecutor:
    def __init__(self, create_file=True, artifact_path=True):
        self.create_file = create_file
        self.artifact_path = artifact_path
    def available(self):
        return True
    def create_notebook(self, *args, **kwargs):
        return NlmPodcastReceipt(success=True, result_id="nb-current", operation="create_notebook")
    def add_source_text(self, *args, **kwargs):
        return NlmPodcastReceipt(success=True, operation="add_source_text")
    def create_audio(self, *args, **kwargs):
        return NlmPodcastReceipt(success=True, result_id="art-current", operation="create_audio")
    def download_audio(self, notebook_id, artifact_id, output_dir, **kwargs):
        path = Path(output_dir) / "current.m4a"
        if self.create_file:
            path.write_bytes(b"audio from this invocation")
        return NlmPodcastReceipt(success=True, operation="download_audio",
                                 artifact_path=str(path) if self.artifact_path else None)


def orchestrator_and_folder(tmp_path, monkeypatch):
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    folder = tmp_path / "production"
    folder.mkdir()
    (folder / "manuscrito.md").write_text("# Fonte\n\nConteúdo autorizado.")
    orchestrator = object.__new__(MarceloClaroOrchestrator)
    observations = []
    monkeypatch.setattr(orchestrator, "_record_knowledge_outcome",
                        lambda *args: observations.append(args) or {"persisted": True})
    return orchestrator, folder, observations


def test_orchestrator_does_not_claim_success_without_download(tmp_path, monkeypatch):
    orchestrator, folder, observations = orchestrator_and_folder(tmp_path, monkeypatch)
    report = orchestrator.podcast(str(folder), executor=PipelineExecutor(create_file=False))
    assert report["ok"] is False
    assert report["etapa"] == "download_audio"
    assert observations[0][2]["status"] == "failed"


def test_orchestrator_does_not_select_unrelated_old_audio(tmp_path, monkeypatch):
    orchestrator, folder, observations = orchestrator_and_folder(tmp_path, monkeypatch)
    (folder / "audio").mkdir()
    (folder / "audio/old.m4a").write_bytes(b"old audio")
    report = orchestrator.podcast(str(folder), executor=PipelineExecutor(create_file=False, artifact_path=False))
    assert report["ok"] is False


def test_podcast_observation_has_no_scientific_confidence(tmp_path, monkeypatch):
    import marceloclaro.orchestrator as module
    orchestrator, folder, observations = orchestrator_and_folder(tmp_path, monkeypatch)
    monkeypatch.setattr(module.metabus.memory, "add_reflection",
                        lambda *a, **k: pytest.fail("score/reflexão não comprova operação"))
    report = orchestrator.podcast(str(folder), executor=PipelineExecutor())
    assert report["ok"] is True
    assert report["audio_sha256"] == hashlib.sha256(b"audio from this invocation").hexdigest()
    assert report["metacognition"]["confidence_promoted"] is False
    assert observations[0][2]["externally_validated"] is False
    assert "score" not in observations[0][2]
