---
spec_id: SPEC-935-R364
title: TerminologyGraphAgent — grafo terminológico trilíngue
component: translation/terminology_graph.py + agents/catalog/terminology-graph-agent.md
status: verified
test_file: tests/test_r364_terminology_graph.py
---

# SPEC-935-R364 — TerminologyGraphAgent

**Contrato funcional:** OCB-TERMINOLOGY-GRAPH-001
**Data:** 2026-08-02
**Posição no pipeline:** consumidor dos deltas `propose_upsert` produzidos por
`translation/cultural_episteme.py::build_terminology_delta` (SPEC-935-R359),
que até aqui não tinham destino implementado.

## 1. Objetivo

Implementar o grafo terminológico trilíngue (PT-BR/EN/ZH-CN) que o
CulturalEpistemeAgent referencia: registro versionado de termos, símbolos e
instituições com traduções preferidas, traduções proibidas e decisão humana
explícita. O grafo detecta conflito terminológico (`TERM_CONFLICT`) e deriva
simbólica (`SYMBOL_DRIFT`) em segmentos traduzidos, e produz um **relatório de
consistência medido** — números observados, nunca metas anunciadas.

**Limite epistêmico:** o grafo não decide equivalência cultural. Ele registra
propostas, exige aprovação humana identificada para ativá-las e reporta
inconsistências observáveis por regra. Ausência de conflito ≠ tradução correta.

## 2. Modelo de dados

- `TerminologyGraph(graph_id)` com `revision` inteira monotônica (começa em 0;
  cada mutação aceita incrementa).
- Entrada de termo: `source_term` (chave normalizada casefold), `entity_type`
  (`symbol`, `institution`, `historical`, `clinical`, `regional`, `general`),
  `preferred_en`, `preferred_zh_cn`, `preserve_portuguese`,
  `forbidden_translations`, `rationale`, `provenance`, `approval_state`
  (`proposed` → `approved` | `rejected`), `decided_by` (obrigatório na
  aprovação/rejeição; nunca vazio, nunca "agent").

## 3. Comportamento contratual

1. `apply_delta(delta)` valida o delta com
   `cultural_episteme._validate_terminology_delta` (mesmo contrato; nada de
   segundo schema) e:
   - rejeita `base_graph_id` divergente (`ContractError`);
   - rejeita `base_revision` obsoleta (concorrência otimista, fail-closed);
   - é idempotente por `delta_id` (reaplicar não duplica nem re-incrementa);
   - insere/atualiza como `proposed` — **nunca** ativa sozinho.
2. `approve(source_term, reviewer)` / `reject(source_term, reviewer)`:
   `reviewer` humano identificado obrigatório; aprovar termo inexistente ou já
   decidido → `ContractError`.
3. `check_segment(source_text, translated_text, target_language)`:
   - termo aprovado presente no fonte + tradução proibida presente no alvo →
     achado `TERM_CONFLICT` (severity `high`);
   - termo aprovado com `entity_type=symbol` presente no fonte + tradução
     preferida ausente no alvo → `SYMBOL_DRIFT` (severity `medium`);
   - termo com `preserve_portuguese=True` presente no fonte e ausente no
     alvo → `TERM_CONFLICT` (severity `high`);
   - termos `proposed` **não** geram achados (não aprovados = sem autoridade);
   - códigos vêm de `cultural_episteme.ISSUE_CODES` (sem inventar códigos).
4. `consistency_report(pairs)` sobre lista de (fonte, alvo, idioma): retorna
   contagens medidas — ocorrências de termos aprovados, ocorrências
   consistentes, `consistency_ratio` (ou `None` se não houve ocorrência) e
   achados por código. O relatório declara `"measured": true` e
   `"claim": "internal-fixture-measurement"`; nenhuma meta (98% etc.) aparece
   no código.
5. `release_gate()`: `blocked=True` enquanto houver `TERM_CONFLICT` aberto em
   `check_segment` acumulado ou termo `proposed` de `entity_type` de alto
   risco (`symbol`, `historical`, `clinical`) sem decisão humana. Fail-closed.
6. Persistência: `to_dict()`/`from_dict()` + `save(path)`/`load(path)` JSON
   estável (round-trip sem perda; `revision` preservada).

## 4. Critérios de aceitação

1. Delta gerado por `build_terminology_delta` real é aceito sem adaptação.
2. Idempotência, concorrência otimista e recusa de graph_id divergente.
3. Aprovação exige humano; estados inválidos falham fechado.
4. `check_segment` detecta os três padrões acima e ignora termos `proposed`.
5. Relatório de consistência traz apenas números medidos.
6. Round-trip de persistência preserva termos, estados e revisão.
7. Agent card A2A registrável pelo catalog_loader (episteme:
   `hermeneutico_interpretativo` explícita no frontmatter).
8. Suíte do ciclo verde; falhas pré-existentes do repo não aumentam.
