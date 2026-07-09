# opencode-deep-research

**DeepEvidence-Style Hierarchical Deep Research with Evidence Graphs**

Parte do OpenCode Ecosystem Core (R102 — Deep Research Agent).

## Instalação

```bash
pip install opencode-deep-research
```

## Uso

```python
from opencode_deep_research import (
    EvidenceGraph, Entity, Relation,
    BFRSAgent, DFRSAgent, KnowledgeBaseRegistry, Orchestrator
)

registry = KnowledgeBaseRegistry()
registry.register_kb("semantic_scholar", {"type": "academic"})

bfrs = BFRSAgent(registry)
dfrs = DFRSAgent(registry)
orchestrator = Orchestrator(bfrs, dfrs, registry)
results = orchestrator.run("Your research question")
```

## Componentes

- **EvidenceGraph**: Grafo de conhecimento entidade-relação-evidência
- **BFRSAgent**: Busca ampla (Broad-First Research Search)
- **DFRSAgent**: Mergulho profundo (Deep-First Research Search)
- **KnowledgeBaseRegistry**: Registro e consulta de fontes

## Dependências

- Python ≥ 3.10
