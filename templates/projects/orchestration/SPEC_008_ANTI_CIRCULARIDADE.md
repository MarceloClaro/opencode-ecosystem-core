---
spec_id: SPEC-008
title: "Anti-Circularity Validation Framework"
version: "1.0"
status: "ATIVA"
tdd_suite: "tests/test_anticircularidade.py"
dependencies: [SPEC-001, INTEGRIDADE.md]
last_updated: "2026-05-30"
---

# SPEC-008 — Anti-Circularity Validation Framework

## 1. Objetivo

Fornecer um framework de validacao que detecte e mitigue a circularidade
auto-avaliativa quando nao existe ground truth externo para o dominio
(ausencia de equivalente a Project Euler, Rosalind ou benchmark estabelecido).

## 2. Entradas

| Entrada | Tipo | Descricao |
|---------|------|-----------|
| `corpus` | `List[Document]` | Corpus com timestamps ou metadados temporais |
| `model` | `ExtractorModel` | Modelo de extracao de padroes a ser validado |
| `transformations` | `List[Transform]` | Lista de funcoes de perturbacao (T1-T4) |
| `annotator_budget` | `int` | Numero maximo de documentos a anotar (default: 30) |

## 3. Processamento

### 3.1 Pipeline

```
corpus ──▶ [C1: Temporal Split] ──▶ [C2: Adversarial Perturbation] ──▶ [C3: Active Annotation]
              │                            │                                  │
              ▼                            ▼                                  ▼
         score_temporal              robustness_score                   human_agreement
              │                            │                                  │
              └────────────────────────────┴──────────────────────────────────┘
                                           │
                                           ▼
                                  Matriz de Decisao (A-F)
                                           │
                                           ▼
                                  Relatorio de Transparencia
```

### 3.2 Camada 1 — Split Temporal Cego

```
Input:  corpus com timestamps, cutoff_date
Output: temporal_score ∈ [0, 1], temporal_report

1. Ordenar corpus por timestamp
2. Split: treino = doc.timestamp ≤ cutoff; teste = doc.timestamp > cutoff
3. Treinar modelo em treino
4. Extrair padroes em teste
5. Comparar com padroes extraidos em treino
6. Calcular Jaccard similarity entre conjuntos de padroes
7. temporal_score = |padroes_teste ∩ padroes_treino| / |padroes_treino|
```

### 3.3 Camada 2 — Perturbacao Adversária

```
Input:  corpus, model, transformations=[T1, T2, T3, T4]
Output: robustness_score ∈ [0, 1], robustness_report

1. Para cada T_j:
   a. Gerar corpus perturbado D_j = T_j(corpus)
   b. Extrair padroes P_j = model.extract(D_j)
   c. Calcular Jaccard(P_original, P_j)
2. robustness_score = media das 4 similaridades
3. Identificar quais perturbacoes causaram maior queda
```

### 3.4 Camada 3 — Anotacao Humana Ativa

```
Input:  corpus, model, annotator_budget
Output: human_agreement ∈ [0, 1], human_report

1. Selecionar documentos por uncertainty sampling
2. Apresentar ao especialista com 3 perguntas por padrao
3. Calcular agreement = acordos / (acordos + desacordos)
4. Se agreement < 0.7, expandir amostra ate o triplo
5. Reportar IC 95% binomial exato (Clopper-Pearson)
```

## 4. Saidas

| Saida | Tipo | Descricao |
|-------|------|-----------|
| `temporal_score` | `float` | Similaridade Jaccard entre padroes treino e teste |
| `robustness_score` | `float` | Media de similaridade sob perturbacao |
| `human_agreement` | `float` | Proporcao de concordancia do especialista |
| `decision_matrix` | `str` | Cenario A-F |
| `transparency_report` | `str` | Relatorio em linguagem natural com limitacoes |

## 5. Criterios de Aceitacao (CTs)

| CT | Descricao | Esperado |
|:--:|-----------|----------|
| CT-8.1 | Split temporal com cutoff preserva ordem causal | treino.max_timestamp ≤ cutoff < teste.min_timestamp |
| CT-8.2 | Perturbacao T1 (shuffle paragrafos) reduz similaridade para corpus com estrutura | Jaccard < 1.0 |
| CT-8.3 | Perturbacao T3 (inverter cronologia) preserva padroes a-temporais | Jaccard ≈ 1.0 para padroes sem dependencia temporal |
| CT-8.4 | Uncertainty sampling seleciona documentos com maior entropia | entropia media dos 30 selecionados > entropia media de 30 aleatorios |
| CT-8.5 | Relatorio de transparencia inclui todas as 4 secoes obrigatorias | Nivel, Camadas, Cenario, Limitacoes |
| CT-8.6 | Matriz de decisao classifica corretamente os 6 cenarios | A-F mapeados conforme tabela |
| CT-8.7 | Tempo de execucao C1+C2 < 5 minutos para corpus ate 10K docs | t < 300s |
| CT-8.8 | IC 95% para human_agreement usa Clopper-Pearson exato | binomial exato, nao aproximacao normal |
| CT-8.9 | Documentacao cita no minimo 5 das 15 referencias do framework | ≥ 5 citacoes com DOI |

## 6. Integracao com Cora-Debate

A triangulacao anti-circularidade opera como **camada adicional de verificacao**
que precede a auto-verificacao Cora-Debate:

```
Triangulacao Anti-Circularidade (C1+C2+C3)
    │
    ▼
Cora-Debate V1-V7 (verificacao simbolica)
    │
    ▼
Qualis A1 Scoring
```

A triangulacao estabelece o **nivel de independencia** da validacao. O
Cora-Debate opera dentro desse nivel, com a ressalva de que scores gerados
em dominios sem validacao externa recebem a penalidade `[auto-reportado]`
conforme INTEGRIDADE.md R-I8.

## 7. Limitacoes da Spec

- A Camada 3 depende de disponibilidade de especialista humano
- O split temporal requer timestamps confiaveis no corpus
- As perturbacoes (T1-T4) sao heuristicas — podem nao cobrir todos os tipos
  de fragilidade
- A matriz de decisao (A-F) e qualitativa — os thresholds sao heuristicos
- A triangulacao reduz, mas nao elimina, a circularidade
