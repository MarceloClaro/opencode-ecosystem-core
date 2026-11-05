#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Insere marcadores LaTeX de resumo/abstract/referências nos Markdown.

Os blocos são ignorados na geração DOCX e aplicados apenas no PDF (XeLaTeX).
"""
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ARQUIVOS = [BASE / "01_ARTIGO_CORRIGIDO_ABNT.md", BASE / "02_ARTIGO_QUALIS_A1.md"]

BEGIN_RESUMO = "\n```{=latex}\n\\begin{resumo}\n```\n"
END_RESUMO = "\n```{=latex}\n\\end{resumo}\n```\n"
BEGIN_REFS = "\n```{=latex}\n\\begin{refs}\n```\n"
END_REFS = "\n```{=latex}\n\\end{refs}\n```\n"


def marcar(caminho: Path) -> None:
    texto = caminho.read_text(encoding="utf-8")
    if "\\begin{resumo}" in texto:
        print(f"já marcado: {caminho.name}")
        return
    for titulo, fim in (("**RESUMO**", "**Palavras-chave:**"), ("**ABSTRACT**", "**Keywords:**")):
        if titulo not in texto:
            raise SystemExit(f"{caminho.name}: título {titulo} ausente")
        texto = texto.replace(titulo + "\n", titulo + BEGIN_RESUMO, 1)
        texto = texto.replace("\n" + fim, END_RESUMO + "\n" + fim, 1)
    if "# REFERÊNCIAS" not in texto:
        raise SystemExit(f"{caminho.name}: seção de referências ausente")
    texto = texto.replace("# REFERÊNCIAS\n", "# REFERÊNCIAS" + BEGIN_REFS, 1)
    texto = texto.rstrip() + END_REFS
    caminho.write_text(texto, encoding="utf-8")
    print(f"OK: {caminho.name}")


for arquivo in ARQUIVOS:
    marcar(arquivo)
