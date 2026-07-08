# SPEC-906 — Títulos especiais uniformes e Índice dos Fragmentos em lista

## Objetivo
Padronizar a cor dos títulos especiais do PDF de Molambudos e formatar o `Índice dos Fragmentos` como uma lista LaTeX real.

## Problema
Os títulos gerados por `\chapter*` — por exemplo `Glossário`, `Notas Finais`, `Índice dos Fragmentos`, `Conteúdo` e `Nota do Arquivista` — não recebiam o mesmo tratamento visual dos capítulos numerados. Além disso, o `Índice dos Fragmentos` era composto por linhas manuais com `\noindent\hspace*`, não por uma estrutura de lista.

## Requisitos
1. Títulos de capítulos numerados e não numerados devem usar cor uniforme (`customgold`) e ornamento compatível.
2. `\chapter*` deve ser estilizado explicitamente via `\@makeschapterhead`.
3. Páginas especiais como Glossário, Notas Finais e Índice dos Fragmentos devem resetar a cor de rodapé/cabeçalho para `customgold`.
4. O `Índice dos Fragmentos` deve usar ambiente `list` com itens (`\item`) para cada fragmento.
5. O índice deve preservar agrupamento por tipo (`MEM`, `DOC`, `LUC`, `CONT`), título do fragmento e `\pageref`.

## Arquivo-alvo
- `producao_cientifica/molambudos/build_latex.py`

## Critérios de aceitação
- `misc/options.sty` deve conter redefinição de `\@makeschapterhead` com `\color{customgold}`.
- `content/fragment-index.tex` deve conter `\begin{list}` e itens com `\item`.
- `content/fragment-index.tex` não deve usar linhas antigas com `\noindent\hspace*{1em}` para os fragmentos.
- `content/glossario.tex`, `content/notas-finais.tex` e `content/fragment-index.tex` devem definir `\setrunningfootcolor{customgold}`.
- O PDF deve compilar sem erro fatal.
