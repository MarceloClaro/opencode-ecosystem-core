# -*- coding: utf-8 -*-
"""
Benchmark de Interpretação Estatística.

Testa:
1. Interpretação correta de p-valor
2. Intervalos de confiança
3. Tamanho de efeito vs. significância
4. Bayes Factor
5. Múltiplas comparações
6. Poder estatístico
"""

from typing import Dict, Any, List, Optional, Callable
from .runner import BenchmarkResult, evaluate_pipeline_task


STAT_TASKS = [
    {
        "id": "stat_01",
        "description": (
            "Um estudo reporta p = 0.04 para a diferença entre dois grupos. "
            "Qual a interpretação CORRETA?"
        ),
        "options": [
            "a) Probabilidade de H0 ser verdadeira é 4%",
            "b) Se H0 é verdadeira, a probabilidade de observar um resultado tão ou mais extremo é 4%",
            "c) O tamanho de efeito é grande",
            "d) Há 96% de chance de H1 ser verdadeira",
        ],
        "correct": "b",
        "evaluation_criteria": (
            "Erro clássico: p-valor NÃO é probabilidade de H0. "
            "É P(dados|H0), não P(H0|dados). A interpretação correta é "
            "'probabilidade dos dados ou mais extremos sob H0'."
        ),
    },
    {
        "id": "stat_02",
        "description": (
            "Dois estudos medem o mesmo efeito. Estudo A: p=0.003, d=0.25. "
            "Estudo B: p=0.04, d=0.60. Qual tem evidência mais forte?"
        ),
        "options": [
            "a) Estudo A (p-valor menor = evidência mais forte)",
            "b) Estudo B (tamanho de efeito maior = mais relevante)",
            "c) Ambos têm força similar (ambos significativos)",
            "d) Não é possível comparar sem ver os intervalos de confiança",
        ],
        "correct": "b",
        "evaluation_criteria": (
            "p-valor depende do tamanho amostral. Efeito pequeno (d=0.25) "
            "pode ser significativo com n grande. O efeito médio (d=0.60) "
            "é mais relevante praticamente. Candidato deve demonstrar "
            "compreensão de que significância ≠ tamanho de efeito."
        ),
    },
    {
        "id": "stat_03",
        "description": (
            "Um pesquisador testa 20 hipóteses e encontra 2 com p < 0.05. "
            "Qual a principal preocupação?"
        ),
        "options": [
            "a) Os resultados são robustos",
            "b) Múltiplas comparações: sob H0, espera-se 1 falso positivo em 20 testes",
            "c) O poder estatístico é baixo",
            "d) O tamanho de efeito é negligenciável",
        ],
        "correct": "b",
        "evaluation_criteria": (
            "Com alpha=0.05 e 20 testes independentes, sob H0 global, "
            "espera-se em média 20*0.05 = 1 falso positivo. Encontrar 2 "
            "pode ser devido ao erro de Tipo I. Correção necessária (Bonferroni, FDR)."
        ),
    },
]


class StatisticalInterpretationBenchmark:
    """Benchmark de interpretação estatística."""

    def __init__(self):
        self.tasks = STAT_TASKS

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
            name="Statistical Interpretation",
            score=passed / len(self.tasks),
            tasks_total=len(self.tasks),
            tasks_passed=passed,
            details=details,
        )
