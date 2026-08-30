# Relatório de Evolução Auditável — R462

> **SPEC-935-R462** · Cadeia de Custódia Auditável · Gerado em 2026-08-30 18:10 UTC

## Métricas de Custódia

| Métrica | Valor |
|---|---|
| Custódia global | **0.4%** (1/279 ciclos) |
| Custódia recente (R462+) | **100.0%** (1/1) |
| Âncoras de imutabilidade (merkle) | 1 |
| Rejeitados pelo gate | 0 |
| Tamper detectado | 0 |
| Ciclos legados (pré-R462, não reescritos) | 278 |

## Detalhe por ciclo (últimos 20)

| Ciclo | Auditado | Verificador | Hash | Veredito | Merkle | Commit |
|---|---|---|---|---|---|---|
| R442 | Legacy | — | 0 | — | — | — |
| R443 | Legacy | — | 0 | — | — | — |
| R444 | Legacy | — | 0 | — | — | — |
| R445 | Legacy | — | 0 | — | — | — |
| R446 | Legacy | — | 0 | — | — | — |
| R447 | Legacy | — | 0 | — | — | — |
| R448 | Legacy | — | 0 | — | — | — |
| R449 | Legacy | — | 0 | — | — | — |
| R450 | Legacy | — | 0 | — | — | — |
| R451 | Legacy | — | 0 | — | — | — |
| R452 | Legacy | — | 0 | — | — | — |
| R453 | Legacy | — | 0 | — | — | — |
| R454 | Legacy | — | 0 | — | — | — |
| R455 | Legacy | — | 0 | — | — | — |
| R456 | Legacy | — | 0 | — | — | — |
| R457 | Legacy | — | 0 | — | — | — |
| R458 | Legacy | — | 0 | — | — | — |
| R459 | Legacy | — | 0 | — | — | — |
| R460 | Legacy | — | 0 | — | — | — |
| R462 | Sim | marceloclaro@auditor.blind | 5 | APROVADO | 6a3ee615af8a… | f35927d405… |

## Anti-Tamper (SHA-256 ancorado)

Cada artefato é ancorado por hash SHA-256 no momento da produção; o `merkle_root` agrega todos os hashes do ciclo em uma ancora única e o `origin_commit` fixa a versão do código-fonte no registro. Alterações posteriores são detectáveis via `EvolutionAuditGate.verify_tamper()`/`verify_merkle()`. O hash prova **ausência de alteração**, não **correção** do conteúdo.