# -*- coding: utf-8 -*-
"""
Bridge — fachada DeepSeekHarnessBridge (SPEC-935-R433).

Orquestra inventory + adapter + metacognição + pool sob gate SDD.
Singleton: deepseek_harness_bridge
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional

from integrations.deepseek_harness.inventory import DeepSeekHarnessInventory
from integrations.deepseek_harness.adapter import DeepSeekHarnessAdapter
from integrations.deepseek_harness.metacognition import DSHMetacognitionIngestor
from integrations.deepseek_harness.worker_pool import DeepSeekWorkerPool

DEFAULT_DSH_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "deepseek-harness",
)


class DeepSeekHarnessBridge:
    """Fachada integrada do dsh no ecossistema Core."""

    def __init__(self, dsh_root: str | None = None, metabus: Any | None = None):
        self.dsh_root = os.path.abspath(dsh_root or DEFAULT_DSH_ROOT)
        self.monorepo = os.path.join(self.dsh_root, "DEEPSEEK-HARNESS")

        if metabus is not None:
            self.metabus = metabus
        else:
            from mci.metabus import metabus as _global_metabus

            self.metabus = _global_metabus

        self.inventory = DeepSeekHarnessInventory(dsh_root=self.dsh_root)
        self.adapter = DeepSeekHarnessAdapter(dsh_root=self.dsh_root)
        self.ingestor = DSHMetacognitionIngestor(dsh_root=self.dsh_root, metabus=self.metabus)
        self.pool = DeepSeekWorkerPool(metabus=self.metabus, adapter=self.adapter, dsh_root=self.dsh_root)

    # ------------------------------------------------------------------
    def status(self) -> Dict[str, Any]:
        """Estado auditável da ponte (inventário + canal + pool)."""
        try:
            inv = self.inventory.discover()
        except Exception as exc:
            inv = {"available": os.path.isdir(self.monorepo), "error": str(exc)}

        try:
            adapter_status = self.adapter.status()
        except Exception as exc:
            adapter_status = {"channel": "unknown", "error": str(exc)}

        try:
            pool_report = self.pool.report()
        except Exception as exc:
            pool_report = {"error": str(exc)}

        return {
            "inventory": inv,
            "adapter": adapter_status,
            "pool": pool_report,
            "dsh_root": self.dsh_root,
            "monorepo": self.monorepo,
        }

    def delegate(
        self,
        objective: str,
        runner: Optional[Callable[..., Dict[str, Any]]] = None,
        workers: int = 1,
    ) -> List[Dict[str, Any]]:
        """Garante workers e delega o objetivo (fan-out).

        Retorna a lista de resultados por worker.
        """
        if self.pool.report()["workers"] < workers:
            self.pool.scale(workers)
        return self.pool.submit(objective, runner=runner)

    def orchestrate(
        self,
        objective: str,
        runner: Optional[Callable[..., Dict[str, Any]]] = None,
        workers: int = 1,
    ) -> Dict[str, Any]:
        """Ciclo orquestrado completo: SDD spec → execução → ingestão → verificação.

        Cria uma spec dinâmica (TSPEC) com gate SDD, executa via pool,
        ingere metacognição quando houver eventos e verifica a entrega.
        """
        from sdd.spec_engine import spec_registry, spec_verifier

        # Gate SDD — spec dinâmica criada ANTES da execução (RED)
        title = f"dsh: {objective[:80]}"
        spec = spec_registry.create_task_spec(
            title=title,
            objective=objective,
            criteria_descriptions=[
                "Ao menos uma produção do dsh deve completar com status completed.",
            ],
        )
        # Critério executável (TDD): ao menos um resultado succeeded
        spec.add_criterion(
            "Verificação de conclusão do harness",
            lambda out: isinstance(out, dict)
            and any(
                isinstance(r, dict) and r.get("status") == "completed"
                for r in (out.get("results") if isinstance(out.get("results"), list) else [])
            ),
        )

        # Execução escalada
        if self.pool.report()["workers"] < workers:
            self.pool.scale(workers)

        results = self.pool.submit(objective, runner=runner)

        # Ingestão metacognitiva quando houver eventos nos resultados
        ingested: List[Dict[str, Any]] = []
        for res in results:
            events = res.get("events") if isinstance(res, dict) else None
            if isinstance(events, list) and events:
                try:
                    summary = self.ingestor.ingest_session_events(
                        events, task_id=res.get("worker", "dsh-pool")
                    )
                    ingested.append(summary)
                except Exception:
                    continue

        # Verifica a entrega contra a spec (GREEN)
        payload: Dict[str, Any] = {
            "objective": objective,
            "results": results,
            "ingested": ingested,
        }
        verification = spec_verifier.verify(spec.spec_id, payload)

        # Publica evento de subsistema — auditável no MetaBus
        try:
            self.metabus.publish_subsystem_event(
                "deepseek_harness",
                "orchestrate.completed",
                {
                    "spec_id": spec.spec_id,
                    "objective": objective,
                    "workers": workers,
                    "results_count": len(results),
                    "verification": verification,
                },
                source_agent="deepseek-harness-bridge",
            )
        except Exception:
            pass

        # Reflexão final no Global Workspace
        try:
            ok = bool(verification.get("verified"))
            self.metabus.memory.add_reflection(
                agent_id="deepseek-harness-bridge",
                task_context=f"orquestração dsh: {objective[:100]}",
                reflection=(
                    f"Orquestração dsh concluída: {len(results)} produção(ões) "
                    f"por {workers} worker(s); gate SDD {spec.spec_id} "
                    f"{'aprovado' if ok else 'reprovado'} "
                    f"({verification.get('passed_count', 0)}/{verification.get('total_count', 0)} critérios)."
                ),
                score=1.0 if ok else 0.4,
            )
        except Exception:
            pass

        return {
            "spec_id": spec.spec_id,
            "verification": verification,
            "results": results,
            "ingested": ingested,
            "workers": workers,
        }


# Singleton lazy — não executa I/O na importação
deepseek_harness_bridge = DeepSeekHarnessBridge()
