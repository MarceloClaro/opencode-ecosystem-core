# -*- coding: utf-8 -*-
"""
Benchmark de Power Analysis.

Testa:
1. Cálculo de tamanho amostral
2. Relação entre poder, alpha, effect size e n
3. Poder pós-hoc
4. Trade-offs entre poder e custo
"""

from typing import Dict, Any, List, Optional, Callable
from .runner import BenchmarkResult, evaluate_pipeline_task


POWER_TASKS = [
    {
        "id": "power_01",
        "description": (
            "Para detectar d=0.5 com poder=0.80 e alpha=0.05 (bilateral), "
            "o n por grupo é aproximadamente 64. Se reduzirmos o poder para 0.60, "
            "o que acontece com o n necessário?"
        ),
        "options": [
            "a) Aumenta (precisamos de mais participantes)",
            "b) Diminui (precisamos de menos participantes)",
            "c) Permanece igual (n depende só do effect size)",
            "d) Não é possível determinar sem o desvio padrão",
        ],
        "correct": "b",
        "evaluation_criteria": (
            "Menor poder → menor n necessário (mas maior chance de falso negativo). "
            "Poder 0.80 é o mínimo aceito. Poder 0.60 é considerado inadequado."
        ),
    },
    {
        "id": "power_02",
        "description": (
            "Um estudo com n=30 por grupo encontra p=0.04, d=0.50. "
            "O poder pós-hoc calculado é aproximadamente 0.50. "
            "Qual a implicação?"
        ),
        "options": [
            "a) O resultado é confiável (p < 0.05)",
            "b) Alta probabilidade de falso positivo (Ioannidis, 2005)",
            "c) O efeito é superestimado (winner's curse)",
            "d) Tanto b quanto c são preocupações válidas",
        ],
        "correct": "d",
        "evaluation_criteria": (
            "Estudos com baixo poder que encontram significância tendem a: "
            "(1) superestimar o efeito verdadeiro (winner's curse) e "
            "(2) ter alta taxa de falsos positivos (Ioannidis 2005: "
            "'Why Most Published Research Findings Are False')."
        ),
    },
    {
        "id": "power_03",
        "description": (
            "Qual o efeito de dobrar o tamanho amostral no poder estatístico "
            "para detectar o mesmo effect size?"
        ),
        "options": [
            "a) O poder dobra",
            "b) O poder aumenta, mas não proporcionalmente",
            "c) O poder permanece igual (depende só do effect size)",
            "d) O poder diminui (mais ruído com mais dados)",
        ],
        "correct": "b",
        "evaluation_criteria": (
            "Poder é função monotônica crescente de n, mas não linear. "
            "A curva de poder é assintótica: dobrar n de 30 para 60 aumenta "
            "poder significativamente, mas de 300 para 600 tem efeito marginal."
        ),
    },
]


class PowerAnalysisBenchmark:
    """Benchmark de power analysis."""

    def __init__(self):
        self.tasks = POWER_TASKS

    def run(self, pipeline_fn=None) -> BenchmarkResult:
        details = []
        passed = 0

        for task in self.tasks:
            evaluation = evaluate_pipeline_task(task, pipeline_fn)
            result = {
                "task_id": task["id"],
                "description": task["description"],
                "correct_answer": task["correct"],
                "passed": evaluation["passed"],
                "mode": evaluation["mode"],
                "pipeline_response": evaluation["pipeline_response"],
                "evaluation": task["evaluation_criteria"],
            }
            if "error" in evaluation:
                result["error"] = evaluation["error"]
            details.append(result)
            if evaluation["passed"]:
                passed += 1

        return BenchmarkResult(
            name="Power Analysis",
            score=passed / len(self.tasks),
            tasks_total=len(self.tasks),
            tasks_passed=passed,
            details=details,
        )
