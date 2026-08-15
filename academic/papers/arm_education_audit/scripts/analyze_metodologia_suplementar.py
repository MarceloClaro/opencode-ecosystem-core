#!/usr/bin/env python3
"""R423 — Melhorias metodológicas pós-peer-review (SPEC-935-R423).

Implementa três complementos recomendados pelo blind peer review (R422),
sem alterar nenhum número já publicado:

1. ID 2 — dispersão dos folds de teste da LOOCV (seção 4.3):
   mediana/DP/IQR/min/max/%positivos do rho_teste por país + associação
   com o tamanho amostral do país (instabilidade em n pequeno).
2. ID 3 — especificação comparativa sem cluster (seção 4.5 / Tabela 5):
   mesmo modelo FE de país/ano com erros padrão homocedásticos.
3. ID 4 — limites de detecção e TOST (seção 4.10):
   MDES com poder 80% e teste de equivalência de dois one-sided com bounds
   ±0,10 e ±0,05 no log da matrícula terciária.

Artefatos novos (não sobrescreve R412/R418/R419):
  outputs/expanded/tabela12_loocv_dispersao.csv
  outputs/expanded/tabela5b_cluster_comparativo.csv
  outputs/expanded/tabela13_tost_deteccao.csv
  outputs/expanded/provenance_r423.json

Uso: python3 scripts/analyze_metodologia_suplementar.py
"""

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
OUT = ROOT / "outputs" / "expanded"

LAG_ANOS = 5


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def carregar_painel() -> pd.DataFrame:
    df = pd.read_csv(PROC / "panel_wdi_expandido_1960_2023.csv")
    return df


def carregar_folds() -> list[dict]:
    dados = json.loads((OUT / "loocv_folds_expanded.json").read_text(encoding="utf-8"))
    return dados["folds"]


def dispersao_loocv(folds: list[dict]) -> dict:
    """ID 2 — distribuição do rho_teste e associação com n do país."""
    pares = [
        (f["n_obs_excluidas"], f["rho_niveis_teste"])
        for f in folds
        if not math.isnan(f["rho_niveis_teste"])
    ]
    n_obs = np.array([p[0] for p in pares], dtype=float)
    rho_teste = np.array([p[1] for p in pares], dtype=float)
    validos = int(len(pares))

    res = {
        "n_folds_validos": validos,
        "n_folds_total": len(folds),
        "rho_teste_media": float(np.mean(rho_teste)),
        "rho_teste_mediana": float(np.median(rho_teste)),
        "rho_teste_dp": float(np.std(rho_teste, ddof=1)),
        "rho_teste_iqr": float(np.percentile(rho_teste, 75) - np.percentile(rho_teste, 25)),
        "rho_teste_min": float(np.min(rho_teste)),
        "rho_teste_max": float(np.max(rho_teste)),
        "rho_teste_pct_positivo": float(100.0 * np.mean(rho_teste > 0)),
        "n_obs_por_pais_min": int(np.min(n_obs)),
        "n_obs_por_pais_max": int(np.max(n_obs)),
    }

    # instabilidade: correlação entre n de observações do país e |rho_teste|
    if validos >= 5:
        rho_n, p_n = stats.spearmanr(n_obs, np.abs(rho_teste))
        res["corr_n_obs_x_abs_rho_teste"] = float(rho_n)
        res["corr_n_obs_x_abs_rho_teste_p"] = float(p_n)
        rho_pos, p_pos = stats.spearmanr(n_obs, rho_teste)
        res["corr_n_obs_x_rho_teste"] = float(rho_pos)
        res["corr_n_obs_x_rho_teste_p"] = float(p_pos)
    else:
        res["corr_n_obs_x_abs_rho_teste"] = None
        res["corr_n_obs_x_abs_rho_teste_p"] = None
        res["corr_n_obs_x_rho_teste"] = None
        res["corr_n_obs_x_rho_teste_p"] = None

    # IC95% empírico da média por bootstrap por país (seed fixa)
    rng = np.random.RandomState(42)
    medias = []
    n_boot = 2000
    for _ in range(n_boot):
        idx = rng.randint(0, validos, size=validos)
        medias.append(np.mean(rho_teste[idx]))
    res["rho_teste_media_ic95_inf"] = float(np.percentile(medias, 2.5))
    res["rho_teste_media_ic95_sup"] = float(np.percentile(medias, 97.5))
    res["bootstrap_replicacoes"] = n_boot
    res["semente"] = 42
    return res


def painel_fe_sem_cluster(df: pd.DataFrame) -> dict:
    """ID 3 — mesma especificação FE sem cluster (erros homocedásticos)."""
    from statsmodels.formula.api import ols

    d = df.copy()
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
    model = ols(formula, data=amostra).fit(cov_type="nonrobust")
    coef = float(model.params["ln_gdp_pc_lag5"])
    se = float(model.bse["ln_gdp_pc_lag5"])
    ic_inf, ic_sup = model.conf_int().loc["ln_gdp_pc_lag5"]
    return {
        "especificacao": "ln_tertiaria ~ ln_gdp_pc_lag5 + controles + FE pais + FE ano",
        "lag_anos": LAG_ANOS,
        "erros": "homocedasticos_sem_cluster",
        "coef": coef,
        "se": se,
        "ic_95_inf": float(ic_inf),
        "ic_95_sup": float(ic_sup),
        "p_value": float(model.pvalues["ln_gdp_pc_lag5"]),
        "n_clusters": int(amostra["iso3"].nunique()),
        "n_obs": int(len(amostra)),
    }


def tost_e_deteccao(coef_cluster: float, ic_inf: float, ic_sup: float) -> dict:
    """ID 4 — TOST e limite de detecção para o coeficiente nulo.

    coef_cluster: 0,073; IC95% [−0,169; 0,314] → SE = (0,314−0,073)/1,96.
    MDES = (z_0,975 + z_0,80) × SE (poder 80%, α 5% bilateral).
    TOST: dois testes unilaterais H0: coef ≥ +bound e H0: coef ≤ −bound.
    """
    z = stats.norm.ppf(0.975)  # 1,96
    se = (ic_sup - coef_cluster) / (2 * z)
    mdes = (z + stats.norm.ppf(0.80)) * se

    def tost(bound: float) -> dict:
        # t = (|coef| - bound) / SE  ~  N(0,1) assintótico (g.l. grande)
        t_sup = (coef_cluster - bound) / se
        t_inf = (-bound - coef_cluster) / se
        p_sup = stats.norm.cdf(t_sup)          # H0: coef >= bound
        p_inf = stats.norm.cdf(t_inf)          # H0: coef <= -bound
        p_tost = max(p_sup, p_inf)
        return {
            "bound": bound,
            "se_coef": float(se),
            "t_upper": float(t_sup),
            "p_upper": float(p_sup),
            "t_lower": float(t_inf),
            "p_lower": float(p_inf),
            "p_tost": float(p_tost),
            "conclusao": (
                "equivale" if p_tost < 0.05
                else "nao_rejeita_efeito_pequeno"
            ),
        }

    return {
        "coef_cluster": float(coef_cluster),
        "ic_95_inf": float(ic_inf),
        "ic_95_sup": float(ic_sup),
        "se_cluster": float(se),
        "mdes_poder80_alpha5": float(mdes),
        "z_alpha": float(z),
        "z_poder80": float(stats.norm.ppf(0.80)),
        "tost_010": tost(0.10),
        "tost_005": tost(0.05),
        "nota": (
            "MDES = (z_0,975 + z_0,80) x SE; TOST de dois unilaterais com "
            "bounds em log da matrícula terciária; p >= 0,05 indica que "
            "não se pode descartar efeito de magnitude superior ao bound."
        ),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    df = carregar_painel()
    folds = carregar_folds()

    d_loocv = dispersao_loocv(folds)
    d_sem_cluster = painel_fe_sem_cluster(df)

    # valores clusterizados (R412, não reexecutados aqui)
    prov_412 = json.loads((OUT / "provenance_expanded.json").read_text(encoding="utf-8"))
    coef_cluster = float(prov_412["efeito_fixo_cluster_coef"])
    ic_inf = float(prov_412["efeito_fixo_cluster_ic_inf"])
    ic_sup = float(prov_412["efeito_fixo_cluster_ic_sup"])
    se_cluster = float(prov_412.get("se_cluster", np.nan))
    if math.isnan(se_cluster):
        se_cluster = (ic_sup - coef_cluster) / (2 * stats.norm.ppf(0.975))
    d_tost = tost_e_deteccao(coef_cluster, ic_inf, ic_sup)

    # tabelas
    pd.DataFrame(
        [{
            "metrica": k,
            "valor": (v if not isinstance(v, (float, np.floating))
                      else round(float(v), 4)),
        } for k, v in d_loocv.items() if k not in ("nota",)]
    ).to_csv(OUT / "tabela12_loocv_dispersao.csv", index=False)

    pd.DataFrame([
        {"metrica": "coef_log_pib_lag5", "com_cluster": coef_cluster,
         "sem_cluster": d_sem_cluster["coef"], "se_cluster": se_cluster,
         "se_sem_cluster": d_sem_cluster["se"]},
        {"metrica": "ic_95_inf", "com_cluster": ic_inf,
         "sem_cluster": d_sem_cluster["ic_95_inf"],
         "se_cluster": None, "se_sem_cluster": None},
        {"metrica": "ic_95_sup", "com_cluster": ic_sup,
         "sem_cluster": d_sem_cluster["ic_95_sup"],
         "se_cluster": None, "se_sem_cluster": None},
        {"metrica": "p_value", "com_cluster": prov_412["p_value"],
         "sem_cluster": d_sem_cluster["p_value"],
         "se_cluster": None, "se_sem_cluster": None},
        {"metrica": "n_clusters", "com_cluster": prov_412["n_clusters"],
         "sem_cluster": d_sem_cluster["n_clusters"],
         "se_cluster": None, "se_sem_cluster": None},
        {"metrica": "n_obs", "com_cluster": prov_412["n_obs"],
         "sem_cluster": d_sem_cluster["n_obs"],
         "se_cluster": None, "se_sem_cluster": None},
    ]).to_csv(OUT / "tabela5b_cluster_comparativo.csv", index=False)

    linhas_tost = []
    for bound in (0.10, 0.05):
        t = d_tost[f"tost_{'010' if bound == 0.10 else '005'}"]
        linhas_tost.append({
            "bound": bound, "se_coef": round(t["se_coef"], 4),
            "p_upper": round(t["p_upper"], 4),
            "p_lower": round(t["p_lower"], 4),
            "p_tost": round(t["p_tost"], 4),
            "conclusao": t["conclusao"],
        })
    linhas_tost.append({"bound": "MDES", "se_coef": round(d_tost["se_cluster"], 4),
                        "p_upper": None, "p_lower": None, "p_tost": None,
                        "conclusao": f"mdes_poder80_alpha5={d_tost['mdes_poder80_alpha5']:.4f}"})
    pd.DataFrame(linhas_tost).to_csv(OUT / "tabela13_tost_deteccao.csv", index=False)

    # provenance
    prov = {
        "ciclo": "R423",
        "spec": "SPEC-935-R423-metodologia-suplementar.md",
        "painel_entrada": {
            "caminho": str((PROC / "panel_wdi_expandido_1960_2023.csv").relative_to(ROOT)),
            "sha256": sha256(PROC / "panel_wdi_expandido_1960_2023.csv"),
        },
        "folds_entrada": {
            "caminho": str((OUT / "loocv_folds_expanded.json").relative_to(ROOT)),
            "sha256": sha256(OUT / "loocv_folds_expanded.json"),
        },
        "loocv_dispersao": d_loocv,
        "painel_fe_sem_cluster": d_sem_cluster,
        "painel_fe_cluster_referencia": {
            "coef": coef_cluster, "ic_95_inf": ic_inf, "ic_95_sup": ic_sup,
            "se": se_cluster, "p_value": prov_412["p_value"],
            "n_clusters": prov_412["n_clusters"], "n_obs": prov_412["n_obs"],
        },
        "tost_deteccao": {k: v for k, v in d_tost.items() if k != "nota"},
        "nota": d_tost["nota"],
    }
    (OUT / "provenance_r423.json").write_text(
        json.dumps(prov, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("=== R423: melhorias metodológicas ===")
    print(f"LOOCV teste: média {d_loocv['rho_teste_media']:.3f} | "
          f"mediana {d_loocv['rho_teste_mediana']:.3f} | DP {d_loocv['rho_teste_dp']:.3f} | "
          f"IC95 média [{d_loocv['rho_teste_media_ic95_inf']:.3f}, "
          f"{d_loocv['rho_teste_media_ic95_sup']:.3f}] | %>0 {d_loocv['rho_teste_pct_positivo']:.1f}")
    print(f"corr n_obs × |rho_teste|: {d_loocv.get('corr_n_obs_x_abs_rho_teste'):.3f} "
          f"(p={d_loocv.get('corr_n_obs_x_abs_rho_teste_p'):.4f})")
    print(f"FE sem cluster: coef {d_sem_cluster['coef']:.4f} | SE {d_sem_cluster['se']:.4f} | "
          f"IC [{d_sem_cluster['ic_95_inf']:.3f}, {d_sem_cluster['ic_95_sup']:.3f}] | "
          f"p {d_sem_cluster['p_value']:.4f}")
    print(f"FE cluster (ref): coef {coef_cluster:.4f} | SE {se_cluster:.4f} | "
          f"IC [{ic_inf:.3f}, {ic_sup:.3f}]")
    print(f"MDES (poder 80%): {d_tost['mdes_poder80_alpha5']:.4f}")
    for b in (0.10, 0.05):
        t = d_tost[f"tost_{'010' if b == 0.10 else '005'}"]
        print(f"TOST ±{b:.2f}: p_tost = {t['p_tost']:.4f} -> {t['conclusao']}")
    print("Artefatos em outputs/expanded/ (tabela12, tabela5b, tabela13, provenance_r423.json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
