# Deep-Research Skill

**Pesquisa Profunda Multi-Fontes — R102 Deep Research Agent**

Baseado no framework DeepEvidence (hierarchical orchestration with evidence graphs),
este skill implementa busca hierárquica com varredura ampla (BFRS) + mergulho profundo (DFRS).

## Comandos

| Comando | Descrição |
|---------|-----------|
| `/deep-research <query>` | Inicia pesquisa profunda (BFRS+DFRS) |
| `/deep-evidence <claim>` | Busca evidências para uma afirmação |
| `/deep-graph <entity>` | Explora grafo de evidências |
| `/deep-summary` | Gera sumário da pesquisa |

## Uso

```
/deep-research "Impact of chain-of-thought prompting on LLM reasoning"
/deep-evidence "CoT improves mathematical reasoning by 20%"
/deep-graph "chain-of-thought"
/deep-summary
```

## Exemplo de saída

```
Evidence Graph: 24 entidades, 47 relações
Caminho crítico: chain-of-thought → step-by-step → mathematical reasoning (score: 0.89)
Fontes consultadas: 12
```

## Dependências

- Python ≥ 3.10
- `agentic_science_v2` (core OpenCode Ecosystem)
