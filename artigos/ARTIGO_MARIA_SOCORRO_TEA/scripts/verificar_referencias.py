#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica as referências do artigo via Crossref (API pública).

Não inventa metadados: registra o que a API devolve e marca como
"nao_verificada" o que não for encontrado. Saída em JSON + Markdown.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT_JSON = BASE / "dados" / "crossref_referencias.json"
OUT_MD = BASE / "dados" / "crossref_referencias.md"
MAILTO = "marceloclaro@example.org"
UA = f"OpenCodeCore-RefAudit/1.0 (mailto:{MAILTO})"

REFERENCIAS = [
    {"id": "costa2016", "autores": "Costa, Luciane Silva da", "ano": 2016,
     "titulo": "Escolarização de crianças com transtorno do espectro autista: a concepção do educador numa perspectiva inclusiva",
     "veiculo": "", "volume": "", "numero": "", "paginas": ""},
    {"id": "couto2019", "autores": "Couto, Cirleine Costa", "ano": 2019,
     "titulo": "Experiências de professores com o autismo: impacto no diagnóstico precoce e na inclusão escolar",
     "veiculo": "Revista Eletrônica de Enfermagem", "volume": "21", "numero": "", "paginas": ""},
    {"id": "silva2020", "autores": "Silva, Hanna Christina da; Arantes, Adlene Silva", "ano": 2020,
     "titulo": "Inclusão dos estudantes com transtorno do espectro autista TEA: percepções docentes",
     "veiculo": "Revista Educação Inclusiva", "volume": "4", "numero": "1", "paginas": "86-103"},
    {"id": "fam2021", "autores": "Fam, Antônio Eustáquio de Oliveira", "ano": 2021,
     "titulo": "O brincar no espaço escolar como estratégia de inclusão de alunos com Transtorno do Espectro Autista (TEA)",
     "veiculo": "Research, Society and Development", "volume": "10", "numero": "6", "paginas": ""},
    {"id": "nunes2021", "autores": "Nunes, Debora Regina de Paula; Azevedo, Mariana Queiroz Orrico; Schmidt, Carlo", "ano": 2021,
     "titulo": "Inclusão educacional de pessoas com Autismo no Brasil: uma revisão da literatura",
     "veiculo": "Revista Educação Especial", "volume": "26", "numero": "47", "paginas": "557-572"},
    {"id": "nascimento2017", "autores": "Nascimento, Fabiana Ferreira do; Cruz, Mara Lucia Reis Monteiro da", "ano": 2017,
     "titulo": "Da realidade à inclusão: uma investigação acerca da aprendizagem e do desenvolvimento do/a aluno/a com transtornos do espectro autista TEA",
     "veiculo": "Revista Polyphonia", "volume": "25", "numero": "2", "paginas": "51-66"},
    {"id": "maia2020", "autores": "Maia, Juliana; Bataglion, Giandra Anceski; Mazo, Janice Zarpellon", "ano": 2020,
     "titulo": "Alunos com transtorno do espectro autista na escola regular: relatos de professores de educação física",
     "veiculo": "Revista da Associação Brasileira de Atividade Motora Adaptada", "volume": "21", "numero": "1", "paginas": ""},
    {"id": "mendonca2022", "autores": "Mendonça, Mariana Ferreira de", "ano": 2022,
     "titulo": "A inclusão escolar de crianças com transtorno do espectro do autismo: uma revisão bibliográfica",
     "veiculo": "", "volume": "", "numero": "", "paginas": ""},
    {"id": "mendonca2017", "autores": "Mendonça, Vera Lucia; Oliveira, José Carlos", "ano": 2017,
     "titulo": "Formação docente para inclusão de alunos com Transtorno do Espectro Autista no Ensino Médio Integrado",
     "veiculo": "Revista Ensaio", "volume": "25", "numero": "96", "paginas": "661-686"},
    {"id": "nunes2018", "autores": "Nunes, Vera Lucia Mendonça", "ano": 2018,
     "titulo": "Práticas pedagógicas na inclusão do aluno com TEA: uma revisão sistemática",
     "veiculo": "Congresso Brasileiro de Educação Especial", "volume": "", "numero": "", "paginas": ""},
    {"id": "ribeiro2019", "autores": "Ribeiro, Mariana Laura Queiroz", "ano": 2019,
     "titulo": "Intervenções neuropsicopedagógicas em casos de autismo",
     "veiculo": "CONEDU", "volume": "", "numero": "", "paginas": ""},
    {"id": "santos2021", "autores": "Santos, Renata Cristina; Lopes, Fábio Augusto", "ano": 2021,
     "titulo": "Abordagens neuropsicopedagógicas no processo ensino: uma revisão bibliográfica entre os anos de 2010 e 2021",
     "veiculo": "Revista Educação Pública", "volume": "17", "numero": "3", "paginas": "123-138"},
    {"id": "schmidt2016", "autores": "Schmidt, Carlo", "ano": 2016,
     "titulo": "Inclusão escolar e autismo: uma análise da percepção docente e práticas pedagógicas",
     "veiculo": "Psicologia: Teoria e Prática", "volume": "18", "numero": "1", "paginas": "222-235"},
    {"id": "silvaoliveira2016", "autores": "Silva, Adriana Paula dos Santos; Oliveira, Amanda Lima", "ano": 2016,
     "titulo": "Inclusão de crianças com transtorno do espectro autista: revisão de literatura",
     "veiculo": "Psicologia em Estudo", "volume": "21", "numero": "4", "paginas": "533-542"},
    {"id": "togashi2016", "autores": "Togashi, Cláudia Miharu; Walter, Cátia Crivelenti de Figueiredo", "ano": 2016,
     "titulo": "As contribuições do uso da comunicação alternativa no processo de inclusão escolar de um aluno com transtorno do espectro do autismo",
     "veiculo": "Revista Brasileira de Educação Especial", "volume": "22", "numero": "", "paginas": "351-366"},
]


def consulta(ref: dict) -> dict:
    partes = [ref["autores"].split(";")[0], ref["titulo"]]
    if ref["veiculo"]:
        partes.append(ref["veiculo"])
    q = " ".join(partes)
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {"query.bibliographic": q, "rows": 4, "select": "DOI,title,container-title,issued,volume,issue,page,author,type,publisher"}
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as fh:
            data = json.load(fh)
    except Exception as exc:  # rede/API
        return {"status": "erro_api", "erro": f"{type(exc).__name__}: {exc}", "candidatos": []}

    candidatos = []
    for item in data.get("message", {}).get("items", []):
        titulo = (item.get("title") or [""])[0]
        container = (item.get("container-title") or [""])[0]
        ano = None
        try:
            ano = item["issued"]["date-parts"][0][0]
        except Exception:
            pass
        candidatos.append({
            "doi": item.get("DOI"),
            "titulo": titulo,
            "veiculo": container,
            "ano": ano,
            "volume": item.get("volume"),
            "numero": item.get("issue"),
            "paginas": item.get("page"),
            "tipo": item.get("type"),
            "editora": item.get("publisher"),
            "autores": [f"{a.get('family','')}, {a.get('given','')}" for a in item.get("author", [])][:6],
        })
    return {"status": "ok", "consulta": q, "candidatos": candidatos}


def main() -> int:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    resultados = []
    for ref in REFERENCIAS:
        res = consulta(ref)
        res["referencia"] = ref
        resultados.append(res)
        time.sleep(1.0)
        print(f"[{ref['id']}] {res['status']} -> {len(res.get('candidatos', []))} candidatos", file=sys.stderr)

    payload = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "fonte": "Crossref REST API",
        "aviso": "Correspondência automática por similaridade; exige conferência humana. Ausência não prova inexistência.",
        "resultados": resultados,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    linhas = ["# Verificação de referências — Crossref", "",
              f"Gerado em: {payload['gerado_em']}", "",
              "> Correspondência automática por similaridade. Exige conferência humana; ausência não prova inexistência.", ""]
    for res in resultados:
        ref = res["referencia"]
        linhas.append(f"## {ref['id']} — {ref['autores']} ({ref['ano']})")
        linhas.append(f"**Título declarado:** {ref['titulo']}")
        if res["status"] != "ok":
            linhas.append(f"- Status: **{res['status']}** — {res.get('erro','')}")
            linhas.append("")
            continue
        for i, c in enumerate(res["candidatos"], 1):
            linhas.append(f"{i}. `{c['doi']}` — {c['titulo'][:110]} — *{c['veiculo']}* — {c['ano']} — v.{c['volume']} n.{c['numero']} p.{c['paginas']}")
        linhas.append("")
    OUT_MD.write_text("\n".join(linhas), encoding="utf-8")
    print(f"OK: {OUT_JSON} e {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
