"""Ciclo local compartilhado pelo primário e pelo middleware Reflexion.

Registra observações e próximas ações; não transforma autoavaliação em
confiança, prova ou autorização. Nenhuma chamada LLM/rede é feita aqui.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any


def _text(value: Any, limit: int = 800) -> str:
    if not isinstance(value, str):
        try:
            value = json.dumps(value, ensure_ascii=False, allow_nan=False)
        except (TypeError, ValueError, RecursionError):
            value = f"[conteúdo não serializável: {type(value).__name__}]"
    return "".join(char if char >= " " or char == "\n" else " " for char in value)[:limit]


class MetacognitiveLoop:
    """Prepara contexto e registra resultados com a memória canônica do bus."""

    def __init__(self, bus):
        self.bus = bus

    def prepare(self, query: str, *, reasoner=None, limit: int = 5) -> dict:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("A consulta deve conter texto útil.")
        if type(limit) is not int or not 1 <= limit <= 5:
            raise ValueError("O limite de recuperação deve estar entre 1 e 5.")
        records, lessons, seen_tasks = [], [], set()
        superseded = {entry["observation"].get("supersedes")
                      for entry in self.bus.memory.episodic if isinstance(entry, dict)
                      and isinstance(entry.get("observation"), dict)}
        for item in self.bus.memory.search_memory(query[:2000], limit=limit):
            if item.get("id") is not None and item["id"] in superseded:
                continue
            observation = item.get("observation", {})
            if not isinstance(observation, dict):
                observation = {}
            task_id = observation.get("task_id")
            if task_id:
                if task_id in seen_tasks:
                    continue
                seen_tasks.add(task_id)
            summary = " | ".join(_text(observation[key], 250) for key in
                                  ("result_summary", "observed_error", "next_action", "lesson")
                                  if observation.get(key))
            if not summary:
                summary = _text(item.get("reflection") or observation or item.get("lessons", []), 700)
            records.append({"id": _text(item.get("id", item.get("topic", "")), 120),
                            "kind": item.get("kind"), "context": _text(item.get("context", ""), 200),
                            "summary": summary[:700], "outcome": _text(observation.get("outcome", "unknown"), 30),
                            "source_agent": _text(item.get("agent_id", ""), 100),
                            "timestamp": _text(item.get("timestamp", ""), 80)})
            lessons.append(summary[:500])
        analysis = {"engine": None, "available": False, "calibrated": False,
                    "limitation": "Preparação sem motor solicitado."}
        if reasoner is not None:
            try:
                raw = reasoner(query[:2000])
                analysis = {"engine": _text(raw.get("engine", ""), 60),
                            "available": raw.get("available") is True,
                            "conclusion": _text(raw.get("conclusion", ""), 1000),
                            "calibrated": False, "verification": "heuristic_preparation"}
            except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as error:
                analysis = {"engine": None, "available": False, "calibrated": False,
                            "error_type": type(error).__name__, "verification": "not_evaluated"}
        briefing = {"orchestrator": "marceloclaro", "query": query[:1000],
                    "records": records, "lessons": lessons, "analysis": analysis,
                    "memory_is_instruction": False, "calibrated": False,
                    "confidence_promoted": False, "verification": "local_memory_retrieval"}
        self.bus.publish("metacognition.prepared", {"query": query[:160],
                         "record_ids": [item["id"] for item in records],
                         "selected_engine": analysis.get("engine"), "calibrated": False},
                         source_agent="marceloclaro")
        return briefing

    def observe_reasoning(self, query: str, result: dict, briefing: dict) -> dict:
        payload = {"kind": "reasoning_observation", "engine": result.get("engine"),
                   "result_summary": _text(result.get("conclusion", ""), 1200),
                   "available": result.get("available") is True,
                   "retrieved_ids": [record["id"] for record in briefing["records"]],
                   "calibrated": False, "confidence_promoted": False,
                   "verification": "local_reasoning_observation"}
        evidence = result.get("evidence")
        if result.get("engine") == "quantum" and isinstance(evidence, dict):
            from reasoning.quantum import validate_configuration
            configuration = evidence.get("configuration")
            digest = evidence.get("report_sha256")
            if (evidence.get("execution_kind") == "classical_simulation"
                    and evidence.get("backend") == "python_statevector"
                    and evidence.get("quantum_hardware_used") is False
                    and evidence.get("query_evaluated") is False
                    and isinstance(configuration, dict) and isinstance(digest, str)
                    and len(digest) == 64 and all(char in "0123456789abcdef" for char in digest)):
                try:
                    configuration = validate_configuration(configuration.get("n_qubits"),
                        configuration.get("seeds"), configuration.get("shots"))
                except ValueError:
                    pass
                else:
                    payload["execution"] = {
                        "execution_kind": "classical_simulation", "backend": "python_statevector",
                        "quantum_hardware_used": False, "query_evaluated": False,
                        "configuration": configuration, "report_sha256": digest,
                        "verification": "local_execution_metadata_recorded", "calibrated": False}
        identifier = self.bus.memory.record_observation("marceloclaro", query[:2000], payload)
        return {"observation_id": identifier, "retrieved_records": len(briefing["records"]),
                "record_ids": payload["retrieved_ids"],
                "contextual_review": briefing["lessons"],
                "formal_input_modified_by_memory": False,
                "status": "recorded", "calibrated": False, "confidence_promoted": False}

    def complete(self, *, task_id: str, agent_id: str, context: str,
                 result: Any, success: bool, sdd_verification=None) -> dict:
        from mci.metacognitive_evaluator import (
            MetacognitiveEvaluator,
            MetacognitiveTrace,
        )

        verification = sdd_verification if isinstance(sdd_verification, dict) else {}
        sdd_status = _text(verification.get("status", "not_provided"), 100)
        sdd_verified = verification.get("verified") is True
        data = result if isinstance(result, dict) else {}
        try:
            serialized = json.dumps([task_id, agent_id, result, success, verification],
                                    ensure_ascii=False, sort_keys=True, allow_nan=False)
            completion_key = hashlib.sha256(serialized.encode()).hexdigest()
        except (TypeError, ValueError, RecursionError):
            completion_key = None
        prior = [entry for entry in self.bus.memory.episodic
                 if isinstance(entry, dict) and entry.get("agent_id") == agent_id
                 and isinstance(entry.get("observation"), dict)
                 and entry["observation"].get("kind") == "metacognitive_episode"
                 and entry["observation"].get("task_id") == task_id]
        if completion_key:
            existing = prior[-1] if prior and prior[-1]["observation"].get("completion_key") == completion_key else None
            if existing:
                return self._report(existing["id"], agent_id, existing["observation"], reused=True)
        summary = _text(data.get("output") or data.get("conclusion") or result, 1200)
        references = []
        for field in ("evidence", "references", "citations"):
            declared = data.get(field, [])
            for reference in declared if isinstance(declared, list) else [declared]:
                if reference and len(references) < 10:
                    references.append({"reference": _text(reference, 500),
                                       "verification": "declared_unverified"})
        observed_error = _text(data.get("error") or "", 400)
        if not success and not observed_error:
            observed_error = (f"Gate SDD: {sdd_status}" if verification and not sdd_verified
                              else "A execução foi reportada como falha; causa não determinada.")
        if not success and verification and not sdd_verified and sdd_status != "legacy_unverified":
            next_action = f"Corrigir o bloqueio SDD ({sdd_status}) antes de repetir a entrega."
        elif not success:
            next_action = f"Investigar o erro observado: {observed_error}. Testar a correção antes de repetir."
        else:
            next_action = "Conferir o resultado contra os critérios da próxima tarefa; não inferir validade geral deste sucesso local."
        before = self.bus.memory.confidence_ledger.get(agent_id, 0.5)
        if type(before) not in (int, float) or not math.isfinite(before):
            before = 0.5
        reflection = f"Resultado observado: {summary}. Falha observada: {observed_error or 'não informada'}. Próxima ação: {next_action}"
        trace = MetacognitiveTrace(action_id=task_id, context=context[:2000],
                                   outcome="success" if success else "failure", reflection=reflection,
                                   confidence_before=before, confidence_after=before,
                                   strategy="contextual_followup", error_type=observed_error or None,
                                   evidence_count=0)
        heuristic = MetacognitiveEvaluator().evaluate([trace], external_validation=False)
        evaluation = {"kind": "heuristic", "dimensions": heuristic["dimensions"],
                      "recommendations": heuristic["recommendations"], "traces_total": 1,
                      "external_validation": False, "calibrated": False}
        episode = {"schema_version": "r886.v1", "kind": "metacognitive_episode",
                   "task_id": _text(task_id, 160), "outcome": trace.outcome,
                   "completion_key": completion_key,
                   "supersedes": prior[-1]["id"] if prior else None,
                   "result_summary": summary, "summary_sha256": hashlib.sha256(summary.encode()).hexdigest(),
                   "declared_references": references,
                   "observed_error": observed_error, "next_action": next_action,
                   "sdd_status": sdd_status, "sdd_verified": sdd_verified,
                   "evaluation": evaluation, "verification": "local_observation",
                   "calibrated": False, "confidence_promoted": False,
                   "limitations": ["Referências e conclusões do executor não são validadas por esta reflexão.",
                                   "Causa raiz não é inferida de um erro ou escore heurístico.",
                                   "A avaliação não comprova correção, calibração ou qualidade externa."]}
        identifier = self.bus.memory.record_observation(agent_id, context[:2000], episode)
        return self._report(identifier, agent_id, episode)

    def _report(self, identifier: str, agent_id: str, episode: dict, *, reused=False) -> dict:
        return {"task_id": episode["task_id"], "agent_id": agent_id, "reflection_id": identifier,
                "status": "recorded", "reused": reused, "outcome": episode["outcome"], "score": None,
                "new_confidence": self.bus.memory.confidence_ledger.get(agent_id, 0.5),
                "calibrated": False, "confidence_promoted": False, "evaluation": episode["evaluation"]}
