---
name: inferencia-quantitativa-avancada
description: Inferência causal (DID, IV-2SLS, RDD), Bayesiana conjugada e modelos mistos (ICC, EP cluster-robustos) para a orquestração do Core, com suposições declaradas, diagnósticos e limites. Use para estimar efeitos causais sob desenho, atualizar crenças com prior explícito e modelar dados hierárquicos; nunca declarar causalidade, eficácia ou cura sem desenho que a sustente; sem prior oculto e sem teste de densidade presumido.
---

# Inferência Quantitativa Avançada (Fase B da descoberta)

## Quando acionar

Quando houver CSV real e pergunta causal ("o tratamento causou?"), prior a
atualizar ("qual a crença posterior?") ou dados hierárquicos ("grupos
importam?"). Para associação simples, basta `research/discovery` Fase A
(Welch/Pearson/Cohen). Sem dados reais: produzir protocolo, nunca número.

## Mapa método → suposição → diagnóstico

| Método | Suposição central | Diagnóstico obrigatório | Se falhar |
|---|---|---|---|
| DID (`estimar_did`) | tendências paralelas | p por permutação; placebo exige 3+ períodos | declarar suposição, não testar |
| IV-2SLS (`estimar_iv`) | relevância + exclusão | F do 1º estágio (F<10 = fraco) | NÃO alegar causalidade |
| RDD (`causal.rdd`) | continuidade no corte | sensibilidade h/2, 2h + placebos | sem teste de densidade (limite) |
| Bayes (`atualizar_bayes`) | prior justificado + σ | sensibilidade a 2 priors | registrar ambos os priors |
| ICC + EP cluster (`icc_cluster`) | ≥2 clusters | ICC + n por cluster | OLS simples se ICC baixo |

## Bloqueadores

- Palavras causais ("causa", "prova", "eficaz", "cura", "leads to") só com desenho causal + diagnósticos ok — verificado pelo hook `causal_claim_guard.sh`.
- Prior nunca oculto: `mu0`/`tau0` sempre registrados na saída.
- F<10 no primeiro estágio = instrumento fraco: qualquer frase causal é overclaim.
- MCMC/HMC, efeitos aleatórios em inclinação, DID escalonado e McCrary: fora de escopo (SPEC-935-R710 §4).

## Ferramentas

MCP `artigo-academico-mcp`: `estimar_did`, `estimar_iv`, `atualizar_bayes`, `icc_cluster` (CSV inline, teto de linhas, fail-closed). Agentes: `inferencia-causal-did-iv-rdd`, `modelagem-bayesiana-mista`.
