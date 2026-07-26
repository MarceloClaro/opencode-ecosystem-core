---
spec_id: SPEC-935-R221
title: "Mecanismo de Autocorreção em Circuito Fechado (Self-Correction Engine)"
component: mci/self_correction.py, CORRIGENDUM.md
test_file: tests/test_r221_self_correction_engine.py
status: green
---

# SPEC-935-R221 — Motor de Autocorreção em Circuito Fechado (Closed-Loop Self-Correction Engine)
==============================================================================================

## 1. Visão Geral
Esta especificação define o motor de autocorreção em circuito fechado do ecossistema, combinando a rastreabilidade do `CORRIGENDUM.md`, a execução RED → GREEN do `SpecVerifier` e o modelo de revisão reflexiva inspirado no OpenSquilla, AutoGen e smolagents.

## 2. Requisitos Funcionais (Circuito Fechado de 4 Fases)
1. **Diagnóstico (Diagnose)**: Capturar falhas, erros de asserção ou desvios de testes.
2. **Correção (Patch/Fix)**: Gerar proposta de correção com tentativa reflexiva.
3. **Validação (Validate)**: Executar os critérios de aceitação programáticos da spec via `SpecVerifier` (RED → GREEN).
4. **Aplicação & Registro (Apply & Log)**: Aplicar as correções validadas e registrar o evento de autocorreção no `MetaBus` e no arquivo `CORRIGENDUM.md`.

## 3. Interface da Classe `SelfCorrectionEngine`
- `run_correction_cycle(spec_id: str, error_context: Dict[str, Any], fix_fn: Callable) -> Dict[str, Any]`
- `get_correction_history() -> List[Dict[str, Any]]`
