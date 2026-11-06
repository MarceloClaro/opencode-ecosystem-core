#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificação profunda das seis referências não localizadas.

Consulta Crossref, OpenAlex e Semantic Scholar com pausas e retentativas.
Não conclui por similaridade: apenas registra candidatos para inspeção humana.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "dados" / "verificacao_profunda.json"
UA = "OpenCodeCore-RefAudit/1.0 (mailto:marceloclaro@example.org)"

ALVOS = [
    {
        "id": "costa2016",
        "autores": ["Luciane Silva da Costa"],
        "titulo": "Escolarização de crianças com transtorno do espectro autista: a concepção do educador numa perspectiva inclusiva",
        "ano": 2016,
        "veiculo": "",
    },
    {
        "id": "nunes2018",
        "autores": ["Vera Lucia Mendonça Nunes"],
        "titulo": "Práticas pedagógicas na inclusão do aluno com TEA: uma revisão sistemática",
        "ano": 2018,
        "veiculo": "Congresso Brasileiro de Educação Especial",
    },
    {
        "id": "ribeiro2019",
        "autores": ["Mariana Laura Queiroz Ribeiro"],
        "titulo": "Intervenções neuropsicopedagógicas em casos de autismo",
        "ano": 2019,
        "veiculo": "CONEDU",
    },
    {
        "id": "santos2021",
        "autores": ["Renata Cristina Santos", "Fábio Augusto Lopes"],
        "titulo": "Abordagens neuropsicopedagógicas no processo ensino: uma revisão bibliográfica entre os anos de 2010 e 2021",
        "ano": 2021,
        "veiculo": "Revista Educação Pública",
    },
    {
        "id": "silvaoliveira2016",
        "autores": ["Adriana Paula dos Santos Silva", "Amanda Lima Oliveira"],
        "titulo": "Inclusão de crianças com transtorno do espectro autista: revisão de literatura",
        "ano": 2016,
        "veiculo": "Psicologia em Estudo",
    },
    {
        "id": "silvaarantes2020",
        "autores": ["Hanna Christina da Silva", "Adlene Silva Arantes"],
        "titulo": "Inclusão dos estudantes com transtorno do espectro autista TEA: percepções docentes",
        "ano": 2020,
        "veiculo": "Revista Educação Inclusiva",
    },
]


def buscar(url: str, headers: dict | None = None, tentativas: int = 3) -> dict | list | None:
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers=headers or {"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=35) as fh:
                return json.load(fh)
        except Exception as exc:
            if i == tentativas - 1:
                return {"_erro": f"{type(exc).__name__}: {exc}"}
            time.sleep(3 * (i + 1))
    return None


def crossref(consulta: str) -> dict:
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {"query.bibliographic": consulta, "rows": 6,
         "select": "DOI,title,container-title,issued,volume,issue,page,author,type,publisher"}
    )
    data = buscar(url)
    if not isinstance(data, dict) or "_erro" in data:
        return {"erro": data.get("_erro") if isinstance(data, dict) else "sem resposta", "itens": []}
    itens = []
    for it in data.get("message", {}).get("items", []):
        itens.append({
            "doi": it.get("DOI"),
            "titulo": (it.get("title") or [""])[0],
            "veiculo": (it.get("container-title") or [""])[0],
            "ano": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "volume": it.get("volume"),
            "numero": it.get("issue"),
            "paginas": it.get("page"),
            "autores": [f"{a.get('family','')}, {a.get('given','')}" for a in it.get("author", [])][:6],
        })
    return {"itens": itens}


def openalex(consulta: str) -> dict:
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(
        {"search": consulta, "per-page": 6, "mailto": "marceloclaro@example.org"}
    )
    data = buscar(url)
    if not isinstance(data, dict) or "_erro" in data:
        return {"erro": data.get("_erro") if isinstance(data, dict) else "sem resposta", "itens": []}
    itens = []
    for w in data.get("results", []):
        loc = (w.get("primary_location") or {}).get("source") or {}
        itens.append({
            "doi": w.get("doi"),
            "titulo": w.get("title"),
            "veiculo": loc.get("display_name"),
            "ano": w.get("publication_year"),
            "autores": [a.get("author", {}).get("display_name") for a in w.get("authorships", [])][:6],
            "tipo": w.get("type"),
        })
    return {"itens": itens}


def semantic(consulta: str) -> dict:
    url = "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(
        {"query": consulta, "limit": 6, "fields": "title,year,venue,authors,externalIds,publicationTypes"}
    )
    data = buscar(url, headers={"User-Agent": UA, "Accept": "application/json"})
    if not isinstance(data, dict) or "_erro" in data:
        return {"erro": data.get("_erro") if isinstance(data, dict) else "sem resposta", "itens": []}
    itens = []
    for p in data.get("data", []):
        itens.append({
            "doi": (p.get("externalIds") or {}).get("DOI"),
            "titulo": p.get("title"),
            "veiculo": p.get("venue"),
            "ano": p.get("year"),
            "autores": [a.get("name") for a in p.get("authors", [])][:6],
        })
    return {"itens": itens}


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    resultados = []
    for alvo in ALVOS:
        consulta = f"{alvo['titulo']} {alvo['autores'][0]}"
        print(f"[{alvo['id']}] consultando...", flush=True)
        cr = crossref(consulta)
        time.sleep(2)
        oa = openalex(consulta)
        time.sleep(2)
        ss = semantic(consulta)
        time.sleep(2)
        resultados.append({"alvo": alvo, "crossref": cr, "openalex": oa, "semantic": ss})

    payload = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "aviso": "Candidatos automáticos; exigem inspeção humana. Ausência não prova inexistência.",
        "resultados": resultados,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    for res in resultados:
        print(f"\n=== {res['alvo']['id']} ===")
        for fonte in ("crossref", "openalex", "semantic"):
            bloco = res[fonte]
            if bloco.get("erro"):
                print(f"  {fonte}: ERRO {bloco['erro']}")
                continue
            print(f"  {fonte}:")
            for item in bloco["itens"][:4]:
                print(f"    {item.get('ano')} | {(item.get('titulo') or '')[:95]} | "
                      f"{(item.get('veiculo') or '')[:45]} | {item.get('doi')}")
    print(f"\nOK: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
