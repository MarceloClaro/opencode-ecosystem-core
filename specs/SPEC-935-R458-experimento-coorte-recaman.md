---
spec_id: SPEC-935-R458
title: Experimento de coorte — Recamán vs MMR vs estado atual no RAG científico
component: benchmarks/cohort_recaman.py, tests/test_r458_cohort_experiment.py
status: green
round_id: R458
test_file: tests/test_r458_cohort_experiment.py
---

# SPEC-935-R458 — Experimento de coorte (Fase 3 do roadmap da Seção 9.3)

## Objetivo

Medir, de forma **honesta, justa e reprodutível**, se a diversificação estruturada
por Recamán (R457) produz ganho mensurável sobre o estado atual, usando a métrica
de diversidade `Div(S)` e métricas de qualidade, em um corpus-piloto controlado,
comparando três estratégias de seleção pós-ranqueamento:

1. **Atual** — top-k por `final_score` (baseline de referência);
2. **MMR** — Maximal Marginal Relevance (baseline clássico de diversificação);
3. **Recamán** — diversificador determinístico de R457 (proposta).

**Anti-overclaim**: este experimento declara **resultados observados em corpus
piloto controlado**, com escopo explícito. **Não** generaliza para produção, **não**
equivale a certificação externa e **não** promove o diversificador ao pipeline
padrão sem decisão posterior.

## Hipótese mensurável (H2)

> **H2:** em um corpus-piloto com múltiplos ângulos (perspectivas) sobre um tópico,
> a seleção por Recamán atinge diversidade `Div(S)` **maior ou igual** à do estado
> atual (top-k), **sem degradar** groundness (`groundedness` médio) além de um
> limiar tolerável (e.g. ≤ 5% de queda relativa).

H2 é **refutável**: se a evidência do coorte não a sustentar, registramos o
resultado como falha da hipótese (sem maquiar).

## Desenho do corpus-piloto

- Tópico com `A` ângulos (famílias de perspectiva) distintos, simetricamente
  povoados com `m` documentos cada.
- Cada documento é um `ScientificDocument` com texto contendo as palavras-chave do
  seu ângulo (determinístico, sem aleatoriedade).
- Queries cobrem um subconjunto de ângulos (e.g. 3 dos A), para que o ranking
  cruze múltiplas famílias e a métrica de "cobertura" seja objetiva.

## Métricas por seleção

- `Div(S)` — diversidade sobre âncoras canônicas (Eq. 6.1 do manual), via
  `rag.recaman.diversity`.
- `groundedness` — média dos `final_score` dos itens selecionados.
- `coverage` — fração de ângulos-alvo representados na seleção (cobertura de
  consulta).
- `loss_rel_groundedness` — queda relativa de groundedness vs. estado atual.

## Comparação (baseline justo)

- Mesmo corpus, mesmas queries, mesma ordenação primária (`ScientificRAG.retrieve`).
- Cada estratégia seleciona o mesmo orçamento `k`.
- MMR usa similaridade por sobreposição de tokens (sem embeds), λ fixo documentado.
- Recamán usa `RecamanDiversifier.diversify(top_N_candidates, k)`.

## Teste de hipótese — desfecho observado (corpus-piloto, 4 queries)

**Veredito registrado: `refuta_H2`** (H2 não demonstrada no desenho testado).

Métricas médias (n_queries=4, k=4, corpus determinístico de 6 ângulos × 3 docs):

| Estratégia | Div(S) | groundedness | coverage |
|---|---|---|---|
| atual (top-k) | 0.500 | 0.4561 | 0.667 |
| MMR (λ=0.7)  | 0.750 | 0.4256 | 0.917 |
| Recamán       | 0.500 | 0.4561 | 0.667 |

- `gain_div_vs_atual(Recamán) = 0.0` → **empate, não ganho estrito** (H2 pedia ganho).
- `loss_rel_groundedness(Recamán) = 0.0` → **não degrada relevância**.
- `mmr_supera_recaman = true` → o baseline clássico diverge claramente mais (0.75 vs 0.50).

### Interpretação (achado científico, sem overclaim)

O esquema posicional de Recamán diversifica **posições** de forma determinística
(offsets `(1+a_m) mod N`), **mas não âncoras/fontes**. Quando o ranking é
"localmente monopolista" — 3 docs da mesma família de perspectiva ocupando as 3
primeiras posições, como ocorre neste corpus — os offsets caem na mesma família,
reproduzindo o top-k. O MMR, por maximizar explicitamente a dissimilaridade de
conteúdo entre os selecionados, espalha por fonte e supera a proposta neste desenho.

**Conclusão honesta**: esses números **não** autorizam promover o diversificador
Recamán ao pipeline padrão. A proposta mantém validade como **capacidade
determinística exposta (R457)**, mas H2 de "ganho de diversidade sobre o top-k"
**não foi demonstrada** neste coorte-piloto; exigiria redesenho dos offsets para
operar sobre âncoras (não posições) ou experimento com corpus real (fora do
escopo desta spec).

## Critérios de Aceitação Executáveis

- `benchmark_module_exists` — existe `benchmarks/cohort_recaman.py`.
- `cohort_has_angles` — o corpus-piloto tem `A ≥ 3` ângulos e documentos suficientes.
- `current_is_topk` — estratégia 'atual' seleciona por `final_score` (top-k).
- `recaman_includes_top1` — Recamán sempre inclui o item mais relevante.
- `recaman_deterministic` — duas execuções do coorte dão o mesmo resultado.
- `metrics_in_range` — `Div ∈ [0,1]`, `groundedness ∈ [0,1]`, `coverage ∈ [0,1]`.
- `loss_lte_tolerance` — `loss_rel_groundedness(Recamán) ≤ 0.05` (H2 parte de qualidade).
- `report_created` — a execução gera um relatório estruturado (`cohort_report.json`)
  com métricas por estratégia e o veredito (sustenta/refuta H2).
- `no_overclaim` — o relatório rotula o resultado como observação em corpus piloto,
  sem generalização.

## Estratégia TDD

1. Testes (RED) validam a existência do módulo e os contratos acima.
2. Implementar (GREEN) `benchmarks/cohort_recaman.py` e um baseline MMR simples e
   determinístico.
3. Executar o coorte; gerar `cohort_report.json`.
4. Registrar resultado **honesto** (sustenta ou refuta H2), VALIDATION_R458 e ciclo
   evolutivo R458.

## Não objetivos

- Não medir qualidade de resposta gerada (LLM) — apenas seleção/recuperação.
- Não usar embeddings externos (corpus-determinístico, similaridade por tokens).
- Não promover o diversificador ao pipeline padrão nesta spec.
- Não generalizar para produção sem novo ciclo.
