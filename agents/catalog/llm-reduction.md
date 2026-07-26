# LLM Reduction Layer

**ID:** `llm-reduction`
**Tipo:** Fachada unificada
**Fonte:** `skills/tooling/llm_reduction.py`

## Descrição

Camada única que integra os 4 substitutos locais de LLM:

| Componente | Substituto de | LLM Calls Evitadas |
|---|---|---|
| Whoosh3Engine (BM25F) | Busca semântica via LLM | ~10/chamada |
| RuleBasedRouter (regex + DecisionTree) | AttentionRouter | ~21 classes/tarefa |
| LocalClassifier (TF-IDF + LogReg + regras) | Ollama/OpenAI classificação | ~10 classes/texto |
| GameTheoryLocal (nashpy + numpy) | debate_strategies | ~146 chamadas |

## Impacto Econômico

- **Custo evitado**: ~$0.02 a $0.50 por chamada LLM eliminada
- **Latência reduzida**: ~3ms média vs 2-10s via LLM
- **Offline-first**: 100% operacional sem internet

## Uso

```python
from skills.tooling.llm_reduction import get_reduction_layer
layer = get_reduction_layer()

# Roteia sem LLM
agent = layer.route("preciso buscar biblioteca python")

# Busca full-text sem LLM
docs = layer.search("trust engine slashing")

# Classifica intenção sem LLM
intent = layer.classify("implementar função")
```
