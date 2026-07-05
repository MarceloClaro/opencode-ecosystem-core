# SPEC-032: MINIMUM CAPABILITY SET SOLVER — Formalização Matemática do Conjunto Mínimo de Capacidades

**Versão:** 1.0.0  
**Data:** 2026-06-08  
**Dependências:** SPEC-028 (NoologicalScanner), SPEC-029 (TeleologicalReverseScanner), SPEC-030 (CrossValidationEngine)

---

## 1. Problema Formal

### Definição

Seja um ecossistema de conhecimento modelado como grafo direcionado ponderado:

```
G = (V, E)

onde:
  V = {v₁, v₂, ..., v₉₂}  — 92 capacidades (10 dimensões × categorias)
  E = {(a, b, w) | w ∈ (0,1]}  — arestas de dependência
    - (a, b, w) significa: "a requer b com peso w"
    - (a, b, w) com relação "enables": "a habilita b com peso w"

Estado atual:
  S = {v ∈ V | v está coberto no scan noológico}  — capacidades presentes

Estado futuro desejado:
  T = {v ∈ V | v é requerido pelos objetivos teleológicos}  — capacidades alvo
```

### Problema de Otimização (MCSP — Minimum Capability Set Problem)

> **Encontrar C ⊆ V \ S tal que:**
>
> 1. **Cobertura:** S ∪ C ⊇ T (todas as capacidades alvo estão presentes)
> 2. **Fecho de dependências:** ∀c ∈ C, ∀p ∈ prereq(c): p ∈ S ∪ C
>    (todos os pré-requisitos de cada capacidade escolhida também estão presentes)
> 3. **Minimalidade:** |C| é mínimo dentre todos os conjuntos que satisfazem (1) e (2)
>
> Se múltiplos conjuntos mínimos existirem, selecionar o de **menor custo ponderado:**
>   cost(C) = Σ_{c∈C} (1 - weight(c)) onde weight(c) = facilidade de aquisição

### Complexidade

MCSP é **NP-difícil** (redução de Minimum Set Cover com restrições de precedência).  
Para o grafo de 92 nós, usamos heurística gulosa com garantia de aproximação logarítmica.

---

## 2. Algoritmo

### Fase 1: Propagação Reversa de Dependências (Backward Closure)

```
Entrada: G, S, T
Saída:   R = fecho reverso de dependências de T

Algoritmo:
  R ← T
  fila ← T
  enquanto fila não vazia:
    v ← fila.pop()
    para cada (u, v, w) ∈ E:  // u requer v, ou v habilita u... 
      se u ∉ R e u ∉ S:
        R ← R ∪ {u}
        fila.append(u)
  retorna R
```

R contém todas as capacidades que precisam ser adquiridas para que T seja viável, **incluindo dependências transitivas**.

### Fase 2: Seleção Gulosa por Impacto em Cascata (Greedy Selection)

```
Entrada: G, S, T, R
Saída:   C = conjunto mínimo aproximado

Algoritmo:
  C ← ∅
  pendentes ← T \ S  // capacidades alvo ainda não cobertas
  
  enquanto pendentes ≠ ∅:
    // Para cada capacidade em R \ (S ∪ C), calcular score:
    para cada c ∈ R \ (S ∪ C):
      score(c) = cascade_impact(c) × coverage_gain(c, pendentes) / cost(c)
      onde:
        cascade_impact(c) = Σ_{v depende de c} weight(c,v)
        coverage_gain(c)  = |{t ∈ pendentes alcançável a partir de c}|
        cost(c)           = 1 + |prereq(c) \ (S ∪ C)|  // custo de adquirir c
    
    c* ← argmax score(c)
    C ← C ∪ {c*}
    pendentes ← pendentes \ alcançável(c*)
  
  retorna C
```

### Fase 3: Ordenação Topológica (Execution Order)

```
Entrada: G, S, C
Saída:   ordem de aquisição viável

Algoritmo:
  Ordenar C por ordem topológica: se a requer b, b vem antes de a.
  Usar Kahn's algorithm (BFS com in-degree).
```

---

## 3. Estruturas de Dados

```python
@dataclass
class CapabilitySet:
    required: set[str]           # capacidades a adquirir
    cost: float                  # custo total (soma de 1-weight)
    topological_order: list[str] # ordem de aquisição
    coverage_pct: float          # % de T coberto por S ∪ C
    transitive_deps: int         # dependências transitivas incluídas

@dataclass
class MCSPSolution:
    minimum_set: CapabilitySet
    greedy_set: CapabilitySet    # solução gulosa (mais rápida, aproximada)
    is_optimal: bool             # True se mínimo global encontrado
    search_space: int            # tamanho do espaço de busca
    elapsed_ms: float            # tempo de execução
```

---

## 4. Testes (TDD)

> Suite: `specs/test_minimum_capability_solver.py`

### Fase 1 — Fecho de Dependências (4 CTs)

| CT | Descrição |
|----|-----------|
| MCSP-001 | `backward_closure`: grafo trivial A→B, T={B} → R={A,B} |
| MCSP-002 | `backward_closure`: S já cobre dependência → R não inclui o que já existe |
| MCSP-003 | `backward_closure`: dependência transitiva A→B→C, T={C} → R={A,B,C} |
| MCSP-004 | `backward_closure`: grafo com 92 nós, T com 3 alvos → R ≥ 3 |

### Fase 2 — Seleção Gulosa (4 CTs)

| CT | Descrição |
|----|-----------|
| MCSP-005 | `greedy_select`: 1 alvo sem dependências → C com 1 elemento |
| MCSP-006 | `greedy_select`: 2 alvos, 1 cobre ambos → C com 1 elemento |
| MCSP-007 | `greedy_select`: prioriza alta cascade_impact sobre baixa |
| MCSP-008 | `greedy_select`: C nunca inclui capacidades já em S |

### Fase 3 — Ordenação Topológica (3 CTs)

| CT | Descrição |
|----|-----------|
| MCSP-009 | `topological_order`: A→B → ordem = [B, A] (pré-requisito primeiro) |
| MCSP-010 | `topological_order`: sem dependências → qualquer ordem é válida |
| MCSP-011 | `topological_order`: ciclo detectado → raise TopologicalCycleError |

### Integração (3 CTs)

| CT | Descrição |
|----|-----------|
| MCSP-012 | Pipeline completo: scan noológico → requisitos teleológicos → MCSP solution |
| MCSP-013 | `cost(solution)` ≤ |C| (custo nunca excede cardinalidade) |
| MCSP-014 | Solução completa: conjunto, custo, ordem, cobertura %, tempo |

---

## 5. Exemplo de Uso

```python
from minimum_capability_solver import MinimumCapabilitySolver
from cross_validation_engine import CrossValidationEngine

# Estado atual (do scan noológico)
engine = CrossValidationEngine()
engine.build_graph(noological_scan)

# Alvos (dos requisitos teleológicos)
targets = {"raciocinio.Probabilístico", "teoria_jogos.Equilíbrio de Nash"}

# Resolver
solver = MinimumCapabilitySolver(engine)
solution = solver.solve(
    present=covered_capabilities,   # S
    targets=targets,                 # T
)

print(f"Conjunto mínimo: {solution.greedy_set.required}")
print(f"Custo: {solution.greedy_set.cost:.2f}")
print(f"Ordem: {solution.greedy_set.topological_order}")
print(f"Cobertura: {solution.greedy_set.coverage_pct:.0%}")
```

---

## 6. Métricas

| Métrica | Meta |
|---------|------|
| CTs TDD | 14/14 PASS |
| Algoritmo backward_closure | O(|V| + |E|) |
| Algoritmo greedy_select | O(|V|²·|E|) |
| Acurácia da heurística | ≥ 80% do ótimo (para grafos ≤ 100 nós) |
| Integração com scanners | Pipeline Noológico → Teleológico → MCSP funcional |
