# SPEC-907 — Títulos reais dos fragmentos expandidos de Molambudos

## Objetivo
Preencher corretamente os títulos dos fragmentos expandidos que ainda aparecem com identificadores genéricos no manifesto e nos artefatos LaTeX/PDF.

## Problema
Os fragmentos abaixo possuem título real na primeira linha dos arquivos Markdown (`## ID — Título`), mas o `network/manifest.json` registra o campo `title` como o próprio ID, por exemplo `MEM-27`, `DOC-20`, `LUC-13`, `CONT-14`. Isso faz o cabeçalho de fragmento e o `Índice dos Fragmentos` exibirem títulos genéricos.

## Escopo
Corrigir os títulos dos seguintes grupos:

- `CONT-14` a `CONT-26`;
- `LUC-13` e `LUC-14`;
- `DOC-20` a `DOC-28`;
- `MEM-27` a `MEM-34`.

## Requisitos
1. O `network/manifest.json` deve conter os títulos reais desses 32 fragmentos.
2. O `build_latex.py` deve ser resiliente: se o manifesto trouxer título vazio ou igual ao ID, deve extrair o título da primeira linha Markdown `## ID — Título`.
3. O `Índice dos Fragmentos` deve exibir os títulos reais.
4. As seções de abertura de cada fragmento devem exibir os títulos reais.
5. O PDF deve compilar sem erro fatal.

## Critérios de aceitação
- Não deve haver no `content/fragment-index.tex` entradas como `MEM-27 --- MEM-27`, `DOC-20 --- DOC-20`, `LUC-13 --- LUC-13` ou `CONT-14 --- CONT-14`.
- Os títulos reais extraídos dos `.md` devem aparecer no `fragment-index.tex` e nas partes correspondentes.
- `main.pdf` deve ser regenerado com sucesso.
