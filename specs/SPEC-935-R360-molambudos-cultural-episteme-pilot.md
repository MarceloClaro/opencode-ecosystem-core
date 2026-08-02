---
spec_id: SPEC-935-R360
title: Piloto de mediação cultural PT-BR→EN-US/ZH-CN em Molambudos
component: validacao_externa/cultural_episteme/molambudos_r360_*
status: green
test_file: tests/test_r360_cultural_episteme_pilot.py
---

# SPEC-935-R360 — Piloto CulturalEpistemeAgent em Molambudos

**Estado:** green
**Data:** 2026-08-01
**Base:** SPEC-935-R355, R356, R357, R358 e R359

## 1. Objetivo

Executar o `cultural-episteme-agent` em segmentos reais e culturalmente
sensíveis de *Molambudos*, comparando PT-BR→EN-US e PT-BR→ZH-CN. O piloto deve
identificar riscos, produzir alternativas condicionais e propostas de delta
terminológico, sem editar automaticamente o manuscrito nem alegar validação
cultural externa.

## 2. Unidades do piloto

1. `Curral do Governo` — instituição histórica e metáfora desumanizante.
2. `retirante(s)` — categoria histórica/regional de deslocamento pela seca.
3. `Rasga Mortalha` — símbolo folclórico, religioso e ominoso.
4. `molambudo(s)` — denominação social, insulto e neologismo central da obra.
5. `Hospital Colônia / Colônia` — nome institucional e memória histórica.
6. `você é o próximo` — ameaça direta e função pragmática.

Cada unidade será avaliada separadamente em EN-US e ZH-CN: **12 pareceres**.

## 3. Entradas e contexto

- excerto PT e tradução publicada no fragmento correspondente;
- perfil de voz e tipo de documento;
- período, região e proveniência editorial;
- decisões dos glossários R355/R356;
- snapshot terminológico versionado;
- contexto vizinho suficiente para evitar julgamento lexical isolado.

## 4. Gates

1. Todas as 12 execuções retornam envelope não vazio.
2. Cada envelope passa em `validate_agent_output()`; a decisão final é derivada
   por `evaluate_gate()`, nunca aceita do agente.
3. `release_gate` permanece `blocked` e `human_review_required` permanece `true`.
4. `Curral do Governo`, `Rasga Mortalha`, `molambudo` e `Colônia` não podem ser
   alterados automaticamente; qualquer delta nasce `proposed`.
5. Scores/sinais não aprovam traduções nem compensam risco histórico/ético.
6. O dossiê distingue:
   - correção mecânica de baixo risco;
   - recomendação editorial condicionada;
   - decisão terminológica de alto risco pendente de humano.
7. Saídas agregadas:
   - `validacao_externa/cultural_episteme/molambudos_r360_reviews.json`;
   - `validacao_externa/cultural_episteme/molambudos_r360_dossier.md`.
8. Testes R360 validam contagem, idiomas, unidades, bloqueios, proveniência,
   taxonomia, alternativas e deltas propostos.
9. Nenhum fragmento é editado antes da conclusão e classificação do dossiê.
10. Anti-overclaim: o resultado é auditoria heurística interna; revisão humana
    bilíngue, histórica e cultural continua obrigatória.

## 5. TDD

1. **RED:** criar teste do formato esperado do dossiê antes dos artefatos.
2. **GREEN:** executar o agente, validar envelopes e gerar os dois artefatos.
3. **REFACTOR:** consolidar duplicações sem apagar incerteza ou dissenso.

## 6. Não escopo

- revisão integral dos 234 fragmentos;
- atualização automática do TerminologyGraph;
- aprovação para publicação;
- uso de retrotradução como prova;
- substituir tradutor, autor, historiador ou revisor qualificado.

## 7. Evidência de execução

- RED controlado: `1 passed, 6 failed`; falhas restritas à ausência inicial dos
  dois artefatos exigidos.
- 12 execuções runtime não vazias do `cultural-episteme-agent`, identificadas no
  JSON por `task_id`.
- Duas respostas foram rejeitadas por divergência entre `delta_id` e
  `idempotency_key`; as mesmas sessões corrigiram os envelopes antes da
  persistência, sem redução de alertas ou abertura do release.
- GREEN R360: `9 passed`; regressão conjunta R358--R360: `36 passed`.
- SpecVerifier executado com seis critérios programáticos: `6/6` aprovados e
  transição interna para `green`.
- BehavioralGate da finalização: permitido em nível `moderate`, trust `0.50`,
  threshold `0.40` e shadow mode explícito.
- Economia auditada: quatro stakes sofreram slashing (dois erros do gerador e
  dois deltas inválidos); três stakes foram liberados após correções/conclusão.
- Artefatos idempotentes:
  `validacao_externa/cultural_episteme/molambudos_r360_reviews.json` e
  `validacao_externa/cultural_episteme/molambudos_r360_dossier.md`.
- Gate de controle:
  `validacao_externa/cultural_episteme/molambudos_r360_control_gates.json`.
- Nenhum fragmento ou glossário foi alterado. Todos os deltas permanecem
  `proposed`; `release_gate` permanece `blocked`.
- Doctor pós-gate: 8 checks `pass`, 3 `warn`, 0 `failed`; estado global
  `degraded` por avisos preexistentes/externos.
- Ciclo `R360` registrado no EvolutionRegistry com score interno de processo
  `8.3/10`, não score de qualidade cultural; reflexões do orquestrador e do
  agente registradas no MetaBus.
- O estado `green` expressa conformidade interna SDD/TDD, não validação cultural
  externa, equivalência comprovada ou prontidão para publicação.
