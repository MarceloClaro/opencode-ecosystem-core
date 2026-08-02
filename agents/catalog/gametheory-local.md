---
name: gametheory-local
description: Agente especializado gametheory-local
version: '1.0.0'
skills:
- id: gametheory-local
  name: Gametheory Local
  description: Executa tarefas especializadas de gametheory local conforme protocolo SDD/TDD.
  tags: [gametheory, local]
  examples: [Execute esta tarefa conforme especificação, Analise e reporte os resultados]
tags: [gametheory, local]
examples: [Execute esta tarefa conforme especificação, Analise e reporte os resultados, Execute esta tarefa conforme especificação]
---

# GameTheoryLocal

**ID:** `gametheory-local`
**Tipo:** Subagente local (sem LLM)
**Fonte:** `skills/tooling/game_theory_local.py`

## Descrição

Cálculo de teoria dos jogos determinístico usando `nashpy` + `numpy`.
Substitui completamente o módulo `debate_strategies.py` que fazia 146 chamadas
de `reasoning` via LLM para calcular equilíbrios de Nash e valores de Shapley.

## Capacidades

| Capacidade | Descrição | Substitui |
|---|---|---|
| `nash_equilibrium` | Equilíbrio de Nash para 2 jogadores (suporte enum) | `debate_strategies.nash_via_llm` |
| `stackelberg_equilibrium` | Equilíbrio líder-seguidor | otimização manual |
| `shapley_value` | Valor de Shapley justo por agente | distribuição baseada em LLM |
| `pareto_frontier` | Fronteira de Pareto multi-objetivo | trade-off via LLM |

## Performance

- Nash: ~6ms (vs ~5000ms via LLM)
- Shapley: ~3ms (combinatória exata)
- Pareto: ~2ms
- Stackelberg: ~2ms

## Dependências

- `nashpy` (opcional — fallback para estratégia pura)
- `numpy`

## Uso

```python
from skills.tooling.game_theory_local import GameTheoryLocal
gt = GameTheoryLocal()

# Dilema do Prisioneiro
eq = gt.nash_equilibrium([[-1,-3],[0,-2]], [[-1,0],[-3,-2]])
print(eq)
```
