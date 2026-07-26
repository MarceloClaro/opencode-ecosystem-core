---
spec_id: SPEC-935-R216
title: "Integração Completa do Ecossistema e Roteamento Inteligente do Colibri Provider"
component: integrations/model_router.py, integrations/colibri_provider.py
test_file: tests/test_r216_full_ecosystem_integration.py
status: green
---

# SPEC-935-R216 — Integração Completa do Ecossistema e Roteamento do Colibri
=============================================================================

## 1. Visão Geral
Esta especificação consolida a integração completa de todos os provedores e componentes do **OpenCode Ecosystem Core**, incluindo o motor local de alta velocidade **Colibri** (`olmoe-1b-7b` e `glm-5.2-colibri`) no `ModelRouter` (`integrations/model_router.py`).

## 2. Requisitos Funcionais
- **Integração do Colibri no ModelRouter**:
  - Adicionar o loader `_get_colibri()` ao `ModelRouter`.
  - Mapear `olmoe-1b-7b` e `glm-5.2-colibri` nos perfis de roteamento de tarefas `fast`, `coding`, `reasoning` e `writing`.
- **Roteamento Inteligente e Fallback**:
  - Permitir a seleção automática do Colibri quando o usuário solicitar modelos locais de ultra-baixa latência (MoE).
- **Validação de Saúde do Ecossistema**:
  - Garantir 100% de aprovação no `doctor` e na suíte de testes.
