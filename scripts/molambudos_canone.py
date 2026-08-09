#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificador de coerência factual de Molambudos (SPEC-935-R406).

Até este ciclo, a checagem de contradições era **reativa**: os defeitos
apareciam por acaso, ao medir outra coisa. Foi assim que se descobriu que a
edição chinesa matava Oliveira em 1989 e que a portuguesa o matava em 1981 ---
enquanto o resto da obra o tem desaparecido em 1979 e vivo até 2026.

Um livro-arquivo que se apresenta como perícia fiel não pode errar sobre os
próprios fatos: é o leitor atento --- exatamente o que esta obra cultiva ---
quem bate na contradição.

Este script fixa os fatos-âncora do cânone e verifica, nas três edições:

1. **Fatos afirmados**: cada âncora tem de aparecer em todas as edições.
2. **Fatos proibidos**: afirmações que contradizem o cânone não podem aparecer
   em nenhuma.
3. **Paridade de datas**: um ano citado numa edição tem de existir nas outras.

    python3 -m scripts.molambudos_canone            # relatório
    python3 -m scripts.molambudos_canone --json     # saída estruturada

Sai com código 1 se houver qualquer violação.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"
EDICOES = {"pt": "fragmentos", "en": "en/fragmentos", "zh": "zh/fragmentos"}

# Ano isolado: `\b` não serve porque em chinês o ano vem colado a 年, que o
# módulo `re` trata como caractere de palavra — foi assim que uma medição
# anterior "perdeu" 17 anos na edição chinesa.
ANO_RE = re.compile(r"(?<!\d)(1[89]\d{2}|20[0-4]\d)(?!\d)")

# --- Fatos que DEVEM aparecer em todas as edições ---------------------------
# (rótulo, {edição: padrão}). O padrão é regex; o teste é presença.
AFIRMADOS: list[tuple[str, dict[str, str]]] = [
    ("entidade nasce em 1853", {e: r"1853" for e in EDICOES}),
    ("Joaquim morre em 1979", {e: r"1979" for e in EDICOES}),
    ("Colônia fecha em 1980", {e: r"1980" for e in EDICOES}),
    ("investigação de Lúcia em 2026", {e: r"2026" for e in EDICOES}),
    ("ciclo de 62", {e: r"(?<!\d)62(?!\d)" for e in EDICOES}),
    ("Oliveira desaparece, não morre", {
        "pt": r"desapareceu em 13 de junho de 1979",
        "en": r"disappeared on 13 June 1979",
        "zh": r"1979年6月13日失踪",
    }),
    ("leitor é o paciente 1.263", {
        "pt": r"1\.263", "en": r"1,263", "zh": r"1,263",
    }),
    ("Joaquim nasce em 1907", {e: r"1907" for e in EDICOES}),
    ("Joaquim entra no Colônia em 1917", {e: r"1917" for e in EDICOES}),
    ("Joaquim morre aos 72", {e: r"(?<!\d)72(?!\d)" for e in EDICOES}),
    ("Oliveira entrega o diário aos 81", {e: r"(?<!\d)81(?!\d)" for e in EDICOES}),
    ("CRM de Lúcia", {e: r"CRM[- ]?MG\s*28[.,]391" for e in EDICOES}),
    ("CRM de Oliveira", {e: r"CRM[- ]?MG\s*4[.,]892" for e in EDICOES}),
    ("CRM do legista Álvaro Torres", {e: r"CRM[- ]?MG\s*3[.,]117" for e in EDICOES}),
]

# Registros profissionais: um número por pessoa, sem colisão entre elas.
REGISTROS = {"28.391": "Dra. Lúcia Mendes", "4.892": "Dr. Heitor Oliveira",
             "3.117": "Dr. Álvaro Torres (legista)"}

# --- Fatos PROIBIDOS: contradizem o cânone ----------------------------------
PROIBIDOS: list[tuple[str, str, str]] = [
    ("Oliveira morto em 1981", r"(?<!\d)1981(?!\d)",
     "o cânone é desaparecimento em 13/jun/1979 sem corpo; DOC-25 afirma que ele "
     "'não desapareceu, foi guardado', e DOC-26 o tem escrevendo até 2026"),
    ("Oliveira morto em 1989", r"(?<!\d)1989(?!\d)",
     "mesma contradição; a data não existe em nenhum outro ponto da obra"),
    ("leitor tratado pelo número de Oliveira", r"1[.,]261\s*(?:é você|is you)",
     "1.261 é o Dr. Heitor Oliveira (DOC-16 o assina); o leitor é 1.263"),
    ("Lúcia com registro de psicóloga", r"CRP[- ]?(?:MG|04)",
     "decisão do autor no R398: Lúcia é psiquiatra forense, CRM-MG 28.391"),
]


def _corpus(edicao: str) -> dict[str, str]:
    base = BOOK / EDICOES[edicao]
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(base.rglob("*.tex"))}


def verificar() -> dict:
    corpora = {e: _corpus(e) for e in EDICOES}
    juntos = {e: "\n".join(v.values()) for e, v in corpora.items()}
    problemas: list[dict] = []

    for rotulo, padroes in AFIRMADOS:
        for edicao, padrao in padroes.items():
            if not re.search(padrao, juntos[edicao]):
                problemas.append({
                    "tipo": "fato ausente", "fato": rotulo,
                    "edicao": edicao, "detalhe": f"padrão {padrao!r} não encontrado",
                })

    for rotulo, padrao, porque in PROIBIDOS:
        for edicao in EDICOES:
            atingidos = [n for n, t in corpora[edicao].items() if re.search(padrao, t)]
            if atingidos:
                problemas.append({
                    "tipo": "contradição", "fato": rotulo, "edicao": edicao,
                    "arquivos": sorted(atingidos), "porque": porque,
                })

    crm_re = re.compile(r"CRM[- ]?MG\s*([\d.,]+)")
    for edicao in EDICOES:
        vistos = {m.replace(",", ".").rstrip(".") for m in crm_re.findall(juntos[edicao])}
        intrusos = sorted(vistos - set(REGISTROS))
        if intrusos:
            problemas.append({
                "tipo": "registro desconhecido", "fato": "CRM fora do cânone",
                "edicao": edicao, "detalhe": f"encontrados: {intrusos}; canônicos: {sorted(REGISTROS)}",
            })

    anos = {e: Counter(ANO_RE.findall(juntos[e])) for e in EDICOES}
    for ano in sorted(set().union(*[set(a) for a in anos.values()])):
        presentes = [e for e in EDICOES if anos[e][ano]]
        if len(presentes) != len(EDICOES):
            ausentes = [e for e in EDICOES if e not in presentes]
            problemas.append({
                "tipo": "data sem paridade", "fato": f"ano {ano}",
                "edicao": ",".join(ausentes),
                "detalhe": f"presente em {','.join(presentes)}, ausente em {','.join(ausentes)}",
            })

    return {
        "fragmentos_por_edicao": {e: len(v) for e, v in corpora.items()},
        "fatos_afirmados": len(AFIRMADOS),
        "fatos_proibidos": len(PROIBIDOS),
        "anos_distintos": len(set().union(*[set(a) for a in anos.values()])),
        "problemas": problemas,
        "ok": not problemas,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    r = verificar()
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0 if r["ok"] else 1

    print(f"fragmentos: {r['fragmentos_por_edicao']}")
    print(f"fatos-âncora afirmados: {r['fatos_afirmados']} | proibidos: {r['fatos_proibidos']}"
          f" | anos distintos: {r['anos_distintos']}")
    if r["ok"]:
        print("\ncoerência factual: sem contradições nas três edições")
        return 0
    print(f"\n{len(r['problemas'])} problema(s):")
    for x in r["problemas"]:
        print(f"  [{x['tipo']}] {x['fato']} — edição {x['edicao']}")
        if x.get("arquivos"):
            print(f"      arquivos: {', '.join(x['arquivos'])}")
        if x.get("porque"):
            print(f"      porquê: {x['porque']}")
        if x.get("detalhe"):
            print(f"      {x['detalhe']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
