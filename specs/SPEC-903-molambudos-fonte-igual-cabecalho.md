# SPEC-903 — Fonte da página igual à cor do cabeçalho em Molambudos

## Objetivo
Alterar a geração LaTeX de Molambudos para que a cor principal do texto de cada página/fragmento seja a mesma cor usada no cabeçalho central.

## Comportamento atual
Cada fragmento define:

- fundo próprio: `bgmem`, `bgdoc`, `bgluc`, `bgcont`;
- texto do corpo em cores `textmem`, `textdoc`, `textluc`, `textcont`;
- cabeçalho central em cores `titlemem`, `titledoc`, `titleluc`, `titlecont`.

## Comportamento desejado
O texto da página deve usar a mesma cor do cabeçalho:

- MEM: corpo e cabeçalho em `titlemem`;
- DOC: corpo e cabeçalho em `titledoc`;
- LUC: corpo e cabeçalho em `titleluc`;
- CONT: corpo e cabeçalho em `titlecont`.

## Arquivo-alvo
- `producao_cientifica/molambudos/build_latex.py`

## Critérios de aceitação
1. Os arquivos gerados `content/parte*.tex` não devem usar `\color{textmem}`, `\color{textdoc}`, `\color{textluc}` ou `\color{textcont}` como cor principal dos fragmentos.
2. Os arquivos gerados devem usar `\color{titlemem}`, `\color{titledoc}`, `\color{titleluc}` e `\color{titlecont}` no corpo dos fragmentos correspondentes.
3. O cabeçalho central deve continuar usando as mesmas cores `title*`.
4. O PDF deve ser regenerado e compilar sem erro fatal.
