#!/usr/bin/env python3
"""Estatística da hipótese, amostragem e confiabilidade (SPEC-935-R419).

Complementa a análise expandida (R412) com três blocos formais:

1. TESTE DA HIPÓTESE CENTRAL
   Hipótese do artigo: a associação matrícula terciária × renda é forte entre
   países (níveis) e fraca dentro do país (primeiras diferenças). Teste
   formal da diferença Δ = ρ_níveis − ρ_primeiras_diferenças via bootstrap
   por país (re-amostragem de países com reposição, 500 replicações, seed
   42), com IC95% percentil e p-valor (proporção de replicações com Δ ≤ 0).

2. AMOSTRAGEM
   População: países oficiais do WDI (excluídos agregados e territórios sem
   ISO3). Elegibilidade: ≥ MIN_OBS_PAIS observações não nulas de matrícula
   terciária E de PIB per capita. Documenta exclusões por motivo (matrícula,
   PIB, ambos) e por região, e a cobertura temporal por década.

3. CONFIABILIDADE
   IC95% bootstrap por país dos ρ centrais (níveis e primeiras diferenças) e
   robustez de semente: ρ recalculados com sementes alternativas (7, 2024,
   123) para atestar estabilidade dos resultados.

Gera outputs/expanded/provenance_r419.json + tabela9_hipotese.csv +
tabela10_amostragem.csv + tabela11_confiabilidade.csv, com proveniência
fechada (sha256 dos JSONs crus de entrada).

Execução: python3 scripts/analyze_hipotese_confiabilidade.py
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

AUDIT = Path(__file__).resolve().parent.parent
RAW = AUDIT / "data" / "raw_expandido"
OUT = AUDIT / "outputs" / "expanded"
SCRIPT_DIR = AUDIT / "scripts"

sys.path.insert(0, str(SCRIPT_DIR))

from analyze_expanded import (  # noqa: E402
    MIN_OBS_PAIS,
    build_panel,
    load_countries,
    load_series,
    rho_diferencas,
    rho_niveis,
)

N_BOOT = 500
SEED_PRINCIPAL = 42
SEMENTES_ROBUSTEZ = [7, 2024, 123]
ALPHA = 0.05

INDICADORES_NECESSARIOS = [
    "NY.GDP.PCAP.KD",
    "SE.TER.ENRR",
]


def sha256_arquivo(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def carregar_meta_paises() -> pd.DataFrame:
    """DataFrame com iso3, região e nível de renda de cada país oficial."""
    data = json.loads((RAW / "wdi_countries_meta.json").read_text(encoding="utf-8"))[1]
    linhas = []
    for c in data:
        if c.get("region", {}).get("id") == "NA":
            continue
        code = c.get("id", "")
        if not code or len(code) != 3:
            continue
        linhas.append({
            "iso3": code,
            "regiao": (c.get("region", {}).get("value") or "").strip(),
            "renda": (c.get("incomeLevel", {}).get("value") or "").strip(),
        })
    return pd.DataFrame(linhas)


def rho_niveis_boot(df: pd.DataFrame, paises: np.ndarray, rng: np.random.RandomState) -> float:
    """ρ em níveis sobre amostra bootstrap de países (com reposição)."""
    sel = df[df["iso3"].isin(paises)]
    return rho_niveis(sel)


def rho_dif_boot(df: pd.DataFrame, paises: np.ndarray, rng: np.random.RandomState) -> float:
    """ρ em primeiras diferenças sobre amostra bootstrap de países."""
    sel = df[df["iso3"].isin(paises)]
    return rho_diferencas(sel)


def bootstrap_por_pais(df: pd.DataFrame, seed: int) -> dict:
    """Bootstrap por país: ρ_níveis, ρ_1ªdif e Δ para cada replicação."""
    rng = np.random.RandomState(seed)
    paises = df["iso3"].unique()
    n_paises = len(paises)
    replicacoes = []
    for _ in range(N_BOOT):
        amostra = rng.choice(paises, size=n_paises, replace=True)
        rn = rho_niveis_boot(df, amostra, rng)
        rd = rho_dif_boot(df, amostra, rng)
        if np.isnan(rn) or np.isnan(rd):
            continue
        replicacoes.append({"rho_niveis": rn, "rho_diferencas": rd,
                            "delta": rn - rd})
    arr = np.array([[r["rho_niveis"], r["rho_diferencas"], r["delta"]]
                    for r in replicacoes])
    if len(arr) < 100:
        raise RuntimeError(f"bootstrap gerou poucas replicações válidas: {len(arr)}")
    delta_obs = rho_niveis(df) - rho_diferencas(df)
    p_valor = float(np.mean(arr[:, 2] <= 0.0))
    ic_inf, ic_sup = np.percentile(arr[:, 2], [100 * ALPHA / 2,
                                               100 * (1 - ALPHA / 2)])
    return {
        "n_boot": N_BOOT,
        "n_replicacoes_validas": int(len(arr)),
        "seed": seed,
        "rho_niveis_obs": float(rho_niveis(df)),
        "rho_diferencas_obs": float(rho_diferencas(df)),
        "delta_obs": float(delta_obs),
        "delta_ic95_inf": float(ic_inf),
        "delta_ic95_sup": float(ic_sup),
        "p_valor_delta_positivo": p_valor,
        "p_valor_delta_interpretacao": (
            "proporção de replicações bootstrap com Δ ≤ 0; p < 0,05 indica "
            "que a diferença ρ_níveis − ρ_1ªdif é estatisticamente positiva"
        ),
        "rho_niveis_ic95_inf": float(np.percentile(arr[:, 0], 2.5)),
        "rho_niveis_ic95_sup": float(np.percentile(arr[:, 0], 97.5)),
        "rho_diferencas_ic95_inf": float(np.percentile(arr[:, 1], 2.5)),
        "rho_diferencas_ic95_sup": float(np.percentile(arr[:, 1], 97.5)),
    }


def amostragem(df: pd.DataFrame) -> dict:
    """Descrição formal do processo de amostragem."""
    meta = carregar_meta_paises()
    paises_oficiais = set(load_countries())

    # contagem de observações não nulas por país a partir dos DADOS BRUTOS
    # (o painel já vem filtrado por elegibilidade; os brutos permitem
    # classificar o motivo de exclusão de cada país)
    mat_bruta = load_series("SE.TER.ENRR")
    pib_bruto = load_series("NY.GDP.PCAP.KD")
    n_mat = mat_bruta.groupby("iso3")["SE_TER_ENRR"].count()
    n_pib = pib_bruto.groupby("iso3")["NY_GDP_PCAP_KD"].count()

    def motivo(iso: str) -> str:
        nm = int(n_mat.get(iso, 0))
        np_ = int(n_pib.get(iso, 0))
        if nm == 0 and np_ == 0:
            return "sem_matricula_e_sem_pib"
        if nm == 0:
            return "sem_matricula"
        if np_ == 0:
            return "sem_pib"
        if nm < MIN_OBS_PAIS or np_ < MIN_OBS_PAIS:
            return "menos_de_20_obs"
        return "elegivel"

    classificacao = {iso: motivo(iso) for iso in paises_oficiais}
    contagem_motivo = {}
    for iso, m in classificacao.items():
        contagem_motivo[m] = contagem_motivo.get(m, 0) + 1

    elegiveis = {iso for iso, m in classificacao.items() if m == "elegivel"}
    n_elegiveis = len(elegiveis)
    n_amostra = int(df["iso3"].nunique())

    # por região
    pop = meta[meta["iso3"].isin(paises_oficiais)]
    n_pop = int(pop["iso3"].nunique())
    regiao_pop = pop["regiao"].value_counts().to_dict()
    regiao_amostra = (df[["iso3"]].drop_duplicates()
                      .merge(pop[["iso3", "regiao"]], on="iso3", how="left")
                      ["regiao"].value_counts().to_dict())

    # cobertura temporal por década
    decadas = {}
    for dec in range(1960, 2030, 10):
        sub = df[(df["year"] >= dec) & (df["year"] < dec + 10)]
        decadas[f"{dec}s"] = {
            "n_pais_ano": int(len(sub)),
            "n_paises": int(sub["iso3"].nunique()),
        }

    return {
        "populacao": {
            "n_paises_oficiais_wdi": n_pop,
            "definicao": "países oficiais do WDI com região definida (excluídos agregados e territórios sem ISO3)",
        },
        "criterio_elegibilidade": (
            f">= {MIN_OBS_PAIS} observações não nulas de matrícula terciária "
            "E de PIB per capita (sem imputação)"
        ),
        "elegiveis": n_elegiveis,
        "amostra_final": n_amostra,
        "exclusoes": {
            "total_paises_excluidos": n_pop - n_amostra,
            "por_motivo": contagem_motivo,
        },
        "por_regiao": {
            "populacao": regiao_pop,
            "amostra": regiao_amostra,
        },
        "cobertura_decadas": decadas,
        "nota": (
            "A seleção é condicionada à disponibilidade de dados, não aleatória; "
            "a generalização vale para a amostra observada."
        ),
    }


def robustez_seed(df: pd.DataFrame) -> list[dict]:
    """ρ centrais com sementes alternativas (estabilidade do bootstrap)."""
    resultados = []
    for seed in [SEED_PRINCIPAL] + SEMENTES_ROBUSTEZ:
        b = bootstrap_por_pais(df, seed=seed)
        resultados.append({
            "seed": seed,
            "delta_obs": b["delta_obs"],
            "delta_ic95_inf": b["delta_ic95_inf"],
            "delta_ic95_sup": b["delta_ic95_sup"],
            "p_valor_delta_positivo": b["p_valor_delta_positivo"],
            "rho_niveis_obs": b["rho_niveis_obs"],
            "rho_diferencas_obs": b["rho_diferencas_obs"],
        })
    return resultados


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    hashes = {ind: sha256_arquivo(RAW / f"wdi_{ind}.json")
              for ind in INDICADORES_NECESSARIOS}
    hashes["manifest_expandido.json"] = sha256_arquivo(RAW / "manifest_expandido.json")
    sha_meta = sha256_arquivo(RAW / "wdi_countries_meta.json")

    df = build_panel()

    teste = bootstrap_por_pais(df, seed=SEED_PRINCIPAL)
    amostra = amostragem(df)
    seeds = robustez_seed(df)

    prov = {
        "painel_fonte": "panel_wdi_expandido_1960_2023.csv (R412)",
        "sha256_raw": hashes,
        "sha256_countries_meta": sha_meta,
        "proveniencia_fechada": True,
        "n_paises": int(df["iso3"].nunique()),
        "n_pais_ano": int(len(df)),
        "hipotese": {
            "enunciado": (
                "A associação matrícula terciária × renda é forte entre países "
                "(níveis) e fraca dentro do país (primeiras diferenças)."
            ),
            "h0": "ρ_níveis − ρ_1ªdif ≤ 0",
            "h1": "ρ_níveis − ρ_1ªdif > 0",
            "metodo": (
                "bootstrap por país (re-amostragem de países com reposição, "
                f"{N_BOOT} replicações, seed {SEED_PRINCIPAL}); IC95% percentil"
            ),
            **teste,
        },
        "amostragem": amostra,
        "confiabilidade": {
            "metodo": (
                "IC95% bootstrap por país (percentil 2,5%–97,5%) e robustez "
                "de semente"
            ),
            "sementes": seeds,
        },
    }

    (OUT / "provenance_r419.json").write_text(
        json.dumps(prov, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # --- tabela 9: hipótese (vírgula decimal, padrão pt-BR do artigo) ---
    def f3(x: float) -> str:
        return f"{x:.3f}".replace(".", ",")

    with open(OUT / "tabela9_hipotese.csv", "w", encoding="utf-8") as f:
        f.write("estatistica;valor;ic95_inf;ic95_sup\n")
        f.write(f"rho_niveis;{f3(teste['rho_niveis_obs'])};{f3(teste['rho_niveis_ic95_inf'])};{f3(teste['rho_niveis_ic95_sup'])}\n")
        f.write(f"rho_primeiras_diferencas;{f3(teste['rho_diferencas_obs'])};{f3(teste['rho_diferencas_ic95_inf'])};{f3(teste['rho_diferencas_ic95_sup'])}\n")
        f.write(f"delta_rho;{f3(teste['delta_obs'])};{f3(teste['delta_ic95_inf'])};{f3(teste['delta_ic95_sup'])}\n")
        f.write(f"p_valor_delta_positivo;{f3(teste['p_valor_delta_positivo'])};;\n")

    # --- tabela 10: amostragem ---
    with open(OUT / "tabela10_amostragem.csv", "w", encoding="utf-8") as f:
        f.write("regiao;populacao;amostra\n")
        for reg in sorted(set(amostra["por_regiao"]["populacao"]) | set(amostra["por_regiao"]["amostra"])):
            f.write(f"{reg};{amostra['por_regiao']['populacao'].get(reg, 0)};{amostra['por_regiao']['amostra'].get(reg, 0)}\n")
        f.write(f"TOTAL;{sum(amostra['por_regiao']['populacao'].values())};{sum(amostra['por_regiao']['amostra'].values())}\n")

    # --- tabela 11: confiabilidade ---
    with open(OUT / "tabela11_confiabilidade.csv", "w", encoding="utf-8") as f:
        f.write("seed;delta_obs;ic95_inf;ic95_sup;p_valor\n")
        for s in seeds:
            f.write(f"{s['seed']};{f3(s['delta_obs'])};{f3(s['delta_ic95_inf'])};{f3(s['delta_ic95_sup'])};{f3(s['p_valor_delta_positivo'])}\n")

    print(json.dumps({
        "delta_obs": teste["delta_obs"],
        "delta_ic95": [teste["delta_ic95_inf"], teste["delta_ic95_sup"]],
        "p_valor": teste["p_valor_delta_positivo"],
        "rho_niveis_ic95": [teste["rho_niveis_ic95_inf"], teste["rho_niveis_ic95_sup"]],
        "rho_dif_ic95": [teste["rho_diferencas_ic95_inf"], teste["rho_diferencas_ic95_sup"]],
        "amostragem": {
            "populacao": amostra["populacao"]["n_paises_oficiais_wdi"],
            "elegiveis": amostra["elegiveis"],
            "amostra": amostra["amostra_final"],
        },
        "seeds": [s["delta_obs"] for s in seeds],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
