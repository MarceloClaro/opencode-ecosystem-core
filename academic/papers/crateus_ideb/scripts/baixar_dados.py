#!/usr/bin/env python3
"""Coleta dados oficiais do estudo Crateús-IDEB (R426).

Baixa de fontes oficiais (INEP, IBGE) para data/raw/ e gera os arquivos
processados em data/processed/ (JSON, para uso offline). Registra
proveniência (URL, timestamp, sha256) em data/raw/SOURCE_MANIFEST.json.

Fontes:
- INEP: IDEB municipal anos iniciais/finais 2005-2025
- IBGE: PIB municipal 2010-2021; renda do responsável Censo 2022;
  malha municipal CE 2023 (para o mapa)

Uso: python3 scripts/baixar_dados.py
"""
from __future__ import annotations

import hashlib
import json
import warnings
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

warnings.filterwarnings("ignore")

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
RAW = DATA / "raw"
PROC = DATA / "processed"
RAW.mkdir(parents=True, exist_ok=True)
PROC.mkdir(parents=True, exist_ok=True)

MUNICIPIOS_MICRO = [
    2301257,  # Ararendá
    2304103,  # Crateús
    2305605,  # Independência
    2305654,  # Ipaporanga
    2308609,  # Monsenhor Tabosa
    2309300,  # Nova Russas
    2309409,  # Novo Oriente
    2311264,  # Quiterianópolis
    2313203,  # Tamboril
]

FONTES = {
    "ideb_ai_2025": "https://download.inep.gov.br/ideb/resultados/divulgacao_anos_iniciais_municipios_2025.zip",
    "ideb_af_2025": "https://download.inep.gov.br/ideb/resultados/divulgacao_anos_finais_municipios_2025.zip",
    "pib_municipal": "https://ftp.ibge.gov.br/Pib_Municipios/2021/base/base_de_dados_2010_2021_xlsx.zip",
    "renda_responsavel": "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios_Rendimento_do_Responsavel/Agregados_por_municipios_renda_responsavel_BR_20260508_csv.zip",
    "malha_ce": "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2023/UFs/CE/CE_Municipios_2023.zip",
}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def baixar(nome: str, url: str, destino: Path) -> dict:
    if destino.exists():
        conteudo = destino.read_bytes()
    else:
        r = requests.get(url, timeout=300, verify=False)
        r.raise_for_status()
        conteudo = r.content
        destino.write_bytes(conteudo)
    return {
        "fonte": nome,
        "url": url,
        "data_acesso": datetime.now(timezone.utc).isoformat(),
        "sha256": sha256_bytes(conteudo),
        "bytes": len(conteudo),
        "arquivo_local": str(destino.relative_to(RAIZ)),
    }


def ler_ideb(zip_path: Path, url: str) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as zf:
        xlsx = [n for n in zf.namelist() if n.endswith(".xlsx")][0]
        with zf.open(xlsx) as f:
            df = pd.read_excel(f, skiprows=9)
    df = df.rename(columns={
        "SG_UF": "uf", "CO_MUNICIPIO": "cod_mun", "NO_MUNICIPIO": "nome_mun",
        "REDE": "rede",
    })
    df["cod_mun"] = pd.to_numeric(df["cod_mun"], errors="coerce").astype("Int64")
    obs = {c: c.replace("VL_OBSERVADO_", "") for c in df.columns if str(c).startswith("VL_OBSERVADO_")}
    df = df.rename(columns=obs)
    proj = {c: c.replace("VL_PROJECAO_", "proj_") for c in df.columns if str(c).startswith("VL_PROJECAO_")}
    df = df.rename(columns=proj)
    cols = ["uf", "cod_mun", "nome_mun", "rede"] + list(obs.values()) + list(proj.values())
    df = df[cols]
    df["etapa"] = "anos_iniciais" if "anos_iniciais" in url else "anos_finais"
    return df


def processar_ideb() -> pd.DataFrame:
    registros = []
    for nome in ["ideb_ai_2025", "ideb_af_2025"]:
        url = FONTES[nome]
        destino = RAW / f"{nome}.zip"
        if not destino.exists():
            baixar(nome, url, destino)
        registros.append(baixar(nome, url, destino))
        df = ler_ideb(destino, url)
        if nome == "ideb_ai_2025":
            ideb = df
        else:
            ideb = pd.concat([ideb, df], ignore_index=True)
    return ideb, registros


def processar_pib() -> pd.DataFrame:
    nome = "pib_municipal"
    destino = RAW / f"{nome}.zip"
    registro = baixar(nome, FONTES[nome], destino)
    with zipfile.ZipFile(destino) as zf:
        xlsx = [n for n in zf.namelist() if n.endswith(".xlsx")][0]
        with zf.open(xlsx) as f:
            df = pd.read_excel(f)
    df = df.rename(columns={
        "Ano": "ano", "Código do Município": "cod_mun", "Nome do Município": "nome_mun",
        "Código da Microrregião": "cod_micro", "Nome da Microrregião": "nome_micro",
        "Produto Interno Bruto per capita, \na preços correntes\n(R$ 1,00)": "pib_per_capita",
        "Produto Interno Bruto, \na preços correntes\n(R$ 1.000)": "pib_total_1000",
    })
    df["cod_mun"] = pd.to_numeric(df["cod_mun"], errors="coerce").astype("Int64")
    cols = ["ano", "cod_mun", "nome_mun", "cod_micro", "nome_micro", "pib_per_capita", "pib_total_1000"]
    return df[cols], [registro]


def processar_renda() -> pd.DataFrame:
    nome = "renda_responsavel"
    destino = RAW / f"{nome}.zip"
    registro = baixar(nome, FONTES[nome], destino)
    with zipfile.ZipFile(destino) as zf:
        csv = [n for n in zf.namelist() if n.endswith(".csv")][0]
        with zf.open(csv) as f:
            df = pd.read_csv(f, encoding="latin-1", sep=";", decimal=",")
    df = df.rename(columns={
        "CD_MUN": "cod_mun", "NM_MUN": "nome_mun",
        "V06002": "moradores", "V06004": "renda_media_resp",
        "V06006": "renda_mediana_resp", "V06001": "pessoas_resp",
    })
    df["cod_mun"] = pd.to_numeric(df["cod_mun"], errors="coerce").astype("Int64")
    cols = ["cod_mun", "nome_mun", "moradores", "pessoas_resp", "renda_media_resp", "renda_mediana_resp"]
    return df[cols], [registro]


def salvar_json(df: pd.DataFrame, nome: str) -> None:
    df.to_json(PROC / nome, orient="records", force_ascii=False, indent=1)


def principal() -> None:
    ideb, reg_ideb = processar_ideb()
    pib, reg_pib = processar_pib()
    renda, reg_renda = processar_renda()

    # contexto: Ceará inteiro (para análises de robustez) e Brasil inteiro
    ideb_ce = ideb[ideb["uf"] == "CE"].copy()
    pib_ce = pib[pib["cod_mun"].astype(str).str.startswith("23")].copy()
    renda_ce = renda[renda["cod_mun"].astype(str).str.startswith("23")].copy()

    salvar_json(ideb, "ideb_br.json")
    salvar_json(pib, "pib_br.json")
    salvar_json(renda, "renda_br.json")
    salvar_json(ideb_ce, "ideb_ce.json")
    salvar_json(pib_ce, "pib_ce.json")
    salvar_json(renda_ce, "renda_ce.json")
    salvar_json(ideb_ce[ideb_ce["cod_mun"].isin(MUNICIPIOS_MICRO)], "ideb_microrregiao.json")
    salvar_json(pib_ce[pib_ce["cod_mun"].isin(MUNICIPIOS_MICRO)], "pib_microrregiao.json")
    salvar_json(renda_ce[renda_ce["cod_mun"].isin(MUNICIPIOS_MICRO)], "renda_microrregiao.json")

    manifest = {"gerado_em": datetime.now(timezone.utc).isoformat(),
                "microrregiao": "Sertão de Cratéus (IBGE 23018)",
                "municipios": MUNICIPIOS_MICRO,
                "fontes": reg_ideb + reg_pib + reg_renda}
    (RAW / "SOURCE_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OK: ideb CE linhas:", len(ideb_ce), "| PIB CE:", len(pib_ce), "| renda CE:", len(renda_ce))
    print("Manifest:", RAW / "SOURCE_MANIFEST.json")


if __name__ == "__main__":
    principal()
