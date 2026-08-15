#!/usr/bin/env python3
"""Coleta de indicadores municipais do Censo Demográfico 2022 (IBGE SIDRA v3)
para os 9 municípios da microrregião do Sertão de Cratéus (IBGE 23018).

Ciclo R427 — SPEC-935-R427-crateus-diagnostico.md.

Fonte: IBGE SIDRA (servicodados.ibge.gov.br), tabelas do Censo 2022.
Saída: data/processed/indicadores_sidra.json + data/processed/manifest_sidra.json
"""

import json
import sys
import time
import urllib.request
import gzip
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent
PROC = PAPER / "data" / "processed"

MUNICIPIOS = [
    2301257, 2304103, 2305605, 2305654, 2308609,
    2309300, 2309409, 2311264, 2313203,
]

# tabela: (nome_indicador, tabela, variavel, classificacoes: {class_id: [cat_ids]}, periodo)
COLETA = [
    ("taxa_alfabetizacao_15_pct", 9543, "2513", {"2": ["6794"], "86": ["95251"], "287": ["100362"]}, "2022"),
    ("agua_rede_geral_pct", 6803, "1000381", {"1821": ["72144"]}, "2022"),
    ("esgoto_rede_pct", 6805, "1000381", {"11558": ["72110"]}, "2022"),
    ("lixo_coletado_pct", 6892, "1000381", {"67": ["2520"]}, "2022"),
    ("internet_domicilios_pct", 9936, "1000381", {"2072": ["77585"], "63": ["95826"], "125": ["2932"]}, "2022"),
    ("banheiro_exclusivo_pct", 6806, "1000381", {"458": ["12032"], "11558": ["46292"]}, "2022"),
    # Nota: Gini municipal do Censo 2022 não publicado no SIDRA (tabelas 3568/2037 são 2000/2010).
]


def _get(url: str, tentativas: int = 4) -> dict | list:
    ultimo = None
    for i in range(tentativas):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip"}
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
            return json.loads(data)
        except Exception as e:  # noqa: BLE001
            ultimo = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"falha ao obter {url}: {ultimo}")


def coletar() -> dict:
    dados = {}
    for nome, tabela, variavel, classificacoes, periodo in COLETA:
        loc = ",".join(str(m) for m in MUNICIPIOS)
        cls = "&".join(f"classificacao={c}[{','.join(v)}]" for c, v in classificacoes.items())
        url = (f"https://servicodados.ibge.gov.br/api/v3/agregados/{tabela}/periodos/{periodo}"
               f"/variaveis/{variavel}?localidades=N6[{loc}]&{cls}")
        resp = _get(url)
        for bloco in resp:
            for res in bloco.get("resultados", []):
                for serie in res.get("series", []):
                    mun_id = serie["localidade"]["id"]
                    valor = list(serie["serie"].values())[0]
                    dados.setdefault(int(mun_id), {})[nome] = _num(valor)
        print(f"  ok {nome}: {len(dados)} municípios", flush=True)
    return dados


def _num(v) -> float | None:
    if v is None or v == "-":
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


def main() -> int:
    PROC.mkdir(parents=True, exist_ok=True)
    print("Coletando SIDRA Censo 2022 (R427)...", flush=True)
    dados = coletar()
    registros = [{"cod_mun": m, **dados.get(m, {})} for m in MUNICIPIOS]

    out = PROC / "indicadores_sidra.json"
    out.write_text(json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8")

    import hashlib
    manifest = {
        "ciclo": "R427",
        "fonte": "IBGE SIDRA v3 — Censo Demográfico 2022",
        "coleta": {
            "tabelas": [{"indicador": n, "tabela": t, "variavel": v, "periodo": p}
                        for n, t, v, _c, p in COLETA],
        },
        "municipios": MUNICIPIOS,
        "sha256_json": hashlib.sha256(out.read_bytes()).hexdigest(),
    }
    (PROC / "manifest_sidra.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK: {len(registros)} municípios × {len(COLETA)} indicadores → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
