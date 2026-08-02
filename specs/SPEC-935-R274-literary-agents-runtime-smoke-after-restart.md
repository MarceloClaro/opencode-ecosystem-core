---
spec_id: SPEC-935-R274
title: Smoke tests runtime dos agentes literários após reinício do OpenCode
component: agents/catalog/literary-*.md + projetos/molambudos/Molambudos_VictoriaRegia/relatorios
status: verified
test_file: tests/test_r274_literary_agents_runtime_smoke.py
---

# SPEC-935-R274 — Validação runtime pós-reinício dos agentes literários

## Objetivo

Após o usuário reiniciar o OpenCode, executar smoke tests e pareceres curtos com todos os agentes `literary-*`, validando se os contratos de saída corrigidos em R272 agora produzem respostas não vazias em runtime real.

## Agentes avaliados

1. `literary-orchestrator-phd`
2. `literary-narratology-architect-phd`
3. `literary-style-voice-phd`
4. `literary-character-psychology-phd`
5. `literary-symbolic-imagery-phd`
6. `literary-ethics-trauma-phd`
7. `literary-innovation-editorial-phd`
8. `literary-research-scholar-phd`

## Entradas

- `relatorios/molambudos_full_literary_scan_R270.md`
- `relatorios/molambudos_critical_dossier_R271.md`
- `relatorios/molambudos_repeat_analysis_R273.md`

## Saídas esperadas

- `relatorios/literary_agents_runtime_smoke_R274.json`
- `relatorios/literary_agents_runtime_smoke_R274.md`

## Critérios de aceitação

1. Os oito agentes `literary-*` devem ser tentados via `task` runtime.
2. O relatório JSON deve registrar, para cada agente, `returned_content`, `content_length`, `has_required_contract_fields` e uma síntese curta.
3. O relatório Markdown deve declarar de forma explícita se o problema de retorno vazio foi resolvido após reinício.
4. Se algum agente ainda retornar vazio, o relatório deve listar o agente e a remediação recomendada.
5. Se agentes retornarem conteúdo, o relatório deve preservar os blocos do contrato: `veredito`, `strengths`, `risks`, `recommendations`, `safe_claim` e `limites` sempre que detectáveis.
6. O relatório deve conter guarda anti-overclaim: pareceres são smoke tests/leituras internas, não validação literária externa.
7. Testes direcionados devem passar.
8. Doctor final não deve apresentar falhas críticas novas.

## Não escopo

- Não alterar os agentes novamente neste ciclo, salvo se o relatório indicar falha posterior.
- Não alterar o texto de `Molambudos`.
- Não realizar busca bibliográfica externa real.

## Resultado — 2026-07-27

Artefatos gerados:

- `projetos/molambudos/Molambudos_VictoriaRegia/relatorios/literary_agents_runtime_smoke_R274.json`
- `projetos/molambudos/Molambudos_VictoriaRegia/relatorios/literary_agents_runtime_smoke_R274.md`

Resultado runtime:

- `literary-orchestrator-phd`: retornou vazio.
- `literary-narratology-architect-phd`: retornou vazio.
- `literary-style-voice-phd`: retornou vazio.
- `literary-character-psychology-phd`: retornou vazio.
- `literary-symbolic-imagery-phd`: retornou vazio.
- `literary-ethics-trauma-phd`: retornou vazio.
- `literary-innovation-editorial-phd`: retornou vazio.
- `literary-research-scholar-phd`: retornou vazio.

Controles:

- `honest-critic-agent`: retornou conteúdo.
- `general`: retornou conteúdo.
- `docs-writer`: retornou conteúdo.

Diagnóstico:

- O `task` runtime funciona em geral.
- A falha persiste especificamente nos agentes `literary-*`.
- O problema não foi resolvido pelo reinício informado.
- Hipóteses principais: registry interno ainda não recarregou esses slugs; definição pré-compilada dos `literary-*`; falha silenciosa específica de rota/modelo desses agentes; ou bug de dispatcher para agentes recém-criados.

Validações:

- RED inicial: `pytest -q tests/test_r274_literary_agents_runtime_smoke.py` falhou antes dos artefatos existirem.
- GREEN: `pytest -q tests/test_r274_literary_agents_runtime_smoke.py` → 4 passed.

Remediação recomendada:

- Criar agente literário mínimo com slug novo para isolar cache por nome.
- Testar remoção temporária do campo `model` ou usar padrão de agente funcional.
- Inspecionar logs do dispatcher/Task tool para task IDs vazios.
- Até correção runtime, continuar declarando fallback do orquestrador para pareceres literários.
