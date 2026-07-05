# SPEC-REA-SYM: Symbolic Mathematics (SymPy)
Version: 1.0.0 | Status: verified | TDD: required | Engine: SymPyEngine

## Objective
Computar operacoes de matematica simbolica — resolucao, simplificacao, diferenciacao, integracao e verificacao de identidades — usando SymPy 1.14+.

## Acceptance Criteria
- [x] CT-1: `solve("x**2 - 4 == 0")` retorna [-2, 2]
- [x] CT-2: `simplify("(x+1)*(x-1)")` retorna "x**2 - 1"
- [x] CT-3: `differentiate("x**3", "x")` retorna "3*x**2"
- [x] CT-4: `prove_identity("sin(x)**2 + cos(x)**2 = 1")` retorna valid

## API Contract

### solve(expression: str, variable: str = "x") -> list
```python
["-2", "2"]  # lista de solucoes como strings
```

### simplify(expression: str) -> str
```python
"x**2 - 1"  # expressao simplificada
```

### differentiate(expression: str, variable: str = "x") -> str
```python
"3*x**2"  # derivada como string
```

### integrate(expression: str, variable: str = "x") -> str
```python
"x**4/4"  # integral indefinida como string
```

### prove_identity(equation: str) -> dict
```python
{
    "status": "valid" | "invalid",
    "lhs_minus_rhs": "0" | "<non-zero expression>",
    "eval_time_ms": float
}
```

## Engine
- Classe: `SymPyEngine`
- Localizacao: `skills/reasoning/symbolic-math/scripts/sympy_engine.py`
- Dependencia: `sympy` (SymPy 1.14+)

## Dependencias da Skill
- `reasoning-orchestrator` (compativel com raciocinios: algebraic_manipulation, pattern_recognition, inductive_generalization)

## Test Results
- CT-1 to CT-4: PASSED
