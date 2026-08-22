# -*- coding: utf-8 -*-
"""
Orquestrador MarceloClaro
=========================
Orquestrador supremo do OpenCode Ecosystem Core. Coordena todos os agentes por meio
da camada Metacognitive Interconnect (MCI):

1. PERCEBE  — consulta a memória metacognitiva compartilhada (Global Workspace)
              antes de qualquer decisão, herdando lições de execuções anteriores.
2. DELEGA   — posta tarefas no Blackboard; agentes elegíveis voluntariam-se
              (padrão Blackboard, arXiv:2510.01285) e a seleção final pondera
              capacidades declaradas (Agent Cards A2A) × confidence ledger.
3. REFLETE  — após cada conclusão, o ReflexionEngine gera auto-reflexões
              (Reflexion, Shinn et al. 2023) que realimentam a memória global.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import copy
import math
import uuid
import time
import logging
from dataclasses import dataclass
from typing import Dict, List, Any, Iterable, Mapping, Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mci.metabus import metabus
from mci.blackboard import blackboard
from mci.task_runtime import AcceptanceCriterion, NanoTaskSpec, TaskGraph, TaskRuntime
from synthetic_university import SyntheticUniversity
from mci.reflexion import reflexion_engine  # noqa: F401 — ativa o singleton
from mci import run_scientific_cycle, run_scientific_governance_pipeline
from marceloclaro.agent_loader import register_all_agents, load_agent_definitions
from skills.tooling.llm_reduction import LLMReductionLayer
from transformer.attention import AttentionRouter
from transformer.pipeline import TransformerPipeline, GradingHead
from transformer.memory import HierarchicalMemory
from sdd.spec_engine import spec_registry, spec_verifier
from sdd.tdd_runner import tdd_runner, run_pytest
from sdd.loop_spec import LoopSpecification, loop_spec_registry, is_stagnant
from marceloclaro.doctor import run_doctor
from marceloclaro.helpdesk import run_helpdesk
from marceloclaro.inspiration_audit import audit_inspirations as run_inspiration_audit
from trust import create_trust_engine
from economy import TokenEconomy
from scanners import diagnostic_pipeline
from academic import MaswosPipeline
from reasoning import multi_reasoning, run_experiment_suite
from reasoning.production_scaffolds import audit_scientific_manuscript
from agentic_science_v2.paper_composer import compose_paper as compose_paper_core
from evolution import evolution_registry
from integrations.antigravity import antigravity_bridge
from marceloclaro.catalog_loader import register_catalog_agents

logger = logging.getLogger("marceloclaro")
logger.setLevel(logging.INFO)


@dataclass(frozen=True)
class NanoTaskAssignment:
    """Atribuição auditável vinculada ao lease concedido pelo runtime."""

    graph_id: str
    task_id: str
    agent_id: str
    lease_token: str
    attempt: int
    lease_expires_at: float


class MarceloClaroOrchestrator:
    """Orquestrador central metacognitivo do ecossistema."""

    RUNTIME_MIN_TRUST = 0.25
    RUNTIME_MAX_LOAD = 1.0

    def __init__(self, auto_load_agents: bool = True, pipeline_layers: int = 3,
                 strict_sdd: bool = True,
                 reduction_layer: Optional[LLMReductionLayer] = None):
        self.id = "marceloclaro"
        self.pending_cfps: Dict[str, List[str]] = {}  # task_id -> agentes elegíveis
        self.results: Dict[str, Any] = {}

        # Modo SDD estrito: nenhuma conclusão aceita sem verificação de spec (INV-006.1)
        self.strict_sdd = strict_sdd
        self.task_specs: Dict[str, str] = {}  # task_id -> spec_id

        # LLM Reduction Layer (SPEC-967): substitui AttentionRouter para
        # tarefas com alta confiança no roteamento determinístico.
        self.reduction_layer = reduction_layer or LLMReductionLayer()
        self.reduction_threshold = 0.85
        self._llm_calls_saved = 0

        # Trust Engine (SPEC-038): gate comportamental, esquecimento natural, outcomes
        self.trust = create_trust_engine()

        # Runtime R212: DAGs locais, leases e recuperação com orçamento finito.
        self.task_runtime = TaskRuntime(outcome_recorder=self._record_runtime_outcome)
        self._assignment_explanations: Dict[tuple[str, str], Dict[str, Any]] = {}

        # Token Economy (SPEC-022~025): staking, slashing, fee market
        self.economy = TokenEconomy()
        self.task_stakes: Dict[str, str] = {}  # task_id -> agent_id com stake

        # Pipeline acadêmico Qualis A1 (MASWOS) acoplado à delegação real
        self.maswos = MaswosPipeline(delegate_fn=self._maswos_delegate)

        # Ponte DeepSeek Harness (SPEC-935-R433/R434) — lazy, não falha sem zip
        self._dsh_bridge = None
        self._dsh_bridge_failed = False
        self._dsh_reasoning_loop = None
        # Harness Universal agnóstico (SPEC-935-R435) — qualquer modelo OpenCode
        self._harness_bridge = None
        self._harness_bridge_failed = False
        self._harness_reasoning_loop = None
        # Buscas/RAG/Referências aprimorados (SPEC-935-R436) — lazy
        self._search_rag = None
        # Reversa Universal (SPEC-935-R437) — lazy
        self._reversa_bridge = None

        # MiroFish (enxame preditivo) — carregamento tardio
        self._swarm_validator = None

        # Camada Transformer (inspiração: Vaswani 2017, Perceiver, HTM, Aletheia)
        self.attention_router = AttentionRouter()
        self.pipeline = TransformerPipeline(num_layers=pipeline_layers, grading_head=GradingHead())
        self.hierarchical_memory = HierarchicalMemory(metabus.memory)
        self._task_counter = 0  # positional encoding das tarefas

        # Escuta o Global Workspace
        metabus.subscribe("task.cfp", self._on_cfp, f"{self.id}:task.cfp")
        metabus.subscribe("task.assigned", self._on_assigned, f"{self.id}:task.assigned")
        metabus.subscribe(
            "metacognition.reflected",
            self._on_reflected,
            f"{self.id}:metacognition.reflected",
        )

        if auto_load_agents:
            register_all_agents(metabus)

        # Catálogo de 128+ agentes especializados (portados do OpenCode_Ecosystem)
        self.catalog_size = 0
        if auto_load_agents:
            try:
                self.catalog_size = register_catalog_agents(metabus)
                logger.info(f"[{self.id}] Catálogo registrado: {self.catalog_size} agentes especializados")
            except Exception as exc:
                logger.warning(f"[{self.id}] Falha ao registrar catálogo: {exc}")

        # MIRA R126: o executor só é registrado no modo normal; a opção
        # auto_load_agents=False continua útil para testes e chamadas leves.
        self._mira_agent = None
        if auto_load_agents:
            self.register_mira_agent()

        # Loop Engineering R109: registro idempotente e independente do
        # carregamento do catálogo, para que describe_scientific_loop() seja
        # utilizável também em instâncias mínimas.
        loop_spec_registry.register(LoopSpecification(
            name="scientific-discovery",
            description=(
                "Repete o pipeline R101-R105 (scientific_discovery_pipeline) "
                "até atingir o gate de exportação do R103 ou um estado "
                "terminal de parada (no_op/blocked/stalled/exhausted/error)."
            ),
            use_when=(
                "Uma rodada do pipeline científico não atingiu o gate de qualidade "
                "e vale a pena tentar novas rodadas antes de desistir."
            ),
            trigger="manual",
            trigger_justification=(
                "O resultado de cada rodada (gate e readiness_score) muda a "
                "decisão da próxima rodada — há feedback real entre voltas."
            ),
            goal="R103 aprova export_gate_passed e R104d/R105 completam com sucesso.",
            goal_verifiable=True,
            verification_level=1,
            verification_description=(
                "export_gate_passed do R103, threshold determinístico sobre "
                "traceability/coverage do AuditGraph."
            ),
            architecture="solo",
            terminal_states=["success", "no_op", "blocked", "stalled", "exhausted", "error"],
            stagnation_window=3,
            stagnation_threshold=0.02,
            max_iterations=5,
            memory_location=(
                "mci.metabus.metabus.memory (episodic + confidence_ledger, "
                "persistido em .mci_state/)"
            ),
            guardrails=[
                "Erro interrompe o loop imediatamente.",
                "Estagnação para o loop antes do teto de orçamento.",
                "R101 sem ideias é no_op, não sucesso.",
            ],
        ))

    # ------------------------------------------------------------------
    # 1. PERCEPÇÃO METACOGNITIVA
    # ------------------------------------------------------------------
    def perceive(self, topic: str = "general_execution", limit: int = 5) -> Dict[str, Any]:
        """Consulta o Global Workspace antes de decidir: lições + contexto recente."""
        return {
            "recent_context": metabus.memory.get_recent_context(limit),
            "lessons": metabus.memory.extract_lessons(topic),
            "confidence_ledger": dict(metabus.memory.confidence_ledger),
        }

    # ------------------------------------------------------------------
    # 2. DELEGAÇÃO VIA BLACKBOARD
    # ------------------------------------------------------------------
    def delegate(self, description: str, required_capabilities: Optional[List[str]] = None,
                 context: Optional[Dict[str, Any]] = None) -> str:
        """Posta uma tarefa no Blackboard e retorna o task_id."""
        task_id = f"task-{uuid.uuid4().hex[:8]}"

        # Percepção metacognitiva pré-delegação
        awareness = self.perceive()
        enriched_context = dict(context or {})
        enriched_context["metacognitive_briefing"] = {
            "lessons": awareness["lessons"][-5:],
            "orchestrator": self.id,
        }

        metabus.publish("task.post", {
            "task_id": task_id,
            "description": description,
            "required_capabilities": required_capabilities or [],
            "context": enriched_context,
        }, source_agent=self.id)

        logger.info(f"[{self.id}] Tarefa delegada: {task_id} — {description}")
        return task_id

    # ------------------------------------------------------------------
    # 2a. RUNTIME NANOGRANULAR (SPEC-935-R212)
    # ------------------------------------------------------------------
    def _record_runtime_outcome(self, action_id: str, success: bool) -> None:
        """Atualiza trust sem tornar a conclusão do runtime dependente do ledger."""

        try:
            self.trust.learn(action_id, success=success)
        except Exception as exc:
            logger.warning(
                "[%s] Não foi possível registrar outcome do runtime para %s: %s",
                self.id,
                action_id,
                exc,
            )

    def nanogranulate(
        self,
        objective: str,
        required_capabilities: Iterable[str] = (),
        expected_artifact: Optional[str] = None,
        acceptance_criteria: Optional[Iterable[AcceptanceCriterion]] = None,
    ) -> TaskGraph:
        """Decompõe um objetivo pela implementação determinística do runtime."""

        return self.task_runtime.nanogranulate(
            objective=objective,
            required_capabilities=required_capabilities,
            expected_artifact=expected_artifact,
            acceptance_criteria=acceptance_criteria,
        )

    def submit_graph(self, graph: TaskGraph) -> str:
        """Submete o DAG sem contornar as validações fail-closed do runtime."""

        return self.task_runtime.submit_graph(graph)

    @staticmethod
    def _unit_metric(value: Any) -> Optional[float]:
        """Retorna métrica finita em ``[0, 1]`` ou ``None`` se inválida."""

        if isinstance(value, bool):
            return None
        try:
            metric = float(value)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(metric) or not 0.0 <= metric <= 1.0:
            return None
        return metric

    def _runtime_candidate_snapshot(self) -> tuple[Dict[str, Any], ...]:
        """Converte o registry legado em candidatos explícitos e imutáveis."""

        candidates: List[Dict[str, Any]] = []
        for card in blackboard.registry.values():
            candidate = dict(card.to_dict())
            candidate["load"] = 0.0 if candidate.get("status") == "available" else 1.0
            candidate["circuit_open"] = False
            candidates.append(candidate)
        return tuple(candidates)

    def _gate_runtime_candidates(
        self,
        task: NanoTaskSpec,
        candidates: Iterable[object],
    ) -> tuple[List[Dict[str, Any]], Dict[str, List[str]], Dict[str, Dict[str, Any]]]:
        """Aplica capability/status/trust/circuit/load antes de qualquer score."""

        eligible_by_id: Dict[str, Dict[str, Any]] = {}
        excluded: Dict[str, List[str]] = {}
        evidence: Dict[str, Dict[str, Any]] = {}
        seen_agent_ids: set[str] = set()
        required = set(task.required_capabilities)

        for index, raw_candidate in enumerate(candidates):
            fallback_id = f"candidate-{index}"
            if not isinstance(raw_candidate, Mapping):
                excluded[fallback_id] = ["invalid_candidate"]
                evidence[fallback_id] = {
                    "passed": False,
                    "reasons": ["invalid_candidate"],
                }
                continue

            candidate = dict(raw_candidate)
            raw_agent_id = candidate.get("agent_id")
            if not isinstance(raw_agent_id, str) or not raw_agent_id.strip():
                excluded[fallback_id] = ["missing_agent_id"]
                evidence[fallback_id] = {
                    "passed": False,
                    "reasons": ["missing_agent_id"],
                }
                continue
            agent_id = raw_agent_id.strip()
            if agent_id in seen_agent_ids:
                eligible_by_id.pop(agent_id, None)
                excluded[agent_id] = ["duplicate_agent_id"]
                evidence[agent_id] = {
                    "passed": False,
                    "reasons": ["duplicate_agent_id"],
                }
                continue
            seen_agent_ids.add(agent_id)
            reasons: List[str] = []

            raw_capabilities = candidate.get("capabilities", ())
            if isinstance(raw_capabilities, str):
                capabilities = (raw_capabilities.strip(),) if raw_capabilities.strip() else ()
            else:
                try:
                    declared_capabilities = tuple(raw_capabilities)
                except TypeError:
                    capabilities = ()
                    reasons.append("invalid_capabilities")
                else:
                    if any(
                        not isinstance(capability, str)
                        for capability in declared_capabilities
                    ):
                        reasons.append("invalid_capabilities")
                    capabilities = tuple(
                        capability.strip()
                        for capability in declared_capabilities
                        if isinstance(capability, str) and capability.strip()
                    )
            missing = sorted(required - set(capabilities))
            if missing:
                reasons.append("missing_capabilities:" + ",".join(missing))

            status = candidate.get("status")
            if status != "available":
                reasons.append("status_not_available")

            raw_circuit = candidate.get("circuit_open", False)
            if not isinstance(raw_circuit, bool):
                circuit_open = True
                reasons.append("invalid_circuit_state")
            else:
                circuit_open = raw_circuit
                if circuit_open:
                    reasons.append("circuit_open")

            raw_load = candidate.get("load", 0.0)
            load = self._unit_metric(raw_load)
            if load is None:
                load = 1.0
                reasons.append("invalid_load")
            elif load >= self.RUNTIME_MAX_LOAD:
                reasons.append("load_at_capacity")

            supplied_trust = "trust_score" in candidate
            trust_score = self._unit_metric(candidate.get("trust_score"))
            if supplied_trust and trust_score is None:
                reasons.append("invalid_trust_score")

            trust_allowed = False
            trust_reason = "trust gate sem decisão"
            try:
                trust_decision = self.trust.execute(f"delegate:{agent_id}")
                trust_allowed = bool(getattr(trust_decision, "allowed", False))
                trust_reason = str(getattr(trust_decision, "reason", trust_reason))
                if trust_score is None and not supplied_trust:
                    trust_score = self._unit_metric(
                        getattr(trust_decision, "trust_score", None)
                    )
            except Exception as exc:
                trust_reason = f"trust gate indisponível: {exc}"
                reasons.append("trust_gate_error")
            if not trust_allowed:
                reasons.append("trust_denied")
            if trust_score is None:
                trust_score = 0.5 if trust_allowed and not supplied_trust else 0.0
            if trust_score < self.RUNTIME_MIN_TRUST:
                reasons.append("trust_below_minimum")

            live_confidence = metabus.memory.confidence_ledger.get(
                agent_id,
                candidate.get("confidence_score", 0.5),
            )
            normalized = dict(candidate)
            normalized.update({
                "agent_id": agent_id,
                "capabilities": list(dict.fromkeys(capabilities)),
                "status": status,
                "trust_score": trust_score,
                "confidence_score": live_confidence,
                "load": load,
                "circuit_open": circuit_open,
            })

            # Evita repetir uma mesma razão quando dois sinais de trust falham.
            reasons = list(dict.fromkeys(reasons))
            gate_evidence = {
                "passed": not reasons,
                "reasons": list(reasons),
                "required_capabilities": sorted(required),
                "declared_capabilities": list(normalized["capabilities"]),
                "status": status,
                "trust_score": trust_score,
                "trust_allowed": trust_allowed,
                "trust_reason": trust_reason,
                "circuit_open": circuit_open,
                "load": load,
            }
            evidence[agent_id] = gate_evidence
            if reasons:
                excluded[agent_id] = reasons
            else:
                eligible_by_id[agent_id] = normalized

        return list(eligible_by_id.values()), excluded, evidence

    def dispatch_ready(
        self,
        graph_id: str,
        candidates: Optional[Iterable[Mapping[str, Any]]] = None,
    ) -> tuple[NanoTaskAssignment, ...]:
        """Ranqueia a fronteira pronta e concede leases somente após hard gates."""

        if candidates is None:
            candidate_snapshot: tuple[object, ...] = self._runtime_candidate_snapshot()
        elif isinstance(candidates, Mapping):
            candidate_snapshot = (dict(candidates),)
        else:
            candidate_snapshot = tuple(candidates)

        assignments: List[NanoTaskAssignment] = []
        for task in self.task_runtime.ready_tasks(graph_id):
            eligible, excluded, gate_evidence = self._gate_runtime_candidates(
                task,
                candidate_snapshot,
            )
            routing = self.attention_router.explain(
                task.description,
                list(task.required_capabilities),
                eligible,
            )
            for agent_id, reasons in routing["excluded"].items():
                excluded.setdefault(agent_id, []).extend(reasons)

            ranking = list(routing["ranking"])
            ranked_ids = [agent_id for agent_id, _ in ranking]
            ranking_weights = dict(ranking)
            scores = {
                agent_id: {
                    **{
                        head: routing["heads"][head][agent_id]
                        for head in routing["heads"]
                    },
                    "utility": routing["utility"][agent_id],
                    "ranking_weight": ranking_weights[agent_id],
                }
                for agent_id in ranked_ids
            }
            explanation: Dict[str, Any] = {
                "graph_id": graph_id,
                "task_id": task.task_id,
                "selected_agent_id": None,
                "eligible_agents": ranked_ids,
                "excluded_agents": excluded,
                "hard_gate_results": gate_evidence,
                "scores": scores,
                "weights": dict(routing["weights"]),
                "ranking": ranking,
                "lease": None,
                "hard_gates": {
                    "capabilities": "all_of",
                    "status": "available",
                    "minimum_trust": self.RUNTIME_MIN_TRUST,
                    "circuit_open": False,
                    "maximum_load_exclusive": self.RUNTIME_MAX_LOAD,
                },
            }

            key = (graph_id, task.task_id)
            if not ranking:
                reason = "nenhum candidato passou por todos os hard gates"
                self.task_runtime.block_task(graph_id, task.task_id, reason)
                explanation["blocked_reason"] = reason
                self._assignment_explanations[key] = copy.deepcopy(explanation)
                continue

            selected_agent_id = ranking[0][0]
            lease = self.task_runtime.lease_task(
                graph_id,
                task.task_id,
                selected_agent_id,
            )
            assignment = NanoTaskAssignment(
                graph_id=graph_id,
                task_id=task.task_id,
                agent_id=selected_agent_id,
                lease_token=lease.token,
                attempt=lease.attempt,
                lease_expires_at=lease.expires_at,
            )
            assignments.append(assignment)
            explanation["selected_agent_id"] = selected_agent_id
            explanation["lease"] = {
                "token": lease.token,
                "attempt": lease.attempt,
                "issued_at": lease.issued_at,
                "expires_at": lease.expires_at,
            }
            self._assignment_explanations[key] = copy.deepcopy(explanation)

        return tuple(assignments)

    def explain_assignment(self, graph_id: str, task_id: str) -> Dict[str, Any]:
        """Retorna cópia da decisão persistida; nunca fabrica auditoria ausente."""

        self.task_runtime.task_state(graph_id, task_id)
        key = (graph_id, task_id)
        try:
            explanation = self._assignment_explanations[key]
        except KeyError:
            raise KeyError(
                f"não há decisão de atribuição para {graph_id!r}/{task_id!r}"
            ) from None
        return copy.deepcopy(explanation)

    def _on_cfp(self, event: Dict[str, Any]):
        """Recebe o Call for Proposals e roteia via Multi-Head Attention.

        Integra o Trust Engine (SPEC-038): agentes cujo BehavioralGate bloqueia
        a ação são removidos da elegibilidade antes do roteamento por atenção.
        """
        payload = event.get("payload", {})
        task_id = payload.get("task_id")
        description = payload.get("description", "")
        eligible = payload.get("eligible_agents", [])

        # Gate comportamental (Trust Engine): qualquer erro ou negação exclui.
        gated = []
        for agent_id in eligible:
            try:
                decision = self.trust.execute(f"delegate:{agent_id}")
            except Exception as exc:
                logger.warning(
                    "[%s] BehavioralGate indisponível para %s: %s",
                    self.id,
                    agent_id,
                    exc,
                )
                continue
            if bool(getattr(decision, "allowed", False)):
                gated.append(agent_id)
            else:
                logger.info(
                    "[%s] BehavioralGate bloqueou %s: %s",
                    self.id,
                    agent_id,
                    getattr(decision, "reason", "decisão sem justificativa"),
                )
        eligible = gated
        self.pending_cfps[task_id] = list(eligible)

        if not eligible:
            logger.warning(f"[{self.id}] Nenhum agente elegível para {task_id}")
            task = blackboard.tasks.get(task_id)
            if task is not None:
                task.status = "blocked"
                task.assigned_to = None
            return

        # ─── LLM Reduction Layer (SPEC-967): tenta roteamento determinístico ───
        # Se a confiança for ≥ threshold e o agente sugerido for elegível,
        # evita a chamada ao AttentionRouter (LLM real).
        reduction_result = self.reduction_layer.route(description)
        reduction_agent = reduction_result.get("agent", "")
        reduction_conf = reduction_result.get("confidence", 0.0)
        chosen: Optional[str] = None

        if (reduction_conf >= self.reduction_threshold
                and reduction_agent in eligible):
            chosen = reduction_agent
            self._llm_calls_saved += 1
            logger.info(
                "[%s] Redução LLM: %s → %s (conf=%.2f, método=%s)",
                self.id, task_id, chosen, reduction_conf,
                reduction_result.get("method", "?"),
            )
        else:
            # Fallback: roteamento por atenção multi-cabeça
            task = blackboard.tasks.get(task_id)
            required = task.required_capabilities if task else []
            cards = [blackboard.registry[a].to_dict() for a in eligible if a in blackboard.registry]

            self._task_counter += 1
            ranking = self.attention_router.route(description, required, cards,
                                                  positional_index=self._task_counter)
            self.pending_cfps[task_id] = [agent_id for agent_id, _ in ranking]
            if not ranking:
                logger.warning(f"[{self.id}] Nenhum agente passou pelos hard gates para {task_id}")
                if task is not None:
                    task.status = "blocked"
                    task.assigned_to = None
                return
            chosen = ranking[0][0]
            logger.info(f"[{self.id}] Atenção rankeou {task_id}: {ranking[:3]}")

        # chosen está definido neste ponto

        # Token Economy: cotação de fee e stake do agente escolhido
        try:
            self.economy.post_task(self.id, task_id, priority="normal")
            self.economy.commit(chosen, task_id, amount=2.0)
            self.task_stakes[task_id] = chosen
        except Exception as exc:
            logger.debug(f"[{self.id}] Economia indisponível para {task_id}: {exc}")

        metabus.publish("task.volunteer", {
            "task_id": task_id,
            "agent_id": chosen,
        }, source_agent=self.id)

    def _on_assigned(self, event: Dict[str, Any]):
        payload = event.get("payload", {})
        logger.info(f"[{self.id}] Tarefa {payload.get('task_id')} atribuída a {payload.get('agent_id')}")

    # ------------------------------------------------------------------
    # 3. CONCLUSÃO E REFLEXÃO
    # ------------------------------------------------------------------
    def report_completion(self, task_id: str, agent_id: str, result: Any, success: bool = True):
        """
        Reporta a conclusão de uma tarefa (chamado pelo executor do agente).

        Gate SDD (INV-006.1): se a tarefa possui especificação associada, a entrega
        é verificada contra os critérios de aceitação ANTES de ser aceita. No modo
        estrito, entregas reprovadas são registradas como falha.
        """
        spec_id = self.task_specs.get(task_id)
        verification = None
        if spec_id:
            verification = spec_verifier.verify(spec_id, result)
            metabus.memory.add_reflection(
                agent_id=agent_id,
                task_context=f"verificação SDD da tarefa {task_id} (spec {spec_id})",
                reflection=(
                    f"Verificação SDD: {verification['passed_count']}/"
                    f"{verification['total_count']} critérios aprovados "
                    f"(status: {verification['status']})."
                ),
                score=1.0 if verification["verified"] else 0.0,
            )
            if self.strict_sdd and not verification["verified"]:
                logger.warning(
                    f"[{self.id}] GATE SDD: entrega de {agent_id} para {task_id} "
                    f"REPROVADA na spec {spec_id}; registrando como falha."
                )
                success = False

        metabus.publish("task.complete", {
            "task_id": task_id,
            "agent_id": agent_id,
            "status": "completed" if success else "failed",
            "result": result,
            "sdd_verification": verification,
        }, source_agent=agent_id)
        self.results[task_id] = result

        # Trust Engine aprende com o outcome (OutcomeTracker + TrustScorer)
        self.trust.learn(f"delegate:{agent_id}", success=success)

        # Token Economy: resolve stakes (recompensa ou slashing)
        if task_id in self.task_stakes:
            try:
                resolution = self.economy.resolve(task_id, success=success)
                if not success:
                    logger.info(f"[{self.id}] Slashing aplicado a {agent_id} na tarefa {task_id}")
                del self.task_stakes[task_id]
            except Exception as exc:
                logger.debug(f"[{self.id}] Resolução econômica falhou: {exc}")

    def _on_reflected(self, event: Dict[str, Any]):
        payload = event.get("payload", {})
        logger.info(
            f"[{self.id}] Reflexão registrada para {payload.get('agent_id')} "
            f"(nova confiança: {payload.get('new_confidence')})"
        )

    # ------------------------------------------------------------------
    # LLM REDUCTION STATS (SPEC-967)
    # ------------------------------------------------------------------
    def get_reduction_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da camada de redução de LLM."""
        stats = dict(self.reduction_layer.stats)
        stats["_llm_calls_saved"] = self._llm_calls_saved
        if hasattr(self.reduction_layer, "get_stats"):
            extra = self.reduction_layer.get_stats()
            if isinstance(extra, dict):
                stats["router_stats"] = extra
        return stats

    # ------------------------------------------------------------------
    # AUDITORIA
    # ------------------------------------------------------------------
    def status(self) -> Dict[str, Any]:
        """Estado global do ecossistema para auditoria."""
        return {
            "orchestrator": self.id,
            "agents": [card.to_dict() for card in blackboard.registry.values()],
            "tasks": {tid: t.status for tid, t in blackboard.tasks.items()},
            "confidence_ledger": dict(metabus.memory.confidence_ledger),
            "episodic_memory_size": len(metabus.memory.episodic),
            "sdd": {
                "strict_mode": self.strict_sdd,
                "specs_registered": len(spec_registry.specs),
                "tasks_with_spec": len(self.task_specs),
            },
            "trust": self.trust.status,
            "economy": self.economy.report(),
            "catalog_agents": self.catalog_size,
            "reasoning_engines": multi_reasoning.status(),
            "antigravity": antigravity_bridge.status(),
            "evolution_avg_score": evolution_registry.average_score(),
        }

    # ------------------------------------------------------------------
    # DOCTOR — DIAGNÓSTICO DE SAÚDE DO ECOSSISTEMA (SPEC-935-R110)
    # ------------------------------------------------------------------
    def doctor(self) -> Dict[str, Any]:
        """
        Diagnóstico estrutural rápido do ecossistema (specs formais,
        registro de evolução, loop specs, memória metacognitiva,
        configuração do opencode.json, prática de correção pública de
        overclaims). Complementa — não substitui — a suíte pytest
        completa (``scripts/quality_report.py``).
        """
        report = run_doctor()
        report["catalog_agents"] = self.catalog_size
        report["trust_status"] = self.trust.status
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context="diagnóstico de saúde do ecossistema (doctor)",
            reflection=(
                f"Doctor: {report['overall']} — {report['checks_passed']} ok, "
                f"{report['checks_warned']} avisos, {report['checks_failed']} falhas."
            ),
            score={"healthy": 1.0, "degraded": 0.6, "unhealthy": 0.1}.get(report["overall"], 0.5),
        )
        return report

    def helpdesk(self) -> Dict[str, Any]:
        """Executa o diagnóstico guiado e registra a reflexão resultante."""
        report = run_helpdesk()
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context="helpdesk (diagnóstico guiado)",
            reflection=report["summary"],
            score={"healthy": 1.0, "degraded": 0.6, "unhealthy": 0.1}.get(
                report["overall"], 0.5,
            ),
        )
        return report

    # ------------------------------------------------------------------
    # PONTE DEEPSEEK HARNESS (SPEC-935-R433)
    # Integra produções autônomas e metacognições do dsh ao ciclo
    # Perceber → Especificar → Delegar → Executar → Verificar → Refletir.
    # Lazy: a ponte é resolvida apenas no primeiro acesso; falhas de
    # import ou ausência do diretório deepseek-harness/ não quebram o
    # __init__ do orquestrador.
    # ------------------------------------------------------------------
    @property
    def dsh_bridge(self):
        if not hasattr(self, "_dsh_bridge") or self._dsh_bridge is None:
            # cache miss — tenta resolver lazy
            if getattr(self, "_dsh_bridge_failed", False):
                return None
            try:
                from integrations.deepseek_harness.bridge import DeepSeekHarnessBridge

                self._dsh_bridge = DeepSeekHarnessBridge()
                self._dsh_bridge_failed = False
            except Exception as exc:
                logger.warning(f"[{self.id}] Ponte dsh indisponível: {exc}")
                self._dsh_bridge = None
                self._dsh_bridge_failed = True
                return None
        return self._dsh_bridge

    def dsh_state(self) -> Dict[str, Any]:
        """Estado auditável da ponte dsh (inventário + canal + pool)."""
        bridge = self.dsh_bridge
        if bridge is None:
            return {"available": False, "reason": "ponte dsh indisponível nesta instalação"}
        try:
            return bridge.status()
        except Exception as exc:
            return {"available": False, "error": str(exc)}

    def orchestrate_deepseek_harness(
        self,
        objective: str,
        workers: int = 1,
        runner=None,
    ) -> Dict[str, Any]:
        """Orquestra uma produção autônoma do dsh sob gate SDD e reflexão.

        Aplica percepção metacognitiva prévia, delega via ponte com workers
        escaláveis, verifica o gate SDD e registra reflexão no Global Workspace.
        """
        awareness = self.perceive(topic="deepseek_harness")
        bridge = self.dsh_bridge
        if bridge is None:
            return {
                "status": "unavailable",
                "reason": "ponte dsh indisponível",
                "lessons_considered": len(awareness.get("lessons", [])),
            }
        outcome = bridge.orchestrate(objective, runner=runner, workers=workers)
        # Reflexão adicional no orquestrador (nível Core)
        try:
            verified = bool(outcome.get("verification", {}).get("verified"))
            metabus.memory.add_reflection(
                agent_id=self.id,
                task_context=f"orquestração dsh: {objective[:100]}",
                reflection=(
                    f"Core orquestrou dsh ({workers} worker(s)): "
                    f"gate SDD {outcome.get('spec_id')} "
                    f"{'aprovado' if verified else 'reprovado'}; "
                    f"{len(outcome.get('results', []))} produção(ões) escalada(s)."
                ),
                score=1.0 if verified else 0.5,
            )
        except Exception:
            pass
        outcome["lessons_considered"] = len(awareness.get("lessons", []))
        return outcome

    # ------------------------------------------------------------------
    # PONTE DSH RACIOCINADA — CICLO REFLEXIVO ATÉ 97 (SPEC-935-R434)
    # ------------------------------------------------------------------
    @property
    def dsh_reasoning_loop(self):
        if getattr(self, "_dsh_reasoning_loop", None) is not None:
            return self._dsh_reasoning_loop
        try:
            from integrations.deepseek_harness.reasoning_loop import DeepSeekReasoningLoop

            self._dsh_reasoning_loop = DeepSeekReasoningLoop(bridge=self.dsh_bridge)
        except Exception as exc:
            logger.warning(f"[{self.id}] Loop raciocinado dsh indisponível: {exc}")
            return None
        return self._dsh_reasoning_loop

    def dsh_reasoning_status(self) -> Dict[str, Any]:
        """Estado do loop raciocinado (motores + loop spec + último histórico)."""
        try:
            from reasoning import multi_reasoning

            reasoning = multi_reasoning.status()
        except Exception:
            reasoning = {}
        try:
            from sdd.loop_spec import loop_spec_registry

            spec = loop_spec_registry.get("dsh-reasoning-97")
            loop = spec.to_dict() if spec else None
        except Exception:
            loop = None
        return {
            "reasoning_engines": reasoning,
            "loop_spec": loop,
            "bridge_available": self.dsh_bridge is not None,
        }

    def orchestrate_deepseek_harness_iterative(
        self,
        objective: str,
        workers: int = 1,
        runner=None,
        max_iters: int = 3,
        target: float = 0.97,
    ) -> Dict[str, Any]:
        """Ciclo reflexivo raciocinado até o gate 97 (calibrada + grading).

        Aplica percepção metacognitiva, pré-raciocínio multi-motor, loop de
        execução-calibração-grading-reflexão e reflexão final no Global Workspace.
        """
        awareness = self.perceive(topic="deepseek_harness")
        loop = self.dsh_reasoning_loop
        if loop is None:
            return {
                "status": "unavailable",
                "reason": "loop raciocinado indisponível",
                "lessons_considered": len(awareness.get("lessons", [])),
            }
        result = loop.run(objective, runner=runner, workers=workers, max_iters=max_iters, target=target)
        # Reflexão do orquestrador sobre o ciclo iterativo
        try:
            best = result.get("best", {})
            cal = best.get("calibrated_value", 0) if isinstance(best, dict) else 0
            grade = best.get("grade", {}) if isinstance(best, dict) else {}
            achieved = bool(result.get("achieved_target"))
            metabus.memory.add_reflection(
                agent_id=self.id,
                task_context=f"orquestração iterativa dsh (97): {objective[:80]}",
                reflection=(
                    f"Ciclo iterativo dsh concluído em {result.get('iterations',0)} iteração(ões) "
                    f"({'atingiu' if achieved else 'não atingiu'} gate 97): "
                    f"calibrada {cal:.2f}, grade {grade.get('score','?')}/7, "
                    f"terminal={result.get('terminal')}, best_engine={result.get('pre_reason',{}).get('best_engine')}."
                ),
                score=cal if achieved else max(0.4, cal),
            )
        except Exception:
            pass
        result["lessons_considered"] = len(awareness.get("lessons", []))
        return result

    # ------------------------------------------------------------------
    # HARNESS UNIVERSAL AGNÓSTICO (SPEC-935-R435) — qualquer modelo OpenCode
    # ------------------------------------------------------------------
    @property
    def harness(self):
        """Harness universal (ModelRouter: litert/colibri/openai/zen/go/deepseek)."""
        if getattr(self, "_harness_bridge", None) is not None:
            return self._harness_bridge
        if getattr(self, "_harness_bridge_failed", False):
            return None
        try:
            from integrations.harness.universal_bridge import UniversalHarnessBridge

            self._harness_bridge = UniversalHarnessBridge()
            self._harness_bridge_failed = False
        except Exception as exc:
            logger.warning(f"[{self.id}] Harness universal indisponível: {exc}")
            self._harness_bridge = None
            self._harness_bridge_failed = True
            return None
        return self._harness_bridge

    def harness_status(self) -> Dict[str, Any]:
        """Inventário universal: modelos, providers, perfis e pool."""
        bridge = self.harness
        if bridge is None:
            return {"available": False, "reason": "harness universal indisponível"}
        try:
            return bridge.status()
        except Exception as exc:
            return {"available": False, "error": str(exc)}

    def harness_reasoning_status(self) -> Dict[str, Any]:
        try:
            from reasoning import multi_reasoning

            reasoning = multi_reasoning.status()
        except Exception:
            reasoning = {}
        try:
            from sdd.loop_spec import loop_spec_registry

            spec = loop_spec_registry.get("harness-reasoning-97")
            loop = spec.to_dict() if spec else None
        except Exception:
            loop = None
        return {"reasoning_engines": reasoning, "loop_spec": loop, "harness_available": self.harness is not None}

    @property
    def harness_reasoning_loop(self):
        if getattr(self, "_harness_reasoning_loop", None) is not None:
            return self._harness_reasoning_loop
        try:
            from integrations.harness.universal_reasoning_loop import UniversalReasoningLoop

            self._harness_reasoning_loop = UniversalReasoningLoop(bridge=self.harness)
        except Exception as exc:
            logger.warning(f"[{self.id}] Loop universal indisponível: {exc}")
            return None
        return self._harness_reasoning_loop

    def orchestrate_harness(
        self,
        objective: str,
        task_type: str = "coding",
        provider: str | None = None,
        model: str | None = None,
        workers: int = 1,
        runner=None,
    ) -> Dict[str, Any]:
        """Orquestra harness universal com qualquer modelo (gate SDD)."""
        awareness = self.perceive(topic="harness")
        bridge = self.harness
        if bridge is None:
            return {"status": "unavailable", "reason": "harness universal indisponível", "lessons_considered": len(awareness.get("lessons", []))}
        outcome = bridge.orchestrate(objective, task_type=task_type, provider=provider, model=model, runner=runner, workers=workers)
        try:
            verified = bool(outcome.get("verification", {}).get("verified"))
            metabus.memory.add_reflection(
                agent_id=self.id,
                task_context=f"harness universal {task_type}: {objective[:80]}",
                reflection=(
                    f"Harness universal ({task_type} via {provider or 'auto'}/{model or 'auto'}): "
                    f"{len(outcome.get('results',[]))} produção(ões), gate {outcome.get('spec_id')} "
                    f"{'aprovado' if verified else 'reprovado'}."
                ),
                score=1.0 if verified else 0.5,
            )
        except Exception:
            pass
        outcome["lessons_considered"] = len(awareness.get("lessons", []))
        return outcome

    def orchestrate_harness_iterative(
        self,
        objective: str,
        task_type: str = "coding",
        provider: str | None = None,
        model: str | None = None,
        workers: int = 1,
        runner=None,
        max_iters: int = 3,
        target: float = 0.97,
    ) -> Dict[str, Any]:
        """Ciclo universal reflexivo até gate 97 com qualquer modelo."""
        awareness = self.perceive(topic="harness")
        loop = self.harness_reasoning_loop
        if loop is None:
            return {"status": "unavailable", "reason": "loop universal indisponível", "lessons_considered": len(awareness.get("lessons", []))}
        result = loop.run(objective, task_type=task_type, provider=provider, model=model, runner=runner, workers=workers, max_iters=max_iters, target=target)
        try:
            best = result.get("best", {})
            cal = best.get("calibrated_value", 0) if isinstance(best, dict) else 0
            grade = best.get("grade", {}) if isinstance(best, dict) else {}
            achieved = bool(result.get("achieved_target"))
            metabus.memory.add_reflection(
                agent_id=self.id,
                task_context=f"harness iterativo 97 ({task_type}): {objective[:80]}",
                reflection=(
                    f"Harness iterativo {task_type} ({provider or 'auto'}/{model or 'auto'}) "
                    f"em {result.get('iterations',0)} it(s) {'atingiu' if achieved else 'não atingiu'} 97: "
                    f"cal {cal:.2f}, grade {grade.get('score','?')}/7, terminal={result.get('terminal')}."
                ),
                score=cal if achieved else max(0.4, cal),
            )
        except Exception:
            pass
        result["lessons_considered"] = len(awareness.get("lessons", []))
        return result

    # ------------------------------------------------------------------
    # BUSCAS UNIFICADAS + RAG APRIMORADO + REFERÊNCIAS ABNT (SPEC-935-R436)
    # ------------------------------------------------------------------
    @property
    def search_rag(self):
        if getattr(self, "_search_rag", None) is not None:
            return self._search_rag
        try:
            from rag.enhanced_search_rag import UnifiedSearchRAG

            self._search_rag = UnifiedSearchRAG()
        except Exception as exc:
            logger.warning(f"[{self.id}] search_rag indisponível: {exc}")
            return None
        return self._search_rag

    def search_rag_status(self) -> Dict[str, Any]:
        s = self.search_rag
        if s is None:
            return {"available": False, "reason": "search_rag indisponível"}
        try:
            return s.status()
        except Exception as exc:
            return {"available": False, "error": str(exc)}

    def unified_search(self, query: str, limit: int = 10, providers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Busca unificada dedup + temporal (MultiSearcher + RAG + web)."""
        s = self.search_rag
        if s is None:
            return []
        results = s.search(query, limit=limit, providers=providers)
        try:
            metabus.memory.add_reflection(
                agent_id=self.id,
                task_context=f"busca unificada: {query[:80]}",
                reflection=f"Busca unificada retornou {len(results)} resultados para '{query[:60]}'.",
                score=min(1.0, len(results) / max(1, limit)),
            )
        except Exception:
            pass
        return results

    def rag_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """RAG aprimorado grounded (expansão + temporal + citação)."""
        s = self.search_rag
        if s is None:
            return {"query": query, "abstained": True, "evidence": [], "error": "search_rag indisponível"}
        result = s.rag_query(query, top_k=top_k)
        try:
            metabus.memory.add_reflection(
                agent_id=self.id,
                task_context=f"rag query: {query[:80]}",
                reflection=(
                    f"RAG retornou {result.get('evidence_count',0)} evidências "
                    f"({'absteve' if result.get('abstained') else 'grounded'}, "
                    f"groundedness={result.get('groundedness',0):.2f})."
                ),
                score=float(result.get("groundedness", 0.0)),
            )
        except Exception:
            pass
        return result

    def audit_references(self, references: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Auditoria ABNT determinística (DOI, ano, duplicata, completude)."""
        s = self.search_rag
        if s is None:
            return {"total": 0, "error": "search_rag indisponível"}
        result = s.audit(references)
        try:
            metabus.memory.add_reflection(
                agent_id=self.id,
                task_context=f"auditoria referências: {len(references)} refs",
                reflection=(
                    f"Auditoria ABNT: {result.get('valid',0)}/{result.get('total',0)} válidas, "
                    f"{len(result.get('duplicates',[]))} duplicatas, "
                    f"{len(result.get('incomplete',[]))} incompletas."
                ),
                score=float(result.get("valid", 0)) / max(1, float(result.get("total", 0))),
            )
        except Exception:
            pass
        return result

    # ------------------------------------------------------------------
    # REVERSA UNIVERSAL — artigos, repos, códigos, scripts e gaps (SPEC-935-R437)
    # ------------------------------------------------------------------
    @property
    def reversa_bridge(self):
        if getattr(self, "_reversa_bridge", None) is not None:
            return self._reversa_bridge
        try:
            from reversa_universal.bridge import ReversaBridge

            self._reversa_bridge = ReversaBridge()
        except Exception as exc:
            logger.warning(f"[{self.id}] reversa universal indisponível: {exc}")
            return None
        return self._reversa_bridge

    def reversa_analyze(self, path: str, output_root: Optional[str] = None) -> Dict[str, Any]:
        """Análise Reversa Universal em qualquer path (artigo/repo/script)."""
        bridge = self.reversa_bridge
        if bridge is None:
            return {"error": "reversa_bridge indisponível", "target": path}
        result = bridge.analyze_and_reflect(path, output_root=output_root)
        # Metacognição adicional no orquestrador
        try:
            gaps = result.get("gaps", {}).get("metrics", {}).get("total_gaps", 0)
            metabus.memory.add_reflection(
                agent_id=self.id,
                task_context=f"reversa universal: {path}",
                reflection=f"Orquestrador aplicou Reversa em {path}: {len(result.get('modules',[]))} módulos, {gaps} gaps. Recomendações: {len(result.get('recommendations',[]))}.",
                score=min(1.0, 0.6 + gaps * 0.08) if isinstance(gaps, int) else 0.6,
            )
        except Exception:
            pass
        return result

    def reversa_on_article(self, article_path: str, output_root: Optional[str] = None) -> Dict[str, Any]:
        """Reversa em manuscrito científico (seções, referências, dados)."""
        return self.reversa_analyze(article_path, output_root=output_root)

    def reversa_on_repo(self, repo_path: str, output_root: Optional[str] = None) -> Dict[str, Any]:
        """Reversa em repositório (módulos, dependências, integrações)."""
        return self.reversa_analyze(repo_path, output_root=output_root)

    def reversa_on_scripts(self, pattern: str, base_dir: str = ".", output_root: Optional[str] = None) -> Dict[str, Any]:
        """Reversa em conjunto de scripts via glob pattern (ex. 'scripts/*.py')."""
        import glob as _glob
        import pathlib as _pl
        matches = _glob.glob(os.path.join(base_dir, pattern), recursive=True)
        if not matches:
            return {"error": f"nenhum script encontrado para pattern {pattern}", "pattern": pattern}
        # Analisa diretório comum ou primeiro match
        # Para simplicidade, analisa base_dir e filtra por pattern no report
        result = self.reversa_analyze(base_dir if _pl.Path(base_dir).is_dir() else matches[0], output_root=output_root)
        result["pattern"] = pattern
        result["matched_files"] = matches[:20]
        return result

    def reversa_enhance_gaps(self, diagnostic_report: Dict[str, Any], path: Optional[str] = None) -> Dict[str, Any]:
        """Injeta gaps Reversa em relatório de diagnóstico (scanners de gaps)."""
        bridge = self.reversa_bridge
        if bridge is None:
            return diagnostic_report
        analysis = None
        if path:
            try:
                from reversa_universal.engine import reversa_engine

                analysis = reversa_engine.analyze(path)
            except Exception:
                pass
        return bridge.enhance_gaps(diagnostic_report, analysis=analysis)

    def reversa_status(self) -> Dict[str, Any]:
        bridge = self.reversa_bridge
        if bridge is None:
            return {"available": False}
        try:
            return bridge.status()
        except Exception as exc:
            return {"available": False, "error": str(exc)}

    def reversa_enhance_reasoning(self, context: Dict[str, Any], path: Optional[str] = None) -> Dict[str, Any]:
        """Enriquece contexto de raciocínio com estrutura Reversa."""
        try:
            from reversa_universal.engine import reversa_engine

            analysis = reversa_engine.analyze(path) if path else None
            return reversa_engine.enhance_reasoning(context, analysis)
        except Exception:
            return context

    def list_agents(self) -> List[Dict[str, Any]]:
        return [card.to_dict() for card in blackboard.registry.values()]

    # ------------------------------------------------------------------
    # CAMADA TRANSFORMER (inspiração: superhuman/Aletheia + deepmind-research)
    # ------------------------------------------------------------------
    def run_pipeline(self, task_description: str, executor_fn,
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa a tarefa pelo encoder stack gerar → verificar → revisar
        (padrão Aletheia), com avaliação GradingHead (IMO-GradingBench, 0-7).
        """
        result = self.pipeline.run(task_description, executor_fn, context)
        # Registra a experiência na memória metacognitiva global
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"pipeline: {task_description}",
            reflection=(
                f"Pipeline concluído em {result['layers_used']} camada(s) com nota "
                f"{result['final_grade']['score']}/{result['final_grade']['max_score']}."
            ),
            score=result["final_grade"]["normalized"],
        )
        return result

    def run_scientific_governance(self, problem_text: str, executor_fn: Any = None,
                                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa a tarefa no pipeline científico completo com governança (OQS + MCI + VSEE + EGS).
        """
        if executor_fn is None:
            def default_exec(ctx):
                return {"result_type": "original", "data": f"Executado raciocínio original para: {problem_text}"}
            executor_fn = default_exec
            
        result = run_scientific_governance_pipeline(problem_text, executor_fn, context)
        
        # Registra a experiência na memória metacognitiva global
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"scientific_governance: {problem_text}",
            reflection=(
                f"Pipeline científico concluído com status {result['status']}. "
                f"OQS: {'passou' if result['oqs']['pass'] else 'falhou'} (CS={result['oqs']['scores']['CS']}), "
                f"EGS: decisão={result['egs']['decision']} (score={result['egs']['alignment_score']})."
            ),
            score=1.0 if result["pipeline_success"] else 0.0,
        )
        return result

    def recall(self, query: str, top_entries: int = 5) -> List[Dict[str, Any]]:
        """Recuperação hierárquica (HTM) sobre a memória episódica global."""
        return self.hierarchical_memory.retrieve(query, top_entries=top_entries)

    def explain_routing(self, description: str,
                        required_capabilities: Optional[List[str]] = None) -> Dict[str, Any]:
        """Auditoria transparente: scores de cada cabeça de atenção por agente."""
        cards = [card.to_dict() for card in blackboard.registry.values()]
        return self.attention_router.explain(description, required_capabilities or [], cards)

    # ------------------------------------------------------------------
    # CAMADA SDD/TDD (Specification-Driven + Test-Driven Development)
    # ------------------------------------------------------------------
    def delegate_with_spec(self, description: str,
                           required_capabilities: Optional[List[str]] = None,
                           acceptance_criteria: Optional[List[str]] = None,
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Delegação SDD-first: cria a especificação ANTES da tarefa (fase RED)
        e injeta o spec_id no contexto para que o agente conheça os critérios.
        """
        spec = spec_registry.create_task_spec(
            title=description,
            objective=description,
            criteria_descriptions=acceptance_criteria or ["A entrega não pode ser vazia."],
        )
        enriched = dict(context or {})
        enriched["sdd"] = {
            "spec_id": spec.spec_id,
            "acceptance_criteria": [c.description for c in spec.criteria],
            "protocol": "ESPECIFICAR -> RED -> GREEN -> REFACTOR -> VERIFICAR",
        }
        task_id = self.delegate(description, required_capabilities, enriched)
        self.task_specs[task_id] = spec.spec_id
        logger.info(f"[{self.id}] Delegação SDD: {task_id} vinculada à spec {spec.spec_id} (RED)")
        return {"task_id": task_id, "spec_id": spec.spec_id}

    def run_tdd_cycle(self, description: str, producer_fn,
                      acceptance_criteria: Optional[List[Any]] = None,
                      refactor_fn=None) -> Dict[str, Any]:
        """
        Executa o ciclo TDD completo (RED -> GREEN -> REFACTOR) sobre uma tarefa.
        `acceptance_criteria` aceita strings (descrições) ou tuplas (descrição, check_fn).
        """
        spec = spec_registry.create_task_spec(description, description)
        for item in (acceptance_criteria or []):
            if isinstance(item, tuple):
                spec.add_criterion(item[0], item[1])
            else:
                spec.add_criterion(str(item))

        result = tdd_runner.run_cycle(spec, producer_fn, refactor_fn)
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"ciclo TDD: {description}",
            reflection=(
                f"Ciclo TDD {'concluído (verified)' if result['success'] else 'falhou'} "
                f"na fase {result['phase']} para a spec {spec.spec_id}."
            ),
            score=1.0 if result["success"] else 0.0,
        )
        result["spec_id"] = spec.spec_id
        return result

    def audit_specs(self) -> Dict[str, Any]:
        """Relatório de cobertura SDD: specs formais + dinâmicas registradas."""
        return spec_registry.coverage_report()

    def audit_inspirations(self) -> Dict[str, Any]:
        """Audita a portabilidade das inspirações do diretório INSPIRAÇÕES/."""
        report = run_inspiration_audit()
        summary = report["summary"]
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context="auditoria de inspirações do ecossistema",
            reflection=(
                f"Auditoria de inspirações concluída: {summary['implemented']} implementadas, "
                f"{summary['partial']} parciais e {summary['absent']} ausentes."
            ),
            score=summary["implemented"] / max(1, summary["total_items"]),
        )
        return report

    def run_test_suite(self) -> Dict[str, Any]:
        """Executa a bateria pytest real e registra o resultado na memória global."""
        outcome = run_pytest()
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context="execução da bateria de testes do ecossistema (TDD)",
            reflection=f"Bateria pytest: {outcome['summary']}",
            score=1.0 if outcome["all_passed"] else 0.0,
        )
        return outcome

    # ------------------------------------------------------------------
    # SUBSISTEMAS AVANÇADOS (portados do OpenCode_Ecosystem original)
    # ------------------------------------------------------------------
    def diagnose(self, corpus: str, domain: str = "",
                 goals: Optional[List[Dict[str, Any]]] = None,
                 deep: bool = False,
                 include_legal_impact: bool = False,
                 legal_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Pipeline de diagnóstico com os scanners (noológico, teleológico,
        evolutivo, potentiality, social impact, reversa e opcionalmente legal impact).

        Com ``deep=True`` executa também a camada profunda (SPEC-020):
        roadmap evolutivo M1–M5 completo (trajetórias + composição unitária +
        sequenciamento), priorização epistemológica (erro → ausência →
        oportunidade) e gerador de sucessores plausíveis (DNA estrutural).
        Registra o resultado na memória metacognitiva."""
        report = diagnostic_pipeline.run(
            corpus,
            domain=domain,
            goals=goals,
            deep=deep,
            include_legal_impact=include_legal_impact,
            legal_params=legal_params,
        )
        if include_legal_impact and "legal_impact" in report:
            params = legal_params or {}
            domain_id = params.get("domain_id", "general")
            payload = {
                "titulo": params.get("titulo", "Diagnóstico Jurídico"),
                "marker": params.get("marker"),
                "overall_score": report["legal_impact"].get("overall_score", 0.0),
                "metacognitive_gain_score": report["legal_impact"].get("metacognitive_gain_score", 0.0),
                "legal_readiness": report["legal_impact"].get("legal_readiness", "—"),
                "high_risk_flags": report["legal_impact"].get("high_risk_flags", []),
            }
            metabus.publish_legal_event(
                "impact_assessed",
                domain_id=domain_id,
                payload=payload,
                source_agent=self.id,
            )
            metabus.memory.upsert_semantic_topic(
                f"legal.domain.{domain_id}",
                lesson=(
                    f"Diagnóstico jurídico '{payload['titulo']}' com readiness "
                    f"{payload['legal_readiness']} e score {payload['overall_score']}."
                ),
                metadata={
                    "last_overall_score": payload["overall_score"],
                    "last_metacognitive_gain": payload["metacognitive_gain_score"],
                },
            )
            metabus.memory.update_domain_confidence(
                domain_id,
                float(payload["metacognitive_gain_score"] or 0.0) / 100.0,
            )
        gaps = report.get("evolutionary", {}).get("total_gaps", 0)
        extra = ""
        if deep:
            eo = report.get("epistemic_opportunities", {})
            su = report.get("successors", {})
            extra = (f" Camada profunda: {eo.get('total', 0)} oportunidades "
                     f"epistemológicas ({eo.get('breakthroughs', 0)} "
                     f"breakthroughs) e {su.get('total', 0)} sucessores "
                     f"plausíveis ({su.get('immediate', 0)} imediatos).")
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"diagnóstico do ecossistema (domínio: {domain or 'geral'})",
            reflection=f"Diagnóstico concluído: {gaps} lacunas identificadas. "
                       f"{report['evolutionary']['recommendation']}" + extra,
            score=max(0.0, 1.0 - gaps / 10.0),
        )
        return report

    def academic_pipeline(self, topic: str, manuscript: str = "",
                          stages: Optional[List[str]] = None) -> Dict[str, Any]:
        """Pipeline acadêmico MASWOS Qualis A1 (16 estágios + AUTO_SCORE gate)."""
        run = self.maswos.run(topic, manuscript, stages)
        summary = run.summary()
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"pipeline acadêmico MASWOS: {topic}",
            reflection=f"MASWOS: {summary['stages_completed']}/{summary['stages_total']} "
                       f"estágios, nota final {summary['final_score']}/10 "
                       f"({'APROVADO' if summary['approved'] else 'reprovado'} no gate Qualis A1).",
            score=(summary["final_score"] or 0) / 10.0,
        )
        return summary

    def academic_pipeline_with_rigorous_board(
        self,
        topic: str,
        manuscript: str = "",
        venue: str = "auto",
        references: Optional[List[Dict[str, Any]]] = None,
        max_iter: int = 3,
        stages: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Pipeline MASWOS + Banca Rigorosa Multi-Periódico (R439) — sempre revisa e corrige antes de entregar.

        Fluxo: MASWOS (16 estágios) → Banca Rigorosa (3 revisores × 4 venues) →
        GapCleaningEngine (limpa TODO/ABNT/ética) → re-verificação até accept/minor
        ou max_iter. Só entrega se banca final não for reject/major persistente.
        """
        # Percepção metacognitiva: lições de bancas anteriores
        awareness = self.perceive(topic=f"banca_{venue}")

        run = self.maswos.run_with_rigorous_board(
            topic, manuscript, venue=venue, references=references, max_iter=max_iter, stages=stages
        )
        summary = run.summary()
        # Anexa dados da banca ao summary para transparência
        board_report = getattr(run, "board_report", None)
        if board_report:
            summary["board"] = board_report
            summary["board_iterations"] = getattr(run, "board_iterations", 1)
            summary["gaps_cleaned"] = getattr(run, "gaps_cleaned", 0)
            summary["final_manuscript"] = getattr(run, "final_manuscript", manuscript)[:8000]  # limita para serialização
            summary["board_score"] = getattr(run, "board_score", None)

        # Reflexão metacognitiva: banca rigorosa
        try:
            board_status = board_report.get("status", "unknown") if isinstance(board_report, dict) else "unknown"
            board_score = board_report.get("overall_score", 0) if isinstance(board_report, dict) else 0
            metabus.memory.add_reflection(
                agent_id=self.id,
                task_context=f"banca rigorosa {venue}: {topic[:60]}",
                reflection=(
                    f"Banca rigorosa {venue} ({summary.get('board_iterations',1)} iterações): "
                    f"{board_status} (score {board_score}/10), "
                    f"{summary.get('gaps_cleaned',0)} gaps limpos, "
                    f"MASWOS {summary['final_score']}/10 → "
                    f"{'ENTREGUE' if summary['approved'] else 'BLOQUEADO até correções'}."
                ),
                score=board_score / 10.0 if board_score else (summary["final_score"] or 0) / 10.0,
            )
            # Também registra no EvolutionRegistry via academic pipeline
            if summary.get("approved"):
                metabus.memory.upsert_semantic_topic(
                    f"academic.board.{venue}",
                    lesson=f"Banca {venue} aprovou '{topic[:40]}' com {board_score}/10 após {summary.get('board_iterations',1)} iterações.",
                    metadata={"venue": venue, "score": board_score, "gaps_cleaned": summary.get("gaps_cleaned", 0)},
                )
        except Exception:
            pass

        summary["lessons_considered"] = len(awareness.get("lessons", []))
        return summary

    # ------------------------------------------------------------------
    # FUSÃO DO PIPELINE CIENTÍFICO R101-R105 (SPEC-935-R108)
    # ------------------------------------------------------------------
    def scientific_discovery_pipeline(self, seed_domain: str, max_rounds: int = 3,
                                      venue: str = "abnt",
                                      strict_gates: bool = True) -> Dict[str, Any]:
        """Executa EvoSci → Deep Research → Peer Review → Revision → Composer.

        A implementação mantém as fronteiras dos cinco estágios, mas faz a
        orquestração no MarceloClaro: o gate de exportação do R103 é uma
        barreira real, as confidências são calibradas com evidência do run e
        a avaliação metacognitiva usa os próprios rastros da execução.
        Erros são retornados como dados estruturados; não há alegação de
        validação externa ou superioridade implícita.
        """
        from mci.confidence_calibrator import calibrate_confidence
        from mci.metacognitive_evaluator import MetacognitiveEvaluator, MetacognitiveTrace

        start = time.time()
        timeline: Dict[str, float] = {}
        stages: Dict[str, Any] = {}
        calibrated_confidences: Dict[str, Any] = {}
        traces: List[Any] = []

        def _calibrate(stage: str, raw_confidence: float,
                       succeeded: bool) -> Dict[str, Any]:
            claim: Dict[str, Any] = {}
            if not succeeded:
                claim["adversarial_findings"] = [
                    f"ALERTA: estágio {stage} não foi bem-sucedido",
                    f"CONFOUNDER: resultado do estágio {stage} não atingiu o critério",
                ]
            result = calibrate_confidence(
                claim=claim,
                context={
                    "reproducibility_score": max(0.0, min(1.0, raw_confidence)),
                    "actual_outcome": 1 if succeeded else 0,
                    "actual_verdict": "supported" if succeeded else "refuted",
                },
            )
            calibrated_confidences[stage] = result
            return result

        def _trace(stage: str, outcome: str, reflection: str,
                   before: float, after: float, evidence_count: int = 1,
                   abstained: bool = False,
                   error_type: Optional[str] = None) -> None:
            traces.append(MetacognitiveTrace(
                action_id=f"scientific_pipeline.{stage}",
                context=f"{stage} — {seed_domain[:60]}",
                outcome=outcome,
                reflection=reflection,
                confidence_before=before,
                confidence_after=after,
                strategy="scientific_discovery_pipeline",
                error_type=error_type,
                evidence_count=evidence_count,
                abstained=abstained,
            ))
            metabus.memory.add_reflection(
                agent_id=self.id,
                task_context=f"{stage}: {seed_domain[:80]}",
                reflection=reflection,
                score=after,
            )
            metabus.publish_subsystem_event(
                "scientific_pipeline", f"{stage}.completed",
                {"outcome": outcome, "confidence": after},
                source_agent=self.id,
            )
            self.trust.learn(
                f"scientific_pipeline:{stage}", success=(outcome == "success"),
            )

        try:
            # R101 — EvoSci
            t0 = time.time()
            from agentic_science_v2.orchestrator import run_agentic_science_v2
            r101 = run_agentic_science_v2(seed_domain=seed_domain, max_rounds=max_rounds)
            timeline["r101"] = round(time.time() - t0, 1)
            stages["r101"] = r101

            ideas = [
                idea
                for cycle in r101.get("history", [])
                for idea in cycle.get("ideas", [])
            ]
            best_idea = max(
                ideas,
                key=lambda item: (item.get("scores", {}) or {}).get("overall", 0.0),
            ) if ideas else {}
            best_content = (
                best_idea.get("hypothesis")
                or best_idea.get("title")
                or seed_domain
            )
            r101_confidence = float(
                (best_idea.get("scores", {}) or {}).get("overall", 0.0)
            ) if ideas else 0.0
            calibration = _calibrate("r101", r101_confidence, bool(ideas))
            _trace(
                "r101", "success" if ideas else "abstained",
                f"EvoSci gerou {len(ideas)} ideia(s); melhor score bruto "
                f"{r101_confidence:.2f}, calibrado "
                f"{calibration['calibrated_confidence']:.2f}.",
                before=r101_confidence,
                after=calibration["calibrated_confidence"],
                evidence_count=len(ideas),
                abstained=not ideas,
            )

            # R102 — Deep Research
            t1 = time.time()
            from agentic_science_v2.deep_research import run_deep_research
            r102 = run_deep_research(
                question=best_content,
                max_rounds=max_rounds,
                max_depth=3,
            )
            timeline["r102"] = round(time.time() - t1, 1)
            stages["r102"] = r102
            r102_reports = r102.get("reports", [])
            r102_failed = r102.get("status") == "error"
            r102_confidence = 0.0 if r102_failed else (
                float(r102_reports[-1].get("confidence", 0.5))
                if r102_reports else 0.5
            )
            calibration = _calibrate("r102", r102_confidence, not r102_failed)
            _trace(
                "r102", "failure" if r102_failed else "success",
                f"Deep research concluída com confiança bruta {r102_confidence:.2f}, "
                f"calibrada {calibration['calibrated_confidence']:.2f}.",
                before=r102_confidence,
                after=calibration["calibrated_confidence"],
                evidence_count=len(r102_reports),
                error_type="pipeline_error" if r102_failed else None,
            )

            # R103 — Peer Review
            t2 = time.time()
            from agentic_science_v2.review_agent import OrchestratorReviewer
            answer = r102_reports[-1].get("summary", "") if r102_reports else best_content
            review_package = OrchestratorReviewer().review({
                "title": seed_domain,
                "abstract": answer[:500],
                "sections": ["Introduction", "Methods", "Results", "Discussion", "Conclusion"],
                "citations": [],
            })
            r103 = review_package.to_dict()
            timeline["r103"] = round(time.time() - t2, 1)
            stages["r103"] = r103
            r103_confidence = float(r103.get("overall_score", 0.5))
            gate_passed = bool(r103.get("export_gate_passed", False))
            calibration = _calibrate("r103", r103_confidence, gate_passed)
            _trace(
                "r103", "success" if gate_passed else "blocked",
                f"Peer review: overall_score={r103_confidence:.2f}, "
                f"traceability={r103.get('traceability', 0)}, "
                f"coverage={r103.get('coverage', 0)}, "
                f"gate={'APROVADO' if gate_passed else 'REPROVADO'}.",
                before=r103_confidence,
                after=calibration["calibrated_confidence"],
                evidence_count=r103.get("critiques_count", 0),
                abstained=not gate_passed,
            )

            gate_decision = {
                "passed": gate_passed,
                "traceability": r103.get("traceability", 0),
                "coverage": r103.get("coverage", 0),
                "reason": (
                    "R103 export_gate_passed"
                    if gate_passed
                    else "R103 reprovou export_gate_passed (traceability/coverage abaixo do mínimo)"
                ),
            }

            if strict_gates and not gate_passed:
                timeline["total"] = round(time.time() - start, 1)
                metabus.publish_subsystem_event(
                    "scientific_pipeline", "gate.blocked",
                    gate_decision, source_agent=self.id,
                )
                metacog = MetacognitiveEvaluator().evaluate(traces)
                return {
                    "status": "blocked",
                    "reason": gate_decision["reason"],
                    "seed_domain": seed_domain,
                    "venue": venue,
                    "timeline": timeline,
                    "stages": stages,
                    "gate_decision": gate_decision,
                    "calibrated_confidences": calibrated_confidences,
                    "metacognitive_report": metacog,
                }

            # R104d — Revision
            t3 = time.time()
            from agentic_science_v2.revision_agent import create_revision
            manuscript_seed = answer or f"Manuscrito gerado automaticamente para {seed_domain}."
            r104d = create_revision(review_package.to_revision_contract(), manuscript_seed)
            timeline["r104d"] = round(time.time() - t3, 1)
            stages["r104d"] = r104d
            r104d_failed = r104d.get("status") == "error"
            r104d_report = r104d.get("report", {}) or {}
            r104d_confidence = float(r104d_report.get("traceability_pct", 0)) / 100.0
            calibration = _calibrate("r104d", r104d_confidence, not r104d_failed)
            _trace(
                "r104d", "failure" if r104d_failed else "success",
                f"Revisão de manuscrito: traceability_pct="
                f"{r104d_report.get('traceability_pct', 0)}, "
                f"integridade={r104d.get('integrity', {}).get('intact')}, "
                f"auto_rollback={r104d.get('integrity', {}).get('auto_rolled_back', False)}.",
                before=r104d_confidence,
                after=calibration["calibrated_confidence"],
                evidence_count=r104d_report.get("total_claims", 0),
                error_type="pipeline_error" if r104d_failed else None,
            )

            # R105 — Paper Composer
            t4 = time.time()
            revised_manuscript = manuscript_seed
            for revision in reversed(r104d.get("revisions", [])):
                proposal = revision.get("proposal") or {}
                if proposal.get("revised_text"):
                    revised_manuscript = proposal["revised_text"]
                    break
            r105 = compose_paper_core(
                title=seed_domain,
                discoveries=[best_idea] if best_idea else [],
                evidence_graph=r102.get("evidence_graph", {}),
                review=r103,
                revisions=r104d.get("revisions", []),
                venue=venue,
            )
            timeline["r105"] = round(time.time() - t4, 1)
            stages["r105"] = r105
            r105_failed = r105.get("status") == "error"
            r105_confidence = 0.0 if r105_failed else float(
                r105.get("consistency_report", {}).get("overall_score", 50)
            ) / 100.0
            calibration = _calibrate("r105", r105_confidence, not r105_failed)
            _trace(
                "r105", "failure" if r105_failed else "success",
                "Composição final: consistency "
                f"overall_score={r105.get('consistency_report', {}).get('overall_score', 'N/A')}.",
                before=r105_confidence,
                after=calibration["calibrated_confidence"],
                error_type="pipeline_error" if r105_failed else None,
            )

            # Auditoria de Rigor do Manuscrito (SPEC-935-R381)
            t5 = time.time()
            r105_sections = r105.get("sections") if not r105_failed else None
            manuscript_rigor_gate: Optional[Dict[str, Any]] = None
            if r105_sections:
                r381 = audit_scientific_manuscript(r105_sections)
                r381_high = any(
                    f.get("severity") == "high" for f in r381.get("findings", [])
                )
                r381_confidence = 0.0 if r381_high else 1.0
                calibration = _calibrate("r381", r381_confidence, not r381_high)
                _trace(
                    "r381", "failure" if r381_high else "success",
                    f"Auditoria de rigor (R369): {len(r381.get('moves_presentes', []))} "
                    f"movimentos presentes, {len(r381.get('findings', []))} achados, "
                    f"human_gate={r381.get('human_gate')}. Não bloqueia o pipeline "
                    "(consultivo, como R104d/R105).",
                    before=r381_confidence,
                    after=calibration["calibrated_confidence"],
                    evidence_count=len(r381.get("findings", [])),
                )
                manuscript_rigor_gate = {
                    "human_gate": r381.get("human_gate"),
                    "high_severity_findings": sum(
                        1 for f in r381.get("findings", []) if f.get("severity") == "high"
                    ),
                    "moves_ausentes": [
                        f["move"] for f in r381.get("findings", [])
                        if f.get("code") == "MISSING_MOVE" and f.get("move")
                    ],
                }
            else:
                r381 = {
                    "status": "skipped",
                    "reason": (
                        "R105 falhou ou não produziu seções compostas "
                        "(sections vazio/ausente) — auditoria de rigor não "
                        "fabricada sobre dado inexistente."
                    ),
                }
            timeline["r381"] = round(time.time() - t5, 1)
            stages["r381"] = r381

            timeline["total"] = round(time.time() - start, 1)
            metacog = MetacognitiveEvaluator().evaluate(traces)
            result = {
                "status": "completed",
                "seed_domain": seed_domain,
                "venue": venue,
                "timeline": timeline,
                "stages": stages,
                "gate_decision": gate_decision,
                "calibrated_confidences": calibrated_confidences,
                "metacognitive_report": metacog,
                "revised_manuscript": revised_manuscript,
            }
            if manuscript_rigor_gate is not None:
                result["manuscript_rigor_gate"] = manuscript_rigor_gate
            return result

        except Exception as exc:
            logger.exception("[%s] Falha no scientific_discovery_pipeline: %s", self.id, exc)
            _trace(
                "pipeline", "failure",
                f"Pipeline científico interrompido por exceção: {exc}",
                before=0.5,
                after=0.1,
                error_type="unhandled_exception",
            )
            timeline["total"] = round(time.time() - start, 1)
            metacog = MetacognitiveEvaluator().evaluate(traces)
            return {
                "status": "error",
                "error": str(exc),
                "seed_domain": seed_domain,
                "venue": venue,
                "timeline": timeline,
                "stages": stages,
                "calibrated_confidences": calibrated_confidences,
                "metacognitive_report": metacog,
            }

    # ------------------------------------------------------------------
    # LOOP ENGINEERING (SPEC-935-R109)
    # ------------------------------------------------------------------
    def describe_scientific_loop(self) -> Dict[str, Any]:
        """Expõe a especificação formal registrada para o loop científico."""
        loop = loop_spec_registry.get("scientific-discovery")
        return loop.to_dict() if loop else {}

    def run_scientific_discovery_loop(
        self,
        seed_domain: str,
        max_iterations: int = 5,
        stagnation_window: int = 3,
        stagnation_threshold: float = 0.02,
        venue: str = "abnt",
    ) -> Dict[str, Any]:
        """Repete o pipeline até um estado terminal explicitamente nomeado."""
        loop = loop_spec_registry.get("scientific-discovery")
        max_iterations = (
            max_iterations if max_iterations > 0
            else loop.max_iterations if loop else 5
        )
        start = time.time()
        readiness_history: List[float] = []
        iterations: List[Dict[str, Any]] = []
        terminal_state = "exhausted"
        reason = "Orçamento de iterações esgotado sem aprovar o gate."
        final_result: Dict[str, Any] = {}

        for iteration in range(1, max_iterations + 1):
            result = self.scientific_discovery_pipeline(
                seed_domain=seed_domain,
                max_rounds=3 + (iteration - 1),
                venue=venue,
                strict_gates=True,
            )
            final_result = result
            iterations.append({
                "iteration": iteration,
                "status": result.get("status"),
                "gate_passed": result.get("gate_decision", {}).get("passed"),
                "readiness_score": result.get("metacognitive_report", {}).get("readiness_score"),
            })
            metabus.publish_subsystem_event(
                "scientific_pipeline_loop", "iteration.completed",
                {"seed_domain": seed_domain, "iteration": iteration,
                 "status": result.get("status")},
                source_agent=self.id,
            )

            if result.get("status") == "error":
                terminal_state = "error"
                reason = f"Iteração {iteration} falhou com exceção não tratada: {result.get('error')}"
                break
            if result.get("status") == "completed":
                terminal_state = "success"
                reason = f"Gate aprovado e pipeline completo na iteração {iteration}."
                break

            r101_ideas = [
                idea
                for cycle in result.get("stages", {}).get("r101", {}).get("history", [])
                for idea in cycle.get("ideas", [])
            ]
            if not r101_ideas:
                terminal_state = "no_op"
                reason = (
                    f"EvoSci não gerou nenhuma ideia na iteração {iteration} — "
                    "nenhum trabalho genuíno a repetir."
                )
                break

            readiness = result.get("metacognitive_report", {}).get("readiness_score")
            if readiness is not None:
                readiness_history.append(float(readiness))
            if is_stagnant(
                readiness_history,
                window=stagnation_window,
                threshold=stagnation_threshold,
            ):
                terminal_state = "stalled"
                reason = (
                    f"readiness_score estagnado nas últimas {stagnation_window} iterações "
                    f"(variação < {stagnation_threshold}): "
                    f"{readiness_history[-stagnation_window:]}."
                )
                break

            if iteration == max_iterations:
                terminal_state = "blocked"
                reason = (
                    f"Gate do R103 nunca foi aprovado em {max_iterations} iterações "
                    "(orçamento esgotado por qualidade, não por estagnação)."
                )

        duration = round(time.time() - start, 1)
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"loop científico: {seed_domain[:80]}",
            reflection=(
                f"Loop terminou em '{terminal_state}' após {len(iterations)} "
                f"iteração(ões): {reason}"
            ),
            score={
                "success": 1.0, "no_op": 0.5, "blocked": 0.3,
                "stalled": 0.2, "error": 0.0,
            }.get(terminal_state, 0.0),
        )
        metabus.publish_subsystem_event(
            "scientific_pipeline_loop", "loop.terminal",
            {"seed_domain": seed_domain, "terminal_state": terminal_state,
             "iterations": len(iterations)},
            source_agent=self.id,
        )
        self.trust.learn(
            "scientific_discovery_loop", success=(terminal_state == "success"),
        )
        return {
            "terminal_state": terminal_state,
            "reason": reason,
            "iterations_used": len(iterations),
            "max_iterations": max_iterations,
            "readiness_history": readiness_history,
            "iterations": iterations,
            "final_result": final_result,
            "duration_seconds": duration,
        }

    def _maswos_delegate(self, agent_id: str, capability: str, description: str) -> str:
        """Delegação interna dos estágios MASWOS via Blackboard."""
        task_id = self.delegate(description, required_capabilities=[capability])
        task = blackboard.tasks.get(task_id)
        assigned = getattr(task, "assigned_to", None) or agent_id
        output = f"[{assigned}] estágio executado: {description[:120]}"
        self.report_completion(task_id, assigned, output, success=True)
        return output

    def reason(self, query: str, engine: str = "auto", **kwargs) -> Dict[str, Any]:
        """Raciocínio formal com os 4 motores (Z3, SymPy, Kanren, Critical)."""
        result = multi_reasoning.reason(query, engine=engine, **kwargs)
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"raciocínio ({result.engine}): {query[:80]}",
            reflection=f"Conclusão: {result.conclusion[:200]}",
            score=result.confidence,
        )
        return result.to_dict()

    def quantum_experiment(self, n_qubits: int = 3,
                           seeds: Optional[List[int]] = None,
                           shots: int = 1024) -> Dict[str, Any]:
        """Suite quântica reprodutível (Bell, GHZ, superposição) com 5 seeds."""
        report = run_experiment_suite(n_qubits, seeds, shots)
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"experimento quântico ({n_qubits} qubits)",
            reflection=f"Suite quântica concluída com seeds {report['seeds']}.",
            score=0.9,
        )
        return report

    def record_evolution(self, objective: str, changes: List[str],
                         score: Optional[float] = None,
                         lessons: Optional[List[str]] = None) -> Dict[str, Any]:
        """Registra um ciclo evolutivo (R47+) e injeta lições na memória global."""
        cycle = evolution_registry.record(objective, changes, score, lessons)
        for lesson in (lessons or []):
            metabus.memory.add_reflection(
                agent_id=self.id,
                task_context=f"ciclo evolutivo {cycle.round_id}",
                reflection=lesson,
                score=(score or 5.0) / 10.0,
            )
        return {"round_id": cycle.round_id, "score": cycle.score,
                "avg_score": evolution_registry.average_score()}

    def delegate_external(self, prompt: str, agent: str = "default") -> Dict[str, Any]:
        """Delegação externa via Antigravity CLI (SPEC-046), com fila de handoff."""
        return antigravity_bridge.delegate(prompt, agent=agent)

    # ------------------------------------------------------------------
    # MIROFISH — ENXAME PREDITIVO (inspiração: MarceloClaro/MiroFish)
    # ------------------------------------------------------------------
    @property
    def swarm_validator(self):
        """CrossValidator MiroFish com carregamento tardio (lazy)."""
        if self._swarm_validator is None:
            from mirofish import CrossValidator
            self._swarm_validator = CrossValidator(n_agents=25, seed=42)
        return self._swarm_validator

    def swarm_predict(self, question: str, signal: float = 0.5) -> Dict[str, Any]:
        """Previsão por enxame MiroFish (wisdom of crowds ponderada)."""
        result = self.swarm_validator.swarm.debate(question, rounds=3, signal=signal)
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"previsão de enxame MiroFish: {question[:80]}",
            reflection=(
                f"Enxame convergiu em {result['final']:.2f} "
                f"({'convergente' if result['converged'] else 'divergente'}) "
                f"após {result['rounds']} rodadas."
            ),
            score=result["final"],
        )
        return result

    def swarm_validate(self, question: str, signal: float = 0.5) -> Dict[str, Any]:
        """Validação cruzada tripla: enxame MiroFish × equilíbrio de Nash × Qualis."""
        verdict = self.swarm_validator.validate_decision(question, signal=signal)
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"validação cruzada MiroFish: {question[:80]}",
            reflection=f"Veredito: {'APROVADO' if verdict['approved'] else 'reprovado'} — "
                       f"{verdict['rationale']}.",
            score=1.0 if verdict["approved"] else 0.3,
        )
        return verdict

    # ------------------------------------------------------------------
    # TEORIA DOS JOGOS — 38 RACIOCÍNIOS (agent-forum portado)
    # ------------------------------------------------------------------
    def meta_reason(self, topic: str) -> Dict[str, Any]:
        """Seleciona dinamicamente os tipos de raciocínio (38) para o contexto,
        incluindo os 10+ modelos de Teoria dos Jogos (Nash, Shapley, Tit-for-Tat...)."""
        from gametheory import MetaReasoner
        reasoner = MetaReasoner()
        selected = reasoner.select_for_context({"topic": topic})
        names = [s.name for s in selected]
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"meta-raciocínio para: {topic[:80]}",
            reflection=f"Estratégias selecionadas: {', '.join(names[:8])}.",
            score=0.8,
        )
        return {"topic": topic, "strategies": names, "count": len(names)}

    def nash_analysis(self, game: str = "prisoners_dilemma", **kwargs) -> Dict[str, Any]:
        """Análise de equilíbrio de Nash para jogos 2×2 clássicos."""
        from gametheory import PayoffMatrix
        factory = getattr(PayoffMatrix, game, None)
        matrix = factory(**kwargs) if callable(factory) else PayoffMatrix.prisoners_dilemma()
        equilibria = matrix.find_nash_equilibria()
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"análise de Nash: {game}",
            reflection=f"Equilíbrios puros encontrados: {equilibria}.",
            score=0.9,
        )
        return {"game": game, "equilibria": equilibria}

    # ------------------------------------------------------------------
    # PRODUÇÃO CIENTÍFICA — PASTA ÚNICA (LaTeX + PDF + DOCX + MD + ODT/KDP)
    # ------------------------------------------------------------------
    def produce_scientific_work(self, title: str, content: str,
                                template: str = "artigo",
                                author: str = "Prof. Marcelo Claro") -> Dict[str, Any]:
        """
        Gera a pasta única de produção científica com fonte LaTeX (template
        Qualis A1/ABNT/livro) e compilados PDF, DOCX, MD e ODT (Amazon KDP),
        com manifesto auditável (checksums SHA-256).
        """
        from publishing import ScientificProduction
        production = ScientificProduction(title=title, template=template, author=author)
        manifest = production.build(content)
        generated = [f for f, info in manifest["formats"].items() if info]
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"produção científica: {title[:80]} (template {template})",
            reflection=(
                f"Pasta única gerada em {manifest['slug']} com formatos "
                f"{', '.join(generated)}; KDP-ready: {manifest['kdp_ready']}."
            ),
            score=len(generated) / 4.0,
        )
        return manifest

    # ------------------------------------------------------------------
    # RESEARCH — BUSCA E EXTRAÇÃO ACADÊMICA (SPEC-017)
    # ------------------------------------------------------------------
    def research_search(self, topic: str, platforms: Optional[List[str]] = None,
                        limit_per_platform: int = 5) -> List[Dict[str, Any]]:
        """Busca federada em plataformas acadêmicas (arXiv, OpenAlex, Crossref,
        Semantic Scholar, Europe PMC) e repositórios (GitHub, Kaggle),
        retornando registros deduplicados ordenados por aderência ao tema."""
        from research import MultiSearcher, CriticalAnalyzer
        searcher = MultiSearcher(platforms=platforms)
        analyzer = CriticalAnalyzer(topic)
        records = searcher.search(topic, limit_per_platform=limit_per_platform)
        ranked = sorted(records,
                        key=lambda r: analyzer.analyze(r).aderencia_score,
                        reverse=True)
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"busca acadêmica: {topic[:80]}",
            reflection=f"{len(ranked)} registros encontrados nas plataformas "
                       f"{platforms or 'todas'}.",
            score=min(1.0, len(ranked) / 10.0),
        )
        return [r.to_dict() for r in ranked]

    def research(self, topic: str, production_folder: Optional[str] = None,
                 max_papers: int = 8, platforms: Optional[List[str]] = None,
                 download: bool = True, use_llm: bool = False,
                 llm_provider: str = "auto",
                 llm_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Pipeline completo de revisão de literatura (SPEC-017):
        busca multiplataforma → download de PDFs (scihub-cli/OA direto) →
        conversão PDF→Markdown na subpasta `pesquisa/md/` → fichamento em três
        camadas + resenha crítica (ABNT NBR 6023:2018/10520:2023 e APA 7) →
        referências consolidadas (.md ABNT/APA + .bib) → manifest auditável.

        Se `production_folder` for a pasta única de uma produção científica
        existente (produce_scientific_work), a pesquisa é anexada a ela.

        Com ``use_llm=True``, fichamentos/resenhas são enriquecidos por LLM
        com prioridade para **modelos locais via Ollama** (``llm_provider=
        'auto'|'ollama'|'openai'``; ``llm_model`` ex.: ``llama3.2``).
        """
        from research import ResearchHub
        hub = ResearchHub(topic, production_folder=production_folder,
                          platforms=platforms)
        manifest = hub.run(max_papers=max_papers, download=download,
                           use_llm=use_llm, llm_provider=llm_provider,
                           llm_model=llm_model)
        resumo = manifest["resumo"]
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"pipeline de pesquisa: {topic[:80]}",
            reflection=(
                f"Pesquisa concluída: {resumo['artigos_selecionados']} artigos, "
                f"{resumo['pdfs_baixados']} PDFs, {resumo['convertidos_md']} MDs, "
                f"{resumo['fichamentos']} fichamentos e {resumo['resenhas']} "
                f"resenhas críticas em ABNT/APA na pasta {hub.folder}."
            ),
            score=min(1.0, resumo["fichamentos"] / max(1, max_papers)),
        )
        manifest["folder"] = str(hub.folder)
        return manifest

    # ==================================================================
    # Ilustrações científicas (SPEC-018): Mermaid + Graphify + MIRA
    # ==================================================================
    def illustrate(self, production_folder: str,
                   sections: Optional[Dict[str, str]] = None,
                   outline: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Gera as ilustrações da produção científica na subpasta `ilustracoes/`:
        diagrama Mermaid do outline (renderizado em PNG quando possível),
        grafo de conhecimento Graphify (graph.html + GRAPH_REPORT.md) e
        cards MIRA animados (metáforas visuais em loop perpetuo) por seção.
        """
        from pathlib import Path as _P
        from illustrations import MermaidEngine, GraphifyEngine, MiraEngine
        folder = _P(production_folder)
        illus = folder / "ilustracoes"
        report: Dict[str, Any] = {"folder": str(illus)}

        # 1. Mermaid: estrutura lógica do manuscrito
        me = MermaidEngine(output_dir=str(illus))
        if outline and len(outline) >= 2:
            fig = me.from_outline("Estrutura do Manuscrito", outline)
            me.render(fig)
            report["mermaid"] = fig.image_path or fig.mmd_path

        # 2. Graphify: grafo de conhecimento (manuscrito + fichamentos)
        texts: Dict[str, str] = dict(sections or {})
        for md in list(folder.rglob("pesquisa/md/*.md"))[:6]:
            try:
                texts[md.stem] = md.read_text(encoding="utf-8", errors="ignore")[:20000]
            except OSError:
                continue
        if texts:
            ge = GraphifyEngine(output_dir=str(illus / "grafo"))
            graph = ge.build(texts)
            report["graphify"] = ge.export(graph)
            report["graph_stats"] = {"nodes": len(graph.nodes), "edges": len(graph.edges)}

        # 3. MIRA: metáforas animadas por seção
        if sections:
            mi = MiraEngine(output_dir=str(illus / "mira"))
            cards = mi.illustrate_sections(sections)
            report["mira_cards"] = [c.html_path for c in cards]

        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"ilustrações da produção {folder.name[:60]}",
            reflection=(
                f"Ilustrações geradas: mermaid={bool(report.get('mermaid'))}, "
                f"grafo={report.get('graph_stats')}, "
                f"cards MIRA={len(report.get('mira_cards', []))}."
            ),
            score=0.8,
        )
        return report

    def present(self, production_folder: str) -> Dict[str, Any]:
        """Gera a apresentação MIRA direta de ``manuscrito.md``."""
        from pathlib import Path as _P
        from illustrations import MiraDeckPipeline

        folder = _P(production_folder)
        manuscript = folder / "manuscrito.md"
        if not manuscript.exists():
            metabus.memory.add_reflection(
                agent_id=self.id,
                task_context=f"apresentação MIRA de {folder.name[:60]}",
                reflection="manuscrito.md ausente — nada a apresentar.",
                score=0.2,
            )
            return {"ok": False, "error": f"manuscrito.md não encontrado em {folder}"}

        markdown = manuscript.read_text(encoding="utf-8", errors="ignore")
        output = folder / "apresentacao"
        report = MiraDeckPipeline().run(markdown, str(output))
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"apresentação MIRA de {folder.name[:60]}",
            reflection=(
                f"Deck gerado em {output}/deck.html — conformidade="
                f"{'OK' if report.passed else 'FALHOU'}, "
                f"{len(report.violations)} violação(ões)."
            ),
            score=0.85 if report.passed else 0.4,
        )
        return {
            "ok": True,
            "passed": report.passed,
            "deck": str(output / "deck.html"),
            "conformidade": str(output / "CONFORMIDADE.md"),
            "violations": report.violations,
        }

    def register_mira_agent(self) -> str:
        """Registra de forma idempotente o executor MIRA no Blackboard."""
        from illustrations.mira_agent import MiraPresentationAgent, MIRA_AGENT_ID

        if MIRA_AGENT_ID in blackboard.registry:
            if self._mira_agent is None:
                self._mira_agent = MiraPresentationAgent()
            return MIRA_AGENT_ID
        self._mira_agent = MiraPresentationAgent()
        metabus.publish(
            "agent.register",
            self._mira_agent.register_payload(),
            source_agent=self.id,
        )
        return MIRA_AGENT_ID

    def present_task(self, production_folder: str) -> Dict[str, Any]:
        """Executa apresentação pela via delegada do Blackboard."""
        from pathlib import Path as _P
        from illustrations.mira_agent import MIRA_AGENT_ID

        self.register_mira_agent()
        task_id = self.delegate(
            f"Apresentação MIRA da produção {_P(production_folder).name[:60]}",
            required_capabilities=["apresentacao-mira"],
            context={"production_folder": production_folder},
        )
        result = self._mira_agent.execute({"production_folder": production_folder})
        success = bool(result.get("ok")) and bool(result.get("passed", False))
        self.report_completion(task_id, MIRA_AGENT_ID, result, success=success)
        return {"task_id": task_id, "agent_id": MIRA_AGENT_ID, **result}

    def knowledge_graph(self, texts: Dict[str, str],
                        output_dir: str = "ilustracoes/grafo") -> Dict[str, Any]:
        """Constrói o grafo de conhecimento Graphify de textos arbitrários."""
        from illustrations import GraphifyEngine
        ge = GraphifyEngine(output_dir=output_dir)
        graph = ge.build(texts)
        paths = ge.export(graph)
        return {"paths": paths, "nodes": len(graph.nodes), "edges": len(graph.edges)}

    def hunt_figures(self, production_folder: str,
                     papers_meta: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Extrai figuras reais dos PDFs da produção (`pesquisa/pdfs/`) para
        `pesquisa/imagens/`, com catálogo FONTES.md (ABNT NBR 6023:2018 +
        APA 7) e blocos LaTeX prontos com citação da fonte na legenda.
        """
        from research.figure_hunter import FigureHunter
        hunter = FigureHunter()
        figs = hunter.harvest_production(production_folder, papers_meta)
        catalog = str(hunter.images_dir / "FONTES.md") if figs else ""
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"extração de figuras reais: {production_folder[:60]}",
            reflection=f"{len(figs)} figuras extraídas com fonte ABNT/APA em {catalog or 'nenhuma'}.",
            score=min(1.0, 0.5 + 0.1 * len(figs)),
        )
        return {"figuras": len(figs), "catalogo": catalog,
                "imagens": [f.image_path for f in figs]}

    def synthetic_university(
        self,
        target_combinations: int = 1000,
        generate_theses: bool = True,
    ) -> Dict[str, Any]:
        """
        Executa a Universidade Sintética Transversal (SPEC-935).

        Usa MiroFish-powered combinatorial engine para testar 10.000+
        combinações de conceitos entre 10 faculdades, descobrir correlações
        interdisciplinares e gerar teses PhD-level.

        Args:
            target_combinations: Número alvo de combinações a testar.
            generate_theses: Se deve gerar teses a partir das descobertas.

        Returns:
            Dict com summary, relatório e CV da universidade.
        """
        university = SyntheticUniversity(target_combinations=target_combinations)

        # Conectar eventos ao MetaBus
        def _on_university_event(event_type: str, data: dict):
            try:
                metabus.publish_subsystem_event(
                    "synthetic_university", event_type, data
                )
                # Atualizar memória semântica
                if event_type in ("cycle.complete", "theses.ready"):
                    metabus.memory.upsert_semantic_topic(
                        f"synthetic_university.{event_type}",
                        f"{data.get('report', data).get('theses', 0)} teses geradas",
                        {"timestamp": time.time(), "data": data},
                    )
            except Exception:
                pass

        university.on_event(_on_university_event)

        # Registrar evolução
        self.record_evolution(
            objective=f"Universidade Sintética: {target_combinations} combinações",
            changes=[
                f"Motor combinatorial: {target_combinations} combinações",
                "Correlações interdisciplinares" if generate_theses else "Apenas combinações",
                "Teses PhD-level geradas" if generate_theses else "",
            ],
            score=9.0,
        )

        # Executar ciclo
        report = university.run_full_cycle(
            target_combinations=target_combinations,
            generate_theses=generate_theses,
        )

        # Registrar reflexão
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"Universidade Sintética: {target_combinations} combinações, "
                         f"{report.theses_generated} teses",
            reflection=(
                f"Ciclo completo: {report.combinations_tested} combinações testadas, "
                f"{report.correlations_found} correlações descobertas, "
                f"{report.theses_generated} teses geradas, "
                f"{report.graph_nodes} nós no grafo de conhecimento. "
                f"Duração: {report.duration_s:.1f}s."
            ),
            score=min(1.0, 0.5 + 0.1 * min(report.theses_generated, 5)),
        )

        return {
            "summary": university.get_summary(),
            "report": {
                "combinations_tested": report.combinations_tested,
                "correlations_found": report.correlations_found,
                "theses_generated": report.theses_generated,
                "graph_nodes": report.graph_nodes,
                "graph_edges": report.graph_edges,
                "duration_s": report.duration_s,
            },
            "curriculum_vitae": university.get_curriculum_vitae(),
            "top_theses": [
                {
                    "title": t.title,
                    "level": t.academic_level.value,
                    "score": t.composite_score,
                    "faculties": list(t.faculties_involved),
                }
                for t in report.top_theses[:5]
            ],
            "top_correlations": [
                {
                    "concepts": list(c.concepts),
                    "type": c.correlation_type.value,
                    "strength": c.strength,
                }
                for c in report.top_correlations[:5]
            ],
        }

    def audit_and_certify(self, text: str = "Produção do Ecossistema OpenCode Core") -> Dict[str, Any]:
        """Audita, certifica e registra a integridade, orquestração e excelência de uma produção."""
        from scanners.pipeline import super_rigor_pipeline
        from benchmarks.internal_audit_harness import internal_audit_harness
        from benchmarks.merkle_integrity_guard import merkle_integrity_guard
        from integrations.cli_ecosystem_bridge import cli_ecosystem_bridge
        from benchmarks.standalone_readiness_eval import standalone_readiness_eval

        rigor = super_rigor_pipeline.audit_production(text)
        cert = internal_audit_harness.generate_audit_certificate(text)
        merkle = merkle_integrity_guard.compute_merkle_root()
        cli_status = cli_ecosystem_bridge.get_unified_status()
        standalone_status = standalone_readiness_eval.eval_standalone_readiness()

        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"auditoria super-rigor: {text[:60]}",
            reflection=(
                f"Auditoria concluída com EXS {rigor['excellence_score']:.1f} e "
                f"Certificado {cert['certificate_id']}. Merkle Root: {merkle['merkle_root'][:12]}... "
                f"Autonomia Standalone: {standalone_status['standalone_score']:.0f}%."
            ),
            score=rigor["excellence_score"] / 100.0,
        )

        return {
            "orchestrator_id": self.id,
            "excellence_score": rigor["excellence_score"],
            "passed": rigor["passed"],
            "rigor_audit": rigor,
            "certificate": cert,
            "merkle_root": merkle["merkle_root"],
            "cli_ecosystem_bridge": cli_status,
            "standalone_readiness": standalone_status,
            "status": "certified_by_marceloclaro" if rigor["passed"] else "refinement_requested",
        }
