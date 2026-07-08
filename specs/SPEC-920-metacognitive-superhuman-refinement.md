# SPEC-920: Metacognitive Superhuman Refinement Suite

**STATUS**: IMPLEMENTADO  
**DATA**: 2026-07-08  
**AUTOR**: marceloclaro  
**VERSÃO**: 1.0

## 1. Objetivo

Refinar o ecossistema inteiro por meio de uma camada metacognitiva mensurável e conservadora, capaz de avaliar, explicar e melhorar o próprio ciclo operacional do OpenCode Ecosystem Core.

O foco é sair de “metacognição procedural” para **metacognição auditável research-grade**, preparando o caminho para um futuro selo `metacognitive_superhuman_verified` somente após validação externa.

## 2. Diagnóstico

O ecossistema já possui:

- `MetaBus` como Global Workspace;
- `MetacognitiveMemory` episódica/semântica;
- `ReflexionEngine` pós-tarefa;
- `Blackboard` A2A;
- `TrustEngine` + `BehavioralGate`;
- `NaturalForgetting`;
- `HierarchicalMemory`;
- `EvolutionRegistry`;
- SDD/TDD operacional.

Lacunas atuais:

- reflexões ainda são heurísticas simples;
- não há benchmark dedicado de metacognição;
- não há score formal de maturidade metacognitiva;
- não há análise causal estruturada de falhas;
- não há política central para impedir overclaim metacognitivo;
- não há relatório agregando memória, confiança, reflexion, trust, RAG e evolução.

## 3. Escopo

Criar módulo:

```text
mci/metacognitive_evaluator.py
```

Componentes:

- `MetacognitiveTrace` — unidade auditável de ação/reflexão.
- `MetacognitiveEvaluator` — avalia maturidade metacognitiva.
- `MetacognitiveBenchmarkSuite` — executa casos determinísticos de benchmark.
- `classify_metacognitive_tier()` — classifica nível conservador.
- `run_metacognitive_superhuman_suite()` — gera relatório integrado.

## 4. Dimensões avaliadas

| Dimensão | Peso | Descrição |
|---|---:|---|
| Awareness | 20% | Percepção de contexto, estado, riscos e histórico |
| Reflection | 20% | Qualidade da reflexão pós-tarefa e extração de lições |
| Adaptation | 20% | Mudança de confiança/estratégia após feedback |
| Memory Quality | 15% | Recuperação, promoção, esquecimento e relevância |
| Error Causality | 15% | Explicação causal de falhas e prevenção de repetição |
| Epistemic Humility | 10% | Abstenção/evitar overclaim quando evidência é baixa |

## 5. Tiers

| Tier | Condição |
|---|---|
| `reactive` | score < 50 |
| `reflective` | 50 ≤ score < 70 |
| `research_grade` | 70 ≤ score < 85 |
| `metacognitive_superhuman_candidate` | score ≥ 85, sem validação externa |
| `metacognitive_superhuman_verified` | score ≥ 90 e `external_validation=True` |

## 6. Critérios de Aceitação

- [x] Existe `mci/metacognitive_evaluator.py` com API pública testável.
- [x] `classify_metacognitive_tier()` impede `verified` sem `external_validation=True`.
- [x] Benchmark detecta repetição de erro e recomenda mudança de estratégia.
- [x] Benchmark mede atualização de confiança após sucesso/falha.
- [x] Benchmark mede qualidade de memória e recuperação.
- [x] Benchmark mede humildade epistêmica/abstenção em baixa evidência.
- [x] Relatório retorna `readiness_score`, `tier`, `dimensions`, `recommendations` e `evidence`.
- [x] Integra R55: política conservadora anti-overclaim.
- [x] Testes RED→GREEN cobrem ao menos 8 cenários.
- [x] Suíte operacional `pytest tests -q` permanece verde.

## 7. Política de Claim

É proibido declarar `metacognitive_superhuman_verified` sem validação externa explícita. Em ambiente interno, o máximo permitido é `metacognitive_superhuman_candidate`.

## 8. Validação TDD

```bash
pytest tests/test_metacognitive_superhuman.py -q
# 8 passed
```

Validação operacional completa executada após implementação:

```bash
pytest tests -q
# 263 passed, 2 skipped, 1 warning
```
