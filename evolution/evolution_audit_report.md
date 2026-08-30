# Relatório de Evolução Auditável — R462

> **SPEC-935-R462** · Cadeia de Custódia Auditável · Gerado em 2026-08-30 17:41 UTC

## Métricas de Custódia

| Métrica | Valor |
|---|---|
| Custódia global | **0.4%** (1/279 ciclos) |
| Custódia recente (R462+) | **100.0%** (1/1) |
| Rejeitados pelo gate | 0 |
| Tamper detectado | 0 |
| Ciclos legados (pré-R462, não reescritos) | 0 |

## Detalhe por ciclo (últimos 20)

| Ciclo | Auditado | Verificador | Hash | Veredito |
|---|---|---|---|---|
| R442 | Não | — | 0 | — |
| R443 | Não | — | 0 | — |
| R444 | Não | — | 0 | — |
| R445 | Não | — | 0 | — |
| R446 | Não | — | 0 | — |
| R447 | Não | — | 0 | — |
| R448 | Não | — | 0 | — |
| R449 | Não | — | 0 | — |
| R450 | Não | — | 0 | — |
| R451 | Não | — | 0 | — |
| R452 | Não | — | 0 | — |
| R453 | Não | — | 0 | — |
| R454 | Não | — | 0 | — |
| R455 | Não | — | 0 | — |
| R456 | Não | — | 0 | — |
| R457 | Não | — | 0 | — |
| R458 | Não | — | 0 | — |
| R459 | Não | — | 0 | — |
| R460 | Não | — | 0 | — |
| R462 | Sim | marceloclaro@auditor.blind | 4 | APROVADO |

## Anti-Tamper (SHA-256 ancorado)

Cada artefato é ancorado por hash SHA-256 no momento da produção. Alterações posteriores são detectáveis via `EvolutionAuditGate.verify_tamper()`. O hash prova **ausência de alteração**, não **correção** do conteúdo.