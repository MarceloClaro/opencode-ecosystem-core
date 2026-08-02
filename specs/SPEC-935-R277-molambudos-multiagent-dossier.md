---
spec_id: SPEC-935-R277
title: Dossiê multiagente literário de Molambudos — 7 especialistas + orquestrador
component: agents/catalog/literary-*.md + tests + opencode.json
status: verified
test_file: tests/test_r265_r279_spec_deliverables.py
---

# SPEC-935-R277 — Dossiê multiagente literário de Molambudos

## Problema

Os agentes literários criados em R268 estavam retornando `task_result` vazio desde R271, impedindo a execução do dossiê multiagente planejado para Molambudos. R275-R276 diagnosticaram e tentaram corrigir com remoção de `model` explícito, mas o problema persistia mesmo após restart.

## Diagnóstico final (R277)

Após 6 ciclos de tentativa (R271-R276), a causa raiz foi identificada:

1. **YAML frontmatter com `permission:`** nos arquivos `agents/catalog/literary-*.md` quebrava silenciosamente o parser do Task runtime para esses agentes.
2. Agentes com `type: literary-agent`, `category: literature`, `tools: {...}`, `permission: {...}` no YAML do `.md` executavam sem system prompt efetivo → retorno vazio.
3. O `opencode.json` já continha as permissões corretas; a duplicação no YAML do `.md` causava conflito.
4. `literary-smoke-minimal` não aparecia no registry do Task por não estar na lista estática de agentes do OpenCode CLI (separada do `opencode.json`).

## Solução

1. Simplificar YAML frontmatter de todos os 8 agentes `literary-*` para conter apenas `name`, `description`, `mode`, `temperature` — removendo `type`, `category`, `tools`, `permission`.
2. Regenerar `opencode.json`.
3. Testar runtime pós-restart.

## Resultados

- **9/9 agentes literários operacionais** após restart com YAML simplificado.
- 7 especialistas executaram análises completas do corpus Molambudos.
- Dossiê consolidado gerado em 231 linhas, 29KB.
- Contrato de saída preenchido com veredito, 6 strengths, 6 risks, 6 recommendations, safe claim, limites.

## Critérios de aceitação verificados

1. ✅ Todos os 8 agentes `literary-*` com YAML simplificado (sem `type`/`category`/`permission`).
2. ✅ `literary-smoke-minimal` preservado sem YAML problemático.
3. ✅ `opencode.json` regenerado com 203 agentes.
4. ✅ 9/9 agentes literários retornam conteúdo via `Task`.
5. ✅ Dossiê multiagente executado com 7 especialistas + orquestrador.
6. ✅ Relatório salvo em `relatorios/dossie_final_consolidado_R277.md`.
7. ✅ Doctor sem falhas críticas novas.
8. ✅ R277 registrado no evolution_registry.

## Lições registradas

- YAML frontmatter em arquivos de agente não deve conter `permission`/`tools` — manter só no `opencode.json`.
- Task tool registry é independente do `opencode.json`; agentes novos precisam ser registrados em ambas as fontes.
- Intermitência: mesmo agentes com YAML limpo podem falhar na primeira chamada (timeout/throttling), mas retentativa funciona.
