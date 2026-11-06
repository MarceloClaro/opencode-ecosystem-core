#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audita DOIs: resolve, confere Crossref e procura DOIs ausentes."""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "TCC" / "doi_audit.json"
UA = "OpenCodeCore-DOI-Audit/1.0 (mailto:marceloclaro@example.org)"

CONHECIDOS = {
    "bezerra2022": "10.31417/educitec.v8.1826",
    "cabral2017": "10.1590/0102-4698142079",
    "couto2019": "10.5216/ree.v21.55954",
    "fam2021": "10.33448/rsd-v10i6.15912",
    "maia2020": "10.36311/2674-8681.2020.v21n1.02.p15",
    "nascimento2015": "10.5216/rp.v25i2.38149",
    "nunes2013": "10.5902/1984686X10178",
    "schmidt2016": "10.15348/1980-6906/psicologia.v18n1p222-235",
    "togashi2016": "10.1590/S1413-65382216000300004",
}

AUSENTES = {
    "costa2016": {
        "titulo": "Escolarização de crianças com transtorno do espectro autista: a concepção do educador numa perspectiva inclusiva",
        "autor": "Luciane Silva da Costa",
        "urls": ["https://repositorio.ufsm.br/handle/1/7260?show=full"],
    },
    "nunes2018": {
        "titulo": "Práticas pedagógicas na inclusão do aluno com TEA: uma revisão sistemática",
        "autor": "Vera Lucia Mendonça Nunes",
        "urls": ["https://proceedings.science/cbee-2018/papers?query=Pr%C3%A1ticas%20pedag%C3%B3gicas%20na%20inclus%C3%A3o%20do%20aluno%20com%20TEA"],
    },
    "ribeiro2019": {
        "titulo": "Intervenções neuropsicopedagógicas em casos de autismo",
        "autor": "MCCA Menezes",
        "urls": [],
    },
    "santos2021": {
        "titulo": "Abordagens neuropsicopedagógicas no processo ensino: uma revisão bibliográfica entre os anos de 2010 e 2021",
        "autor": "Renata Cristina Santos",
        "urls": ["https://educacaopublica.cecierj.edu.br/biblioteca?busca=Abordagens+neuropsicopedag%C3%B3gicas+no+processo+ensino"],
    },
    "silvaarantes2020": {
        "titulo": "Inclusão dos estudantes com transtorno do espectro autista TEA: percepções docentes",
        "autor": "Hanna Christina da Silva",
        "urls": ["https://revista.uepb.edu.br/REIN/article/view/218"],
    },
}


def http(url: str, method: str = "GET", timeout: int = 40) -> tuple[int, str, str]:
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as fh:
            corpo = fh.read(200000).decode("utf-8", "ignore") if method == "GET" else ""
            return fh.status, fh.geturl(), corpo
    except urllib.error.HTTPError as exc:
        return exc.code, url, ""
    except Exception as exc:
        return 0, url, f"{type(exc).__name__}: {exc}"


def crossref_doi(doi: str) -> dict | None:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40) as fh:
            m = json.load(fh)["message"]
        return {
            "titulo": (m.get("title") or [""])[0],
            "ano": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "doi": m.get("DOI"),
        }
    except Exception:
        return None


def resolver(doi: str) -> dict:
    status, final, _ = http("https://doi.org/" + urllib.parse.quote(doi, safe=""), method="HEAD")
    if status == 0:
        status, final, _ = http("https://doi.org/" + urllib.parse.quote(doi, safe=""), method="GET")
    meta = crossref_doi(doi)
    return {"doi": doi, "status_http": status, "url_final": final, "crossref": meta,
            "ativo": status in (200, 301, 302, 303, 307, 308) and meta is not None}


def buscar_crossref(titulo: str, autor: str) -> list[dict]:
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {"query.bibliographic": f"{titulo} {autor}", "rows": 8,
         "select": "DOI,title,container-title,issued,author"}
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40) as fh:
            itens = json.load(fh)["message"]["items"]
    except Exception as exc:
        return [{"erro": str(exc)}]
    saida = []
    for it in itens:
        saida.append({
            "doi": it.get("DOI"),
            "titulo": (it.get("title") or [""])[0],
            "veiculo": (it.get("container-title") or [""])[0],
            "ano": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
        })
    return saida


def procurar_doi_em_url(url: str) -> list[str]:
    status, final, corpo = http(url)
    if status == 0 or not corpo:
        return []
    achados = set()
    for m in re.finditer(r'(?:citation_doi|dc\.identifier\.doi|DOI)[^>]{0,80}?["\'>](10\.\d{4,9}/[^"\'<>\s]+)', corpo, re.I):
        achados.add(m.group(1).rstrip("."))
    for m in re.finditer(r'https?://doi\.org/(10\.\d{4,9}/[^"\'<>\s]+)', corpo, re.I):
        achados.add(m.group(1).rstrip("."))
    return sorted(achados)


def main() -> int:
    resultado = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "regra": "Só aceitar citação científica com DOI ativo e auditável.",
        "conhecidos": [],
        "ausentes": [],
    }

    for chave, doi in CONHECIDOS.items():
        print("verificando", chave, doi, flush=True)
        resultado["conhecidos"].append({"chave": chave, **resolver(doi)})
        time.sleep(1)

    for chave, dados in AUSENTES.items():
        print("procurando", chave, flush=True)
        candidatos = buscar_crossref(dados["titulo"], dados["autor"])
        time.sleep(1)
        dois_em_urls = {}
        for url in dados["urls"]:
            dois_em_urls[url] = procurar_doi_em_url(url)
            time.sleep(1)
        resultado["ausentes"].append({
            "chave": chave,
            "titulo": dados["titulo"],
            "autor": dados["autor"],
            "crossref": candidatos,
            "dois_em_urls": dois_em_urls,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== CONHECIDOS ===")
    for r in resultado["conhecidos"]:
        print(f"{r['chave']:16s} {r['doi']:55s} HTTP {r['status_http']} ativo={r['ativo']}")
    print("\n=== AUSENTES ===")
    for r in resultado["ausentes"]:
        print(f"\n{r['chave']}: {r['titulo'][:80]}")
        for url, dois in r["dois_em_urls"].items():
            print("  ", url[:80], "->", dois or "sem DOI no HTML")
        for c in r["crossref"][:5]:
            print("   crossref:", c.get("doi"), "|", (c.get("titulo") or "")[:80], "|", c.get("ano"))
    print(f"\nOK: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
