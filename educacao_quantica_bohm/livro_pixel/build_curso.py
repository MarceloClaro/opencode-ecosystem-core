"""Compila a edição de curso expandida (12 módulos, 600 laudas) em PDF e EPUB.

Quatro conceitos por módulo, um em N0, um em N1, um em N2 e um em N1. Cada
conceito entra com as dez lentes. O gabarito e as 100 fichas completas ficam
na edição de referência; aqui entram apenas as notas ao professor e o
apêndice de aprofundamento.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from build_enxuta import FIGURAS_MODULO, lauda_html, notas_html

RAIZ = Path(__file__).resolve().parents[2]
LIVRO = RAIZ / "educacao_quantica_bohm" / "livro_pixel"
HTML = LIVRO / "EDICAO_CURSO_600.html"
HTML_EPUB = LIVRO / "EDICAO_CURSO_600_EPUB.html"
PDF = LIVRO / "EDICAO_CURSO_600.pdf"
EPUB = LIVRO / "EDICAO_CURSO_600.epub"
PY = RAIZ / ".venv-pdf" / "bin" / "python"

# (título, descrição, [(nível, número do conceito), ...])
MODULOS = [
    ("Módulo 1 — Diferença e medida",
     "Do bit à medida: contar, tabular e comparar.",
     [(0, 1), (1, 2), (2, 4), (1, 5), (1, 75)]),
    ("Módulo 2 — Amplitude e probabilidade",
     "A conta que sustenta a previsão.",
     [(0, 3), (1, 6), (2, 30), (1, 63), (1, 68)]),
    ("Módulo 3 — Fase e interferência",
     "O sinal que muda o resultado.",
     [(0, 7), (1, 8), (2, 22), (1, 23), (1, 70)]),
    ("Módulo 4 — Emaranhamento e Bell",
     "Correlação que não é cópia.",
     [(0, 9), (1, 10), (2, 26), (1, 14), (1, 15)]),
    ("Módulo 5 — Portas e circuitos",
     "A receita do estado.",
     [(0, 21), (1, 24), (2, 25), (1, 64), (1, 36)]),
    ("Módulo 6 — GHZ e QASM",
     "Escala e linguagem.",
     [(0, 27), (1, 28), (2, 29), (1, 51), (1, 48)]),
    ("Módulo 7 — Ferramentas",
     "Python, Qiskit, PennyLane e GJQ.",
     [(0, 31), (1, 32), (2, 33), (1, 40), (1, 35)]),
    ("Módulo 8 — Bloch e amostragem",
     "Visualizar e estimar.",
     [(0, 38), (1, 37), (2, 39), (1, 34), (1, 67)]),
    ("Módulo 9 — Hardware e ruído",
     "O que o chip acrescenta.",
     [(0, 41), (1, 42), (2, 43), (1, 44), (1, 45)]),
    ("Módulo 10 — VQC e acurácia",
     "Aprender com poucos pontos.",
     [(0, 52), (1, 55), (2, 56), (1, 57), (1, 58)]),
    ("Módulo 11 — Ética e sociedade",
     "Quem ganha, quem perde.",
     [(0, 83), (1, 84), (2, 85), (1, 90), (1, 82)]),
    ("Módulo 12 — Projeto final",
     "Pergunta, evidência e limite.",
     [(0, 91), (1, 92), (2, 93), (1, 94), (1, 95)]),
]


def markdown_html(path: Path) -> str:
    return subprocess.run(
        ["pandoc", str(path), "-f", "markdown", "-t", "html"],
        capture_output=True, text=True, check=True,
    ).stdout


def laudas_do_conceito(nivel: int, conceito: int) -> list[str]:
    base = nivel * 1000 + (conceito - 1) * 10 + 1
    return [lauda_html(f"{codigo:04d}") for codigo in range(base, base + 10)]


def main() -> int:
    partes = [
        '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">',
        '<link rel="stylesheet" href="estilo_print.css">',
        '<title>Do Bit ao Todo — Edição de Curso</title>',
        '</head><body>',
        '<section class="capa">',
        '<p class="meta">EDIÇÃO DE CURSO · 12 MÓDULOS · 600 LAUDAS</p>',
        '<h1>Do Bit ao Todo</h1>',
        '<p class="sub">3000 Laudas de Física Quântica<br>do fundamental ao PhD</p>',
        '<p class="meta">Marcelo Claro Laranjeira</p>',
        '<p class="selo">CC BY-NC-SA 4.0 · código MIT</p>',
        '<p class="meta" style="margin-top:16mm">Seleção de 60 conceitos, cinco por módulo, com as dez lentes.<br>'
        'O gabarito e as 100 fichas completas permanecem na edição de referência.</p>',
        '</section>',
        '<section class="como-usar"><h1>Como usar esta edição</h1>'
        '<p>Cada módulo tem cinco conceitos: um em N0 (concreto), três em N1 (circuito e fórmula) '
        'e um em N2 (formalização e limite). Cada conceito entra com as dez lentes: '
        'ideia, analogia, prática, laboratório, erro, além, diálogo, ética, vida e checkpoint.</p>'
        '<p>O percurso sugerido é ler a lente <strong>ideia</strong>, fazer a <strong>prática</strong>, '
        'comparar com o <strong>laboratório</strong> e responder ao <strong>checkpoint</strong>. '
        'As lentes de diálogo, ética e vida podem ser usadas em roda ou como escrita breve.</p>'
        '<p><strong>O que não entra:</strong> o gabarito completo dos 100 checkpoints e as 100 fichas '
        'de evidência ficam na edição de referência. Esta edição traz as notas ao professor e o '
        'apêndice de aprofundamento.</p></section>',
    ]
    for indice, (titulo, descricao, selecao) in enumerate(MODULOS):
        partes.append(f'<section class="modulo"><h1>{titulo}</h1><p>{descricao}</p>')
        imagem, legenda = FIGURAS_MODULO[indice]
        partes.append(
            f'<figure class="modulo-fig"><img src="../livro/figuras_geradas/{imagem}" '
            f'alt="{legenda}"><figcaption>{legenda}</figcaption></figure>'
        )
        partes.append('</section>')
        for nivel, conceito in selecao:
            partes.extend(laudas_do_conceito(nivel, conceito))
    partes.append(notas_html())
    partes.append('<section class="aprofundamento">' + markdown_html(LIVRO / "APROFUNDAMENTO_QUANTICO.md") + '</section>')
    partes.append(
        '<section class="licenca"><h1>Licença, fontes e limite</h1>'
        '<p>Texto: CC BY-NC-SA 4.0. Código: MIT. Figuras e dados mantêm a licença da edição de referência.</p>'
        '<p>Esta edição de curso não é peer review, não mede eficácia e não substitui a obra completa. '
        'O gabarito e as fichas completas estão na referência.</p></section>'
    )
    partes.append("</body></html>")
    html = "\n".join(partes)
    HTML.write_text(html, encoding="utf-8")
    HTML_EPUB.write_text(html.replace('<link rel="stylesheet" href="estilo_print.css">', ""), encoding="utf-8")

    subprocess.run([str(PY), "-m", "weasyprint", HTML.name, PDF.name], cwd=LIVRO, check=True)
    subprocess.run(
        ["pandoc", str(HTML_EPUB), "-o", str(EPUB),
         "--css", str(LIVRO / "estilo_epub.css"),
         "--metadata", "title=Do Bit ao Todo — Edição de Curso",
         "--metadata", "lang=pt-BR",
         "--toc",
         "--resource-path", f"{LIVRO}:{LIVRO.parent / 'livro' / 'figuras_geradas'}"],
        check=True,
    )
    print(f"HTML: {HTML} ({HTML.stat().st_size:,} bytes)")
    print(f"PDF:  {PDF} ({PDF.stat().st_size:,} bytes)")
    print(f"EPUB: {EPUB} ({EPUB.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
