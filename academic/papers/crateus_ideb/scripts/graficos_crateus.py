#!/usr/bin/env python3
"""Gráficos do estudo Crateús-IDEB (R426) — matplotlib, sem geopandas.

Gera em outputs/figuras/:
1. fig_scatter_niveis_micro.png  — scatter IDEB × log PIB per capita (níveis,
   microrregião, por etapa), com reta de regressão linear e r de Pearson.
2. fig_serie_ideb_micro.png      — séries temporais do IDEB (anos iniciais e
   finais) por município da microrregião, 2007–2025, com linha de meta 2021.
3. fig_scatter_ganho_renda.png   — ganho de IDEB (2007→2025, AI) × renda média
   do responsável (Censo 2022), com r e p.
4. fig_loocv_r_teste.png         — r de teste do LOOCV por município (barras).

Uso: python3 scripts/graficos_crateus.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "data" / "processed"
OUT = RAIZ / "outputs" / "figuras"
OUT.mkdir(parents=True, exist_ok=True)

MUNICIPIOS_MICRO = [
    2301257, 2304103, 2305605, 2305654, 2308609,
    2309300, 2309409, 2311264, 2313203,
]
NOMES_MICRO = {
    2301257: "Ararendá", 2304103: "Crateús", 2305605: "Independência",
    2305654: "Ipaporanga", 2308609: "Monsenhor Tabosa", 2309300: "Nova Russas",
    2309409: "Novo Oriente", 2311264: "Quiterianópolis", 2313203: "Tamboril",
}
DEFASAGEM = 2


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
    pib["ano_def"] = pib["ano"] + DEFASAGEM
    painel = ideb_long.merge(pib[["cod_mun", "ano_def", "pib_per_capita"]],
                             left_on=["cod_mun", "ano_ideb"], right_on=["cod_mun", "ano_def"],
                             how="left")
    for c in ["renda_media_resp", "renda_mediana_resp"]:
        renda[c] = pd.to_numeric(renda[c], errors="coerce")
    painel = painel.merge(renda[["cod_mun", "renda_media_resp"]], on="cod_mun", how="left")
    painel["log_pibpc"] = np.log(painel["pib_per_capita"])
    painel["micro"] = painel["cod_mun"].isin(MUNICIPIOS_MICRO)
    return painel


def fig_scatter_niveis(painel: pd.DataFrame) -> Path:
    d = painel[painel["micro"]].dropna(subset=["ideb", "log_pibpc"])
    cores = {"anos_iniciais": "#1f77b4", "anos_finais": "#d62728"}
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for etapa, cor in cores.items():
        sub = d[d["etapa"] == etapa]
        ax.scatter(sub["log_pibpc"], sub["ideb"], c=cor, alpha=0.55,
                   edgecolor="white", linewidth=0.4, s=42,
                   label="Anos iniciais" if etapa == "anos_iniciais" else "Anos finais")
    # reta global
    m, b = np.polyfit(d["log_pibpc"], d["ideb"], 1)
    xr = np.linspace(d["log_pibpc"].min(), d["log_pibpc"].max(), 100)
    ax.plot(xr, m * xr + b, color="black", lw=1.2, ls="--",
            label=f"Reta de regressão (r = {stats.pearsonr(d['ideb'], d['log_pibpc']).statistic:.2f})")
    ax.set_xlabel("log do PIB per capita (R$, defasado 2 anos)")
    ax.set_ylabel("IDEB (rede municipal)")
    ax.set_title("Associação em níveis entre IDEB e renda — Sertão de Cratéus (2013–2023)")
    ax.legend(frameon=False, fontsize=8.5)
    ax.grid(alpha=0.25, ls=":")
    fig.tight_layout()
    p = OUT / "fig_scatter_niveis_micro.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_serie_ideb(painel: pd.DataFrame) -> Path:
    d = painel[painel["micro"]].dropna(subset=["ideb"]).copy()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6), sharey=True)
    for ax, etapa in zip(axes, ["anos_iniciais", "anos_finais"]):
        titulo = "Anos iniciais" if etapa == "anos_iniciais" else "Anos finais"
        sub = d[d["etapa"] == etapa]
        for cod in MUNICIPIOS_MICRO:
            s = sub[sub["cod_mun"] == cod].sort_values("ano_ideb")
            if len(s) < 3:
                continue
            ax.plot(s["ano_ideb"], s["ideb"], marker="o", ms=3, lw=1.1,
                    label=NOMES_MICRO[cod])
        # meta 2021 (projeção INEP) — média simples das metas por município
        ax.axhline(5.5, color="grey", lw=0.9, ls=":", label="Meta 2021 (média região)")
        ax.set_title(titulo, fontsize=11)
        ax.set_xlabel("Ano do IDEB")
        ax.grid(alpha=0.25, ls=":")
        if ax is axes[0]:
            ax.set_ylabel("IDEB (rede municipal)")
    axes[0].legend(frameon=False, fontsize=7.2, loc="upper left", ncol=1)
    fig.suptitle("Trajetória do IDEB por município — Sertão de Cratéus (2007–2025)",
                 fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    p = OUT / "fig_serie_ideb_micro.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_scatter_ganho_renda(painel: pd.DataFrame) -> Path:
    d = painel[painel["micro"]].dropna(subset=["ideb"]).copy()
    linhas = []
    for (cod, etapa), sub in d.groupby(["cod_mun", "etapa"]):
        base = sub[sub["ano_ideb"] == 2007]
        fim = sub[sub["ano_ideb"] == sub["ano_ideb"].max()]
        if base.empty or fim.empty:
            continue
        renda = float(sub["renda_media_resp"].dropna().iloc[0]) if sub["renda_media_resp"].notna().any() else np.nan
        linhas.append({"cod_mun": cod, "etapa": etapa,
                       "ganho": float(fim["ideb"].iloc[0]) - float(base["ideb"].iloc[0]),
                       "renda": renda})
    df = pd.DataFrame(linhas)
    df = df[(df["etapa"] == "anos_iniciais") & df["cod_mun"].isin(MUNICIPIOS_MICRO)]
    df = df.dropna(subset=["ganho", "renda"])
    r = stats.pearsonr(df["ganho"], df["renda"])
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for _, row in df.iterrows():
        ax.scatter(row["renda"], row["ganho"], s=60, c="#1f77b4",
                   edgecolor="white", linewidth=0.5, zorder=3)
        ax.annotate(NOMES_MICRO[int(row["cod_mun"])],
                    (row["renda"], row["ganho"]),
                    textcoords="offset points", xytext=(6, 5), fontsize=8)
    m, b = np.polyfit(df["renda"], df["ganho"], 1)
    xr = np.linspace(df["renda"].min(), df["renda"].max(), 50)
    ax.plot(xr, m * xr + b, color="black", lw=1.2, ls="--")
    ax.set_xlabel("Renda média do responsável (R$/mês, Censo 2022)")
    ax.set_ylabel("Ganho de IDEB 2007→2025 (anos iniciais)")
    ax.set_title(f"Ganho educacional e renda municipal (r = {r.statistic:.2f}; p = {r.pvalue:.2f})")
    ax.grid(alpha=0.25, ls=":")
    fig.tight_layout()
    p = OUT / "fig_scatter_ganho_renda.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_loocv(resultados: dict) -> Path:
    folds = resultados["loocv_microrregiao"]["folds"]
    nomes = [f["nome"] for f in folds]
    rt = [f["r_teste"] for f in folds]
    cores = ["#2ca02c" if v > 0 else "#d62728" for v in rt]
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.bar(nomes, rt, color=cores, alpha=0.85, edgecolor="white")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_ylabel("r de teste (município retido)")
    ax.set_title("Validação cruzada leave-one-out por município (r fora da amostra)")
    ax.tick_params(axis="x", rotation=30)
    ax.grid(alpha=0.25, axis="y", ls=":")
    fig.tight_layout()
    p = OUT / "fig_loocv_r_teste.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def principal() -> None:
    painel = carregar_painel()
    resultados = json.loads((RAIZ / "outputs" / "expanded" / "resultados_r426.json").read_text())
    gerados = {}
    for nome, fn in [
        ("fig_scatter_niveis_micro.png", fig_scatter_niveis),
        ("fig_serie_ideb_micro.png", fig_serie_ideb),
        ("fig_scatter_ganho_renda.png", fig_scatter_ganho_renda),
        ("fig_loocv_r_teste.png", fig_loocv),
    ]:
        p = fn(painel if "loocv" not in nome else resultados)
        gerados[nome] = {"arquivo": str(p.relative_to(RAIZ)), "bytes": p.stat().st_size}
        print("gerado:", p.name)
    (OUT / "figuras_manifest.json").write_text(
        json.dumps({"figuras": gerados}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    principal()
