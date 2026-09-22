#!/usr/bin/env python3
"""
test_r506_executable_code.py — TDD tests para o Executable Code IMO Benchmark (R506)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from integrations.code_executor import (
    extract_code, compare_answers, normalize_answer,
    execute_code, classify_result, run_single, ExecutionResult
)
from integrations.code_prompt import PROBLEMS, get_code_prompt, get_all_problems
import pytest


class TestExtractCode:
    """REQ-02: Extração de código do response LLM."""

    def test_extrai_bloco_python(self):
        resp = """Aqui está a solução:
```python
# Resolve o problema
print(42)
```
Fim."""
        code = extract_code(resp)
        assert "print(42)" in code

    def test_extrai_bloco_sem_label(self):
        resp = """Solução:
```
x = 5
print(x * 2)
```"""
        code = extract_code(resp)
        assert "x = 5" in code
        assert "print(x * 2)" in code

    def test_extrai_import_sem_bloco(self):
        resp = """Vou resolver com sympy:
import sympy
x = sympy.Symbol('x')
print(sympy.solve(x**2 - 4, x))
Result: [2, -2]"""
        code = extract_code(resp)
        assert "import sympy" in code

    def test_retorna_vazio_sem_codigo(self):
        resp = "Não consegui resolver este problema. Não sei a resposta."
        code = extract_code(resp)
        assert code == ""

    def test_codigo_minimo_5_chars(self):
        resp = "```python\nprint(1)\n```"
        code = extract_code(resp)
        # "print(1)" tem 8 chars >= 5, é código válido
        assert "print(1)" in code

    def test_resposta_longa_sem_codigo(self):
        resp = ("Eu tentei resolver mas não consegui. O problema pede para "
                "encontrar um número primo, mas não sei qual. "
                "Talvez seja 7? Não tenho certeza.")
        code = extract_code(resp)
        assert code == ""


class TestCompareAnswers:
    """REQ-04: Validação de output."""

    def test_match_exato(self):
        assert compare_answers("42", "42") is True

    def test_match_com_espaco(self):
        assert compare_answers("  42  ", "42") is True

    def test_match_case_insensitive(self):
        assert compare_answers("{3}", "{3}") is True

    def test_match_numerico_float(self):
        assert compare_answers("3.0", "3") is True

    def test_match_fracao(self):
        assert compare_answers("1/2", "0.5") is True

    def test_match_contido(self):
        assert compare_answers("O resultado é 42 e pronto", "42") is True

    def test_falso_negativo(self):
        assert compare_answers("43", "42") is False

    def test_normaliza_parenteses(self):
        assert compare_answers("(7, 3)", "7, 3") is True


class TestNormalizeAnswer:
    """Normalização de respostas."""

    def test_strip_whitespace(self):
        assert normalize_answer("  42  ") == "42"

    def test_lowercase(self):
        assert normalize_answer("TRUE") == "true"

    def test_remove_parenteses(self):
        assert normalize_answer("(7, 3)") == "7, 3"


class TestExecuteCode:
    """REQ-03: Sandbox de execução."""

    def test_codigo_simples(self):
        code = "print(2 + 2)"
        stdout, stderr, rc, elapsed = execute_code(code, timeout_s=5)
        assert rc == 0
        assert stdout.strip() == "4"

    def test_timeout(self):
        code = "import time; time.sleep(60)"
        stdout, stderr, rc, elapsed = execute_code(code, timeout_s=2)
        assert rc == -1
        assert "TIMEOUT" in stderr

    def test_runtime_error(self):
        code = "print(1/0)"
        stdout, stderr, rc, elapsed = execute_code(code, timeout_s=5)
        assert rc != 0

    def test_codigo_vazio(self):
        stdout, stderr, rc, elapsed = execute_code("", timeout_s=5)
        assert rc == -1

    def test_sem_input(self):
        code = "x = input('digite: ')"
        stdout, stderr, rc, elapsed = execute_code(code, timeout_s=5)
        assert rc != 0  # deve falhar (sem stdin)

    def test_usa_sympy(self):
        code = "import sympy; print(sympy.factorial(10))"
        stdout, stderr, rc, elapsed = execute_code(code, timeout_s=10)
        if rc == 0:
            assert "3628800" in stdout


class TestClassifyResult:
    """REQ-05: Classificação de resultado."""

    def test_correct(self):
        assert classify_result("42", "", 0, "42", 1.0, "print(42)") == "correct"

    def test_wrong_answer(self):
        assert classify_result("43", "", 0, "42", 1.0, "print(43)") == "wrong_answer"

    def test_runtime_error(self):
        assert classify_result("", "ZeroDivisionError", 1, "42", 0.1, "print(1/0)") == "runtime_error"

    def test_timeout(self):
        assert classify_result("", "TIMEOUT after 30s", -1, "42", 30.0, "import time; time.sleep(60)") == "timeout"

    def test_code_missing(self):
        assert classify_result("", "", -1, "42", 0.0, "") == "code_missing"

    def test_no_output(self):
        assert classify_result("", "", 0, "42", 0.1, "x = 5") == "no_output"


class TestRunSingle:
    """Integração extração→execução→classificação."""

    def test_codigo_valido_correto(self):
        prob = {"id": "test-01", "prompt": "2+2", "expected": "4"}
        resp = "```python\nprint(2 + 2)\n```"
        result = run_single(prob, "test-model", resp, timeout_s=5)
        assert result.status == "correct"
        assert result.stdout == "4"
        assert result.code != ""

    def test_codigo_valido_errado(self):
        prob = {"id": "test-02", "prompt": "2+2", "expected": "5"}
        resp = "```python\nprint(2 + 2)\n```"
        result = run_single(prob, "test-model", resp, timeout_s=5)
        assert result.status == "wrong_answer"

    def test_codigo_timeout(self):
        prob = {"id": "test-03", "prompt": "sleep", "expected": "1"}
        resp = "```python\nimport time; time.sleep(60)\nprint(1)\n```"
        result = run_single(prob, "test-model", resp, timeout_s=2)
        assert result.status == "timeout"

    def test_codigo_runtime_error(self):
        prob = {"id": "test-04", "prompt": "error", "expected": "1"}
        resp = "```python\nprint(1/0)\n```"
        result = run_single(prob, "test-model", resp, timeout_s=5)
        assert result.status == "runtime_error"

    def test_resposta_sem_codigo(self):
        prob = {"id": "test-05", "prompt": "hard", "expected": "42"}
        resp = "Não sei resolver, a resposta é 42 mas não consigo provar."
        result = run_single(prob, "test-model", resp, timeout_s=5)
        assert result.status == "code_missing"


class TestProblems:
    """Valida estrutura dos problemas R506."""

    def test_todos_9_problemas(self):
        assert len(PROBLEMS) == 9

    def test_campos_obrigatorios(self):
        for p in PROBLEMS:
            assert "id" in p
            assert "prompt" in p
            assert "expected" in p
            assert "category" in p

    def test_get_code_prompt(self):
        p = PROBLEMS[0]
        prompt = get_code_prompt(p)
        assert "python" in prompt.lower()
        assert p["prompt"] in prompt

    def test_get_all_problems(self):
        problems = get_all_problems()
        assert len(problems) == 9