#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Índice de Fragmentos: verificação e geração a partir do corpus (SPEC-935-R407).

Num livro-hipertexto o Índice de Fragmentos não é enfeite: é o instrumento com
que o leitor localiza um fragmento pelo nome. Ele estava mantido à mão em
quatro arquivos independentes (`main.tex`, `en/main_en.tex`, `zh/main_zh.tex`,
`tri/main_tri.tex`) e divergiu:

* a edição inglesa listava 73 dos 84 fragmentos --- faltavam DOC-20 a DOC-27
  (incluindo ``O Homem do Pano Preto''), LUC-13, LUC-14 e MEM-27;
* a chinesa faltava MEM-27; a trilíngue faltava CONT-08 a CONT-13 e MEM-27;
* o rótulo de DOC-26 ainda dizia **1981** em zh e tri --- o ano que o R406
  removeu do corpus por contradizer o cânone;
* DOC-09 aparecia como ``Escala 1.261'' em en/zh/tri: 1.261 é Oliveira, e o
  fragmento é a escala do **1.263**, o leitor;
* MEM-27 tinha três títulos diferentes, um por edição, e em português repetia
  o título de MEM-26;
* as contagens declaradas por parte não batiam com as entradas listadas.

A causa é estrutural: quatro cópias manuais da mesma informação. A correção é
derivar as três traduções da edição de referência --- ordem e rótulos do
português, títulos lidos do próprio fragmento de cada idioma.

    python3 -m scripts.molambudos_indice verificar   # sai != 0 se divergir
    python3 -m scripts.molambudos_indice gerar       # reescreve en, zh e tri
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"

MAINS = {
    "pt": ("main.tex", "fragmentos"),
    "en": ("en/main_en.tex", "en/fragmentos"),
    "zh": ("zh/main_zh.tex", "zh/fragmentos"),
    "tri": ("tri/main_tri.tex", None),
}

FRAGLINK_RE = re.compile(r"\\fraglink\{([A-Z]{3,4}-[A-Za-z0-9-]+)\}\{(.*?)\}\{(.*?)\}\s*$", re.M)
FRAGLINKTRI_RE = re.compile(
    r"\\fraglinktri\{([A-Z]{3,4}-[A-Za-z0-9-]+)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}\s*$", re.M
)
TITULO_RE = re.compile(r"\\section\*\{\\textbf\{[^}]+\}\s*---\s*(.+?)\}\s*$", re.M)

# Cabeçalhos de parte. A contagem é calculada, não escrita à mão: era daí que
# vinham os "26 fragmentos" numa parte de 25.
PARTES = [
    ("Sertão", "The Sertão", "塞尔唐"),
    ("Colônia", "The Colony", "收容院"),
    ("Diário de Oliveira\\\\\\hspace*{2.5em}e Laudos",
     "Oliveira's Diary\\\\\\hspace*{2.5em}and Reports",
     "奥利维拉日记\\\\\\hspace*{2.5em}与鉴定报告"),
    ("Investigação Lúcia", "Lúcia's Investigation", "卢西亚调查"),
    ("Contaminação", "Contamination", "污染"),
]

# Rótulos que não são ano. Anos e intervalos (1979, 1920--1930) passam iguais.
ROTULOS = {
    "Daniela Arbex": ("Daniela Arbex", "达妮埃拉·阿尔贝克斯"),
    "Lúcia Mendes": ("Lúcia Mendes", "卢西亚·门德斯"),
    "Instrumento clínico": ("Clinical instrument", "临床工具"),
    "Padre José Inácio": ("Father José Inácio", "若泽·伊纳西奥神父"),
    "Joaquim, 1907--1979": ("Joaquim, 1907--1979", "若阿金，1907--1979"),
}


def _titulo(dir_frag: str, fid: str) -> str | None:
    for p in (BOOK / dir_frag).rglob(f"{fid}.tex"):
        m = TITULO_RE.search(p.read_text(encoding="utf-8"))
        if m:
            return m.group(1).strip()
    return None


def estrutura_pt() -> list[tuple[int, list[tuple[str, str]]]]:
    """Ordem canônica: as 5 partes do índice português, com (id, rótulo)."""
    texto = (BOOK / "main.tex").read_text(encoding="utf-8")
    partes: list[tuple[int, list[tuple[str, str]]]] = []
    cortes = [m.start() for m in re.finditer(r"\\subsection\*\{Parte \d", texto)]
    for i, ini in enumerate(cortes):
        fim = cortes[i + 1] if i + 1 < len(cortes) else texto.index("\\newpage", ini)
        entradas = [(m.group(1), m.group(3)) for m in FRAGLINK_RE.finditer(texto[ini:fim])]
        partes.append((i + 1, entradas))
    return partes


def _rotulo(rot: str, idioma: str) -> str:
    # O rótulo do português é a própria fonte: não se traduz de volta.
    if idioma == "pt" or not rot or re.fullmatch(r"\d{4}(--\d{4})?", rot):
        return rot
    traducao = ROTULOS.get(rot)
    if traducao is None:
        return rot
    return traducao[0] if idioma == "en" else traducao[1]


def _cabecalho(idioma: str, n: int, total: int, epilogo: bool) -> str:
    pt, en, zh = PARTES[n - 1]
    if idioma == "pt":
        extra = f"{total} fragmentos" + (" + Epílogo" if epilogo else "")
        return f"\\subsection*{{Parte {n} --- {pt} ({extra})}}"
    if idioma == "en":
        extra = f"{total} fragments" + (" + Epilogue" if epilogo else "")
        return f"\\subsection*{{Part {n} --- {en} ({extra})}}"
    if idioma == "zh":
        extra = f"{total}个碎片" + ("＋尾声" if epilogo else "")
        return f"\\subsection*{{第{'一二三四五'[n-1]}部 —— {zh}（{extra}）}}"
    extra_pt = f"{total} fragmentos" + (" + Epílogo" if epilogo else "")
    return (f"\\subsection*{{Parte {n} · Part {n} · 第{'一二三四五'[n-1]}部 --- "
            f"{pt} · {en} · {zh} ({extra_pt})}}")


def gerar_bloco(idioma: str, estrutura=None) -> str:
    linhas: list[str] = []
    for n, entradas in (estrutura or estrutura_pt()):
        epilogo = any(fid == "MEM-27" for fid, _ in entradas)
        linhas.append(_cabecalho(idioma, n, len(entradas), epilogo))
        linhas.append("{\\setlength{\\parskip}{0.15em}")
        for fid, rot in entradas:
            if idioma == "tri":
                t_pt = _titulo("fragmentos", fid)
                t_en = _titulo("en/fragmentos", fid)
                t_zh = _titulo("zh/fragmentos", fid)
                linhas.append(
                    f"\\fraglinktri{{{fid}}}{{{t_pt}}}{{{t_en}}}{{{t_zh}}}{{{_rotulo(rot, 'zh')}}}")
            else:
                t = _titulo(MAINS[idioma][1], fid)
                linhas.append(f"\\fraglink{{{fid}}}{{{t}}}{{{_rotulo(rot, idioma)}}}")
        linhas.append("}")
        linhas.append("")
    return "\n".join(linhas).rstrip() + "\n"


def _bloco_atual(idioma: str) -> tuple[str, int, int]:
    caminho = BOOK / MAINS[idioma][0]
    texto = caminho.read_text(encoding="utf-8")
    marca = {
        "pt": r"\\subsection\*\{Parte ",
        "en": r"\\subsection\*\{Part ",
        "zh": r"\\subsection\*\{第",
        # A trilíngue já teve cabeçalho começando por 第 e por "Parte".
        "tri": r"\\subsection\*\{(?:Parte |Part |第)",
    }[idioma]
    achado = re.search(marca, texto)
    if achado is None:
        raise SystemExit(f"não achei o início do índice em {MAINS[idioma][0]}")
    ini = achado.start()
    ult = list(re.finditer(r"\\fraglink(?:tri)?\{", texto))[-1].start()
    fim = texto.index("}", texto.index("\n", ult)) + 1
    fim = texto.index("\n", fim) + 1
    return texto, ini, fim


def verificar() -> list[str]:
    problemas: list[str] = []
    esperados = [fid for _, ents in estrutura_pt() for fid, _ in ents]
    for idioma in ("pt", "en", "zh", "tri"):
        texto = (BOOK / MAINS[idioma][0]).read_text(encoding="utf-8")
        if idioma == "tri":
            achados = [m.group(1) for m in FRAGLINKTRI_RE.finditer(texto)]
        else:
            achados = [m.group(1) for m in FRAGLINK_RE.finditer(texto)]
        faltam = [f for f in esperados if f not in achados]
        se_sobra = [f for f in achados if f not in esperados]
        if faltam:
            problemas.append(f"{idioma}: {len(faltam)} fragmento(s) fora do índice: {faltam}")
        if se_sobra:
            problemas.append(f"{idioma}: entradas sem fragmento: {se_sobra}")
        if achados != esperados and not faltam and not se_sobra:
            problemas.append(f"{idioma}: índice fora da ordem da edição de referência")

        # Título do índice tem de bater com o do próprio fragmento: era assim
        # que DOC-09 anunciava a escala do "1.261" (Oliveira) em vez do 1.263
        # (o leitor), e que MEM-27 tinha um título por edição.
        if idioma == "tri":
            for m in FRAGLINKTRI_RE.finditer(texto):
                for i, dir_frag in enumerate(("fragmentos", "en/fragmentos", "zh/fragmentos")):
                    real = _titulo(dir_frag, m.group(1))
                    if real and m.group(2 + i) != real:
                        problemas.append(f"tri/{m.group(1)} [{dir_frag}]: índice diz "
                                         f"{m.group(2 + i)!r}, fragmento diz {real!r}")
        else:
            for m in FRAGLINK_RE.finditer(texto):
                real = _titulo(MAINS[idioma][1], m.group(1))
                if real and m.group(2) != real:
                    problemas.append(
                        f"{idioma}/{m.group(1)}: índice diz {m.group(2)!r}, fragmento diz {real!r}")

        # Contagem declarada no cabeçalho tem de bater com as entradas listadas
        # logo abaixo dele. Era daí que vinha "26 fragmentos" numa parte de 25.
        cortes = [m.start() for m in re.finditer(r"\\subsection\*\{(?:Parte |Part |第)", texto)]
        for i, ini in enumerate(cortes):
            fim = cortes[i + 1] if i + 1 < len(cortes) else len(texto)
            trecho = texto[ini:fim]
            m = re.search(r"[（(](\d+)\s*(?:fragmento|fragment|个碎片)", trecho)
            if not m:
                continue
            listadas = len(re.findall(r"\\fraglink(?:tri)?\{", trecho))
            if int(m.group(1)) != listadas:
                problemas.append(
                    f"{idioma}/parte {i+1}: cabeçalho declara {m.group(1)}, lista {listadas}")
    return problemas


def gerar() -> list[str]:
    # A estrutura é lida uma única vez, antes de qualquer escrita: o português
    # é a fonte da ordem e dos rótulos, e também vai ser reescrito.
    estrutura = estrutura_pt()
    tocados = []
    for idioma in ("pt", "en", "zh", "tri"):
        texto, ini, fim = _bloco_atual(idioma)
        novo = texto[:ini] + gerar_bloco(idioma, estrutura) + texto[fim:]
        if novo != texto:
            (BOOK / MAINS[idioma][0]).write_text(novo, encoding="utf-8")
            tocados.append(MAINS[idioma][0])
    return tocados


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("acao", choices=["verificar", "gerar"])
    args = p.parse_args(argv)

    if args.acao == "gerar":
        tocados = gerar()
        print("índice regenerado em: " + (", ".join(tocados) if tocados else "(nada mudou)"))

    problemas = verificar()
    total = len(estrutura_pt())
    n = sum(len(e) for _, e in estrutura_pt())
    print(f"partes: {total} | fragmentos na edição de referência: {n}")
    if not problemas:
        print("índice íntegro nas quatro edições")
        return 0
    print(f"\n{len(problemas)} divergência(s):")
    for x in problemas:
        print(f"  {x}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
