"""Interrupção real de processos inertes e cancelamento MCP, sem provider."""
import asyncio
from copy import deepcopy
import json
import os
from pathlib import Path
import signal
import sys
import time
from threading import Event

import pytest

from integrations.harness_runtime import HarnessRuntime
from test_r640_autonomous import isolated_orchestrator, registry


def _running(pid):
    try:
        state = Path(f"/proc/{pid}/stat").read_text().split()[2]
    except FileNotFoundError:
        return False
    return state != "Z"


@pytest.fixture
def process_cli(tmp_path, monkeypatch):
    """A CLI cria um filho sem ação externa; o finalizer limpa o RED também."""
    pidfile = tmp_path / "child.json"
    executable = tmp_path / "isolated-cli"
    children = []
    def prepare(*, wait, inherit_pipes=False, ignore_term=False):
        executable.write_text(
            f"#!{sys.executable}\n"
            "import json, subprocess, sys, time\n"
            "from pathlib import Path\n"
            "sys.stdin.read()\n"
            f"child = subprocess.Popen([sys.executable, '-c', {('import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)' if ignore_term else 'import time; time.sleep(30)')!r}]"
            + (")\n" if inherit_pipes else ", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n")
            + f"Path({str(pidfile)!r}).write_text(json.dumps({{'child_pid': child.pid}}))\n"
            + ("time.sleep(30)\n" if wait else "print(json.dumps({'result': 'Resultado local inerte'}))\n"),
            encoding="utf-8",
        )
        executable.chmod(0o700)
        runtime = HarnessRuntime(tmp_path)
        monkeypatch.setattr(runtime, "_resolve_cli", lambda _: str(executable))
        return runtime, pidfile
    yield prepare
    if pidfile.exists():
        children.append(json.loads(pidfile.read_text())["child_pid"])
    for pid in children:
        if _running(pid):
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


@pytest.mark.skipif(os.name != "posix" or not Path("/proc").is_dir(), reason="Prova POSIX real usa /proc")
def test_timeout_stops_cli_descendant_before_return(process_cli):
    runtime, pidfile = process_cli(wait=True)
    result = runtime.execute("claude", "Sonda hermética", timeout=0.4)
    assert result["success"] is False and "limite" in result["error"]
    assert pidfile.exists(), "A sonda deve realmente iniciar o descendente."
    assert not _running(json.loads(pidfile.read_text())["child_pid"]), "Descendente sobreviveu ao prazo da CLI."


@pytest.mark.skipif(os.name != "posix" or not Path("/proc").is_dir(), reason="Prova POSIX real usa /proc")
def test_normal_exit_stops_background_descendant_before_return(process_cli):
    runtime, pidfile = process_cli(wait=False)
    result = runtime.execute("claude", "Sonda hermética", timeout=2)
    assert result["success"] is True and result["output"] == "Resultado local inerte"
    assert pidfile.exists(), "A sonda deve realmente iniciar o descendente."
    assert not _running(json.loads(pidfile.read_text())["child_pid"]), "Descendente sobreviveu à conclusão da CLI."


class _MemoryStore:
    def __init__(self):
        self.records = {}
    def create_record(self, workflow_id, record):
        self.records[workflow_id] = deepcopy(record)
    def save(self, workflow_id, record):
        self.records[workflow_id] = deepcopy(record)
    def load(self, workflow_id):
        return deepcopy(self.records[workflow_id])


def test_cancelled_mcp_workflow_does_not_execute_next_node(monkeypatch):
    asyncio.run(_cancelled_workflow_probe(monkeypatch))


async def _cancelled_workflow_probe(monkeypatch):
    from integrations import ecosystem_mcp as surface
    from marceloclaro.workflow import WorkflowCoordinator
    entered, release, finished = Event(), Event(), Event()
    calls = []
    class Child:
        def run(self, task, **kwargs):
            calls.append(task)
            if len(calls) == 1:
                entered.set()
                assert release.wait(5), "A sonda deve liberar o coordenador."
            return {"status": "completed", "success": True, "steps": 1,
                    "output": "Saída hermética", "task_id": "local-" + str(len(calls))}
    store = _MemoryStore()
    workflow = WorkflowCoordinator(Child(), store)
    run = workflow.run
    def observed(*args, **kwargs):
        try:
            return run(*args, **kwargs)
        finally:
            finished.set()
    monkeypatch.setattr(workflow, "run", observed)
    monkeypatch.setattr(surface, "get_workflow_coordinator", lambda: workflow)
    request = asyncio.create_task(surface.ecosystem_workflow([
        {"id": "a", "task": "Primeira etapa"},
        {"id": "b", "task": "Segunda etapa", "dependencies": ["a"]},
    ], workflow_id="cancelled-local"))
    try:
        assert await asyncio.to_thread(entered.wait, 5)
        request.cancel()
        await asyncio.sleep(0)
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await request
        assert await asyncio.to_thread(finished.wait, 5)
    finally:
        release.set()
        await asyncio.to_thread(finished.wait, 5)
    assert len(calls) == 1, "O cancelamento deve impedir novos nós."
    checkpoint = store.load("cancelled-local")
    assert checkpoint["success"] is False and checkpoint["status"] != "completed"
    assert checkpoint["nodes"]["a"]["execution_uncertain"] is True
    assert checkpoint["nodes"]["b"]["execution_attempted"] is False
    nodes = [{"id": "a", "task": "Primeira etapa"},
             {"id": "b", "task": "Segunda etapa", "dependencies": ["a"]}]
    resumed = workflow.run(nodes, workflow_id="cancelled-local", resume=True)
    assert len(calls) == 1 and resumed["success"] is False
    retried = workflow.run(nodes, workflow_id="cancelled-local", resume=True, retry_failed=True)
    assert len(calls) == 3 and retried["success"] is True
    assert retried["steps"] == 3 and retried["nodes"]["a"]["history"][0]["execution_uncertain"] is True


@pytest.mark.skipif(os.name != "posix" or not Path("/proc").is_dir(), reason="Prova POSIX real usa /proc")
def test_timeout_stops_descendant_holding_pipes_and_ignoring_term(process_cli):
    runtime, pidfile = process_cli(wait=True, inherit_pipes=True, ignore_term=True)
    started = time.monotonic()
    result = runtime.execute("claude", "Sonda hermética", timeout=0.4)
    assert result["success"] is False and "limite" in result["error"]
    assert time.monotonic() - started < 3, "Pipes herdados não podem reter a espera por 30 segundos."
    assert pidfile.exists() and not _running(json.loads(pidfile.read_text())["child_pid"])


@pytest.mark.skipif(os.name != "posix" or not Path("/proc").is_dir(), reason="Prova POSIX real usa /proc")
def test_runtime_cancel_stops_real_cli_and_descendant(process_cli):
    from concurrent.futures import ThreadPoolExecutor
    from integrations.execution_control import cancellation_scope
    event = Event()
    runtime, pidfile = process_cli(wait=True, inherit_pipes=True, ignore_term=True)
    def execute():
        with cancellation_scope(event):
            return runtime.execute("claude", "Sonda hermética", timeout=20)
    with ThreadPoolExecutor(max_workers=1) as pool:
        worker = pool.submit(execute)
        try:
            deadline = time.monotonic() + 5
            while not pidfile.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            assert pidfile.exists(), "A CLI deve iniciar antes do cancelamento."
            event.set()
            result = worker.result(timeout=3)
        finally:
            event.set()
    assert result["success"] is False and result["cancelled"] is True
    assert not _running(json.loads(pidfile.read_text())["child_pid"])


def test_cancel_between_nodes_preserves_completed_delivery_for_resume():
    from types import SimpleNamespace
    from integrations.execution_control import cancellation_scope
    from marceloclaro.workflow import WorkflowCoordinator
    event, calls = Event(), []
    class Store(_MemoryStore):
        def save(self, workflow_id, record):
            super().save(workflow_id, record)
            if record["nodes"]["a"]["status"] == "completed":
                event.set()
    store = Store()
    def execute(task, **kwargs):
        calls.append(task)
        return {"status": "completed", "success": True, "steps": 1,
                "output": "Entrega anterior preservada", "task_id": "local-" + str(len(calls))}
    workflow = WorkflowCoordinator(SimpleNamespace(run=execute), store)
    nodes = [{"id": "a", "task": "A"}, {"id": "b", "task": "B", "dependencies": ["a"]}]
    with cancellation_scope(event):
        record = workflow.run(nodes, workflow_id="between")
    assert len(calls) == 1 and record["nodes"]["a"]["status"] == "completed"
    assert record["nodes"]["b"]["execution_attempted"] is False and record["success"] is False
    resumed = workflow.run(nodes, workflow_id="between", resume=True)
    assert len(calls) == 2 and resumed["success"] is True
    assert resumed["nodes"]["a"]["task_id"] == "local-1"


def test_repeated_request_cancel_waits_for_worker_cleanup():
    asyncio.run(_repeated_cancel_probe())


async def _repeated_cancel_probe():
    from integrations.execution_control import is_cancelled, run_cancellable
    started, cleaning, release, finished = Event(), Event(), Event(), Event()
    def execute():
        started.set()
        while not is_cancelled():
            time.sleep(0.01)
        cleaning.set()
        assert release.wait(5)
        finished.set()
    request = asyncio.create_task(run_cancellable(execute))
    try:
        assert await asyncio.to_thread(started.wait, 5)
        request.cancel()
        assert await asyncio.to_thread(cleaning.wait, 5)
        request.cancel()
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        assert not request.done(), "Cancelamento repetido não pode abandonar a limpeza."
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await request
        assert finished.is_set()
    finally:
        release.set()
        await asyncio.to_thread(finished.wait, 5)


def test_anyio_cancel_scope_waits_for_worker_cleanup():
    import anyio
    anyio.run(_anyio_cancel_probe)


async def _anyio_cancel_probe():
    import anyio
    from integrations.execution_control import is_cancelled, run_cancellable
    started, cleaning, release, finished, returned = Event(), Event(), Event(), Event(), Event()
    request_scope = []
    def execute():
        started.set()
        while not is_cancelled():
            time.sleep(0.01)
        cleaning.set()
        assert release.wait(5)
        finished.set()
    async def caller():
        try:
            with anyio.CancelScope() as scope:
                request_scope.append(scope)
                await run_cancellable(execute)
        finally:
            returned.set()
    try:
        async with anyio.create_task_group() as group:
            group.start_soon(caller)
            assert await anyio.to_thread.run_sync(started.wait, 5)
            request_scope[0].cancel()
            assert await anyio.to_thread.run_sync(cleaning.wait, 5)
            await anyio.sleep(0.05)
            assert not returned.is_set(), "CancelScope não pode abandonar a limpeza síncrona."
            release.set()
        assert finished.is_set() and returned.is_set()
    finally:
        release.set()
        await anyio.to_thread.run_sync(finished.wait, 5)


def test_cancelled_knowledge_operation_does_not_wait_for_busy_mcp_lock(monkeypatch):
    asyncio.run(_cancelled_queue_probe(monkeypatch))


async def _cancelled_queue_probe(monkeypatch):
    from integrations import ecosystem_mcp as surface
    from integrations.execution_control import run_cancellable
    from threading import Lock
    from types import SimpleNamespace
    lock = Lock()
    calls, finished, entered = [], Event(), Event()
    def operation(**kwargs):
        calls.append(kwargs)
        return {"success": True}
    monkeypatch.setattr(surface, "_execution_lock", lock)
    monkeypatch.setattr(surface, "get_library_orchestrator", lambda: SimpleNamespace(local=operation))
    def queued():
        entered.set()
        try:
            return surface._knowledge_operation("local", {"probe": True})
        finally:
            finished.set()
    lock.acquire()
    request = asyncio.create_task(run_cancellable(queued))
    try:
        assert await asyncio.to_thread(entered.wait, 5)
        request.cancel()
        await asyncio.sleep(0.15)
        assert finished.is_set(), "A espera pelo lock deve reconhecer o cancelamento sem adquiri-lo."
        with pytest.raises(asyncio.CancelledError):
            await request
        assert calls == [], "Cancelar a fila não pode executar a operação."
    finally:
        lock.release()
        await asyncio.to_thread(finished.wait, 5)


@pytest.mark.parametrize("phase", ["before", "during"])
def test_autonomous_cancel_does_not_fallback_or_complete(isolated_orchestrator, registry, phase):
    from integrations.execution_control import cancellation_scope
    from marceloclaro.autonomous import AutonomousCoordinator
    from mci.blackboard import blackboard
    from test_r640_autonomous import RuntimeDouble
    event = Event()
    class Runtime(RuntimeDouble):
        def execute(self, *args, **kwargs):
            outcome = super().execute(*args, **kwargs)
            event.set()
            return outcome
    runtime = Runtime(available=("claude", "codex", "antigravity"))
    if phase == "before":
        event.set()
    with cancellation_scope(event):
        result = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código", max_steps=2)
    assert result["success"] is False and result["status"] != "completed"
    assert len(runtime.calls) == (0 if phase == "before" else 1)
    assert result["fallbacks"] == [] and "cancelada" in result["error"]
    if phase == "before":
        assert result["task_id"] is None and blackboard.tasks == {}
    else:
        assert blackboard.tasks[result["task_id"]].status == "failed"
        assert blackboard.registry[result["agent_id"]].status == "available"


def test_cancel_after_checkpoint_reservation_prevents_coordinator_call():
    from types import SimpleNamespace
    from integrations.execution_control import cancellation_scope
    from marceloclaro.workflow import WorkflowCoordinator
    event, calls = Event(), []
    class Store(_MemoryStore):
        def save(self, workflow_id, record):
            super().save(workflow_id, record)
            if record["nodes"]["a"]["status"] == "running":
                event.set()
    def execute(task, **kwargs):
        calls.append(task)
        return {"status": "completed", "success": True, "steps": 1,
                "output": "Saída local", "task_id": "should-not-start"}
    store = Store()
    workflow = WorkflowCoordinator(SimpleNamespace(run=execute), store)
    with cancellation_scope(event):
        result = workflow.run([{"id": "a", "task": "A"}], workflow_id="precall")
    assert calls == [], "Cancelar após persistir a reserva deve impedir a chamada externa."
    assert result["success"] is False and result["steps"] == 0
    assert result["nodes"]["a"]["execution_attempted"] is False


def test_windows_tree_command_failure_still_stops_real_primary_process(monkeypatch):
    """Falha Windows simulada; o fallback encerra um processo local real."""
    import subprocess
    from types import SimpleNamespace
    from integrations import harness_runtime as module
    process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    calls = []
    def taskkill(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 1, "", "falha controlada")
    monkeypatch.setattr(module, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(module.subprocess, "run", taskkill)
    try:
        HarnessRuntime._stop_process_tree(process)
        time.sleep(0.05)
        assert process.poll() is not None, "Falha de taskkill não pode deixar a CLI principal executando."
        assert calls[0][0] == ["taskkill", "/PID", str(process.pid), "/T", "/F"]
        assert calls[0][1]["shell"] is False and calls[0][1]["timeout"] == 2
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=2)
