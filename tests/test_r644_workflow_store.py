"""Checkpoints duráveis e exclusão concorrente; nenhum modelo externo."""
import subprocess
import sys

import pytest

from marceloclaro.workflow_store import WorkflowStore


def test_checkpoint_survives_reopening(tmp_path):
    store = WorkflowStore(tmp_path)
    record = store.create("wf-1", {"nodes": [{"id": "analyse", "task": "Analisar"}]})
    record.update(status="completed", steps=1, nodes={"analyse": {"status": "completed", "output": "Resultado"}})
    store.save("wf-1", record)
    restored = WorkflowStore(tmp_path).load("wf-1")
    assert restored["nodes"]["analyse"]["output"] == "Resultado"
    assert restored["steps"] == 1 and restored["status"] == "completed"


@pytest.mark.parametrize("workflow_id", ["../private", "/tmp/private", "", ".", "a/b", "a" * 65])
def test_invalid_id_never_becomes_a_file(tmp_path, workflow_id):
    with pytest.raises(ValueError):
        WorkflowStore(tmp_path).create(workflow_id, {})
    assert not list(tmp_path.iterdir())


def test_existing_record_is_not_overwritten(tmp_path):
    store = WorkflowStore(tmp_path)
    original = store.create("wf-1", {"task": "Original"})
    with pytest.raises(FileExistsError):
        store.create("wf-1", {"task": "Replacement"})
    assert store.load("wf-1") == original


def test_failed_atomic_replace_preserves_last_checkpoint(tmp_path, monkeypatch):
    store = WorkflowStore(tmp_path)
    original = store.create("wf-1", {})
    import marceloclaro.workflow_store as module
    monkeypatch.setattr(module.os, "replace", lambda *args: (_ for _ in ()).throw(OSError("disco indisponível")))
    with pytest.raises(OSError):
        store.save("wf-1", {**original, "status": "completed"})
    assert store.load("wf-1") == original
    assert not list(tmp_path.glob("*.tmp"))


def test_process_lock_prevents_duplicate_workflow(tmp_path):
    store = WorkflowStore(tmp_path)
    code = (
        "import sys; from marceloclaro.workflow_store import WorkflowStore, WorkflowBusyError; "
        "store=WorkflowStore(sys.argv[1]); "
        "\ntry:\n with store.claim('wf-1'): print('unexpected')"
        "\nexcept WorkflowBusyError: print('busy')"
    )
    with store.claim("wf-1"):
        process = subprocess.run([sys.executable, "-c", code, str(tmp_path)],
                                 capture_output=True, text=True, timeout=10)
        assert process.returncode == 0 and process.stdout.strip() == "busy"
    with store.claim("wf-1"):
        pass


def test_corrupt_checkpoint_is_explicit(tmp_path):
    (tmp_path / "wf-1.json").write_text("{truncated", encoding="utf-8")
    with pytest.raises(ValueError, match="inválido"):
        WorkflowStore(tmp_path).load("wf-1")


def test_record_identity_cannot_redirect_checkpoint(tmp_path):
    with pytest.raises(ValueError):
        WorkflowStore(tmp_path).save("wf-1", {"workflow_id": "another"})
