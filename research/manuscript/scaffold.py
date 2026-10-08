# -*- coding: utf-8 -*-
"""Scaffold de workspace isolado por artigo (SPEC-935-R706, AC2)."""
from __future__ import annotations

import os

from research.manuscript.config import ArticleConfig

PREAMBULO_TEX = r"""\documentclass[12pt,a4paper,oneside]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazil]{babel}
\usepackage[top=3cm,bottom=2cm,left=3cm,right=2cm]{geometry}
\usepackage[alf]{abntex2cite}
\usepackage{setspace}
\onehalfspacing
\setlength{\parindent}{1.25cm}
\usepackage{indentfirst}
\usepackage[hidelinks]{hyperref}
\usepackage{url}
\usepackage{booktabs}
\begin{document}
% Conteúdo gerado pelo orquestrador/LLM. Preencher cada módulo em \input abaixo.
"""

MAIN_TEX_TAIL = r"""\bibliography{referencias}
\end{document}
"""

BIB_ESQUELETO = """% referencias.bib — esqueleto. Toda entrada exige DOI/metadados verificados
% em fonte primária (Crossref/SciELO) antes de ser citada. Sem DOI resolvível:
% marcar [NÃO VERIFICADA] ou remover.
"""

TRIAGEM_CABECALHO = ""


def scaffold_workspace(config: ArticleConfig, force: bool = False) -> dict:
    """Cria artigos/<slug>/ com main.tex, modulos/, .bib, triagem e README.

    Fail-closed: diretório existente sem force=True => erro explícito.
    Retorna dicionário com workspace e arquivos criados.
    """
    ws = os.path.join(config.saida_base, config.slug)
    if os.path.exists(ws) and not force:
        raise FileExistsError(f"workspace existente (use force=True para recriar): {ws}.")
    os.makedirs(os.path.join(ws, "modulos"), exist_ok=True)

    mod_inputs = "\n".join(f"\\input{{modulos/{m}}}" for m in config.modulos if m != "referencias")
    with open(os.path.join(ws, "main.tex"), "w", encoding="utf-8") as fh:
        fh.write(PREAMBULO_TEX + mod_inputs + "\n" + MAIN_TEX_TAIL)

    criados = ["main.tex"]
    for modulo in config.modulos:
        if modulo == "referencias":
            continue
        caminho = os.path.join(ws, "modulos", f"{modulo}.tex")
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write(f"% MODULO: {modulo}\n% Tipo: {config.tipo} | Norma: {config.norma}\n"
                     f"% [A PREENCHER pelo orquestrador/LLM]\n")
        criados.append(f"modulos/{modulo}.tex")

    with open(os.path.join(ws, "referencias.bib"), "w", encoding="utf-8") as fh:
        fh.write(BIB_ESQUELETO)
    criados.append("referencias.bib")

    with open(os.path.join(ws, "triagem.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(TRIAGEM_CABECALHO)
    criados.append("triagem.jsonl")

    with open(os.path.join(ws, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(
            f"# {config.titulo}\n\n- Autores: {'; '.join(config.autores)}\n"
            f"- Área: {config.area} | Nível: {config.nivel} | Tipo: {config.tipo}\n"
            f"- Norma: {config.norma} | Idioma: {config.idioma} | Alvo: {config.periodico_alvo or '[A DEFINIR]'}\n\n"
            "## Pendências\n\n- [ ] Preencher módulos\n- [ ] TCLE/ética quando houver participante\n"
            "- [ ] Auditar cada referência (DOI em fonte primária)\n- [ ] Gates: citações, força de alegação, artefatos\n"
        )
    criados.append("README.md")
    return {"workspace": ws, "slug": config.slug, "arquivos": criados, "total": len(criados)}
