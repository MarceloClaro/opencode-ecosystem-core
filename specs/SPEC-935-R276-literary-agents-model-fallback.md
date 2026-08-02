---
spec_id: SPEC-935-R276
title: Agentes literários sem model explícito para testar fallback de runtime
component: agents/catalog/literary-*.md + tests + opencode.json
status: verified
test_file: tests/test_r276_literary_agents_model_fallback.py
---

# SPEC-935-R276 — Remediação por fallback de modelo nos agentes literários

## Problema

R275 indicou que agentes novos com `model` explícito (`literary-*`, `kdp-*`) retornam vazio, enquanto controles antigos sem evidência de `model` explícito retornam conteúdo. A próxima hipótese a testar é que o campo `model` explícito desses agentes aciona rota/model provider incompatível ou silenciosa no runtime de subtarefas.

## Objetivo

Remover temporariamente `model` explícito dos agentes `literary-*`, mantendo contratos de saída, para permitir que o runtime use fallback/modelo padrão do ambiente. Regenerar `opencode.json` e validar estruturalmente.

## Critérios de aceitação

1. Os oito agentes `literary-*` principais não devem conter `model:` no frontmatter.
2. `literary-smoke-minimal` também deve permanecer sem `model:` explícito.
3. Todos os agentes literários devem manter `mode: subagent`, `temperature`, descrição e contrato de saída obrigatório.
4. Os testes R268/R272 devem ser atualizados para aceitar fallback de modelo documentado, sem exigir `model` explícito.
5. `opencode.json` regenerado não deve incluir `model` nos agentes `literary-*` principais nem em `literary-smoke-minimal`.
6. Relatório R276 deve registrar a mudança e avisar que validação runtime real exige nova sessão/registry recarregado.
7. Testes direcionados devem passar.
8. Doctor final não deve apresentar falhas críticas novas.

## Não escopo

- Não alterar KDP neste ciclo.
- Não afirmar que os agentes runtime foram corrigidos até executar smoke tests em sessão realmente recarregada.
- Não alterar textos ou relatórios literários de `Molambudos`.

## Resultado — 2026-07-27

Mudança aplicada:

- Removido `model:` explícito dos oito agentes `literary-*` principais.
- `literary-smoke-minimal` já permanecia sem `model:`.
- `opencode.json` regenerado com 203 agentes.

Artefatos:

- `projetos/molambudos/Molambudos_VictoriaRegia/relatorios/literary_agents_model_fallback_R276.json`
- `projetos/molambudos/Molambudos_VictoriaRegia/relatorios/literary_agents_model_fallback_R276.md`

Validações:

- RED inicial: `pytest -q tests/test_r276_literary_agents_model_fallback.py` falhou por `model:` ainda presente e relatório ausente.
- GREEN: `pytest -q tests/test_r276_literary_agents_model_fallback.py` → 3 passed.
- Regressão R268/R272/R275/R276 → 20 passed.
- `python3 -m integrations.opencode_cli --check` → OK: 203 agentes.
- Doctor final sem falhas críticas novas.

Smoke na mesma sessão:

- `literary-style-voice-phd` continuou retornando vazio.
- Controle `code-reviewer` retornou conteúdo.

Interpretação:

- Remover `model:` é uma remediação estrutural coerente com o diagnóstico de R275, mas a sessão/registry atual ainda não executa corretamente os `literary-*`.
- Próximo teste exige sessão/registry realmente recarregado; se persistir, o problema deve ser investigado fora dos arquivos de agente, na camada dispatcher/Task registry.
