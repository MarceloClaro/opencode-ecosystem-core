---
spec_id: SPEC-935-R272
title: Correção e polimento dos agentes literários para retornos não vazios
component: agents/catalog/literary-*.md + integrations/opencode_cli.py
status: verified
test_file: tests/test_r272_literary_agents_output_contract.py
---

# SPEC-935-R272 — Agentes literários: contrato de saída robusto

## Problema

Durante o ciclo R271, as chamadas aos agentes literários especializados (`literary-*`) foram concluídas pelo orquestrador de subtarefas, mas retornaram `task_result` vazio. Isso inviabilizou um parecer multiagente efetivo e exigiu consolidação direta pelo orquestrador.

## Hipótese inicial

Os agentes literários criados em R268 têm prompts conceituais, porém possivelmente não contêm um protocolo explícito, imperativo e testável de **resposta final obrigatória**. Em subagentes, prompts sem contrato de saída rígido podem resultar em execução silenciosa, resumo omitido, ou conclusão sem conteúdo útil.

## Objetivo

Diagnosticar, corrigir e polir os arquivos `agents/catalog/literary-*.md` para que cada agente literário especializado declare um contrato final de saída não vazio, estruturado e seguro, com guarda anti-overclaim.

## Critérios de aceitação

1. Todos os agentes `literary-*.md` devem conter seção explícita `## Contrato de saída obrigatório`.
2. O contrato deve instruir que a resposta final **nunca pode ser vazia**.
3. O contrato deve exigir campos ou blocos: `veredito`, `strengths`, `risks`, `recommendations`, `safe_claim` e `limites`.
4. O contrato deve conter fallback: se não houver dados suficientes, retornar diagnóstico de insuficiência com perguntas/necessidades, não silêncio.
5. Cada agente deve declarar guarda anti-overclaim: não substituir crítica humana, corpus comparativo, revisão externa, peer review ou parecer editorial profissional.
6. Cada agente deve mencionar pelo menos um scanner literário ou de pesquisa literária compatível com sua especialidade.
7. O agente `literary-orchestrator-phd` deve conter protocolo de consolidação e validação de retornos de subagentes, incluindo detecção de retorno vazio.
8. O agente `literary-research-scholar-phd` deve conter protocolo explícito para ausência de busca externa real e exigência de separar evidência interna de validação externa.
9. `opencode.json` deve ser regenerado e conter os prompts atualizados dos agentes literários.
10. Testes direcionados devem passar.
11. Doctor final não deve apresentar falhas críticas novas.

## Não escopo

- Não modificar a API do `task` tool.
- Não prometer que o runtime externo jamais retornará vazio; a correção é contratual/estrutural nos prompts e verificável por configuração.
- Não alterar o texto de `Molambudos`, scanners ou relatórios R270/R271.

## Diagnóstico — 2026-07-27

Achados:

1. Os agentes literários R268 existiam e eram carregados no catálogo, mas tinham prompts curtos e conceituais, sem seção imperativa de resposta final obrigatória.
2. Diferentemente de agentes funcionais como `honest-critic-agent`, os agentes `literary-*` não declaravam formato de saída mínimo. Em execução R271, isso resultou em `task_result` vazio.
3. Os agentes literários usavam modelos específicos (`openai/gpt-4.1` e `openai/o3`). Embora constem no provider, essa escolha adiciona risco de instabilidade/silêncio no runtime de subtarefas; foram padronizados em `openai/gpt-4o` para comportamento conversacional mais previsível dentro da configuração atual.
4. Após a correção em disco e regeneração de `opencode.json`, smoke tests via `task` na **mesma sessão** ainda retornaram vazios para agentes literários, enquanto `honest-critic-agent` respondeu normalmente. Isso indica que a sessão atual provavelmente mantém definições de agentes cacheadas, pois `opencode.json`/arquivos de agente não são hot-reloaded.

Correções aplicadas:

- Todos os oito agentes `literary-*.md` passaram a usar `model: openai/gpt-4o`.
- Todos receberam seção `## Contrato de saída obrigatório`.
- Todos declaram que a resposta final nunca pode ser vazia.
- Todos exigem blocos `veredito`, `strengths`, `risks`, `recommendations`, `safe_claim` e `limites`.
- Todos incluem fallback para `dados insuficientes`.
- Todos reforçam `crítica humana`, `corpus comparativo`, `validação externa`, revisão especializada/peer review e anti-overclaim.
- `literary-orchestrator-phd` recebeu protocolo de detecção de `retorno vazio`, fallback de consolidação e proibição de declarar parecer multiagente quando subagentes não retornarem conteúdo.
- `literary-research-scholar-phd` recebeu protocolo explícito para `sem busca externa real`, separando `evidência interna` de `validação externa`, DOI/ISBN, bases e peer review.

Validações:

- RED inicial: `pytest -q tests/test_r272_literary_agents_output_contract.py` falhou por ausência de contrato/modelo seguro.
- GREEN estrutural: `pytest -q tests/test_r272_literary_agents_output_contract.py` → 6 passed.
- Regressão R268: `pytest -q tests/test_r268_literary_agents_research_scanners.py` → 7 passed.
- Bateria literária R267/R268/R270/R271/R272: 29 passed.
- `python3 -m integrations.opencode_cli --check` → OK: 202 agentes, 6 MCP servers, 9 comandos.

Limitação operacional:

- Para validar runtime real dos agentes corrigidos via `task`, é necessário reiniciar o OpenCode, pois a sessão corrente preserva as definições antigas. Sem reinício, os smoke tests ainda podem refletir os prompts/modelos anteriores.

Nota posterior:

- R276 supersede a padronização em `model: openai/gpt-4o` feita em R272. Após R275 indicar suspeita de rota/model explícito e registry estático, os agentes literários passaram a usar fallback de modelo, sem `model:` explícito no frontmatter.
