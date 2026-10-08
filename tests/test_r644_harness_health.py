"""SPEC-935-R644: histórico real de saúde, sem chamar modelos no inventário."""

import json
import os
import sqlite3
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from integrations.harness_health import HarnessHealthStore
from integrations.harness_runtime import HarnessRuntime


@pytest.fixture
def runtime(tmp_path, monkeypatch):
    monkeypatch.setenv("HARNESS_HEALTH_PATH", str(tmp_path / "health.sqlite3"))
    harness = HarnessRuntime(tmp_path)
    binary = tmp_path / "claude"
    binary.write_text("CLI fixture", encoding="utf-8")
    binary.chmod(0o755)
    monkeypatch.setattr(harness, "_resolve_cli", lambda name: str(binary))
    return harness


def response(output="Análise concluída", error=False, returncode=0, stderr=""):
    return subprocess.CompletedProcess([], returncode, json.dumps({"result": output, "is_error": error}), stderr)


def test_initial_status_does_not_run_any_subprocess_or_create_database(runtime, monkeypatch):
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *a, **k: pytest.fail("Inventário não executa CLIs"))
    state = runtime.status()["claude"]
    assert state["available"] and state["eligible_for_auto"]
    assert state["verification"] == "installation_only"
    assert state["health"]["last_outcome"] is None
    assert not (runtime.repo_root / "health.sqlite3").exists()


def test_success_persists_real_execution_and_duration_without_content(runtime, monkeypatch):
    ticks = iter([2.0, 3.25])
    monkeypatch.setattr("integrations.harness_runtime.time.monotonic", lambda: next(ticks))
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *a, **k: response("private_output_935"))
    assert runtime.execute("claude", "private_prompt_935")["success"]
    store = runtime.health_store
    reloaded = HarnessHealthStore(store.path)
    health = reloaded.snapshot("claude", runtime._resolve_cli("claude"))
    assert health["last_outcome"] == "success"
    assert health["last_success_at"] and health["last_attempt_at"]
    assert health["duration_seconds"] == pytest.approx(1.25)
    assert runtime.status()["claude"]["verification"] == "execution_succeeded"
    assert runtime.status()["claude"]["eligible_for_auto"]
    database = store.path.read_bytes()
    assert b"private_output_935" not in database and b"private_prompt_935" not in database


@pytest.mark.parametrize("failure,category", [("Credit balance is too low", "account_limit"), ("authentication failed", "authentication"), ("service unavailable HTTP 503", "unavailable")])
def test_provider_failure_is_sanitized_and_cools_only_automatic_selection(runtime, monkeypatch, failure, category):
    calls = []
    def run(*args, **kwargs):
        calls.append(args)
        return response(failure + " api_key=private_secret_935", True, 1)
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", run)
    result = runtime.execute("claude", "private_prompt_935")
    state = runtime.status()["claude"]
    assert not result["success"]
    assert state["available"] and not state["eligible_for_auto"]
    assert state["verification"] == "execution_failed"
    assert state["health"]["error_category"] == category
    assert 0 < state["health"]["cooldown_remaining_seconds"] <= 120
    assert "private_secret_935" not in json.dumps(state)
    assert b"private_secret_935" not in runtime.health_store.path.read_bytes()
    # A escolha explícita continua disponível; não há retry implícito.
    runtime.execute("claude", "Tentar explicitamente")
    assert len(calls) == 2


def test_failure_reported_in_success_exit_is_also_classified(runtime, monkeypatch):
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *a, **k: response("Credit balance is too low secret_marker_935", True))
    result = runtime.execute("claude", "Analise")
    assert not result["success"]
    assert runtime.status()["claude"]["health"]["error_category"] == "account_limit"
    assert "saldo" in result["error"]
    assert "secret_marker_935" not in result["error"]


def test_cooldown_expires_and_success_clears_it(tmp_path):
    clock = [1000.0]
    store = HarnessHealthStore(tmp_path / "health.sqlite3", clock=lambda: clock[0])
    store.record("claude", "/tools/claude", success=False, duration_seconds=1, error_category="authentication")
    assert store.snapshot("claude", "/tools/claude")["cooldown_remaining_seconds"] == 120
    clock[0] += 121
    assert store.snapshot("claude", "/tools/claude")["cooldown_remaining_seconds"] == 0
    store.record("claude", "/tools/claude", success=False, duration_seconds=2, error_category="unavailable")
    store.record("claude", "/tools/claude", success=True, duration_seconds=3)
    state = store.snapshot("claude", "/tools/claude")
    assert state["cooldown_remaining_seconds"] == 0
    assert state["last_failure_at"] and state["last_success_at"]
    assert state["error_category"] is None


def test_binary_change_invalidates_observation_and_cooldown(runtime, monkeypatch):
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *a, **k: response("authentication failed", True, 1))
    runtime.execute("claude", "Analise")
    binary = Path(runtime._resolve_cli("claude"))
    original = binary.stat()
    # Uma atualização preservando o tamanho ainda invalida a observação.
    os.utime(binary, ns=(original.st_atime_ns, original.st_mtime_ns + 1_000_000_000))
    state = runtime.status()["claude"]
    assert state["eligible_for_auto"]
    assert state["verification"] == "installation_only"
    assert state["health"]["last_outcome"] is None
    another = runtime.repo_root / "different-cli"
    another.write_text("different", encoding="utf-8")
    monkeypatch.setattr(runtime, "_resolve_cli", lambda name: str(another))
    assert runtime.status()["claude"]["health"]["last_outcome"] is None


def test_wall_clock_rollback_never_extends_a_cooldown(tmp_path):
    clock = [1000.0]
    store = HarnessHealthStore(tmp_path / "health.sqlite3", clock=lambda: clock[0])
    store.record("claude", "/tools/claude", success=False, duration_seconds=1, error_category="account_limit")
    clock[0] -= 3600
    assert store.snapshot("claude", "/tools/claude")["cooldown_remaining_seconds"] == 0


def test_binary_updated_during_execution_cannot_inherit_its_old_health(runtime, monkeypatch):
    binary = Path(runtime._resolve_cli("claude"))
    def update_while_running(*args, **kwargs):
        original = binary.stat()
        os.utime(binary, ns=(original.st_atime_ns, original.st_mtime_ns + 1_000_000_000))
        return response()
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", update_while_running)
    assert runtime.execute("claude", "Analise")["success"]
    assert runtime.status()["claude"]["verification"] == "installation_only"


def test_symlink_database_target_is_not_modified(tmp_path):
    target = tmp_path / "private-target"
    target.write_text("preserve", encoding="utf-8")
    link = tmp_path / "health.sqlite3"
    link.symlink_to(target)
    store = HarnessHealthStore(link)
    store.record("claude", "/tools/claude", success=True, duration_seconds=1)
    assert target.read_text(encoding="utf-8") == "preserve"
    assert store.snapshot("claude", "/tools/claude")["storage"] == "memory"


def test_timeout_and_spawn_failure_are_observed(runtime, monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"], output="private_partial_935")
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", timeout)
    assert not runtime.execute("claude", "Analise", timeout=.1)["success"]
    assert runtime.status()["claude"]["health"]["error_category"] == "timeout"
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *a, **k: (_ for _ in ()).throw(OSError("private_os_error_935")))
    assert not runtime.execute("claude", "Analise")["success"]
    assert runtime.status()["claude"]["health"]["error_category"] == "unavailable"


def test_invalid_input_is_not_a_real_execution_observation(runtime, monkeypatch):
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *a, **k: pytest.fail("Não iniciar CLI"))
    assert not runtime.execute("claude", "", timeout=1)["success"]
    assert not runtime.execute("claude", "Analise", timeout=0)["success"]
    assert runtime.status()["claude"]["health"]["last_outcome"] is None


def test_unwritable_storage_keeps_execution_and_in_memory_health(tmp_path, monkeypatch):
    blocker = tmp_path / "blocked"
    blocker.write_text("file", encoding="utf-8")
    monkeypatch.setenv("HARNESS_HEALTH_PATH", str(blocker / "health.sqlite3"))
    harness = HarnessRuntime(tmp_path)
    monkeypatch.setattr(harness, "_resolve_cli", lambda name: "/tools/claude")
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *a, **k: response("authentication failed", True, 1))
    assert not harness.execute("claude", "Analise")["success"]
    state = harness.status()["claude"]
    assert not state["eligible_for_auto"]
    assert state["health"]["storage"] == "memory"


def test_concurrent_instances_preserve_all_executor_observations(tmp_path):
    path = tmp_path / "health.sqlite3"
    def write(index):
        store = HarnessHealthStore(path)
        store.record(f"executor{index}", f"/tools/cli{index}", success=True, duration_seconds=.1)
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(write, range(16)))
    reloaded = HarnessHealthStore(path)
    for index in range(16):
        assert reloaded.snapshot(f"executor{index}", f"/tools/cli{index}")["last_outcome"] == "success"


def test_late_writer_preserves_latest_outcome_and_both_history_timestamps(tmp_path):
    path = tmp_path / "health.sqlite3"
    recent = HarnessHealthStore(path, clock=lambda: 1001)
    late = HarnessHealthStore(path, clock=lambda: 1000)
    recent.record("claude", "/tools/claude", success=True, duration_seconds=2)
    late.record("claude", "/tools/claude", success=False, duration_seconds=1, error_category="authentication")
    state = HarnessHealthStore(path, clock=lambda: 1002).snapshot("claude", "/tools/claude")
    assert state["last_outcome"] == "success" and state["duration_seconds"] == 2
    assert state["last_success_at"] == "1970-01-01T00:16:41Z"
    assert state["last_failure_at"] == "1970-01-01T00:16:40Z"
    assert state["cooldown_remaining_seconds"] == 0


def test_corrupt_database_never_breaks_status_or_execution(runtime, monkeypatch):
    runtime.health_store.path.write_bytes(b"corrupt database")
    assert runtime.status()["claude"]["eligible_for_auto"]
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *a, **k: response())
    assert runtime.execute("claude", "Analise")["success"]
    assert runtime.status()["claude"]["health"]["last_outcome"] == "success"
    assert runtime.status()["claude"]["health"]["storage"] == "memory"


def test_store_rejects_arbitrary_failure_text_and_private_permissions(tmp_path):
    store = HarnessHealthStore(tmp_path / "health.sqlite3")
    store.record("claude", "/tools/claude", success=False, duration_seconds=1, error_category="api_key=secret_935")
    state = store.snapshot("claude", "/tools/claude")
    assert state["error_category"] == "execution_failed"
    assert "secret_935" not in json.dumps(state)
    assert store.path.stat().st_mode & 0o077 == 0
    with sqlite3.connect(store.path) as conn:
        assert "secret_935" not in str(conn.execute("SELECT * FROM harness_health").fetchall())
