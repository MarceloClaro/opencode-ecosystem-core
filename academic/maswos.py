# -*- coding: utf-8 -*-
"""
MASWOS — Multi-Agent Scientific Writing Orchestration System
============================================================
Pipeline acadêmico Qualis A1 portado da arquitetura MASWOS v4 do
OpenCode_Ecosystem original (criador-artigo).

Orquestra os agentes MASWOS do catálogo (agents/catalog/00..21) em um
pipeline de produção científica em estágios, com gates de qualidade:

    Diagnóstico → Busca/Curadoria (SEEKER) → Estrutura → Redação por seção
    → Auditoria ABNT → QA Qualis A1 (AUTO_SCORE) → Entrega

Cada estágio delega ao agente correspondente via Blackboard (quando um
orquestrador é fornecido) ou executa validações locais (modo standalone).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from academic.auto_score_qualis import RUBRIC  # rubrica oficial de 10 critérios

# Palavras-chave para roteamento de artigos sobre infraestrutura cloud.
CLOUD_TOPIC_KEYWORDS = [
    "alloydb", "cloud sql", "bigquery", "dataflow", "composer",
    "dataproc", "spark", "gcp", "google cloud", "cloud infrastructure",
    "cloud computing", "big data", "data pipeline", "cloud database",
    "postgresql", "mysql", "sql server", "firestore", "spanner",
    "gcs", "cloud storage", "data lake", "data warehouse",
    "cloud migration", "cloud security", "cloud optimization",
    "infraestrutura em nuvem", "banco de dados cloud",
    "alloydb omni", "cloud data", "pipeline de dados",
]


# Pipeline canônico MASWOS: (estágio, agente do catálogo, capacidade)
MASWOS_STAGES = [
    ("diagnostico_escopo", "01_agente_diagnostico_escopo", "research"),
    ("busca_curadoria", "02_agente_busca_curadoria", "search"),
    ("evidencias_citacoes", "03_agente_evidencias_citacoes", "citations"),
    ("estrutura_argumentativa", "04_agente_estrutura_argumentativa", "academic_writing"),
    ("revisao_literatura", "05_agente_revisao_literatura_teoria", "literature_review"),
    ("metodologia", "06_agente_metodologia_reprodutibilidade", "methodology"),
    ("estatistica", "07_agente_estatistica_analise", "statistics"),
    ("visualizacao", "08_agente_visualizacao_evidencia_grafica", "visualization"),
    ("resultados", "09_agente_resultados", "academic_writing"),
    ("discussao", "10_agente_discussao_contribuicao", "argumentation"),
    ("conclusao", "11_agente_conclusao_coerencia_final", "academic_writing"),
    ("auditoria_abnt", "12_agente_auditoria_bibliografica_abnt", "abnt"),
    ("qa_qualis_a1", "13_agente_qa_qualis_a1", "qualis_a1"),
    ("consistencia", "14_agente_consistencia_interna", "verification"),
    ("abstract", "15_agente_resumo_abstract_palavras_chave", "academic_writing"),
    ("integracao_editorial", "16_agente_integracao_editorial_docx", "editorial"),
]

QUALITY_GATE_THRESHOLD = 8.0  # nota mínima (0-10) do AUTO_SCORE para aprovação


@dataclass
class StageResult:
    stage: str
    agent_id: str
    status: str = "pending"     # pending | completed | failed | skipped
    output: str = ""
    score: Optional[float] = None
    duration_s: float = 0.0


@dataclass
class MaswosRun:
    topic: str
    stages: List[StageResult] = field(default_factory=list)
    final_score: Optional[float] = None
    approved: bool = False
    started_at: float = field(default_factory=time.time)
    # R439 — banca rigorosa (opcionais, preenchidos por run_with_rigorous_board)
    manuscript: Optional[str] = None
    board_report: Optional[Dict[str, Any]] = None
    board_history: Optional[List[Dict[str, Any]]] = None
    final_manuscript: Optional[str] = None
    gaps_cleaned: Optional[int] = None
    board_iterations: Optional[int] = None
    board_score: Optional[float] = None
    board_error: Optional[str] = None

    def summary(self) -> Dict[str, Any]:
        base = {
            "topic": self.topic,
            "stages_completed": sum(1 for s in self.stages if s.status == "completed"),
            "stages_total": len(self.stages),
            "final_score": self.final_score,
            "approved": self.approved,
            "duration_s": round(time.time() - self.started_at, 2),
        }
        # Anexa dados da banca quando presentes (R439)
        if self.board_report is not None:
            base["board"] = self.board_report
        if self.board_history is not None:
            base["board_history"] = self.board_history
        if self.final_manuscript is not None:
            base["final_manuscript"] = self.final_manuscript[:8000]
        if self.gaps_cleaned is not None:
            base["gaps_cleaned"] = self.gaps_cleaned
        if self.board_iterations is not None:
            base["board_iterations"] = self.board_iterations
        if self.board_score is not None:
            base["board_score"] = self.board_score
        return base


class MaswosPipeline:
    """Pipeline MASWOS de produção científica Qualis A1.

    Args:
        delegate_fn: função opcional (agent_id, capacidade, descrição) -> saída str.
                     Quando fornecida (pelo orquestrador marceloclaro), cada
                     estágio é delegado ao agente real. Sem ela, o pipeline
                     roda em modo de planejamento (dry-run).
        score_fn: função opcional (manuscrito: str) -> float 0-10. Default: rubrica local.
    """

    def __init__(self,
                 delegate_fn: Optional[Callable[[str, str, str], str]] = None,
                 score_fn: Optional[Callable[[str], float]] = None):
        self.delegate_fn = delegate_fn
        self.score_fn = score_fn or self._heuristic_score

    def run(self, topic: str, manuscript: str = "",
            stages: Optional[List[str]] = None) -> MaswosRun:
        """Executa o pipeline completo (ou subconjunto de estágios)."""
        run = MaswosRun(topic=topic)
        selected = [s for s in MASWOS_STAGES
                    if stages is None or s[0] in stages]
        accumulated = manuscript
        for stage_name, agent_id, capability in selected:
            started = time.time()
            result = StageResult(stage=stage_name, agent_id=agent_id)
            try:
                if self.delegate_fn:
                    output = self.delegate_fn(
                        agent_id, capability,
                        f"[MASWOS:{stage_name}] Tópico: {topic}. "
                        f"Contexto atual: {accumulated[-2000:] if accumulated else '(início)'}"
                    )
                    result.output = output or ""
                    accumulated += f"\n\n## [{stage_name}]\n{result.output}"
                    result.status = "completed"
                else:
                    result.status = "skipped"
                    result.output = f"(dry-run) delegaria a {agent_id} ({capability})"
            except Exception as exc:
                result.status = "failed"
                result.output = f"erro: {exc}"
            result.duration_s = round(time.time() - started, 3)
            run.stages.append(result)

        # Quality gate final: AUTO_SCORE_QUALIS
        run.final_score = round(self.score_fn(accumulated or topic), 2)
        run.approved = run.final_score >= QUALITY_GATE_THRESHOLD
        # Anexa manuscrito acumulado para uso pela banca rigorosa
        run.manuscript = accumulated  # type: ignore
        return run

    def run_with_rigorous_board(
        self,
        topic: str,
        manuscript: str = "",
        venue: str = "auto",
        references: Optional[List[Dict[str, Any]]] = None,
        max_iter: int = 3,
        stages: Optional[List[str]] = None,
    ) -> MaswosRun:
        """Pipeline com banca rigorosa multi-periódico obrigatória antes da entrega.

        Executa o pipeline canônico e, antes de aprovar, submete o manuscrito
        à banca rigorosa (CAPES/Nature/IEEE/Lancet) com loop de correção e
        limpeza de gaps. Só aprova se a banca final for accept/minor_revision.
        """
        # 1. Pipeline canônico
        run = self.run(topic, manuscript, stages=stages)
        # Usa manuscrito acumulado se existir
        base_manuscript = getattr(run, "manuscript", manuscript) or manuscript or topic

        # 2. Banca rigorosa com correção
        try:
            from academic.rigorous_board import RigorousBoard

            board = RigorousBoard()
            loop_result = board.correction_loop(base_manuscript, venue=venue, references=references, max_iter=max_iter)
            final_decision = loop_result["final_decision"]
            final_manuscript = loop_result["final_manuscript"]

            # Anexa resultado da banca ao run
            run.board_report = final_decision.to_dict()  # type: ignore
            run.board_history = loop_result["history"]  # type: ignore
            run.final_manuscript = final_manuscript  # type: ignore
            run.gaps_cleaned = loop_result["gaps_cleaned"]  # type: ignore
            run.board_iterations = loop_result["iterations"]  # type: ignore

            # Só aprova se banca não for reject/major persistente
            board_approved = final_decision.status in ("accept", "minor_revision")
            # Mantém approved original apenas se banca também aprovar
            run.approved = bool(run.approved and board_approved)
            # Se banca rejeitou mas pipeline aprovou, força reprovação honesta
            if not board_approved and run.final_score >= QUALITY_GATE_THRESHOLD:
                run.approved = False

            # Atualiza final_score para refletir board se for menor (não infla)
            run.board_score = final_decision.overall_score  # type: ignore
            if final_decision.overall_score < run.final_score:
                # Mantém o menor como sinal honesto
                pass

            # Publica no MetaBus
            try:
                from mci.metabus import metabus

                metabus.publish_subsystem_event(
                    "academic",
                    "rigorous_board.completed",
                    {
                        "topic": topic,
                        "venue": venue,
                        "iterations": loop_result["iterations"],
                        "final_status": final_decision.status,
                        "overall_score": final_decision.overall_score,
                        "gaps_cleaned": loop_result["gaps_cleaned"],
                    },
                    source_agent="maswos_rigorous_board",
                )
                metabus.memory.add_reflection(
                    agent_id="maswos_pipeline",
                    task_context=f"banca rigorosa {venue}: {topic[:60]}",
                    reflection=(
                        f"Banca {venue} concluiu {loop_result['iterations']} iteração(ões): "
                        f"{final_decision.status} (score {final_decision.overall_score}/10), "
                        f"{len(final_decision.gaps)} gaps, {loop_result['gaps_cleaned']} limpos."
                    ),
                    score=final_decision.overall_score / 10.0,
                )
            except Exception:
                pass

        except Exception as exc:
            # Falha da banca não deve derrubar pipeline — registra e mantém decisão original
            run.board_error = str(exc)  # type: ignore

        return run

    @staticmethod
    def _heuristic_score(manuscript: str) -> float:
        """Nota heurística local (0-10) baseada na rubrica AUTO_SCORE_QUALIS.

        Usa presença de sinais estruturais no manuscrito, um por critério
        da rubrica oficial, como aproximação do scorer completo.
        """
        text = (manuscript or "").lower()
        signals = {
            "rigor_academico": ["metodologia", "hipótese", "teoria", "fundament"],
            "densidade_citacoes": ["doi", "(20", "et al", "referênc"],
            "abnt_compliance": ["abnt", "referências", "p. "],
            "originalidade": ["contribuição", "lacuna", "inédit", "original"],
            "metodologia": ["amostra", "procedimento", "reprodutib", "protocolo"],
            "analise_estatistica": ["p-valor", "estatístic", "intervalo de confiança", "anova"],
            "coerencia": ["introdução", "conclusão", "objetivo"],
            "qualidade_visual": ["figura", "tabela", "gráfico"],
            "internacionalizacao": ["abstract", "keywords"],
            "autocontencao": [],  # avaliado por tamanho
        }
        total_weight = sum(c["peso"] for c in RUBRIC.values())
        earned = 0.0
        for criterion, spec in RUBRIC.items():
            weight = spec["peso"]
            keys = signals.get(criterion, [])
            if criterion == "autocontencao":
                ratio = min(1.0, len(text) / 20000.0)
            elif keys:
                hits = sum(1 for k in keys if k in text)
                ratio = hits / len(keys)
            else:
                ratio = 0.5
            earned += weight * ratio
        return 10.0 * earned / total_weight


# Pipeline especializado para artigos de infraestrutura cloud.
CLOUD_STAGES = [
    ("cloud_diagnostico", "cloud-data-infra-generalist", "cloud_assessment"),
    ("cloud_arquitetura", "cloud-data-pipelines-specialist", "cloud_architecture"),
    ("cloud_seguranca", "cloud-security-specialist", "cloud_security"),
    ("cloud_banco_dados", "cloud-alloydb-specialist", "cloud_database"),
    ("cloud_bigquery_analytics", "cloud-bigquery-specialist", "cloud_analytics"),
    ("cloud_implementacao", "cloud-data-pipelines-specialist", "cloud_implementation"),
    ("cloud_otimizacao", "cloud-sql-postgres-specialist", "cloud_optimization"),
    ("cloud_revisao_tecnicas", "cloud-sql-mysql-specialist", "cloud_review"),
]


def is_cloud_topic(topic: str) -> bool:
    """Retorna se o tópico contém sinais de infraestrutura cloud."""
    normalized_topic = topic.casefold()
    return any(keyword in normalized_topic for keyword in CLOUD_TOPIC_KEYWORDS)


def run_maswos_cloud(
    topic: str,
    manuscript: str = "",
    delegate_fn: Optional[Callable[[str, str, str], str]] = None,
) -> MaswosRun:
    """Executa o pipeline cloud ou delega ao MASWOS padrão.

    Sem ``delegate_fn``, nenhum agente externo é chamado: os oito estágios
    cloud são marcados como ``skipped`` para manter o dry-run seguro.
    Tópicos não-cloud seguem exatamente o pipeline canônico, sem prefixo no
    tópico.
    """
    pipeline = MaswosPipeline(delegate_fn=delegate_fn)

    if not is_cloud_topic(topic):
        return pipeline.run(topic, manuscript)

    run = MaswosRun(topic=f"[CLOUD] {topic}")
    accumulated = manuscript
    for stage_name, agent_id, capability in CLOUD_STAGES:
        started = time.time()
        result = StageResult(stage=stage_name, agent_id=agent_id)
        try:
            if delegate_fn:
                output = delegate_fn(
                    agent_id,
                    capability,
                    f"[MASWOS-CLOUD:{stage_name}] Tópico cloud: {topic}. "
                    f"Skills de referência em scripts/cloud/. "
                    f"Contexto: {accumulated[-2000:] if accumulated else '(início)'}",
                )
                result.output = output or ""
                accumulated += f"\n\n## [{stage_name}]\n{result.output}"
                result.status = "completed"
            else:
                result.status = "skipped"
                result.output = (
                    f"(dry-run) delegaria a {agent_id} ({capability}) "
                    "com skills cloud"
                )
        except Exception as exc:
            result.status = "failed"
            result.output = f"erro: {exc}"
        result.duration_s = round(time.time() - started, 3)
        run.stages.append(result)

    run.final_score = round(pipeline.score_fn(accumulated or topic), 2)
    run.approved = run.final_score >= QUALITY_GATE_THRESHOLD
    return run


# Singleton em modo standalone
maswos_pipeline = MaswosPipeline()
