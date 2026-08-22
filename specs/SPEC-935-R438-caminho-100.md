---
spec_id: SPEC-935-R438
component: evolution.gap-closure-100
title: Caminho para 100 — Fechamento dos 5 Gaps Residuais
version: 1.0.0
status: green
test_file: tests/test_r438_caminho_100.py
---

# SPEC-935-R438 — Caminho para 100: Fechamento dos 5 Gaps Residuais

## Meta
- **Ciclo**: R438
- **Alvo**: 10.0 (100) — fechar os 5 gaps apontados na auditoria R437 para atingir excelência plena
- **Gaps a fechar**:
  1. `specs/loops/` sem dumps dos LoopSpecs em memória (`dsh-reasoning-97`, `harness-reasoning-97`)
  2. `UnifiedSearcher` sem `web_searcher` padrão (Antigravity) quando `provider=web`
  3. `reversa_universal/engine.py` sem fallback `tomli` quando `tomllib` ausente (<3.11)
  4. `UniversalHarnessBridge` reusa `DeepSeekWorkerPool` com override de prefixo (acoplamento)
  5. `evolution/cycles.py:average_score` não documentado como média móvel (confusão com gate)

## Arquitetura

### G1 — LoopSpecs em disco
Gerar `specs/loops/dsh-reasoning-97.md` e `specs/loops/harness-reasoning-97.md` via `loop_spec_registry` dump no formato idêntico a `scientific-discovery-loop.md` (trigger, objetivo, arquitetura, estados terminais, guardrails). `doctor` passa a reportar `loop_specs: pass` quando arquivos existem.

### G2 — Antigravity como web_searcher padrão
`rag/enhanced_search_rag.py:UnifiedSearcher.__init__` tenta instanciar `AntigravityBridge` como `web_searcher` padrão quando não injetado. Novo wrapper `AntigravityWebSearcher` com `search(query, limit)` → `bridge.delegate(prompt, agent="search")` ou `fallback_bridge` quando CLI ausente. `search()` com `providers=["web"]` ou `query` contendo `http` usa web_searcher. Teste com injeção mantém determinismo.

### G3 — tomli fallback
`reversa_universal/engine.py:dependencies` tenta `import tomllib` → fallback `import tomli as tomllib` (se instalado) → fallback regex. Teste verifica que `tomli` é tentado quando `tomllib` falha.

### G4 — HarnessWorkerPool dedicado
Novo `integrations/harness/harness_worker_pool.py` com classe `HarnessWorkerPool` nativa (`harness-worker-N`, capabilities `harness_execution/universal_model_routing/autonomous_production`, `ThreadPoolExecutor` + `trust.learn`/`TokenEconomy`). `UniversalHarnessBridge` passa a usar `HarnessWorkerPool` em vez de `DeepSeekWorkerPool` com override.

### G5 — Documentação average_score
`evolution/cycles.py:EvolutionRegistry.average_score` docstring e `README.md` (seção Ciclos Evolutivos) explicitam: *"média móvel dos scores dos ciclos com score, não gate de qualidade; gate é `SpecVerifier` + `GradingHead` + `calibration`, não a média"*.

## Critérios de Aceitação
1. AC1 — SPEC-935-R438 `green`
2. AC2 — `specs/loops/dsh-reasoning-97.md` e `specs/loops/harness-reasoning-97.md` existem e contêm `dsh-reasoning-97`/`harness-reasoning-97`
3. AC3 — `doctor` com `loop_specs: pass` (quando arquivos existem)
4. AC4 — `UnifiedSearcher` com `web_searcher` padrão usa `AntigravityBridge` quando disponível; `search` com `providers=["web"]` chama web_searcher
5. AC5 — `reversa_universal/engine.py` tenta `tomli` quando `tomllib` falha (verificável via monkeypatch)
6. AC6 — `integrations/harness/harness_worker_pool.py` existe com `HarnessWorkerPool` e `UniversalHarnessBridge` o usa (não mais `DeepSeekWorkerPool`)
7. AC7 — `HarnessWorkerPool.scale(n)` registra `harness-worker-N` e `submit` funciona
8. AC8 — `evolution/cycles.py:average_score` docstring menciona "média móvel" e `README.md` menciona que média ≠ gate
9. AC9 — `doctor` com 101 specs e 256 ciclos, `pytest tests/test_r438* -q` GREEN
10. AC10 — Compatibilidade: `tests/test_r43*` (R433-R437) permanecem GREEN

## Não Objetivos
- Não altera lógica de scoring dos harnesses; apenas fecha gaps de infraestrutura/documentação
- Não exige `tomli` instalado em produção — fallback regex permanece quando ambos ausentes
- Não exige Antigravity CLI instalado — handoff em `.antigravity/queue/` quando indisponível
