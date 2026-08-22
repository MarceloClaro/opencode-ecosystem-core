# -*- coding: utf-8 -*-
"""
Worker Pool — escala N workers dsh no Blackboard com Trust/Economy.

Cada worker é um AgentCard "dsh-worker-i" com capability dsh_execution.
submit(objective) fan-out: o mesmo objetivo é executado em paralelo por
todos os workers via adapter.run_task (runner injetável para TDD).
"""

from __future__ import annotations

import concurrent.futures
import os
from typing import Any, Callable, Dict, List, Optional

DEFAULT_DSH_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "deepseek-harness",
)


class DeepSeekWorkerPool:
    """Pool escalável de workers do dsh registrados no Blackboard."""

    WORKER_CAPABILITIES = [
        "dsh_execution",
        "external_agent_delegation",
        "autonomous_production",
    ]

    def __init__(
        self,
        metabus: Any | None = None,
        adapter: Any | None = None,
        dsh_root: str | None = None,
    ):
        self.dsh_root = os.path.abspath(dsh_root or DEFAULT_DSH_ROOT)
        if metabus is not None:
            self.metabus = metabus
        else:
            from mci.metabus import metabus as _global_metabus

            self.metabus = _global_metabus

        if adapter is not None:
            self.adapter = adapter
        else:
            from integrations.deepseek_harness.adapter import DeepSeekHarnessAdapter

            self.adapter = DeepSeekHarnessAdapter(dsh_root=self.dsh_root)

        self._workers: List[str] = []
        self._runs: int = 0
        self._successes: int = 0
        self._failures: int = 0
        # Trust/Economy — lazy, tolera ausência
        self._trust: Any | None = None
        self._economy: Any | None = None
        try:
            from trust import create_trust_engine

            self._trust = create_trust_engine()
        except Exception:
            self._trust = None
        try:
            from economy import TokenEconomy

            self._economy = TokenEconomy()
        except Exception:
            self._economy = None

    # ------------------------------------------------------------------
    def scale(self, n: int) -> List[str]:
        """Ajusta o pool para exatamente n workers (0 desregistra todos)."""
        n = max(0, int(n))
        current = len(self._workers)

        if n == current:
            return list(self._workers)

        if n < current:
            # Remove excedentes do Blackboard e da lista
            to_remove = self._workers[n:]
            for worker_id in to_remove:
                try:
                    from mci.blackboard import blackboard

                    if worker_id in blackboard.registry:
                        del blackboard.registry[worker_id]
                except Exception:
                    pass
            self._workers = self._workers[:n]
            return list(self._workers)

        # n > current: adiciona novos workers
        for i in range(current, n):
            worker_id = f"dsh-worker-{i}"
            # Evita duplicata se já existe no registry por execução anterior
            if worker_id in self._workers:
                continue
            try:
                self.metabus.publish(
                    "agent.register",
                    {
                        "agent_id": worker_id,
                        "name": f"DeepSeek Harness Worker {i}",
                        "description": (
                            "Worker autônomo do DeepSeek Harness escalado pelo "
                            "OpenCode Ecosystem Core (SPEC-935-R433)."
                        ),
                        "capabilities": list(self.WORKER_CAPABILITIES),
                        "schema": {},
                    },
                    source_agent="deepseek-harness-pool",
                )
            except Exception:
                # Fallback direto no registry quando publish falha
                try:
                    from mci.blackboard import AgentCard, blackboard

                    card = AgentCard(
                        agent_id=worker_id,
                        name=f"DeepSeek Harness Worker {i}",
                        description="Worker dsh escalado pelo Core.",
                        capabilities=list(self.WORKER_CAPABILITIES),
                        schema={},
                    )
                    blackboard.registry[worker_id] = card
                except Exception:
                    continue
            self._workers.append(worker_id)

        return list(self._workers)

    def list_workers(self) -> List[Dict[str, Any]]:
        """Lista workers ativos com seus AgentCards."""
        try:
            from mci.blackboard import blackboard
        except Exception:
            return []
        result: List[Dict[str, Any]] = []
        for worker_id in list(self._workers):
            card = blackboard.registry.get(worker_id)
            if card is not None:
                try:
                    result.append(card.to_dict())
                except Exception:
                    result.append({"agent_id": worker_id, "capabilities": list(self.WORKER_CAPABILITIES)})
        return result

    def submit(
        self,
        objective: str,
        runner: Optional[Callable[..., Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """Executa o objetivo em paralelo por todos os workers.

        Cada worker invoca adapter.run_task com o mesmo prompt (fan-out).
        Runner injetável garante determinismo em testes.
        """
        workers = list(self._workers)
        if not workers:
            return []

        def _run_for_worker(worker_id: str) -> Dict[str, Any]:
            res = self.adapter.run_task(objective, runner=runner)
            # Normaliza com proveniência do worker
            out: Dict[str, Any] = dict(res) if isinstance(res, dict) else {"status": "completed", "final_response": str(res)}
            out["worker"] = worker_id
            out["objective"] = objective

            # Trust learning por worker
            if self._trust is not None:
                try:
                    success = out.get("status") == "completed"
                    self._trust.learn(f"delegate:{worker_id}", success=success)
                except Exception:
                    pass

            # Token economy (best-effort)
            if self._economy is not None:
                try:
                    # post + commit + resolve com task_id sintético por execução
                    task_id = f"dsh-{worker_id}-{self._runs + hash(objective) % 10000:05d}"
                    # Não falha o fluxo se a economia estiver indisponível
                    self._economy.post_task(worker_id, task_id, priority="normal")
                    self._economy.commit(worker_id, task_id, amount=1.0)
                    self._economy.resolve(task_id, success=(out.get("status") == "completed"))
                except Exception:
                    pass

            return out

        max_workers = min(len(workers), 4)
        results: List[Dict[str, Any]] = []
        if max_workers <= 1:
            for wid in workers:
                results.append(_run_for_worker(wid))
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(_run_for_worker, wid): wid for wid in workers}
                # Preserva ordem dos workers na saída
                ordered: Dict[str, Dict[str, Any]] = {}
                for fut in concurrent.futures.as_completed(futures):
                    wid = futures[fut]
                    try:
                        ordered[wid] = fut.result()
                    except Exception as exc:
                        ordered[wid] = {"status": "error", "error": str(exc), "worker": wid}
                for wid in workers:
                    if wid in ordered:
                        results.append(ordered[wid])

        # Contadores globais
        self._runs += len(results)
        for r in results:
            if r.get("status") == "completed":
                self._successes += 1
            else:
                self._failures += 1

        return results

    def report(self) -> Dict[str, Any]:
        return {
            "workers": len(self._workers),
            "runs": self._runs,
            "successes": self._successes,
            "failures": self._failures,
            "worker_ids": list(self._workers),
        }
