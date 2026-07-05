#!/usr/bin/env python3
"""
Runner dos CTs do Round 17 (Gartner Hype Cycle 2026) + Round 18 (Token Economy).
Uso:
    python specs/tests/run_all_cts.py              # executa todos
    python specs/tests/run_all_cts.py --cov         # com cobertura
    python specs/tests/run_all_cts.py --spec 022    # apenas SPEC-022
    python specs/tests/run_all_cts.py --html        # relatório HTML
"""
import subprocess
import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))
TEST_FILES = {
    # Round 17 — Gartner Hype Cycle 2026
    19: os.path.join(BASE, "test_spec019_api_governance.py"),
    20: os.path.join(BASE, "test_spec020_data_streaming.py"),
    21: os.path.join(BASE, "test_spec021_low_code_platform.py"),
    # Round 18 — Token Economy
    22: os.path.join(BASE, "test_spec022_token_economy.py"),
    23: os.path.join(BASE, "test_spec023_agent_economics.py"),
    24: os.path.join(BASE, "test_spec024_audit_integration.py"),
}

def main():
    args = sys.argv[1:]
    cmd = [sys.executable, "-m", "pytest"]

    # Filtro por SPEC (suporta múltiplos: --spec 22 --spec 23)
    spec_filters = []
    skip_next = False
    for i, a in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if a.startswith("--spec="):
            spec_filters.append(int(a.split("=")[1]))
        elif a.startswith("--spec"):
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                spec_filters.append(int(args[i + 1]))
                skip_next = True

    if spec_filters:
        for s in spec_filters:
            if s not in TEST_FILES:
                print(f"SPEC-{s:03d} não encontrada. Opções: {list(TEST_FILES.keys())}")
                sys.exit(1)
        cmd.extend(TEST_FILES[s] for s in spec_filters)
    else:
        cmd.extend(TEST_FILES.values())

    # Flags
    if "--cov" in args or "--coverage" in args:
        cmd.extend(["--cov", "--cov-report=term-missing"])
    if "--html" in args:
        cmd.extend(["--html=report.html", "--self-contained-html"])
    if "--verbose" in args or "-v" in args:
        if "-v" not in cmd:
            cmd.append("-v")

    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=BASE, text=True)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
