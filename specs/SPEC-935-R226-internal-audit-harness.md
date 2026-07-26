---
spec_id: SPEC-935-R226
title: "Harness Interno Auditável Unificado (Internal Audit Harness)"
component: benchmarks/internal_audit_harness.py
test_file: tests/test_r226_internal_audit_harness.py
status: green
---

# SPEC-935-R226 — Harness Interno Auditável Unificado
=====================================================

## 1. Visão Geral
Esta especificação consolida a capacidade do **OpenCode Ecosystem Core** de atuar como um **Harness Interno Auditável Autônomo**, unificando as verificações SDD, a telemetria do MetaBus, o registro imutável do `CORRIGENDUM.md`, a auditoria dos 8 Scanners e o cálculo do TSR em um único relatório de integridade criptográfica.

## 2. Requisitos Funcionais
- **Geração de Certificado Digital Interno**: Gera uma prova SHA-256 da saúde, rigor e métricas de desempenho de cada execução do sistema.
- **Relatório Unificado**: Consolida `SpecVerifier`, `AgentEvalHarness`, `SuperRigorPipeline` e `EvolutionRegistry`.
- **Interface da Classe `InternalAuditHarness`**:
  - `generate_audit_certificate() -> Dict[str, Any]`
  - `verify_internal_integrity() -> Dict[str, Any]`
