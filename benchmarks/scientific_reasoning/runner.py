# -*- coding: utf-8 -*-
"""
Runner central dos benchmarks científicos.
Executa todos os benchmarks e compila resultados comparativos.
"""

from typing import Dict, Any, List, Optional


class BenchmarkResult:
    """Resultado consolidado de um benchmark."""

    def __init__(
        self,
        name: str,
        score: float,
        tasks_total: int,
        tasks_passed: int,
        details: List[Dict[str, Any]],
    ):
        self.name = name
        self.score = score
        self.tasks_total = tasks_total
        self.tasks_passed = tasks_passed
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benchmark": self.name,
            "score": round(self.score, 4),
            "tasks_total": self.tasks_total,
            "tasks_passed": self.tasks_passed,
            "pass_rate": round(
                self.tasks_passed / self.tasks_total, 4
            ) if self.tasks_total > 0 else 0,
            "details": self.details,
        }


def run_all_benchmarks(
    pipeline_fn=None,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Executa todos os benchmarks científicos.

    Args:
        pipeline_fn: Função do pipeline científico para testar.
                     Se None, testa cada módulo individualmente.
        verbose: Se True, imprime progresso.

    Returns:
        Dict com resultados consolidados
    """
    # Imports internos para evitar circular imports
    from .causal_benchmark import CausalInferenceBenchmark
    from .experimental_design_benchmark import ExperimentalDesignBenchmark
    from .statistical_benchmark import StatisticalInterpretationBenchmark
    from .power_analysis_benchmark import PowerAnalysisBenchmark
    from .bias_detection_benchmark import BiasDetectionBenchmark

    benchmarks = [
        ("Causal Inference", CausalInferenceBenchmark()),
        ("Experimental Design", ExperimentalDesignBenchmark()),
        ("Statistical Interpretation", StatisticalInterpretationBenchmark()),
        ("Power Analysis", PowerAnalysisBenchmark()),
        ("Bias Detection", BiasDetectionBenchmark()),
    ]

    results = []
    total_tasks = 0
    total_passed = 0

    for name, bench in benchmarks:
        if verbose:
            print(f"Executando benchmark: {name}...")

        try:
            bench_result = bench.run(pipeline_fn)
            results.append(bench_result.to_dict())
            total_tasks += bench_result.tasks_total
            total_passed += bench_result.tasks_passed

            if verbose:
                print(f"  Score: {bench_result.score:.2%} "
                      f"({bench_result.tasks_passed}/{bench_result.tasks_total})")
        except Exception as e:
            if verbose:
                print(f"  ERRO: {e}")
            results.append({
                "benchmark": name,
                "score": 0.0,
                "tasks_total": 0,
                "tasks_passed": 0,
                "error": str(e),
            })

    overall_score = total_passed / total_tasks if total_tasks > 0 else 0.0

    return {
        "benchmarks": results,
        "overall_score": round(overall_score, 4),
        "total_tasks": total_tasks,
        "total_passed": total_passed,
        "overall_pass_rate": round(total_passed / total_tasks, 4)
        if total_tasks > 0 else 0,
    }
