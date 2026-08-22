# -*- coding: utf-8 -*-
"""
Universal Bridge — harness agnóstico com gate SDD (SPEC-935-R435)
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from integrations.harness.model_registry import HarnessModelRegistry
from integrations.harness.universal_adapter import UniversalHarnessAdapter


class UniversalHarnessBridge:
    """Fachada universal — qualquer modelo do OpenCode pode orquestrar."""

    def __init__(self, router: Any | None = None, metabus: Any | None = None):
        if metabus is not None:
            self.metabus = metabus
        else:
            from mci.metabus import metabus as _mb

            self.metabus = _mb

        self.registry = HarnessModelRegistry(router=router)
        # Reusa o router do registry para o adapter
        self.adapter = UniversalHarnessAdapter(router=self.registry.router, registry=self.registry)

        # Pool universal — reutiliza DeepSeekWorkerPool mas com workers universal_*
        # Para evitar acoplamento, cria pool próprio com metabus e adapter universal
        try:
            from integrations.deepseek_harness.worker_pool import DeepSeekWorkerPool

            # Pool será adaptado: usaremos nosso adapter universal mas mantemos lógica de escala
            self.pool = DeepSeekWorkerPool(metabus=self.metabus, adapter=self.adapter)
            # Sobrescreve capabilities do pool para universal
            self.pool.WORKER_CAPABILITIES = [
                "harness_execution",
                "universal_model_routing",
                "autonomous_production",
            ]
            # Renomeia prefixo de workers para universal
            self._worker_prefix = "harness-worker-"
        except Exception:
            self.pool = None
            self._worker_prefix = "harness-worker-"

        # Pool universal simplificado quando DeepSeek pool indisponível
        self._workers: List[str] = []
        self._use_simple_pool = self.pool is None

    # ------------------------------------------------------------------
    def status(self) -> Dict[str, Any]:
        try:
            reg = self.registry.discover()
        except Exception as exc:
            reg = {"error": str(exc), "total_models": 0}
        try:
            ad = self.adapter.status()
        except Exception as exc:
            ad = {"error": str(exc)}
        # Pool status
        try:
            if self.pool is not None:
                pool_status = self.pool.report()
                # Normaliza key 'workers' para ser contagem
                pool_status = dict(pool_status)
                # Mantém compatibilidade com teste que espera pool.workers
            else:
                pool_status = {"workers": len(self._workers), "runs": 0}
        except Exception as exc:
            pool_status = {"error": str(exc)}
        return {
            "registry": reg,
            "adapter": ad,
            "pool": pool_status,
            "harness": "universal",
        }

    # ------------------------------------------------------------------
    def _ensure_workers(self, n: int) -> None:
        if self.pool is not None:
            # Delega para pool existente mas garante workers universais
            # Pool original usa dsh-worker-*; vamos escalar e depois renomear se necessário
            current = len(self.pool.list_workers())
            if current != n:
                self.pool.scale(n)
                # Se pool usou dsh-worker-*, mantém — compatibilidade
            return
        # Simple pool interno
        n = max(0, int(n))
        if len(self._workers) == n:
            return
        if len(self._workers) < n:
            for i in range(len(self._workers), n):
                wid = f"{self._worker_prefix}{i}"
                try:
                    self.metabus.publish(
                        "agent.register",
                        {
                            "agent_id": wid,
                            "name": f"Harness Worker {i}",
                            "description": "Worker universal do Harness OpenCode (qualquer modelo).",
                            "capabilities": ["harness_execution", "universal_model_routing", "autonomous_production"],
                            "schema": {},
                        },
                        source_agent="harness-bridge",
                    )
                except Exception:
                    pass
                self._workers.append(wid)
        else:
            # Scale down
            to_remove = self._workers[n:]
            for wid in to_remove:
                try:
                    from mci.blackboard import blackboard

                    if wid in blackboard.registry:
                        del blackboard.registry[wid]
                except Exception:
                    pass
            self._workers = self._workers[:n]

    def _pool_submit(
        self,
        objective: str,
        task_type: str = "coding",
        provider: str | None = None,
        model: str | None = None,
        runner: Optional[Callable[..., Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        if self.pool is not None:
            # Wrap runner para propagar provider/model
            def _wrapped(prompt, **kw):
                # Runner pode ser simples; tenta chamar com provider/model
                if runner is None:
                    return self.adapter.run_task(prompt, task_type=task_type, provider=provider, model=model)
                try:
                    return runner(prompt, provider=provider, model=model, task_type=task_type)
                except TypeError:
                    try:
                        return runner(prompt)
                    except Exception as exc:
                        return {"status": "error", "error": str(exc)}

            # Se pool já tem workers, usa submit; senão garante
            workers = self.pool.report().get("workers", 0) if hasattr(self.pool, "report") else len(self._workers)
            if workers == 0:
                self.pool.scale(1)
            return self.pool.submit(objective, runner=_wrapped)
        # Simple pool: executa 1x via adapter
        result = self.adapter.run_task(objective, task_type=task_type, provider=provider, model=model, runner=runner)
        result = dict(result)
        result.setdefault("worker", f"{self._worker_prefix}0")
        return [result]

    # ------------------------------------------------------------------
    def orchestrate(
        self,
        objective: str,
        task_type: str = "coding",
        provider: str | None = None,
        model: str | None = None,
        runner: Optional[Callable[..., Dict[str, Any]]] = None,
        workers: int = 1,
    ) -> Dict[str, Any]:
        """Orquestra com gate SDD (TSPEC) usando qualquer modelo."""
        from sdd.spec_engine import spec_registry, spec_verifier

        title = f"harness:{task_type}:{objective[:60]}"
        spec = spec_registry.create_task_spec(
            title=title,
            objective=objective,
            criteria_descriptions=[
                "Ao menos uma produção do harness universal deve completar com status completed.",
            ],
        )
        spec.add_criterion(
            "Verificação de conclusão universal",
            lambda out: isinstance(out, dict)
            and any(
                isinstance(r, dict) and r.get("status") == "completed"
                for r in (out.get("results") if isinstance(out.get("results"), list) else [])
            ),
        )

        # Garante workers
        if self.pool is not None:
            if self.pool.report().get("workers", 0) < workers:
                self.pool.scale(workers)
        else:
            self._ensure_workers(workers)

        results = self._pool_submit(objective, task_type=task_type, provider=provider, model=model, runner=runner)

        # Ingestão metacognitiva quando houver eventos (compatível com deepseek harness)
        ingested: List[Dict[str, Any]] = []
        for res in results:
            events = res.get("events") if isinstance(res, dict) else None
            if isinstance(events, list) and events:
                try:
                    from integrations.deepseek_harness.metacognition import DSHMetacognitionIngestor

                    ingestor = DSHMetacognitionIngestor(metabus=self.metabus)
                    summary = ingestor.ingest_session_events(events, task_id=res.get("worker", "harness"))
                    ingested.append(summary)
                except Exception:
                    continue

        payload: Dict[str, Any] = {"objective": objective, "task_type": task_type, "provider": provider, "model": model, "results": results, "ingested": ingested}
        verification = spec_verifier.verify(spec.spec_id, payload)

        try:
            self.metabus.publish_subsystem_event(
                "harness",
                "orchestrate.completed",
                {"spec_id": spec.spec_id, "objective": objective, "task_type": task_type, "provider": provider, "model": model, "workers": workers, "verification": verification},
                source_agent="harness-bridge",
            )
        except Exception:
            pass

        try:
            ok = bool(verification.get("verified"))
            self.metabus.memory.add_reflection(
                agent_id="harness-bridge",
                task_context=f"harness universal {task_type}: {objective[:80]}",
                reflection=(
                    f"Harness universal ({task_type} via {provider or 'auto'}/{model or 'auto'}): "
                    f"{len(results)} produção(ões) por {workers} worker(s); gate {spec.spec_id} "
                    f"{'aprovado' if ok else 'reprovado'} ({verification.get('passed_count',0)}/{verification.get('total_count',0)})."
                ),
                score=1.0 if ok else 0.4,
            )
        except Exception:
            pass

        return {"spec_id": spec.spec_id, "verification": verification, "results": results, "ingested": ingested, "workers": workers, "task_type": task_type, "provider": provider, "model": model}


# Singleton
harness_bridge = UniversalHarnessBridge()
