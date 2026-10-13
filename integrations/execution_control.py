"""Cancelamento cooperativo de operações síncronas expostas pelo MCP.

O contexto atravessa asyncio.to_thread; cada requisição possui seu próprio
sinal. A espera de limpeza não abandona a thread ao cancelar a requisição.
"""
from __future__ import annotations

import asyncio
import anyio
from contextlib import contextmanager
from contextvars import ContextVar
from threading import Event


_CANCELLATION: ContextVar[Event | None] = ContextVar("core_execution_cancellation", default=None)


class ExecutionCancelled(Exception):
    """A requisição deixou de autorizar novas operações desta execução."""


class ExecutionBusy(Exception):
    """A operação exige aquisição imediata, mas a rede está ocupada."""


def is_cancelled() -> bool:
    event = _CANCELLATION.get()
    return event is not None and event.is_set()


@contextmanager
def cancellation_scope(event: Event):
    token = _CANCELLATION.set(event)
    try:
        yield
    finally:
        _CANCELLATION.reset(token)


@contextmanager
def execution_gate(lock, *, wait=True):
    """Espera cooperativa; cancelar a fila nunca inicia a operação protegida."""
    while True:
        if is_cancelled():
            raise ExecutionCancelled("Execução cancelada enquanto aguardava a rede.")
        acquired = lock.acquire(timeout=0.05) if wait else lock.acquire(blocking=False)
        if acquired:
            break
        if not wait:
            raise ExecutionBusy("Já existe uma execução na rede; aguarde sua conclusão.")
    try:
        if is_cancelled():
            raise ExecutionCancelled("Execução cancelada antes de iniciar a operação.")
        yield
    finally:
        lock.release()


async def run_cancellable(function, *args, **kwargs):
    """Sinaliza o worker cancelado e aguarda sua limpeza antes de propagar."""
    event = Event()
    def execute():
        with cancellation_scope(event):
            if event.is_set():
                raise ExecutionCancelled("Execução cancelada antes de iniciar.")
            return function(*args, **kwargs)
    worker = asyncio.create_task(asyncio.to_thread(execute))
    try:
        return await asyncio.shield(worker)
    except asyncio.CancelledError:
        event.set()
        # FastMCP/AnyIO entrega cancelamento em cada await. O shield do scope
        # protege essa limpeza; cancelamentos explícitos Task.cancel() ainda
        # chegam e são consumidos até o worker liberar os recursos.
        with anyio.CancelScope(shield=True):
            while not worker.done():
                try:
                    await asyncio.shield(worker)
                except asyncio.CancelledError:
                    continue
                except Exception:
                    break
            if worker.done():
                try:
                    worker.result()
                except (Exception, asyncio.CancelledError):
                    # Conservar o cancelamento externo, inclusive se a própria
                    # operação concluiu sua limpeza com uma falha.
                    pass
        raise
