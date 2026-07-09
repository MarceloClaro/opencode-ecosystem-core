# Evo-Science Skill

**Ciclo Evolutivo de Descoberta Científica — R101 Agentic Science V2**

Baseado no framework EvoSci (bio-inspired multi-agent research), este skill
implementa um ciclo darwiniano de hipóteses: Mentor → Researcher → Reviewer → Evolution.

## Comandos

| Comando | Descrição |
|---------|-----------|
| `/evo-init <topic>` | Inicializa ciclo evolutivo com hipótese inicial |
| `/evo-evolve` | Executa uma rodada de seleção→crossover→mutação→herança |
| `/evo-status` | Mostra estado atual da população de hipóteses |
| `/evo-report` | Gera relatório de evolução |

## Uso

```
/evo-init "Quantum attention mechanisms for efficient transformers"
/evo-evolve
/evo-status
/evo-report
```

## Exemplo de saída

```
População: 8 hipóteses | Geração: 3 | Fitness médio: 0.78
Melhor hipótese: "Sparse quantum attention with topological protection"
Score: 0.92 | Diversity: 0.65
```

## Dependências

- Python ≥ 3.10
- `agentic_science_v2` (core OpenCode Ecosystem)
