# SPEC-007 — Trust Engine (portado do SPEC-038 original)

```yaml
spec_id: SPEC-007
title: Trust Engine — Segurança Comportamental
module: trust/trust_engine.py
origin: OpenCode_Ecosystem SPEC-038
status: implemented
```

## Objetivo

Garantir segurança comportamental do ecossistema por meio de três mecanismos: **TrustScorer/BehavioralGate** (decide se uma ação pode ser executada com base no histórico de confiança), **NaturalForgetting** (memória Atkinson-Shiffrin com decaimento por importância) e **OutcomeTracker** (registro de resultados que realimenta os scores).

## Requisitos

| ID | Requisito | Critério de Aceitação |
|---|---|---|
| REQ-007.1 | O BehavioralGate deve permitir ações novas (baseline 0.5) e bloquear ações com trust < threshold | `gate()` retorna `GateDecision.allowed` coerente com o score |
| REQ-007.2 | O TrustScorer deve operar em shadow mode nas primeiras execuções (score ≤ 0.5) | score só ultrapassa 0.5 após `SHADOW_MODE_THRESHOLD` execuções |
| REQ-007.3 | Falhas consecutivas devem aplicar penalidade progressiva (até 0.5) | 5 falhas seguidas ⇒ trust < 0.5 |
| REQ-007.4 | NaturalForgetting deve armazenar e recuperar memórias por dica de conteúdo | `store()` + `recall(hint)` retorna o slot |
| REQ-007.5 | O orquestrador deve filtrar agentes bloqueados pelo gate no CFP, com fallback anti-orfandade | `_on_cfp` nunca deixa tarefa sem candidatos |

## Invariantes

- INV-007.1: `0.0 <= trust_score <= 1.0` sempre.
- INV-007.2: O gate nunca lança exceção — em dúvida, decide com `reason` explicativo.
- INV-007.3: `trust.learn()` é chamado em TODA conclusão de tarefa (sucesso ou falha).

## Testes

`tests/test_advanced_subsystems.py::TestTrustEngine` (3 testes).
