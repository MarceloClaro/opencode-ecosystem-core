# SPEC-902 — Correção simbólica do número 1.260 em Molambudos

## Objetivo
Corrigir a passagem de `CONT-11 — O Número` que associa incorretamente `1260` a `666 × 2`, preservando o tom apocalíptico e a função narrativa do número.

## Problema
A formulação atual afirma que `1260` é uma alternativa do número da Besta por derivação de `666 × 2`. Isso é matematicamente incorreto, pois `666 × 2 = 1332`.

## Requisito editorial
Substituir a associação matemática falsa por uma associação simbólica correta:

- `666` nomeia a Besta / marca da Besta.
- `1260` deve remeter ao tempo apocalíptico de domínio, perseguição ou testemunho, equivalente narrativamente a 42 meses / 1.260 dias.

## Arquivos-alvo
- `producao_cientifica/molambudos/fragments/content/cont-11.md`
- Artefatos LaTeX regenerados em `producao_cientifica/molambudos/output/latex-molambudos/`

## Critérios de aceitação
1. Nenhum arquivo-fonte `.md` de Molambudos deve conter a expressão `666 × 2`.
2. `CONT-11 — O Número` deve manter o efeito de ameaça e obsessão numérica.
3. A nova frase deve deixar claro que `1260` não é o número da Besta, mas o tempo associado ao domínio/perseguição apocalíptica.
4. O projeto LaTeX deve ser regenerado e compilar sem erro fatal.
5. A saída LaTeX final não deve conter a expressão incorreta `666 × 2`.

## Verificação
- Busca textual por `666 × 2`, `666*2` e `tradução alternativa` nos fontes e na saída LaTeX.
- Compilação de `main.tex` com `pdflatex -interaction=nonstopmode`.
