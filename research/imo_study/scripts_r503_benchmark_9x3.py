# -*- coding: utf-8 -*-
"""Benchmark R503 — 9 problemas × 3 modelos free (condição C2, MASWOS).
Execução pós-reinício do host (estado limpo). Salva incremental por problema.
Uso: python3 scripts_r503_benchmark_9x3.py
"""
import json, re, subprocess, sys, time, os

sys.path.insert(0, '.')
from integrations.deepmind.imobench_harness import IMOBenchmarkHarness
from research.imo_study.llm_free_benchmark import MASWOS_SCAFFOLD

OUT = "research/imo_study/benchmark_9x3.json"
EXPECTED = {
    "imo-bench-algebra-001": "3",
    "imo-bench-algebra-004": "2^(u-2)",
    "imo-bench-number-theory-001": "(7, 3)",
    "imo-bench-combinatorics-001": "2^{n-1}",
    "imo-bench-algebra-002": "5",
    "imo-bench-number-theory-002": "{3}",
    "imo-bench-number-theory-003": "1006",
    "imo-bench-combinatorics-002": "88",
    "imo-bench-geometry-001": "2043230",
}
# (regex com grupo, marcador canônico simplificado)
EXTRACT = {
    "imo-bench-algebra-001": (r"([0-9]+)", "3"),
    "imo-bench-algebra-004": (r"(2\^\{u-2\}|2\^\(u-2\)|2\^u-2)", "2"),  # presença da forma
    "imo-bench-number-theory-001": (r"(\(?\s*7\s*,\s*3\s*\)?)", "73"),
    "imo-bench-combinatorics-001": (r"(2\^\{n-1\}|2\^\(n-1\)|2\^\(n-1\)=)", "2"),
    "imo-bench-algebra-002": (r"([0-9]+)", "5"),
    "imo-bench-number-theory-002": (r"(3)", "3"),
    "imo-bench-number-theory-003": (r"([0-9]{3,5})", "1006"),
    "imo-bench-combinatorics-002": (r"([0-9]{1,3})", "88"),
    "imo-bench-geometry-001": (r"([0-9]{6,8})", "2043230"),
}
TIMEOUT = {"opencode/mimo-v2.5-free": 100, "opencode/big-pickle": 110,
           "opencode/nemotron-3-ultra-free": 150}


def build_prompt(p):
    return MASWOS_SCAFFOLD + "\n\nPROBLEMA: " + p.problem_text + "\n\nResponda no formato exato pedido."


def ask(model, prompt, timeout):
    cmd = f"opencode run -m {model} " + "'" + prompt.replace("'", "'\\''") + "'"
    t0 = time.time()
    try:
        out = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                             timeout=timeout, cwd=".").stdout
        return out, time.time() - t0, "ok"
    except subprocess.TimeoutExpired:
        return "", time.time() - t0, "timeout"


def eval_answer(out, pid):
    t = re.sub(r"\s+", "", out.lower())
    pat, marker = EXTRACT[pid]
    m = re.search(pat, t)
    if not m:
        return None, False
    v = m.group(1)
    if pid in ("imo-bench-algebra-004", "imo-bench-combinatorics-001"):
        return v, True  # presença da forma canônica resolve
    return v, (v.replace(",", "").replace("{", "").replace("}", "") == marker
               or (pid == "imo-bench-number-theory-001" and "7,3" in t))


def main():
    h = IMOBenchmarkHarness()
    probs = h.sample_dataset
    models = ["opencode/mimo-v2.5-free", "opencode/big-pickle",
              "opencode/nemotron-3-ultra-free"]
    # carrega parcial anterior
    results = {}
    if os.path.exists(OUT):
        results = json.load(open(OUT, encoding="utf-8"))
    for model in models:
        results.setdefault(model, [])
        done = {r["problem"] for r in results[model]}
        for p in probs:
            if p.problem_id in done:
                continue
            out, dur, status = ask(model, build_prompt(p), TIMEOUT[model])
            ans, correct = eval_answer(out, p.problem_id)
            exp = EXPECTED[p.problem_id]
            results[model].append({
                "problem": p.problem_id, "expected": exp,
                "elapsed_s": round(dur, 1), "status": status,
                "correct": correct, "answer": ans,
                "raw_tail": out[-150:],
            })
            json.dump(results, open(OUT, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
            print(f"{model.split('/')[-1][:12]:12s} {p.problem_id[-12:]:12s} "
                  f"{dur:6.1f}s {status:7s} correct={correct} ans={str(ans)[:14]}",
                  flush=True)
    print("\nResumo 9x3:")
    for model, rs in results.items():
        print(f"  {model:34s} {sum(r['correct'] for r in rs)}/{len(rs)} "
              f"acc={sum(r['correct'] for r in rs)/len(rs):.2f}")


if __name__ == "__main__":
    main()