---
spec_id: SPEC-935-R275
title: Isolamento da falha runtime dos agentes literários por slug/model/registry
component: agents/catalog + opencode.json + projetos/molambudos/Molambudos_VictoriaRegia/relatorios
status: verified
test_file: tests/test_r275_literary_agent_runtime_isolation.py
---

# SPEC-935-R275 — Isolar falha runtime dos agentes literários

## Problema

Em R274, após reinício informado, os oito agentes `literary-*` continuaram retornando `task_result` vazio, enquanto controles (`honest-critic-agent`, `general`, `docs-writer`) retornaram conteúdo. É necessário isolar se a falha vem de slug antigo/cache, modelo explícito, formato do agente, categoria literária ou dispatcher/registry.

## Objetivo

Criar um agente literário mínimo com slug novo e formato de frontmatter reduzido, regenerar `opencode.json`, executar smoke tests comparativos e produzir relatório diagnóstico.

## Hipóteses testadas

1. **Slug/cache**: agentes `literary-*` antigos continuam mapeados para definições inválidas/cacheadas.
2. **Modelo explícito**: `model: openai/gpt-4o` nos agentes literários pode induzir rota silenciosa específica.
3. **Formato/frontmatter**: campos extras (`type`, `category`, `tools`) podem interferir em algum registry externo.
4. **Categoria/descrição**: agentes recém-criados do catálogo podem não ser incorporados corretamente ao runtime de subtarefas.

## Saídas esperadas

- `agents/catalog/literary-smoke-minimal.md`
- `relatorios/literary_agent_runtime_isolation_R275.json`
- `relatorios/literary_agent_runtime_isolation_R275.md`

## Critérios de aceitação

1. Criar agente `literary-smoke-minimal` com slug novo, frontmatter mínimo permitido, sem `model` explícito, com contrato de saída não vazio.
2. `opencode.json` deve conter `literary-smoke-minimal` após regeneração.
3. Executar smoke tests comparando: agente literário mínimo, agentes literários antigos, agente KDP novo e agentes de controle antigos.
4. O relatório JSON deve registrar `returned_content`, `content_length`, `has_required_contract_fields` e síntese para cada agente tentado.
5. O relatório Markdown deve concluir qual hipótese ficou mais provável.
6. Se o agente mínimo não puder ser chamado via `task` por não estar no registry atual, registrar isso explicitamente.
7. Testes direcionados devem passar.
8. Doctor final não deve apresentar falhas críticas novas.

## Não escopo

- Não alterar novamente os oito agentes `literary-*` neste ciclo.
- Não alterar `Molambudos`.
- Não afirmar que uma correção runtime está concluída se os smoke tests não passarem.

## Resultado — 2026-07-27

Artefatos gerados:

- `agents/catalog/literary-smoke-minimal.md`
- `projetos/molambudos/Molambudos_VictoriaRegia/relatorios/literary_agent_runtime_isolation_R275.json`
- `projetos/molambudos/Molambudos_VictoriaRegia/relatorios/literary_agent_runtime_isolation_R275.md`

Achados:

- `literary-smoke-minimal` entrou no `opencode.json`; a configuração passou a ter 203 agentes.
- O `Task` tool respondeu `Unknown agent type` para `literary-smoke-minimal`, evidenciando que o registry de subagentes usado nesta conversa não reflete automaticamente o `opencode.json` regenerado.
- `literary-style-voice-phd` continuou retornando vazio.
- Agentes KDP novos (`kdp-final-qa-phd`, `kdp-orchestrator-phd`) também retornaram vazio.
- Controles antigos (`code-reviewer`, `technical-writer`, `general`, `honest-critic-agent`) retornaram conteúdo.

Hipótese mais provável:

- Registry/dispatcher estático ou parcialmente recarregado para agentes novos; rota/model explícito também permanece suspeito.

Validações:

- RED inicial: `pytest -q tests/test_r275_literary_agent_runtime_isolation.py` falhou antes do agente/relatórios existirem.
- GREEN: `pytest -q tests/test_r275_literary_agent_runtime_isolation.py` → 4 passed.
- `python3 -m integrations.opencode_cli --check` → OK: 203 agentes.
- Doctor final sem falhas críticas novas.
