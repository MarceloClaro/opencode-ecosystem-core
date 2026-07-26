# SPEC-963: Redução de Dependência de LLM na Orquestração

**Round**: R50
**Data**: 2026-07-25
**Status**: 80% Implementado (4/5 componentes + fachada unificada)
**Score**: 0.92

## Objetivo

Substituir chamadas de LLM na orquestração por bibliotecas Python
determinísticas locais, reduzindo custo, latência e dependência de
conectividade.

## Estratégias

1. **Whoosh3Engine** ✅ — substitui busca semântica via LLM no MetaBus
   por full-text indexação local (BM25F, < 30ms por consulta)
2. **RuleBasedRouter** ✅ — substitui AttentionRouter (LLM) por
   DecisionTreeClassifier do sklearn + 25 regras regex determinísticas
   (21 classes de agentes, ~2ms por roteamento)
3. **LocalClassifier** ✅ — substitui classificação por LLM (Ollama/OpenAI)
   por TF-IDF + LogisticRegression + 10 regras regex (10 classes,
   ~0.3ms por classificação)
4. **GameTheoryLocal** ✅ — substitui debate_strategies.py (146 calls
   de reasoning) por nashpy + numpy (Nash, Shapley, Pareto, Stackelberg,
   ~3ms média)
5. **Jinja2Templates** — substitui geração de texto por LLM por
   templates Jinja2 pré-definidos (pendente)

### Componente Integrador

6. **LLMReductionLayer** ✅ — fachada unificada que expõe todos os 4
   componentes em uma única interface `get_reduction_layer()`, com
   contador de chamadas LLM evitadas.

## Métricas de Performance

| Componente | Tempo (ms) | vs LLM (ms) | Ganho |
|---|---|---|---|
| Whoosh3Engine | 29 | 2000-5000 | **69-172x** |
| RuleBasedRouter | 2 | 2000-5000 | **1000-2500x** |
| LocalClassifier | 0.3 | 1500-3000 | **5000-10000x** |
| GameTheoryLocal | 3 | 5000-8000 | **1667-2667x** |

## Critérios de Aceitação

- [x] Whoosh3Engine indexa e busca em < 100ms (29ms real ✓)
- [x] RuleBasedRouter classifica tarefas com acurácia > 85%
- [x] LocalClassifier opera sem qualquer API externa
- [x] GameTheoryLocal calcula Nash/Stackelberg/Shapley sem LLM
- [ ] Modo offline: ecossistema opera sem OPENAI_API_KEY (parcial — 4/5 componentes)
- [ ] Jinja2Templates para geração de documentos

## Impacto Atual

- **Chamadas LLM evitáveis por dia**: ~162 (est.) no ciclo de orquestração
- **Latência reduzida**: de segundos para milissegundos (69-10000x)
- **Custo zero** de API tokens para 4 operações críticas
- **Operação offline** parcial (4/5 componentes funcionam sem internet)

## Arquivos Implementados

| Arquivo | Linhas | Componente |
|---|---|---|
| `skills/tooling/whoosh3_engine.py` | 267 | Whoosh3Engine |
| `skills/tooling/rule_based_router.py` | 379 | RuleBasedRouter |
| `skills/tooling/local_classifier.py` | 302 | LocalClassifier |
| `skills/tooling/game_theory_local.py` | 290 | GameTheoryLocal |
| `skills/tooling/llm_reduction.py` | 228 | LLMReductionLayer |
| `agents/catalog/gametheory-local.md` | 41 | Agent card |
| `agents/catalog/llm-reduction.md` | 42 | Agent card |
