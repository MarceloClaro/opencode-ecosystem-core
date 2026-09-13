# -*- coding: utf-8 -*-
"""ResearchFactory — meta-graph de fábrica de pesquisa (SPEC-935-R471, M1).

Cinco entrypoints no espírito do open-swe (langchain-ai/open-swe):
research (Agent), review (Reviewer), analyze (Analyzer), chat (Chat)
e schedule (Scheduler). Todos registram invocação na thread e entradas
de auditoria. Os componentes externos (investigação, composição e
revisão) são injetáveis, permitindo testes herméticos e reuso do
pipeline nativo do Core (research/, agentic_science_v2/).
"""
from __future__ import annotations

import json
from typing import Any, Callable, Dict, Optional

from research_factory.analyzer import ReviewStyleAnalyzer
from research_factory.audit import AuditLog
from research_factory.autonomy import AutonomyCore
from research_factory.reasoning import PlanConsistencyChecker
from research_factory.scheduler import ResearchScheduler
from research_factory.search import OpenScienceSearchOrchestrator
from research_factory.threads import ThreadStore


class ResearchFactory:
    """Fachada do meta-graph; cada entrypoint atua sobre uma thread."""

    def __init__(
        self,
        thread_store: ThreadStore,
        researcher: Callable[[str, Optional[str]], Dict[str, Any]],
        composer: Callable[[Dict[str, Any]], str],
        reviewer: Callable[[str], Dict[str, Any]],
        audit: Optional[AuditLog] = None,
        scheduler: Optional[ResearchScheduler] = None,
        analyzer: Optional[ReviewStyleAnalyzer] = None,
    ):
        self.thread_store = thread_store
        self.researcher = researcher      # f(topic, question) -> report dict
        self.composer = composer          # f(report) -> manuscript str
        self.reviewer = reviewer          # f(manuscript) -> {decision, ...}
        self.audit = audit or AuditLog(
            root=thread_store.root.parent / "audit"
        )
        self.scheduler = scheduler or ResearchScheduler(
            root=thread_store.root.parent / "scheduler"
        )
        self.analyzer = analyzer or ReviewStyleAnalyzer(
            root=thread_store.root.parent / "analyzer"
        )
        # Extensões R476 (autonomia, raciocínio e pesquisa open science):
        # injetáveis; defaults com memória/factory nulos => comportamento
        # determinístico e sem rede (self_supervise sem lições; busca sem
        # searcher registrado retorna recibo vazio).
        self.autonomy = AutonomyCore()
        self.reasoning = PlanConsistencyChecker()
        self.search = OpenScienceSearchOrchestrator()

    # ---- research (Agent) ----

    def research(self, thread_id: str,
                 question: Optional[str] = None) -> Dict[str, Any]:
        """Investiga o tópico da thread e compõe o manuscrito."""
        thread = self.thread_store.load(thread_id)
        report = self.researcher(topic=thread.topic, question=question)
        self.audit.record(
            "investigate", "research", thread_id,
            artifact=json.dumps(report, ensure_ascii=False).encode("utf-8"),
        )
        manuscript = self.composer(report)
        self.audit.record(
            "compose", "research", thread_id,
            artifact=manuscript.encode("utf-8"),
        )
        thread.add_invocation("research", "ok", {"question": question})
        self.thread_store.save(thread)
        return {
            "thread_id": thread_id,
            "manuscript": manuscript,
            "report": report,
            "question": question,
        }

    # ---- review (Reviewer) ----

    def review(self, thread_id: str, manuscript: str) -> Dict[str, Any]:
        """Revisão grounded: consome o manuscrito e devolve decisão."""
        thread = self.thread_store.load(thread_id)
        result = self.reviewer(manuscript)
        self.audit.record(
            "review", "review", thread_id,
            artifact=manuscript.encode("utf-8"),
            decision=result.get("decision"),
        )
        thread.add_invocation(
            "review", "ok", {"decision": result.get("decision")}
        )
        self.thread_store.save(thread)
        return {"thread_id": thread_id, **result}

    # ---- analyze (Analyzer) ----

    def analyze(self, thread_id: str, feedback: Dict[str, Any],
                accepted: Optional[str] = None,
                manuscript: Optional[str] = None) -> Dict[str, Any]:
        """Aprende regras de revisão a partir de feedback histórico."""
        thread = self.thread_store.load(thread_id)
        if manuscript is None:
            artifact = self.audit.last_artifact(thread_id, "compose")
            manuscript = artifact.decode("utf-8") if artifact else ""
        self.analyzer.add_example(
            manuscript=manuscript, feedback=feedback, accepted=accepted
        )
        self.audit.record(
            "analyze", "analyze", thread_id,
            artifact=json.dumps(feedback, ensure_ascii=False).encode("utf-8"),
        )
        thread.add_invocation("analyze", "ok", {})
        self.thread_store.save(thread)
        return {"thread_id": thread_id, "rules": self.analyzer.rules()}

    # ---- chat (Chat, read-only) ----

    def chat(self, thread_id: str, question: str) -> Dict[str, Any]:
        """Responde a perguntas sobre o estado da thread, sem alterar artefatos."""
        thread = self.thread_store.load(thread_id)
        invocations = thread.invocations
        last = invocations[-1]["entrypoint"] if invocations else "nenhuma"
        answer = (
            f"Estado atual da thread '{thread.topic}': "
            f"{len(invocations)} invocação(ões); "
            f"última etapa: {last}. Pergunta registrada: {question}"
        )
        self.audit.record(
            "chat", "chat", thread_id,
            artifact=json.dumps({"answer": answer},
                                ensure_ascii=False).encode("utf-8"),
        )
        thread.add_invocation("chat", "ok", {"question": question})
        self.thread_store.save(thread)
        return {
            "thread_id": thread_id,
            "answer": answer,
            "state": {"invocations": len(invocations), "last": last},
        }

    # ---- schedule (Scheduler) ----

    def schedule(self, thread_id: str, name: str, interval_seconds: float,
                 fn: Callable[[], Any],
                 extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Agenda uma tarefa recorrente vinculada à thread."""
        thread = self.thread_store.load(thread_id)
        job = self.scheduler.add(
            name=name, fn=fn, interval_seconds=interval_seconds, extra=extra
        )
        self.audit.record(
            "schedule", "schedule", thread_id,
            artifact=json.dumps(
                {"name": name, "interval_seconds": interval_seconds},
                ensure_ascii=False,
            ).encode("utf-8"),
        )
        thread.add_invocation(
            "schedule", "ok",
            {"name": name, "interval_seconds": interval_seconds},
        )
        self.thread_store.save(thread)
        return {"thread_id": thread_id, "job": job["id"], "name": name}

    # ---- util ----

    def run_due_scheduled(self, now: float) -> int:
        """Executa tarefas agendadas vencidas (delega ao scheduler)."""
        return self.scheduler.run_due(now=now)

    # ---- autonomia (R476) ----

    def self_supervise(self, executed_actions, topic=None):
        """Reflexão pós-execução: lições do MetaBus -> plano de ação."""
        return self.autonomy.self_supervise(executed_actions, topic=topic)