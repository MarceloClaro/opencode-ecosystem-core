# -*- coding: utf-8 -*-
"""Ablações da bancada: ataca a circularidade da confiança e compara forte.

- conf_embaralhada: permuta confidence_score (quebra proxy com q).
- conf_anticorrelacionada: conf = 1 - conf (inversão adversarial).
- conf_ruidosa: ruído N(0, 0.4) reamostrado (mal calibrada).
- media_igual: utilidade = média das 4 cabeças reais (comparador forte).
- sem_confianca: utilidade sem a cabeça confidence, renormalizada.
- Estatística pareada por decisão: diff de regret vs atenção + taxa de vitória.
Uso: python3 bancada_ablacao.py (lê mesmos seeds/tasks da bancada).
"""
from __future__ import annotations

import json
import math
import os
import random
import statistics
import sys

sys.path.insert(0, "/home/marceloclaro/opencode-ecosystem-core")

from transformer.attention import AttentionRouter  # noqa: E402

from bancada_routing import (  # noqa: E402
    make_pool, make_task, ci95,
)

BASE = os.path.dirname(os.path.abspath(__file__))
PESOS = {"semantic": 0.30, "capability": 0.35, "confidence": 0.25, "load": 0.10}


def top1_ordenado(pesos):
    return sorted(pesos.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def oracle_qw(card, req, latent, qw):
    cov = len(set(card["capabilities"]) & set(req)) / len(req)
    return cov * ((1.0 - qw) + qw * latent[card["agent_id"]])


def run_seed(seed: int, n_tasks: int = 40, qw: float = 0.6):
    rng = random.Random(10_000 + seed)
    router = AttentionRouter()
    pool, latent = make_pool(rng)
    rows = []
    for t in range(n_tasks):
        desc, req, elig = make_task(rng, pool)
        eids = [c["agent_id"] for c in elig]
        oracle = {c["agent_id"]: oracle_qw(c, req, latent, qw) for c in elig}
        best = max(oracle.values())
        ev = router._evaluate(desc, req, pool)
        heads, util = ev["heads"], ev["utility"]
        row = {"seed": seed, "task": t, "oracle_best": best}
        # atenção real
        pick = ev["ranking"][0][0]
        row["atencao"] = best - oracle[pick]
        # pools com confiança atacada
        confs = [c["confidence_score"] for c in pool]
        for nome, novo in (
            ("conf_embaralhada", rng.sample(confs, len(confs))),
            ("conf_anticorrelacionada",
             [round(1.0 - v, 3) for v in confs]),
            ("conf_ruidosa",
             [round(min(1.0, max(0.0, v + rng.gauss(0, 0.4))))
              for v in confs]),
        ):
            pool2 = [dict(c, confidence_score=n)
                     for c, n in zip(pool, novo)]
            r2 = router.route(desc, req, pool2)
            row[nome] = best - oracle[r2[0][0]]
        # comparadores fortes sobre as cabeças reais
        util_eq = {a: sum(heads[h][a] for h in PESOS) / 4.0
                   for a in eids}
        row["media_igual"] = best - oracle[top1_ordenado(util_eq)]
        wn = {h: PESOS[h] / 0.75 for h in PESOS if h != "confidence"}
        util_nc = {a: sum(wn[h] * heads[h][a] for h in wn)
                   for a in eids}
        row["sem_confianca"] = best - oracle[top1_ordenado(util_nc)]
        rows.append(row)
    return rows


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--qw", type=float, default=0.6)
    args = ap.parse_args()
    rows = []
    for s in (11, 22, 33, 44, 55):
        rows += run_seed(s, qw=args.qw)
    n = len(rows)
    res = {"n_decisoes": n, "qw": args.qw, "estrategias": {}}
    base = [r["atencao"] for r in rows]
    for k in ("atencao", "conf_embaralhada", "conf_anticorrelacionada",
              "conf_ruidosa", "media_igual", "sem_confianca"):
        m, h = ci95([r[k] for r in rows])
        res["estrategias"][k] = {"regret_medio": m, "regret_ci95": h}
    for k in res["estrategias"]:
        if k == "atencao":
            continue
        diffs = [r[k] - r["atencao"] for r in rows]
        m, h = ci95(diffs)
        wins = sum(1 for r in rows if r["atencao"] <= r[k]) / n
        res["estrategias"][k]["diff_pareado_medio"] = m
        res["estrategias"][k]["diff_pareado_ci95"] = h
        res["estrategias"][k]["atencao_vence_ou_empata"] = wins
    tag = f"_q{args.qw}".replace(".", "p")
    with open(os.path.join(BASE, f"resultado_ablacao{tag}.json"), "w",
              encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(f"qw={args.qw}")
    for k, v in res["estrategias"].items():
        extra = (f" diff={v['diff_pareado_medio']:+.4f}±{v['diff_pareado_ci95']:.4f}"
                 f" win={v['atencao_vence_ou_empata']:.3f}"
                 if k != "atencao" else "")
        print(f"{k:24s} regret={v['regret_medio']:.4f}±{v['regret_ci95']:.4f}"
              f"{extra}")


if __name__ == "__main__":
    main()
