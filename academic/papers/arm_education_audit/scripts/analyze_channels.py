#!/usr/bin/env python3
"""Canais associativos da educação terciária (R413) — SPEC-935-R413.

Reusa o painel expandido (R412: data/processed/panel_wdi_expandido_1960_2023.csv)
e produz em outputs/channels/:

1. Matriz de correlações parciais (controles: ln PIB; WGI quando o par
   envolve PIB) com IC bootstrap por país (500 replicações, seed 42).
2. Análise em etapas do par matrícula×PIB: sem controle → +WGI →
   +estrutura → +saúde (mediação descritiva; rho parcial cai ao adicionar
   saúde) com IC bootstrap por país.
3. Canais associativos com painel de efeitos fixos e erros clusterizados
   por país (statsmodels):
   - saúde: matrícula defasada → expectativa de vida
   - desigualdade: matrícula defasada → Gini
   - inovação: P&D defasado → exportações de alta tecnologia
4. Moderação institucional (exploratória): interações matrícula×WGI e
   matrícula×P&D no painel FE clusterizado.
5. LOOCV por país das parciais centrais (≥ 20 folds).
6. proveniência fechada (provenance_r413.json + sha256 do painel).

Linguagem estritamente associativa; nenhuma inferência causal.
"""

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

AUDIT = Path(__file__).resolve().parent.parent
PAINEL = AUDIT / "data" / "processed" / "panel_wdi_expandido_1960_2023.csv"
OUT = AUDIT / "outputs" / "channels"

LAG_ANOS = 5
N_BOOT = 500
SEED = 42
ALPHA = 0.05

WGI_LIST = ["WGI_CC", "WGI_GE", "WGI_PV", "WGI_RQ", "WGI_RL", "WGI_VA"]

# Variáveis da matriz de parciais (controle padrão: ln PIB)
VARIAVEIS = [
    "ln_tertiaria", "ln_gdp_pc", "SE_XPD_TOTL_GD_ZS", "GB_XPD_RSDV_GD_ZS",
    "SP_DYN_LE00_IN", "SI_POV_GINI", "SP_URB_TOTL_IN_ZS",
    "NV_IND_MANF_ZS", "TX_VAL_TECH_MF_ZS", "BX_KLT_DINV_WD_GD_ZS",
    "WGI_media", "WGI_CC", "WGI_GE",
]

LABEL = {
    "ln_tertiaria": "Matrícula terciária (log)",
    "ln_gdp_pc": "PIB per capita (log)",
    "SE_XPD_TOTL_GD_ZS": "Gasto público educacional (% PIB)",
    "GB_XPD_RSDV_GD_ZS": "P&D (% PIB)",
    "SP_DYN_LE00_IN": "Expectativa de vida",
    "SI_POV_GINI": "Gini",
    "SP_URB_TOTL_IN_ZS": "Urbanização (% pop.)",
    "NV_IND_MANF_ZS": "Indústria manufatureira (% PIB)",
    "TX_VAL_TECH_MF_ZS": "Exportação alta tecnologia (% manuf.)",
    "BX_KLT_DINV_WD_GD_ZS": "IDE (% PIB)",
    "WGI_media": "WGI (média 6 indicadores)",
    "WGI_CC": "WGI — Controle da corrupção",
    "WGI_GE": "WGI — Efetividade governamental",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def carregar_painel() -> pd.DataFrame:
    df = pd.read_csv(PAINEL)
    df["ln_gdp_pc"] = np.log(df["NY_GDP_PCAP_KD"].where(df["NY_GDP_PCAP_KD"] > 0))
    df["ln_tertiaria"] = np.log(df["SE_TER_ENRR"].where(df["SE_TER_ENRR"] > 0))
    df["WGI_media"] = df[WGI_LIST].mean(axis=1)
    df["ln_tertiaria_lag5"] = df.groupby("iso3")["ln_tertiaria"].shift(LAG_ANOS)
    df["GB_XPD_RSDV_GD_ZS_lag5"] = df.groupby("iso3")["GB_XPD_RSDV_GD_ZS"].shift(LAG_ANOS)
    return df.sort_values(["iso3", "year"]).reset_index(drop=True)


def _ols_residuals(y: np.ndarray, X_controles: np.ndarray) -> np.ndarray:
    """Resíduos de y sobre controles (com intercepto)."""
    X = np.column_stack([np.ones(len(y)), X_controles])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ coef


def corr_parcial(df: pd.DataFrame, x: str, y: str, controles: list[str]) -> dict:
    """Correlação parcial de Pearson (resíduos de x e y sobre controles).

    Controles que colidem com x ou y são descartados (evita colunas
    duplicadas em pandas quando a variável de interesse é também controle).
    """
    controles = [c for c in controles if c not in {x, y}]
    cols = [x, y] + controles
    d = df[cols].dropna()
    n = len(d)
    if n < 10:
        return {"x": x, "y": y, "controles": controles, "rho_parcial": None,
                "n": int(n), "ic_boot_inf": None, "ic_boot_sup": None}
    rx = _ols_residuals(d[x].to_numpy(), d[controles].to_numpy() if controles else np.empty((n, 0)))
    ry = _ols_residuals(d[y].to_numpy(), d[controles].to_numpy() if controles else np.empty((n, 0)))
    rho = float(np.corrcoef(rx, ry)[0, 1])
    return {"x": x, "y": y, "controles": controles, "rho_parcial": rho,
            "n": int(n), "ic_boot_inf": None, "ic_boot_sup": None}


def bootstrap_pais(df: pd.DataFrame, x: str, y: str, controles: list[str],
                   rng: np.random.Generator) -> tuple[float, float]:
    """Cluster bootstrap por país para a correlação parcial; retorna IC (2.5, 97.5)."""
    paises = df["iso3"].unique()
    rhos = []
    for _ in range(N_BOOT):
        amostra_paises = rng.choice(paises, size=len(paises), replace=True)
        sub = df[df["iso3"].isin(amostra_paises)]
        r = corr_parcial(sub, x, y, controles)["rho_parcial"]
        if r is not None and not math.isnan(r):
            rhos.append(r)
    if len(rhos) < 100:
        return (np.nan, np.nan)
    return (float(np.percentile(rhos, 100 * ALPHA / 2)),
            float(np.percentile(rhos, 100 * (1 - ALPHA / 2))))


def matriz_parciais(df: pd.DataFrame) -> list[dict]:
    rng = np.random.default_rng(SEED)
    out = []
    for i, x in enumerate(VARIAVEIS):
        for y in VARIAVEIS[i + 1:]:
            # controle padrão: ln PIB; se o par envolve PIB, usa WGI média
            if "ln_gdp_pc" in {x, y}:
                controles = ["WGI_media"]
            else:
                controles = ["ln_gdp_pc"]
            r = corr_parcial(df, x, y, controles)
            r["ic_boot_inf"], r["ic_boot_sup"] = bootstrap_pais(
                df, x, y, controles, rng
            )
            out.append(r)
    return out


def analise_etapas(df: pd.DataFrame) -> list[dict]:
    rng = np.random.default_rng(SEED)
    etapas = [
        {"ordem": 0, "etapa": "inicial", "controle": "nenhum", "controles": []},
        {"ordem": 1, "etapa": "wgi", "controle": "wgi", "controles": ["WGI_media"]},
        {"ordem": 2, "etapa": "estrutura", "controle": "wgi+estrutura",
         "controles": ["WGI_media", "SE_XPD_TOTL_GD_ZS", "GB_XPD_RSDV_GD_ZS",
                       "SP_URB_TOTL_IN_ZS", "NV_IND_MANF_ZS"]},
        {"ordem": 3, "etapa": "saude", "controle": "saude",
         "controles": ["WGI_media", "SE_XPD_TOTL_GD_ZS", "GB_XPD_RSDV_GD_ZS",
                       "SP_URB_TOTL_IN_ZS", "NV_IND_MANF_ZS", "SP_DYN_LE00_IN"]},
    ]
    for e in etapas:
        r = corr_parcial(df, "ln_tertiaria", "ln_gdp_pc", e["controles"])
        e["rho"] = r["rho_parcial"]
        e["n"] = r["n"]
        e["ic_boot_inf"], e["ic_boot_sup"] = bootstrap_pais(
            df, "ln_tertiaria", "ln_gdp_pc", e["controles"], rng
        )
    return etapas


def painel_fe(df: pd.DataFrame, y: str, x_lag: str,
              controles_extra: list[str] | None = None) -> dict:
    """Regressão com FE de país e ano; erros clusterizados por país."""
    from statsmodels.formula.api import ols

    d = df.copy()
    d["WGI_media"] = d[WGI_LIST].mean(axis=1)
    controles = ["WGI_media", "SE_XPD_TOTL_GD_ZS", "GB_XPD_RSDV_GD_ZS",
                 "SP_URB_TOTL_IN_ZS", "NV_IND_MANF_ZS"]
    controles = controles + (controles_extra or [])
    subset = [y, x_lag] + controles
    amostra = d.dropna(subset=subset).copy()
    if len(amostra) < 30 or amostra["iso3"].nunique() < 10:
        return {"especificacao": f"{y} ~ {x_lag} + controles + FE",
                "coef": None, "p_value": None, "n_clusters": 0, "n_obs": 0,
                "cluster": "por_pais", "aviso": "amostra insuficiente"}
    amostra["iso3_cat"] = amostra["iso3"].astype("category")
    amostra["year_cat"] = amostra["year"].astype("category")
    formula = (f"{y} ~ {x_lag} + " + " + ".join(controles)
               + " + C(iso3_cat) + C(year_cat)")
    model = ols(formula, data=amostra).fit(
        cov_type="cluster", cov_kwds={"groups": amostra["iso3"]}
    )
    return {
        "especificacao": formula,
        "coef": float(model.params[x_lag]),
        "ic_inf": float(model.conf_int().loc[x_lag][0]),
        "ic_sup": float(model.conf_int().loc[x_lag][1]),
        "p_value": float(model.pvalues[x_lag]),
        "cluster": "por_pais",
        "n_clusters": int(amostra["iso3"].nunique()),
        "n_obs": int(len(amostra)),
        "nota": ("associação condicional dentro do país (FE), com controles; "
                 "sem inferência causal"),
    }


def canais(df: pd.DataFrame) -> dict:
    return {
        "saude": painel_fe(df, "SP_DYN_LE00_IN", "ln_tertiaria_lag5"),
        "desigualdade": painel_fe(df, "SI_POV_GINI", "ln_tertiaria_lag5"),
        "inovacao": painel_fe(df, "TX_VAL_TECH_MF_ZS", "GB_XPD_RSDV_GD_ZS_lag5"),
    }


def interacoes(df: pd.DataFrame) -> list[dict]:
    from statsmodels.formula.api import ols

    d = df.copy()
    d["WGI_media"] = d[WGI_LIST].mean(axis=1)
    d["ln_tertiaria_lag5_WGI_media"] = d["ln_tertiaria_lag5"] * d["WGI_media"]
    d["ln_tertiaria_lag5_GB_XPD_RSDV_GD_ZS_lag5"] = (
        d["ln_tertiaria_lag5"] * d["GB_XPD_RSDV_GD_ZS_lag5"]
    )
    controles = ["SE_XPD_TOTL_GD_ZS", "GB_XPD_RSDV_GD_ZS",
                 "SP_URB_TOTL_IN_ZS", "NV_IND_MANF_ZS"]

    resultados = []
    for termo in ["ln_tertiaria_lag5_WGI_media",
                  "ln_tertiaria_lag5_GB_XPD_RSDV_GD_ZS_lag5"]:
        subset = ["ln_gdp_pc", "ln_tertiaria_lag5", termo] + controles
        amostra = d.dropna(subset=subset).copy()
        if len(amostra) < 30 or amostra["iso3"].nunique() < 10:
            resultados.append({"termo": termo, "coef": None, "p_value": None,
                               "n_obs": 0, "exploratorio": True,
                               "aviso": "amostra insuficiente"})
            continue
        amostra["iso3_cat"] = amostra["iso3"].astype("category")
        amostra["year_cat"] = amostra["year"].astype("category")
        formula = (f"ln_gdp_pc ~ ln_tertiaria_lag5 + {termo} + "
                   + " + ".join(controles) + " + C(iso3_cat) + C(year_cat)")
        model = ols(formula, data=amostra).fit(
            cov_type="cluster", cov_kwds={"groups": amostra["iso3"]}
        )
        resultados.append({
            "termo": termo,
            "coef": float(model.params[termo]),
            "ic_inf": float(model.conf_int().loc[termo][0]),
            "ic_sup": float(model.conf_int().loc[termo][1]),
            "p_value": float(model.pvalues[termo]),
            "cluster": "por_pais",
            "n_clusters": int(amostra["iso3"].nunique()),
            "n_obs": int(len(amostra)),
            "exploratorio": True,
            "nota": ("exploratório: interação no painel FE clusterizado; "
                     "não é evidência de moderação causal"),
        })
    return resultados


def loocv_parciais(df: pd.DataFrame) -> tuple[list[dict], int]:
    """LOOCV por país das duas parciais centrais."""
    pares = [
        ("ln_tertiaria", "ln_gdp_pc",
         ["WGI_media", "SE_XPD_TOTL_GD_ZS", "GB_XPD_RSDV_GD_ZS",
          "SP_URB_TOTL_IN_ZS", "NV_IND_MANF_ZS", "SP_DYN_LE00_IN"]),
        ("ln_tertiaria", "SP_DYN_LE00_IN", ["ln_gdp_pc"]),
    ]
    folds = []
    paises = sorted(df["iso3"].unique())
    for iso in paises:
        treino = df[df["iso3"] != iso]
        teste = df[df["iso3"] == iso]
        fold = {"pais_excluido": iso, "parciais": {}}
        for x, y, ctrl in pares:
            r_treino = corr_parcial(treino, x, y, ctrl)
            r_teste = corr_parcial(teste, x, y, ctrl)
            chave = f"{x}__{y}"
            fold["parciais"][chave] = {
                "rho_treino": r_treino["rho_parcial"],
                "n_treino": r_treino["n"],
                "rho_teste": r_teste["rho_parcial"],
                "n_teste": r_teste["n"],
                "diferenca": (None if r_treino["rho_parcial"] is None or
                              r_teste["rho_parcial"] is None
                              else r_treino["rho_parcial"] - r_teste["rho_parcial"]),
            }
        folds.append(fold)
    return folds, len(paises)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    df = carregar_painel()
    n_paises = int(df["iso3"].nunique())
    print(f"Painel carregado: {n_paises} países, {len(df)} obs país-ano")

    prov = {
        "spec": "SPEC-935-R413",
        "painel_fonte": "data/processed/panel_wdi_expandido_1960_2023.csv",
        "sha256_painel": sha256_file(PAINEL),
        "n_paises": n_paises,
        "n_pais_ano": int(len(df)),
        "n_bootstrap": N_BOOT,
        "seed": SEED,
        "lag_anos": LAG_ANOS,
        "proveniencia_fechada": True,
        "nota_metodologica": (
            "Correlações parciais de Pearson sobre resíduos; IC via cluster "
            "bootstrap por país (500 replicações, seed 42). Painel FE com erros "
            "padrão clusterizados por país. Linguagem associativa; nenhuma "
            "inferência causal."),
    }

    prov["parciais"] = matriz_parciais(df)
    prov["etapas"] = analise_etapas(df)
    prov["canais"] = canais(df)
    prov["interacoes"] = interacoes(df)

    folds, n_paises_loocv = loocv_parciais(df)
    prov["loocv_folds"] = n_paises_loocv
    (OUT / "loocv_folds_channels.json").write_text(
        json.dumps({"n_folds": n_paises_loocv, "folds": folds},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    (OUT / "provenance_r413.json").write_text(
        json.dumps(prov, ensure_ascii=False, indent=2, allow_nan=True),
        encoding="utf-8",
    )

    # --- tabelas ---
    pd.DataFrame(prov["parciais"]).to_csv(OUT / "tabela_parciais.csv", index=False)
    pd.DataFrame(prov["etapas"]).to_csv(OUT / "tabela_etapas.csv", index=False)
    canais_flat = []
    for nome, c in prov["canais"].items():
        canais_flat.append({"canal": nome, **c})
    pd.DataFrame(canais_flat).to_csv(OUT / "tabela_canais.csv", index=False)
    pd.DataFrame(prov["interacoes"]).to_csv(OUT / "tabela_interacoes.csv", index=False)

    # --- resumo para log ---
    for e in prov["etapas"]:
        print(f"Etapa {e['ordem']} ({e['etapa']}): rho={e['rho']:.3f} "
              f"IC=[{e['ic_boot_inf']:.3f},{e['ic_boot_sup']:.3f}] n={e['n']}")
    for nome, c in prov["canais"].items():
        print(f"Canal {nome}: coef={c['coef']:.4f} p={c['p_value']:.4f} "
              f"clusters={c['n_clusters']}")
    print(f"LOOCV: {prov['loocv_folds']} folds")
    print("R413 concluído em outputs/channels/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
