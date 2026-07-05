# SPEC-REA-Z3: Formal Verification (Z3)
Version: 1.0.0 | Status: verified | TDD: required | Engine: Z3Engine

## Objective
Prover e verificar logicamente premissas e conclusoes usando o solver SMT Z3 para raciocinio formal automatizado.

## Acceptance Criteria
- [x] CT-1: `prove("x > 0 and y > 0", "x + y > 0")` retorna valid
- [x] CT-2: `check_sat(["x > 0", "x < 0"])` retorna unsat
- [x] CT-3: `check_sat(["x + y == 10", "x - y == 2"])` retorna sat com x=6, y=4
- [x] CT-4: `prove("x > 0", "x < 0")` retorna invalid (counterexample)

## API Contract

### prove(premise: str, conclusion: str) -> dict
```python
{
    "status": "valid" | "invalid",
    "counterexample": {var: value} | None,
    "proof_time_ms": float
}
```

### check_sat(constraints: list[str]) -> dict
```python
{
    "status": "sat" | "unsat",
    "model": {var: value} | None,
    "solve_time_ms": float
}
```

## Engine
- Classe: `Z3Engine`
- Localizacao: `skills/reasoning/formal-verification/scripts/z3_engine.py`
- Dependencia: `z3-solver` (Z3 4.16+)

## Dependencias da Skill
- `reasoning-orchestrator` (compativel com raciocinios: deduction, contradiction, lemma_tracking)

## Test Results
- CT-1 to CT-4: PASSED
