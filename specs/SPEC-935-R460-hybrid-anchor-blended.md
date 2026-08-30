---
spec_id: SPEC-935-R460
title: Diversificador híbrido anchor-blended determinístico (HABD) — superar MMR e Recamán
component: rag/habd.py, benchmarks/cohort_recaman.py (Novastrategia), tests/test_r460_habd.py
status: green
round_id: R460
test_file: tests/test_r460_habd.py
---

# SPEC-935-R460 — HABD: Diversificador híbrido anchor-blended determinístico

## Motivação (achados do R458 + literatura 2024–2026)

O experimento R458 mostrou:
- Recamán (posicional) **empata** com top-k sob ranking monopolista por família
  (ganho `Div` = 0.0) — diversifica posição, não âncora/fonte.
- MMR (similaridade de conteúdo, λ=0.7 fixo) supera (Div 0.75 vs 0.50), mas com
  queda de relevância (~6.7%) acima da tolerância de 5%.

A literatura recente reforça duas direções que este ciclo incorpora:
- **DF-RAG** (arXiv 2601.17212): o λ ótimo do MMR varia por query/dataset; **λ
  adaptativo por query** melhora F1 4–10% sobre MMR vanilla e cobre até ~91% do
  gap do Oracle. MMR com λ fixo é subótimo.
- **RAG Cookbook 2026 / Qdrant**: "over-retrieve before MMR" (pool maior) e
  **rotação adaptativa** do λ por tipo de query; λ=0.7 é standard de produção mas
  não universal.
- **"Reranking trap"** (Chauzov 2025): rerankers de relevância colapsam
  diversidade por design; MMR é o `trade-off` explícito relevância↔diversidade.

**Síntese (proposta disruptiva HABD):** combinar a virtude do Recamán
(determinismo, custo O(K)) com a virtude do MMR (dissimilaridade de conteúdo),
**operando sobre âncoras canônicas** e **ajustando o balanço λ por query** de
forma **determinística e sem LLM/fine-tuning**.

## Definição do HABD

Dado um ranking de candidatos `R` (já deduplicado por documento) e orçamento `K`:

1. **Resolução de âncoras**: cada item mapeia a uma âncora canônica via
   `AnchorResolver` (identidade de fonte/âmago), como em R457.

2. **Índice de mistura de ângulos** (heurística determinística por query):
   \[
   \mu \;=\; \frac{\#\text{âncoras distintas no top-}N}{\min(N, \#\text{âncoras no pool})}
   \]
   `μ ∈ [0,1]`. Se `μ` é baixo (ranking monopolista), a consulta *precisa* de
   diversidade; se `μ` já é alto (ranking misto), diversidade extra tem custo
   marginal. Isso traduz o "λ adaptativo" sem LLM.

3. **λ adaptativo determinístico**:
   \[
   \lambda_{\text{habd}}(q) \;=\; \lambda_\text{base} + (1-\lambda_\text{base})\,(1-\mu)
   \]
   com `λ_base=0.7`. Assim: ranking muito monopolista (`μ→0`) ⇒ `λ→1.0`
   (relevância pura... não!) — **correção**: queremos MAIS diversidade quando
   monopolista, logo `λ` deve DIMINUIR. Ajuste: `λ = λ_base · μ + (1-μ)·λ_min`,
   com `λ_min=0.3`. Monopolista (`μ→0`) ⇒ `λ→0.3` (diversidade); misto (`μ→1`)
   ⇒ `λ→0.7` (relevância).

4. **MMR anchor-blended**: seleção gulosa
   \[
   \mathrm{score}(d) = \lambda\,\mathrm{relev}(d) - (1-\lambda)\,
   \underbrace{\max_{d_j\in S}\bigl(\Sim_{\text{anchor}}(d,d_j)\bigr)}_{\text{0 se d tem âncora nova}},
   \]
   onde `Sim_anchor = 1` se mesma âncora, `0` se âncoras diferentes. Isso garante
   que, a cada passo, uma **âncora não-representada** seja preferida (diversidade
   de fonte) e, entre candidatos da mesma âncora, o mais relevante vença.

5. **Determinismo**: sem seed; desempates por ordem de ranking (livre de
   aleatoriedade).
6. **Custo**: O(K·N) no pior caso (como MMR), com running max opcional.

## Expectativa (hipótese H3, REFUTÁVEL)

> **H3:** no benchmark de coorte R458, `HABD` atinge diversidade `Div(HABD) >
> Div(Recamán) = Div(top-k)`, **e** `Div(HABD) >= Div(MMR-0.7)`, **e** queda
> relativa de groundedness `<= 5%` (melhor ponto na fronteira relevância↔diversidade
> que MMR-0.7).

H3 é refutável: se HABD não superar, registramos refuta (sem maquiar). O objetivo
é *superar*, mas a honestidade exige reportar o que ocorrer.

## Critérios de Aceitação Executáveis

- `module_exists` — `rag/habd.py` importável com `HABD`.
- `anchor_resolved` — itens de mesma fonte mapeiam para a mesma âncora.
- `deterministic` — duas execuções idênticas, sem seed.
- `top1_preserved` — o item mais relevante sempre entra.
- `budget_respected` — <= K itens, sem duplicatas.
- `lambda_adaptive_mono` — ranking monopolista (μ≈0) ⇒ `λ≈λ_min` (0.3);
  ranking misto (μ≈1) ⇒ `λ≈λ_base` (0.7).
- `prefers_novel_anchor` — nas primeiras iterações, âncora não-representada tem
  prioridade sobre repetir âncora já selecionada (mesmo com relevância menor).
- `beats_recaman_topk` — no coorte R458, `Div(HABD) > 0.5` (supera empate).
- `vs_mmr` — `Div(HABD) >= Div(MMR0.7)` OU (se menor) registro honesto; reportado
  no relatório.
- `grounded_tolerance` — `loss_rel(groundedness) <= 0.05`.
- `verdict` — relatório de coorte contém comparação HABD e veredito (sustenta/refuta H3).
- `no_overclaim` — escopo corpus-piloto, não generaliza.

## Estratégia TDD
1. Testes RED validam os contratos acima (incl. preferência por âncora nova e λ
   adaptativo).
2. Implementar `rag/habd.py` (GREEN).
3. Estender `benchmarks/cohort_recaman.py` com a estratégia `habd` e re-rodar o
   coorte R458 (comparação justa, mesmos dados/query/k).
4. Registrar resultado honesto (sustenta/refuta H3), VALIDATION_R460, ciclo R460.

## Não objetivos
- Não usar LLM/fine-tuning para o λ (heurística determinística).
- Não usar embeddings externos (coerência com R458: similaridade por tokens).
- Não alegar superioridade absoluta; reportar o observado no corpus-piloto.
