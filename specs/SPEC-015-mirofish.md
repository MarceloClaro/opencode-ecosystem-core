# SPEC-015 — MiroFish Swarm Intelligence Engine

```yaml
spec_id: SPEC-015
title: Enxame Preditivo MiroFish com Validação Cruzada
status: implemented
component: mirofish/
inspiration: github.com/MarceloClaro/MiroFish (BettaFish v5.0 integration)
```

## Objetivo

Prover um motor de inteligência de enxame universal ("Predicting Anything"):
agentes heterogêneos com vieses distintos (otimista, pessimista, contrário,
neutro, momentum) emitem previsões independentes agregadas por média ponderada
pela acurácia histórica (wisdom of crowds), com debate iterativo estilo Delphi
e validação cruzada tripla (enxame × equilíbrio de Nash × auditoria Qualis).

## Requisitos

| ID | Requisito | Critério de aceitação |
|----|-----------|----------------------|
| R-015.1 | Enxame configurável | `MiroFishSwarm(n_agents=N)` cria N agentes com vieses cíclicos |
| R-015.2 | Previsão agregada | `predict()` retorna aggregate ∈ [0,1], stdev, consensus e previsões individuais |
| R-015.3 | Aprendizado por feedback | `feedback(id, actual)` recalibra o peso de cada agente pelo erro absoluto |
| R-015.4 | Debate Delphi | `debate()` converge (Δ < 0.02 entre rodadas) na maioria dos cenários com sinal estável |
| R-015.5 | Validação cruzada | `CrossValidator.validate_decision()` combina enxame + Nash e retorna veredito com rationale |
| R-015.6 | Persistência | Estado do enxame (pesos, previsões) sobrevive a reinicializações via `.mci_state/mirofish_swarm.json` |
| R-015.7 | Integração orquestrador | `orch.swarm_predict()` e `orch.swarm_validate()` registram reflexões na memória global |

## Invariantes

- INV-015.1: Previsões individuais e agregadas sempre pertencem a [0, 1].
- INV-015.2: Pesos de agentes nunca caem abaixo de 0.1 (nenhum agente é silenciado).
- INV-015.3: Reprodutibilidade: com `seed` fixa, previsões são determinísticas.

## Referências

Surowiecki (2004) — The Wisdom of Crowds; Dalkey & Helmer (1963) — Delphi;
Rosenberg (2015) — Swarm AI; Nash (1950); MarceloClaro/MiroFish.
