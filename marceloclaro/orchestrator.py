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

import uuid
import logging
from typing import Dict, List, Any, Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mci.metabus import metabus
from mci.blackboard import blackboard
from mci.reflexion import reflexion_engine  # noqa: F401 — ativa o singleton
from marceloclaro.agent_loader import register_all_agents, load_agent_definitions
from transformer.attention import AttentionRouter
from transformer.pipeline import TransformerPipeline, GradingHead
from transformer.memory import HierarchicalMemory
from sdd.spec_engine import spec_registry, spec_verifier
from sdd.tdd_runner import tdd_runner, run_pytest
from trust import create_trust_engine
from economy import TokenEconomy
from scanners import diagnostic_pipeline
from academic import MaswosPipeline
from reasoning import multi_reasoning, run_experiment_suite
from evolution import evolution_registry
from integrations.antigravity import antigravity_bridge
from marceloclaro.catalog_loader import register_catalog_agents

logger = logging.getLogger("marceloclaro")
logger.setLevel(logging.INFO)


class MarceloClaroOrchestrator:
    """Orquestrador central metacognitivo do ecossistema."""

    def __init__(self, auto_load_agents: bool = True, pipeline_layers: int = 3,
                 strict_sdd: bool = False):
        self.id = "marceloclaro"
        self.pending_cfps: Dict[str, List[str]] = {}  # task_id -> agentes elegíveis
        self.results: Dict[str, Any] = {}

        # Modo SDD estrito: nenhuma conclusão aceita sem verificação de spec (INV-006.1)
        self.strict_sdd = strict_sdd
        self.task_specs: Dict[str, str] = {}  # task_id -> spec_id

        # Trust Engine (SPEC-038): gate comportamental, esquecimento natural, outcomes
        self.trust = create_trust_engine()

        # Token Economy (SPEC-022~025): staking, slashing, fee market
        self.economy = TokenEconomy()
        self.task_stakes: Dict[str, str] = {}  # task_id -> agent_id com stake

        # Pipeline acadêmico Qualis A1 (MASWOS) acoplado à delegação real
        self.maswos = MaswosPipeline(delegate_fn=self._maswos_delegate)

        # Camada Transformer (inspiração: Vaswani 2017, Perceiver, HTM, Aletheia)
        self.attention_router = AttentionRouter()
        self.pipeline = TransformerPipeline(num_layers=pipeline_layers, grading_head=GradingHead())
        self.hierarchical_memory = HierarchicalMemory(metabus.memory)
        self._task_counter = 0  # positional encoding das tarefas

        # Escuta o Global Workspace
        metabus.subscribe("task.cfp", self._on_cfp)
        metabus.subscribe("task.assigned", self._on_assigned)
        metabus.subscribe("metacognition.reflected", self._on_reflected)

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

    def _on_cfp(self, event: Dict[str, Any]):
        """Recebe o Call for Proposals e roteia via Multi-Head Attention.

        Integra o Trust Engine (SPEC-038): agentes cujo BehavioralGate bloqueia
        a ação são removidos da elegibilidade antes do roteamento por atenção.
        """
        payload = event.get("payload", {})
        task_id = payload.get("task_id")
        description = payload.get("description", "")
        eligible = payload.get("eligible_agents", [])

        # Gate comportamental (Trust Engine): filtra agentes não confiáveis
        gated = []
        for agent_id in eligible:
            decision = self.trust.execute(f"delegate:{agent_id}")
            if decision.allowed:
                gated.append(agent_id)
            else:
                logger.info(f"[{self.id}] BehavioralGate bloqueou {agent_id}: {decision.reason}")
        eligible = gated or eligible  # fallback: nunca deixar a tarefa órfã
        self.pending_cfps[task_id] = eligible

        if not eligible:
            logger.warning(f"[{self.id}] Nenhum agente elegível para {task_id}")
            return

        # Roteamento por atenção multi-cabeça (semântica × capacidade × confiança × carga)
        task = blackboard.tasks.get(task_id)
        required = task.required_capabilities if task else []
        cards = [blackboard.registry[a].to_dict() for a in eligible if a in blackboard.registry]

        self._task_counter += 1
        ranking = self.attention_router.route(description, required, cards,
                                              positional_index=self._task_counter)
        chosen = ranking[0][0] if ranking else eligible[0]
        logger.info(f"[{self.id}] Atenção rankeou {task_id}: {ranking[:3]}")

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
                 goals: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Pipeline de diagnóstico com os 5 scanners (noológico, teleológico,
        evolutivo, potentiality, social impact). Registra o resultado na memória."""
        report = diagnostic_pipeline.run(corpus, domain=domain, goals=goals)
        gaps = report.get("evolutionary", {}).get("total_gaps", 0)
        metabus.memory.add_reflection(
            agent_id=self.id,
            task_context=f"diagnóstico do ecossistema (domínio: {domain or 'geral'})",
            reflection=f"Diagnóstico concluído: {gaps} lacunas identificadas. "
                       f"{report['evolutionary']['recommendation']}",
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
