#!/usr/bin/env python3
"""Análise R427 — correlações entre indicadores municipais (Censo 2022) e
desempenho escolar (IDEB 2025 AI/AF; ganho AI 2007–2025) na microrregião do
Sertão de Cratéus, com ranking top/bottom e perfil de Crateús.

SPEC-935-R427-crateus-diagnostico.md
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import spearmanr, pearsonr

PAPER = Path(__file__).resolve().parent.parent
PROC = PAPER / "data" / "processed"
OUT = PAPER / "outputs" / "expanded"
FIG = PAPER / "outputs" / "figuras_r427"

MUNICIPIOS_MICRO = {
    2301257: "Ararendá", 2304103: "Crateús", 2305605: "Independência",
    2305654: "Ipaporanga", 2308609: "Monsenhor Tabosa", 2309300: "Nova Russas",
    2309409: "Novo Oriente", 2311264: "Quiterianópolis", 2313203: "Tamboril",
}
CRATEUS = 2304103
SEED = 42
B = 5000

DESFECHOS = {
    "ideb_2025_ai": "IDEB 2025 anos iniciais",
    "ideb_2025_af": "IDEB 2025 anos finais",
    "ganho_ideb_ai": "Ganho IDEB AI 2007–2025",
}

FAMILIAS = {
    "taxa_alfabetizacao_15_pct": "Capital humano",
    "agua_rede_geral_pct": "Saneamento",
    "esgoto_rede_pct": "Saneamento",
    "lixo_coletado_pct": "Saneamento",
    "banheiro_exclusivo_pct": "Saneamento",
    "internet_domicilios_pct": "Conectividade",
    "renda_responsavel": "Renda/desigualdade",
    "pib_per_capita": "Renda/desigualdade",
}

ETIQUETAS = {
    "taxa_alfabetizacao_15_pct": "Alfabetização 15+ (%)",
    "agua_rede_geral_pct": "Água rede geral (%)",
    "esgoto_rede_pct": "Esgoto rede (%)",
    "lixo_coletado_pct": "Lixo coletado (%)",
    "banheiro_exclusivo_pct": "Banheiro exclusivo (%)",
    "internet_domicilios_pct": "Internet domicílios (%)",
    "renda_responsavel": "Renda do responsável (R$)",
    "pib_per_capita": "PIB per capita (R$)",
}


def carregar_base() -> pd.DataFrame:
    sidra = pd.read_json(PROC / "indicadores_sidra.json", orient="records")
    r426 = json.loads((OUT / "resultados_r426.json").read_text())
    renda = pd.read_json(PROC / "renda_microrregiao.json", orient="records")

    # desfechos do R426 (detalhe do h3: todos os municípios BR × 2 etapas)
    linhas = []
    for d in r426["h3_estagnacao"]["detalhe"]:
        if int(float(d["cod_mun"])) in MUNICIPIOS_MICRO:
            linhas.append({
                "cod_mun": int(float(d["cod_mun"])),
                "etapa": d["etapa"],
                "ideb_fim": d["ideb_fim"],
                "ganho": d["ganho"],
            })
    h3 = pd.DataFrame(linhas)
    ai = h3[h3["etapa"] == "anos_iniciais"].set_index("cod_mun")
    af = h3[h3["etapa"] == "anos_finais"].set_index("cod_mun")

    base = sidra.set_index("cod_mun").copy()
    base["renda_responsavel"] = renda.set_index("cod_mun")["renda_media_resp"].astype(float)
    base["pib_per_capita"] = _pib_per_capita()
    base["ideb_2025_ai"] = ai["ideb_fim"].astype(float)
    base["ideb_2025_af"] = af["ideb_fim"].astype(float)
    base["ganho_ideb_ai"] = ai["ganho"].astype(float)
    base["nome"] = [MUNICIPIOS_MICRO[i] for i in base.index]
    return base


def _pib_per_capita() -> pd.Series:
    """PIB per capita 2021 (R$ correntes) — arquivo do R426."""
    pib = json.loads((PROC / "pib_microrregiao.json").read_text())
    s = {int(x["cod_mun"]): float(x["pib_per_capita"]) for x in pib if x["ano"] == 2021}
    return pd.Series(s)


def bootstrap_corr(x: np.ndarray, y: np.ndarray, seed: int = SEED, b: int = B):
    """Bootstrap não paramétrico (n=9) — IC95 percentil e estabilidade de sinal."""
    rng = np.random.default_rng(seed)
    n = len(x)
    vals_p = []
    vals_s = []
    for _ in range(b):
        idx = rng.integers(0, n, n)
        xx, yy = x[idx], y[idx]
        if np.std(xx) == 0 or np.std(yy) == 0:
            continue
        r_p = pearsonr(xx, yy)[0]
        r_s = spearmanr(xx, yy)[0]
        vals_p.append(r_p)
        vals_s.append(r_s)
    vals_p = np.array(vals_p)
    vals_s = np.array(vals_s)
    return {
        "pearson": float(pearsonr(x, y)[0]),
        "spearman": float(spearmanr(x, y)[0]),
        "pearson_ic95": [float(np.percentile(vals_p, 2.5)), float(np.percentile(vals_p, 97.5))],
        "spearman_ic95": [float(np.percentile(vals_s, 2.5)), float(np.percentile(vals_s, 97.5))],
        "sinal_estavel_pct": float(np.mean(np.sign(vals_p) == np.sign(pearsonr(x, y)[0])) * 100),
    }


def main() -> int:
    base = carregar_base()
    indicadores = list(ETIQUETAS.keys())

    resultados = {}
    ranking_p = []
    ranking_s = []

    for ind in indicadores:
        for desf, _rotulo in DESFECHOS.items():
            x = base[ind].to_numpy(dtype=float)
            y = base[desf].to_numpy(dtype=float)
            if np.any(np.isnan(x)) or np.any(np.isnan(y)):
                continue
            bc = bootstrap_corr(x, y)
            key = f"{ind}|{desf}"
            resultados[key] = {
                "indicador": ind,
                "desfecho": desf,
                "familia": FAMILIAS.get(ind, "Outros"),
                "n": len(x),
                **bc,
            }
            ranking_p.append({
                "indicador": ind, "desfecho": desf,
                "familia": FAMILIAS.get(ind, "Outros"),
                "r": bc["pearson"], "r_abs": abs(bc["pearson"]),
                "ic95": bc["pearson_ic95"], "sinal_estavel_pct": bc["sinal_estavel_pct"],
            })
            ranking_s.append({
                "indicador": ind, "desfecho": desf,
                "rho": bc["spearman"], "rho_abs": abs(bc["spearman"]),
                "ic95": bc["spearman_ic95"], "sinal_estavel_pct": bc["sinal_estavel_pct"],
            })

    ranking_p = sorted(ranking_p, key=lambda r: -r["r_abs"])
    ranking_s = sorted(ranking_s, key=lambda r: -r["rho_abs"])

    # ranking agregado por indicador (média dos |r| entre desfechos)
    agregado = {}
    for ind in indicadores:
        chaves = [k for k in resultados if k.startswith(ind + "|")]
        if not chaves:
            continue
        med = float(np.mean([resultados[k]["pearson"] for k in chaves]))
        med_abs = float(np.mean([abs(resultados[k]["pearson"]) for k in chaves]))
        rho_med = float(np.mean([resultados[k]["spearman"] for k in chaves]))
        agregado[ind] = {
            "indicador": ind, "familia": FAMILIAS.get(ind, "Outros"),
            "r_medio": med, "|r|_medio": med_abs, "rho_medio": rho_med,
            "sinal_estavel_medio_pct": float(np.mean([resultados[k]["sinal_estavel_pct"] for k in chaves])),
        }
    ranking_agregado = sorted(agregado.values(), key=lambda r: -r["|r|_medio"])

    # perfil de Crateús e matriz prioridade
    perfil = {}
    for ind in indicadores:
        serie = base[ind].astype(float)
        valor_crateus = float(serie.loc[CRATEUS])
        mediana = float(serie.median())
        melhor = float(serie.max())
        pior = float(serie.min())
        acima_mediana = valor_crateus > mediana
        ag = agregado.get(ind, {})
        # gap até o melhor município da micro (em % do valor do melhor)
        gap_melhor = max(0.0, float((melhor - valor_crateus) / melhor * 100)) if melhor != 0 else 0.0
        perfil[ind] = {
            "indicador": ind,
            "valor_crateus": valor_crateus,
            "mediana_micro": mediana,
            "melhor_micro": melhor,
            "pior_micro": pior,
            "acima_mediana": acima_mediana,
            "posicao_relativa": float((valor_crateus - pior) / (melhor - pior)) if melhor != pior else 1.0,
            "gap_melhor_pct": gap_melhor,
            "|r|_medio": ag.get("|r|_medio", 0.0),
        }

    # matriz prioridade: indicadores de alta correlação em que Crateús tem gap até o melhor
    matriz_prioridade = sorted(
        [p for p in perfil.values() if p["gap_melhor_pct"] > 5.0 and p["|r|_medio"] > 0.2],
        key=lambda p: -(p["|r|_medio"] * p["gap_melhor_pct"]),
    )
    alavancas = [p for p in perfil.values() if p["|r|_medio"] >= 0.45]
    nao_alavancas = [p for p in perfil.values() if p["|r|_medio"] < 0.2]

    resultados_json = {
        "ciclo": "R427",
        "n": len(base),
        "municipios": MUNICIPIOS_MICRO,
        "desfechos": DESFECHOS,
        "correlacoes": resultados,
        "ranking_pearson": ranking_p,
        "ranking_spearman": ranking_s,
        "ranking_agregado": ranking_agregado,
        "perfil_crateus": perfil,
        "matriz_prioridade": matriz_prioridade,
        "alavancas": alavancas,
        "nao_alavancas": nao_alavancas,
        "metadados": {
            "fonte": "IBGE Censo 2022 (SIDRA) + INEP IDEB + IBGE PIB",
            "bootstrap": {"seed": SEED, "reamostragens": B, "ic": "percentil 2.5/97.5"},
            "anti_overclaim": "n=9; associação != causalidade; IC95 amplos; sinal estável >= 90%",
            "limite_financas": "FINBRA/SICONFI e indicadores educacionais escolares indisponíveis via API no momento da coleta",
        },
    }
    (OUT / "resultados_r427.json").write_text(
        json.dumps(resultados_json, ensure_ascii=False, indent=2), encoding="utf-8")

    provenance = {
        "ciclo": "R427",
        "entradas": {
            "indicadores_sidra": str(PROC / "indicadores_sidra.json"),
            "resultados_r426": str(OUT / "resultados_r426.json"),
            "renda_microrregiao": str(PROC / "renda_microrregiao.json"),
        },
        "sha256_script": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "bootstrap": {"seed": SEED, "b": B},
    }
    (OUT / "provenance_r427.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8")

    _graficos(base, resultados)
    print("R427 OK → resultados_r427.json + figuras_r427/")
    return 0


def _graficos(base: pd.DataFrame, resultados: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIG.mkdir(parents=True, exist_ok=True)

    # 1) heatmap de correlações (indicador × desfecho)
    inds = list(ETIQUETAS.keys())
    desfs = list(DESFECHOS.keys())
    M = np.full((len(inds), len(desfs)), np.nan)
    for i, ind in enumerate(inds):
        for j, desf in enumerate(desfs):
            key = f"{ind}|{desf}"
            if key in resultados:
                M[i, j] = resultados[key]["pearson"]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    im = ax.imshow(M, cmap="RdYlBu", vmin=-1, vmax=1)
    ax.set_xticks(range(len(desfs)), [DESFECHOS[d] for d in desfs], rotation=20, ha="right")
    ax.set_yticks(range(len(inds)), [ETIQUETAS[i] for i in inds])
    for i in range(len(inds)):
        for j in range(len(desfs)):
            if not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=8)
    ax.set_title("Correlação Pearson: indicadores × desempenho (n=9) — Sertão de Cratéus")
    fig.colorbar(im, label="r de Pearson")
    fig.tight_layout()
    fig.savefig(FIG / "heatmap_correlacoes.png", dpi=150)
    plt.close(fig)

    # 2) scatter top-3 indicadores por |r| médio × IDEB AI
    top = sorted(
        [inds.index(i) for i in inds if not np.isnan(M[inds.index(i), 0])],
        key=lambda i: -abs(M[i, 0]),
    )[:3]
    for rank, pos in enumerate(top, start=1):
        ind = inds[pos]
        fig, ax = plt.subplots(figsize=(6, 4.5))
        x = base[ind].astype(float)
        y = base["ideb_2025_ai"].astype(float)
        nomes = base["nome"]
        cores = ["#d62728" if m == CRATEUS else "#1f77b4" for m in base.index]
        ax.scatter(x, y, c=cores, s=60)
        for xi, yi, nome in zip(x, y, nomes):
            ax.annotate(nome, (xi, yi), fontsize=7, xytext=(4, 4), textcoords="offset points")
        r, p = pearsonr(x, y)
        ax.set_xlabel(ETIQUETAS[ind])
        ax.set_ylabel("IDEB 2025 anos iniciais")
        ax.set_title(f"Top {rank}: {ETIQUETAS[ind]} (r={r:.2f}) — Crateús em vermelho")
        fig.tight_layout()
        fig.savefig(FIG / f"scatter_top{rank}_{ind}.png", dpi=150)
        plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
