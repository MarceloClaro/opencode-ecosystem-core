---
spec_id: SPEC-108
title: Integração OpenCode Go + OpenCode Zen + Antigravity com SDD/TDD
component: integrations.opencode_go, integrations.opencode_zen, integrations.model_router
test_file: tests/test_opencode_go_zen.py
status: verified
cycle: R108
---

# SPEC-108 — Integração OpenCode Go + OpenCode Zen + Antigravity

## Objetivo

Integrar os providers **OpenCode Go** e **OpenCode Zen** ao ecossistema OpenCode Core,
com roteamento inteligente de modelos via `ModelRouter`, cumprimento obrigatório de
protocolo SDD/TDD em todas as tarefas, e exposição como ferramentas MCP no
`antigravity-bridge`.

---

## Critérios de Aceitação

### CA-1: Provider OpenCode Go registrado e funcional
- `OpenCodeGoProvider` instância sem erros
- Método `list_models()` retorna ≥ 4 modelos
- Modelos incluem ao menos: `kimi-k2.7-code`, `deepseek-v4-pro`, `glm-5.2`, `qwen3.7-max`

### CA-2: Provider OpenCode Zen registrado e funcional
- `OpenCodeZenProvider` instância sem erros
- Método `list_models()` retorna ≥ 3 modelos curados
- Modelos incluem ao menos: `gpt-5.5`, `claude-opus-4`, `gemini-2.5-pro`

### CA-3: ModelRouter roteia corretamente
- `ModelRouter.route(task_type="coding")` → retorna modelo do perfil de coding
- `ModelRouter.route(task_type="reasoning")` → retorna modelo do perfil de reasoning
- `ModelRouter.route(task_type="academic")` → retorna modelo do perfil de academic

### CA-4: Integração SDD/TDD nos providers
- Toda requisição ao provider cria/vincula uma `Specification` no `SpecRegistry`
- `SpecVerifier.verify()` é chamado após cada resposta
- Falha de verificação propaga `SpecVerificationError`

### CA-5: MCP tools disponíveis no antigravity-bridge
- `antigravity_route_model` disponível no servidor MCP
- `antigravity_list_providers` disponível no servidor MCP
- Chamadas retornam JSON estruturado com provider, model, spec_id

### CA-6: opencode.json atualizado
- Seção `"provider"` com `opencode-go` e `opencode-zen`
- Seção `"model"` com modelo padrão definido
- Novos comandos: `sdd`, `tdd`, `models`

### CA-7: Agentes de provider no catálogo
- `opencode-go-agent.md` existe em `agents/catalog/`
- `opencode-zen-agent.md` existe em `agents/catalog/`
- Ambos aparecem no `opencode.json`

### CA-8: Testes TDD passam
- `tests/test_opencode_go_zen.py` com ≥ 12 testes
- Todos passam com `pytest -q`
- Cobertura dos módulos novos ≥ 80%

---

## Invariantes

- O protocolo SDD/TDD é **sempre** executado; nenhuma entrega pode ser enviada sem verificação de spec
- As chaves de API são sempre lidas de variáveis de ambiente ou `~/.local/share/opencode/auth.json`
- O `ModelRouter` nunca acessa a rede diretamente; delega ao provider selecionado
- O `MetaBus` recebe evento após cada roteamento bem-sucedido

## Non-goals

- Não implementar autenticação OAuth completa (usa `/connect` do OpenCode TUI)
- Não executar chamadas LLM reais nos testes (mock via `unittest.mock`)
- Não substituir o orquestrador `marceloclaro` como ponto de entrada primário
