#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quality Report Generator
=========================
Gera relatorio consolidado de qualidade do ecossistema:
  - Contagem de testes
  - Taxa de aprovacao
  - Cobertura estimada por modulo
  - Score de qualidade (0-10)
  - Recomendacoes

Uso: python scripts/quality_report.py [--json] [--output report.json] [--quick]
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTEST_TIMEOUT_SECONDS = 300


def _parse_pytest_counts(output: str) -> dict:
    """Extrai passed/failed/skipped da saída do pytest."""
    counts = {"passed": 0, "failed": 0, "skipped": 0}
    for count, label in re.findall(r"(\d+)\s+(passed|failed|skipped)", output):
        counts[label] = int(count)

    total = counts["passed"] + counts["failed"] + counts["skipped"]
    return {
        "total": total,
        "passed": counts["passed"],
        "failed": counts["failed"],
        "skipped": counts["skipped"],
        "pass_rate": round(counts["passed"] / max(total, 1) * 100, 1),
    }


def run_tests() -> dict:
    """Executa pytest e captura resultados."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short"],
        capture_output=True, text=True, timeout=PYTEST_TIMEOUT_SECONDS,
        cwd=str(REPO_ROOT)
    )
    output = result.stdout + result.stderr
    parsed = _parse_pytest_counts(output)
    parsed["raw_output"] = output[:1000]
    return parsed


def estimate_coverage() -> dict:
    """Estima cobertura por modulo (contagem de testes vs classes)."""
    modules = {}
    test_dir = REPO_ROOT / "tests"

    for test_file in sorted(test_dir.glob("test_*.py")):
        module_name = test_file.stem.replace("test_", "", 1)
        with open(test_file) as f:
            content = f.read()
        test_count = content.count("def test_")
        modules[module_name] = {
            "test_count": test_count,
            "has_fixtures": "def setup" in content or "@pytest.fixture" in content,
        }

    return modules


def check_lint() -> dict:
    """Verifica lint com Ruff (se instalado)."""
    try:
        result = subprocess.run(
            ["ruff", "check", "--output-format=json", "."],
            capture_output=True, text=True, timeout=30,
            cwd=str(REPO_ROOT)
        )
        if result.returncode == 0:
            return {"errors": 0, "status": "clean"}
        errors = json.loads(result.stdout) if result.stdout else []
        return {"errors": len(errors), "status": "issues_found"}
    except (FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired):
        return {"errors": -1, "status": "ruff_not_available"}


def calculate_score(test_results: dict, coverage: dict, lint: dict) -> dict:
    """Calcula score de qualidade (0-10)."""
    scores = {}

    # Test pass rate (peso 3)
    pass_rate = test_results.get("pass_rate", 0)
    scores["test_pass_rate"] = min(10, pass_rate / 10)

    # Test count (peso 2)
    test_count = test_results.get("total", 0)
    scores["test_coverage"] = min(10, test_count / 60)  # 600 testes = 10

    # Zero failures (peso 2)
    failures = test_results.get("failed", 0)
    scores["zero_failures"] = 10 if failures == 0 else max(0, 10 - failures * 2)

    # Module coverage (peso 2)
    modules_covered = len(coverage)
    scores["module_coverage"] = min(10, modules_covered / 2)

    # Lint (peso 1)
    lint_errors = lint.get("errors", 0)
    if lint_errors == -1:
        scores["lint_quality"] = 5  # neutral se ruff nao disponivel
    elif lint_errors == 0:
        scores["lint_quality"] = 10
    else:
        scores["lint_quality"] = max(0, 10 - lint_errors)

    # Weighted average
    weights = {"test_pass_rate": 3, "test_coverage": 2, "zero_failures": 2,
               "module_coverage": 2, "lint_quality": 1}
    total_weight = sum(weights.values())
    weighted_score = sum(scores[k] * weights[k] for k in scores) / total_weight

    return {
        "overall_score": round(weighted_score, 1),
        "dimensions": scores,
        "weights": weights,
    }


def generate_report(quick: bool = False) -> dict:
    """Gera relatorio completo."""
    print("[quality] Gerando relatorio de qualidade...")

    if quick:
        test_results = {"total": 0, "passed": 0, "failed": 0,
                        "skipped": 0, "pass_rate": 100.0}
        print("  (quick mode - test execution skipped)")
    else:
        test_results = run_tests()

    print(f"  Testes: {test_results['passed']} passed, "
          f"{test_results['failed']} failed, "
          f"{test_results['skipped']} skipped")

    coverage = estimate_coverage()
    print(f"  Modulos com testes: {len(coverage)}")

    lint = check_lint()
    print(f"  Lint: {lint['status']} ({lint['errors']} erros)")

    score = calculate_score(test_results, coverage, lint)
    print(f"  Score: {score['overall_score']}/10")
    # Recomendacoes
    recommendations = []
    if test_results.get("failed", 0) > 0:
        recommendations.append(f"Corrigir {test_results['failed']} teste(s) falhando")
    if lint.get("errors", 0) > 0:
        recommendations.append(f"Corrigir {lint['errors']} erro(s) de lint")
    if score["overall_score"] < 7:
        recommendations.append("Aumentar cobertura de testes")
    if not recommendations:
        recommendations.append("Nenhuma acao urgente identificada")

    report = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "repository": "opencode-ecosystem-core",
        "test_results": test_results,
        "module_coverage": coverage,
        "lint": lint,
        "quality_score": score,
        "recommendations": recommendations,
        "overall_status": "PASS" if test_results["failed"] == 0 else "FAIL",
    }

    return report


def main():
    parser = argparse.ArgumentParser(description="Quality Report Generator")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    parser.add_argument("--quick", action="store_true", help="Pular execucao de testes (usa dados sinteticos)")
    parser.add_argument("--output", "-o", type=str, help="Save report to file")
    args = parser.parse_args()

    report = generate_report(quick=args.quick)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(report, indent=2, default=str))
        print(f"  Relatorio salvo em: {output_path}")

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(f"\nRELATORIO DE QUALIDADE")
        print(f"  Status: {report['overall_status']}")
        print(f"  Score: {report['quality_score']['overall_score']}/10")
        print(f"  Testes: {report['test_results']['passed']}/{report['test_results']['total']}")
        print(f"  Lint: {report['lint']['status']}")
        print(f"  Recomendacoes: {report['recommendations'][0] if report['recommendations'] else 'Nenhuma'}")

    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
