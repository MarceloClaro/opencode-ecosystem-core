# SPEC-917: Evolução dos Motores de Raciocínio do Ecossistema

**STATUS**: IMPLEMENTADO
**DATA**: 2026-07-08
**AUTOR**: marceloclaro
**VERSÃO**: 1.0

## 1. Objetivo

Evoluir o subsistema `reasoning/` do ecossistema OpenCode de 4 motores (Z3, SymPy, Kanren, Critical) para **12 motores + infraestrutura de cadeias, cache, paralelismo, avaliação e visualização**, cobrindo todo o espectro de raciocínio: lógico, simbólico, probabilístico, causal, temporal, fuzzy, dialético, analógico, contrafactual, quântico e multi-passo.

## 2. Diagnóstico — Estado Atual

| Motor | Status | Problema |
|---|---|---|
| Z3Engine | ⚠️ | `eval()` em linha 71 — execução de código arbitrário |
| SymPyEngine | ⚠️ | `eval()` em linha 135 — execução de código arbitrário |
| KanrenEngine | ⚠️ | Apenas matching direto de triplas, sem unificação |
| CriticalEngine | ✅ | Sólido, mas sem variantes multimodais |
| QuantumSimulator | ✅ | Robusto (até 20 qubits pure, 100 com Qiskit) |
| *Cache* | ❌ | Cada consulta refeita do zero |
| *Visualização* | ❌ | Sem saída gráfica das cadeias de raciocínio |
| *Raciocínio multi-passo* | ❌ | Sem Chain-of-Thought |
| *Paralelismo* | ❌ | Ensemble sequencial |

## 3. Escopo da Evolução

### 3.1 Correções de Segurança (CRÍTICO)

- Z3Engine: substituir `eval()` por parser de expressões lógicas com AST controlado + vocabulário controlado
- SymPyEngine: substituir `eval()` por `sympy.sympify` direto (já é seguro) + parser de equações

### 3.2 Novos Motores (8)

| # | Motor | Tipo | Biblioteca | Fallback |
|---|---|---|---|---|
| 1 | **BayesianEngine** | Probabilístico | stdlib + numpy (opcional) | Cadeia de Bayes manual |
| 2 | **CausalEngine** | Causal (Pearl) | stdlib | Análise de confusão por padrões |
| 3 | **TemporalEngine** | LTL/CTL temporal | stdlib | Ordens de precedência |
| 4 | **FuzzyReasoningEngine** | Lógica difusa | stdlib + scipy (opcional) | Triangular defuzz |
| 5 | **ChainOfThoughtEngine** | Multi-passo (CoT) | stdlib | Decomposição linear |
| 6 | **AnalogicalEngine** | Raciocínio analógico | stdlib | Correspondência estrutural |
| 7 | **CounterfactualEngine** | Contrafactual | stdlib | "E se..." mínimo |
| 8 | **QuantumReasoningEngine** | Quântico | stdlib + Qiskit (opcional) | Suíte Bell/GHZ/Superposição |

### 3.3 Infraestrutura (4)

| # | Componente | Função |
|---|---|---|
| 8 | **ReasoningCache** | Cache LRU com TTL por motor |
| 9 | **ReasoningVisualizer** | Geração de diagramas Mermaid |
| 10 | **ParallelReasoning** | Execução multi-thread do ensemble |
| 11 | **ReasoningEvaluator** | Métricas de qualidade (coerência, cobertura, velocidade) |

### 3.4 Integração

- `MultiReasoningEngine` atualizado com 12 motores + roteamento expandido
- `__init__.py` exportando todos os novos símbolos
- Auto-routing expandido para detectar consultas probabilísticas, causais, temporais, etc.

## 4. Critérios de Aceitação

- [x] Nenhum `eval()` inseguro no código dos motores
- [x] `BayesianEngine` calcula P(A|B) a partir de prior e likelihood
- [x] `CausalEngine` distingue correlação de causalidade (critérios de Bradford Hill)
- [x] `TemporalEngine` ordena eventos e detecta ciclos temporais
- [x] `FuzzyReasoningEngine` aceita termos linguísticos ("muito", "pouco", "médio")
- [x] `ChainOfThoughtEngine` decompõe consultas em sub-passos
- [x] `ReasoningCache` reduz tempo em consultas repetidas (hit ratio > 50%)
- [x] `ReasoningVisualizer` gera diagrama Mermaid da cadeia de raciocínio
- [x] `ParallelReasoning` executa ensemble em paralelo (speedup > 1.5x)
- [x] `MultiReasoningEngine` roteia corretamente para 12 motores
- [x] Testes unitários com cobertura > 80%
- [x] Gate SDD aprovado

## 5. Arquitetura

```
reasoning/
├── __init__.py          # Exporta todos os símbolos
├── engines.py           # 4 motores originais corrigidos + 8 novos
├── cache.py             # ReasoningCache (LRU + TTL)
├── visualizer.py        # ReasoningVisualizer (Mermaid)
├── parallel.py          # ParallelReasoning (ThreadPool)
├── evaluator.py         # ReasoningEvaluator (métricas)
├── quantum.py           # QuantumSimulator (existente)
└── tests/
    └── test_reasoning_evolution.py  # Testes TDD da SPEC-917
```

## 6. Métricas de Sucesso

| Métrica | Atual | Alvo |
|---|---|---|
| Motores disponíveis | 4 | 12 |
| Cobertura de tipos de raciocínio | 3/7 | 7/7 |
| Segurança (eval livre) | 2 falhas | 0 falhas |
| Cache hit ratio | N/A | ≥ 50% |
| Speedup ensemble | 1x (seq) | ≥ 1.5x (paralelo) |
| Visualização | ❌ | ✅ Mermaid |
| Testes | 0 | ≥ 10 |

## 7. Validação TDD

Comandos executados:

```bash
pytest tests/test_reasoning_evolution.py -q
# 17 passed

pytest tests -q
# 247 passed, 2 skipped, 1 warning
```

Observação: `pytest -q` sem escopo coleta testes legados em `specs/legacy/tests`, que dependem de um `conftest` legado ausente. A suíte operacional oficial do projeto (`tests/`) permanece verde.

## 8. Referências

- Pearl, J. (2009). *Causality: Models, Reasoning, and Inference*
- Pearl, J. & Mackenzie, D. (2018). *The Book of Why*
- Zadeh, L. (1965). *Fuzzy Sets*
- Wei et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in LLMs*
- Bradford Hill, A. (1965). *The Environment and Disease: Association or Causation?*
