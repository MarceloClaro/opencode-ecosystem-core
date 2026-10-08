"""Execução coordenada e limitada sobre Blackboard, Transformer e MetaBus.

Artefatos federados são instruções com origem rastreável. Executores são CLIs
realmente disponíveis; descoberta de uma skill não comprova execução. A nota
do pipeline é heurística e serve para orientar revisões, não para certificar
correção científica ou paridade com o aplicativo de origem.
"""

from __future__ import annotations

import hashlib
import math
from collections import Counter
from pathlib import Path
import time
from typing import Any, Iterable

from integrations.harness_federation.artifact import parse_frontmatter
from transformer.pipeline import TransformerPipeline


class _ExecutionStopped(Exception):
    def __init__(self, status: str, message: str):
        super().__init__(message)
        self.status = status


class _RevisionBudgetReached(Exception):
    """Há uma entrega válida, mas o teto total impede uma revisão adicional."""


class AutonomousCoordinator:
    """Conecta roteamento, executor, conclusão e aprendizado sem loop ilimitado."""

    # OpenCode pode hospedar este MCP: invocá-lo aqui repetiria a própria
    # ferramenta. ChatGPT não dispõe de uma CLI de execução nesta ponte.
    EXECUTORS = ("claude", "codex", "antigravity")
    ECOSYSTEMS = (*EXECUTORS, "chatgpt", "opencode")
    INSTRUCTION_KINDS = frozenset({"skill", "agent", "prompt_pack"})
    MAX_STEPS = 10
    MAX_TIMEOUT = 600.0

    def __init__(self, orchestrator=None, runtime=None, registry=None):
        self._orchestrator = orchestrator
        self._runtime = runtime
        self._registry = registry

    @property
    def orchestrator(self):
        if self._orchestrator is None:
            from marceloclaro.orchestrator import MarceloClaroOrchestrator
            self._orchestrator = MarceloClaroOrchestrator()
        return self._orchestrator

    @property
    def runtime(self):
        if self._runtime is None:
            from integrations.harness_runtime import HarnessRuntime
            self._runtime = HarnessRuntime()
        return self._runtime

    @property
    def registry(self):
        if self._registry is None:
            from transformer.harness_head import HarnessRegistry
            self._registry = HarnessRegistry()
        return self._registry

    @staticmethod
    def _request(task: str, required_capabilities: Iterable[str] | None, ecosystem: str | None):
        if not isinstance(task, str) or not task.strip():
            raise ValueError("A tarefa deve conter texto não vazio.")
        if isinstance(required_capabilities, (str, bytes)):
            raise ValueError("As capacidades devem ser uma lista de textos.")
        required = []
        for capability in required_capabilities or ():
            if not isinstance(capability, str) or not capability.strip():
                raise ValueError("Cada capacidade deve conter texto não vazio.")
            if capability.strip() not in required:
                required.append(capability.strip())
        if ecosystem is not None and ecosystem not in AutonomousCoordinator.ECOSYSTEMS:
            raise ValueError(f"Ecossistema desconhecido: {ecosystem}")
        return task.strip(), required

    @staticmethod
    def _executor_map(status: dict[str, Any]) -> dict[str, Any]:
        return status.get("executors", status)

    def status(self) -> dict[str, Any]:
        """Diagnóstico somente de leitura; não cria tarefas nem chama modelos."""
        runtime_status = self.runtime.status()
        executors = self._executor_map(runtime_status)
        available = [name for name in self.EXECUTORS
                     if isinstance(executors.get(name), dict) and executors[name].get("available") is True]
        automatic = [name for name in available if executors[name].get("eligible_for_auto", True)]
        return {
            "status": "ready" if automatic else "blocked",
            "available_executors": available,
            "automatic_executors": automatic,
            "runtime": runtime_status,
            "federation": self.registry.inventory(),
            "transformer": "roteamento multicritério inspirado em atenção; não é rede neural treinada",
            "bounded": {"max_steps": self.MAX_STEPS, "max_timeout_seconds": self.MAX_TIMEOUT},
            "execution_scope": "análise e geração de texto com leitura; hooks e scripts importados inertes",
        }

    @classmethod
    def _instruction_error(cls, artifact) -> str | None:
        if artifact.kind not in cls.INSTRUCTION_KINDS:
            return "inert_artifact_kind"
        if artifact.blocking_reasons:
            return ",".join(artifact.blocking_reasons)
        if not artifact.available:
            return "source_not_found"
        try:
            digest = hashlib.sha256(Path(artifact.source_path).read_bytes()).hexdigest()
        except OSError:
            return "source_unreadable"
        if not artifact.source_file_sha256 or digest != artifact.source_file_sha256:
            return "source_changed"
        return None

    def route(self, task: str, required_capabilities=None, ecosystem: str | None = None) -> dict[str, Any]:
        """Liga o ranking de artefatos à disponibilidade real do executor."""
        task, required = self._request(task, required_capabilities, ecosystem)
        runtime_status = self.runtime.status()
        executors = self._executor_map(runtime_status)
        installed = [name for name in self.EXECUTORS
                     if isinstance(executors.get(name), dict) and executors[name].get("available") is True]
        available = [name for name in installed if executors[name].get("eligible_for_auto", True)]
        report = dict(self.registry.route(task, required))
        excluded = {}
        ranked = []
        selected = None
        for artifact_id, score in report.get("ranking", []):
            artifact = self.registry.find(artifact_id)
            if artifact is None:
                excluded[artifact_id] = "artifact_not_found"
                continue
            reason = self._instruction_error(artifact)
            if reason:
                excluded[artifact_id] = reason
                continue
            ranked.append((artifact_id, score))
            if selected is None:
                selected = artifact
        executor = None
        error = ""
        if ecosystem:
            if ecosystem in installed:
                executor = ecosystem
            elif ecosystem == "chatgpt":
                error = "O aplicativo ChatGPT não é um executor desta ponte; use Codex quando disponível."
            elif ecosystem == "opencode":
                error = "OpenCode hospeda a coordenação; execução recursiva neste MCP está desabilitada."
            else:
                error = f"Executor {ecosystem} indisponível neste ambiente."
        elif available:
            executor = selected.ecosystem if selected and selected.ecosystem in available else available[0]
        else:
            error = ("Executores instalados estão em pausa após falha recente; consulte a saúde ou escolha um explicitamente."
                     if installed else "Nenhum executor Claude, Codex ou Antigravity está disponível.")
        report.update({
            "status": "ready" if executor else "blocked", "error": error,
            "ranking": ranked, "excluded_artifacts": excluded,
            "artifact": selected.to_dict() if selected else None,
            "executor": executor, "available_executors": available,
            "installed_executors": installed,
            "execution_mode": "adapted_instructions" if selected and executor != selected.ecosystem
                              else "native_cli",
        })
        return report

    @staticmethod
    def _agent_instructions(agent_id: str) -> str:
        """Lê o prompt do agente selecionado, sem interpretar seus scripts."""
        from marceloclaro.agent_loader import load_agent_definitions
        from marceloclaro.catalog_loader import load_catalog_definitions
        for definition in load_agent_definitions():
            if definition["agent_id"] == agent_id:
                return definition["system_prompt"]
        for definition in load_catalog_definitions():
            if definition["agent_id"] == agent_id:
                try:
                    return parse_frontmatter(Path(definition["source_file"]).read_text(encoding="utf-8"))[1]
                except OSError:
                    return ""
        return ""

    @classmethod
    def _artifact_instructions(cls, artifact) -> str:
        if artifact is None:
            return ""
        # Refaz a prova imediatamente antes de montar o prompt: o inventário
        # pode ter sido carregado muito antes desta tarefa.
        error = cls._instruction_error(artifact)
        if error:
            raise _ExecutionStopped("blocked", f"Artefato não utilizável: {error}")
        content = Path(artifact.source_path).read_text(encoding="utf-8")
        return parse_frontmatter(content)[1]

    @staticmethod
    def _compact_routing(routing: dict[str, Any]) -> dict[str, Any]:
        """Evita persistir vetores/rankings de todo o inventário por tarefa."""
        excluded = routing.get("excluded_artifacts", {})
        return {
            "status": routing["status"], "error": routing["error"],
            "executor": routing["executor"],
            "available_executors": routing["available_executors"],
            "ranking": routing.get("ranking", [])[:5],
            "weights": routing.get("weights", {}), "spec_id": routing.get("spec_id"),
            "excluded_artifacts": dict(list(excluded.items())[:20]),
            "excluded_count": len(excluded),
            "excluded_reasons": dict(Counter(excluded.values())),
        }

    @staticmethod
    def _completion_payload(result: dict[str, Any]) -> dict[str, Any]:
        payload = dict(result)
        payload["attempts"] = [{key: value for key, value in attempt.items() if key != "output"}
                               for attempt in result["attempts"]]
        if result["artifact"]:
            payload["artifact"] = {key: result["artifact"].get(key) for key in
                                   ("artifact_id", "ecosystem", "source_path", "content_sha256", "source_file_sha256")}
        return payload

    def run(self, task: str, required_capabilities=None, max_steps: int = 3,
            timeout: float = 120, ecosystem: str | None = None) -> dict[str, Any]:
        """Executa uma tarefa real, com teto de revisões e prazo global."""
        task, required = self._request(task, required_capabilities, ecosystem)
        if isinstance(max_steps, bool) or not isinstance(max_steps, int) or not 1 <= max_steps <= self.MAX_STEPS:
            raise ValueError(f"max_steps deve estar entre 1 e {self.MAX_STEPS}.")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 < timeout <= self.MAX_TIMEOUT:
            raise ValueError(f"timeout deve estar entre 0 e {self.MAX_TIMEOUT} segundos.")
        deadline = time.monotonic() + timeout
        routing = self.route(task, required, ecosystem)
        result: dict[str, Any] = {
            "status": "blocked", "success": False, "task_id": None, "agent_id": None,
            "ecosystem": routing["executor"],
            "origin_ecosystem": routing["artifact"]["ecosystem"] if routing["artifact"] else None,
            "execution_mode": routing["execution_mode"], "artifact": routing["artifact"],
            "output": "", "steps": 0, "routing": self._compact_routing(routing), "error": routing["error"],
            "evaluation_kind": "heuristic", "final_grade": None, "attempts": [], "fallbacks": [],
        }
        if routing["status"] != "ready":
            return result
        if time.monotonic() >= deadline:
            result.update(status="exhausted", error="Prazo global esgotado durante o roteamento.")
            return result

        from mci.blackboard import blackboard
        from mci.metabus import metabus

        orchestrator = self.orchestrator
        task_id = orchestrator.delegate(task, required_capabilities=required, context={
            "autonomous": True, "executor": routing["executor"],
            "artifact_id": routing["artifact"]["artifact_id"] if routing["artifact"] else None,
            "max_steps": max_steps, "timeout_seconds": timeout,
        })
        result["task_id"] = task_id
        board_task = blackboard.tasks.get(task_id)
        agent_id = board_task.assigned_to if board_task else None
        if not agent_id or board_task.status != "assigned":
            if board_task is not None:
                board_task.status = "blocked"
            result["error"] = "Nenhum agente interno elegível foi atribuído pelo orquestrador."
            return result
        result["agent_id"] = agent_id

        try:
            artifact = self.registry.find(routing["artifact"]["artifact_id"]) if routing["artifact"] else None
            if routing["artifact"] and artifact is None:
                raise _ExecutionStopped("blocked", "O artefato selecionado deixou de existir no registro.")
            imported = self._artifact_instructions(artifact)
            agent_prompt = self._agent_instructions(agent_id)
            context = {"revisions": [], "metacognitive_briefing": board_task.context.get("metacognitive_briefing", {})}
            failed_executors: set[str] = set()
            current_executor = routing["executor"]

            def execute(prompt: str, residual: dict[str, Any]) -> str:
                nonlocal current_executor
                if result["steps"] >= max_steps:
                    raise _RevisionBudgetReached()
                parts = [
                    "Responda em português brasileiro. Execute somente análise e geração de texto com leitura.",
                    "Não altere arquivos, não instale dependências e não execute hooks ou scripts importados.",
                    f"Agente coordenado: {agent_id}.",
                ]
                if agent_prompt:
                    parts.append(f"[INSTRUÇÕES DO AGENTE]\n{agent_prompt}")
                if imported:
                    parts.append(f"[INSTRUÇÕES FEDERADAS — origem {artifact.ecosystem}; artefato {artifact.artifact_id}]\n{imported}")
                if residual.get("metacognitive_briefing"):
                    parts.append(f"[MEMÓRIA METACOGNITIVA]\n{residual['metacognitive_briefing']}")
                if residual["revisions"]:
                    parts.append(f"[SAÍDA ANTERIOR]\n{residual['revisions'][-1]['output']}")
                parts.append(f"[TAREFA]\n{prompt}")
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise _ExecutionStopped("exhausted", "Prazo global esgotado antes da próxima tentativa.")
                    result["steps"] += 1
                    # O ID e o prompt selecionado já estão no contexto, inclusive
                    # para agentes registrados em código sem um arquivo .md.
                    try:
                        outcome = self.runtime.execute(current_executor, "\n\n".join(parts),
                                                       timeout=remaining, agent_id=None)
                    except Exception as exc:
                        outcome = {"success": False, "output": "", "error": str(exc)}
                    if not isinstance(outcome, dict):
                        outcome = {"success": False, "output": "", "error": "Executor não devolveu um resultado estruturado."}
                    finished = time.monotonic()
                    output = outcome.get("output", "")
                    error = ""
                    if outcome.get("success") is not True or outcome.get("status") in {"queued", "pending", "formatted", "blocked", "failed", "error"}:
                        error = str(outcome.get("error") or "Executor não concluiu a tarefa.")
                    elif not isinstance(output, str) or not output.strip():
                        error = "Executor devolveu saída vazia."
                    if finished > deadline:
                        error = "Prazo global esgotado durante a execução."
                    attempt = dict(outcome)
                    attempt.update(ecosystem=current_executor, step=result["steps"], success=not error,
                                   error=error, elapsed_seconds=round(max(0.0, finished - (deadline - remaining)), 3))
                    if error:
                        attempt.pop("output", None)
                    result["attempts"].append(attempt)
                    result["runtime_execution_mode"] = outcome.get("execution_mode")
                    result["ecosystem"] = current_executor
                    result["execution_mode"] = "adapted_instructions" if artifact and current_executor != artifact.ecosystem else "native_cli"
                    if not error:
                        return output
                    failed_executors.add(current_executor)
                    metabus.publish("autonomous.executor_failed", {
                        "task_id": task_id, "agent_id": agent_id, "executor": current_executor,
                        "step": result["steps"], "error": error,
                    }, source_agent="marceloclaro.autonomous")
                    if finished > deadline:
                        raise _ExecutionStopped("exhausted", error)
                    if ecosystem is not None or result["steps"] >= max_steps:
                        raise _ExecutionStopped("failed", error)
                    # Outra sessão pode ter observado uma falha enquanto esta
                    # chamada executava. Não reutilizar a elegibilidade antiga.
                    fresh = self._executor_map(self.runtime.status())
                    alternatives = [name for name in ("codex", "antigravity", "claude")
                                    if name not in failed_executors
                                    and isinstance(fresh.get(name), dict)
                                    and fresh[name].get("available") is True
                                    and fresh[name].get("eligible_for_auto", True)]
                    if not alternatives:
                        raise _ExecutionStopped("failed", error)
                    successor = alternatives[0]
                    result["fallbacks"].append({"from": current_executor, "to": successor,
                                                "reason": error, "after_step": result["steps"]})
                    current_executor = successor

            pipeline = TransformerPipeline(num_layers=max_steps, grading_head=orchestrator.pipeline.grading_head)
            try:
                pipeline_result = pipeline.run(task, execute, context)
            except _RevisionBudgetReached:
                best = max(context["revisions"], key=lambda revision: revision["grade"]["score"])
                pipeline_result = {"final_output": best["output"], "final_grade": best["grade"]}
            result.update(status="completed", success=True, output=pipeline_result["final_output"],
                          final_grade=pipeline_result["final_grade"], error="")
            delivery = next(attempt for attempt in result["attempts"]
                            if attempt["success"] and attempt.get("output") == result["output"])
            result.update(ecosystem=delivery["ecosystem"], runtime_execution_mode=delivery.get("execution_mode"),
                          delivery_step=delivery["step"],
                          execution_mode="adapted_instructions" if artifact and delivery["ecosystem"] != artifact.ecosystem else "native_cli")
        except _ExecutionStopped as exc:
            result.update(status=exc.status, success=False, error=str(exc))
        except Exception as exc:
            result.update(status="failed", success=False, error=str(exc))

        # report_completion já integra SDD, trust, economia e reflexão MetaBus.
        # O resultado público acompanha o estado aceito, inclusive veto SDD.
        completion_payload = self._completion_payload(result)
        # O gate ainda não avaliou a entrega. MetaBus serializa o evento antes
        # do retorno, portanto não publique uma alegação de aceitação aqui.
        # task.complete.status será o desfecho autoritativo emitido pelo gate.
        completion_payload.pop("status")
        completion_payload.pop("success")
        try:
            orchestrator.report_completion(task_id, agent_id, completion_payload, success=result["success"])
            accepted = blackboard.tasks[task_id].status == "completed"
            if result["success"] and not accepted:
                result.update(status="failed", success=False, error="A conclusão foi recusada pelo gate do orquestrador.")
        except Exception as exc:
            result.update(status="failed", success=False, error=f"Falha ao registrar conclusão: {exc}")
            completion_payload.update(status=result["status"], success=False, error=result["error"])
            metabus.publish("task.complete", {"task_id": task_id, "agent_id": agent_id,
                            "status": "failed", "result": completion_payload}, source_agent=agent_id)
        finally:
            # BlackboardTask.result e orchestrator.results compartilham este
            # objeto. Atualize-o após o gate sem repetir conclusão/reflexão.
            completion_payload.update(status=result["status"], success=result["success"], error=result["error"])
        return result
