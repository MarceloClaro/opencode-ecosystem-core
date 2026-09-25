#!/usr/bin/env python3
"""
R506 — Sandbox de execução de código gerado por LLM.
Executa código Python em subprocess isolado com timeout,
captura stdout/stderr e compara com resposta esperada.
"""
import subprocess, sys, os, re, json, time, textwrap
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

TIMEOUT_S = 30
MAX_OUTPUT_CHARS = 100_000

@dataclass
class ExecutionResult:
    problem: str
    model: str
    expected: str
    code: str
    stdout: str = ""
    stderr: str = ""
    status: str = "pending"  # correct/wrong_answer/runtime_error/timeout/code_missing/no_output
    elapsed_s: float = 0.0
    exit_code: Optional[int] = None

    def to_dict(self):
        return asdict(self)


def extract_code(llm_response: str) -> str:
    """Extrai o primeiro bloco ```python ... ``` do response LLM."""
    # Tenta padrão markdown (com ou sem label, com ou sem newline)
    patterns = [
        r'```python\s*\n(.*?)```',
        r'```python\n(.*?)```',
        r'```python(.*?)```',
        r'```\s*\n(.*?)```',
        r'```\w*\s*\n(.*?)```',
        r'```python\s*\n(.*?)$',
    ]
    for pat in patterns:
        m = re.search(pat, llm_response, re.DOTALL | re.MULTILINE)
        if m:
            code = m.group(1).strip()
            if len(code) >= 5:  # mínimo: print(x) já é válido
                return code

    # Fallback: procura código que começa com import/def
    lines = llm_response.split('\n')
    code_lines = []
    capturing = False
    for line in lines:
        stripped = line.strip()
        if not capturing:
            if stripped.startswith(('import ', 'from ', 'def ', 'class ', '#!/usr/bin')):
                capturing = True
                code_lines.append(line)
        else:
            if stripped.startswith(('```', '---', '===', '**')) and len(code_lines) > 2:
                break
            code_lines.append(line)

    code = '\n'.join(code_lines).strip()
    if len(code) > 20:
        return code

    return ""


def normalize_answer(answer: str) -> str:
    """Normaliza resposta para comparação."""
    s = answer.strip().lower()
    # Remove whitespace extra
    s = re.sub(r'\s+', ' ', s)
    # Remove parênteses externos
    while s.startswith('(') and s.endswith(')'):
        s = s[1:-1].strip()
    return s


def compare_answers(obtained: str, expected: str) -> bool:
    """Compara saída com resposta esperada (numérico ou string)."""
    norm_o = normalize_answer(obtained)
    norm_e = normalize_answer(expected)

    # Match exato
    if norm_o == norm_e:
        return True

    # Tenta match numérico
    try:
        # Remove notation ex: 2^{n-1} → tenta avaliar
        if float(norm_o) == float(norm_e):
            return True
    except (ValueError, OverflowError):
        pass

    # Tenta match com fracionário
    try:
        from fractions import Fraction
        fo = Fraction(norm_o)
        fe = Fraction(norm_e)
        if fo == fe:
            return True
    except (ValueError, ZeroDivisionError):
        pass

    # Contém a resposta (flexível)
    if norm_e in norm_o or norm_o in norm_e:
        return True

    return False


def execute_code(code: str, timeout_s: int = TIMEOUT_S) -> tuple:
    """Executa código Python em subprocess isolado."""
    if not code:
        return "", "", -1, 0.0

    # Script completo com print de debug
    full_script = code

    tmpfile = Path("/tmp") / f"r506_exec_{os.getpid()}.py"
    tmpfile.write_text(full_script, encoding='utf-8')

    try:
        t0 = time.time()
        result = subprocess.run(
            [sys.executable, str(tmpfile)],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            env={
                **os.environ,
                "PYTHONPATH": "",
                "PYTHONDONTWRITEBYTECODE": "1",
            },
            cwd="/tmp",
        )
        elapsed = time.time() - t0
        stdout = result.stdout[:MAX_OUTPUT_CHARS]
        stderr = result.stderr[:MAX_OUTPUT_CHARS]
        return stdout, stderr, result.returncode, elapsed

    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        return "", f"TIMEOUT after {timeout_s}s", -1, elapsed
    except Exception as e:
        return "", f"EXEC_ERROR: {e}", -1, 0.0
    finally:
        try:
            tmpfile.unlink()
        except:
            pass


def classify_result(stdout: str, stderr: str, exit_code: int,
                    expected: str, elapsed: float, code: str) -> str:
    """Classifica o resultado da execução."""
    if not code:
        return "code_missing"
    if exit_code == -1 and "TIMEOUT" in stderr:
        return "timeout"
    if exit_code != 0 and not stdout.strip():
        return "runtime_error"
    if not stdout.strip():
        return "no_output"
    if compare_answers(stdout, expected):
        return "correct"
    return "wrong_answer"


def run_single(problem: dict, model_id: str, llm_response: str,
               timeout_s: int = TIMEOUT_S) -> ExecutionResult:
    """Executa um único problema: extrai código, roda, classifica."""
    code = extract_code(llm_response)
    expected = problem.get("expected", "")

    if not code:
        return ExecutionResult(
            problem=problem["id"],
            model=model_id,
            expected=expected,
            code="",
            status="code_missing",
        )

    stdout, stderr, exit_code, elapsed = execute_code(code, timeout_s)
    status = classify_result(stdout, stderr, exit_code, expected, elapsed, code)

    return ExecutionResult(
        problem=problem["id"],
        model=model_id,
        expected=expected,
        code=code,
        stdout=stdout.strip(),
        stderr=stderr.strip(),
        status=status,
        elapsed_s=round(elapsed, 2),
        exit_code=exit_code,
    )


def run_benchmark(problems: list, model_id: str, model_fn, timeout_s: int = TIMEOUT_S) -> list:
    """
    Roda benchmark completo para um modelo.
    problems: lista de dicts {id, prompt, expected}
    model_fn: callable(prompt) -> str (chama o LLM)
    """
    results = []
    for prob in problems:
        try:
            llm_response = model_fn(prob["prompt"])
        except Exception as e:
            llm_response = f"MODEL_ERROR: {e}"

        res = run_single(prob, model_id, llm_response, timeout_s)
        results.append(res)
        print(f"  {prob['id']:30s} {res.status:16s} {res.elapsed_s:6.1f}s"
              f"  code={len(res.code):5d}B"
              f"  out={res.stdout[:50]}")

    return results


if __name__ == "__main__":
    # Smoke test
    test_code = '''
import math
# Encontre todos os primos p até 20
primos = [p for p in range(2, 21) if all(p % d != 0 for d in range(2, int(math.sqrt(p))+1))]
print(primos)
'''
    result = execute_code(test_code, timeout_s=5)
    print("Smoke test:", result)
    print("Classification:", classify_result(result[0], result[1], result[2], "[2, 3, 5, 7, 11, 13, 17, 19]", result[3], test_code))