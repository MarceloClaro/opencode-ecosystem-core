# SPEC-905 — Redução da tabela de diagnóstico e paginação inferior visível

## Objetivo
Corrigir dois pontos visuais no PDF LaTeX de Molambudos:

1. Reduzir a tabela curta de `DOC-21 — Tabela Comparativa de Diagnósticos`, vista na página indicada pelo usuário como 195, para que siga o padrão legível das demais tabelas e não seja esticada artificialmente.
2. Tornar a cor da fonte das paginações inferiores sempre visível sobre os fundos escuros/temáticos.

## Problema
- O conversor Markdown→LaTeX estava aplicando `\resizebox{\textwidth}{!}` a todas as tabelas, inclusive tabelas curtas de 2 colunas. Isso amplia tabelas pequenas e torna visualmente desproporcional o quadro com linhas `Critério`, `Diagnóstico`, `Etiologia`, `Prognóstico`, `Destino`.
- A paginação inferior usava `\thepage` sem cor explícita, podendo herdar uma cor pouco visível em páginas com fundo escuro.

## Requisitos
1. Tabelas de 2 colunas devem ser renderizadas sem `resizebox`, em tamanho reduzido/normal, centralizadas e com colunas `p{...}` para quebra de linha.
2. Tabelas de 3+ colunas podem continuar usando redimensionamento para caber na página.
3. A paginação inferior deve usar cor explícita de alto contraste/visibilidade.
4. Em páginas de fragmento, a paginação inferior deve acompanhar a cor temática do fragmento (`titlemem`, `titledoc`, `titleluc`, `titlecont`).
5. Páginas `plain` de abertura de capítulo também devem mostrar paginação inferior colorida.

## Arquivos-alvo
- `producao_cientifica/molambudos/build_latex.py`
- Arquivos LaTeX regenerados em `producao_cientifica/molambudos/output/latex-molambudos/`

## Critérios de aceitação
- A tabela final de `DOC-21` não deve conter `\resizebox{\textwidth}{!}` imediatamente antes do quadro de 2 colunas `Critério / Sua vez`.
- A tabela deve usar ambiente `center` e colunas `p{...}`.
- `misc/options.sty` deve definir paginação inferior com cor explícita.
- `content/parte*.tex` deve atualizar a cor da paginação por fragmento com `\setrunningfootcolor{title...}`.
- O PDF deve compilar sem erro fatal.
