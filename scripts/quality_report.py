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

Uso: python scripts/quality_report.py [--json] [--output report.json]
     [--junit pytest.xml | --quick]
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parent.parent
# A execução direta conserva uma janela suficiente para a suíte integral.
# A CI fornece --junit e não executa a mesma bateria novamente.
PYTEST_TIMEOUT_SECONDS = 3600


def _parse_pytest_counts(output: str) -> dict:
    """Extrai passed/failed/skipped da saída do pytest."""
    counts = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
    for count, label in re.findall(r"(\d+)\s+(passed|failed|skipped|errors?)", output):
        counts["errors" if label.startswith("error") else label] = int(count)

    total = sum(counts.values())
    return {
        "total": total,
        **counts,
        "pass_rate": round(counts["passed"] / max(total, 1) * 100, 1),
    }


def run_tests() -> dict:
    """Executa pytest e captura resultados."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short"],
            capture_output=True, text=True, timeout=PYTEST_TIMEOUT_SECONDS,
            cwd=str(REPO_ROOT)
        )
    except subprocess.TimeoutExpired:
        return {**_parse_pytest_counts(""), "executed": True,
                "source": "pytest_cli", "exit_code": None,
                "execution_error": "timeout", "raw_output": ""}
    output = result.stdout + result.stderr
    parsed = _parse_pytest_counts(output)
    parsed["raw_output"] = output[:1000]
    parsed.update(executed=True, source="pytest_cli", exit_code=result.returncode)
    return parsed


def load_junit_results(path: str | Path) -> dict:
    """Conta testcases do JUnit fornecido, sem executar nem autenticar a suíte."""
    source = Path(path)
    if source.stat().st_size > 32 * 1024 * 1024:
        raise ValueError("JUnit excede o limite de 32 MiB.")
    raw = source.read_bytes()
    if b"<!doctype" in raw.lower() or b"<!entity" in raw.lower():
        raise ValueError("Declarações DTD/ENTITY não são aceitas no JUnit.")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError("JUnit inválido.") from exc
    if root.tag not in {"testsuite", "testsuites"}:
        raise ValueError("Raiz JUnit não reconhecida.")
    cases = list(root.iter("testcase"))
    if not cases:
        raise ValueError("JUnit não contém casos de teste.")

    def count_cases(selected):
        counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
        for case in selected:
            flags = [(tag, case.find(tag) is not None) for tag in ("failure", "error", "skipped")]
            outcomes = [tag for tag, present in flags if present]
            if len(outcomes) > 1:
                raise ValueError("JUnit contém desfechos conflitantes no mesmo caso.")
            outcome = outcomes[0] if outcomes else "passed"
            counts[{"failure": "failed", "error": "errors"}.get(outcome, outcome)] += 1
        return counts

    counts = count_cases(cases)
    unrepresented_tests = 0
    declared_tests = len(cases)
    # Atributos agregados validam coerência, mas não somam novamente os casos.
    for suite in root.iter():
        if suite.tag not in {"testsuite", "testsuites"}:
            continue
        selected = list(suite.iter("testcase"))
        selected_counts = count_cases(selected)
        expected = {"tests": len(selected), "failures": selected_counts["failed"],
                    "errors": selected_counts["errors"], "skipped": selected_counts["skipped"]}
        for field, value in expected.items():
            if field in suite.attrib:
                try:
                    declared = int(suite.attrib[field])
                except ValueError as exc:
                    raise ValueError("Contador JUnit inválido.") from exc
                # Pytest pode incluir subtestes no agregado sem serializar um
                # testcase para cada aprovação. Registrar o desvio não cria
                # aprovações adicionais nem transforma o atributo em medida.
                if (field == "tests" and declared > value
                        and suite.tag == "testsuite" and suite.get("name") == "pytest"):
                    unrepresented_tests += declared - value
                    declared_tests += declared - value
                    continue
                if declared != value:
                    raise ValueError("Contadores JUnit não correspondem aos casos registrados.")
    measured = counts["passed"] + counts["failed"] + counts["errors"] > 0
    return {"total": len(cases), **counts,
            "pass_rate": round(counts["passed"] / len(cases) * 100, 1) if measured else None,
            "executed": measured, "source": "provided_junit", "exit_code": None,
            "declared_tests": declared_tests, "unrepresented_tests": unrepresented_tests,
            "suite_aggregate_fully_represented": unrepresented_tests == 0,
            "junit_path": str(source.resolve()), "junit_sha256": hashlib.sha256(raw).hexdigest(),
            "provenance_verified": False}


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
            [sys.executable, "-m", "ruff", "check", "--output-format=json", "."],
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
    """Calcula heurística local; não representa cobertura funcional ou certificação."""
    if test_results.get("pass_rate") is None:
        return {"overall_score": None, "dimensions": {}, "weights": {},
                "score_kind": "not_measured"}
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
        "score_kind": "heuristic_inventory",
    }


def generate_report(quick: bool = False, junit_path: str | Path | None = None) -> dict:
    """Gera relatorio completo."""
    print("[quality] Gerando relatorio de qualidade...")

    if quick and junit_path is not None:
        raise ValueError("Modo quick e JUnit fornecido são mutuamente exclusivos.")
    if junit_path is not None:
        test_results = load_junit_results(junit_path)
    elif quick:
        test_results = {"total": 0, "passed": 0, "failed": 0,
                        "skipped": 0, "errors": 0, "pass_rate": None,
                        "executed": False, "source": "not_run", "exit_code": None}
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
    print(f"  Score: {score['overall_score']}/10" if score["overall_score"] is not None else "  Score: não medido")
    # Recomendacoes
    recommendations = []
    if test_results.get("failed", 0) > 0:
        recommendations.append(f"Corrigir {test_results['failed']} teste(s) falhando")
    if test_results.get("errors", 0) > 0:
        recommendations.append(f"Corrigir {test_results['errors']} erro(s) de execução/coleta")
    if lint.get("errors", 0) > 0:
        recommendations.append(f"Corrigir {lint['errors']} erro(s) de lint")
    if score["overall_score"] is not None and score["overall_score"] < 7:
        recommendations.append("Aumentar cobertura de testes")
    if not test_results.get("executed"):
        recommendations.append("Não houve medição de testes executados; execute a suíte ou forneça seu JUnit.")
    if test_results.get("unrepresented_tests", 0):
        recommendations.append(
            f"{test_results['unrepresented_tests']} item(ns) do agregado pytest sem testcase próprio; "
            "não incluídos na contagem de aprovações."
        )
    if not recommendations:
        recommendations.append("Nenhuma acao urgente identificada")

    if (test_results.get("failed", 0) or test_results.get("errors", 0)
            or test_results.get("execution_error")
            or test_results.get("exit_code") not in (None, 0)):
        overall_status = "FAIL"
    elif not test_results.get("executed") or test_results["passed"] == 0:
        overall_status = "NOT_RUN"
    else:
        overall_status = "PASS_WITH_SKIPS" if test_results["skipped"] else "PASS"
    report = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "repository": "opencode-ecosystem-core",
        "test_results": test_results,
        "module_coverage": coverage,
        "lint": lint,
        "quality_score": score,
        "recommendations": recommendations,
        "overall_status": overall_status,
        "verification_scope": "local_test_report",
        "externally_validated": False,
    }

    return report


def main():
    parser = argparse.ArgumentParser(description="Quality Report Generator")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--quick", action="store_true", help="Gerar inventário sem medição de testes (NOT_RUN)")
    inputs.add_argument("--junit", type=Path, help="Reutilizar JUnit de pytest já executado, sem repetir a suíte")
    parser.add_argument("--output", "-o", type=str, help="Save report to file")
    args = parser.parse_args()

    try:
        report = generate_report(quick=args.quick, junit_path=args.junit)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(report, indent=2, default=str))
        print(f"  Relatorio salvo em: {output_path}")

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print("\nRELATORIO DE QUALIDADE")
        print(f"  Status: {report['overall_status']}")
        print(f"  Score: {report['quality_score']['overall_score']}/10")
        print(f"  Testes: {report['test_results']['passed']}/{report['test_results']['total']}")
        print(f"  Lint: {report['lint']['status']}")
        print(f"  Recomendacoes: {report['recommendations'][0] if report['recommendations'] else 'Nenhuma'}")

    if report["overall_status"] == "NOT_RUN":
        return 0 if args.quick else 2
    return 0 if report["overall_status"] in {"PASS", "PASS_WITH_SKIPS"} else 1


if __name__ == "__main__":
    sys.exit(main())
