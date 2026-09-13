# -*- coding: utf-8 -*-
"""Benchmark comparativo de LLMs free reais do OpenCode Ecosystem (R499-raiox).

Condições controladas (mesma tarefa IMO, variando apenas a camada de
orquestração):
  C0 raw   : prompt direto, sem orquestração
  C1 ctx   : prompt + contexto do estudo (dados reais do MetaBus/estudo)
  C2 maswos: prompt com scaffold MASWOS (instrução de estágio estruturada)

Métricas: latência (s), comprimento, exatidão (contém resposta correta),
conformidade (responde apenas o que foi pedido), status.
"""

from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

MODELS = ["opencode/mimo-v2.5-free", "opencode/nemotron-3-ultra-free"]

TASK = (
    "Encontre todos os pares de primos (p, q) tais que p^3 - q^5 = (p+q)^2. "
    "Responda com o par (p,q) encontrado e uma linha de verificação."
)

CONTEXT = (
    "Contexto do estudo IMO-AnswerBench (Shortlist 2022, teoria dos números): "
    "o solver determinístico enumerou primos 2..400 e encontrou o par (7,3): "
    "7^3 - 3^5 = 343 - 243 = 100 = (7+3)^2. " + TASK
)

MASWOS_SCAFFOLD = (
    "Você é o estágio '03-resultados' do pipeline acadêmico MASWOS do "
    "OpenCode Ecosystem Core (capacidade: redação de resultados com precisão). "
    "Escreva APENAS o par de primos (p,q) que satisfaz p^3 - q^5 = (p+q)^2 e "
    "a linha de verificação aritmética, sem texto introdutório."
)


@dataclass
class Trial:
    model: str
    condition: str
    elapsed_s: float
    output: str
    status: str
    correct: bool = False
    conforming: bool = False

    def metrics(self) -> dict:
        return {
            "model": self.model,
            "condition": self.condition,
            "elapsed_s": round(self.elapsed_s, 2),
            "chars": len(self.output),
            "correct": self.correct,
            "conforming": self.conforming,
            "status": self.status,
            "output_head": self.output[:140],
        }


def ask(prompt: str, model: str) -> tuple[str, float, str]:
    t0 = time.time()
    try:
        res = subprocess.run(
            ["opencode", "run", prompt, "-m", model],
            capture_output=True, text=True, timeout=110,
            env={"PATH": "/home/marceloclaro/.npm-global/bin:/usr/bin:/bin",
                 "HOME": "/home/marceloclaro"},
        )
        raw = re.sub(r"\x1b\[[0-9;]*m", "", res.stdout or "")
        out = " ".join(l.strip() for l in raw.splitlines()
                       if l.strip() and not l.strip().startswith(">"))
        status = "ok" if ("7, 3" in out or "(7,3)" in out or "(7, 3)" in out
                          or "erro" not in (res.stderr or "").lower()
                          and out.strip()) else ("vazio" if not out.strip() else "sem-evidencias")
        return out.strip(), time.time() - t0, status
    except subprocess.TimeoutExpired:
        return "", 110.0, "timeout"
    except Exception as exc:  # noqa: BLE001
        return "", time.time() - t0, f"erro:{exc}"


def run_battery(out_path: Path) -> list[dict]:
    trials: list[Trial] = []
    for model in MODELS:
        for cond, prompt in (("raw", TASK), ("ctx", CONTEXT), ("maswos", MASWOS_SCAFFOLD)):
            out, elapsed, status = ask(prompt, model)
            t = Trial(model=model, condition=cond, elapsed_s=elapsed,
                      output=out, status=status)
            t.correct = bool(re.search(r"7\s*,\s*3|\(7,3\)|\(7, 3\)", out))
            t.conforming = bool(re.match(r"^\s*(\(?\s*7\s*,\s*3\s*\)?|7\^3)", out))
            trials.append(t)
            print(f"[{model.split('/')[-1]:22s} {cond:6s}] {t.elapsed_s:6.1f}s "
                  f"correct={t.correct} conf={t.conforming} status={status} chars={len(out):4d}",
                  flush=True)
    out_path.write_text(
        json.dumps([t.metrics() for t in trials], ensure_ascii=False, indent=2),
        encoding="utf-8")
    return [t.metrics() for t in trials]


if __name__ == "__main__":
    p = Path("research/imo_study/llm_free_benchmark.json")
    run_battery(p)
    print("salvo:", p)