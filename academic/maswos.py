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

    def summary(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "stages_completed": sum(1 for s in self.stages if s.status == "completed"),
            "stages_total": len(self.stages),
            "final_score": self.final_score,
            "approved": self.approved,
            "duration_s": round(time.time() - self.started_at, 2),
        }


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


# Singleton em modo standalone
maswos_pipeline = MaswosPipeline()
