"""Rotas públicas MCP: cancelar uma requisição não inicia trabalho da fila."""
import asyncio
from threading import Event, Lock
from types import SimpleNamespace

import pytest

ROUTES = [
    ("ecosystem_knowledge_plan", "knowledge_evolution_plan"),
    ("ecosystem_scientific_run", "scientific_reproducible_run"),
    ("ecosystem_scientific_runtime", "scientific_runtime_run"),
    ("ecosystem_dataset_download", "scientific_dataset_download"),
    ("ecosystem_dataset_custom", "scientific_dataset_custom"),
    ("ecosystem_scientific_plugins", "scientific_plugin_action"),
    ("ecosystem_gemini_notebook", "gemini_notebook_action"),
]


class ObservedLock:
    def __init__(self):
        self.lock = Lock()
        self.waiting = Event()
    def acquire(self, *args, **kwargs):
        self.waiting.set()
        return self.lock.acquire(*args, **kwargs)
    def release(self):
        self.lock.release()


def prepare(monkeypatch, method, worker):
    from integrations import ecosystem_mcp as gateway
    from marceloclaro import knowledge_evolution, runtime_actions
    from integrations import gemini_notebook
    # Estes testes isolam transporte/fila: os validadores de domínio possuem
    # baterias próprias. Não executamos modelos, rede ou operações de notebook.
    monkeypatch.setattr(knowledge_evolution, "validate_plan_config", lambda config: dict(config))
    monkeypatch.setattr(knowledge_evolution, "validate_science_config", lambda config: dict(config))
    monkeypatch.setattr(runtime_actions, "validate_action", lambda kind, config: dict(config))
    monkeypatch.setattr(gemini_notebook, "validate_notebook_config", lambda config: dict(config))
    monkeypatch.setattr(gateway, "get_library_orchestrator", lambda: SimpleNamespace(**{method: worker}))
    lock = ObservedLock()
    monkeypatch.setattr(gateway, "_execution_lock", lock)
    return gateway, lock


@pytest.mark.parametrize("route,method", ROUTES)
def test_cancelled_queue_never_invokes_operation(monkeypatch, route, method):
    entered, finished = Event(), Event()
    def worker(**config):
        entered.set()
        finished.set()
        return {"status": "completed"}
    gateway, lock = prepare(monkeypatch, method, worker)
    lock.lock.acquire()
    async def prove():
        task = asyncio.create_task(getattr(gateway, route)({}))
        assert await asyncio.to_thread(lock.waiting.wait, 2), "worker não alcançou a fila"
        task.cancel()
        try:
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, 2)
        finally:
            lock.lock.release()
        # Espera suficiente para detectar o início tardio da implementação RED.
        await asyncio.to_thread(finished.wait, 0.15)
        assert not entered.is_set(), "operação começou depois do cancelamento"
    asyncio.run(prove())


@pytest.mark.parametrize("route,method", ROUTES)
def test_active_worker_receives_signal_and_cleanup_is_awaited(monkeypatch, route, method):
    from integrations.execution_control import is_cancelled
    entered, cleaned, stop = Event(), Event(), Event()
    signals = []
    def worker(**config):
        entered.set()
        while not is_cancelled() and not stop.wait(0.01):
            pass
        signals.append(is_cancelled())
        cleaned.set()
        return {"status": "cancelled" if signals[-1] else "completed"}
    gateway, _ = prepare(monkeypatch, method, worker)
    async def prove():
        task = asyncio.create_task(getattr(gateway, route)({}))
        assert await asyncio.to_thread(entered.wait, 2)
        task.cancel()
        try:
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, 2)
            assert cleaned.is_set(), "gateway abandonou worker antes de sua limpeza"
            assert signals == [True]
        finally:
            stop.set()
            await asyncio.to_thread(cleaned.wait, 1)
    asyncio.run(prove())
