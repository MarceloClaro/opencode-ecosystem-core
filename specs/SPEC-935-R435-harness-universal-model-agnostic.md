---
spec_id: SPEC-935-R435
component: integrations.harness
title: Harness Universal — Agnóstico a Modelo (qualquer modelo OpenCode)
version: 1.0.0
status: green
test_file: tests/test_r435_harness_universal.py
---

# SPEC-935-R435 — Harness Universal Agnóstico a Modelo (OpenCode)

## Meta
- **Ciclo**: R435
- **Antecessores**: R433 (ponte dsh específica, 9.3) + R434 (loop raciocinado 97, 9.7)
- **Objetivo**: desacoplar o harness do DeepSeek e torná-lo **universal**: qualquer modelo do ecossistema (LiteRT-LM, Colibri, OpenAI, Zen/Go, DeepSeek via Zen) pode orquestrar produções e metacognições
- **Score alvo**: 9.8 (98) — universalidade + preservação do gate 97

## Diagnóstico R434
- R433/R434 amarram o harness ao `deepseek-harness/` (monorepo, `.reversa/state.json`, `DeepSeekHarnessAdapter`). Canal `sdk/runtime-bin/unavailable` é DeepSeek-específico.
- OpenCode já possui `ModelRouter` (coding/reasoning/academic/writing/fast/local/math + fallback) que roteia para `colibri`, `litert-lm`, `opencode-zen`, `opencode-go`, `openai`. Não é usado pelo harness.
- Oportunidade: harness universal = `ModelRouter` + `UniversalAdapter` + `UniversalBridge` + `UniversalReasoningLoop` (reuso do loop 97) + inventário de modelos.

## Arquitetura R435

```
marceloclaro/orchestrator.py
│
├── integrations/harness/                          ← NOVO (agnóstico)
│   ├── model_registry.py   HarnessModelRegistry   — descobre modelos via ModelRouter
│   ├── universal_adapter.py UniversalHarnessAdapter — run_task(prompt, task_type, provider, model, runner)
│   ├── universal_bridge.py  UniversalHarnessBridge  — orchestrate() com gate SDD TSPEC
│   └── universal_reasoning_loop.py UniversalReasoningLoop — loop 97 com qualquer modelo
│
└── integrations/deepseek_harness/                 ← preservado como provider específico
    └── (compatível: harness universal pode delegar para deepseek via provider opencode-zen/deepseek-*)
```

### C1 — HarnessModelRegistry (`model_registry.py`)
| Método | Contrato |
|---|---|
| `discover()` | Usa `ModelRouter` + providers diretos para listar `models`, `providers`, `profiles`; contagem real, nunca fabricada |
| `status()` | `{router, providers:{litert, colibri, openai, zen, go}, total_models}` |
| `route(task_type, provider, model)` | Delega a `ModelRouter.route()` e retorna `RouteResult` |

Invariante: sem modelo configurado → lista vazia, não erro; `discover()` sempre retorna dict auditável.

### C2 — UniversalHarnessAdapter (`universal_adapter.py`)
| Método | Contrato |
|---|---|
| `available_providers()` | Dict de providers do router |
| `resolve_model(task_type, provider, model)` | `RouteResult` com `provider_id` e `model_id` |
| `run_task(prompt, task_type="coding", provider=None, model=None, runner=None)` | Se `runner` injetado → usa runner (TDD); senão `ModelRouter.route_and_complete(prompt, task_type, force_provider, force_model)`; sem provider → `unavailable` com handoff em `.harness/queue/` |

Canais: runner injetado > ModelRouter (qualquer provider) > handoff. Nunca simula sucesso.

### C3 — UniversalHarnessBridge (`universal_bridge.py`)
| Método | Contrato |
|---|---|
| `status()` | `{registry, adapter, pool}` — pool reutiliza `DeepSeekWorkerPool` mas com `universal_` workers |
| `orchestrate(objective, task_type, provider, model, runner)` | Cria `TSPEC` dinâmica, executa via `adapter.run_task`, verifica `spec_verifier`, publica `harness/orchestrate.completed` |

### C4 — UniversalReasoningLoop (`universal_reasoning_loop.py`)
Subclasse/composição de `DeepSeekReasoningLoop` mas com `UniversalHarnessBridge`. Reusa `pre_reason` (ensemble 12 motores), `grade`, `calibrate`, `reflect_and_refine` e o loop até gate 97. Assinatura estendida:
`run(objective, task_type="coding", provider=None, model=None, runner, workers, max_iters, target)` — `provider/model` propagados a cada iteração para o bridge.

### C5 — Orquestrador
- `MarceloClaroOrchestrator.harness` (property lazy `UniversalHarnessBridge`)
- `harness_status()` — inventário universal
- `orchestrate_harness(objective, task_type="coding", provider=None, model=None, workers=1, runner=None)` — gate SDD
- `orchestrate_harness_iterative(objective, task_type, provider, model, workers, runner, max_iters, target)` — loop 97 universal
- Compatibilidade: `dsh_bridge`/`orchestrate_deepseek_harness*` preservados (delegam para harness com `provider="opencode-zen", model="deepseek-v3"` quando chamados)

## Critérios de aceitação (teste R435)
1. AC1 — SPEC-935-R435 registrada `green`.
2. AC2 — `HarnessModelRegistry.discover()` retorna `total_models>=5` e `providers` contém ao menos 2 chaves (ex. `litert`, `colibri`, `zen`).
3. AC3 — `UniversalHarnessAdapter.resolve_model("coding")` retorna `RouteResult` com `provider_id` e `model_id` não vazios.
4. AC4 — `run_task` com runner injetado retorna `completed` e incrementa `executions` independente do modelo solicitado.
5. AC5 — `run_task` com `provider="litert-lm", model="gemma-4-E2B-it"` e runner injetado respeita o modelo roteado no resultado.
6. AC6 — `UniversalHarnessBridge.orchestrate` cria `TSPEC` e verifica `green` com runner universal.
7. AC7 — `UniversalReasoningLoop.run` com runner longo atinge `achieved_target` (cal≥0.97 & grade≥6) para `task_type` arbitrário (`reasoning`, `coding`).
8. AC8 — `MarceloClaroOrchestrator.orchestrate_harness` e `orchestrate_harness_iterative` existem, são lazy e funcionam com qualquer `task_type`/`provider`.
9. AC9 — Compatibilidade: `orchestrate_deepseek_harness` ainda funciona (delega para harness universal com deepseek).
10. AC10 — `doctor` com 98 specs formais e `evolution` 253 ciclos.

## Não objetivos
- Não remove `integrations/deepseek_harness/` — mantém como provider legado.
- Não instala modelos nem exige credenciais; testes usam runners injetados.
- Não alega superioridade de modelo; gate 97 permanece interno (calibração + grading).

## Score 98 — decomposição
R434 9.7 + universalidade (0.05) + preservação de compatibilidade (0.03) + inventário multi-provider (0.02) = 9.8
