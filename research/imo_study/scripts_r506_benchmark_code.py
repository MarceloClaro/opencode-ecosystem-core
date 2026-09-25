#!/usr/bin/env python3
"""
R506 — Benchmark runner: 9 problemas × 3 modelos (código executável).
Chama cada LLM com prompt de código, extrai, executa, classifica.
"""
import sys, os, json, time, subprocess
from pathlib import Path

# Adiciona raiz do projeto ao path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from integrations.code_executor import run_single, execute_code, classify_result, extract_code
from integrations.code_prompt import PROBLEMS, get_code_prompt

OUTPUT = PROJECT_ROOT / "research" / "imo_study" / "benchmark_r506_code.json"

MODELS = [
    ("opencode/mimo-v2.5-free", "mimo-v2.5", 100),
    ("opencode/big-pickle", "big-pickle", 110),
    ("opencode/nemotron-3-ultra-free", "nemotron-3", 150),
]

def call_model(model_id: str, prompt: str, timeout_s: int) -> str:
    """Chama o modelo via opencode run CLI."""
    import re as _re
    cmd = [
        "opencode", "run",
        "-m", model_id,
        prompt,
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s + 30,
            cwd=str(Path(__file__).resolve().parents[2]),
        )
        # Remove ANSI codes e linhas de log
        raw = result.stdout
        lines = []
        for line in raw.split('\n'):
            clean = _re.sub(r'\x1b\[[0-9;]*m', '', line).strip()
            # Pula linhas de log do build
            if clean.startswith('>') or clean.startswith('·') or not clean:
                continue
            lines.append(clean)
        return '\n'.join(lines)
    except subprocess.TimeoutExpired:
        return "[MODEL_TIMEOUT]"
    except Exception as e:
        return f"[MODEL_ERROR: {e}]"


def run_benchmark():
    """Executa benchmark completo: 9 problemas × 3 modelos."""
    all_results = {}

    for model_id, model_label, model_timeout in MODELS:
        print(f"\n{'='*60}")
        print(f"MODELO: {model_label} ({model_id})")
        print(f"{'='*60}")

        model_results = []
        for prob in PROBLEMS:
            print(f"\n--- {prob['id']} ({prob['category']}) ---")
            print(f"  Esperado: {prob['expected']}")

            # Gera prompt de código
            prompt = get_code_prompt(prob)

            # Chama o LLM
            t0 = time.time()
            llm_response = call_model(model_id, prompt, model_timeout)
            model_time = time.time() - t0
            print(f"  LLM respondeu em {model_time:.1f}s ({len(llm_response)} chars)")

            # Extrai código
            code = extract_code(llm_response)
            print(f"  Código extraído: {len(code)} chars")
            if code:
                print(f"  Primeiras 3 linhas:")
                for line in code.split('\n')[:3]:
                    print(f"    {line}")

            # Executa código
            if code:
                stdout, stderr, exit_code, exec_time = execute_code(code, timeout_s=30)
                status = classify_result(stdout, stderr, exit_code,
                                         prob['expected'], exec_time, code)
                print(f"  stdout: {stdout[:80]}")
                if stderr:
                    print(f"  stderr: {stderr[:80]}")
                print(f"  status: {status} ({exec_time:.2f}s)")
            else:
                stdout, stderr, exit_code, exec_time = "", "no_code", -1, 0.0
                status = "code_missing"
                print(f"  status: code_missing")

            model_results.append({
                "problem": prob["id"],
                "category": prob["category"],
                "expected": prob["expected"],
                "code": code,
                "stdout": stdout[:2000],
                "stderr": stderr[:500],
                "status": status,
                "elapsed_s": round(exec_time, 2),
                "model_time_s": round(model_time, 1),
                "exit_code": exit_code,
            })

        all_results[model_id] = model_results

        # Salva incrementalmente
        with open(OUTPUT, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        # Resumo do modelo
        correct = sum(1 for r in model_results if r["status"] == "correct")
        runtime_errors = sum(1 for r in model_results if r["status"] == "runtime_error")
        timeouts = sum(1 for r in model_results if r["status"] == "timeout")
        code_missing = sum(1 for r in model_results if r["status"] == "code_missing")
        wrong = sum(1 for r in model_results if r["status"] == "wrong_answer")
        no_output = sum(1 for r in model_results if r["status"] == "no_output")
        print(f"\n  RESUMO {model_label}: {correct}/9 correct | "
              f"{wrong} wrong | {runtime_errors} runtime_error | "
              f"{timeouts} timeout | {no_output} no_output | "
              f"{code_missing} code_missing")

    # Resumo final
    print(f"\n{'='*60}")
    print("RESUMO FINAL — R506 Executable Code Benchmark")
    print(f"{'='*60}")
    print(f"{'modelo':20s} {'correct':>8s} {'wrong':>8s} {'rt_err':>8s} {'timeout':>8s} {'no_out':>8s} {'missing':>8s}")
    for model_id, model_label, _ in MODELS:
        rs = all_results[model_id]
        c = sum(1 for r in rs if r["status"] == "correct")
        w = sum(1 for r in rs if r["status"] == "wrong_answer")
        e = sum(1 for r in rs if r["status"] == "runtime_error")
        t = sum(1 for r in rs if r["status"] == "timeout")
        n = sum(1 for r in rs if r["status"] == "no_output")
        m = sum(1 for r in rs if r["status"] == "code_missing")
        print(f"{model_label:20s} {c:8d} {w:8d} {e:8d} {t:8d} {n:8d} {m:8d}")

    print(f"\nResultados salvos em: {OUTPUT}")
    return all_results


if __name__ == "__main__":
    run_benchmark()