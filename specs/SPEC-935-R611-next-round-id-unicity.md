# SPEC-935-R611: Sequência de round_id não pode colidir com specs existentes

## Objetivo
Eliminar a colisão entre o numeral derivado por `EvolutionRegistry.next_round_id()`
(evolution/cycles.py:138) e os R-ids das especificações em `specs/SPEC-935-R*.md`.
Ciclos de evolução e specs compartilham o mesmo espaço de nomes numerado (R###);
a sequência deve considerar AMBAS as fontes.

## Motivação (fato observado, 2026-09-29)
`record()` sem `round_id` explícito derivava o numeral máximo apenas dos ciclos
carregados de `cycles.json` (máx. R606). Como `specs/SPEC-935-R607.md` já existia,
o ciclo do reparo das descrições do catálogo foi gravado como **R607** — numeral
já ocupado por uma spec. Mitigação imediata: `round_id="R608"`/`"R609"` explícitos;
correção permanente é o escopo desta spec.

## Mudanças
- `evolution/cycles.py`: novos `SPECS_PATH` (default `<raiz>/specs`) e
  `EVOLUTION_SPECS_PATH` (override de teste).
- `EvolutionRegistry.__init__(state_path=None)`: lê `EVOLUTION_STATE_PATH` por
  chamada (isolamento hermético).
- `next_round_id()`: além dos ciclos, varre `specs_dir/SPEC-935-R*.md` e
  devolve `R(max+1)` nas duas fontes.

## Critérios de aceitação (gate SDD/TDD)
- [B1] `next_round_id()` considera o maior numeral entre ciclos E specs.
- [B2] `record()` sem `round_id` herda a sequência sem colidir com specs.
- [B3] Diretório de specs ausente não quebra (fallback base R46).
- [B4] Isolamento via `EVOLUTION_STATE_PATH`/`EVOLUTION_SPECS_PATH` (tmp_path).
- [B5] Sem regressão na série `test_r462*`/`test_r581*`/`test_r488*`.

## Verificação
`pytest tests/test_r611_round_id_unique.py` — 4 testes verdes.