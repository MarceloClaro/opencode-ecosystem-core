---
spec_id: SPEC-935-R433
component: integrations.deepseek_harness
title: Ponte Orquestrada DeepSeek Harness (dsh)
version: 1.0.0
status: green
test_file: tests/test_r433_deepseek_harness_bridge.py
---

# SPEC-935-R433 — Ponte Orquestrada DeepSeek Harness: produções autônomas e metacognições escaladas

## Meta
- **Ciclo**: R433 (evolution/cycles.json)
- **Autor**: marceloclaro (orquestrador central)
- **Status**: green
- **Teste**: `tests/test_r433_deepseek_harness_bridge.py`
- **Componente**: `integrations/deepseek_harness/`

## Objetivo
Integrar de forma nativa ao OpenCode Ecosystem Core o sistema **DeepSeek Harness (`dsh`)** presente em
`deepseek-harness.zip` (extraído em `deepseek-harness/`, com análise Reversa concluída em `_reversa_sdd/`),
de modo que o orquestrador `marceloclaro` **orquestre** as produções autônomas do dsh (execução de tarefas
via SDK/runtime JSON-RPC) e **escale** sua metacognição (eventos de sessão e Agent Notes → MetaBus),
com Trust Engine, Token Economy, SDD gate e registro evolutivo aplicados a cada execução.

## Escopo factual (base confirmada)
- `DEEPSEEK-HARNESS/`: monorepo `@deepseek-ai/dsh-root` v0.1.0-rc.7, 231 pacotes, 49 grupos, MIT.
- `python/sdk`: pacote `deepseek-harness-sdk` (`DeepSeekHarness`, JSON-RPC sobre stdio para runtime local).
- `.reversa/state.json`: análise Reversa na fase `concluido`; 13 módulos; 231 pacotes de workspace.
- `_reversa_sdd/inventory.md`: inventário CONFIRMADO/INFERIDO/LACUNA gerado pelo Scout.

## Arquitetura

```
marceloclaro (Core)
│
├── integrations/deepseek_harness/
│   ├── inventory.py      DeepSeekHarnessInventory — indexa o monorepo + artefatos Reversa
│   ├── adapter.py        DeepSeekHarnessAdapter — canal de execução (SDK | subprocesso | indisponível)
│   ├── metacognition.py  DSHMetacognitionIngestor — sessões/Agent Notes → MetaBus (lições + reflexões)
│   ├── worker_pool.py    DeepSeekWorkerPool — escala N workers "dsh-worker-N" no Blackboard
│   └── bridge.py         DeepSeekHarnessBridge (facade) + deepseek_harness_bridge (singleton)
│
└── marceloclaro/orchestrator.py
    └── orchestrate_deepseek_harness(objective) — percepção → spec SDD → pool → gate → reflexão
```

### C1 — Inventory (`inventory.py`)
| Método | Contrato |
|---|---|
| `discover()` | Lê `.reversa/state.json`, `_reversa_sdd/inventory.md` e a árvore real de `packages/`; retorna dict auditável |
| `capability_groups()` | Grupos de pacotes reais (`packages/*`) mapeados a capacidades semânticas do Core |
| `is_available()` | True somente se o diretório do monorepo existe no checkout |

Invariantes: nenhum dado fabricado — toda métrica vem de arquivo ou contagem real; ausência de artefato
resulta em campo ausente (nunca valor padrão fictício).

### C2 — Adapter (`adapter.py`)
| Método | Contrato |
|---|---|
| `resolve_channel()` | `'sdk'` se `import deepseek_harness` funcionar; `'runtime-bin'` se binário existir; senão `'unavailable'` |
| `run_task(prompt, cwd=None, runner=None)` | Executa via canal resolvido; `runner` injetável para TDD; nunca simula sucesso |
| `status()` | Canal, disponibilidade do monorepo, contadores de execução |

Anti-overclaim: quando o canal é `'unavailable'`, o resultado é `status="unavailable"` com handoff
enfileirado em `.deepseek-harness/queue/` (padrão SPEC-046); não há produção simulada.

### C3 — Metacognition (`metacognition.py`)
| Método | Contrato |
|---|---|
| `ingest_session_events(events, task_id)` | Converte eventos `session.event` do dsh em `publish_subsystem_event("deepseek_harness", ...)` e reflexões com score calibrado |
| `ingest_agent_notes(limit)` | Varre `DEEPSEEK-HARNESS/.agents/notes/**/*.md` (metacognição nativa do dsh) e registra tópicos semânticos com proveniência |

### C4 — Worker Pool (`worker_pool.py`)
| Método | Contrato |
|---|---|
| `scale(n)` | Registra/atualiza `n` agent cards `dsh-worker-i` no Blackboard via `metabus.register_agent` |
| `submit(objective, runner=None)` | Executa paralelamente (ThreadPoolExecutor limitado), alimenta trust.learn/economy por outcome |
| `report()` | Workers ativos, execuções, sucessos, falhas |

### C5 — Facade Bridge + integração no orquestrador
`DeepSeekHarnessBridge.status()/delegate()/orchestrate(objective)`; singleton `deepseek_harness_bridge`.
Em `MarceloClaroOrchestrator`: propriedade lazy `dsh_bridge` + método
`orchestrate_deepseek_harness(objective)` que aplica o ciclo completo (perceber → especificar → delegar →
executar → verificar → refletir). Import lazy: a inicialização do orquestrador não pode falhar se o zip
estiver ausente.

## Critérios de aceitação (verificados em teste)
1. AC1 — A spec formal `SPEC-935-R433` está registrada no SpecRegistry com status `green`.
2. AC2 — O inventory descobre ≥ 40 grupos de pacotes reais e reporta os metadados do `.reversa/state.json`.
3. AC3 — O adapter resolve canal `unavailable` sem SDK instalado e enfileira handoff auditável (sem fingir execução).
4. AC4 — Com runner injetado, `run_task` produz resultado `completed` com saída íntegra e contador incrementado.
5. AC5 — `ingest_session_events` converte eventos do dsh em reflexões no MetaBus e eventos de subsistema.
6. AC6 — `scale(2)` registra exatamente 2 workers com capacidade `dsh_execution`; `scale(1)` reduz para 1.
7. AC7 — `pool.submit` com runner injetado executa em paralelo e aprende outcomes no Trust Engine.
8. AC8 — O bridge expõe `status()` auditável e `orchestrate()` aplica gate SDD (spec dinâmica criada).
9. AC9 — `orchestrate_deepseek_harness` existe no orquestrador, é lazy e não quebra `__init__` sem zip.
10. AC10 — Ciclo R433 registrado no EvolutionRegistry com lições.

## Não objetivos
- Não instalar nem compilar o monorepo TypeScript do dsh neste ciclo (Node/pnpm fora do escopo).
- Não alegar execução real contra API da DeepSeek (requer `DEEPSEEK_API_KEY`; testes usam runners injetados).
- Não substituir o Blackboard/MetaBus do Core pelos plugins Cordis do dsh — a ponte é adaptativa, não fusional.
