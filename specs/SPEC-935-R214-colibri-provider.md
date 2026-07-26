---
spec_id: SPEC-935-R214
title: "Colibri Engine Provider Integration"
component: integrations/colibri_provider.py
test_file: tests/test_r214.py
status: green
---

# SPEC-935-R214: Colibri Engine Provider Integration
=====================================================

## 1. Visão Geral
Integração do motor de inferência MoE local **Colibri** (`colibri-engine` / OLMoE / GLM-5.2) ao `opencode-ecosystem-core` como um provedor de modelos de primeira classe em `integrations/colibri_provider.py`.

## 2. Requisitos Funcionais
- **Configuração de Porta Não-Conflitante**: Por padrão utilizar a porta `8090` (ou customizável via `COLIBRI_PORT` ou argumento), evitando conflito com a porta `8080` do ecossistema.
- **Interface da Classe `ColibriProvider`**:
  - `complete(prompt, model="olmoe-1b-7b", max_tokens=512, temperature=0.7)` -> `Dict[str, Any]`
  - `health_check()` -> `Dict[str, Any]`
  - `is_available()` -> `bool`
- **Modelos Suportados**:
  - `olmoe-1b-7b` (OLMoE 1B/7B MoE int4)
  - `glm-5.2-colibri` (GLM-5.2 744B MoE int4)

## 3. Requisitos Não-Funcionais
- Tratamento de exceções e timeout gracioso.
- Compatibilidade com API OpenAI (`/v1/chat/completions`).
- Respostas estritamente formatadas em português brasileiro formal quando solicitado.

## 4. Estrutura de Testes
- Testes unitários em `tests/test_r214.py` cobrindo inicialização, listagem de modelos, checagem de saúde e chamadas de completude.
