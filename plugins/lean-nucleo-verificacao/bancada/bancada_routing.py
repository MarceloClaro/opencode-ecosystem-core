# -*- coding: utf-8 -*-
"""Bancada honesta do roteamento por atenção vs baselines (R756+).

Oráculo oculto (qualidade latente q): o roteador nunca vê q; vê apenas
cobertura, confiança ruidosa, carga e semântica. Comparação não-circular.
Determinístico por seed. Uso: python3 bancada_routing.py [--seeds 11,22,33,44,55]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import statistics
import sys
import time

sys.path.insert(0, "/home/marceloclaro/opencode-ecosystem-core")

from transformer.attention import AttentionRouter  # noqa: E402

VOCAB = [f"cap_{c}" for c in
         ["formal", "revisao", "dados", "codigo", "geo", "bio", "nlp",
          "visao", "ml", "qa", "latex", "etica"]]
NOISE_WORDS = ["análise", "síntese", "relatório", "urgente", "rotina", "projeto"]


def make_pool(rng: random.Random, n_agents: int = 40):
    pool, latent = [], {}
    for k in range(n_agents):
        aid = f"ag_{k:02d}"
        caps = rng.sample(VOCAB, rng.randint(3, 6))
        q = rng.random()
        pool.append({
            "agent_id": aid,
            "status": "available",
            "capabilities": caps,
            "description": f"Agente {aid} especialista em " + ", ".join(caps),
            "load": round(rng.uniform(0.0, 0.9), 3),
            "confidence_score": round(min(1.0, max(0.0, q + rng.gauss(0, 0.15))), 3),
        })
        latent[aid] = q
    return pool, latent


def make_task(rng: random.Random, pool):
    for _ in range(50):  # garante >=4 elegíveis
        req = sorted(rng.sample(VOCAB, rng.randint(2, 3)))
        elig = [c for c in pool if set(req) <= set(c["capabilities"])]
        if len(elig) >= 4:
            desc = ("Tarefa requer " + ", ".join(req) + " "
                    + " ".join(rng.sample(NOISE_WORDS, 2)))
            return desc, req, elig
    raise RuntimeError("falha ao gerar tarefa elegível")


def oracle_u(card, req, latent):
    cov = len(set(card["capabilities"]) & set(req)) / len(req)
    return cov * (0.4 + 0.6 * latent[card["agent_id"]])


def ci95(vals):
    n = len(vals)
    m = statistics.fmean(vals)
    if n < 2:
        return m, 0.0
    sd = statistics.pstdev(vals)
    return m, 1.96 * sd / math.sqrt(n)


def run_seed(seed: int, n_tasks: int = 40):
    rng = random.Random(seed)
    router = AttentionRouter()
    pool, latent = make_pool(rng)
    out = []
    for t in range(n_tasks):
        desc, req, elig = make_task(rng, pool)
        oracle = {c["agent_id"]: oracle_u(c, req, latent) for c in elig}
        best = max(oracle.values())
        row = {"seed": seed, "task": t, "n_elig": len(elig),
               "oracle_best": best}
        # atenção
        t0 = time.perf_counter()
        ranking = router.route(desc, req, pool)
        dt = time.perf_counter() - t0
        top1 = ranking[0][0]
        row["atencao_escolha"] = top1
        row["atencao_regret"] = best - oracle[top1]
        row["atencao_hit"] = 1 if oracle[top1] == best else 0
        row["atencao_lat_ms"] = dt * 1000.0
        row["softmax_sum"] = sum(w for _, w in ranking)
        # baselines sobre elegíveis
        row["aleatorio_escolha"] = rng.choice(elig)["agent_id"]
        row["menor_carga_escolha"] = min(elig, key=lambda c: c["load"])["agent_id"]
        covs = [(len(set(c["capabilities"]) & set(req)), c) for c in elig]
        maxcov = max(c[0] for c in covs)
        row["maior_cobertura_escolha"] = rng.choice(
            [c["agent_id"] for v, c in covs if v == maxcov])
        for b in ("aleatorio", "menor_carga", "maior_cobertura"):
            pick = row[f"{b}_escolha"]
            row[f"{b}_regret"] = best - oracle[pick]
            row[f"{b}_hit"] = 1 if oracle[pick] == best else 0
        out.append(row)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="11,22,33,44,55")
    ap.add_argument("--tasks", type=int, default=40)
    args = ap.parse_args()
    rows = []
    for s in [int(x) for x in args.seeds.split(",")]:
        rows += run_seed(s, args.tasks)
    res = {"seeds": args.seeds, "n_decisoes": len(rows)}
    for b in ("atencao", "aleatorio", "menor_carga", "maior_cobertura"):
        m, h = ci95([r[f"{b}_regret"] for r in rows])
        hm, hh = ci95([r[f"{b}_hit"] for r in rows])
        res[b] = {"regret_medio": m, "regret_ci95": h,
                  "hit_rate": hm, "hit_ci95": hh}
    lat = [r["atencao_lat_ms"] for r in rows]
    res["atencao_lat_ms"] = {"media": statistics.fmean(lat),
                             "max": max(lat)}
    dev = max(abs(r["softmax_sum"] - 1.0) for r in rows)
    res["softmax_desvio_max"] = dev
    res["amostra"] = rows[:3]
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "resultado_bancada.json"), "w",
              encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    for b in ("atencao", "aleatorio", "menor_carga", "maior_cobertura"):
        r = res[b]
        print(f"{b:15s} regret={r['regret_medio']:.4f}±{r['regret_ci95']:.4f} "
              f"hit={r['hit_rate']:.3f}±{r['hit_ci95']:.3f}")
    print(f"lat_med={res['atencao_lat_ms']['media']:.2f}ms "
          f"max={res['atencao_lat_ms']['max']:.2f}ms "
          f"softmax_dev_max={dev:.2e} n={len(rows)}")


if __name__ == "__main__":
    main()
