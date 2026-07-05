# SPEC-008 — Token Economy (portado dos SPEC-022~025 originais)

```yaml
spec_id: SPEC-008
title: Token Economy — Staking, Slashing e Fee Market
module: economy/token_economy.py
origin: OpenCode_Ecosystem SPEC-022, SPEC-023, SPEC-024, SPEC-025
status: implemented
```

## Objetivo

Implementar a economia de agentes: cada agente possui saldo em tokens; ao aceitar uma tarefa, faz **stake** (caução); tarefas concluídas com sucesso liberam o stake com recompensa; falhas sofrem **slashing** (perda parcial); o **fee market** precifica tarefas por prioridade.

## Requisitos

| ID | Requisito | Critério de Aceitação |
|---|---|---|
| REQ-008.1 | Stake liberado com recompensa em caso de sucesso | `resolve(success=True)` ⇒ status `released`, saldo aumenta |
| REQ-008.2 | Slashing aplicado em caso de falha | `resolve(success=False)` ⇒ status `slashed`, saldo diminui |
| REQ-008.3 | Fee market cobra mais por prioridade alta | `post_task(priority="high").total_fee > post_task(priority="low").total_fee` |
| REQ-008.4 | Ledger auditável com histórico de transações | `report()` expõe balances, total_locked, stakes, transactions |
| REQ-008.5 | Integração ao ciclo de delegação do orquestrador | commit no CFP; resolve no `report_completion` |

## Invariantes

- INV-008.1: Saldo nunca fica negativo (stake limitado ao saldo disponível).
- INV-008.2: Todo stake tem exatamente um desfecho: `released` ou `slashed`.
- INV-008.3: Falhas econômicas nunca bloqueiam a delegação (try/except no orquestrador).

## Testes

`tests/test_advanced_subsystems.py::TestTokenEconomy` (3 testes).
