# SPEC-935-R710 — Fase B: inferência causal, Bayesiana e modelos mistos

**Status:** `em implementação`
**Ciclo:** R710+
**Data:** 2026-10-07
**Base:** SPEC-935-R708 (Fase A concluída: desenho, Welch/Pearson/Cohen, Holm, relato, replicação)

## 1. Problema

A Fase A quantifica associações; não identifica causalidade, não atualiza
crenças com prior explícito e não modela estrutura hierárquica. Artigos
relevantes exigem esses três degraus — cada um com suposições declaradas e
diagnósticos, nunca como caixa-preta.

## 2. Objetivo

Estender `research/discovery/` com `causal.py` (DID + inferência por
permutação; IV-2SLS com F do primeiro estágio; RDD linear local com
sensibilidade de banda e placebos), `bayes.py` (Normal-Normal conjugado com
sensibilidade a prior) e `mistos.py` (ICC + EP robustos a cluster) —
fórmulas explícitas em numpy/scipy, sem dependência nova.

## 3. Critérios de aceitação

- [ ] AC1 — DID: estimador de dupla diferença + p por permutação de rótulos; limitação de tendências paralelas declarada (não testável com 2 períodos).
- [ ] AC2 — IV-2SLS: primeiro estágio + F; alerta explícito se F<10 (Staiger-Stock, heurística); comparação com OLS; sem alegação causal se instrumento fraco.
- [ ] AC3 — RDD: τ por regressão linear local em banda h + sensibilidade h/2 e 2h + placebos em cortes falsos; sem teste de densidade (limitação declarada).
- [ ] AC4 — Bayes: posterior Normal-Normal fechada + IC crível + P(θ>0) + sensibilidade a 2 priors; prior sempre registrado (sem prior oculto).
- [ ] AC5 — Mistos: ICC por ANOVA de efeitos aleatórios + EP cluster-robustos (sanduíche CR0) para OLS; fail-closed em grupo unitário.
- [ ] AC6 — Testes herméticos `tests/test_r710_fase_b.py` (sementes fixas): DID recupera efeito; nulo ≈ 0; IV válido recupera, fraco acusa F<10; RDD recupera salto; Bayes entre prior e verossimilhança; ICC alto em clusters coesos.
- [ ] AC7 — Skill + 2 agentes + 4 ferramentas MCP + 1 hook de guarda causal, todos testados.

## 4. Fora de escopo (declarado)

- Testes de densidade do running (McCrary), Sargan/Hansen, MCMC/HMC, modelos mistos com efeitos aleatórios em inclinação, diff-in-diff escalonado (staggered).
- Qualquer frase causal ("causa", "prova", "eficaz") sem desenho que a sustente — barrada pelo hook.
