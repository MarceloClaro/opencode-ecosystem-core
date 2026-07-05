# SPEC-011 — Motores de Raciocínio + Módulo Quântico

```yaml
spec_id: SPEC-011
title: Multi-Reasoning (Z3, SymPy, Kanren, Critical) + Quantum Simulator
module: reasoning/engines.py, reasoning/quantum.py
origin: OpenCode_Ecosystem reasoning engines + quantum module
status: implemented
```

## Objetivo

Raciocínio formal com quatro motores — **Z3** (satisfatibilidade/restrições), **SymPy** (álgebra simbólica), **Kanren** (lógica relacional) e **Critical** (análise crítica heurística, sempre disponível) — mais um **simulador quântico statevector** reprodutível (Bell, GHZ, superposição) com suporte a 2–100 qubits e 5 seeds.

## Requisitos

| ID | Requisito | Critério de Aceitação |
|---|---|---|
| REQ-011.1 | Os 4 motores registrados em `multi_reasoning.engines` | chaves exatas `{z3, sympy, kanren, critical}` |
| REQ-011.2 | Roteamento automático por palavras-chave (`engine="auto"`) | "equação" ⇒ sympy; "restrição/sat" ⇒ z3 |
| REQ-011.3 | O motor Critical nunca fica indisponível (fallback stdlib) | `available is True` sempre |
| REQ-011.4 | Estado de Bell mede apenas `00`/`11`; GHZ tem entropia de emaranhamento 1 bit | testes de correlação passam |
| REQ-011.5 | Faixa de qubits validada: 2 ≤ n ≤ 100 | `ValueError` fora da faixa |
| REQ-011.6 | Reprodutibilidade por seed: mesma seed ⇒ mesmas contagens | suites idênticas com seed 42 |

## Invariantes

- INV-011.1: Norma do statevector = 1 após cada porta (tolerância 1e-9).
- INV-011.2: Motores com dependência ausente degradam para heurística com `available=False`, nunca exceção.

## Testes

`tests/test_advanced_subsystems.py::TestReasoning` + `TestQuantum` (7 testes).
