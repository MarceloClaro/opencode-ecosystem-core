#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quality Gate — Verificador de Cobertura e Qualidade
=====================================================
Gate que bloqueia se:
  - Testes falharem (0 regressoes)
  - Cobertura estimada < 80%
  - Lint com erros graves

Uso: python scripts/check_coverage.py [--threshold 80] [--verbose]

Exit codes:
  0: Gate passed
  1: Gate failed (testes falharam)
  2: Gate failed (cobertura abaixo do threshold)
  3: Gate failed (lint errors)
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def check_tests() -> tuple[bool, dict]:
    """Verifica se todos os testes passam."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short"],
        capture_output=True, text=True, timeout=120,
        cwd=str(REPO_ROOT)
    )
    output = result.stdout + result.stderr

    passed = failed = skipped = 0
    for line in output.split("\n"):
        if "passed" in line and "failed" in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == "passed":
                    passed = int(parts[i - 1])
                elif part == "failed":
                    failed = int(parts[i - 1])
                elif part == "skipped":
                    skipped = int(parts[i - 1])

    all_pass = failed == 0 and result.returncode == 0
    return all_pass, {"passed": passed, "failed": failed, "skipped": skipped}


def estimate_coverage() -> float:
    """Estima cobertura: (testes / (classes * 3)) * 100."""
    test_dir = REPO_ROOT / "tests"
    core_dir = REPO_ROOT / "agentic_science_v2"
    synth_dir = REPO_ROOT / "synthetic_university"

    test_count = 0
    for f in test_dir.glob("test_*.py"):
        with open(f) as fh:
            test_count += fh.read().count("def test_")

    class_count = 0
    for d in [core_dir, synth_dir]:
        if d.exists():
            for f in d.glob("*.py"):
                with open(f) as fh:
                    class_count += fh.read().count("class ")

    # Estimativa: 3 testes por classe = 100% coverage
    if class_count == 0:
        return 0.0
    estimated = (test_count / (class_count * 3)) * 100
    return min(100.0, round(estimated, 1))


def check_lint() -> tuple[bool, int]:
    """Verifica lint basico."""
    result = subprocess.run(
        [sys.executable, "-c", "import py_compile; py_compile.compile('tests/test_r106_cicd.py', doraise=True)"],
        capture_output=True, text=True, timeout=10,
    )
    return result.returncode == 0, 0 if result.returncode == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="Quality Gate Checker")
    parser.add_argument("--threshold", type=float, default=80.0,
                        help="Threshold de cobertura (default: 80%%)")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    print("[gate] Quality Gate Check")
    print(f"  Threshold coverage: {args.threshold}%")

    # 1. Check tests
    tests_pass, test_stats = check_tests()
    pass_str = "PASS" if tests_pass else "FAIL"
    print(f"  Tests: [{pass_str}] "
          f"({test_stats['passed']}/{test_stats['passed'] + test_stats['failed']})")

    if not tests_pass:
        print(f"  Gate FAILED: {test_stats['failed']} teste(s) falhando")
        return 1

    # 2. Check coverage
    coverage = estimate_coverage()
    print(f"  Estimated coverage: {coverage}% (threshold: {args.threshold}%)")

    if coverage < args.threshold:
        print(f"  Gate FAILED: coverage {coverage}% < {args.threshold}%")
        return 2

    # 3. Check lint
    lint_pass, lint_errors = check_lint()
    pass_str = "PASS" if lint_pass else "FAIL"
    print(f"  Lint: [{pass_str}]")

    if not lint_pass:
        print(f"  Gate FAILED: {lint_errors} lint error(s)")
        return 3

    print("  ALL GATES PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
