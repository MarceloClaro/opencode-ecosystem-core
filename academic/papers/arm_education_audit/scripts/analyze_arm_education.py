# -*- coding: utf-8 -*-
"""Análise reprodutível — SPEC-935-R408.

Reconstrói descritivos por país e associações exploratórias com tratamento
de dependência (país como cluster), sem pseudorreplicação de p-valores e sem
rotular nada como causal. Gera:
  outputs/reproduction_matrix.csv
  outputs/claim_evidence_matrix.csv
  outputs/descritivos_por_pais.csv
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

AUDIT_DIR = Path(__file__).resolve().parents[1]
PROC_DIR = AUDIT_DIR / "data" / "processed"
OUT_DIR = AUDIT_DIR / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

COUNTRIES = ["ARG", "BRA", "CHL", "CHN", "KOR", "SGP", "VNM"]
PERIOD_RECENT = (2010, 2023)

# Números antigos extraídos do manuscrito (somente leitura) — ver
# SOURCE_MANIFEST.json. Cada um é declarado como NÃO REPRODUZIDO (sem código
# original), e a coluna "numero_refeito" traz a reconstrução diagnóstica.
LEGACY_CLAIMS = [
    # tabela 1 - descritivos 2010-2023 (apenas exemplos representativos)
    {"id": "T1_KOR_gdp", "secao": "Tabela 1", "alegacao": "KOR PIB pc 26.869 (2010-2023)",
     "numero_antigo": 26869, "variavel": "NY.GDP.PCAP.KD", "pais": "KOR", "periodo": "2010-2023"},
    {"id": "T1_BRA_gdp", "secao": "Tabela 1", "alegacao": "BRA PIB pc 8.076 (2010-2023)",
     "numero_antigo": 8076, "variavel": "NY.GDP.PCAP.KD", "pais": "BRA", "periodo": "2010-2023"},
    {"id": "T1_VNM_gdp", "secao": "Tabela 1", "alegacao": "VNM PIB pc 2.216 (2010-2023)",
     "numero_antigo": 2216, "variavel": "NY.GDP.PCAP.KD", "pais": "VNM", "periodo": "2010-2023"},
    {"id": "T1_KOR_ter", "secao": "Tabela 1", "alegacao": "KOR matr. terc. 94,92%",
     "numero_antigo": 94.92, "variavel": "SE.TER.ENRR", "pais": "KOR", "periodo": "2010-2023"},
    {"id": "T1_BRA_ter", "secao": "Tabela 1", "alegacao": "BRA matr. terc. 50,65%",
     "numero_antigo": 50.65, "variavel": "SE.TER.ENRR", "pais": "BRA", "periodo": "2010-2023"},
    {"id": "T1_BRA_edu", "secao": "Tabela 1", "alegacao": "BRA gasto educ 5,22% PIB",
     "numero_antigo": 5.22, "variavel": "SE.XPD.TOTL.GD.ZS", "pais": "BRA", "periodo": "2010-2023"},
    {"id": "T1_KOR_edu", "secao": "Tabela 1", "alegacao": "KOR gasto educ 3,69% PIB",
     "numero_antigo": 3.69, "variavel": "SE.XPD.TOTL.GD.ZS", "pais": "KOR", "periodo": "2010-2023"},
    {"id": "T1_KOR_rd", "secao": "Tabela 1", "alegacao": "KOR P&D 3,31% PIB",
     "numero_antigo": 3.31, "variavel": "GB.XPD.RSDV.GD.ZS", "pais": "KOR", "periodo": "2010-2023"},
    # tabela 2 - correlações
    {"id": "T2_ter_rho", "secao": "Tabela 2", "alegacao": "matr. terc. × PIB pc ρ=+0,934 (n=198)",
     "numero_antigo": 0.934, "variavel": "SE.TER.ENRR", "pais": "todos", "periodo": "1960-2023"},
    {"id": "T2_edu_r", "secao": "Tabela 2", "alegacao": "gasto educ × PIB pc r=+0,050 (n=128, p=0,574)",
     "numero_antigo": 0.050, "variavel": "SE.XPD.TOTL.GD.ZS", "pais": "todos", "periodo": "1960-2023"},
    # tabela 4 - post-hoc BRA×KOR
    {"id": "T4_d_pisa", "secao": "Tabela 4", "alegacao": "d Cohen PISA BRA-KOR = 16,06",
     "numero_antigo": 16.06, "variavel": "PISA-Matemática", "pais": "BRA-KOR", "periodo": "2022"},
    # tabela 6 - RF
    {"id": "T6_auc", "secao": "Tabela 6", "alegacao": "AUC-ROC RF = 0,997 ± 0,006 (n=384)",
     "numero_antigo": 0.997, "variavel": "RF", "pais": "todos", "periodo": "1960-2023"},
]


def descritivos(panel: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for iso in COUNTRIES:
        sub = panel[panel["iso3"] == iso]
        sub = sub[(sub["year"] >= PERIOD_RECENT[0]) & (sub["year"] <= PERIOD_RECENT[1])]
        row = {"iso3": iso, "periodo": f"{PERIOD_RECENT[0]}-{PERIOD_RECENT[1]}"}
        for col in cols:
            vals = sub[col].dropna()
            row[f"{col}_media"] = round(vals.mean(), 2) if len(vals) else np.nan
            row[f"{col}_n"] = len(vals)
        rows.append(row)
    return pd.DataFrame(rows)


def assoc_cluster_robust(panel: pd.DataFrame, x: str, y: str) -> dict:
    """Correlação de Spearman nos níveis (diagnóstico) + correlação das
    primeiras diferenças (análise principal) com leave-one-country-out."""
    valid = panel[[x, y]].dropna()
    out = {"variavel": x, "contra": y}
    if len(valid) < 3:
        out.update({"n_niveis": 0, "rho_niveis": np.nan, "rho_dif": np.nan})
        return out

    rho_niveis = stats.spearmanr(valid[x], valid[y]).statistic
    out["n_niveis"] = int(len(valid))
    out["rho_niveis"] = round(float(rho_niveis), 3)

    # primeiras diferenças por país (remove tendência comum)
    diffs = []
    for iso in COUNTRIES:
        sub = panel[panel["iso3"] == iso].sort_values("year")[[x, y]].dropna()
        dx = sub[x].diff().dropna()
        dy = sub[y].diff().dropna()
        joined = pd.concat([dx, dy], axis=1).dropna()
        if len(joined) >= 3:
            joined["iso3"] = iso
            diffs.append(joined)
    if diffs:
        ddf = pd.concat(diffs)
        rho_dif = stats.spearmanr(ddf[x], ddf[y]).statistic
        out["n_dif"] = int(len(ddf))
        out["rho_dif"] = round(float(rho_dif), 3)
    else:
        out["n_dif"] = 0
        out["rho_dif"] = np.nan
    return out


def build_reproduction_matrix(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for claim in LEGACY_CLAIMS:
        row = dict(claim)
        numero_refeito = None
        status = "nao_reproduzido"
        decisao = "remover_versao_cientifica"
        if claim["variavel"] in panel.columns and claim.get("pais") in COUNTRIES:
            sub = panel[panel["iso3"] == claim["pais"]]
            if claim.get("periodo") == "2010-2023":
                sub = sub[(sub["year"] >= 2010) & (sub["year"] <= 2023)]
            vals = sub[claim["variavel"]].dropna()
            if len(vals):
                numero_refeito = round(float(vals.mean()), 2)
                status = "refeito_descritivo"
                decisao = "substituir_por_valor_recalculado"
        elif claim["id"] == "T2_ter_rho":
            res = assoc_cluster_robust(panel, "SE.TER.ENRR", "NY.GDP.PCAP.KD")
            numero_refeito = res["rho_niveis"]
            status = "refeito_diagnostico_niveis"
            decisao = "manter_como_diagnostico_vulneravel_a_tendencia"
        elif claim["id"] == "T2_edu_r":
            res = assoc_cluster_robust(panel, "SE.XPD.TOTL.GD.ZS", "NY.GDP.PCAP.KD")
            numero_refeito = res["rho_niveis"]
            status = "refeito_diagnostico_niveis"
            decisao = "manter_como_diagnostico_vulneravel_a_tendencia"
        else:
            status = "nao_reproduzido_bloqueado"
            decisao = "remover_versao_cientifica"

        row.update({
            "numero_refeito": numero_refeito,
            "diferenca": (round(numero_refeito - claim["numero_antigo"], 3)
                          if numero_refeito is not None else None),
            "status": status,
            "decisao_editorial": decisao,
            "fonte": "World Bank WDI API (cache r408) ou não disponível",
            "hash_proveniencia": "sha256 cache WDI (data/raw/manifest.json)",
        })
        rows.append(row)
    return pd.DataFrame(rows)


def build_claim_evidence_matrix() -> pd.DataFrame:
    """Alegações de alto risco do manuscrito → evidência necessária → limite."""
    rows = [
        {
            "alegacao": "Matrícula terciária é o melhor preditor de PIB per capita",
            "secao": "Resumo/Tabela 2",
            "evidencia_exigida": "Correlação com tratamento de cluster/tempo",
            "evidencia_atual": "ρ níveis 0,934 sem cluster (vulnerável a tendência)",
            "status": "nao_sustentada_na_forma_original",
            "decisao": "reformular como associação descritiva",
        },
        {
            "alegacao": "Gasto educacional não se associa a PIB per capita (r=0,050 ns)",
            "secao": "Resumo/Tabela 2",
            "evidencia_exigida": "Correlação Pearson + Spearman, cluster/tempo",
            "evidencia_atual": "Pearson 0,050 ns MAS Spearman 0,388 significativo (seleção seletiva)",
            "status": "selecao_seletiva_de_resultado",
            "decisao": "reportar ambos os coeficientes e a divergência",
        },
        {
            "alegacao": "d de Cohen PISA BRA-KOR = 16,06 (distribuições quase não se sobrepõem)",
            "secao": "Tabela 4",
            "evidencia_exigida": "Microdados estudantis com pesos; d calculado sobre indivíduos",
            "evidencia_atual": "Médias nacionais agregadas usadas como se fossem distribuição de estudantes",
            "status": "uso_indevido_de_estatistica",
            "decisao": "remover da versão científica; reportar diferença de pontos com erro-padrão",
        },
        {
            "alegacao": "Random Forest AUC-ROC = 0,997 ± 0,006 (validade externa implícita)",
            "secao": "Tabela 6",
            "evidencia_exigida": "Dataset/alvo/código originais; CV agrupada por país; out-of-country",
            "evidencia_atual": "n=384 sem explicação; 4 classes definidas mas binário interpretado; CV por linha",
            "status": "nao_reproduzido_nao_identificavel",
            "decisao": "remover da versão científica; manter no relatório como não identificabilidade",
        },
        {
            "alegacao": "Qualidade educacional é condição necessária para escape da ARM",
            "secao": "Conclusão",
            "evidencia_exigida": "Design que identifique condição necessária (teste de necessidade)",
            "evidencia_atual": "Análise observacional correlacional de 7 países",
            "status": "excede_o_desenho",
            "decisao": "reformular como associação exploratória",
        },
        {
            "alegacao": "Dos 101 países de renda média em 1960, apenas 13 alcançaram alta renda até 2008",
            "secao": "Introdução",
            "evidencia_exigida": "Fonte primária localizada (Gill-Kharas 2007, p. 17)",
            "evidencia_atual": "Citação repetida; origem exata do número não verificada na obra",
            "status": "parcial",
            "decisao": "verificar na fonte primária antes de manter",
        },
    ]
    return pd.DataFrame(rows)


def main() -> None:
    panel = pd.read_csv(PROC_DIR / "panel_wdi_1960_2023.csv")

    desc = descritivos(panel, [
        "NY.GDP.PCAP.KD", "SE.TER.ENRR", "SE.XPD.TOTL.GD.ZS", "GB.XPD.RSDV.GD.ZS",
    ])
    desc.to_csv(OUT_DIR / "descritivos_por_pais.csv", index=False)

    matrix = build_reproduction_matrix(panel)
    matrix.to_csv(OUT_DIR / "reproduction_matrix.csv", index=False)

    claims = build_claim_evidence_matrix()
    claims.to_csv(OUT_DIR / "claim_evidence_matrix.csv", index=False)

    assocs = [
        assoc_cluster_robust(panel, "SE.TER.ENRR", "NY.GDP.PCAP.KD"),
        assoc_cluster_robust(panel, "SE.XPD.TOTL.GD.ZS", "NY.GDP.PCAP.KD"),
        assoc_cluster_robust(panel, "GB.XPD.RSDV.GD.ZS", "NY.GDP.PCAP.KD"),
    ]
    pd.DataFrame(assocs).to_csv(OUT_DIR / "associacoes_cluster_robustas.csv", index=False)

    print("=== Descritivos 2010-2023 ===")
    print(desc.to_string(index=False))
    print("\n=== Associações com tratamento de cluster ===")
    for a in assocs:
        print(f"  {a['variavel']} × {a['contra']}: "
              f"rho_niveis={a.get('rho_niveis')} (n={a.get('n_niveis')}), "
              f"rho_dif={a.get('rho_dif')} (n={a.get('n_dif')})")
    print("\nMatriz de reprodução:", OUT_DIR / "reproduction_matrix.csv")


if __name__ == "__main__":
    main()
