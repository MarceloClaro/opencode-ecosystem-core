---
spec_id: SPEC-935-R225
title: "Harness de Validação Externa Auditável para Benchmarks (External Validation Harness)"
component: benchmarks/external_validation_harness.py, mci/metacognitive_evaluator.py
test_file: tests/test_r225_external_validation_harness.py
status: green
---

# SPEC-935-R225 — Harness de Validação Externa Auditável
=========================================================

## 1. Visão Geral
Esta especificação introduz o **`ExternalValidationHarness`**, uma infraestrutura para importação, verificação criptográfica (hash SHA-256) e auditoria de resultados de benchmarks externos de terceiros (ex.: GAIA, SWE-bench, HumanEval).

## 2. Requisitos Funcionais
- **Auditoria de Evidência Externa**: Valida relatórios de avaliação de terceiros via assinatura digital, hash SHA-256 e score mínimo ($\ge 90.0\%$).
- **Integração com `MetacognitiveEvaluator`**: Alimenta a flag `external_validation=True` somente se a prova criptográfica do relatório de avaliação for 100% verificada.
- **Interface da Classe `ExternalValidationHarness`**:
  - `verify_external_report(report_path: str) -> Dict[str, Any]`
  - `register_validation_proof(evaluator_id: str, score: float, signature: str) -> Dict[str, Any]`
