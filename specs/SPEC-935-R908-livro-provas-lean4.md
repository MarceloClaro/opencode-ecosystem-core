# SPEC-935-R908 — Fórmulas e deduções do livro verificadas com Lean 4

Status: concluída no escopo matemático local, com compilação real, auditoria de axiomas e PDF revisado. Não declara validação científica externa.

## Objetivo

Resolver a pendência de verificação formal do livro R901/R907. Inventariar as
famílias de fórmulas, explicitar hipóteses, demonstrar propriedades e cálculos
em Lean 4/Mathlib e vincular cada família aos trechos do livro.

## Contrato

- Usar Lean 4 e Mathlib com versões fixadas e registrar revisão, comandos,
  hashes das fontes e logs da execução real do compilador.
- Aceitar somente compilação bem-sucedida e auditoria de dependências de cada
  teorema. Recusar `sorryAx`, `sorry`, `admit`, axiomas locais e provas de
  proposições falsas. Os axiomas fundamentais da biblioteca ficam declarados.
- Distinguir dedução exata, intervalo racional demonstrado para aproximação,
  hipótese de modelagem e número obtido de observação. Não provar dados
  empíricos por substituição de constantes nem atribuir ao código Python uma
  equivalência que não foi demonstrada.
- Cobrir probabilidade/complemento, proporções e gates, PPV, contabilidade
  PRISMA, EMA, Amdahl, custos/taxas, reconciliação, seleção, Jaccard, utilidade
  e softmax, além de outras famílias localizadas no inventário independente.
- Contraexemplos e mutações devem ser recusados pelo compilador/gate; fonte
  alterada depois da verificação invalida o recibo.
- Atualizar o livro e a matriz enunciado–hipótese–teorema–fonte com o alcance
  efetivamente demonstrado; compilar e conferir o PDF existente.

## Entrega e verificação

Fontes em `livro-core/lean/`; verificador reexecutável em
`scripts/verify_book_lean.py`; testes `tests/test_r908_book_lean.py`;
matriz e recibo públicos em `docs/`. Não encerrar a pendência com mera análise
sintática ou instalação do compilador. Verificação mecânica não equivale a
revisão científica externa, prova de hipótese empírica ou segurança IEEE-754.

## Resultado local

158 teoremas em quatro módulos, 27 famílias matemáticas/modelos e uma família
observacional fora da alegação de prova. 183 testes selecionados aprovados.
Livro completo compilado (538 páginas), margens conferidas por coordenadas
e amostragem visual. Recibos: `docs/verification-book-lean-r908.json`
e `docs/verification-book-r908.json`; matriz: `docs/book-math-map-r908.json`.
