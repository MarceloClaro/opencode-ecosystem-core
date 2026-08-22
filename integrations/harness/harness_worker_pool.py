# -*- coding: utf-8 -*-
"""
HarnessWorkerPool — pool dedicado do Harness Universal (G4 — R438)

Nativo com prefixo harness-worker-N e capabilities harness_execution,
sem depender de DeepSeekWorkerPool (desacoplamento).
"""

from __future__ import annotations

import concurrent.futures
from typing import Any, Callable, Dict, List, Optional


class HarnessWorkerPool:
    """Pool escalável nativo do Harness Universal no Blackboard."""

    WORKER_CAPABILITIES = [
        "harness_execution",
        "universal_model_routing",
        "autonomous_production",
    ]
    PREFIX = "harness-worker-"

    def __init__(
        self,
        metabus: Any | None = None,
        adapter: Any | None = None,
    ):
        if metabus is not None:
            self.metabus = metabus
        else:
            from mci.metabus import metabus as _global_metabus

            self.metabus = _global_metabus

        if adapter is not None:
            self.adapter = adapter
        else:
            from integrations.harness.universal_adapter import UniversalHarnessAdapter

            self.adapter = UniversalHarnessAdapter()

        self._workers: List[str] = []
        self._runs: int = 0
        self._successes: int = 0
        self._failures: int = 0
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

    def scale(self, n: int) -> List[str]:
        n = max(0, int(n))
        current = len(self._workers)
        if n == current:
            return list(self._workers)
        if n < current:
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
        for i in range(current, n):
            worker_id = f"{self.PREFIX}{i}"
            if worker_id in self._workers:
                continue
            try:
                self.metabus.publish(
                    "agent.register",
                    {
                        "agent_id": worker_id,
                        "name": f"Harness Worker {i}",
                        "description": "Worker nativo do Harness Universal (qualquer modelo OpenCode, SPEC-935-R438).",
                        "capabilities": list(self.WORKER_CAPABILITIES),
                        "schema": {},
                    },
                    source_agent="harness-pool",
                )
            except Exception:
                try:
                    from mci.blackboard import AgentCard, blackboard

                    card = AgentCard(
                        agent_id=worker_id,
                        name=f"Harness Worker {i}",
                        description="Worker harness universal nativo.",
                        capabilities=list(self.WORKER_CAPABILITIES),
                        schema={},
                    )
                    blackboard.registry[worker_id] = card
                except Exception:
                    continue
            self._workers.append(worker_id)
        return list(self._workers)

    def list_workers(self) -> List[Dict[str, Any]]:
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
        task_type: str = "coding",
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        workers = list(self._workers)
        if not workers:
            return []

        def _run_for_worker(worker_id: str) -> Dict[str, Any]:
            # Adapter universal aceita task_type/provider/model/runner
            try:
                res = self.adapter.run_task(objective, task_type=task_type, provider=provider, model=model, runner=runner)
            except TypeError:
                # Fallback para adapter legado
                res = self.adapter.run_task(objective, runner=runner)
            out: Dict[str, Any] = dict(res) if isinstance(res, dict) else {"status": "completed", "final_response": str(res)}
            out["worker"] = worker_id
            out["objective"] = objective
            if self._trust is not None:
                try:
                    self._trust.learn(f"delegate:{worker_id}", success=(out.get("status") == "completed"))
                except Exception:
                    pass
            if self._economy is not None:
                try:
                    task_id = f"harness-{worker_id}-{self._runs + hash(objective) % 10000:05d}"
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
