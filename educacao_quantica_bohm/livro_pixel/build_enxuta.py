"""Compila o piloto da edição enxuta (12 módulos, 60 laudas) em PDF e EPUB.

O piloto é uma porta de entrada, não a obra de referência. Ele usa laudas N0
selecionadas, CSS claro para impressão e uma versão EPUB reflowable.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
LIVRO = RAIZ / "educacao_quantica_bohm" / "livro_pixel"
SECOES = LIVRO / "secoes"
NOTAS = LIVRO / "NOTAS_PROFESSOR.md"
HTML = LIVRO / "EDICAO_ENXUTA_PILOTO.html"
HTML_EPUB = LIVRO / "EDICAO_ENXUTA_PILOTO_EPUB.html"
PDF = LIVRO / "EDICAO_ENXUTA_PILOTO.pdf"
EPUB = LIVRO / "EDICAO_ENXUTA_PILOTO.epub"
PY = RAIZ / ".venv-pdf" / "bin" / "python"

MODULOS = [
    ("Módulo 1 — Diferença e medida",
     "Do bit à medida: contar, tabular e comparar. Produto: caderno de counts.",
     ["0001", "0002", "0003", "0004", "0010"]),
    ("Módulo 2 — Amplitude e probabilidade",
     "A conta que sustenta a previsão. Produto: probabilidade e erro padrão.",
     ["0021", "0022", "0023", "0024", "0030"]),
    ("Módulo 3 — Fase e interferência",
     "O sinal que muda o resultado. Produto: diagrama H–Z–H.",
     ["0061", "0062", "0063", "0064", "0070"]),
    ("Módulo 4 — Emaranhamento e Bell",
     "Correlação que não é cópia. Produto: tabela CHSH.",
     ["0081", "0082", "0083", "0084", "0090"]),
    ("Módulo 5 — Portas e circuitos",
     "A receita do estado. Produto: circuito no papel.",
     ["0201", "0202", "0203", "0204", "0210"]),
    ("Módulo 6 — GHZ e QASM",
     "Escala e linguagem. Produto: QASM comentado.",
     ["0261", "0262", "0263", "0264", "0270"]),
    ("Módulo 7 — Ferramentas",
     "Python, Qiskit e nuvem. Produto: script rodando.",
     ["0301", "0302", "0303", "0304", "0310"]),
    ("Módulo 8 — Bloch e amostragem",
     "Visualizar e estimar. Produto: gráfico de Bloch.",
     ["0371", "0372", "0373", "0374", "0380"]),
    ("Módulo 9 — Hardware e ruído",
     "O que o chip acrescenta. Produto: task ID e calibração.",
     ["0401", "0402", "0403", "0404", "0410"]),
    ("Módulo 10 — VQC e acurácia",
     "Aprender com poucos pontos. Produto: 4/4 e limite.",
     ["0501", "0502", "0503", "0504", "0510"]),
    ("Módulo 11 — Ética e sociedade",
     "Quem ganha, quem perde. Produto: matriz de risco.",
     ["0801", "0802", "0803", "0804", "0810"]),
    ("Módulo 12 — Projeto final",
     "Pergunta, evidência e limite. Produto: 2 páginas + código.",
     ["0901", "0902", "0903", "0904", "0910"]),
]


FIGURAS_MODULO = [
    ("fig09_probabilidades.png", "Probabilidades de medida: a amostra e a distribuição."),
    ("fig09_probabilidades.png", "A mesma distribuição, lida como probabilidade."),
    ("fig02_interferencia.png", "Interferência: fase e padrão."),
    ("fig11_emaranhamento.png", "Emaranhamento: correlação sem cópia local."),
    ("fig07_qiskit.png", "Circuito de Bell desenhado no Qiskit."),
    ("fig12_ghz4_resultados.png", "GHZ de 4 qubits: populações medidas."),
    ("fig08_tres_frameworks.png", "As três bibliotecas e a mesma pergunta."),
    ("fig10_bloch.png", "Esfera de Bloch: estado, não só bit."),
    ("fig23_calibracao.png", "Calibração: T1, T2, leitura e ruído."),
    ("fig13_vqc_xor.png", "VQC: quatro pontos e o limite da amostra."),
    ("fig04_dialogo.png", "Diálogo: suposições, escuta e consequências."),
    ("fig14_escada_desafios.png", "A escada do teste real: do fácil ao research-grade."),
]


def lauda_html(codigo: str) -> str:
    caminho = next(SECOES.glob(f"{codigo}_*.md"))
    texto = caminho.read_text(encoding="utf-8")
    match = re.match(r"^::: \{\.lauda ([^}]+)\}\n", texto)
    if not match:
        raise ValueError(f"lauda sem fenced div: {caminho}")
    classes = match.group(1).replace(".", "")
    texto = texto.replace(match.group(0), f'<div class="lauda {classes}">\n', 1)
    texto = re.sub(r"\n:::\s*$", "\n</div>\n", texto)
    texto = re.sub(r'<a class="gab" href="#g-\d+">(\[G\d+\])</a>', r'<span class="gab">\1</span>', texto)
    texto = re.sub(r'<a class="ficha-link" href="#f-\d+">(\[F\d+\])</a>', r'<span class="ficha-link">\1</span>', texto)
    # O piloto não inclui oficina/código/gabarito completos: links internos viram texto.
    texto = re.sub(r'<a href="#[^"]+">(.*?)</a>', r'<span>\1</span>', texto, flags=re.S)
    texto = re.sub(r'<img class="ico[^"]*"[^>]*>', "", texto)
    texto = re.sub(r'<div class="xp">.*?</div>\n?', "", texto, flags=re.S)
    return texto


def notas_html() -> str:
    resultado = subprocess.run(
        ["pandoc", str(NOTAS), "-f", "markdown", "-t", "html"],
        capture_output=True, text=True, check=True,
    )
    return f'<section class="notas">{resultado.stdout}</section>'


def main() -> int:
    partes = [
        '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">',
        '<link rel="stylesheet" href="estilo_print.css">',
        '<title>Do Bit ao Todo — Edição Enxuta (piloto)</title>',
        '</head><body>',
        '<section class="capa">',
        '<p class="meta">EDIÇÃO ENXUTA · PILOTO · 12 MÓDULOS · 60 LAUDAS</p>',
        '<h1>Do Bit ao Todo</h1>',
        '<p class="sub">3000 Laudas de Física Quântica<br>do fundamental ao PhD</p>',
        '<p class="meta">Marcelo Claro Laranjeira</p>',
        '<p class="selo">CC BY-NC-SA 4.0 · código MIT</p>',
        '<p class="meta" style="margin-top:18mm">Este piloto seleciona 60 laudas N0 e remove a repetição de micropráticas.<br>'
        'A obra de referência completa continua disponível em PDF.</p>',
        '</section>',
    ]
    for indice, (titulo, descricao, codigos) in enumerate(MODULOS):
        partes.append(f'<section class="modulo"><h1>{titulo}</h1><p>{descricao}</p>')
        imagem, legenda = FIGURAS_MODULO[indice]
        partes.append(
            f'<figure class="modulo-fig"><img src="../livro/figuras_geradas/{imagem}" '
            f'alt="{legenda}"><figcaption>{legenda}</figcaption></figure>'
        )
        partes.append('</section>')
        for codigo in codigos:
            partes.append(lauda_html(codigo))
    partes.append(notas_html())
    partes.append(
        '<section class="licenca"><h1>Licença, fontes e limite</h1>'
        '<p>Texto: CC BY-NC-SA 4.0. Código: MIT. As figuras e os dados mantêm a licença da edição de referência.</p>'
        '<p>Este piloto não é peer review, não mede eficácia e não substitui a obra completa. '
        'As 100 fichas e o gabarito integral estão na edição de referência.</p>'
        '</section>'
    )
    partes.append("</body></html>")
    html = "\n".join(partes)
    HTML.write_text(html, encoding="utf-8")
    HTML_EPUB.write_text(html.replace('<link rel="stylesheet" href="estilo_print.css">', ""), encoding="utf-8")
    if "--html-only" in sys.argv:
        print(f"HTML: {HTML} ({HTML.stat().st_size:,} bytes)")
        return 0

    subprocess.run(
        [str(PY), "-m", "weasyprint", HTML.name, PDF.name],
        cwd=LIVRO, check=True,
    )
    subprocess.run(
        ["pandoc", str(HTML_EPUB), "-o", str(EPUB),
         "--css", str(LIVRO / "estilo_epub.css"),
         "--metadata", "title=Do Bit ao Todo — Edição Enxuta (piloto)",
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
