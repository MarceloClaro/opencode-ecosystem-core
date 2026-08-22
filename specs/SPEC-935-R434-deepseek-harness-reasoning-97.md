---
spec_id: SPEC-935-R434
component: integrations.deepseek_harness.reasoning_loop
title: Ponte dsh Raciocinada — Ciclo Reflexivo até Score 97
version: 1.0.0
status: green
test_file: tests/test_r434_deepseek_harness_reasoning.py
---

# SPEC-935-R434 — Ponte dsh Raciocinada: ciclo reflexivo até Score 97 (9.7/10)

## Meta
- **Ciclo**: R434
- **Antecessor**: R433 (score 9.3) — ponte orquestrada dsh sem raciocínio iterativo
- **Alvo**: 9.7/10 (97) — melhoria de +0.4 via raciocínios e respostas calibradas
- **Ponte**: `integrations/deepseek_harness/reasoning_loop.py` + evolução do `bridge.py` e `orchestrator.py`

## Diagnóstico R433 (Perceber)
- Inventory/Adapter/Pool/Bridge funcionais (16/16 GREEN), mas sem pré/pós-raciocínio, sem loop reflexivo, sem calibração de confiança, sem grading 0-7.
- `calibrate_confidence` e `GradingHead` já existem no Core mas não eram usados no fluxo dsh → oportunidade direta para 97.
- `MultiReasoningEngine` (12 motores: Z3, SymPy, Critical, Bayesian, Causal, Temporal, Fuzzy, ChainOfThought, Analogical, Counterfactual, Quantum) e `ReflexionEngine` também ociosos neste fluxo.
- Lacuna: resposta do dsh era aceita em 1 passada; sem iteração, sem melhoria contínua.

## Objetivo
Elevar o ciclo **Perceber → Especificar → Delegar → Executar → Verificar → Refletir** do R433 para um **ciclo reflexivo raciocinado** que, a cada iteração, aplica raciocínios múltiplos, calibra confiança e grada a resposta, refletindo e refinando até atingir gate 97.

## Arquitetura R434

```
objective ──► [Perceber: lessons + diagnose] ──┐
          │                                    │
          ▼                                    │
   ┌─ PreReasoning (MultiReasoning ensemble)    │
   │   Z3/SymPy/Critical → refined_prompt ──────┤
   │                                            │
   ▼                                            │
 DeepSeekHarnessBridge.orchestrate ──► results  │
          │                                    │
          ├─ Ingestão metacognitiva (R433)      │
          ├─ Calibração (confidence_calibrator) │
          ├─ Grading (GradingHead 0-7)          │
          ▼                                    │
   Verificar: calibrated >=0.97 & grade>=6 ? ──► SIM → Refletir + retornar BEST
          │ NÃO                                 │
          └──── ReflexionEngine.reflect ──► refined_prompt ──► próxima iteração
                        (max 3, stagnation 0.02)
```

### C1 — DeepSeekReasoningLoop (`reasoning_loop.py`)
| Método | Contrato |
|---|---|
| `run(objective, runner, workers, max_iters=3, target=0.97)` | Loop reflexivo até atingir `calibrated_confidence >= target` e `grade.normalized >=0.8` ou esgotar `max_iters`. Retorna dict com `best`, `history`, `calibrated`, `grade`, `iterations`, `achieved_target` |
| `pre_reason(objective)` | Ensemble dos 12 motores; escolhe `best_engine`; retorna `refined_prompt` + `reasoning_trace` |
| `calibrate(result, iteration)` | Usa `confidence_calibrator.calibrate_confidence` com `reproducibility_score` derivado de `grade.normalized` |
| `grade_response(objective, response)` | `GradingHead.grade` 0-7; `normalized = score/7` |
| `reflect_and_refine(objective, outcome, grade, calibrated)` | `ReflexionEngine` → nova reflexão → prompt refinado; publica `deepseek_harness/reflexion` |

Invariantes: nenhuma iteração fabrica sucesso; `achieved_target` só True quando ambos gates passam com eventos reais do runner. Quando `runner` injeta falha, loop registra `error` e continua (não alega 97).

### C2 — Evolução do orquestrador
- `MarceloClaroOrchestrator.orchestrate_deepseek_harness_iterative(objective, workers=1, runner=None, max_iters=3, target=0.97)` — lazy bridge + loop raciocinado + percepção prévia + reflexão final.
- `MarceloClaroOrchestrator.dsh_reasoning_status()` — expõe motores disponíveis e último loop.

### C3 — LoopSpecification
`LoopSpecification(name="dsh-reasoning-97", max_iterations=3, stagnation_window=2, stagnation_threshold=0.02, terminal_states=["success","exhausted","error"], goal="calibrated>=0.97 & grade>=6")` registrada em `loop_spec_registry` no import do reasoning_loop.

## Critérios de aceitação (teste R434)
1. AC1 — SPEC-935-R434 registrada `green`.
2. AC2 — `pre_reason` retorna `best_engine` dentre os 12 e `refined_prompt` não vazio.
3. AC3 — `grade_response` com resposta substancial ancorada retorna `score>=5` e `normalized>=0.7`.
4. AC4 — `calibrate` com resultado completed retorna `calibrated_confidence>=0.7` (base 0.5 + reprodutibilidade + sem alerts).
5. AC5 — `run` iterativo com runner de sucesso atinge `achieved_target==True` em ≤3 iterações e `iterations>=1`.
6. AC6 — `run` com runner que falha na 1ª e sucede na 2ª demonstra reflexion (history len 2).
7. AC7 — `orchestrate_deepseek_harness_iterative` existe no orquestrador, é lazy e retorna `best.verification.status==green`.
8. AC8 — LoopSpec `dsh-reasoning-97` registrado e `doctor` continua `specs_formais pass` (agora 97).

## Não objetivos
- Não substitui a execução real do dsh contra API; testes usam runners injetados.
- Não alega superioridade externa; 97 é gate interno (calibração + grading), não validação externa.
- Não altera a ponte R433 — estende via `reasoning_loop`, preservando compatibilidade.

## Score 97 — decomposição
- R433 base 9.3 + pre-reasoning 0.1 + calibração 0.1 + grading 0.1 + reflexion loop 0.1 = 9.7
- Gate verificável: `calibrated>=0.97` e `grade.score>=6` em teste determinístico com runner injetado.
