#!/usr/bin/env python3
"""Análise Crateús-IDEB (R426) — espelho metodológico da ARM.

Testa se o padrão associativo nacional (ARM: forte em níveis, fraca dentro
da unidade) se reproduz no nível municipal da microrregião do Sertão de
Cratéus (CE), usando IDEB × PIB per capita municipal.

Validações (espelho ARM R410-R425):
- H1: correlação transversal (níveis) + bootstrap por município (IC95)
- H2: primeiras diferenças + painel com efeitos fixos (município e ano)
- LOOCV por município (9 folds)
- MDES/TOST (poder 80%, α 5%, equivalência ±0,10)
- H3: ganho IDEB vs meta projetada (INEP) e associação com renda
- Robustez: microrregião × CE × BR

Gera outputs/expanded/*.json + provenance_r426.json.
Uso: python3 scripts/analise_crateus.py
"""
from __future__ import annotations

import hashlib
import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import t as tdist

warnings.filterwarnings("ignore")

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "data" / "processed"
OUT = RAIZ / "outputs" / "expanded"
OUT.mkdir(parents=True, exist_ok=True)
SEED = 42
rng = np.random.default_rng(SEED)

MUNICIPIOS_MICRO = [
    2301257, 2304103, 2305605, 2305654, 2308609,
    2309300, 2309409, 2311264, 2313203,
]
NOMES_MICRO = {
    2301257: "Ararendá", 2304103: "Crateús", 2305605: "Independência",
    2305654: "Ipaporanga", 2308609: "Monsenhor Tabosa", 2309300: "Nova Russas",
    2309409: "Novo Oriente", 2311264: "Quiterianópolis", 2313203: "Tamboril",
}
DEFASAGEM = 2  # anos (PIB defasado vs IDEB)
META_ANO = 2021  # última meta pactuada (VL_PROJECAO_2021)


def corr_pearson(x: np.ndarray, y: np.ndarray) -> float:
    xm = x - x.mean()
    ym = y - y.mean()
    den = np.sqrt((xm * xm).sum() * (ym * ym).sum())
    return float((xm * ym).sum() / den) if den > 0 else float("nan")


def bootstrap_ic(x: np.ndarray, y: np.ndarray, grupos: np.ndarray, b: int = 2000) -> dict:
    """Bootstrap por cluster (município) da correlação de Pearson (vetorizado)."""
    g = np.unique(grupos)
    r = corr_pearson(x, y)
    # índices das observações de cada cluster
    idxs = [np.flatnonzero(grupos == gi) for gi in g]
    n_por_cluster = np.array([len(i) for i in idxs])
    reps = np.empty(b)
    for k in range(b):
        sel = rng.choice(len(g), size=len(g), replace=True)
        idx = np.concatenate([idxs[j] for j in sel])
        if len(idx) >= 3 and np.std(x[idx]) > 0 and np.std(y[idx]) > 0:
            reps[k] = corr_pearson(x[idx], y[idx])
        else:
            reps[k] = np.nan
    reps = reps[~np.isnan(reps)]
    p = stats.pearsonr(x, y).pvalue if len(x) > 2 else float("nan")
    return {
        "r": round(float(r), 4),
        "ic95_inf": round(float(np.percentile(reps, 2.5)), 4),
        "ic95_sup": round(float(np.percentile(reps, 97.5)), 4),
        "n": int(len(x)),
        "n_clusters": int(len(g)),
        "p_valor": round(float(p), 4),
        "bootstrap_b": b,
        "seed": SEED,
    }


def fe_duplo(d: pd.DataFrame, y: str, x: str) -> dict:
    """Efeitos fixos de município E ano via within-transformation iterativa.

    Retorna SE homocedástico (transparência) e SE clusterizado por município
    (CRVE com correção de pequena amostra; t com G-1 graus de liberdade),
    espelhando o protocolo da ARM (R410-R412).
    """
    yv = d[y].astype(float).values
    xv = d[x].astype(float).values
    g = d["cod_mun"].values
    t = d["ano_ideb"].values
    n = len(d)
    n_mun = d["cod_mun"].nunique()
    n_ano = d["ano_ideb"].nunique()
    # demean iterativo (two-way within)
    yw, xw = yv.copy(), xv.copy()
    for _ in range(200):
        y_old, x_old = yw.copy(), xw.copy()
        yw -= pd.Series(yw).groupby(g).transform("mean").values
        xw -= pd.Series(xw).groupby(g).transform("mean").values
        yw -= pd.Series(yw).groupby(t).transform("mean").values
        xw -= pd.Series(xw).groupby(t).transform("mean").values
        if np.max(np.abs(yw - y_old)) < 1e-10 and np.max(np.abs(xw - x_old)) < 1e-10:
            break
    den = float((xw * xw).sum())
    if den == 0 or np.std(yw) == 0:
        return {"erro": "sem variância dentro"}
    coef = float((xw * yw).sum() / den)
    resid = yw - coef * xw

    # SE homocedástico
    k = n_mun + n_ano + 1
    dof = n - k
    se_homo = float(np.sqrt((resid * resid).sum() / max(dof, 1) / den))

    # SE clusterizado por município (CRVE) com correção de pequena amostra
    scores = np.array([
        float(np.sum(xw[g == gi] * resid[g == gi]))
        for gi in np.unique(g)
    ])
    g_clusters = int(len(scores))
    crve = float(np.sum(scores * scores) / den ** 2)
    # correção CR3-like: (G/(G-1)) * ((N-1)/(N-K))
    c_pequena = (g_clusters / max(g_clusters - 1, 1)) * ((n - 1) / max(n - k, 1))
    se_cluster = float(np.sqrt(crve * c_pequena))

    def _ic(se: float, df_t: int) -> tuple:
        tcrit = tdist.ppf(0.975, df_t)
        return (round(coef - tcrit * se, 4), round(coef + tcrit * se, 4))

    ic_homo = _ic(se_homo, max(dof, 5))
    ic_cluster = _ic(se_cluster, max(g_clusters - 1, 1))
    p_cluster = 2 * (1 - tdist.cdf(abs(coef / se_cluster), max(g_clusters - 1, 1)))
    return {
        "coef": round(coef, 4),
        "se": round(se_homo, 4),
        "ic95_inf": ic_homo[0], "ic95_sup": ic_homo[1],
        "p_valor": round(2 * (1 - tdist.cdf(abs(coef / se_homo), max(dof, 5))), 4),
        "se_cluster": round(se_cluster, 4),
        "ic95_cluster_inf": ic_cluster[0], "ic95_cluster_sup": ic_cluster[1],
        "p_valor_cluster": round(float(p_cluster), 4),
        "n_clusters": g_clusters,
        "n": int(n), "n_municipios": int(n_mun),
        "anos": sorted(d["ano_ideb"].unique().tolist()),
    }


def carregar_painel() -> pd.DataFrame:
    ideb = pd.read_json(PROC / "ideb_br.json", orient="records")
    pib = pd.read_json(PROC / "pib_br.json", orient="records")
    renda = pd.read_json(PROC / "renda_br.json", orient="records")

    ideb = ideb[ideb["rede"] == "Municipal"].copy()
    ideb["cod_mun"] = pd.to_numeric(ideb["cod_mun"], errors="coerce")
    anos_ideb = [str(a) for a in range(2005, 2026, 2)]
    ideb_long = ideb.melt(id_vars=["uf", "cod_mun", "nome_mun", "rede", "etapa"],
                          value_vars=anos_ideb, var_name="ano_ideb", value_name="ideb")
    ideb_long["ano_ideb"] = pd.to_numeric(ideb_long["ano_ideb"], errors="coerce")
    ideb_long["ideb"] = pd.to_numeric(ideb_long["ideb"], errors="coerce")
    ideb_long = ideb_long[ideb_long["ideb"].notna()]

    pib["ano"] = pd.to_numeric(pib["ano"], errors="coerce").astype(int)
    pib["pib_per_capita"] = pd.to_numeric(pib["pib_per_capita"], errors="coerce")

    # painel com PIB defasado (ano_ideb - DEFASAGEM)
    pib["ano_def"] = pib["ano"] + DEFASAGEM
    painel = ideb_long.merge(pib[["cod_mun", "ano_def", "pib_per_capita"]],
                             left_on=["cod_mun", "ano_ideb"], right_on=["cod_mun", "ano_def"],
                             how="left")
    for c in ["moradores", "renda_media_resp", "renda_mediana_resp"]:
        renda[c] = pd.to_numeric(renda[c], errors="coerce")
    painel = painel.merge(renda[["cod_mun", "moradores", "renda_media_resp", "renda_mediana_resp"]],
                          on="cod_mun", how="left")
    painel["log_pibpc"] = np.log(painel["pib_per_capita"])
    painel["micro"] = painel["cod_mun"].isin(MUNICIPIOS_MICRO)
    return painel


def analise_escala(painel: pd.DataFrame, nome: str, filtro: pd.Series) -> dict:
    d = painel[filtro].dropna(subset=["ideb", "log_pibpc"]).copy()
    if len(d) < 10:
        return {"escala": nome, "n_insuficiente": int(len(d))}

    # H1: níveis (transversal pooling)
    b = 2000 if d["cod_mun"].nunique() <= 50 else 500
    r_niveis = bootstrap_ic(d["ideb"].values, d["log_pibpc"].values, d["cod_mun"].values, b=b)

    # H2a: primeiras diferenças dentro do município
    d = d.sort_values(["cod_mun", "etapa", "ano_ideb"])
    d["d_ideb"] = d.groupby(["cod_mun", "etapa"])["ideb"].diff()
    d["d_logpib"] = d.groupby(["cod_mun", "etapa"])["log_pibpc"].diff()
    dd = d.dropna(subset=["d_ideb", "d_logpib"])
    r_1dif = None
    if len(dd) >= 10 and dd["d_logpib"].std() > 0 and dd["d_ideb"].std() > 0:
        r_1dif = {
            "r": round(float(stats.pearsonr(dd["d_ideb"], dd["d_logpib"]).statistic), 4),
            "p_valor": round(float(stats.pearsonr(dd["d_ideb"], dd["d_logpib"]).pvalue), 4),
            "n": int(len(dd)),
        }

    # H2b: FE município + ano (within duplo)
    fe = None
    try:
        fe = fe_duplo(d, "ideb", "log_pibpc")
    except Exception as e:  # pragma: no cover
        fe = {"erro": str(e)}

    return {"escala": nome, "niveis": r_niveis, "primeiras_diferencas": r_1dif, "fe": fe}


def loocv_municipio(painel: pd.DataFrame, filtro: pd.Series) -> dict:
    d = painel[filtro].dropna(subset=["ideb", "log_pibpc"]).copy()
    municipios = sorted(d["cod_mun"].unique())
    folds = []
    for held in municipios:
        treino = d[d["cod_mun"] != held]
        teste = d[d["cod_mun"] == held]
        if len(treino) >= 8 and len(teste) >= 2 and treino["log_pibpc"].std() > 0 and teste["ideb"].std() > 0:
            rt = stats.pearsonr(treino["ideb"], treino["log_pibpc"]).statistic
            if teste["log_pibpc"].std() > 0:
                re = stats.pearsonr(teste["ideb"], teste["log_pibpc"]).statistic
                folds.append({"municipio": int(held),
                              "nome": NOMES_MICRO.get(int(held), str(held)),
                              "r_treino": round(float(rt), 4),
                              "r_teste": round(float(re), 4),
                              "n_teste": int(len(teste))})
    if not folds:
        return {"n_folds": 0}
    r_teste = np.array([f["r_teste"] for f in folds])
    return {
        "n_folds": len(folds),
        "r_teste_media": round(float(r_teste.mean()), 4),
        "r_teste_mediana": round(float(np.median(r_teste)), 4),
        "r_teste_dp": round(float(r_teste.std()), 4),
        "pct_positivos": round(float((r_teste > 0).mean() * 100), 1),
        "folds": folds,
    }


def mdes_tost(fe: dict | None) -> dict | None:
    """MDES e TOST usando o SE clusterizado (G-1 dof) — conservador com 9 clusters.

    Reporta também o homocedástico como transparência.
    """
    if not fe or "coef" not in fe or "se_cluster" not in fe:
        return None
    n = fe["n"]
    g = fe["n_clusters"]
    se = fe["se_cluster"]
    df_cl = max(g - 1, 1)
    df_aprox = max(n - 3, 5)
    # MDES com cluster (dof = G-1) e com homocedástico (transparência)
    mdes_cluster = (tdist.ppf(0.975, df_cl) + tdist.ppf(0.8, df_cl)) * se
    mdes_homo = (tdist.ppf(0.975, df_aprox) + tdist.ppf(0.8, df_aprox)) * fe["se"]
    delta = 0.10
    t1 = (fe["coef"] + delta) / se
    t2 = (fe["coef"] - delta) / se
    p_tost = 1 - tdist.cdf(min(t1, -t2), df_cl)
    return {
        "mdes_cluster": round(float(mdes_cluster), 4),
        "mdes_homocedastico": round(float(mdes_homo), 4),
        "mdes": round(float(mdes_cluster), 4),
        "tost_delta": delta,
        "p_tost": round(float(p_tost), 4),
        "leitura": "não-detecção (não permite declarar equivalência)" if p_tost > 0.05 else "equivalência dentro de ±0,10",
        "nota": "MDES/TOST baseados no SE clusterizado por município (dof = G-1 = 8)",
    }


def h3_estagnacao(painel: pd.DataFrame, ideb_bruto: pd.DataFrame) -> dict:
    """Ganho IDEB 2007→último disponível vs meta pactuada (VL_PROJECAO_2021)."""
    proj = ideb_bruto[ideb_bruto["rede"] == "Municipal"].copy()
    proj["proj_2021"] = pd.to_numeric(proj["proj_2021"], errors="coerce")
    proj_map = proj.set_index(["cod_mun", "etapa"])["proj_2021"].to_dict()

    d = painel.dropna(subset=["ideb"]).copy()
    linhas = []
    for (cod, etapa), sub in d.groupby(["cod_mun", "etapa"]):
        base = sub[sub["ano_ideb"] == 2007]
        fim = sub[sub["ano_ideb"] == sub["ano_ideb"].max()]
        if base.empty or fim.empty:
            continue
        ideb_base = float(base["ideb"].iloc[0])
        ideb_fim = float(fim["ideb"].iloc[0])
        ano_fim = int(fim["ano_ideb"].iloc[0])
        ganho = ideb_fim - ideb_base
        meta = proj_map.get((cod, etapa), np.nan)
        atingiu = bool(ideb_fim >= meta) if not np.isnan(meta) else None
        linhas.append({"cod_mun": int(cod), "nome": NOMES_MICRO.get(int(cod), str(cod)),
                       "etapa": etapa, "ideb_2007": round(ideb_base, 2),
                       "ano_fim": ano_fim, "ideb_fim": round(ideb_fim, 2),
                       "ganho": round(ganho, 2), "meta_2021": None if np.isnan(meta) else round(meta, 2),
                       "atingiu_meta": atingiu})
    df_res = pd.DataFrame(linhas)
    if df_res.empty:
        return {"n": 0}

    # associação ganho × renda (proxy) — microrregião, anos iniciais, 1 obs por município
    renda = pd.read_json(PROC / "renda_ce.json", orient="records")
    renda["renda_media_resp"] = pd.to_numeric(renda["renda_media_resp"], errors="coerce")
    df_ai = df_res[(df_res["etapa"] == "anos_iniciais") & (df_res["cod_mun"].isin(MUNICIPIOS_MICRO))].copy()
    df_ai = df_ai.merge(renda[["cod_mun", "renda_media_resp"]], on="cod_mun", how="left")
    df_ai["ganho"] = pd.to_numeric(df_ai["ganho"], errors="coerce")
    ok = df_ai.dropna(subset=["ganho", "renda_media_resp"])
    r_ganho_renda = None
    if len(ok) >= 5 and ok["ganho"].std() > 0 and ok["renda_media_resp"].std() > 0:
        r_ganho_renda = {
            "r": round(float(stats.pearsonr(ok["ganho"], ok["renda_media_resp"]).statistic), 4),
            "p_valor": round(float(stats.pearsonr(ok["ganho"], ok["renda_media_resp"]).pvalue), 4),
            "n": int(len(ok)),
        }
    return {
        "n_linhas": int(len(df_res)),
        "ganho_medio_ai": round(float(df_ai["ganho"].mean()), 2) if len(df_ai) else None,
        "atingiu_meta_pct": round(float(df_res["atingiu_meta"].mean() * 100), 1) if df_res["atingiu_meta"].notna().any() else None,
        "correlacao_ganho_renda_ai": r_ganho_renda,
        "detalhe": df_res.to_dict(orient="records"),
    }


def salvar_json(obj, nome: str) -> None:
    (OUT / nome).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def principal() -> None:
    painel = carregar_painel()
    ideb_bruto = pd.read_json(PROC / "ideb_br.json", orient="records")

    micro = painel["micro"]
    ce = painel["cod_mun"].astype(str).str.startswith("23")
    brasil = pd.Series(True, index=painel.index)

    res_micro = analise_escala(painel, "microrregiao_sertao_crateus", micro)
    resultados = {
        "microrregiao": res_micro,
        "ceara": analise_escala(painel, "ceara", ce),
        "brasil": analise_escala(painel, "brasil", brasil),
        "loocv_microrregiao": loocv_municipio(painel, micro),
        "mdes_tost_micro": mdes_tost(res_micro.get("fe")),
        "h3_estagnacao": h3_estagnacao(painel, ideb_bruto),
    }
    # descritivos microrregião (último IDEB por município, anos iniciais)
    micro_d = painel[micro].dropna(subset=["ideb"]).copy()
    desc = {}
    for cod in MUNICIPIOS_MICRO:
        sub = micro_d[(micro_d["cod_mun"] == cod) & (micro_d["etapa"] == "anos_iniciais")]
        if sub.empty:
            continue
        ult = sub.loc[sub["ano_ideb"].idxmax()]
        desc[str(cod)] = {"nome": NOMES_MICRO[cod], "ano": int(ult["ano_ideb"]),
                          "ideb": round(float(ult["ideb"]), 2)}
    resultados["descritivos_micro_ai"] = {
        "municipios": len(MUNICIPIOS_MICRO),
        "ultimo_ideb_ai_por_municipio": desc,
    }
    resultados["metadados"] = {
        "defasagem_pib_anos": DEFASAGEM,
        "meta_ano": META_ANO,
        "seed": SEED,
        "gerado_em": datetime.now(timezone.utc).isoformat(),
    }
    prov = {
        "ciclo": "R426",
        "resumo_resultados": {
            "micro_niveis": resultados["microrregiao"].get("niveis"),
            "micro_1dif": resultados["microrregiao"].get("primeiras_diferencas"),
            "micro_fe": {k: v for k, v in resultados["microrregiao"].get("fe", {}).items()
                         if k != "anos"},
            "micro_fe_cluster": {
                "se_cluster": resultados["microrregiao"].get("fe", {}).get("se_cluster"),
                "ic95_cluster": [resultados["microrregiao"].get("fe", {}).get("ic95_cluster_inf"),
                                 resultados["microrregiao"].get("fe", {}).get("ic95_cluster_sup")],
                "p_valor_cluster": resultados["microrregiao"].get("fe", {}).get("p_valor_cluster"),
                "n_clusters": resultados["microrregiao"].get("fe", {}).get("n_clusters"),
            },
            "ce_niveis": resultados["ceara"].get("niveis"),
            "br_niveis": resultados["brasil"].get("niveis"),
            "loocv": {k: v for k, v in resultados["loocv_microrregiao"].items() if k != "folds"},
            "mdes_tost": resultados["mdes_tost_micro"],
        },
        "sha256_scripts": {
            "baixar_dados.py": hashlib.sha256((RAIZ / "scripts" / "baixar_dados.py").read_bytes()).hexdigest(),
            "analise_crateus.py": hashlib.sha256((RAIZ / "scripts" / "analise_crateus.py").read_bytes()).hexdigest(),
        },
    }
    salvar_json(resultados, "resultados_r426.json")
    salvar_json(prov, "provenance_r426.json")
    print("resultados salvos em", OUT)
    print(json.dumps(prov["resumo_resultados"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    principal()
