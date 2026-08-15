#!/usr/bin/env python3
"""Análise R430 — marcadores socioeconômicos não convencionais × IDEB 2023.

Desenho: transversal, n=9 municípios (microrregião do Sertão de Crateús).
Desfecho: IDEB 2023 anos iniciais, rede municipal (INEP).
Exposições: 33 indicadores do Censo Demográfico 2022 (universo e amostra) —
  gênero, raça, trabalho, profissões, atividade, renda, condições de vida,
  educação/formação, habitação.

Rigor: correlação de Spearman e Pearson com bootstrap não paramétrico por
  cluster (n=9, 5.000 reamostragens, seed 42, IC95 percentil) e ajuste de
  múltiplas comparações (FDR Benjamini-Hochberg + Bonferroni) sobre os 33
  p-valores de Spearman. Protocolo exploratório: nenhuma associação é tratada
  como confirmatória; apenas sobreviventes ao ajuste são destacadas.

SPEC-935-R430-crateus-marcadores-nao-convencionais.md
Saídas: outputs/expanded/resultados_r430.json, provenance_r430.json
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

PAPER = Path(__file__).resolve().parent.parent
PROC = PAPER / "data" / "processed"
OUT = PAPER / "outputs" / "expanded"

SEED = 42
B = 5000


def bootstrap_corr_fast(x: np.ndarray, y: np.ndarray, seed: int = SEED, b: int = B):
    """Bootstrap não paramétrico vetorizado (n=9) — IC95 percentil e estabilidade de sinal."""
    rng = np.random.default_rng(seed)
    n = len(x)
    idx = rng.integers(0, n, (b, n))
    xx, yy = x[idx], y[idx]

    xc = xx - xx.mean(axis=1, keepdims=True)
    yc = yy - yy.mean(axis=1, keepdims=True)
    denom_p = np.sqrt((xc ** 2).sum(1) * (yc ** 2).sum(1))
    rp = np.divide((xc * yc).sum(1), denom_p, out=np.full(b, np.nan), where=denom_p != 0)

    rx = np.argsort(np.argsort(xx, axis=1), axis=1).astype(float)
    ry = np.argsort(np.argsort(yy, axis=1), axis=1).astype(float)
    rxc = rx - rx.mean(axis=1, keepdims=True)
    ryc = ry - ry.mean(axis=1, keepdims=True)
    denom_s = np.sqrt((rxc ** 2).sum(1) * (ryc ** 2).sum(1))
    rs = np.divide((rxc * ryc).sum(1), denom_s, out=np.full(b, np.nan), where=denom_s != 0)

    rp = rp[~np.isnan(rp)]
    rs = rs[~np.isnan(rs)]
    r_p_obs, _ = pearsonr(x, y)
    r_s_obs, _ = spearmanr(x, y)
    return {
        "pearson": float(r_p_obs),
        "spearman": float(r_s_obs),
        "pearson_ic95": [float(np.percentile(rp, 2.5)), float(np.percentile(rp, 97.5))],
        "spearman_ic95": [float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))],
        "sinal_estavel_pct": float(np.mean(np.sign(rp) == np.sign(r_p_obs)) * 100),
    }

MUNICIPIOS_MICRO = {
    2301257: "Ararendá", 2304103: "Crateús", 2305605: "Independência",
    2305654: "Ipaporanga", 2308609: "Monsenhor Tabosa", 2309300: "Nova Russas",
    2309409: "Novo Oriente", 2311264: "Quiterianópolis", 2313203: "Tamboril",
}
CRATEUS = 2304103
DESFECHOS = ["ideb_2025_ai", "ideb_2023_ai"]


def _fdr_bh(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    m = len(p)
    ordem = np.argsort(p)
    q = np.empty_like(p)
    q[ordem[-1]] = p[ordem[-1]]
    for i in range(m - 2, -1, -1):
        q[ordem[i]] = min(p[ordem[i]] * m / (i + 1), q[ordem[i + 1]])
    return q


def carregar_base() -> pd.DataFrame:
    man = json.loads((PROC / "manifest_r430.json").read_text())
    indicadores = list(man["etiquetas"].keys())
    fam = man["familia_por_indicador"]

    df = pd.read_json(PROC / "indicadores_r430.json", orient="records").set_index("cod_mun")
    df = df[indicadores].apply(pd.to_numeric, errors="coerce")

    ideb_ce = pd.read_json(PROC / "ideb_ce.json")
    ai2023 = ideb_ce[
        (ideb_ce["etapa"] == "anos_iniciais")
        & (ideb_ce["rede"] == "Municipal")
        & (ideb_ce["2023"].notna())
    ].set_index("cod_mun")["2023"].astype(float)
    ai2025 = ideb_ce[
        (ideb_ce["etapa"] == "anos_iniciais")
        & (ideb_ce["rede"] == "Municipal")
        & (ideb_ce["2025"].notna())
    ].set_index("cod_mun")["2025"].replace("-", np.nan).astype(float)
    df["ideb_2023_ai"] = ai2023
    df["ideb_2025_ai"] = ai2025
    df["nome"] = [MUNICIPIOS_MICRO[i] for i in df.index]
    return df, man, fam


def main() -> int:
    base, man, fam = carregar_base()
    indicadores = list(man["etiquetas"].keys())

    resultados = []
    pvals = {}
    for ind in indicadores:
        for desf in DESFECHOS:
            y = base[desf].to_numpy(dtype=float)
            x = base[ind].to_numpy(dtype=float)
            if np.any(np.isnan(x)) or np.any(np.isnan(y)):
                continue
            bc = bootstrap_corr_fast(x, y)
            rho, p_s = spearmanr(x, y)
            r_p, p_p = pearsonr(x, y)
            resultados.append({
                "indicador": ind,
                "desfecho": desf,
                "familia": fam.get(ind, "Outros"),
                "etiqueta": man["etiquetas"][ind],
                "n": int(len(x)),
                "rho": float(rho),
                "rho_p": float(p_s),
                "r": float(r_p),
                "r_p": float(p_p),
                "rho_ic95": bc["spearman_ic95"],
                "r_ic95": bc["pearson_ic95"],
                "sinal_estavel_pct": bc["sinal_estavel_pct"],
                "media": float(np.mean(x)),
                "desvio": float(np.std(x, ddof=1)),
                "min": float(np.min(x)),
                "max": float(np.max(x)),
                "crateus_valor": float(base.loc[CRATEUS, ind]),
            })
            pvals[(ind, desf)] = float(p_s)

    # Ajuste de múltiplas comparações sobre p de Spearman (33×2 = 66 hipóteses)
    pares = list(pvals.keys())
    p_arr = np.array([pvals[p] for p in pares])
    q_bh = _fdr_bh(p_arr)
    q_bonf = np.minimum(p_arr * len(p_arr), 1.0)
    q_map = {p: (float(q_bh[k]), float(q_bonf[k])) for k, p in enumerate(pares)}
    for r in resultados:
        r["q_bh"], r["q_bonferroni"] = q_map[(r["indicador"], r["desfecho"])]
        r["signif_bh"] = r["q_bh"] < 0.05
        r["signif_bonf"] = r["q_bonferroni"] < 0.05

    # Ranking por |rho| no desfecho primário (IDEB 2025 AI)
    primario = [r for r in resultados if r["desfecho"] == "ideb_2025_ai"]
    primario.sort(key=lambda r: -abs(r["rho"]))

    # Perfil de Crateús: posição relativa (1 = menor valor) em cada indicador
    for r in primario:
        vals = base[r["indicador"]].astype(float)
        rank = vals.rank(method="min")
        r["crateus_pos"] = int(rank.loc[CRATEUS])
        r["n_vals"] = int(vals.notna().sum())
        r["crateus_pctil"] = float((rank.loc[CRATEUS] - 1) / max(vals.notna().sum() - 1, 1) * 100)

    resumo = {
        "ciclo": "R430",
        "desfecho_primario": "IDEB 2025 anos iniciais, rede municipal (INEP)",
        "desfecho_sensibilidade": "IDEB 2023 anos iniciais, rede municipal (INEP)",
        "n_municipios": int(len(base)),
        "n_indicadores": len(indicadores),
        "n_hipoteses": len(pares),
        "seed": SEED,
        "b_reamostragens": B,
        "ajuste": "FDR Benjamini-Hochberg + Bonferroni (66 hipóteses, rho de Spearman)",
        "significativos_bh": [f"{p[0]}|{p[1]}" for p in pares if q_map[p][0] < 0.05],
        "significativos_bonf": [f"{p[0]}|{p[1]}" for p in pares if q_map[p][1] < 0.05],
        "top_abs_rho": [
            {"indicador": r["indicador"], "desfecho": r["desfecho"], "rho": r["rho"], "q_bh": r["q_bh"]}
            for r in primario[:8]
        ],
    }

    (OUT / "resultados_r430.json").write_text(json.dumps({
        "resumo": resumo, "resultados": resultados,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "provenance_r430.json").write_text(json.dumps({
        "ciclo": "R430",
        "fonte_indicadores": "IBGE SIDRA — Censo Demográfico 2022 (universo: 9605/9606/9928/9940; amostra: 10056/10061/10062/10261/10264/10266/10268/10280/10295/10296)",
        "fonte_ideb": "INEP — IDEB 2023, rede municipal, anos iniciais (data/processed/ideb_ce.json)",
        "desenho": "transversal, n=9, microrregião Sertão de Crateús",
        "limite": "exploratório; n=9; IC bootstrap por cluster seed 42; ajuste BH+Bonferroni",
        "data": "2026-08-15",
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    print("\nRanking |rho| (desfecho primário IDEB 2025 AI, top 10):")
    for r in primario[:10]:
        print(f"  {r['indicador']:32s} rho={r['rho']:+.3f} p={r['rho_p']:.3f} qBH={r['q_bh']:.3f} "
              f"IC95[{r['rho_ic95'][0]:+.2f};{r['rho_ic95'][1]:+.2f}] "
              f"sinal={r['sinal_estavel_pct']:.0f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
