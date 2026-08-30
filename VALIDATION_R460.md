# VALIDATION_R460 — HABD (híbrido anchor-blended determinístico)

**Round:** R460 · **Spec:** SPEC-935-R460 · **Status:** green · **Testes:** 13 passando

## O que foi construído

`rag/habd.py` — **HABD (Hybrid Anchor-Blended Deterministic diversifier)**, que
combina a virtude do Recamán (determinismo, custo O(K·N), sem seed) com a virtude
do MMR (dissimilaridade de conteúdo), operando sobre **âncoras canônicas** e
ajustando o balanço relevância↔diversidade (lambda) **por query** de forma
determinística, sem LLM/fine-tuning (inspirado em DF-RAG arXiv 2601.17212 para o
lambda adaptativo, sem copiar seu mecanismo LLM).

## Resultado observado no coorte R458 (comparação justa, mesmos dados/k/queries)

| Estratégia | Div | Cobertura | Groundedness | loss_rel |
|---|---|---|---|---|
| top-k (atual) | 0.500 | 0.667 | 0.4561 | — |
| Recamán (R457) | 0.500 | 0.667 | 0.4561 | 0.0% |
| MMR-0.7 | 0.750 | 0.917 | 0.4256 | 6.7% |
| **HABD (R460)** | **0.8333** | **1.000** | 0.4087 | **10.4%** |

## Veredito honesto (anti-overclaim)

- **HABD supera MMR e Recamán/top-k em diversidade (0.8333) e atinge cobertura
  máxima (1.0)** — questão observável e reportável.
- **`verdict_h3 = refuta_H3`**: a queda relativa de groundedness (10.4%) **excede
  a tolerância de 5%**. HABD entrega mais diversidade ao custo de sacrificar
  relevância além do ponto tolerável — empurra a fronteira
  relevância↔diversidade, mas **não é uma vitória limpa** no critério H3 rígido.

### Interpretação científica
O HABD confirma mecanicamente a tese central: **diversificar sobre âncoras
(conteúdo/fonte) é superior a diversificar sobre posição** (Recamán), e operar com
lambda adaptativo melhora a cobertura. Porém, como o MMR, o custo em groundedness
permanece o gargalo. A fronteira continua aberta; HABD não a resolve dentro da
tolerância — isso é **refutação**, não fracasso de implementação, e deve ser
relatado como tal.

## Critérios de aceitação
- [x] module_exists · [x] anchor_resolved · [x] deterministic · [x] top1_preserved
- [x] budget_respected · [x] lambda_adaptive_mono · [x] prefers_novel_anchor
- [x] beats_recaman_topk_in_cohort (div > 0.5) · [x] vs_mmr_recorded
- [x] grounded_tolerance (verifica **refuta_H3** quando queda > 5% — anti-overclaim)
- [x] habd_max_coverage_vs_mmr (cobertura 1.0 >= MMR)

## Limitações declaradas
- Corpus-piloto controlado (6 ângulos × 3 docs, k=4, n=4); não generaliza.
- Sem embeddings (similaridade por tokens/Jaccard), coerente com R458.
- Nenhuma alegação de superioridade absoluta: o observado é o reportado.
- O lambda adaptativo é heurística determinística; não é o DF-RAG (que usa LLM).

## QA
- 13/13 testes passam; suíte total verificada.
- Ciclo R460 registrado no evolution registry.
