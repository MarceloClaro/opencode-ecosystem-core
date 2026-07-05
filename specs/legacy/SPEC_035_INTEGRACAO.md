# SPEC-035: Integração Composição Unitária ao Pipeline Evolutivo

**Status:** Implementado
**Autor:** Marcelo Claro Laranjeira (2026)
**Data:** 2026-06-10
**CTs:** 6/6 PASS
**Depende de:** SPEC-033 (CapabilityComposer)

---

## 1. Objetivo

Integrar a camada de Composição Unitária do Conhecimento (SPEC-033) ao pipeline evolutivo existente, fazendo com que cada fase do pipeline consuma e enriqueça os dados de composição.

## 2. Escopo da Integração

### 2.1 Arquivos Modificados

| Arquivo | Mudança | Linhas |
|---------|---------|--------|
| `cross_validation_engine.py` | `CapabilityNode.composition` opcional | +1 |
| `evolutionary_pipeline.py` | `EvolutionaryScenario.required_inputs`, `EvolutionaryRoadmap.capability_units`, `total_construction_cost`, pipeline `__init__` + `scan()` | +27 |
| `minimum_capability_solver.py` | `CapabilitySet.shared_inputs`, `solve_with_composer()`, `_greedy_select_with_cost()`, `solve_from_scanners(composer=)` | +106 |

### 2.2 Arquivos Criados

| Arquivo | Descrição |
|---------|-----------|
| `specs/test_capability_integration.py` | Suite TDD com 6 CTs |
| `specs/SPEC_035_INTEGRACAO.md` | Este documento |

## 3. Fluxo do Pipeline (Pós-Integração)

```
M1: NoologicalScanner        → "O que existe?" (scan do estado atual)
M2: TeleologicalScanner      → "O que deveria existir?" (gaps teleológicos)
M3: CrossValidationEngine     → "O que depende do quê?" (grafo de capacidades)
M3.5: CapabilityComposer     → "Do que cada gap é feito?" (decomposição em insumos) ← NOVO
M4: PolymathicConvergence     → "Quem já resolveu isso?" (analogias polimáticas)
M5: TrajectoryMapper          → "Qual o melhor caminho?" (roadmap evolutivo)
```

A nova fase M3.5 executa após o CrossValidationEngine e antes da Convergência Polimática:

1. Extrai `capability_ids` dos gaps teleológicos (formato `dim_key.category`)
2. `composer.decompose_many()` decompõe cada capacidade em `CapabilityUnit`
3. `composer.compute_total_construction_cost()` calcula custo com desconto por inputs compartilhados
4. `CapabilityNode.composition` é populado no grafo de dependências
5. `EvolutionaryScenario.required_inputs` é populado com os `input_ids` da composição

## 4. Integração com MCSP

### 4.1 Novo Método: `solve_with_composer()`

```python
solver.solve_with_composer(present, targets, composer) -> MCSPSolution
```

**Diferenças do `solve()` original:**

| Aspecto | `solve()` | `solve_with_composer()` |
|---------|----------|------------------------|
| Custo | `1.0 + len(unmet_prereqs) * 0.5` | `construction_cost - shared_discount` |
| Inputs compartilhados | Ignorados | Desconto proporcional |
| Heurística gulosa | `cascade * coverage / cost` | `cascade * coverage / effective_cost` |

### 4.2 Método Auxiliar: `_greedy_select_with_cost()`

Seleção gulosa que prioriza capacidades com alta razão `cascade_impact / construction_cost`, aplicando desconto quando inputs já foram construídos por capacidades previamente selecionadas.

### 4.3 `solve_from_scanners()` Aceita `composer` Opcional

```python
# Sem composer (retrocompatível)
sol = solver.solve_from_scanners(nool_scan, tel_gaps)

# Com composer (construction_cost real)
sol = solver.solve_from_scanners(nool_scan, tel_gaps, composer=composer)
```

## 5. CTs (6/6 PASS)

| CT | Nome | Descrição |
|----|------|-----------|
| INT-001 | CapabilityNode.composition populado | Node carrega CapabilityUnit após decomposição |
| INT-002 | EvolutionaryScenario.required_inputs | Cenário inclui input_ids da composição |
| INT-003 | MCSP com construction_cost | `solve_with_composer()` usa custo real |
| INT-004 | Desconto por inputs compartilhados | `shared_cost < individual_sum` |
| INT-005 | Roadmap inclui capability_units | `EvolutionaryRoadmap` tem `capability_units` + `total_construction_cost` |
| INT-006 | Pipeline completo sem erro | Noo -> Telo -> Compose -> CrossVal -> MCSP |

## 6. Retrocompatibilidade

Todas as mudanças são não-invasivas:

- `CapabilityNode.composition` é `None` por default
- `EvolutionaryScenario.required_inputs` é `[]` por default
- `EvolutionaryRoadmap.capability_units` é `[]` por default
- `solve()` original permanece inalterado
- `solve_from_scanners()` funciona sem `composer` (usa `solve()` internamente)

## 7. Referências

- SPEC-028: NoologicalScanner — `noological_scanner.py`
- SPEC-029: TeleologicalReverseScanner — `teleological_scanner.py`
- SPEC-030: EvolutionaryScannerPipeline — `evolutionary_pipeline.py`
- SPEC-032: MinimumCapabilitySolver — `minimum_capability_solver.py`
- SPEC-033: CapabilityComposer — `capability_composer.py`
- architectu-008: Estrutura da Composição Unitária
- architectu-009: Integração Stage 3 ao Pipeline
