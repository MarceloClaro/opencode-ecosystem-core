#!/usr/bin/env python3
"""Análise expandida (R412) — painel ≥ 20 países com controles e erros robustos.

Pipeline:
1. Carrega JSONs brutos (data/raw_expandido/) e a lista oficial de países.
2. Filtra agregados; critério de amostra: ≥ 20 obs não nulas de matrícula
   terciária E de PIB per capita.
3. Monta painel país-ano (sem imputação) → data/processed/panel_wdi_expandido_1960_2023.csv
4. Análises em outputs/expanded/:
   - correlações (níveis e primeiras diferenças)
   - LOOCV por país (≥ 20 folds)
   - subperíodos (1960-1990, 1991-2023)
   - painel com efeitos fixos de país/ano, defasagem de 5 anos,
     controles WGI e estruturais, erros padrão clusterizados por país
   - ML Random Forest (partição por linha vs agrupada por país)
   - proveniência numérica completa (provenance_expanded.json)
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

AUDIT = Path(__file__).resolve().parent.parent
RAW = AUDIT / "data" / "raw_expandido"
PROC = AUDIT / "data" / "processed"
OUT = AUDIT / "outputs" / "expanded"

INDICADORES = {
    "NY.GDP.PCAP.KD": "NY_GDP_PCAP_KD",
    "NY.GDP.PCAP.KD.ZG": "NY_GDP_PCAP_KD_ZG",
    "SE.TER.ENRR": "SE_TER_ENRR",
    "SE.XPD.TOTL.GD.ZS": "SE_XPD_TOTL_GD_ZS",
    "GB.XPD.RSDV.GD.ZS": "GB_XPD_RSDV_GD_ZS",
    "SI.POV.GINI": "SI_POV_GINI",
    "SP.DYN.LE00.IN": "SP_DYN_LE00_IN",
    "SP.URB.TOTL.IN.ZS": "SP_URB_TOTL_IN_ZS",
    "NV.IND.MANF.ZS": "NV_IND_MANF_ZS",
    "BX.KLT.DINV.WD.GD.ZS": "BX_KLT_DINV_WD_GD_ZS",
    "TX.VAL.TECH.MF.ZS": "TX_VAL_TECH_MF_ZS",
    "CC.EST": "WGI_CC",
    "GE.EST": "WGI_GE",
    "PV.EST": "WGI_PV",
    "RQ.EST": "WGI_RQ",
    "RL.EST": "WGI_RL",
    "VA.EST": "WGI_VA",
}

MIN_OBS_PAIS = 20          # obs. não nulas mínimas por país (matrícula e PIB)
LAG_ANOS = 5               # defasagem da especificação de painel
ANO_CORTE = 1990           # subperíodos

RENAME_LABEL = {
    "NY_GDP_PCAP_KD": "PIB per capita (US$ const.)",
    "SE_TER_ENRR": "Matrícula terciária (% bruto)",
    "SE_XPD_TOTL_GD_ZS": "Gasto público educacional (% PIB)",
    "GB_XPD_RSDV_GD_ZS": "P&D (% PIB)",
    "SP_URB_TOTL_IN_ZS": "Urbanização (% pop.)",
    "WGI_CC": "WGI — Controle da corrupção",
    "WGI_GE": "WGI — Efetividade governamental",
    "WGI_RL": "WGI — Estado de direito",
}


def load_countries() -> set[str]:
    """ISO3 dos países oficiais (exclui agregados e territórios sem ISO3)."""
    data = json.loads((RAW / "wdi_countries_meta.json").read_text(encoding="utf-8"))[1]
    iso3 = set()
    for c in data:
        if c.get("region", {}).get("id") == "NA":
            continue
        code = c.get("id", "")
        if code and len(code) == 3:
            iso3.add(code)
    return iso3


def load_series(indicator: str) -> pd.DataFrame:
    raw = json.loads((RAW / f"wdi_{indicator}.json").read_text(encoding="utf-8"))
    rows = []
    for r in raw[1]:
        iso = r.get("countryiso3code") or ""
        if len(iso) != 3:
            continue
        try:
            ano = int(r["date"])
        except (TypeError, ValueError):
            continue
        val = r.get("value")
        rows.append((iso, ano, val))
    df = pd.DataFrame(rows, columns=["iso3", "year", INDICADORES[indicator]])
    return df


def build_panel() -> pd.DataFrame:
    paises_oficiais = load_countries()
    frames = [load_series(ind) for ind in INDICADORES]
    df = frames[0]
    for f in frames[1:]:
        df = df.merge(f, on=["iso3", "year"], how="outer")

    df = df[df["iso3"].isin(paises_oficiais)]

    # critério de amostra: ≥ MIN_OBS_PAIS obs não nulas de matrícula e de PIB
    conta = df.groupby("iso3")[["SE_TER_ENRR", "NY_GDP_PCAP_KD"]].count()
    elegiveis = conta[
        (conta["SE_TER_ENRR"] >= MIN_OBS_PAIS)
        & (conta["NY_GDP_PCAP_KD"] >= MIN_OBS_PAIS)
    ].index
    df = df[df["iso3"].isin(elegiveis)].sort_values(["iso3", "year"]).reset_index(drop=True)

    df["ln_gdp_pc"] = np.log(df["NY_GDP_PCAP_KD"].where(df["NY_GDP_PCAP_KD"] > 0))
    df["ln_gdp_pc_lag5"] = df.groupby("iso3")["ln_gdp_pc"].shift(LAG_ANOS)
    df["ln_tertiaria"] = np.log(df["SE_TER_ENRR"].where(df["SE_TER_ENRR"] > 0))
    df["ln_tertiaria_lag5"] = df.groupby("iso3")["ln_tertiaria"].shift(LAG_ANOS)
    df["gdp_pc_growth"] = df["NY_GDP_PCAP_KD_ZG"] / 100.0

    return df


def rho_niveis(df: pd.DataFrame) -> float:
    d = df[["ln_tertiaria", "ln_gdp_pc"]].dropna()
    if len(d) < 5:
        return np.nan
    return stats.spearmanr(d["ln_tertiaria"], d["ln_gdp_pc"]).statistic


def rho_diferencas(df: pd.DataFrame) -> float:
    d = df[["ln_tertiaria", "ln_gdp_pc"]].dropna()
    if len(d) < 10:
        return np.nan
    dd = d.diff().dropna()
    return stats.spearmanr(dd["ln_tertiaria"], dd["ln_gdp_pc"]).statistic


def loocv_por_pais(df: pd.DataFrame) -> list[dict]:
    folds = []
    for iso in sorted(df["iso3"].unique()):
        treino = df[df["iso3"] != iso]
        teste = df[df["iso3"] == iso]
        folds.append(
            {
                "pais_excluido": iso,
                "n_obs_excluidas": int(teste["ln_tertiaria"].notna().sum()),
                "rho_niveis_treino": rho_niveis(treino),
                "rho_niveis_teste": rho_niveis(teste),
                "diferenca": rho_niveis(treino) - rho_niveis(teste),
            }
        )
    return folds


def subperiodos(df: pd.DataFrame) -> dict:
    out = {}
    for nome, masc in [("1960_1990", df["year"] <= ANO_CORTE),
                       ("1991_2023", df["year"] > ANO_CORTE)]:
        sub = df[masc]
        out[nome] = {
            "n_paises": int(sub["iso3"].nunique()),
            "n_pais_ano": int(len(sub)),
            "rho_niveis": rho_niveis(sub),
            "rho_diferencas": rho_diferencas(sub),
        }
    return out


def painel_fe_cluster(df: pd.DataFrame) -> dict:
    """Efeitos fixos de país e ano; erros clusterizados por país (statsmodels)."""
    from statsmodels.formula.api import ols

    d = df.copy()
    # controles disponíveis (sem imputação)
    d["WGI_media"] = d[["WGI_CC", "WGI_GE", "WGI_PV", "WGI_RQ", "WGI_RL", "WGI_VA"]].mean(axis=1)
    d["C_educ"] = d["SE_XPD_TOTL_GD_ZS"]
    d["C_pd"] = d["GB_XPD_RSDV_GD_ZS"]
    d["C_urb"] = d["SP_URB_TOTL_IN_ZS"]
    d["C_manuf"] = d["NV_IND_MANF_ZS"]

    amostra = d.dropna(
        subset=["ln_tertiaria", "ln_gdp_pc_lag5", "C_educ", "C_pd", "C_urb",
                "C_manuf", "WGI_media"]
    ).copy()
    amostra["iso3_cat"] = amostra["iso3"].astype("category")
    amostra["year_cat"] = amostra["year"].astype("category")

    formula = (
        "ln_tertiaria ~ ln_gdp_pc_lag5 + C_educ + C_pd + C_urb + C_manuf + "
        "WGI_media + C(iso3_cat) + C(year_cat)"
    )
    model = ols(formula, data=amostra).fit(
        cov_type="cluster", cov_kwds={"groups": amostra["iso3"]}
    )
    coef = model.params["ln_gdp_pc_lag5"]
    ic_inf, ic_sup = model.conf_int().loc["ln_gdp_pc_lag5"]
    return {
        "especificacao": "ln_tertiaria ~ ln_gdp_pc_lag5 + controles + FE pais + FE ano",
        "lag_anos": LAG_ANOS,
        "efeito_fixo_cluster_coef": float(coef),
        "efeito_fixo_cluster_ic_inf": float(ic_inf),
        "efeito_fixo_cluster_ic_sup": float(ic_sup),
        "coef_log_pib_lag5": float(coef),
        "ic_95_inf": float(ic_inf),
        "ic_95_sup": float(ic_sup),
        "p_value": float(model.pvalues["ln_gdp_pc_lag5"]),
        "cluster_tipo": "por_pais",
        "n_clusters": int(amostra["iso3"].nunique()),
        "n_obs": int(len(amostra)),
        "usou_controle_wgi": True,
        "controles": ["gasto_educ", "pd", "urbanizacao", "manufatura", "WGI_media"],
    }


def ml_agrupado(df: pd.DataFrame) -> dict:
    """RF: prever crescimento acima da mediana; partição por linha vs agrupada."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import GroupKFold

    d = df.copy()
    d["WGI_media"] = d[["WGI_CC", "WGI_GE", "WGI_PV", "WGI_RQ", "WGI_RL", "WGI_VA"]].mean(axis=1)
    d["y"] = (d["gdp_pc_growth"] > d["gdp_pc_growth"].median()).astype(int)
    features = ["ln_tertiaria_lag5", "ln_gdp_pc_lag5", "SE_XPD_TOTL_GD_ZS",
                "GB_XPD_RSDV_GD_ZS", "SP_URB_TOTL_IN_ZS", "NV_IND_MANF_ZS", "WGI_media"]
    amostra = d.dropna(subset=["y"] + features).copy()
    X = amostra[features].values
    y = amostra["y"].values
    grupos = amostra["iso3"].values
    rng = np.random.RandomState(42)

    # AUC por linha (split aleatório — tendencioso, para contraste)
    mask = rng.rand(len(amostra)) < 0.7
    clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    clf.fit(X[mask], y[mask])
    auc_linha = roc_auc_score(y[~mask], clf.predict_proba(X[~mask])[:, 1])

    # AUC agrupado (GroupKFold — sem vazamento por país)
    aucs = []
    gkf = GroupKFold(n_splits=5)
    for tr, te in gkf.split(X, y, grupos):
        clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
        clf.fit(X[tr], y[tr])
        if len(np.unique(y[te])) < 2:
            continue
        aucs.append(roc_auc_score(y[te], clf.predict_proba(X[te])[:, 1]))
    auc_agrupado = float(np.mean(aucs)) if aucs else np.nan

    return {
        "ml_auc_linha": float(auc_linha),
        "ml_auc_agrupado": auc_agrupado,
        "target": "crescimento_pib_pc_acima_da_mediana",
        "features": features,
        "nota": ("resultado negativo esperado: AUC agrupado ~0,5 indica que "
                 "matrícula/PIB defasados não predizem crescimento fora da amostra "
                 "de países; nenhuma relação causal é inferida."),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    df = build_panel()
    PROC.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROC / "panel_wdi_expandido_1960_2023.csv", index=False)

    n_paises = int(df["iso3"].nunique())
    n_pais_ano = int(len(df))
    print(f"Painel expandido: {n_paises} países, {n_pais_ano} obs país-ano")

    # --- correlações ---
    res = {
        "amostra_criterio": f">= {MIN_OBS_PAIS} obs nao nulas de matricula e PIB",
        "n_paises": n_paises,
        "n_pais_ano": n_pais_ano,
        "rho_niveis_terciaria": rho_niveis(df),
        "rho_diferencas_terciaria": rho_diferencas(df),
        "n_obs_rho_niveis": int(df[["ln_tertiaria", "ln_gdp_pc"]].dropna().shape[0]),
        "n_obs_rho_diferencas": int(df[["ln_tertiaria", "ln_gdp_pc"]].dropna().diff().dropna().shape[0]),
        "cobertura_por_variavel": {
            col: int(df[col].notna().sum()) for col in INDICADORES.values()
        },
        "paises": sorted(df["iso3"].unique().tolist()),
    }

    # --- LOOCV ---
    folds = loocv_por_pais(df)
    rho_treino = [f["rho_niveis_treino"] for f in folds if not math.isnan(f["rho_niveis_treino"])]
    res["loocv"] = {
        "n_folds": len(folds),
        "rho_niveis_treino_media": float(np.mean(rho_treino)) if rho_treino else np.nan,
        "rho_niveis_treino_dp": float(np.std(rho_treino)) if rho_treino else np.nan,
        "rho_niveis_teste_media": float(np.mean(
            [f["rho_niveis_teste"] for f in folds if not math.isnan(f["rho_niveis_teste"])]
        )) if any(not math.isnan(f["rho_niveis_teste"]) for f in folds) else np.nan,
    }
    (OUT / "loocv_folds_expanded.json").write_text(
        json.dumps({"n_folds": len(folds), "folds": folds}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # --- subperíodos ---
    res["subperiodos"] = subperiodos(df)

    # --- painel FE com cluster ---
    res.update(painel_fe_cluster(df))

    # --- ML agrupado ---
    res.update(ml_agrupado(df))

    # --- persistência ---
    (OUT / "provenance_expanded.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2, allow_nan=True), encoding="utf-8"
    )

    tabela = pd.DataFrame(
        {
            "variavel": list(RENAME_LABEL),
            "descricao": list(RENAME_LABEL.values()),
            "n_obs": [int(df[c].notna().sum()) for c in RENAME_LABEL],
            "media": [round(float(df[c].mean()), 3) if df[c].notna().any() else None
                      for c in RENAME_LABEL],
            "desvio_padrao": [round(float(df[c].std()), 3) if df[c].notna().any() else None
                              for c in RENAME_LABEL],
        }
    )
    tabela.to_csv(OUT / "tabela1_descr_expandido.csv", index=False)

    pd.DataFrame(
        [{"bloco": "niveis", "rho": res["rho_niveis_terciaria"]},
         {"bloco": "primeiras_diferencas", "rho": res["rho_diferencas_terciaria"]}]
    ).to_csv(OUT / "tabela2_correlacoes_expandido.csv", index=False)

    pd.DataFrame(folds).to_csv(OUT / "tabela3_loocv_expandido.csv", index=False)

    pd.DataFrame(
        [{"bloco": k, **v} for k, v in res["subperiodos"].items()]
    ).to_csv(OUT / "tabela4_subperiodos_expandido.csv", index=False)

    pd.DataFrame(
        [{"metrica": "coef_log_pib_lag5", "valor": res["coef_log_pib_lag5"], "ic_inf": res["ic_95_inf"], "ic_sup": res["ic_95_sup"]},
         {"metrica": "p_value", "valor": res["p_value"], "ic_inf": None, "ic_sup": None},
         {"metrica": "n_clusters", "valor": res["n_clusters"], "ic_inf": None, "ic_sup": None},
         {"metrica": "n_obs", "valor": res["n_obs"], "ic_inf": None, "ic_sup": None}]
    ).to_csv(OUT / "tabela5_painel_fe_expandido.csv", index=False)

    pd.DataFrame(
        [{"metrica": "ml_auc_linha", "valor": res["ml_auc_linha"]},
         {"metrica": "ml_auc_agrupado", "valor": res["ml_auc_agrupado"]}]
    ).to_csv(OUT / "tabela6_ml_expandido.csv", index=False)

    print("Análise expandida concluída em outputs/expanded/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
