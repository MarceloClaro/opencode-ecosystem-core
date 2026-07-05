# SPEC-083: Autonomous Self-Repair System

| Campo | Valor |
|-------|------|
| **SPEC ID** | SPEC-083 |
| **Ciclo** | R39 |
| **Status** | `active` |
| **Prioridade** | Alta |
| **Dependências** | SPEC-082 (Cross-Paradigm Reasoning) |
| **Suítes TDD** | `tests/test_r39_self_repair.py` (14 CTs) |
| **Componente** | `skills/research/cross-paradigm-reasoning/autonomous_self_repair.py` |

---

## 1. Objetivo

Implementar um sistema de auto-reparo autônomo que monitora continuamente a
saúde dos motores de raciocínio do ecossistema (Z3, SymPy, Kanren, Critical)
e das 4 research skills (Game Theory, Temporal Population, Theoretical
Empirical, Logical Multiscale), detecta falhas em tempo real, recarrega módulos
corrompidos e notifica o orquestrador central.

## 2. Arquitetura

```
┌──────────────────────────────────────────────────────┐
│              SelfRepairOrchestrator                      │
│  (pipeline completo: monitor → detect → repair → log)   │
├────────────┬───────────┬──────────┬────────────────────┤
│ Health   │  Repair   │ Repair  │  Repair            │
│ Monitor  │  Engine   │ Logger │  Notifier          │
├──────────┴───────────┴────────┴────────────────────┤
│  4 engines (Z3, SymPy, Kanren, Critical)            │
│  4 research skills (game_theory, temporal, etc.)        │
└──────────────────────────────────────────────────────┘
```

### 2.1 HealthMonitor

- `check_engine(name)` — verifica disponibilidade de motor via
  `importlib.util.spec_from_file_location` + snake case class check
- `check_research_skill(name)` — verifica presenca de todas as classes
  obrigatorias definidas em `RESEARCH_SKILLS`
- `heartbeat()` — varredura completa dos 8 modulos, retorna metricas
  agregadas (health_pct, avg_response_time_ms, unhealthy count)

### 2.2 RepairEngine

- `reload_module(name)` — limpa `sys.modules`, invalida cache de import,
  recarrega modulo do disco
- `check_dependencies(name)` — verifica deps, tenta `pip install -q`
  para dependencias faltantes
- `fallback(name)` — redireciona para engine alternativo definido em
  `ENGINES[name].fallback`

### 2.3 RepairLogger

- Audit trail com SHA-256 chain integrity
- `verify_chain()` — recalcula hashs e valida cadeia
- `export_json(path)` — serializa log completo

### 2.4 RepairNotifier

- `notify_repair(record)` — registra reparo no audit trail
- `notify_health(heartbeat)` — registra heartbeat
- `notify_state_update(path)` — persiste status em ecosystem-state.json

## 3. Engines Monitorados

| Motor | Arquivo | Deps | Fallback |
|-------|---------|------|----------|
| z3 | `skills/reasoning/formal-verification/scripts/z3_engine.py` | z3 | sympy |
| sympy | `skills/reasoning/symbolic-math/scripts/sympy_engine.py` | sympy | z3 |
| kanren | `skills/reasoning/logic-programming/scripts/kanren_engine.py` | — | critical |
| critical | `skills/reasoning/critical-reasoning/scripts/critical_engine.py` | — | kanren |

## 4. Research Skills Monitorados

| Skill | Arquivo | Classes Esperadas |
|-------|---------|-------------------|
| game_theory | `skills/research/game-theory/game_theory.py` | NashEquilibrium, PayoffMatrix |
| temporal_population | `skills/research/temporal-population/temporal_population.py` | TimeSeriesAnalyzer, LongitudinalAnalyzer, PopulationGeneralizer, SampleSizeCalculator |
| theoretical_empirical | `skills/research/theoretical-empirical/theoretical_empirical.py` | EpistemologicalClassifier, EffectSizeCalculator, ReliabilityAnalyzer, TheoreticalFrameworkBuilder |
| logical_multiscale | `skills/research/logical-multiscale/logical_multiscale.py` | InferenceEngine, MultiScaleAnalyzer, ArgumentationValidator |

## 5. Pipeline de Auto-Reparo

1. **Health Check Inicial**: `HealthMonitor.heartbeat()` — varre 8 modulos
2. **Detecção de Falhas**: itera sobre checks com `available == false`
3. **Reparo**: `reload_module()` → se falha → `check_dependencies()` → se
   falha → `fallback()`
4. **Health Check Final**: verifica se reparos restauraram saude
5. **Notificação**: atualiza ecosystem-state.json e audit trail

## 6. CTs (14 Testes)

| CT | Nome | Descrição |
|----|------|-----------|
| CT-01 | `test_health_monitor_init` | HealthMonitor inicializa sem erros |
| CT-02 | `test_health_monitor_check_engine_valid` | check_engine() retorna HealthCheck |
| CT-03 | `test_health_monitor_check_engine_unknown` | Engine desconhecido → unavailable |
| CT-04 | `test_health_monitor_check_research_skill` | check_research_skill() retorna HealthCheck |
| CT-05 | `test_health_monitor_check_all_research_skills` | 4 skills verificadas |
| CT-06 | `test_health_monitor_heartbeat` | heartbeat() → 8 checks, metricas |
| CT-07 | `test_repair_engine_init` | RepairEngine inicializa |
| CT-08 | `test_repair_engine_reload_unknown` | reload desconhecido → failed |
| CT-09 | `test_repair_engine_check_deps_no_deps` | sem deps → success |
| CT-10 | `test_repair_engine_fallback` | fallback definido |
| CT-11 | `test_repair_logger_log` | log() retorna AuditEntry com SHA-256 |
| CT-12 | `test_repair_logger_verify_chain` | verify_chain() integridade |
| CT-13 | `test_repair_notifier_notify_health` | notificar health no logger |
| CT-14 | `test_self_repair_orchestrator_pipeline` | Pipeline completo |

## 7. Critérios de Aceitação

1. Todos os 14 CTs passam (`pytest tests/test_r39_self_repair.py -v`)
2. HealthMonitor detecta engines faltantes com `available == False`
3. RepairLogger mantém SHA-256 chain integrity verificável
4. `SelfRepairOrchestrator.run_pipeline()` retorna relatório completo
5. ecosystem-state.json é atualizado com métricas de auto-reparo

---

*Fim da SPEC-083*