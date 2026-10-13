# -*- coding: utf-8 -*-
"""Cálculos ainda não correlacionados (R763): Pearson entre variáveis que a
bancada principal não cruzou. Reexecuta os seeds (determinístico) coletando,
por decisão: regret, acerto, n_elegíveis, dispersão do oráculo, escores das
4 cabeças por elegível e qualidade latente. Sem pacotes externos.
Uso: python3 correlacoes.py
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
    make_pool, make_task,
)
from bancada_ablacao import oracle_qw  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))


def pearson(xs, ys):
    n = len(xs)
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / n)
    sy = math.sqrt(sum((y - my) ** 2 for y in ys) / n)
    if sx == 0.0 or sy == 0.0:
        return None
    return cov / (sx * sy)


def main(qw: float = 0.6):
    router = AttentionRouter()
    regret, hit, nelig, spread = [], [], [], []
    heads = {"semantic": [], "capability": [], "confidence": [], "load": []}
    conf_q = ([], [])
    for seed in (11, 22, 33, 44, 55):
        rng = random.Random(10_000 + seed)
        pool, latent = make_pool(rng)
        for _ in range(40):
            desc, req, elig = make_task(rng, pool)
            oracle = {c["agent_id"]: oracle_qw(c, req, latent, qw)
                      for c in elig}
            best = max(oracle.values())
            lo = min(oracle.values())
            ev = router._evaluate(desc, req, pool)
            pick = ev["ranking"][0][0]
            regret.append(best - oracle[pick])
            hit.append(1 if oracle[pick] == best else 0)
            nelig.append(len(elig))
            spread.append(best - lo)
            for h in heads:
                for c in elig:
                    heads[h].append(ev["heads"][h][c["agent_id"]])
            for c in elig:
                conf_q[0].append(c["confidence_score"])
                conf_q[1].append(latent[c["agent_id"]])
    res = {
        "n_decisoes": len(regret),
        "nota": "null = variância zero (ex.: capability é 1.0 p/ todo elegível: o gate já decidiu; a escolha corre nas outras 3 cabeças)",
        "pearson": {
            "regret_x_n_elegiveis": pearson(regret, nelig),
            "regret_x_dispersao_oraculo": pearson(regret, spread),
            "acerto_x_n_elegiveis": pearson(hit, nelig),
            "acerto_x_dispersao_oraculo": pearson(hit, spread),
            "confianca_x_q_latente": pearson(*conf_q),
        },
        "correlacao_cabecas": {},
    }
    nomes = list(heads)
    for i in range(len(nomes)):
        for j in range(i + 1, len(nomes)):
            res["correlacao_cabecas"][f"{nomes[i]}_x_{nomes[j]}"] = \
                pearson(heads[nomes[i]], heads[nomes[j]])
    with open(os.path.join(BASE, "correlacoes.json"), "w",
              encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(f"n={res['n_decisoes']}")
    for k, v in res["pearson"].items():
        print(f"{k:28s} r={v:+.3f}" if v is not None else f"{k:28s} nula (constante)")
    for k, v in res["correlacao_cabecas"].items():
        print(f"{k:28s} r={v:+.3f}" if v is not None else f"{k:28s} nula (constante)")


if __name__ == "__main__":
    main()
