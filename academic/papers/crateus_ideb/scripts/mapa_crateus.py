#!/usr/bin/env python3
"""Mapas coropléticos da microrregião Sertão de Cratéus (CE) — R426.

Dois mapas (proxies oficiais do IPCE, que é comercial e não auditável):
1. Renda média mensal do responsável (Censo Demográfico 2022, IBGE)
2. PIB per capita municipal (2021, IBGE)

Usa geopandas (venv: /tmp/crateus_venv/bin/python).
Gera PNG em outputs/mapas/.
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

warnings.filterwarnings("ignore")

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "data" / "processed"
OUT_MAPAS = RAIZ / "outputs" / "mapas"
OUT_MAPAS.mkdir(parents=True, exist_ok=True)
MALHA = Path("/tmp/crateus_data/malha_ce/CE_Municipios_2023.shp")

MUNICIPIOS_MICRO = [
    2301257, 2304103, 2305605, 2305654, 2308609,
    2309300, 2309409, 2311264, 2313203,
]
NOMES_MICRO = {
    2301257: "Ararendá", 2304103: "Crateús", 2305605: "Independência",
    2305654: "Ipaporanga", 2308609: "Monsenhor Tabosa", 2309300: "Nova Russas",
    2309409: "Novo Oriente", 2311264: "Quiterianópolis", 2313203: "Tamboril",
}


def plot_mapa(df: pd.DataFrame, col: str, titulo: str, nome_arquivo: str,
              fmt: str = "{:,.0f}") -> None:
    gdf = gpd.read_file(MALHA)
    gdf = gdf.to_crs(epsg=4326)
    gdf["CD_MUN"] = pd.to_numeric(gdf["CD_MUN"], errors="coerce")
    micro = gdf[gdf["CD_MUN"].isin(MUNICIPIOS_MICRO)].copy()
    micro = micro.merge(df, left_on="CD_MUN", right_on="cod_mun", how="left")
    micro = micro.sort_values("CD_MUN")

    fig, ax = plt.subplots(1, 1, figsize=(9, 8))
    micro.plot(column=col, cmap="YlGnBu", legend=True, ax=ax,
               legend_kwds={"label": col, "shrink": 0.7,
                            "fmt": fmt.replace("|", "")})
    micro.boundary.plot(ax=ax, color="black", linewidth=0.6)
    # rótulos com nome e valor
    for _, row in micro.iterrows():
        pt = row.geometry.centroid
        val = row[col]
        etiqueta = f"{row['NM_MUN']}\n{val:,.0f}" if pd.notna(val) else f"{row['NM_MUN']}\ns/d"
        ax.annotate(etiqueta, xy=(pt.x, pt.y), ha="center", va="center",
                    fontsize=8, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.85))
    ax.set_title(titulo, fontsize=13, fontweight="bold")
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(OUT_MAPAS / nome_arquivo, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("mapa salvo:", OUT_MAPAS / nome_arquivo)


def principal() -> None:
    renda = pd.read_json(PROC / "renda_ce.json", orient="records")
    pib = pd.read_json(PROC / "pib_ce.json", orient="records")
    pib_2021 = pib[pib["ano"] == 2021].copy()

    renda["renda_media_resp"] = pd.to_numeric(renda["renda_media_resp"], errors="coerce")
    renda["renda_mediana_resp"] = pd.to_numeric(renda["renda_mediana_resp"], errors="coerce")
    pib_2021["pib_per_capita"] = pd.to_numeric(pib_2021["pib_per_capita"], errors="coerce")

    micro_renda = renda[renda["cod_mun"].isin(MUNICIPIOS_MICRO)]
    micro_pib = pib_2021[pib_2021["cod_mun"].isin(MUNICIPIOS_MICRO)]

    plot_mapa(micro_renda, "renda_media_resp",
              "Sertão de Cratéus (CE) — renda média mensal do responsável (R$)\nCenso Demográfico 2022, IBGE",
              "mapa_renda_responsavel_censo2022.png")
    plot_mapa(micro_pib, "pib_per_capita",
              "Sertão de Cratéus (CE) — PIB per capita municipal (R$)\n2021, IBGE",
              "mapa_pib_per_capita_2021.png")

    resumo = {
        "mapas": [
            {"arquivo": "mapa_renda_responsavel_censo2022.png",
             "fonte": "IBGE Censo 2022, renda média do responsável (V06004)",
             "nota": "proxy oficial do IPCE (índice comercial, não auditável)"},
            {"arquivo": "mapa_pib_per_capita_2021.png",
             "fonte": "IBGE PIB dos Municípios 2021, PIB per capita",
             "nota": "proxy oficial do IPCE (índice comercial, não auditável)"},
        ]
    }
    (OUT_MAPAS / "mapas_manifest.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    principal()
