"""R1106: cache TTL, orçamento, snapshot verificado e execução real gated."""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from integrations.gjq_budget import (
    budget_status,
    check_budget,
    hardware_enabled,
    record_submission,
    usage_today,
)
from integrations.gjq_real_execution import real_backend, real_execution_enabled
from integrations.gjq_ttl_cache import TTLCache
from integrations.gjq_verified_snapshot import (
    build_verified_snapshot,
    compare_snapshot,
    read_snapshot,
    write_snapshot,
)

QASM = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""


# ---------------------------------------------------------------- cache TTL
def test_ttl_cache_hit_miss_expiracao_e_force():
    agora = [100.0]
    cache = TTLCache(maxsize=4, ttl=10, clock=lambda: agora[0])
    chamadas = []

    def factory():
        chamadas.append(1)
        return {"valor": len(chamadas)}

    valor, meta = cache.get_or_set(("a",), factory)
    assert valor == {"valor": 1}
    assert meta["hit"] is False
    assert meta["ttl_seconds"] == 10

    valor2, meta2 = cache.get_or_set(("a",), factory)
    assert valor2 == {"valor": 1}
    assert meta2["hit"] is True
    assert len(chamadas) == 1

    agora[0] += 11
    valor3, meta3 = cache.get_or_set(("a",), factory)
    assert valor3 == {"valor": 2}
    assert meta3["hit"] is False

    valor4, meta4 = cache.get_or_set(("a",), factory, force=True)
    assert valor4 == {"valor": 3}
    assert meta4["hit"] is False


def test_ttl_cache_limita_tamanho():
    cache = TTLCache(maxsize=2, ttl=60)
    cache.set(("a",), 1)
    cache.set(("b",), 2)
    cache.set(("c",), 3)
    assert cache.stats()["size"] <= 2


# ---------------------------------------------------------------- orçamento
def test_gate_de_hardware_desabilitado_bloqueia(tmp_path, monkeypatch):
    monkeypatch.setenv("GJQ_HARDWARE_ENABLED", "0")
    monkeypatch.setenv("GJQ_BUDGET_LEDGER", str(tmp_path / "ledger.jsonl"))
    assert hardware_enabled() is False
    resultado = check_budget("Baihua", 128, hardware=True)
    assert resultado["allowed"] is False
    assert "GJQ_HARDWARE_ENABLED" in resultado["reason"]


def test_orcamento_de_shots_e_submissoes(tmp_path, monkeypatch):
    ledger = tmp_path / "ledger.jsonl"
    monkeypatch.setenv("GJQ_BUDGET_LEDGER", str(ledger))
    monkeypatch.setenv("GJQ_DAILY_SHOTS", "100")
    monkeypatch.setenv("GJQ_DAILY_SUBMISSIONS", "2")
    monkeypatch.setenv("GJQ_DAILY_HARDWARE_SUBMISSIONS", "1")
    monkeypatch.setenv("GJQ_DAILY_HARDWARE_SHOTS", "50")
    monkeypatch.setenv("GJQ_HARDWARE_ENABLED", "1")

    record_submission("FAS-CPU", 80, "task-1", hardware=False, path=ledger)
    uso = usage_today(path=ledger)
    assert uso["shots"] == 80
    assert uso["submissions"] == 1

    bloqueado_shots = check_budget("FAS-CPU", 30, hardware=False, path=ledger)
    assert bloqueado_shots["allowed"] is False
    assert "shots" in bloqueado_shots["reason"]

    record_submission("Baihua", 40, "task-2", hardware=True, path=ledger)
    bloqueado_hw = check_budget("Baihua", 10, hardware=True, path=ledger)
    assert bloqueado_hw["allowed"] is False
    assert "hardware" in bloqueado_hw["reason"].lower()

    status = budget_status(path=ledger)
    assert status["usage"]["hardware_submissions"] == 1
    assert status["hardware_enabled"] is True
    assert status["ledger"].endswith("ledger.jsonl")


def test_ledger_tolera_linha_invalida(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text('{"shots": 10}\nnao-json\n', encoding="utf-8")
    uso = usage_today(path=ledger)
    assert uso["shots"] == 10


# ---------------------------------------------------------------- snapshot
def test_snapshot_verificado_deterministico_e_comparavel(tmp_path):
    live = [{"name": "FAS-CPU"}, {"name": "Baihua"}, {"name": "BackendNovo"}]
    snap = build_verified_snapshot(live, generated_at="2026-11-09T00:00:00Z")
    assert snap["live_count"] == 3
    assert snap["registry_count"] == 19
    assert "BackendNovo" in snap["missing_in_registry"]
    assert len(snap["snapshot_sha256"]) == 64
    ids = {item["registry_id"] for item in snap["entries"]}
    assert "jiuxiao-fas-cpu" in ids
    assert "baihua" in ids

    again = build_verified_snapshot(live, generated_at="2026-11-09T00:00:00Z")
    assert again["snapshot_sha256"] == snap["snapshot_sha256"]

    path = tmp_path / "verified.json"
    write_snapshot(path, snap)
    loaded = read_snapshot(path)
    assert loaded["snapshot_sha256"] == snap["snapshot_sha256"]

    same = compare_snapshot(snap, build_verified_snapshot(live, generated_at="2026-11-09T01:00:00Z"))
    assert same["changed"] is False

    changed = compare_snapshot(
        snap,
        build_verified_snapshot(
            [{"name": "FAS-CPU"}, {"name": "BaihuaRenomeado"}, {"name": "BackendNovo"}],
            generated_at="2026-11-09T02:00:00Z",
        ),
    )
    assert changed["changed"] is True
    assert changed["renamed"]


# ---------------------------------------------------------------- runtime
def test_runtime_cache_config_e_properties(monkeypatch):
    import integrations.gjq_runtime_mcp as runtime

    class FakeBackend:
        def configuration(self):
            return {"name": "FAS-CPU"}

        def properties(self):
            return {"t1": 1}

    class FakeService:
        def __init__(self):
            self.calls = {"backend": 0, "config": 0, "props": 0}

        def backend(self, name):
            self.calls["backend"] += 1
            return FakeBackend()

        def list_backends(self):
            return [{"name": "FAS-CPU"}]

    fake = FakeService()
    monkeypatch.setattr(runtime, "_key_present", lambda: True)
    monkeypatch.setattr(runtime, "_get_service", lambda: fake)
    runtime._reset_cache()
    tools = runtime.create_server()._tool_manager._tools

    r1 = tools["gjq_backend_config"].fn("FAS-CPU")
    r2 = tools["gjq_backend_config"].fn("FAS-CPU")
    assert r1["cache"]["hit"] is False
    assert r2["cache"]["hit"] is True
    assert fake.calls["config"] == 1

    r3 = tools["gjq_backend_config"].fn("FAS-CPU", True)
    assert r3["cache"]["hit"] is False
    assert fake.calls["config"] == 2

    p1 = tools["gjq_backend_properties"].fn("FAS-CPU")
    p2 = tools["gjq_backend_properties"].fn("FAS-CPU")
    assert p2["cache"]["hit"] is True
    assert fake.calls["props"] == 1


def test_runtime_gate_de_hardware_global_bloqueia_antes_do_servico(monkeypatch):
    import integrations.gjq_runtime_mcp as runtime

    monkeypatch.setattr(runtime, "_key_present", lambda: True)
    monkeypatch.setenv("GJQ_HARDWARE_ENABLED", "0")
    monkeypatch.setattr(
        runtime, "_get_service",
        lambda: (_ for _ in ()).throw(AssertionError("serviço não deveria ser chamado")),
    )
    tools = runtime.create_server()._tool_manager._tools
    resultado = tools["gjq_sample"].fn(QASM, "Baihua", 128, 1, True, None, True, True)
    assert resultado["status"] == "blocked"
    assert resultado["executed"] is False
    assert "GJQ_HARDWARE_ENABLED" in resultado["reason"]


# ---------------------------------------------------------------- real gate
def test_real_execution_exige_as_duas_variaveis(monkeypatch):
    monkeypatch.delenv("GJQ_REAL_EXECUTION", raising=False)
    monkeypatch.delenv("GJQ_API_KEY", raising=False)
    assert real_execution_enabled() is False
    monkeypatch.setenv("GJQ_REAL_EXECUTION", "1")
    assert real_execution_enabled() is False
    monkeypatch.setenv("GJQ_API_KEY", "chave-ficticia")
    assert real_execution_enabled() is True


def test_real_backend_recusa_hardware(monkeypatch):
    monkeypatch.setenv("GJQ_REAL_EXECUTION_BACKEND", "Baihua")
    with pytest.raises(ValueError):
        real_backend()
    monkeypatch.setenv("GJQ_REAL_EXECUTION_BACKEND", "FAS-CPU")
    assert real_backend() == "FAS-CPU"


@pytest.mark.skipif(not real_execution_enabled(), reason="GJQ_REAL_EXECUTION e GJQ_API_KEY ausentes")
def test_real_bell_fas_cpu_gated():
    """Execução real mínima; só roda com as duas variáveis explícitas."""
    import integrations.gjq_runtime_mcp as runtime

    tools = runtime.create_server()._tool_manager._tools
    backend = real_backend()
    shots = min(int(__import__("os").environ.get("GJQ_REAL_EXECUTION_SHOTS", "128")), 1024)
    sub = tools["gjq_sample"].fn(QASM, backend, shots, 1, True, None, False, True)
    assert sub["status"] == "success", sub
    assert sub["executed"] is True
    assert sub["hardware"] is False
    task_id = sub["task_id"]
    assert task_id

    deadline = time.time() + 180
    estado = ""
    while time.time() < deadline:
        status = tools["gjq_task_status"].fn(task_id)
        estado = json.dumps(status.get("task_status", "")).upper()
        if "DONE" in estado:
            break
        if "ERROR" in estado or "CANCELLED" in estado:
            pytest.fail(f"tarefa {task_id} terminou em {estado}")
        time.sleep(5)
    else:
        pytest.skip(f"tarefa {task_id} ainda em execução após 180 s")

    resultado = tools["gjq_task_result"].fn(task_id)
    assert resultado["status"] == "success"
    audit = resultado.get("audit")
    assert audit and audit.get("ok") is True
