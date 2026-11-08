#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Montagem rápida das 1000 laudas: Pandoc só no material de abertura,
laudas já são HTML e são concatenadas diretamente. Evita o parser lento
de 1000 fenced divs."""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SECOES = RAIZ / "secoes"
FICHAS = RAIZ / "fichas"
PARTES = RAIZ / "partes"
HTML = RAIZ / "LIVRO_3000_LAUDAS.html"
PDF = RAIZ / "LIVRO_3000_LAUDAS.pdf"


def fragmento_texto(texto: str) -> str:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("pandoc ausente")
    out = subprocess.run(
        [pandoc, "-", "-f", "markdown+fenced_divs+pipe_tables+raw_html",
         "-t", "html5"],
        input=texto, capture_output=True, text=True, check=True,
    )
    return out.stdout


def fragmento(md: Path) -> str:
    return fragmento_texto(md.read_text(encoding="utf-8"))


def parte_html(numero: int, nivel: int) -> str:
    """Abre uma parte dentro de um nível, com links e âncora próprios."""
    texto = (PARTES / f"parte_{numero:02d}.md").read_text(encoding="utf-8")
    deslocamento = nivel * 1000
    if deslocamento:
        texto = re.sub(
            r"L(\d{4})",
            lambda m: f"L{int(m.group(1)) + deslocamento:04d}",
            texto,
        )
        texto = re.sub(
            r"#l-(\d{4})",
            lambda m: f"#l-{int(m.group(1)) + deslocamento:04d}",
            texto,
        )
    texto = texto.replace(
        f"{{#parte-{numero}}}",
        f"{{#parte-{numero}-n{nivel}}}",
    )
    texto = texto.replace(
        "## O que você vai encontrar",
        f"## O que você vai encontrar {{#parte-{numero}-n{nivel}-oque}}",
    )
    texto = texto.replace(
        "## Nano-trilha",
        f"## Nano-trilha {{#parte-{numero}-n{nivel}-nano}}",
    )
    texto = texto.replace(
        "## Pergunta motriz da parte",
        f"## Pergunta motriz da parte {{#parte-{numero}-n{nivel}-pergunta}}",
    )
    inicio = (numero - 1) * 10 + 1
    fim = numero * 10
    meta = (
        f'<p class="parte-nivel">NÍVEL {nivel} · PASSAGEM {nivel + 1} DE 3 · '
        f'P{numero:02d} · C{inicio:03d}–C{fim:03d} · 100 LAUDAS</p>'
    )
    linhas = texto.splitlines()
    for i, linha in enumerate(linhas):
        if linha.startswith("# Parte "):
            linhas.insert(i + 1, "")
            linhas.insert(i + 2, meta)
            break
    return "\n".join(linhas)


def secao_html(path: Path) -> str:
    texto = path.read_text(encoding="utf-8")
    m = re.match(r"^:::\s*\{\.lauda\s+\.lente-([a-z]+)(?:\s+\.nivel-\d+)?\}\s*$", texto.splitlines()[0])
    if not m:
        raise ValueError(f"cabeçalho inesperado em {path}")
    lente = m.group(1)
    corpo = texto.split("\n", 1)[1]
    corpo = re.sub(r"\n:::\s*$", "", corpo)
    return f'<div class="lauda lente-{lente}">{corpo}</div>\n'


def limpar_ancoras_codigo(html: str) -> str:
    """Remove IDs de bloco de código repetidos entre fragmentos do Pandoc."""
    html = re.sub(r' id="cb\d+(?:-\d+)?"', "", html)
    html = re.sub(
        r'<a href="#cb\d+(?:-\d+)?" aria-hidden="true" tabindex="-1"></a>',
        "",
        html,
    )
    return html


def montar(limite: int | None = None) -> str:
    partes = [
        '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">',
        '<link rel="stylesheet" href="estilo_pixel.css">',
        '<title>3000 Laudas de Física Quântica: do bit ao todo — Bohm, onda piloto e informação quântica do fundamental ao PhD</title>',
        '<meta name="author" content="Marcelo Claro Laranjeira">',
        '<meta name="description" content="Física quântica; ensino; Bohm; computação quântica; tecnologia social">',
        '<meta name="keywords" content="física quântica, Bohm, onda piloto, informação quântica, Qiskit, PennyLane, Cirq, Tiangong, CIQuanta, educação">',
        '<meta name="generator" content="OpenCode Ecosystem Core">',
        '</head><body>',
    ]
    partes.append(fragmento(RAIZ / "abertura_capa.md"))
    arquitetura = RAIZ / "ARQUITETURA_LEITURA.md"
    if arquitetura.exists():
        partes.append(fragmento(arquitetura))
    sumario = RAIZ / "SUMARIO.md"
    if sumario.exists():
        partes.append(fragmento(sumario))
    historia = RAIZ / "HISTORIA_BOHM.md"
    if historia.exists():
        partes.append(fragmento(historia))
    autor = RAIZ / "SOBRE_O_AUTOR.md"
    if autor.exists():
        partes.append(fragmento(autor))
    partes.append(fragmento(RAIZ / "abertura.md"))
    trilhas = RAIZ / "TRILHAS_NIVEIS.md"
    if trilhas.exists():
        partes.append(fragmento(trilhas))
    ferramentas = RAIZ / "TRILHAS_FERRAMENTAS.md"
    if ferramentas.exists():
        partes.append(fragmento(ferramentas))
    for nome in ("MAPA.md", "GLOSSARIO_CHINES.md"):
        caminho = RAIZ / nome
        if caminho.exists():
            partes.append(fragmento(caminho))
    relatorio = RAIZ.parent / "dados_experimentos" / "RELATORIO_EXPERIMENTOS.md"
    if relatorio.exists():
        partes.append(fragmento(relatorio))
    anexo = RAIZ.parent / "ANEXO_QUALIS_A1.md"
    if anexo.exists():
        partes.append(fragmento(anexo))
    pratica_swap = RAIZ.parent / "PRATICA_SWAP_TEST.md"
    if pratica_swap.exists():
        partes.append(fragmento(pratica_swap))
    oficina = RAIZ / "OFICINA_SCRIPTS.md"
    if oficina.exists():
        partes.append(fragmento(oficina))
    calculo = RAIZ.parent / "CALCULO_MANUAL.md"
    if calculo.exists():
        partes.append(fragmento(calculo))
    laboratorio = RAIZ / "LABORATORIO_LEITOR.md"
    if laboratorio.exists():
        partes.append(fragmento(laboratorio))
    gjq = RAIZ / "GJQ_RESULTADOS.md"
    if gjq.exists():
        partes.append(fragmento(gjq))
    codigo_exp = RAIZ / "CODIGO_EXPERIMENTOS.md"
    if codigo_exp.exists():
        partes.append(fragmento(codigo_exp))
    lean = RAIZ / "LEAN_QUANTUM.md"
    if lean.exists():
        partes.append(fragmento(lean))
    for nome in (
        "AVALIACAO_EFICACIA.md",
        "PILOTO_SINTETICO.md",
        "PACOTE_PEER_REVIEW.md",
        "LEDGER_AFIRMACOES.md",
        "PROFUNDIDADE_CIENTIFICA.md",
        "APROFUNDAMENTO_QUANTICO.md",
        "NOTAS_PROFESSOR.md",
        "EDICAO_ENXUTA.md",
        "INTERNATIONAL_EDITION.md",
        "RELATORIO_REPETICOES.md",
    ):
        caminho = RAIZ / nome
        if caminho.exists():
            partes.append(fragmento(caminho))
    gabarito = RAIZ / "GABARITO.md"
    if gabarito.exists():
        partes.append(fragmento(gabarito))
    capitulo = RAIZ.parent / "CAPITULO_CEARA_PARAIBA_GJQ.md"
    if capitulo.exists():
        partes.append(fragmento(capitulo))
    bloch = RAIZ / "BLOCH_SUITE.md"
    if bloch.exists():
        partes.append(fragmento(bloch))
    total = 0
    for nivel in range(3):
        partes.append(fragmento(RAIZ / "niveis" / f"nivel_{nivel}.md"))
        for n in range(nivel * 1000 + 1, (nivel + 1) * 1000 + 1):
            if limite is not None and total >= limite:
                break
            if (n - nivel * 1000 - 1) % 100 == 0:
                parte = (n - nivel * 1000 - 1) // 100 + 1
                partes.append(fragmento_texto(parte_html(parte, nivel)))
            achados = sorted(SECOES.glob(f"{n:04d}_*.md"))
            if len(achados) != 1:
                raise FileNotFoundError(f"lauda {n}: {len(achados)} arquivos")
            partes.append(secao_html(achados[0]))
            total += 1
        if limite is not None and total >= limite:
            break

    if limite is None:
        partes.append(fragmento(RAIZ / "FICHAS.md"))
        for ficha in sorted(FICHAS.glob("F*.md")):
            partes.append(fragmento(ficha))
        dois = RAIZ.parent / "dados_referencias" / "RELATORIO_DOIS.md"
        if dois.exists():
            partes.append(fragmento(dois))
        partes.append(fragmento(RAIZ / "fecho.md"))
        licenca = RAIZ / "LICENCA.md"
        if licenca.exists():
            partes.append(fragmento(licenca))
    partes.append("</body></html>")
    return limpar_ancoras_codigo("\n".join(partes))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()

    html = montar(args.limit)
    HTML.write_text(html, encoding="utf-8")
    print(f"HTML: {HTML} ({len(html):,} caracteres)")

    if args.no_pdf:
        return 0

    # Preferir o venv local com pyphen completo (dicionário pt_BR) para
    # hifenização real; o pyphen do sistema pode ter só inglês.
    venv_pdf = RAIZ.parents[1] / ".venv-pdf" / "bin" / "python"
    if venv_pdf.exists():
        comando = [str(venv_pdf), "-m", "weasyprint", HTML.name, PDF.name]
    else:
        weasyprint = shutil.which("weasyprint")
        if not weasyprint:
            print("weasyprint ausente", file=sys.stderr)
            return 2
        comando = [weasyprint, HTML.name, PDF.name]
    subprocess.run(comando, cwd=RAIZ, check=True)
    print(f"PDF: {PDF} ({PDF.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())