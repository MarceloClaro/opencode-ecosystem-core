---
spec_id: SPEC-935-R273
title: Repetição da análise crítica de Molambudos após polimento dos agentes literários
component: projetos/molambudos/Molambudos_VictoriaRegia/relatorios + agents/catalog/literary-*.md
status: verified
test_file: tests/test_r273_molambudos_repeat_analysis.py
---

# SPEC-935-R273 — Molambudos: repetir análise após R272

## Objetivo

Repetir a análise crítica de `Molambudos — O Diário do Paciente 1.260` após a correção/polimento dos agentes literários em R272, tentando novamente obter retornos dos agentes especializados e gerando relatório auditável com indicação honesta de origem: pareceres de agentes quando disponíveis, ou fallback do orquestrador quando a sessão ainda estiver cacheada.

## Entradas

- `relatorios/molambudos_full_literary_scan_R270.json`
- `relatorios/molambudos_full_literary_scan_R270.md`
- `relatorios/molambudos_critical_dossier_R271.json`
- agentes `agents/catalog/literary-*.md` corrigidos em R272

## Saídas esperadas

- `relatorios/molambudos_repeat_analysis_R273.json`
- `relatorios/molambudos_repeat_analysis_R273.md`

## Critérios de aceitação

1. O JSON R273 deve existir, ser serializável e declarar `spec_id: SPEC-935-R273`.
2. O Markdown R273 deve existir e conter uma análise crítica repetida em linguagem segura.
3. O relatório deve declarar se os agentes literários retornaram conteúdo na sessão atual.
4. Se houver retorno vazio, o relatório deve declarar fallback do orquestrador e não fingir parecer multiagente independente.
5. O relatório deve preservar os dados de corpus R270: 73 unidades narrativas, 45.601 palavras e 272.314 caracteres.
6. A análise deve conter pelo menos sete lentes: narratologia, estilo/voz, personagens, simbologia, ética/trauma, inovação editorial e pesquisa literária.
7. Cada lente deve conter veredito, strengths, risks, recommendations, safe_claim e limites.
8. O relatório deve conter síntese reavaliada, prioridades editoriais e guarda anti-overclaim.
9. Testes direcionados devem passar.
10. Doctor final não deve apresentar falhas críticas novas.

## Não escopo

- Não alterar o texto literário, miolo, capa ou metadados de `Molambudos`.
- Não prometer validação real dos agentes corrigidos sem reiniciar o OpenCode, pois a sessão atual pode manter definições cacheadas.
- Não realizar busca bibliográfica externa real.

## Resultado — 2026-07-27

Artefatos gerados:

- `projetos/molambudos/Molambudos_VictoriaRegia/relatorios/molambudos_repeat_analysis_R273.json`
- `projetos/molambudos/Molambudos_VictoriaRegia/relatorios/molambudos_repeat_analysis_R273.md`

Achado operacional:

- Nova rodada com sete agentes literários especializados foi executada na sessão atual.
- Todos os agentes literários ainda retornaram `task_result` vazio.
- Controle com `honest-critic-agent` retornou conteúdo normalmente.
- Interpretação: o `task` runtime funciona, mas a sessão corrente provavelmente preserva definições/modelos antigos dos agentes literários; é necessário reiniciar o OpenCode para validar os prompts corrigidos em R272.

Conteúdo entregue:

- Síntese reavaliada.
- Status explícito dos agentes literários.
- Leitura segura dos scores R270.
- Sete lentes com contrato completo: narratologia, estilo/voz, personagens, simbologia, ética/trauma, inovação editorial e pesquisa literária.
- Prioridades editoriais.
- Guarda anti-overclaim e blindagem JSON para impedir uso público dos scores como nota de mérito.

Validações:

- RED inicial: `pytest -q tests/test_r273_molambudos_repeat_analysis.py` falhou antes dos artefatos existirem.
- GREEN: `pytest -q tests/test_r273_molambudos_repeat_analysis.py` → 5 passed.
- Auditoria anti-overclaim por `honest-critic-agent`: aprovado para uso interno com ajustes; ajustes aplicados.
- Campo JSON `public_safety` adicionado com `external_validation: false`, `public_quality_grade: null`, `scores_must_not_be_used_as_public_merit_rating: true` e `public_safe_formulation`.
