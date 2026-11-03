---
spec_id: SPEC-935-R1019
title: Cadeia de modelos do agente primário
component: integrations.opencode_cli
status: implemented
test_file: tests/test_r1019_primary_model_chain.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1019-1:
      - "tests/test_r1019_primary_model_chain.py::test_primary_agent_uses_ollama_cloud_head"
    R1019-2:
      - "tests/test_r1019_primary_model_chain.py::test_primary_fallbacks_prefer_openai_then_opencode_go"
    R1019-3:
      - "tests/test_r1019_primary_model_chain.py::test_global_model_and_other_agents_are_unchanged"
    R1019-4:
      - "tests/test_r1019_primary_model_chain.py::test_openai_provider_declares_fallback_model"
    R1019-5:
      - "tests/test_r1019_primary_model_chain.py::test_config_is_reproducible_and_uses_env_placeholders"
---

# SPEC-935-R1019 — Cadeia de modelos do agente primário

**Estado:** implementado e testado localmente; comportamento de fallback em
runtime não verificado.
**Decisão do operador:** o agente primário `marceloclaro` usa Ollama Cloud
`deepseek-v4.1-flash` como cabeça e declare OpenAI → OpenCode Go como
alternativas.

## Objetivo

Tornar explícita, no `opencode.json` gerado, a cadeia de modelos do agente
primário, sem alterar o modelo global nem a política dos demais agentes:

1. cabeça: `ollama-cloud/deepseek-v4.1-flash`;
2. primeira alternativa: `openai/gpt-6.1-sol`;
3. segunda alternativa: `opencode-go/deepseek-v4.1-flash`;
4. alternativa final capaz: `opencode-go/deepseek-v4-pro`.

## Escopo

- `integrations/opencode_cli.py`: constantes da cadeia e bloco do primário.
- `opencode.json`: regenerado a partir do gerador.
- `tests/test_r1019_primary_model_chain.py`: contrato determinístico.
- `tests/test_r982_fixacao_modelo_agentes_literarios.py`: a regra antiga de
  “primário sem modelo fixo” é substituída pela decisão R1019; a proteção dos
  agentes literários permanece.

Não alterar:
- o modelo global `ollama-local/llama3.2`;
- a cadeia dos demais agentes;
- credenciais, preços ou cotas;
- a política de custo dos literários.

## Contrato

- O primário declara `model` e `options.model_fallbacks`.
- `options.model_economy.head` é a cabeça Ollama Cloud.
- O provedor OpenAI declara o modelo de fallback `gpt-6.1-sol`.
- `opencode.json` é reproduzível por `build_config()`.
- Chaves permanecem como placeholders `{env:...}`; nenhum segredo é gravado.

## Critérios de aceitação executáveis (RED → GREEN → REFACTOR)

- `R1019-1` — O primário usa `ollama-cloud/deepseek-v4.1-flash`; a economia
  declara a mesma cabeça.
- `R1019-2` — A cadeia começa com OpenAI e depois OpenCode Go, na ordem
  aprovada.
- `R1019-3` — O modelo global continua `ollama-local/llama3.2`; somente o
  primário recebe a cabeça Ollama Cloud.
- `R1019-4` — O provedor OpenAI declara `gpt-6.1-sol`.
- `R1019-5` — `build_config()` reproduz `opencode.json` e usa placeholders de
  ambiente para OpenAI e OpenCode Go.

## Evidência e limites

O teste verifica a configuração gerada, não uma chamada real. A cadeia é
declarativa: o OpenCode pode não trocar de executor em toda falha, e a
disponibilidade/cota de cada provedor precisa ser observada no runtime. Ollama
Cloud é tratado como assinatura/cota; OpenAI e OpenCode Go podem gerar cobrança
por token. Nenhum custo, latência ou qualidade foi medido nesta rodada.
