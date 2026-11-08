# Build do PDF

O PDF `LIVRO_3000_LAUDAS.pdf` é versionado neste repositório. Para recompilar:

```bash
./educacao_quantica_bohm/livro_pixel/build_pdf.sh
```

O script:

1. verifica `python3`, `pandoc` e `weasyprint`;
2. cria `.venv-pdf` com `--system-site-packages` se ele não existir;
3. instala `pyphen==0.16.0` com dicionários completos, inclusive `pt_BR`;
4. executa `build_pixel_fast.py`, que prefere `.venv-pdf/bin/python -m weasyprint`.

## Por que o `.venv-pdf`

O `pyphen` do sistema pode ter apenas dicionários de inglês; sem o dicionário
`pt_BR`, a propriedade CSS `hyphens: auto` não hifeniza o livro. O venv local
não substitui o WeasyPrint do sistema: ele só garante o `pyphen` completo.

## Requisitos de sistema

- Python 3.12 ou superior;
- Pandoc 3.x;
- WeasyPrint 67.x com as bibliotecas de sistema (Pango, Cairo, GDK-Pixbuf).

## Saída

- `LIVRO_3000_LAUDAS.html`;
- `LIVRO_3000_LAUDAS.pdf` (3504 páginas na versão de 2026-11-08);
- PDF e HTML são gerados a partir de `secoes/`, `GJQ_RESULTADOS.md` e demais
  arquivos editoriais.

## Edição enxuta (piloto)

```bash
python3 educacao_quantica_bohm/livro_pixel/build_enxuta.py
```

Gera `EDICAO_ENXUTA_PILOTO.pdf`, `.epub` e `.html`: 12 módulos, 60 laudas N0,
12 figuras e 76 páginas em papel claro. O piloto remove a repetição de
micropráticas e converte links para seções não incluídas em texto. Ele não é a
edição final de 600–800 páginas nem substitui a obra de referência.
