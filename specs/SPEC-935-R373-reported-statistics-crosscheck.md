---
spec_id: SPEC-935-R373
title: Contraverificação de estatísticas reportadas + correção de falso positivo no R369
component: mci/rigorous_validation.py + reasoning/production_scaffolds.py
status: draft
test_file: tests/test_r373_reported_statistics_crosscheck.py
---

# SPEC-935-R373 — Contraverificação de Estatísticas Reportadas

**Data:** 2026-08-02
**Motivação:** validação fim-a-fim real (não simulada) dos gates R369/R370/
R371/R372 sobre um manuscrito de verdade (dossiê "A Educação como Fator de
Ruptura da Armadilha da Renda Média no Brasil", adaptado para
`academic/papers/manuscrito_educacao_armadilha_renda_media_usp.md`) revelou
dois problemas reais, corrigidos neste ciclo.

## 1. Bug corrigido: falso positivo em `reasoning/production_scaffolds.py`

`_NOVELTY_TERMS` incluía `"primeiro"`/`"primeira"` como gatilhos brutos de
`UNSUPPORTED_NOVELTY_CLAIM`. Isso disparou falso positivo em
**"primeiras diferenças"** (termo econométrico padrão, *first differences*,
não alegação de novidade). `"primeiro"`/`"primeira"` são ordinais comuns do
português ("primeira diferença", "primeiro trimestre", "primeira vista",
"primeiro passo") — tratá-los como alegação de novidade por substring gera
alarme falso em qualquer texto econômico/estatístico comum.

**Correção:** removidos os termos brutos; substituídos por fraseado de
prioridade autoral explícita (`_NOVELTY_PRIORITY_PHRASES`): "pela primeira
vez", "primeiro estudo a", "primeiro trabalho a", "o primeiro a", e
equivalentes em inglês. Regressão testada: "primeiras diferenças... neste
primeiro trimestre" não dispara mais; "pela primeira vez, mostramos..." e
"este é o primeiro estudo a..." continuam disparando corretamente.

## 2. Gap real descoberto: R370 não opera sobre manuscritos publicados

O R370 (`two_sample_hypothesis_test`, `permutation_counter_proof`) exige
**amostras brutas** (arrays individuais, mínimo 3 por grupo). Manuscritos
publicados — como o dossiê testado — reportam apenas **estatística-resumo**
já calculada (r, p, IC 95%, n, F de ANOVA), nunca os dados brutos
subjacentes. Tentar alimentar o R370 com médias de grupo agregadas
(ex.: Tabela 1 do manuscrito, 5 médias de renda por nível educacional)
falha corretamente (`ValueError`, amostra insuficiente) — comportamento
fail-closed correto, mas que deixa o manuscrito **sem nenhum gate
estatístico aplicável**, já que o R370 pressupõe acesso a dados brutos que
o autor de um manuscrito publicado tipicamente não tem à mão (ou já
descartou após calcular as estatísticas).

**Achado adicional durante o diagnóstico:** recalculando independentemente
a significância de Pearson a partir de `(r, n)` via a fórmula-padrão
(t = r·√(n−2)/√(1−r²), teste t bilateral), a maioria dos pares do artigo
bate com precisão de máquina contra os p-values reportados (correlações
cross-country, todas com corte transversal). Mas duas correlações de série
temporal brasileira (GDP×Escolaridade n=8, Gini×Escolaridade n=6) reportam
p **mais conservador** (maior) que a fórmula ingênua sugere — consistente
com a própria Seção 6.1 do manuscrito, que alerta sobre cointegração de
séries não-estacionárias e recomenda correção que "reduz substancialmente
as magnitudes observadas" (ou seja, aumenta o p reportado). Duas outras
correlações (GDP×PISA, GDP×Insegurança Alimentar) **não têm `n` declarado
em lugar nenhum do texto** — a Tabela 2 do manuscrito tem legenda "n =
número de observações" mas nenhuma coluna de `n` por linha, uma lacuna de
transparência real do próprio artigo.

## 2.1 A correção correta: verificação **assimétrica**, nunca simétrica

Uma contraverificação simétrica (flagar qualquer `p_reportado != p_ingênuo`)
geraria falso positivo sistemático contra correções metodológicas legítimas
de séries temporais — o próprio padrão observado no manuscrito real. A
única direção de discrepância que não tem explicação metodológica legítima
é o **inverso**: `p_reportado` **menor** que o `p` ingênuo — alegar mais
significância do que os números brutos (r, n) sozinhos sustentam. Nenhuma
correção de cointegração, autocorrelação ou tamanho efetivo de amostra
jamais torna um resultado artificialmente **mais** significativo; correções
legítimas só tornam o p mais conservador (maior).

## 3. `pearson_naive_significance(r, n) -> float`

Recalcula o p-value bilateral de Pearson a partir de `(r, n)` via a
distribuição t de Student, implementada em Python puro (zero scipy/numpy):
função beta incompleta regularizada por fração contínua (Numerical
Recipes, `betacf`), validada contra `scipy.stats.t.cdf` em 8 casos de
referência com diferença ≤ 1e-15 (validação de desenvolvimento; scipy não
é importado no módulo entregue). `n < 3` ou `abs(r) >= 1` → `ContractError`.

## 4. `crosscheck_reported_correlation(r, n, reported_p, tolerance=1e-3) -> dict`

- Calcula `naive_p = pearson_naive_significance(r, n)`.
- `overstated = reported_p < naive_p - tolerance` (única condição de
  alerta: significância reportada além do que r,n sozinhos sustentam).
- `overstated=True` → achado `OVERSTATED_SIGNIFICANCE` (severity `high`,
  `requires_human_review=True`).
- `reported_p >= naive_p - tolerance` → sem achado (cobre tanto
  correspondência exata quanto correção conservadora legítima).
- Retorna envelope: `schema_version`, `naive_p`, `reported_p`,
  `overstated`, `findings[]`, `human_gate`, `disclaimer` — o disclaimer
  declara explicitamente que a ausência de alerta **não valida** a
  correção aplicada, apenas confirma que a significância reportada não é
  mais forte do que os números brutos permitiriam sem correção alguma.

## 5. Integração no R103

`OrchestratorReviewer.verify_reported_correlation(claim_id, r, n,
reported_p, ledger) -> dict` — mesmo padrão dos três gates anteriores.

## 6. Critérios de aceitação

1. `pearson_naive_significance`: validado contra 8 referências scipy
   (dev-time) com diff ≤ 1e-12; `n<3` ou `|r|>=1` → `ContractError`.
2. `crosscheck_reported_correlation`: p reportado igual ao ingênuo → sem
   achado; p reportado mais conservador (maior) → sem achado; p reportado
   menor que o ingênuo além da tolerância → achado `OVERSTATED_SIGNIFICANCE`.
3. Regressão do bug do R369: "primeiras diferenças"/"primeiro trimestre"
   não disparam `UNSUPPORTED_NOVELTY_CLAIM"; "pela primeira vez"/"primeiro
   estudo a" continuam disparando.
4. Aplicado às 5 correlações do manuscrito real com `n` declarado no
   texto: nenhuma reporta `overstated=True` (achado honesto — o artigo não
   infla significância).
5. `verify_reported_correlation` (R103): mesmo padrão de integração dos
   demais gates.
6. Zero regressão em R369/R370/R371/R372 e no restante da suíte.
