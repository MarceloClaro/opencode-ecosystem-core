# -*- coding: utf-8 -*-
"""
Benchmark de Desenho Experimental.

Testa:
1. Escolha do design apropriado (RCT, quasi-experimental, observacional)
2. Identificação de grupos de controle adequados
3. Randomização e cegamento
4. Tamanho amostral e poder
5. Análise de subgrupos e interações
"""

from typing import Dict, Any, List, Optional, Callable
from .runner import BenchmarkResult, evaluate_pipeline_task


DESIGN_TASKS = [
    {
        "id": "design_01",
        "description": (
            "Para testar se um novo método de ensino melhora notas em matemática, "
            "qual o desenho experimental mais adequado?"
        ),
        "options": [
            "a) RCT: randomizar alunos para método novo vs. tradicional",
            "b) Observacional: comparar escolas que usam vs. não usam o método",
            "c) Pré-pós: medir notas antes e depois da implementação",
            "d) Estudo de caso: entrevistar professores que usam o método",
        ],
        "correct": "a",
        "evaluation_criteria": (
            "RCT é gold standard para inferência causal. Randomização "
            "elimina confounders observados e não observados. "
            "Desenhos observacionais e pré-pós são vulneráveis a viés."
        ),
    },
    {
        "id": "design_02",
        "description": (
            "Um experimento precisa detectar um efeito de d=0.3 com poder de 0.80 "
            "e alpha=0.05 (bilateral). Quantos participantes por grupo são necessários?"
        ),
        "options": [
            "a) aproximadamente 45 por grupo",
            "b) aproximadamente 90 por grupo",
            "c) aproximadamente 175 por grupo",
            "d) aproximadamente 350 por grupo",
        ],
        "correct": "c",
        "evaluation_criteria": (
            "Usando n = 2*(Z_alpha/2 + Z_beta)^2 / d^2 = 2*(1.96+0.84)^2 / 0.09 "
            "≈ 2*7.84/0.09 ≈ 174.2. Portanto ~175 por grupo. "
            "O candidato deve demonstrar conhecimento de power analysis."
        ),
    },
]


class ExperimentalDesignBenchmark:
    """Benchmark de desenho experimental."""

    def __init__(self):
        self.tasks = DESIGN_TASKS

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
            name="Experimental Design",
            score=passed / len(self.tasks),
            tasks_total=len(self.tasks),
            tasks_passed=passed,
            details=details,
        )
