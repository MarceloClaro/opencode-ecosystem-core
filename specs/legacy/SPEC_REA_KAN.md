# SPEC-REA-KAN: Logic Programming (miniKanren)
Version: 1.0.0 | Status: verified | TDD: required | Engine: KanrenEngine

## Objective
Programacao logica relacional com fatos, consultas com backtracking e cadeias de explicacao dedutiva usando miniKanren.

## Acceptance Criteria
- [x] CT-1: `assert_fact` armazena fatos corretamente na base de conhecimento
- [x] CT-2: `query` ancestor retorna solucoes transitivas (fecho transitivo da relacao)
- [x] CT-3: `explain` retorna cadeia de deducao passo a passo
- [x] CT-4: `clear` remove todos os fatos da base de conhecimento

## API Contract

### assert_fact(relation: str, *args: str) -> None
```python
engine.assert_fact("parent", "joao", "maria")
# armazena: parent(joao, maria)
```

### query(relation: str, *args: str) -> list[dict]
```python
engine.query("ancestor", "joao", var)
# retorna: [{"var": "maria"}, {"var": "pedro"}, ...]
```

### explain(relation: str, *args: str) -> list[dict]
```python
engine.explain("ancestor", "joao", "ana")
# retorna: [
#   {"step": 1, "fact": "parent(joao, maria)", "source": "asserted"},
#   {"step": 2, "fact": "parent(maria, ana)", "source": "asserted"},
#   {"step": 3, "rule": "ancestor(X,Z) :- parent(X,Y), ancestor(Y,Z)", "deduced": True}
# ]
```

### clear() -> None
```python
engine.clear()
# remove todos os fatos; len(engine.facts) == 0
```

## Engine
- Classe: `KanrenEngine`
- Localizacao: `skills/reasoning/logic-programming/scripts/kanren_engine.py`
- Dependencia: `miniKanren` (kanren 1.0+)

## Regras Embutidas
- `ancestor(X, Z) :- parent(X, Z)`
- `ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z)`
- `sibling(X, Y) :- parent(P, X), parent(P, Y), X != Y`

## Dependencias da Skill
- `reasoning-orchestrator` (compativel com raciocinios: deduction, syllogism, relational_inference)

## Test Results
- CT-1 to CT-4: PASSED
