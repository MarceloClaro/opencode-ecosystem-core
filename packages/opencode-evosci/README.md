# opencode-evosci

**Bio-Inspired Multi-Agent Evolutionary Science Framework**

Parte do OpenCode Ecosystem Core (R101 — Agentic Science V2).

## Instalação

```bash
pip install opencode-evosci
```

## Uso

```python
from opencode_evosci import (
    MentorAgent, PrimeResearcherAgent, ReviewerAgent,
    EvolutionaryEngine, OrchestratorAgent
)

# Ciclo evolutivo completo
orchestrator = OrchestratorAgent()
result = orchestrator.run("Your research topic here")
```

## Componentes

- **MentorAgent**: Gera hipóteses iniciais
- **PrimeResearcherAgent**: Pesquisa aprofundada
- **ReviewerAgent**: Avaliação crítica
- **EvolutionManagerAgent**: Gerencia ciclo evolutivo
- **EvolutionaryEngine**: Seleção → Crossover → Mutação → Herança

## Dependências

- Python ≥ 3.10
