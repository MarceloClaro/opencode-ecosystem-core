# -*- coding: utf-8 -*-
"""Estudo de caso com agentes reais do catálogo (R776+). Tarefas desenhadas
no vocabulário real de tags; registra elegíveis, cabeças, utilidades,
pesos, latência e soma. Uso: python3 estudo_caso_reais.py"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
import time

sys.path.insert(0, "/home/marceloclaro/opencode-ecosystem-core")

from transformer.attention import AttentionRouter  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
SEL = ["coder", "researcher", "reviewer", "architect", "auditor",
       "technical-writer", "test-engineer", "debugger", "docs-writer",
       "code-reviewer", "optimizer", "security-auditor"]
TASKS = [
    ("Refatorar modulo Python com testes primeiro",
     ["python", "refactor"]),
    ("Revisar codigo buscando falhas de seguranca",
     ["revisa", "seguranca"]),
    ("Comparar revisores para tarefa de revisao",
     ["reviewer"]),
    ("Auditar metricas de integracao continua",
     ["audit", "metrics"]),
    ("Escrever documentacao de projeto",
     ["docs", "escreve"]),
]


def load_cards():
    cards = []
    for path in sorted(glob.glob(
            "/home/marceloclaro/opencode-ecosystem-core/agents/catalog/*.md")):
        text = open(path, encoding="utf-8").read()
        name = re.search(r"^name:\s*(\S+)", text, re.M)
        if not (name and name.group(1) in SEL):
            continue
        tags = re.search(r"^tags:\s*\[(.*?)\]", text, re.M)
        desc = re.search(r"^description:\s*\"(.*?)\"", text, re.M)
        cards.append({
            "agent_id": name.group(1),
            "status": "available",
            "capabilities": [x.strip() for x in tags.group(1).split(",")] if tags else [],
            "description": desc.group(1) if desc else name.group(1),
            "load": 0.0,
            "confidence_score": 0.5,
        })
    return cards


def main():
    router = AttentionRouter()
    cards = load_cards()
    out = {"n_agentes": len(cards), "tarefas": []}
    for desc, req in TASKS:
        t0 = time.perf_counter()
        ev = router._evaluate(desc, req, cards)
        dt = (time.perf_counter() - t0) * 1000.0
        soma = sum(w for _, w in ev["ranking"])
        out["tarefas"].append({
            "descricao": desc, "requeridas": req,
            "elegiveis": ev["eligible"], "excluidos": len(ev["excluded"]),
            "ranking": [[a, round(p, 4)] for a, p in ev["ranking"]],
            "soma_pesos": round(soma, 10), "lat_ms": round(dt, 2),
            "cabecas_top1": {k: round(ev["heads"][k][ev["ranking"][0][0]], 4)
                             for k in ev["heads"]}
            if ev["ranking"] else {},
        })
        top = ev["ranking"][0][0] if ev["ranking"] else "-"
        print(f"{desc[:42]:44s} elig={len(ev['eligible'])} top={top} "
              f"soma={soma:.6f} {dt:.1f}ms")
    with open(os.path.join(BASE, "estudo_caso_reais.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("OK", out["n_agentes"], "agentes,",
          len(out["tarefas"]), "tarefas")


if __name__ == "__main__":
    main()
