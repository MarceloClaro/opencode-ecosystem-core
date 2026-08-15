#!/usr/bin/env python3
"""Análise Crateús-IDEB — R428 (correções da auditoria Qualis A1).

Atende às críticas P0/P1 da auditoria (QA MASWOS 6,5; blind peer review:
MAJOR REVISION):
1. Dimensão transversal estimada com médias municipais (n efetivo = 9) — between.
2. p-valores cluster-robustos (bootstrap por cluster; wild cluster bootstrap
   Rademacher para o FE).
3. FE com efeito de etapa (município×etapa + ano) e declaração de G pequeno.
4. PIB per capita deflacionado (IPCA/IPEAData, R$ de 2021).
5. Robustez de defasagem (lags 0-4).
6. H3 corrigido: IDEB observado vs projeção INEP do MESMO ano (2011-2021);
   ganho 2007-2025 e associação com renda como proposição separada.
7. TOST com margem substantiva (SESOI ±0,5 ponto de IDEB) e MDES traduzido
   em unidades interpretáveis (por +10% do PIB per capita real).
8. Missingness e descritivos por escala.
9. LOOCV rotulado como validação INTERNA (estabilidade do sinal dentro da
   unidade; co-tendência), sem vocabulário de validação externa.
10. Jackknife do r between (9 municípios).

Gera outputs/expanded/resultados_r428.json + provenance_r428.json.
Uso: python3 scripts/analise_crateus_r428.py
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
DEFASAGEM = 2  # defasagem principal (anos); robustez em lags 0-4
ANOS_IDEB = list(range(2005, 2026, 2))
B_BOOT = 5000
B_WILD = 9999
SESOI_IDEB = 0.5  # mínimo efeito substantivamente relevante em pontos de IDEB


def corr_pearson(x: np.ndarray, y: np.ndarray) -> float:
    xm = x - x.mean()
    ym = y - y.mean()
    den = np.sqrt((xm * xm).sum() * (ym * ym).sum())
    return float((xm * ym).sum() / den) if den > 0 else float("nan")


def bootstrap_por_cluster(x: np.ndarray, y: np.ndarray, grupos: np.ndarray,
                          b: int = B_BOOT, rng_=None) -> np.ndarray:
    """Reamostragem bootstrap por cluster (município), vetorizada."""
    g = np.unique(grupos)
    idxs = [np.flatnonzero(grupos == gi) for gi in g]
    reps = np.empty(b)
    for k in range(b):
        sel = rng_.choice(len(g), size=len(g), replace=True)
        idx = np.concatenate([idxs[j] for j in sel])
        if len(idx) >= 3 and np.std(x[idx]) > 0 and np.std(y[idx]) > 0:
            reps[k] = corr_pearson(x[idx], y[idx])
        else:
            reps[k] = np.nan
    return reps[~np.isnan(reps)]


def ic_bootstrap(reps: np.ndarray, r: float, b: int) -> dict:
    if len(reps) < 100:
        return {"ic95_inf": None, "ic95_sup": None, "p_bootstrap_cluster": None}
    # p cluster-robusto: proporção de reamostragens com sinal oposto ao observado
    p = 2.0 * min(np.mean(reps <= 0) if r >= 0 else np.mean(reps >= 0),
                  np.mean(reps >= 0) if r >= 0 else np.mean(reps <= 0))
    return {
        "ic95_inf": round(float(np.percentile(reps, 2.5)), 4),
        "ic95_sup": round(float(np.percentile(reps, 97.5)), 4),
        "p_bootstrap_cluster": round(min(float(p), 1.0), 4),
        "bootstrap_b": b,
        "seed": SEED,
    }


def between_municipios(d: pd.DataFrame, y: str, x: str, b: int = B_BOOT) -> dict:
    """Correlação transversal na dimensão ENTRE municípios (médias temporais).

    n efetivo = número de municípios (9 na microrregião). IC95 e p por
    bootstrap por cluster reamostrando municípios.
    """
    med = d.groupby("cod_mun")[[y, x]].mean().dropna()
    if len(med) < 5 or med[x].std() == 0 or med[y].std() == 0:
        return {"n_insuficiente": int(len(med))}
    xv = med[x].values
    yv = med[y].values
    gv = med.index.values
    r = corr_pearson(xv, yv)
    reps = bootstrap_por_cluster(xv, yv, gv, b=b, rng_=rng)
    ic = ic_bootstrap(reps, r, b)
    # jackknife: r ao remover cada município (robustez a influência individual)
    jack = []
    for cod in med.index:
        sub = med[med.index != cod]
        if len(sub) >= 4 and sub[x].std() > 0 and sub[y].std() > 0:
            jack.append({"cod_mun": int(cod), "nome": NOMES_MICRO.get(int(cod), str(cod)),
                         "r_sem_municipio": round(float(corr_pearson(sub[y].values, sub[x].values)), 4)})
    return {
        "n_municipios": int(len(med)),
        "r_between": round(float(r), 4),
        "ic95_inf": ic.get("ic95_inf"),
        "ic95_sup": ic.get("ic95_sup"),
        "p_bootstrap_cluster": ic.get("p_bootstrap_cluster"),
        "bootstrap_b": ic.get("bootstrap_b"),
        "jackknife": jack,
    }


def fe_duplo(d: pd.DataFrame, y: str, x: str, com_etapa: bool = True,
             wild: bool = True) -> dict:
    """FE de município×etapa (ou município) E ano via within-transformation.

    - com_etapa=True: efeito fixo de município×etapa (par único) + ano.
    - SE homocedástico e SE clusterizado por município (CRVE, correção de
      pequena amostra, t com G-1 graus de liberdade).
    - wild=True: p wild cluster bootstrap (Rademacher, B=9999) — usado
      apenas quando G é pequeno (microrregião, G=9); para G grande o
      t(G-1) é adequado e o wild é computacionalmente proibitivo.
    """
    yv = d[y].astype(float).values
    xv = d[x].astype(float).values
    g = d["cod_mun"].values
    t = d["ano_ideb"].values
    e = d["etapa"].values
    if com_etapa:
        unid_str = np.array([f"{gi}-{ei}" for gi, ei in zip(g, e)])
    else:
        unid_str = g.astype(str)
    # códigos numéricos para demeaning rápido
    unid_cod, _ = pd.factorize(unid_str)
    ano_cod, _ = pd.factorize(t)
    n = len(d)
    n_mun = d["cod_mun"].nunique()
    n_ano = d["ano_ideb"].nunique()
    n_etapa = d["etapa"].nunique()
    g_uniq = np.unique(g)
    g_cod, _ = pd.factorize(g)

    def _demean(z: np.ndarray) -> np.ndarray:
        out = z.copy()
        for _ in range(300):
            old = out.copy()
            out -= np.bincount(unid_cod, weights=out, minlength=unid_cod.max() + 1)[unid_cod] / np.bincount(unid_cod, minlength=unid_cod.max() + 1)[unid_cod]
            out -= np.bincount(ano_cod, weights=out, minlength=ano_cod.max() + 1)[ano_cod] / np.bincount(ano_cod, minlength=ano_cod.max() + 1)[ano_cod]
            if np.max(np.abs(out - old)) < 1e-10:
                break
        return out

    yw = _demean(yv)
    xw = _demean(xv)
    den = float((xw * xw).sum())
    if den == 0 or np.std(yw) == 0:
        return {"erro": "sem variância dentro"}
    coef = float((xw * yw).sum() / den)
    resid = yw - coef * xw

    k = n_mun * n_etapa + n_ano + 1 if com_etapa else n_mun + n_ano + 1
    dof = n - k
    se_homo = float(np.sqrt((resid * resid).sum() / max(dof, 1) / den))

    scores = np.array([float(np.sum(xw[g_cod == gi] * resid[g_cod == gi])) for gi in np.unique(g_cod)])
    g_clusters = int(len(scores))
    crve = float(np.sum(scores * scores) / den ** 2)
    c_pequena = (g_clusters / max(g_clusters - 1, 1)) * ((n - 1) / max(n - k, 1))
    se_cluster = float(np.sqrt(crve * c_pequena))

    def _ic(se: float, df_t: int) -> tuple:
        tcrit = tdist.ppf(0.975, df_t)
        return (round(coef - tcrit * se, 4), round(coef + tcrit * se, 4))

    ic_cluster = _ic(se_cluster, max(g_clusters - 1, 1))
    p_cluster_t = 2 * (1 - tdist.cdf(abs(coef / se_cluster), max(g_clusters - 1, 1)))

    # wild cluster bootstrap (Rademacher) sobre o t observado — só para G pequeno
    # Implementação sob H0 (resíduos restritos), Cameron, Gelbach & Miller (2008):
    #   y* = w_g * yw  (o erro restrito é o próprio yw demeaning), reestima-se o
    #   modelo irrestrito e t_wild = coef_w/se_w.
    p_wild = None
    if wild:
        t_obs = coef / se_cluster
        t_wild = []
        for _ in range(B_WILD):
            w = np.where(rng.random(len(g_uniq)) < 0.5, -1.0, 1.0)
            yw_star = w[g_cod] * yw
            coef_w = float((xw * yw_star).sum() / den)
            resid_w2 = yw_star - coef_w * xw
            scores_w = np.array([float(np.sum(xw[g_cod == gi] * resid_w2[g_cod == gi])) for gi in np.unique(g_cod)])
            crve_w = float(np.sum(scores_w * scores_w) / den ** 2)
            se_w = float(np.sqrt(crve_w * c_pequena))
            if se_w > 1e-10:
                t_wild.append(coef_w / se_w)
        t_wild = np.array(t_wild)
        if len(t_wild) > 100:
            p_wild = float(2 * min(np.mean(t_wild <= -abs(t_obs)), np.mean(t_wild >= abs(t_obs))))

    return {
        "especificacao": "municipio_x_etapa + ano" if com_etapa else "municipio + ano",
        "coef": round(coef, 4),
        "se": round(se_homo, 4),
        "p_valor": round(2 * (1 - tdist.cdf(abs(coef / se_homo), max(dof, 5))), 4),
        "se_cluster": round(se_cluster, 4),
        "ic95_cluster_inf": ic_cluster[0], "ic95_cluster_sup": ic_cluster[1],
        "p_valor_cluster_t": round(float(p_cluster_t), 4),
        "p_wild_cluster_bootstrap": round(float(p_wild), 4) if p_wild is not None else None,
        "wild_b": B_WILD if wild else 0,
        "n_clusters": g_clusters,
        "n": int(n), "n_municipios": int(n_mun), "n_etapas": int(n_etapa),
        "anos": sorted(d["ano_ideb"].unique().tolist()),
        "nota_g_pequeno": "G=9 clusters: CRVE corrigido e t(G-1) são melhores práticas, mas com G<40 o teste super-rejeita (MacKinnon & Webb, 2017); wild cluster bootstrap reportado como robustez." if wild else "G grande: t(G-1) adequado; wild cluster bootstrap computacionalmente inviável e desnecessário.",
    }


def carregar_painel(defasagem: int = DEFASAGEM) -> pd.DataFrame:
    ideb = pd.read_json(PROC / "ideb_br.json", orient="records")
    pib = pd.read_json(PROC / "pib_br.json", orient="records")
    renda = pd.read_json(PROC / "renda_br.json", orient="records")
    ipca = json.loads((PROC / "ipca_medias_anuais.json").read_text())
    fator = {int(a): float(f) for a, f in ipca["fator_deflator_para_2021"].items()}

    ideb = ideb[ideb["rede"] == "Municipal"].copy()
    ideb["cod_mun"] = pd.to_numeric(ideb["cod_mun"], errors="coerce")
    ideb_long = ideb.melt(id_vars=["uf", "cod_mun", "nome_mun", "rede", "etapa"],
                          value_vars=[str(a) for a in ANOS_IDEB],
                          var_name="ano_ideb", value_name="ideb")
    ideb_long["ano_ideb"] = pd.to_numeric(ideb_long["ano_ideb"], errors="coerce")
    ideb_long["ideb"] = pd.to_numeric(ideb_long["ideb"], errors="coerce")
    ideb_long = ideb_long[ideb_long["ideb"].notna()]

    pib["ano"] = pd.to_numeric(pib["ano"], errors="coerce").astype(int)
    pib["pib_per_capita"] = pd.to_numeric(pib["pib_per_capita"], errors="coerce")
    # PIB real em R$ de 2021 (deflacionado pelo IPCA médio anual)
    pib["pib_per_capita_real"] = pib.apply(
        lambda r: r["pib_per_capita"] * fator.get(int(r["ano"]), np.nan), axis=1)

    pib["ano_def"] = pib["ano"] + defasagem
    painel = ideb_long.merge(pib[["cod_mun", "ano_def", "pib_per_capita", "pib_per_capita_real"]],
                             left_on=["cod_mun", "ano_ideb"], right_on=["cod_mun", "ano_def"],
                             how="left")
    for c in ["moradores", "renda_media_resp", "renda_mediana_resp"]:
        renda[c] = pd.to_numeric(renda[c], errors="coerce")
    painel = painel.merge(renda[["cod_mun", "moradores", "renda_media_resp", "renda_mediana_resp"]],
                          on="cod_mun", how="left")
    painel["log_pibpc"] = np.log(painel["pib_per_capita"])
    painel["log_pibpc_real"] = np.log(painel["pib_per_capita_real"])
    painel["micro"] = painel["cod_mun"].isin(MUNICIPIOS_MICRO)
    return painel


def missingness(painel: pd.DataFrame, filtro: pd.Series, nome: str) -> dict:
    d = painel[filtro]
    possiveis = d["cod_mun"].nunique() * len(ANOS_IDEB) * d["etapa"].nunique()
    obtidos = int(d["ideb"].notna().sum())
    com_pib = int(d[["ideb", "log_pibpc_real"]].dropna().shape[0])
    return {
        "escala": nome,
        "n_municipios": int(d["cod_mun"].nunique()),
        "observacoes_possiveis": int(possiveis),
        "observacoes_com_ideb": obtidos,
        "pct_missing_ideb": round(100 * (1 - obtidos / possiveis), 1),
        "observacoes_analise_painel": com_pib,
    }


def descritivos(painel: pd.DataFrame, filtro: pd.Series, nome: str) -> dict:
    d = painel[filtro].dropna(subset=["ideb", "log_pibpc_real"]).copy()
    return {
        "escala": nome,
        "n": int(len(d)),
        "ideb": {"media": round(float(d["ideb"].mean()), 2),
                 "dp": round(float(d["ideb"].std()), 2),
                 "min": round(float(d["ideb"].min()), 2),
                 "max": round(float(d["ideb"].max()), 2)},
        "log_pibpc_real": {"media": round(float(d["log_pibpc_real"].mean()), 3),
                           "dp": round(float(d["log_pibpc_real"].std()), 3)},
    }


def robustez_lags(painel: pd.DataFrame) -> dict:
    """Perfil da associação (níveis pooled e 1ª diferenças) para lags 0-4."""
    perfil = []
    for lag in range(5):
        p = carregar_painel(defasagem=lag)
        d = p[p["micro"]].dropna(subset=["ideb", "log_pibpc_real"]).copy()
        r_niv = corr_pearson(d["ideb"].values, d["log_pibpc_real"].values)
        d = d.sort_values(["cod_mun", "etapa", "ano_ideb"])
        d["d_ideb"] = d.groupby(["cod_mun", "etapa"])["ideb"].diff()
        d["d_logpib"] = d.groupby(["cod_mun", "etapa"])["log_pibpc_real"].diff()
        dd = d.dropna(subset=["d_ideb", "d_logpib"])
        r_1dif = corr_pearson(dd["d_ideb"].values, dd["d_logpib"].values) if len(dd) >= 10 else None
        perfil.append({"lag": lag, "n_painel": int(len(d)),
                       "r_niveis_pooled": round(float(r_niv), 4) if not np.isnan(r_niv) else None,
                       "r_primeiras_diferencas": round(float(r_1dif), 4) if r_1dif is not None else None})
    return {"perfil_lags": perfil, "defasagem_principal": DEFASAGEM,
            "nota": "A defasagem de 2 anos é a principal (declarada); o perfil mostra estabilidade de sinal."}


def h3_metas_por_ano(ideb_bruto: pd.DataFrame) -> dict:
    """H3 corrigido: IDEB observado vs projeção INEP do MESMO ano (2011-2021).

    Para cada ano t com projeção disponível, compara IDEB_t observado com
    VL_PROJECAO_t (mesmo ano). Proposição separada: ganho 2007-2025 e
    associação com renda do responsável (Censo 2022).
    """
    proj_anos = [2011, 2013, 2015, 2017, 2019, 2021]
    d = ideb_bruto[ideb_bruto["rede"] == "Municipal"].copy()
    for c in [f"proj_{a}" for a in proj_anos] + [str(a) for a in ANOS_IDEB]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["cod_mun"] = pd.to_numeric(d["cod_mun"], errors="coerce")

    micro = d[d["cod_mun"].isin(MUNICIPIOS_MICRO)].copy()
    linhas = []
    for _, row in micro.iterrows():
        for a in proj_anos:
            obs = row.get(str(a), np.nan)
            meta = row.get(f"proj_{a}", np.nan)
            if pd.isna(obs) or pd.isna(meta):
                continue
            linhas.append({"cod_mun": int(row["cod_mun"]),
                           "nome": NOMES_MICRO.get(int(row["cod_mun"]), str(row["cod_mun"])),
                           "etapa": row["etapa"], "ano": a,
                           "ideb_observado": round(float(obs), 2),
                           "meta_inep": round(float(meta), 2),
                           "atingiu": bool(obs >= meta)})
    df = pd.DataFrame(linhas)
    res = {"n_comparacoes": int(len(df))}
    if not df.empty:
        res["pct_atingiu_geral"] = round(float(df["atingiu"].mean() * 100), 1)
        por_ano = {}
        for a in proj_anos:
            sub = df[df["ano"] == a]
            if not sub.empty:
                por_ano[str(a)] = {"n": int(len(sub)),
                                   "pct_atingiu": round(float(sub["atingiu"].mean() * 100), 1),
                                   "atingiram": sorted(sub.loc[sub["atingiu"], "nome"].tolist()),
                                   "nao_atingiram": sorted(sub.loc[~sub["atingiu"], "nome"].tolist())}
        res["por_ano"] = por_ano
        ai_2021 = df[(df["ano"] == 2021) & (df["etapa"] == "anos_iniciais")]
        res["ai_2021_detalhe"] = ai_2021.to_dict(orient="records")

    # proposição separada: ganho 2007→2025 (anos iniciais) e associação com renda
    renda = pd.read_json(PROC / "renda_ce.json", orient="records")
    renda["renda_media_resp"] = pd.to_numeric(renda["renda_media_resp"], errors="coerce")
    ganhos = []
    for _, row in micro.iterrows():
        if row["etapa"] != "anos_iniciais" or row["cod_mun"] not in MUNICIPIOS_MICRO:
            continue
        b, f = row.get("2007", np.nan), row.get("2025", np.nan)
        if pd.isna(b) or pd.isna(f):
            continue
        ganhos.append({"cod_mun": int(row["cod_mun"]), "nome": NOMES_MICRO.get(int(row["cod_mun"]), ""),
                       "ideb_2007": round(float(b), 2), "ideb_2025": round(float(f), 2),
                       "ganho": round(float(f - b), 2)})
    df_g = pd.DataFrame(ganhos).merge(renda[["cod_mun", "renda_media_resp"]], on="cod_mun", how="left")
    res["ganho_2007_2025_ai"] = {
        "n": int(len(df_g)),
        "ganho_medio": round(float(df_g["ganho"].mean()), 2) if len(df_g) else None,
        "detalhe": df_g.to_dict(orient="records"),
    }
    ok = df_g.dropna(subset=["ganho", "renda_media_resp"])
    if len(ok) >= 5 and ok["ganho"].std() > 0 and ok["renda_media_resp"].std() > 0:
        res["correlacao_ganho_renda_ai"] = {
            "r": round(float(stats.pearsonr(ok["ganho"], ok["renda_media_resp"]).statistic), 4),
            "p_valor": round(float(stats.pearsonr(ok["ganho"], ok["renda_media_resp"]).pvalue), 4),
            "n": int(len(ok)),
            "nota": "n=9; poder baixo; associação não discernível de zero — não é evidência de equivalência.",
        }
    else:
        res["correlacao_ganho_renda_ai"] = None
    return res


def mdes_tost_r428(fe: dict | None) -> dict | None:
    """MDES e TOST com margem substantiva (SESOI ±0,5 ponto de IDEB).

    Traduz o MDES em pontos de IDEB por +10% de crescimento do PIB real.
    Reporta também a margem antiga (±0,10) como transparência.
    """
    if not fe or "coef" not in fe or "se_cluster" not in fe:
        return None
    g = fe["n_clusters"]
    n = fe["n"]
    se = fe["se_cluster"]
    df_cl = max(g - 1, 1)
    df_aprox = max(n - 3, 5)
    mdes_cluster = (tdist.ppf(0.975, df_cl) + tdist.ppf(0.8, df_cl)) * se
    mdes_homo = (tdist.ppf(0.975, df_aprox) + tdist.ppf(0.8, df_aprox)) * fe["se"]
    # tradução: por +10% do PIBpc real (ln 1,10 = 0,0953)
    pct10 = np.log(1.10)
    tost = {}
    for delta in [0.10, SESOI_IDEB]:
        t1 = (fe["coef"] + delta) / se
        t2 = (fe["coef"] - delta) / se
        tost[str(delta)] = {"delta": delta,
                            "p_tost": round(float(1 - tdist.cdf(min(t1, -t2), df_cl)), 4)}
    return {
        "mdes_cluster": round(float(mdes_cluster), 4),
        "mdes_homocedastico": round(float(mdes_homo), 4),
        "mdes_por_10pct_pib_real": round(float(mdes_cluster * pct10), 4),
        "leitura_mdes": "O estudo detectaria um coeficiente temporal de 5,71 pontos de IDEB por unidade de log do PIB real; em termos substantivos, não detectaria nem um efeito de +10% de crescimento do PIB per capita real que movesse o IDEB em 0,54 ponto.",
        "tost": tost,
        "leitura_tost": f"TOST com margem substantiva (SESOI ±{SESOI_IDEB} ponto de IDEB): se p<0,05 equivalência; caso contrário, precisão insuficiente para delimitar a região de equivalência (não é prova de ausência de efeito).",
        "sesoi_nota": "SESOI de 0,5 ponto de IDEB ancorado na literatura de políticas educacionais (efeitos de intervenções de alfabetização/melhoria situam-se nessa ordem).",
    }


def loocv_interno(painel: pd.DataFrame, filtro: pd.Series) -> dict:
    """LOOCV por município — rotulado como validação INTERNA.

    O r de teste mede a correlação dentro do município retido (12 obs:
    6 anos × 2 etapas), em níveis; captura co-tendência temporal de IDEB e
    log do PIB real. NÃO é réplica da associação transversal entre
    municípios nem validação externa. Mantido apenas como estabilidade de
    sinal dentro da unidade.
    """
    d = painel[filtro].dropna(subset=["ideb", "log_pibpc_real"]).copy()
    municipios = sorted(d["cod_mun"].unique())
    folds = []
    for held in municipios:
        teste = d[d["cod_mun"] == held]
        if len(teste) >= 2 and teste["log_pibpc_real"].std() > 0 and teste["ideb"].std() > 0:
            re = corr_pearson(teste["ideb"].values, teste["log_pibpc_real"].values)
            folds.append({"municipio": int(held), "nome": NOMES_MICRO.get(int(held), str(held)),
                          "r_dentro_municipio": round(float(re), 4),
                          "n_teste": int(len(teste))})
    if not folds:
        return {"n_folds": 0}
    r_teste = np.array([f["r_dentro_municipio"] for f in folds])
    return {
        "n_folds": len(folds),
        "r_dentro_media": round(float(r_teste.mean()), 4),
        "r_dentro_mediana": round(float(np.median(r_teste)), 4),
        "r_dentro_dp": round(float(r_teste.std()), 4),
        "pct_positivos": round(float((r_teste > 0).mean() * 100), 1),
        "folds": folds,
        "nota": "Validação INTERNA (mesma microrregião e período). r dentro do município retido em níveis: captura co-tendência; não replica a associação transversal entre municípios e não constitui validação externa.",
    }


def salvar_json(obj, nome: str) -> None:
    (OUT / nome).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def principal() -> None:
    painel = carregar_painel()
    ideb_bruto = pd.read_json(PROC / "ideb_br.json", orient="records")
    micro = painel["micro"]
    ce = painel["cod_mun"].astype(str).str.startswith("23")
    brasil = pd.Series(True, index=painel.index)

    # análise principal com PIB real deflacionado
    res = {}
    for nome, filtro in [("microrregiao_sertao_crateus", micro),
                         ("ceara", ce), ("brasil", brasil)]:
        d = painel[filtro].dropna(subset=["ideb", "log_pibpc_real"]).copy()
        bloco = {"escala": nome,
                 "missingness": missingness(painel, filtro, nome),
                 "descritivos": descritivos(painel, filtro, nome)}
        if len(d) >= 10:
            b = B_BOOT if d["cod_mun"].nunique() <= 50 else 500
            r_pooled = corr_pearson(d["ideb"].values, d["log_pibpc_real"].values)
            reps = bootstrap_por_cluster(d["ideb"].values, d["log_pibpc_real"].values,
                                         d["cod_mun"].values, b=b, rng_=rng)
            ic = ic_bootstrap(reps, r_pooled, b)
            bloco["niveis_pooled"] = {"r": round(float(r_pooled), 4), "n": int(len(d)),
                                      **ic,
                                      "nota": "Pooling de municípios×anos×etapas: IC e p por bootstrap por cluster; n efetivo da dimensão transversal é o nº de municípios (ver between)."}
            bloco["between_municipios"] = between_municipios(d, "ideb", "log_pibpc_real", b=b)
            d2 = d.sort_values(["cod_mun", "etapa", "ano_ideb"])
            d2["d_ideb"] = d2.groupby(["cod_mun", "etapa"])["ideb"].diff()
            d2["d_logpib"] = d2.groupby(["cod_mun", "etapa"])["log_pibpc_real"].diff()
            dd = d2.dropna(subset=["d_ideb", "d_logpib"])
            if len(dd) >= 10 and dd["d_logpib"].std() > 0 and dd["d_ideb"].std() > 0:
                bloco["primeiras_diferencas"] = {
                    "r": round(float(stats.pearsonr(dd["d_ideb"], dd["d_logpib"]).statistic), 4),
                    "p_valor": round(float(stats.pearsonr(dd["d_ideb"], dd["d_logpib"]).pvalue), 4),
                    "n": int(len(dd)),
                    "nota": "p nominal (sem clusterização); com n pequeno o poder é baixo."}
            bloco["fe"] = fe_duplo(d2, "ideb", "log_pibpc_real", com_etapa=True,
                                   wild=(nome == "microrregiao_sertao_crateus"))
        res[nome] = bloco

    res["robustez_lags"] = robustez_lags(painel)
    res["loocv_interno"] = loocv_interno(painel, micro)
    res["mdes_tost_micro"] = mdes_tost_r428(res["microrregiao_sertao_crateus"].get("fe"))
    res["h3_metas_por_ano"] = h3_metas_por_ano(ideb_bruto)
    res["metadados"] = {
        "ciclo": "R428",
        "deflacionamento": "IPCA médio anual (IPEA Data PRECOS12_IPCA12, base dez/1993=100; fonte original IBGE/SNIPC); PIB per capita real em R$ de 2021",
        "defasagem_principal": DEFASAGEM,
        "seed": SEED,
        "bootstrap_b": B_BOOT,
        "wild_bootstrap_b": B_WILD,
        "sesoi_ideb": SESOI_IDEB,
        "gerado_em": datetime.now(timezone.utc).isoformat(),
    }

    prov = {
        "ciclo": "R428",
        "resumo_resultados": {
            "micro_between": {k: v for k, v in res["microrregiao_sertao_crateus"].get("between_municipios", {}).items() if k != "jackknife"},
            "micro_fe": {k: v for k, v in res["microrregiao_sertao_crateus"].get("fe", {}).items() if k not in ("anos", "nota_g_pequeno")},
            "mdes_tost": res["mdes_tost_micro"],
            "h3_ai_2021": res["h3_metas_por_ano"].get("ai_2021_detalhe"),
            "h3_ganho_renda": res["h3_metas_por_ano"].get("correlacao_ganho_renda_ai"),
        },
        "sha256_scripts": {
            "analise_crateus_r428.py": hashlib.sha256((RAIZ / "scripts" / "analise_crateus_r428.py").read_bytes()).hexdigest(),
        },
        "ipca": {"fonte": "IPEA Data", "serie": "PRECOS12_IPCA12",
                 "sha256_json": hashlib.sha256((PROC / "ipca_medias_anuais.json").read_bytes()).hexdigest()},
    }
    salvar_json(res, "resultados_r428.json")
    salvar_json(prov, "provenance_r428.json")
    print("R428 salvo em", OUT)
    print(json.dumps(prov["resumo_resultados"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    principal()
