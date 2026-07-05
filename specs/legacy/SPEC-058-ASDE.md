# SPEC-058: Autonomous Scientific Discovery Engine (R29)

**Ciclo:** R29 — ASDE
**Status:** SDD Completo
**Prioridade:** Alta
**Inspiração:** InternAgent (Shanghai AI Lab, 1.332★), SciAgents (MIT)

---

## 1. Visão Geral

Pipeline autônomo de descoberta científica que integra todos os componentes R27+R28 em um ciclo fechado: **Pergunta → Hipótese → Experimento → Resultado → Relatório**.

```
OQS (R27) ──► ARCHE RLT (R28) ──► RUMI (R28) ──► ASDE (R29)
  │                │                   │                │
  └── pergunta ────┴── árvore lógica ──┴── hipóteses ──┴── descoberta
                                                           │
                                                      Relatório
                                                    Científico
```

## 2. Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│              ASDE — Autonomous Scientific Discovery          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  IdeaGenerator ───► Gera ideias de pesquisa a partir de     │
│                      OQS + RUMI + ARCHE RLT                  │
│                                                              │
│  OntologyGraph ───► Grafo de conhecimento científico         │
│                      (SciAgents-inspired)                     │
│                                                              │
│  MultiAgentCritic ──► Revisão multi-agente das hipóteses     │
│                        (Scientist 1 → Scientist 2 → Critic)  │
│                                                              │
│  ExperimentPlanner ──► Plano experimental com OPUS            │
│                                                              │
│  ResultSynthesizer ─► Síntese dos resultados em relatório    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.1 IdeaGenerator

Gera ideias de pesquisa usando:
- **OQS** (R27): pergunta ótima a partir de um problema
- **ARCHE RLT** (R28): árvore lógica de raciocínio
- **RUMI** (R28): hipóteses causais
- **OntologyGraph**: conceitos científicos conectados

**Score de inovação**: novelty + feasibility + impact

### 2.2 OntologyGraph

Grafo de conhecimento científico com:
- Nós: conceitos, métodos, teorias, domínios
- Arestas: relações semânticas (causa, deriva, exemplifica, contrasta)
- Busca por caminhos não óbvios entre conceitos (inspirado SciAgents)

### 2.3 MultiAgentCritic

Revisão adversarial multi-agente (SciAgents-inspired):
- **Scientist 1**: propõe mecanismo
- **Scientist 2**: oferece contra-argumento
- **Critic**: avalia e sintetiza
- **Planner**: estrutura plano de pesquisa

### 2.4 ExperimentPlanner

Converte hipótese em plano experimental usando OPUS (R28):
- Open: definir escopo do experimento
- Plan: mapear etapas, métricas, recursos
- Unfold: executar simulação
- Seal: validar resultados

### 2.5 ResultSynthesizer

Gera relatório científico a partir dos resultados:
- Formato IMRaD (Introduction, Methods, Results, and Discussion)
- Citações e referências
- Qualis A1 compliance

---

## 3. Pipeline Completo

```
Entrada: Problema de pesquisa (texto livre)
  │
  ▼
1. IdeaGenerator.generate(problem)
  ├── OQS: pergunta ótima
  ├── RUMI: hipóteses causais
  ├── ARCHE RLT: árvore lógica
  └── OntologyGraph: conceitos relacionados
  │
  ▼
2. MultiAgentCritic.review(idea)
  ├── Scientist 1: propõe mecanismo
  ├── Scientist 2: contra-argumenta
  ├── Critic: avalia
  └── Planner: estrutura
  │
  ▼
3. ExperimentPlanner.plan(hypothesis)
  ├── OPUS Open: escopo
  ├── OPUS Plan: etapas
  ├── OPUS Unfold: execução simulada
  └── OPUS Seal: validação
  │
  ▼
4. ResultSynthesizer.synthesize(results)
  ├── IMRaD structure
  ├── Qualis A1 compliance
  └── Relatório final
  │
  ▼
Saída: Relatório de descoberta científica
```

---

## 4. Métricas

| Métrica | Alvo | Descrição |
|:--------|:----:|:----------|
| Ideias geradas por problema | ≥3 | Diversidade de hipóteses |
| Score de inovação médio | ≥0.7 | novelty + feasibility + impact |
| Críticas por rodada | ≥2 | Scientist 1 + Scientist 2 |
| Planos experimentais gerados | ≥1 | Por hipótese |
| Relatórios sintetizados | 100% | Pipeline completo |
| Tempo total do pipeline | <30s | Para problemas de até 500 palavras |

---

## 5. Integração com Ecossistema

```
TrustEngine (SPEC-038) ───► Witness Pattern (R28) ───► Observa pipeline
       │                                                      │
       └──────────────────────┬───────────────────────────────┘
                              ▼
                    ASDE Pipeline (R29)
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              ARCHE RLT (R28)     OPUS (R28)
              + RUMI (R28)        + OQS (R27)
```

---

## 6. 12 CTs TDD

| CT | Descrição | Entrada | Resultado Esperado |
|:---|:----------|:--------|:-------------------|
| CT-058-001 | IdeaGenerator gera ideias | problema científico | ≥3 ideias com scores |
| CT-058-002 | OntologyGraph conecta conceitos | 2 conceitos distintos | Caminho não óbvio |
| CT-058-003 | MultiAgentCritic revisa hipótese | hipótese | críticas de 2+ agentes |
| CT-058-004 | ExperimentPlanner cria plano | hipótese revista | plano OPUS válido |
| CT-058-005 | ResultSynthesizer gera relatório | resultados | relatório IMRaD |
| CT-058-006 | Pipeline completo executa | problema | relatório final |
| CT-058-007 | Integração OQS→ASDE | problema → OQS → ASDE | pipeline encadeado |
| CT-058-008 | Integração RUMI→ASDE | variáveis → hipóteses → ASDE | hipóteses no relatório |
| CT-058-009 | Score de inovação | ideia com novelty baixa | score < 0.5 |
| CT-058-010 | Score de inovação alto | ideia com novelty alta | score ≥ 0.7 |
| CT-058-011 | OntologyGraph busca caminhos | grafo com 10 nós | caminhos de 2+ hops |
| CT-058-012 | Pipeline com entrada inválida | vazio | erro tratado |
