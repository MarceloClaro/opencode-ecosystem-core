#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audita os 20 DOIs do TCC da Maria do Socorro.

Para cada obra: metadados no Crossref e resolução em doi.org.
Salva `dados/doi_audit_20.json` e imprime um resumo.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DADOS = BASE / "dados"
DADOS.mkdir(exist_ok=True)

OBRAS = {
    "harrower2001": "10.1177/0145445501255006",
    "rotheram2010": "10.1111/j.1469-7610.2010.02289.x",
    "crosland2012": "10.1177/0145445512442682",
    "koegel2012": "10.1016/j.cbpra.2010.11.003",
    "humphrey2013": "10.1080/13603116.2011.580462",
    "lindsay2013": "10.1080/1034912x.2013.846470",
    "nunes2013": "10.5902/1984686X10178",
    "wong2015": "10.1007/s10803-014-2351-z",
    "chang2016": "10.1016/j.rasd.2016.03.010",
    "schmidt2016": "10.15348/1980-6906/psicologia.v18n1p222-235",
    "togashi2016": "10.1590/S1413-65382216000300004",
    "cabral2017": "10.1590/0102-4698142079",
    "couto2019": "10.5216/ree.v21.55954",
    "maia2020": "10.36311/2674-8681.2020.v21n1.02.p15",
    "sousa2020": "10.18554/ifd.v7i3.4979",
    "fam2021": "10.33448/rsd-v10i6.15912",
    "suassuna2021": "10.51891/rease.v7i7.1831",
    "hume2021": "10.1007/s10803-020-04844-2",
    "bezerra2022": "10.31417/educitec.v8.1826",
    "fang2023": "10.1016/j.rasd.2023.102257",
}

UA = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120 Safari/537.36"
}


def crossref(doi: str) -> dict:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    req = urllib.request.Request(
        url, headers={"User-Agent": "OpenCodeCore/1.0 (mailto:marceloclaro@example.org)"}
    )
    for tentativa in range(3):
        try:
            m = json.load(urllib.request.urlopen(req, timeout=60))["message"]
            autores = [
                ((a.get("given") or "") + " " + (a.get("family") or "")).strip()
                for a in m.get("author", [])
            ]
            return {
                "titulo": (m.get("title") or [""])[0],
                "autores": autores,
                "ano": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
                "veiculo": (m.get("container-title") or [""])[0],
                "volume": m.get("volume"),
                "numero": m.get("issue"),
                "paginas": m.get("page"),
                "tipo": m.get("type"),
                "editora": m.get("publisher"),
            }
        except Exception as exc:  # noqa: BLE001
            if tentativa == 2:
                return {"erro_crossref": f"{type(exc).__name__}: {exc}"}
            time.sleep(1.5)
    return {}


def resolver(doi: str) -> dict:
    req = urllib.request.Request(
        "https://doi.org/" + urllib.parse.quote(doi, safe=""), method="GET", headers=UA
    )
    for tentativa in range(2):
        try:
            with urllib.request.urlopen(req, timeout=45) as fh:
                return {"http": fh.status, "url_final": fh.geturl()}
        except Exception as exc:  # noqa: BLE001
            if tentativa == 1:
                return {"http": getattr(exc, "code", 0)}
            time.sleep(1.0)
    return {"http": 0}


def main() -> int:
    saida = []
    for chave, doi in OBRAS.items():
        print(f"{chave:14s} {doi}", flush=True)
        rec = {"chave": chave, "doi": doi}
        rec.update(crossref(doi))
        rec.update(resolver(doi))
        saida.append(rec)
        time.sleep(0.4)

    destino = DADOS / "doi_audit_20.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")

    ok200 = sum(1 for r in saida if r.get("http") == 200)
    ok403 = sum(1 for r in saida if r.get("http") == 403)
    cross = sum(1 for r in saida if "erro_crossref" not in r)
    print(f"\n{len(saida)} obras | Crossref: {cross} | HTTP 200: {ok200} | HTTP 403: {ok403}")
    print("Registro:", destino)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
