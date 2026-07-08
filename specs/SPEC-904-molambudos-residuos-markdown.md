# SPEC-904 — Remoção de resíduos Markdown visíveis em Molambudos

## Objetivo
Remover do PDF/LaTeX final caracteres visíveis que sobraram da conversão Markdown, especialmente asteriscos (`*`) usados originalmente para itálico/negrito.

## Problema
Algumas passagens podem manter símbolos de Markdown no texto final quando a marcação está desbalanceada, dividida entre falas ou misturada a aspas. Esses símbolos aparecem como caracteres estranhos no livro impresso/PDF.

## Requisitos
1. O conversor `build_latex.py` deve tratar marcações Markdown balanceadas e resíduos soltos de `*`.
2. Resíduos de `*` não devem aparecer como texto visível nos arquivos `content/parte*.tex` gerados.
3. Não devem ser alterados comandos LaTeX legítimos com asterisco, como `\chapter*`, `\section*`, `\subsection*` e `\hspace*`.
4. A limpeza deve preservar itálicos e negritos quando a marcação Markdown estiver correta.
5. O projeto LaTeX deve ser regenerado e compilar sem erro fatal.

## Critérios de aceitação
- Busca automatizada nos `content/parte*.tex` não encontra asteriscos visíveis fora de comandos LaTeX estrelados conhecidos.
- O PDF `main.pdf` é regenerado com sucesso.
- Correções anteriores permanecem: `1260` não volta a ser associado a `666 × 2`; a fonte do corpo segue a cor do cabeçalho.
