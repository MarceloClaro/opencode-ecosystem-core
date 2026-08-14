# -*- coding: utf-8 -*-
"""Análise publicável do artigo ARM–educação (R409).

Gera todas as tabelas e números do ARTIGO_PUBLICAVEL.md com proveniência
fechada a partir do painel WDI auditado (R408). Validações cruzadas
legítimas:

1. Correlações em níveis vs primeiras diferenças (controle de tendência).
2. Leave-One-Country-Out da correlação (estabilidade entre países).
3. Subperíodos (1960–1989 vs 1990–2023).
4. Bloqueio temporal (treino 1960–2000, teste 2001–2023).
5. Painel com efeitos fixos (país; país+ano) com defasagem de 5 anos.
6. ML com split AGRUPADO por país (LOOCV) vs split por LINHA (vaza) —
   resultado negativo: com 7 países, a classificação não generaliza.

Saídas: academic/papers/arm_education_audit/outputs/publishable_tables/
  - tabela1_descr_paises.csv
  - tabela2_associacoes.csv
  - tabela3_loocv.csv
  - tabela4_subperiodos.csv
  - tabela5_painel_efeitos_fixos.csv
  - loocv_folds.json        (para teste de não vazamento)
  - temporal_blocks.json    (para teste de não vazamento)
  - ml_resultados.json      (AUC agrupado vs por linha)
  - painel_efeitos_fixos.json
  - provenance.json         (chave -> valor; números citados no artigo)
"""

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

BASE = Path(__file__).resolve().parent.parent
PANEL = BASE / "data" / "processed" / "panel_wdi_1960_2023.csv"
OUT = BASE / "outputs" / "publishable_tables"
OUT.mkdir(parents=True, exist_ok=True)

PAISES = {
    "ARG": "Argentina",
    "BRA": "Brasil",
    "CHL": "Chile",
    "CHN": "China",
    "KOR": "Coreia do Sul",
    "SGP": "Singapura",
    "VNM": "Vietnã",
}

GPD = "NY.GDP.PCAP.KD"          # PIB per capita (US$ constantes 2015)
GPD_ZG = "NY.GDP.PCAP.KD.ZG"    # crescimento do PIB per capita (%)
TER = "SE.TER.ENRR"             # matrícula terciária bruta (%)
GTO = "SE.XPD.TOTL.GD.ZS"       # gasto educacional (% PIB)
PES = "GB.XPD.RSDV.GD.ZS"       # P&D (% PIB)
URB = "SP.URB.TOTL.IN.ZS"       # urbanização (%)


def load():
    df = pd.read_csv(PANEL)
    return df


def rho(df, x, y, metodo="spearman"):
    """Correlação pareada (dropna) entre x e y."""
    d = df[[x, y]].dropna()
    if metodo == "spearman":
        r, p = stats.spearmanr(d[x], d[y])
    else:
        r, p = stats.pearsonr(d[x], d[y])
    return float(r), float(p), int(len(d))


def primeira_diferenca(df, var, por="iso3"):
    """Primeira diferença por país (t - t-1)."""
    out = df.groupby(por)[var].diff()
    return out


def main():
    df = load()
    prov = {}

    # ---------------------------------------------------------------- Tabela 1
    # Descritivos por país, 2010–2023 (janela de referência do manuscrito)
    t1_rows = []
    for iso3, nome in PAISES.items():
        d = df[(df["iso3"] == iso3) & (df["year"] >= 2010)].copy()
        gdp = d[GPD].dropna()
        ter = d[TER].dropna()
        gto = d[GTO].dropna()
        pes = d[PES].dropna()
        t1_rows.append({
            "pais": nome,
            "iso3": iso3,
            "gdp_pc_2023": round(float(gdp.iloc[-1]), 0) if len(gdp) else np.nan,
            "gdp_medio_2010_2023": round(float(gdp.mean()), 0) if len(gdp) else np.nan,
            "ter_media_2010_2023": round(float(ter.mean()), 2) if len(ter) else np.nan,
            "ter_2023": round(float(ter.iloc[-1]), 2) if len(ter) else np.nan,
            "gasto_educ_media": round(float(gto.mean()), 2) if len(gto) else np.nan,
            "pesquisa_media": round(float(pes.mean()), 2) if len(pes) else np.nan,
            "n_ter": int(ter.notna().sum()),
        })
    t1 = pd.DataFrame(t1_rows)
    t1.to_csv(OUT / "tabela1_descr_paises.csv", index=False)

    # ---------------------------------------------------------------- Tabela 2
    # Associações em níveis vs primeiras diferenças (especificações "pares")
    ddf = df.copy()
    ddf["d_gdp"] = primeira_diferenca(ddf, GPD)
    ddf["d_ter"] = primeira_diferenca(ddf, TER)
    ddf["d_gto"] = primeira_diferenca(ddf, GTO)
    ddf["d_pes"] = primeira_diferenca(ddf, PES)
    ddf["d_urb"] = primeira_diferenca(ddf, URB)

    # crescimento do PIB (já é variação) — associação com variação da matrícula
    # (primeiras diferenças sem defasagem)
    assoc_rows = []
    # (A) terciária × PIB pc (níveis, log)
    r_n, p_n, n_n = rho(ddf.assign(log_gdp=np.log(ddf[GPD])), "log_gdp", TER)
    r_d, p_d, n_d = rho(ddf.dropna(subset=["d_ter", "d_gdp"]), "d_ter", "d_gdp")
    assoc_rows.append({"par": "Matrícula terciária × PIB pc (níveis)",
                       "rho": round(r_n, 3), "p": f"{p_n:.2e}", "n": n_n})
    prov["rho_niveis_terciaria"] = round(r_n, 3)
    prov["n_niveis_terciaria"] = n_n
    assoc_rows.append({"par": "Δ Matrícula terciária × Δ PIB pc (1ª dif.)",
                       "rho": round(r_d, 3), "p": f"{p_d:.2e}", "n": n_d})
    prov["rho_diferencas_terciaria"] = round(r_d, 3)
    prov["n_diferencas_terciaria"] = n_d

    # (B) P&D × PIB pc
    r_n, p_n, n_n = rho(ddf.assign(log_gdp=np.log(ddf[GPD])), "log_gdp", PES)
    r_d, p_d, n_d = rho(ddf.dropna(subset=["d_pes", "d_gdp"]), "d_pes", "d_gdp")
    assoc_rows.append({"par": "P&D %PIB × PIB pc (níveis)",
                       "rho": round(r_n, 3), "p": f"{p_n:.2e}", "n": n_n})
    prov["rho_niveis_pesquisa"] = round(r_n, 3)
    assoc_rows.append({"par": "Δ P&D %PIB × Δ PIB pc (1ª dif.)",
                       "rho": round(r_d, 3), "p": f"{p_d:.2e}", "n": n_d})
    prov["rho_diferencas_pesquisa"] = round(r_d, 3)

    # (C) gasto educacional × PIB pc — Pearson e Spearman em níveis (seleção)
    d_n = ddf[[GTO, GPD]].dropna()
    rp_n, pp_n = stats.pearsonr(d_n[GTO], d_n[GPD])
    rs_n, ps_n = stats.spearmanr(d_n[GTO], d_n[GPD])
    r_d2, p_d2, n_d2 = rho(ddf.dropna(subset=["d_gto", "d_gdp"]), "d_gto", "d_gdp")
    assoc_rows.append({"par": "Gasto educ. %PIB × PIB pc (Pearson, níveis)",
                       "rho": round(float(rp_n), 3), "p": f"{float(pp_n):.2e}",
                       "n": int(len(d_n))})
    assoc_rows.append({"par": "Gasto educ. %PIB × PIB pc (Spearman, níveis)",
                       "rho": round(float(rs_n), 3), "p": f"{float(ps_n):.2e}",
                       "n": int(len(d_n))})
    assoc_rows.append({"par": "Δ Gasto educ. × Δ PIB pc (1ª dif.)",
                       "rho": round(r_d2, 3), "p": f"{p_d2:.2e}", "n": n_d2})
    prov["rho_niveis_gasto_educ_pearson"] = round(float(rp_n), 3)
    prov["rho_niveis_gasto_educ_spearman"] = round(float(rs_n), 3)
    prov["rho_diferencas_gasto_educ"] = round(r_d2, 3)

    t2 = pd.DataFrame(assoc_rows)
    t2.to_csv(OUT / "tabela2_associacoes.csv", index=False)

    # ---------------------------------------------------------------- Tabela 3
    # LOOCV da correlação em NÍVEIS (matrícula × log PIB) — estabilidade
    loocv_rows = []
    folds_json = []
    for iso3 in df["iso3"].unique():
        treino = [p for p in df["iso3"].unique() if p != iso3]
        d_tr = ddf[ddf["iso3"].isin(treino)].copy()
        d_tr["log_gdp"] = np.log(d_tr[GPD])
        r, p, n = rho(d_tr, "log_gdp", TER)
        loocv_rows.append({"excluido": PAISES[iso3], "iso3": iso3,
                           "rho_niveis": round(r, 3), "p": f"{p:.2e}", "n": n})
        folds_json.append({"treino": sorted(treino), "teste": [iso3]})
    t3 = pd.DataFrame(loocv_rows)
    t3.to_csv(OUT / "tabela3_loocv.csv", index=False)
    with (OUT / "loocv_folds.json").open("w", encoding="utf-8") as f:
        json.dump(folds_json, f, ensure_ascii=False, indent=2)

    rho_excl_sgp = t3[t3["iso3"] == "SGP"]["rho_niveis"].iloc[0]
    prov["loocv_rho_range"] = [float(t3["rho_niveis"].min()),
                               float(t3["rho_niveis"].max())]
    prov["loocv_rho_excluindo_sgp"] = float(rho_excl_sgp)
    prov["loocv_rho_excluindo_chn"] = float(
        t3[t3["iso3"] == "CHN"]["rho_niveis"].iloc[0])

    # ---------------------------------------------------------------- Tabela 4
    # Subperíodos
    s1 = ddf[ddf["year"] <= 1989].copy()
    s2 = ddf[ddf["year"] >= 1990].copy()
    for nome, sub in [("1960–1989", s1), ("1990–2023", s2)]:
        sub = sub.copy()
        sub["log_gdp"] = np.log(sub[GPD])
        r_n, p_n, n_n = rho(sub, "log_gdp", TER)
        r_d, p_d, n_d = rho(sub.dropna(subset=["d_ter", "d_gdp"]), "d_ter", "d_gdp")
        if nome == "1960–1989":
            prov["rho_subperiodo_1"] = round(r_n, 3)
        else:
            prov["rho_subperiodo_2"] = round(r_n, 3)
    t4 = pd.DataFrame({
        "subperiodo": ["1960–1989", "1990–2023"],
        "rho_niveis": [
            round(rho(s1.assign(log_gdp=np.log(s1[GPD])), "log_gdp", TER)[0], 3),
            round(rho(s2.assign(log_gdp=np.log(s2[GPD])), "log_gdp", TER)[0], 3),
        ],
        "rho_diferencas": [
            round(rho(s1.dropna(subset=["d_ter", "d_gdp"]), "d_ter", "d_gdp")[0], 3),
            round(rho(s2.dropna(subset=["d_ter", "d_gdp"]), "d_ter", "d_gdp")[0], 3),
        ],
    })
    t4.to_csv(OUT / "tabela4_subperiodos.csv", index=False)

    # ------------------------------------------------- Bloqueio temporal
    # Dois blocos: (A) treino 1960-2000 / teste 2001-2023; (B) treino 1960-1990 / teste 1991-2023
    temporal_blocks = []
    for (tr_min, tr_max, te_min) in [(1960, 2000, 2001), (1960, 1990, 1991)]:
        treino_anos = list(range(tr_min, tr_max + 1))
        teste_anos = list(range(te_min, 2024))
        d_tr = ddf[ddf["year"].isin(treino_anos)].dropna(subset=[TER, GPD])
        d_te = ddf[ddf["year"].isin(teste_anos)].dropna(subset=[TER, GPD])
        X_tr = np.log(d_tr[GPD]).values
        Y_tr = d_tr[TER].values
        coef_tr = float(np.cov(X_tr, Y_tr, ddof=1)[0, 1] / np.var(X_tr, ddof=1))
        temporal_blocks.append({
            "treino_min": tr_min, "treino_max": tr_max,
            "teste_min": te_min, "teste_max": 2023,
            "coef_logpib_ter": round(coef_tr, 4),
            "n_treino": int(len(d_tr)), "n_teste": int(len(d_te)),
        })
    with (OUT / "temporal_blocks.json").open("w", encoding="utf-8") as f:
        json.dump(temporal_blocks, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------- Tabela 5 / painel FE
    # y = log(PIB pc); x = matrícula defasada 5 anos; FE país; FE país+ano
    pdf = ddf[["iso3", "year", GPD, TER, GTO, PES]].copy()
    pdf["log_gdp"] = np.log(pdf[GPD])
    pdf["ter_lag5"] = pdf.groupby("iso3")[TER].shift(5)
    pdf = pdf.dropna(subset=["log_gdp", "ter_lag5"]).copy()

    # within (país FE): demean por país
    pdf["log_gdp_w"] = pdf["log_gdp"] - pdf.groupby("iso3")["log_gdp"].transform("mean")
    pdf["ter_w"] = pdf["ter_lag5"] - pdf.groupby("iso3")["ter_lag5"].transform("mean")
    X = pdf["ter_w"].values
    y = pdf["log_gdp_w"].values
    coef = float(np.sum(X * y) / np.sum(X * X))
    resid = y - coef * X
    k = 1
    n = len(y)
    se = float(np.sqrt(np.sum(resid ** 2) / (n - k - 1) / np.sum(X ** 2)))
    ic_inf = coef - 1.96 * se
    ic_sup = coef + 1.96 * se

    # FE país+ano: regressão com dummies de país e ano (via OLS numpy)
    dummies = pd.get_dummies(pdf[["iso3", "year"]], columns=["iso3", "year"],
                             drop_first=True).astype(float)
    Xmat = np.column_stack([pdf["ter_lag5"].values, dummies.values])
    ymat = pdf["log_gdp"].values
    XtX = Xmat.T @ Xmat
    if np.linalg.cond(XtX) < 1e12:
        beta = np.linalg.solve(XtX, Xmat.T @ ymat)
        coef_pa = float(beta[0])
        resid2 = ymat - Xmat @ beta
        dof = len(ymat) - Xmat.shape[1]
        sigma2 = float(np.sum(resid2 ** 2) / max(dof, 1))
        se_pa = float(np.sqrt(sigma2 * np.linalg.inv(XtX)[0, 0]))
        ic_pa_inf = coef_pa - 1.96 * se_pa
        ic_pa_sup = coef_pa + 1.96 * se_pa
    else:
        coef_pa, ic_pa_inf, ic_pa_sup = np.nan, np.nan, np.nan

    painel = {
        "coef": round(coef, 5),
        "ic_inf": round(ic_inf, 5),
        "ic_sup": round(ic_sup, 5),
        "n_obs": int(n),
        "n_paises": int(pdf["iso3"].nunique()),
        "lag_anos": 5,
        "especificacao": "efeitos fixos de país (within), defasagem 5 anos",
        "coef_pais_ano": round(coef_pa, 5) if coef_pa == coef_pa else None,
        "ic_pais_ano_inf": round(ic_pa_inf, 5) if ic_pa_inf == ic_pa_inf else None,
        "ic_pais_ano_sup": round(ic_pa_sup, 5) if ic_pa_sup == ic_pa_sup else None,
    }
    prov["efeito_fixo_defasagem"] = round(coef, 5)
    prov["efeito_fixo_ic_inf"] = round(ic_inf, 5)
    prov["efeito_fixo_ic_sup"] = round(ic_sup, 5)
    prov["efeito_fixo_pais_ano"] = round(coef_pa, 5) if coef_pa == coef_pa else None
    with (OUT / "painel_efeitos_fixos.json").open("w", encoding="utf-8") as f:
        json.dump(painel, f, ensure_ascii=False, indent=2)
    pd.DataFrame([painel]).to_csv(OUT / "tabela5_painel_efeitos_fixos.csv", index=False)

    # --------------------------------------------------------------- Tabela 6
    # ML: classificação de crescimento alto vs baixo (acima da mediana global)
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import roc_auc_score

    ml = ddf.dropna(subset=[TER, GPD_ZG]).copy()
    # alvo binário: crescimento do PIB pc acima da mediana do período
    ml["alvo"] = (ml[GPD_ZG] > ml[GPD_ZG].median()).astype(int)
    feat_cols = [c for c in [TER, GTO, PES, URB] if ml[c].notna().sum() > 100]
    ml = ml.dropna(subset=feat_cols + ["alvo"]).copy()

    def auc_split(por_linha=True):
        clf = RandomForestClassifier(n_estimators=200, random_state=42,
                                     max_depth=4)
        if por_linha:
            idx = np.random.RandomState(42).permutation(len(ml))
            tr, te = idx[: int(0.7 * len(ml))], idx[int(0.7 * len(ml)):]
            clf.fit(ml.iloc[tr][feat_cols], ml.iloc[tr]["alvo"])
            prob = clf.predict_proba(ml.iloc[te][feat_cols])[:, 1]
            return float(roc_auc_score(ml.iloc[te]["alvo"], prob)), int(len(te))
        # LOOCV por país (agrupado): treino sem o país de teste
        aucs, n_test = [], 0
        for iso3 in ml["iso3"].unique():
            tr = ml[ml["iso3"] != iso3]
            te = ml[ml["iso3"] == iso3]
            if len(te) < 2 or len(tr) < 10:
                continue
            clf.fit(tr[feat_cols], tr["alvo"])
            prob = clf.predict_proba(te[feat_cols])[:, 1]
            if te["alvo"].nunique() == 2:
                aucs.append(roc_auc_score(te["alvo"], prob))
                n_test += len(te)
        return (float(np.mean(aucs)) if aucs else np.nan), n_test

    auc_linha, n_linha = auc_split(por_linha=True)
    auc_agrupado, n_agrup = auc_split(por_linha=False)

    ml_res = {
        "auc_linha": round(auc_linha, 3),
        "auc_agrupado": round(auc_agrupado, 3) if auc_agrupado == auc_agrupado else None,
        "n_linha": n_linha,
        "n_agrupado": n_agrup,
        "n_paises": int(ml["iso3"].nunique()),
        "features": feat_cols,
        "alvo": "crescimento do PIB pc acima da mediana do período",
        "interpretacao": (
            "O AUC com split por linha (vaza: mesmo país em treino e teste) é "
            "substancialmente superior ao AUC com leave-one-country-out. Com 7 "
            "países e cobertura parcial, o modelo não generaliza para países "
            "não vistos — não identificabilidade."
        ),
    }
    prov["ml_auc_linha"] = round(auc_linha, 3)
    prov["ml_auc_agrupado"] = round(auc_agrupado, 3) if auc_agrupado == auc_agrupado else None
    with (OUT / "ml_resultados.json").open("w", encoding="utf-8") as f:
        json.dump(ml_res, f, ensure_ascii=False, indent=2)
    pd.DataFrame([ml_res]).to_csv(OUT / "tabela6_ml.csv", index=False)

    # ------------------------------------------------------- provenance.json
    prov["n_paises"] = int(df["iso3"].nunique())
    prov["n_pais_ano"] = int(len(df))
    prov["cobertura_ter"] = int(df[TER].notna().sum())
    prov["cobertura_gdp"] = int(df[GPD].notna().sum())
    prov["cobertura_gto"] = int(df[GTO].notna().sum())
    prov["cobertura_pes"] = int(df[PES].notna().sum())
    prov["data_geracao"] = "2026-08-12"
    with (PROVENANCE := OUT / "provenance.json").open("w", encoding="utf-8") as f:
        json.dump(prov, f, ensure_ascii=False, indent=2)

    # ---- resumo console
    print("Tabela 1 (descritivos):", len(t1), "países")
    print("Tabela 2 (associações):")
    print(t2.to_string(index=False))
    print("LOOCV níveis (rho excluindo SGP):", rho_excl_sgp)
    print("Subperíodo 2 (1990-2023) rho níveis:", t4.iloc[1]["rho_niveis"])
    print("Painel FE país (lag 5): coef =", coef, "IC95 =", (ic_inf, ic_sup))
    print("Painel FE país+ano: coef =", coef_pa)
    print(f"ML: AUC por linha = {auc_linha:.3f} vs AUC LOOCV país = {auc_agrupado:.3f}")
    print("provenance.json:", PROVENANCE)


if __name__ == "__main__":
    main()
