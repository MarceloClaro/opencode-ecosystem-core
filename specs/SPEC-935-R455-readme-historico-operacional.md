---
spec_id: SPEC-935-R455
title: README com mapa historico preservado e diagrama operacional atual
component: README, ARCHITECTURE, tests, validation
status: red
round_id: R455
test_file: tests/test_r455_readme_historico_operacional.py
---

# SPEC-935-R455 — README com mapa histórico preservado e diagrama operacional atual

## Objetivo

Preservar o mapa histórico do `README.md` como snapshot documental, sem usá-lo
 como inventário do runtime atual, e adicionar um diagrama operacional atual que
 reflita os componentes observáveis do checkout: CLI, orquestrador,
 `AttentionRouter`, `SpecRegistry`/`SpecVerifier`/`TDDRunner`, `MetaBus`,
 `Blackboard`, MCPs configurados, agentes configurados e o subsistema MIRA.

## Critérios de Aceitação Executáveis

- `readme_preserves_historical_map_as_snapshot` — o README mantém explicitamente
  o mapa histórico e o identifica como snapshot documental, sem apresentá-lo
  como inventário atual.
- `readme_adds_current_operational_diagram` — o README inclui um diagrama
  operacional atual separado, coerente com o checkout observável e com as
  contagens/documentos autoritativos atuais.
- `current_diagram_matches_runtime_components` — o diagrama atual menciona pelo
  menos CLI, `MarceloClaroOrchestrator`, `AttentionRouter`, `SpecRegistry`,
  `SpecVerifier`, `TDDRunner`, `MetaBus`, `Blackboard`, 6 MCPs configurados,
  209 agentes configurados e `mira-presenter`.
- `readme_distinguishes_summary_from_runtime_inventory` — o README diferencia
  visão resumida, snapshot histórico e diagrama operacional atual.
- `architecture_doc_remains_consistent_with_readme` — `ARCHITECTURE.md` e o
  README apontam para o mesmo conjunto de componentes operacionais de alto
  nível, sem exigir identidade textual completa.
- `readme_restores_multiarea_richness` — o README volta a documentar, de forma
  conservadora, os principais fluxos multiárea do ecossistema: acadêmico,
  formal, jurídico, clínico, MIRA, RAG, Universidade Sintética, runtimes locais
  e quality/integrity gates.
- `docs_remain_conservative` — a atualização não introduz alegações de
  certificação externa, disponibilidade universal de serviços ou completude não
  observada do runtime.

## Estratégia TDD

1. Criar testes documentais RED para separar mapa histórico e diagrama atual.
2. Atualizar README e, se necessário, ARCHITECTURE, preservando as rotas MIRA.
3. Executar os testes documentais e registrar recibo local da rodada.

## Não objetivos

- Não transformar o README em inventário completo de todos os módulos do
  repositório.
- Não prometer que todos os MCPs, modelos ou CLIs estarão disponíveis em toda
  máquina.
