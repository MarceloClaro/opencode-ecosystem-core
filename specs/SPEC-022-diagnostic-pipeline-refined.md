# SPEC-022 — Pipeline de Diagnóstico Refinado para Ecossistema

```yaml
spec_id: SPEC-022
title: Pipeline de Diagnóstico Refinado — Cobertura do Ecossistema + Metas Core
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-009, SPEC-020, SPEC-005]
origin: Diagnóstico inicial (coverage 0%) — refinamento orquestrado por marceloclaro
```

## 1. Contexto

O pipeline de diagnóstico atual (`SPEC-009`, `scanners/pipeline.py`) foi projetado para **corpora acadêmicos** — manuscritos, papers, teses — com 10 dimensões epistemológicas (paradigmas, métodos, teorias, etc.). Quando aplicado ao **próprio ecossistema OpenCode Core** (`diagnostic_pipeline.run("ecosystem")`), o resultado é **cobertura 0%** (grau F) porque as categorias não correspondem aos componentes reais do sistema.

**Problema identificado:**
```
noological.coverage = 0   # 0/92 categorias acadêmicas
teleological.skipped       # sem metas definidas
evolutionary.total_gaps = 0  # falso positivo — não há gaps porque nada foi medido
```

**Necessidade:** Um perfil de escaneamento **noológico específico para ecossistemas de software**, com categorias que reflitam a arquitetura real do OpenCode Core, e metas formais cadastradas para permitir o escaneamento teleológico.

## 2. Requisitos

### 2.1 Perfil de Domínio "ecosystem"

| ID | Requisito | Critério de Aceitação |
|---|---|---|
| REQ-022.1 | `NoologicalScanner` DEVE aceitar `domain="ecosystem"` e carregar dimensões específicas do ecossistema | `run("ecosystem", domain="ecosystem")` cobre ≥ 10 categorias |
| REQ-022.2 | As dimensões "ecosystem" DEVEM refletir a arquitetura real do Core: agentes, MCI, scanners, trust, economia, razão, evolutivo, integrações, protocolos, governance | cada dimensão com ≥ 5 categorias baseadas em componentes reais |
| REQ-022.3 | O escaneamento DEVE detectar automaticamente a presença/ausência de componentes pelos seus nomes de módulo, classes e arquivos | detecção por palavra-chave dos módulos existentes em `scanners/`, `agents/`, `trust/`, etc. |
| REQ-022.4 | O relatório DEVE incluir `components_found`, `components_absent` e `coverage_by_layer` (camadas do ecossistema) | chave `ecosystem_layers` presente no resultado |

### 2.2 Metas do Ecossistema (Teleológico)

| ID | Requisito | Critério de Aceitação |
|---|---|---|
| REQ-022.5 | O orquestrador DEVE registrar metas canônicas do OpenCode Core: SDD/TDD compliance, trust score ≥ 0.7, stake mínimo, cobertura de specs, ciclos evolutivos | `diagnose()` chama pipeline com goals predefinidos |
| REQ-022.6 | O scanner teleológico DEVE comparar presença de specs implementadas vs. metas de cobertura (100% das specs ativas) | teleological.score computado |
| REQ-022.7 | O pipeline DEVE aceitar `goals` como parâmetro e, se omitido com `domain="ecosystem"`, usar metas-padrão do Core | fallback para `_ecosystem_default_goals()` |

### 2.3 Refinamento Evolutivo

| ID | Requisito | Critério de Aceitação |
|---|---|---|
| REQ-022.8 | A síntese evolutiva DEVE considerar lacunas noológicas E teleológicas — `total_gaps = len(absent_categories) + len(teleological_gaps)` | evolutionary.total_gaps ≥ 1 quando há categorias ausentes |
| REQ-022.9 | A recomendação DEVE priorizar camadas mais críticas (ex: segurança > integrações > documentação) com base no peso da dimensão | recommendation menciona a camada mais prioritária |

### 2.4 Metacognição (Reflexion)

| ID | Requisito | Critério de Aceitação |
|---|---|---|
| REQ-022.10 | Cada diagnose com `domain="ecosystem"` DEVE registrar reflexão no MetaBus com lições aprendidas sobre cobertura | `orchestrator.diagnose()` → reflexion registrada |
| REQ-022.11 | O score da reflexão DEVE ser `max(0.1, 1.0 - total_gaps/50)` | score ≥ 0.1 mesmo com coverage 0 |

## 3. Dimensões do Ecossistema

### 3.1 Definição das 10 Dimensões "ecosystem"

| Dimensão | Categorias (exemplos) | Descrição |
|---|---|---|
| `agentes` | orchestrator, coder, researcher, auditor, academic_writer, docs_writer, ws-*, reversa-*, bernstein, antigravity-orchestrator | Catálogo de agentes disponíveis |
| `mci_core` | metabus, blackboard, reflexion, transformer, context_manager, memory_updater, graph_builder | Middleware de Consciência Integral |
| `scanners` | noological, teleological, potentiality, evolutionary, social_impact, reversa, epistemic_prioritizer, successor_generator | Pipeline de diagnóstico |
| `trust_economy` | trust_engine, token_economy, staking, slashing, fee_market, behavioral_gate | Governança econômica |
| `razao_logica` | z3_solver, sympy, kanren, critical_reasoner, quantum_reasoning | Motores de raciocínio formal |
| `evolucao` | evolution_registry, cycles, auto_evolve, reflection_ledger, trajectory_mapper | Ciclos evolutivos e memória |
| `protocolos` | sdd_spec_first, tdd_red_green_refactor, a2a_blackboard, mcp_interconnect, bernstein_orchestration | Protocolos formais do ecossistema |
| `integracoes` | antigravity_bridge, cli_integrations, pypi_searcher, web_search, mcp_servers | Pontes com sistemas externos |
| `infra_dados` | schemas, data_pipeline, benchmarks, notebooks, batch_executor | Dados, esquemas e automação |
| `governanca` | cooperative_governance, dialectical_engine, game_theory, trust_scores, slashing_rules | Mecanismos de governança distribuída |

### 3.2 Keywords de Detecção por Dimensão

Cada categoria mapeia para palavras-chave que o scanner buscará no corpus (nomes de módulos, classes, arquivos):

```python
ECOSYSTEM_KEYWORDS = {
    "agentes": {
        "orchestrator": ["orchestrator", "marceloclaro", "orquestrador"],
        "coder": ["coder", "coding_agent", "coder-agent"],
        "researcher": ["researcher", "research_agent", "web-search-researcher"],
        "auditor": ["auditor", "security-auditor", "code-reviewer"],
        "academic_writer": ["academic_writer", "maswos", "academic-pipeline"],
        "bernstein": ["bernstein", "bernstein-orchestrator", "maestro"],
        "antigravity": ["antigravity", "antigravity-bridge", "antigravity_orchestrator"],
        "reversa": ["reversa", "reversa-agent", "reversa-*"],
        "ws_agents": ["ws-coder", "ws-researcher", "ws-reviewer", "ws-scribe", "ws-academic"],
        "agents_catalog": ["agents/catalog", "catalogo", "catalog/*.md", "agent_catalog"],
    },
    # ... (dimensões análogas, ver implementação)
}
```

## 4. Metas Padrão do Core

```python
ECOSYSTEM_DEFAULT_GOALS = [
    {"name": "spec_coverage_100pct", "description": "100% das specs ativas implementadas e verificadas",
     "goal_type": "evaluative", "weight": 1.0},
    {"name": "trust_min_07", "description": "Trust Score médio dos agentes ≥ 0.7",
     "goal_type": "evaluative", "weight": 1.0},
    {"name": "tdd_sdd_compliance", "description": "Toda entrega passa pelo gate SDD/TDD",
     "goal_type": "evaluative", "weight": 1.2},
    {"name": "evolution_continuous", "description": "Ciclos evolutivos registrados e refletidos no MetaBus",
     "goal_type": "evaluative", "weight": 0.8},
    {"name": "token_economy_healthy", "description": "Saldo de tokens positivo e slashing < 10% do stake total",
     "goal_type": "evaluative", "weight": 0.9},
    {"name": "ecosystem_coverage_30pct", "description": "Cobertura noológica do ecossistema ≥ 30% nas 10 dimensões",
     "goal_type": "strategic", "weight": 1.1},
]
```

## 5. Invariantes

- INV1: `domain="ecosystem"` NUNCA retorna coverage 0 se o módulo detectar ao menos um componente core.
- INV2: `total_gaps` no modo ecosystem SEMPRE conta categorias ausentes como gaps (evolutionary.total_gaps > 0 quando há ausências).
- INV3: Metas padrão só são carregadas se `goals=None` E `domain="ecosystem"`.
- INV4: Dimensões acadêmicas padrão permanecem disponíveis via `domain=""` ou `domain="psicologia"` (retrocompatibilidade total).

## 6. Arquitetura da Modificação

```
scanners/noological_scanner.py
  └── EPISTEMOLOGICAL_DIMENSIONS (existente, 10 dims acadêmicas) — intacto
  └── ECOSYSTEM_DIMENSIONS (nova, 10 dims do ecossistema) — adicionado
  └── NoologicalScanner.__init__()
        └── se domain="ecosystem" → self.dimensions = ECOSYSTEM_DIMENSIONS
        └── senão → self.dimensions = EPISTEMOLOGICAL_DIMENSIONS (default)

scanners/pipeline.py
  └── DiagnosticPipeline.run(domain="ecosystem")
        └── passa domain para NoologicalScanner.scan()
        └── se goals=None: carrega ECOSYSTEM_DEFAULT_GOALS
        └── evolutionary.total_gaps = len(absent) + len(teleological_gaps)

marceloclaro/orchestrator.py
  └── diagnose() — domain padrão = "ecosystem" para self-diagnóstico
```

## 7. Critérios de Aceitação

- [x] `diagnostic_pipeline.run("ecosystem", domain="ecosystem")` retorna `coverage == 100`
- [x] `diagnostic_pipeline.run("ecosystem", domain="ecosystem")` retorna 10 dimensões com categorias cobertas
- [x] `diagnostic_pipeline.run("ecosystem")` com goals implícitos produz `teleological.score == 1.0`
- [x] `evolutionary.total_gaps == 0` quando a cobertura do ecossistema está completa
- [x] Relatório inclui `ecosystem_layers` com presença/ausência por camada
- [x] Pipeline de diagnose existente (`domain=""`) continua funcionando com categorias acadêmicas (retrocompatibilidade)
- [x] Execução de teste legado `python3 -c "from scanners import diagnostic_pipeline; import json; print(json.dumps(diagnostic_pipeline.run('ecosystem'), ensure_ascii=False, indent=2))"` retorna 100% no singleton padrão

## 8. Testes

`tests/test_ecosystem_diagnose.py` com:

| Teste | O que verifica |
|---|---|
| `test_ecosystem_coverage_reaches_100pct` | coverage == 100 com domain="ecosystem" |
| `test_ecosystem_layers_all_present` | `ecosystem_layers` presente e com camadas válidas |
| `test_ecosystem_teleology_uses_ecosystem_dimensions` | teleologia do ecossistema retorna score e gaps coerentes |
| `test_ecosystem_evolutionary_has_no_absent_categories` | `absent_categories == 0` após integração completa |
| `tests/test_advanced_subsystems.py::TestDiagnosticPipeline` | retrocompatibilidade do pipeline padrão |
