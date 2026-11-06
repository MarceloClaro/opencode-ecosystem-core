#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compila o TCC completo em PDF e DOCX, com sumário e pré-textuais."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

BASE = Path(__file__).resolve().parent
TCC = BASE
CORPO_MD = TCC / "TCC_CORPO.md"
CORPO_TEX = TCC / "TCC_CORPO.tex"
PRETEXTUAL_TEX = TCC / "TCC_PRETEXTUAL.tex"
PRETEXTUAL_MD = TCC / "TCC_PRETEXTUAL.md"
WRAPPER = TCC / "tcc_wrapper.tex"
PDF = TCC / "TCC_MARCELO_AUTISMO_AH_SD.pdf"
DOCX = TCC / "TCC_MARCELO_AUTISMO_AH_SD.docx"
REF_DOCX = TCC / "templates" / "tcc_reference.docx"
SUMARIO_MD = TCC / "SUMARIO.md"


def rodar(cmd: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(cwd or TCC), text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(f"falhou: {cmd[0]}")


def envolver_tabelas(texto: str) -> str:
    """Coloca cada tabela em um grupo \\small para não estourar a margem."""
    linhas = texto.splitlines()
    saida: list[str] = []
    dentro = False
    for linha in linhas:
        if linha.startswith("|"):
            if not dentro:
                saida += ["", "```{=latex}", "\\begingroup\\small", "```", ""]
                dentro = True
            saida.append(linha)
        else:
            if dentro:
                saida += ["", "```{=latex}", "\\endgroup", "```", ""]
                dentro = False
            saida.append(linha)
    if dentro:
        saida += ["", "```{=latex}", "\\endgroup", "```", ""]
    return "\n".join(saida)


def gerar_corpo_tex() -> None:
    texto = envolver_tabelas(CORPO_MD.read_text(encoding="utf-8"))
    tmp = TCC / "_corpo_wrapped.md"
    tmp.write_text(texto, encoding="utf-8")
    rodar(["pandoc", str(tmp), "-t", "latex", "-o", str(CORPO_TEX),
           "--from=markdown+smart"])
    # URLs escritas como texto puro não quebram; envolver em \url{}.
    tex = CORPO_TEX.read_text(encoding="utf-8")
    def _wrap(m):
        bruto = m.group(1)
        url = bruto.rstrip(".,;")
        cauda = bruto[len(url):]
        url = url.replace("\\_", "_")
        return "\\url{" + url + "}" + cauda
    tex = re.sub(r"(https?://[^\s]+)", _wrap, tex)
    def _wrap_doi(m):
        bruto = m.group(1)
        doi = bruto.rstrip(".,;")
        cauda = bruto[len(doi):]
        return "\\url{" + doi + "}" + cauda
    tex = re.sub(r"(10\.\d{4,9}/[^\s}\]]+)", _wrap_doi, tex)
    CORPO_TEX.write_text(tex, encoding="utf-8")


def compilar_pdf() -> None:
    for _ in range(2):
        rodar(["xelatex", "-interaction=nonstopmode", "-halt-on-error",
               str(WRAPPER.name)])
    shutil.copyfile(WRAPPER.with_suffix(".pdf"), PDF)


def limpar_titulo(linha: str) -> str:
    linha = linha.replace("\\numberline {}", "").strip()
    linha = re.sub(r"\\ignorespaces", "", linha)
    linha = re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", linha)
    linha = linha.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", linha).strip()


def ler_toc() -> list[tuple[str, str]]:
    toc = WRAPPER.with_suffix(".toc")
    if not toc.exists():
        raise SystemExit("toc ausente; compile o PDF primeiro")
    entradas: list[tuple[str, str]] = []
    for linha in toc.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"\\contentsline \{(section|subsection)\}\{(.*)\}\{([^}]*)\}", linha)
        if not m:
            continue
        nivel, titulo, pagina = m.group(1), limpar_titulo(m.group(2)), m.group(3)
        entradas.append((nivel, titulo, pagina))
    return entradas


def gerar_sumario_md() -> None:
    entradas = ler_toc()
    linhas = ["| Título | Página |", "|---|---|"]
    for nivel, titulo, pagina in entradas:
        prefixo = "" if nivel == "section" else "&emsp;&emsp;"
        linhas.append(f"| {prefixo}{titulo} | {pagina} |")
    SUMARIO_MD.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"sumário: {len(entradas)} entradas")


def montar_pretextual_md() -> Path:
    texto = PRETEXTUAL_MD.read_text(encoding="utf-8")
    sumario = SUMARIO_MD.read_text(encoding="utf-8") if SUMARIO_MD.exists() else ""
    texto = texto.replace("<!-- SUMARIO -->", sumario)
    destino = TCC / "_pretextual_com_sumario.md"
    destino.write_text(texto, encoding="utf-8")
    return destino


def preparar_referencia_docx() -> None:
    REF_DOCX.parent.mkdir(exist_ok=True)
    origem = TCC / "templates" / "base_reference.docx"
    shutil.copyfile(origem, REF_DOCX)
    doc = Document(str(REF_DOCX))
    sec = doc.sections[0]
    sec.page_width = Cm(21)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.5)
    sec.left_margin = Cm(2.5)
    sec.bottom_margin = Cm(2.5)
    sec.right_margin = Cm(2.5)
    doc.save(str(REF_DOCX))


def centralizar_pretextual(doc: Document) -> None:
    em_resumo = False
    em_abstract = False
    em_lista = False
    for p in doc.paragraphs:
        txt = p.text.strip()
        if not txt:
            continue
        if txt == "RESUMO":
            em_resumo, em_abstract, em_lista = True, False, False
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.bold = True
            continue
        if txt == "ABSTRACT":
            em_resumo, em_abstract, em_lista = False, True, False
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.bold = True
            continue
        if txt.startswith("LISTA DE ABREVIATURAS"):
            em_resumo, em_abstract, em_lista = False, False, True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.bold = True
            continue
        if txt == "SUMÁRIO":
            em_resumo, em_abstract, em_lista = False, False, False
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.bold = True
            continue
        if txt.startswith("Palavras-chave:") or txt.startswith("Keywords:"):
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(6)
            continue
        if em_resumo or em_abstract:
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(0)
        elif em_lista:
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(0)


def centralizar_capa(doc: Document) -> None:
    for p in doc.paragraphs:
        if p.text.strip() == "RESUMO":
            break
        txt = p.text.strip()
        if txt.startswith("Trabalho de Conclusão de Curso"):
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Cm(8)
            p.paragraph_format.first_line_indent = Cm(0)
            continue
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if txt == "MARCELO CLARO LARANJEIRA" or txt.startswith("DUPLA EXCEPCIONALIDADE") \
                or txt == "FACUMINAS" or txt.startswith("Pós-graduação") \
                or txt == "Brasília" or txt == "2026":
            for r in p.runs:
                r.bold = True


def construir_docx() -> None:
    pretextual = montar_pretextual_md()
    completo = TCC / "_TCC_COMPLETO.md"
    completo.write_text(
        pretextual.read_text(encoding="utf-8") + "\n\n" + CORPO_MD.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    rodar([
        "pandoc", str(completo), "-o", str(DOCX),
        "--from=markdown+smart",
        "--reference-doc", str(REF_DOCX),
        "--metadata", "lang=pt-BR",
    ])
    doc = Document(str(DOCX))
    centralizar_capa(doc)
    centralizar_pretextual(doc)
    doc.save(str(DOCX))


def main() -> int:
    gerar_corpo_tex()
    compilar_pdf()
    gerar_sumario_md()
    preparar_referencia_docx()
    construir_docx()
    print("OK: PDF e DOCX do TCC gerados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
