# -*- coding: utf-8 -*-
"""
Transformer Pipeline — Encoder Stack com Gerar → Verificar → Revisar
====================================================================
Analogia Transformer: cada tarefa atravessa N camadas de encoder. Em cada
camada ocorre um ciclo completo inspirado no agente Aletheia (superhuman,
Gemini Deep Think): GERAR (executor) → VERIFICAR (GradingHead) → REVISAR
(nova rodada se a nota for insuficiente), com conexão residual (o contexto
original é preservado e enriquecido a cada camada).

O GradingHead pontua saídas em escala 0-7, inspirado no IMO-GradingBench
(superhuman/imobench), onde soluções recebem notas de banca.

Inspiração:
- Aletheia: generate → verify → revise (MarceloClaro/superhuman)
- IMO-GradingBench: avaliação graduada 0-7 (MarceloClaro/superhuman)
- Encoder stack / conexões residuais (Vaswani et al. 2017)

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import logging
from typing import Dict, List, Any, Callable, Optional

logger = logging.getLogger("transformer-pipeline")
logger.setLevel(logging.INFO)

MAX_SCORE = 7  # escala IMO-GradingBench


class GradingHead:
    """
    Cabeça de avaliação (output head). Pontua a saída de um agente em 0-7.
    Por padrão usa heurísticas verificáveis; pode ser substituída por um
    LLM-judge injetando `grader_fn`.
    """

    def __init__(self, grader_fn: Optional[Callable[[str, str], int]] = None):
        self.grader_fn = grader_fn

    def grade(self, task_description: str, output: str) -> Dict[str, Any]:
        if self.grader_fn:
            score = max(0, min(MAX_SCORE, int(self.grader_fn(task_description, output))))
        else:
            score = self._heuristic_grade(task_description, output)
        return {
            "score": score,
            "max_score": MAX_SCORE,
            "passed": score >= 5,  # nota de corte estilo medalha
            "normalized": round(score / MAX_SCORE, 3),
        }

    def _heuristic_grade(self, task_description: str, output: str) -> int:
        """Heurística verificável: completude, substância e ancoragem na tarefa."""
        if not output or not output.strip():
            return 0
        score = 2  # produziu algo
        if len(output.strip()) >= 40:
            score += 2  # substância mínima
        # Ancoragem: tokens da tarefa presentes na saída
        task_tokens = set(task_description.lower().split())
        out_tokens = set(output.lower().split())
        overlap = len(task_tokens & out_tokens)
        if overlap >= 2:
            score += 2
        if overlap >= 5:
            score += 1
        return min(score, MAX_SCORE)


class TransformerPipeline:
    """
    Encoder stack: processa uma tarefa em até `num_layers` camadas de
    gerar → verificar → revisar, com resíduos acumulados no contexto.
    """

    def __init__(self, num_layers: int = 3, grading_head: Optional[GradingHead] = None):
        self.num_layers = num_layers
        self.grading_head = grading_head or GradingHead()

    def run(self, task_description: str,
            executor_fn: Callable[[str, Dict[str, Any]], str],
            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa o pipeline.
        `executor_fn(prompt, context) -> output` é a função que gera a solução
        (um agente real, um LLM, ou uma simulação em testes).
        """
        residual_context: Dict[str, Any] = dict(context or {})
        residual_context.setdefault("revisions", [])
        best = {"output": "", "grade": {"score": -1}}

        for layer in range(1, self.num_layers + 1):
            # --- Sub-camada 1: GERAR (self-attention + FFN do encoder) ---
            prompt = task_description
            if residual_context["revisions"]:
                last = residual_context["revisions"][-1]
                prompt += (
                    f"\n[REVISÃO camada {layer}] Saída anterior obteve nota "
                    f"{last['grade']['score']}/{MAX_SCORE}. Corrija e melhore."
                )

            output = executor_fn(prompt, residual_context)

            # --- Sub-camada 2: VERIFICAR (GradingHead) ---
            grade = self.grading_head.grade(task_description, output)
            logger.info(f"Camada {layer}: nota {grade['score']}/{MAX_SCORE}")

            # --- Conexão residual: acumula histórico sem descartar o passado ---
            residual_context["revisions"].append({
                "layer": layer,
                "output": output,
                "grade": grade,
            })

            if grade["score"] > best["grade"]["score"]:
                best = {"output": output, "grade": grade}

            # --- Early exit: solução aprovada, não precisa revisar ---
            if grade["passed"]:
                break

        return {
            "final_output": best["output"],
            "final_grade": best["grade"],
            "layers_used": len(residual_context["revisions"]),
            "revisions": residual_context["revisions"],
        }
