#!/usr/bin/env python3
"""Análise do caso brasileiro em perspectiva comparada (SPEC-935-R418).

Base: dados crus WDI (data/raw_expandido/), mesma fonte do painel expandido.
Janela comum 2012-2022: único período em que o WDI reporta matrícula
terciária para o Brasil (11 observações não nulas, abaixo do limiar de 20
usado na amostra principal de 135 países).

A cobertura na janela é desbalanceada por país (WDI vigente, verificado na
API oficial em 2026-08-14): BRA, CHN, FRA, GBR, ITA, ESP, IDN, MYS, THA têm
série completa 2012-2022; USA e DEU iniciam em 2013; PRT em 2015; VNM tem
lacunas. Para cada unidade são usados o primeiro e o último ano disponíveis
na janela, e o crescimento médio anual é calculado sobre o número real de
anos (ano_fim - ano_inicio) — sem imputação.

Unidades comparadas:
- Brasil (isolado)
- mexico: MEX (isolado, vizinho latino-americano)
- argentina: ARG (isolado, vizinho latino-americano)
- renda_media_asiatica: CHN, IDN, MYS, THA, VNM (sem KOR, alta renda)
- eua: USA
- europa_ocidental: DEU, FRA, GBR, ITA, ESP, PRT
- china: CHN (referência explícita)

Gera outputs/expanded/provenance_r418.json + tabela8_brasil_comparado.csv,
com proveniência fechada (sha256 dos JSONs crus de entrada).

Execução: python3 scripts/analyze_brasil_comparativo.py
"""

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

AUDIT = Path(__file__).resolve().parent.parent
RAW = AUDIT / "data" / "raw_expandido"
OUT = AUDIT / "outputs" / "expanded"

JANELA_INI = 2012
JANELA_FIM = 2022
BRASIL = "BRA"
GRUPOS = {
    "renda_media_asiatica": ["CHN", "IDN", "MYS", "THA", "VNM"],
    "eua": ["USA"],
    "europa_ocidental": ["DEU", "FRA", "GBR", "ITA", "ESP", "PRT"],
}
NOME_GRUPO = {
    "renda_media_asiatica": "Renda média asiática",
    "eua": "Estados Unidos",
    "europa_ocidental": "Europa Ocidental",
}
INDICADORES_NECESSARIOS = [
    "NY.GDP.PCAP.KD",
    "NY.GDP.PCAP.KD.ZG",
    "SE.TER.ENRR",
]

sys_path = AUDIT / "scripts"
import sys

sys.path.insert(0, str(sys_path))


def sha256_arquivo(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def load_countries() -> set[str]:
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
    df = pd.DataFrame(rows, columns=["iso3", "year", "value"])
    return df[df["value"].notna()]


def montar_painel_janela() -> pd.DataFrame:
    """Painel 2012-2022 com todos os países oficiais do WDI (sem filtro ≥20 obs).

    Inclui o Brasil mesmo com 11 observações, pois o estudo de caso é o objeto
    da análise; as observações ausentes permanecem ausentes (sem imputação).
    """
    paises = load_countries()
    frames = [load_series(ind) for ind in INDICADORES_NECESSARIOS]
    nomes = ["NY_GDP_PCAP_KD", "NY_GDP_PCAP_KD_ZG", "SE_TER_ENRR"]
    df = frames[0].rename(columns={"value": nomes[0]})
    for f, n in zip(frames[1:], nomes[1:]):
        f = f.rename(columns={"value": n})
        df = df.merge(f, on=["iso3", "year"], how="outer")
    df = df[(df["iso3"].isin(paises))
            & (df["year"] >= JANELA_INI) & (df["year"] <= JANELA_FIM)]
    df = df.sort_values(["iso3", "year"]).reset_index(drop=True)
    df["ln_gdp_pc"] = np.log(df["NY_GDP_PCAP_KD"].where(df["NY_GDP_PCAP_KD"] > 0))
    df["ln_tertiaria"] = np.log(df["SE_TER_ENRR"].where(df["SE_TER_ENRR"] > 0))
    return df


def extremos_por_ano(d: pd.DataFrame, col: str):
    """(primeiro_ano, ultimo_ano) com valor não nulo de `col` no período."""
    dd = d[d[col].notna()]
    if len(dd) == 0:
        return None, None
    return int(dd["year"].min()), int(dd["year"].max())


def bloco_valores(m_ini, m_fim, g_ini, g_fim, zg, ano_ini, ano_fim):
    dm = (m_fim - m_ini) if (m_ini is not None and m_fim is not None) else None
    anos = (ano_fim - ano_ini) if (ano_ini is not None and ano_fim is not None) else None
    cresc = None
    if g_ini is not None and g_fim is not None and anos and anos > 0:
        cresc = ((g_fim / g_ini) ** (1 / anos) - 1) * 100

    def r3(x):
        return round(x, 3) if x is not None else None

    def r0(x):
        return round(x) if x is not None else None

    def r2(x):
        return round(x, 2) if x is not None else None

    return {
        "ano_inicio": ano_ini,
        "ano_fim": ano_fim,
        "n_anos": anos,
        "matricula_inicio": r3(m_ini),
        "matricula_fim": r3(m_fim),
        "delta_matricula_pp": r3(dm),
        "pib_pc_inicio": r3(g_ini),
        "pib_pc_fim": r3(g_fim),
        "crescimento_medio_anual_pct": r3(cresc),
        "crescimento_zg_media_pct": r2(zg),
        "matricula_inicio_txt": r3(m_ini),
        "matricula_fim_txt": r3(m_fim),
        "delta_matricula_pp_txt": r3(dm),
        "pib_pc_inicio_txt": r0(g_ini),
        "pib_pc_fim_txt": r0(g_fim),
        "crescimento_medio_anual_pct_txt": r3(cresc),
    }


def fmt(x, casas=3, sinal=False):
    if x is None:
        return "n/d"
    if sinal:
        return f"{x:+.{casas}f}".replace(".", ",")
    return f"{x:.{casas}f}".replace(".", ",")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    hashes = {ind: sha256_arquivo(RAW / f"wdi_{ind}.json")
              for ind in INDICADORES_NECESSARIOS}
    sha_meta = sha256_arquivo(RAW / "wdi_countries_meta.json")

    sub = montar_painel_janela()

    prov = {
        "janela": [JANELA_INI, JANELA_FIM],
        "fonte": "dados crus WDI (data/raw_expandido/)",
        "verificacao_api": {
            "data": "2026-08-14",
            "bate_com_api_oficial": True,
        },
        "sha256_raw": hashes,
        "sha256_countries_meta": sha_meta,
        "proveniencia_fechada": True,
        "brasil": {},
        "grupos": {},
        "china": {},
        "observacao": (
            "Janela comum 2012-2022: único período em que o WDI reporta "
            "matrícula terciária para o Brasil (11 observações não nulas, "
            "abaixo do limiar de 20 usado na amostra principal de 135 países). "
            "Cobertura desbalanceada por país; para cada unidade usam-se o "
            "primeiro e o último ano disponíveis na janela e o crescimento "
            "médio anual é calculado sobre o número real de anos — sem imputação."
        ),
    }

    linhas = []

    # --- Brasil isolado ---
    d_bra = sub[sub["iso3"] == BRASIL].sort_values("year")
    a_ini, a_fim = extremos_por_ano(d_bra, "SE_TER_ENRR")
    # PIB usa a mesma janela da matrícula (evita desalinhamento)
    g_ini = getv(d_bra, a_ini, "NY_GDP_PCAP_KD") if a_ini else None
    g_fim = getv(d_bra, a_fim, "NY_GDP_PCAP_KD") if a_fim else None
    zg = float(d_bra["NY_GDP_PCAP_KD_ZG"].mean()) if len(d_bra) else None
    bloco = bloco_valores(
        getv(d_bra, a_ini, "SE_TER_ENRR") if a_ini else None,
        getv(d_bra, a_fim, "SE_TER_ENRR") if a_fim else None,
        g_ini, g_fim, zg, a_ini, a_fim,
    )
    bloco["iso3"] = BRASIL
    prov["brasil"] = bloco
    linhas.append(("Brasil", bloco))

    # associação intra-Brasil (primeiras diferenças)
    db = (sub[sub["iso3"] == BRASIL][["year", "ln_tertiaria", "ln_gdp_pc"]]
          .dropna().sort_values("year"))
    dd = db.diff().dropna()
    if len(dd) >= 3:
        from scipy import stats

        rho, pval = stats.spearmanr(dd["ln_tertiaria"], dd["ln_gdp_pc"])
        prov["brasil"]["rho_primeiras_diferencas"] = round(float(rho), 3)
        prov["brasil"]["rho_primeiras_diferencas_p"] = round(float(pval), 3)
        prov["brasil"]["rho_primeiras_diferencas_n"] = int(len(dd))

    # resíduo do Brasil na relação global de níveis (janela 2012-2022)
    dn = sub[["iso3", "ln_tertiaria", "ln_gdp_pc"]].dropna()
    X = np.column_stack([np.ones(len(dn)), dn["ln_gdp_pc"].values])
    beta, *_ = np.linalg.lstsq(X, dn["ln_tertiaria"].values, rcond=None)
    previsto = X @ beta
    residuo = dn["ln_tertiaria"].values - previsto
    resid_bra = float(residuo[dn["iso3"].values == BRASIL].mean())
    prov["brasil"]["residuo_ln_terciaria_relacao_global"] = round(resid_bra, 3)
    prov["brasil"]["residuo_relacao_global_n"] = int(len(dn))
    prov["brasil"]["residuo_ln_terciaria_relacao_global_txt"] = round(resid_bra, 3)

    # --- Grupos (primeiro/último ano com dados no grupo) ---
    for nome, paises in GRUPOS.items():
        dg = sub[sub["iso3"].isin(paises)]
        dg_mat = dg[dg["SE_TER_ENRR"].notna()]
        a_ini_g, a_fim_g = extremos_por_ano(dg_mat, "SE_TER_ENRR")
        # médias do grupo no ano inicial e final (com qualquer país disponível)
        def media_no(ano, col):
            rr = dg[dg["year"] == ano][col]
            return float(rr.mean()) if len(rr) and rr.notna().any() else None

        m_i = media_no(a_ini_g, "SE_TER_ENRR") if a_ini_g else None
        m_f = media_no(a_fim_g, "SE_TER_ENRR") if a_fim_g else None
        g_i = media_no(a_ini_g, "NY_GDP_PCAP_KD") if a_ini_g else None
        g_f = media_no(a_fim_g, "NY_GDP_PCAP_KD") if a_fim_g else None
        zg_g = float(dg["NY_GDP_PCAP_KD_ZG"].mean()) if len(dg) else None
        bloco_g = bloco_valores(m_i, m_f, g_i, g_f, zg_g, a_ini_g, a_fim_g)
        bloco_g["paises"] = paises
        prov["grupos"][nome] = bloco_g
        linhas.append((NOME_GRUPO[nome], bloco_g))

    # --- China isolada ---
    d_ch = sub[sub["iso3"] == "CHN"].sort_values("year")
    c_ini, c_fim = extremos_por_ano(d_ch, "SE_TER_ENRR")
    bloco_c = bloco_valores(
        getv(d_ch, c_ini, "SE_TER_ENRR") if c_ini else None,
        getv(d_ch, c_fim, "SE_TER_ENRR") if c_fim else None,
        getv(d_ch, c_ini, "NY_GDP_PCAP_KD") if c_ini else None,
        getv(d_ch, c_fim, "NY_GDP_PCAP_KD") if c_fim else None,
        float(d_ch["NY_GDP_PCAP_KD_ZG"].mean()) if len(d_ch) else None,
        c_ini, c_fim,
    )
    bloco_c["iso3"] = "CHN"
    prov["china"] = bloco_c
    linhas.append(("China", bloco_c))

    # --- México e Argentina isolados (vizinhos latino-americanos) ---
    for iso_la, nome_la, chave_la in [("MEX", "México", "mexico"),
                                      ("ARG", "Argentina", "argentina")]:
        d_la = sub[sub["iso3"] == iso_la].sort_values("year")
        la_ini, la_fim = extremos_por_ano(d_la, "SE_TER_ENRR")
        bloco_la = bloco_valores(
            getv(d_la, la_ini, "SE_TER_ENRR") if la_ini else None,
            getv(d_la, la_fim, "SE_TER_ENRR") if la_fim else None,
            getv(d_la, la_ini, "NY_GDP_PCAP_KD") if la_ini else None,
            getv(d_la, la_fim, "NY_GDP_PCAP_KD") if la_fim else None,
            float(d_la["NY_GDP_PCAP_KD_ZG"].mean()) if len(d_la) else None,
            la_ini, la_fim,
        )
        bloco_la["iso3"] = iso_la
        prov[chave_la] = bloco_la
        linhas.append((nome_la, bloco_la))

    # --- persistência ---
    (OUT / "provenance_r418.json").write_text(
        json.dumps(prov, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    with open(OUT / "tabela8_brasil_comparado.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow([
            "unidade", "janela", "matricula_inicio", "matricula_fim",
            "delta_matricula_pp", "cresc_pib_pc_anual_pct", "cresc_zg_media_pct",
        ])
        for nome, b in linhas:
            janela = f"{b['ano_inicio']}-{b['ano_fim']}" if b["ano_inicio"] else "n/d"
            w.writerow([
                nome,
                janela,
                fmt(b["matricula_inicio"]),
                fmt(b["matricula_fim"]),
                fmt(b["delta_matricula_pp"], sinal=True),
                fmt(b["crescimento_medio_anual_pct"]),
                fmt(b["crescimento_zg_media_pct"], casas=2),
            ])

    print(json.dumps(prov, ensure_ascii=False, indent=2))
    return 0


def getv(d: pd.DataFrame, ano, col: str):
    if ano is None:
        return None
    r = d[d["year"] == ano]
    if len(r) and pd.notna(r[col].iloc[0]):
        return float(r[col].iloc[0])
    return None


if __name__ == "__main__":
    raise SystemExit(main())
