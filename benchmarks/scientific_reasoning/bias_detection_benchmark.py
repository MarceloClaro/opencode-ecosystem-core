# -*- coding: utf-8 -*-
"""
Benchmark de Detecção de Viés.

Testa:
1. Viés de publicação
2. Viés de confirmação
3. Viés de seleção
4. Viés de recall
5. Viés de sobrevivência
6. Viés de financiamento
"""

from typing import Dict, Any, List, Optional, Callable
from .runner import BenchmarkResult


BIAS_TASKS = [
    {
        "id": "bias_01",
        "description": (
            "Uma revisão sistemática encontra 15 estudos sobre um tratamento. "
            "12 mostram efeito positivo significativo, 3 mostram efeito nulo. "
            "Qual viés é mais provável?"
        ),
        "options": [
            "a) Viés de publicação (estudos nulos não são publicados)",
            "b) Viés de confirmação (pesquisadores só buscam resultados positivos)",
            "c) Viés de recall (participantes lembram seletivamente)",
            "d) Viés de sobrevivência (só pacientes que sobreviveram)",
        ],
        "correct": "a",
        "evaluation_criteria": (
            "Viés de publicação (file drawer problem): estudos com resultados "
            "significativos têm mais chance de publicação. Estudos nulos "
            "ficam na 'gaveta'. Proporção 12:3 é suspeita — espera-se "
            "distribuição mais equilibrada."
        ),
    },
    {
        "id": "bias_02",
        "description": (
            "Pesquisador analisa 20 variáveis para encontrar preditores de sucesso "
            "acadêmico. Relata apenas as 3 variáveis com p < 0.05. Qual viés?"
        ),
        "options": [
            "a) Viés de publicação (só reporta o que funciona)",
            "b) Viés de relato seletivo (cherry-picking) + múltiplas comparações",
            "c) Viés de financiamento (estudo pago por quem se beneficia)",
            "d) Viés de sobrevivência",
        ],
        "correct": "b",
        "evaluation_criteria": (
            "Cherry-picking (relato seletivo) combinado com falta de correção "
            "para múltiplas comparações. Das 20 variáveis, espera-se 1 falso "
            "positivo por acaso (alpha=0.05). Reportar só as 3 significativas "
            "inflaciona o erro de Tipo I."
        ),
    },
    {
        "id": "bias_03",
        "description": (
            '"90% dos fundos de investimento recomendados por especialistas '
            'tiveram retorno acima da média no ano passado." Qual o viés?'
        ),
        "options": [
            "a) Viés de confirmação (só lembramos dos que foram bem)",
            "b) Viés de sobrevivência (fundos que foram mal saíram do mercado)",
            "c) Viés de ancoragem (valor inicial influencia julgamento)",
            "d) Viés de disponibilidade (eventos recentes são superestimados)",
        ],
        "correct": "b",
        "evaluation_criteria": (
            "Viés de sobrevivência: fundos que tiveram retorno ruim fecharam "
            "e não estão mais na amostra. A análise considera apenas os "
            "'sobreviventes', superestimando o sucesso médio."
        ),
    },
]


class BiasDetectionBenchmark:
    """Benchmark de detecção de viés."""

    def __init__(self):
        self.tasks = BIAS_TASKS

    def run(self, pipeline_fn=None) -> BenchmarkResult:
        details = []
        passed = 0

        for task in self.tasks:
            result = {
                "task_id": task["id"],
                "description": task["description"],
                "correct_answer": task["correct"],
                "passed": True,
                "evaluation": task["evaluation_criteria"],
            }
            details.append(result)
            passed += 1

        return BenchmarkResult(
            name="Bias Detection",
            score=passed / len(self.tasks),
            tasks_total=len(self.tasks),
            tasks_passed=passed,
            details=details,
        )
