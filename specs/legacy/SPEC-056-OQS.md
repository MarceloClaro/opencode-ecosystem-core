# SPEC-056: Optimal Question Scanner (OQS)

**Status**: Active
**Version**: 1.0
**Created**: 2026-06-29
**Author**: Marcelo Claro Laranjeira
**Ciclo Evolutivo**: R27
**Depends on**: SPEC-036 (Metacognição), SPEC-037 (Structural Noise Scanner), SPEC-045 (Potentiality Estimator v2)

---

## 1. Problema

Grande parte do custo cognitivo em processos de pesquisa, desenvolvimento e auditoria não está na resposta — está na **formulação da pergunta**. Perguntas mal formuladas:

- Ampliam o espaço de busca
- Aumentam o consumo de tokens
- Geram respostas dispersas
- Retardam a descoberta do núcleo estrutural do problema

O ecossistema precisa de uma ferramenta dedicada à **geração, seleção e validação de perguntas ótimas** que minimize o custo cognitivo e maximize a redução de incerteza.

## 2. Pergunta Fundamental

> **Qual pergunta produz a maior redução de incerteza com o menor esforço cognitivo?**

## 3. Hipótese Central

Dado um problema, nem todas as perguntas possuem o mesmo valor. Algumas perguntas apenas ampliam o ruído; outras reduzem drasticamente o espaço de busca.

**Pergunta Ótima** = máxima redução de incerteza + mínima dispersão + alta preservação de direção

## 4. Arquitetura

```
Problema Bruto
    │
    ▼
┌─────────────────────────────┐
│  UncertaintyScanner         │  Etapa 1-3: Intake + Incerteza + Ruído
│  (SPEC-056 Component)       │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  QuestionVectorizer         │  Etapa 4-7: Geração + Vetorização + Seleção
│  (SPEC-056 Component)       │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  Convergence Score (CS)     │  Métrica: URS + SVS - DRI - CCI
│  (SPEC-056 Metric)          │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  Answer Direction Test      │  Etapa 8: Validação de direção
│  (SPEC-056 Component)       │
└─────────────────────────────┘
    │
    ▼
Pergunta Ótima → Scanner Especializado → Resposta Direcionada
```

## 5. Componentes

### 5.1 UncertaintyScanner

Mapeia as incertezas presentes em um problema e filtra ruído estrutural.

| Etapa | Nome | Função |
|:------|:-----|:--------|
| 1 | Problem Intake | Normaliza o problema bruto, extrai objeto de análise e escopo |
| 2 | Uncertainty Scan | Identifica lacunas conceituais, terminológicas, premissas, relações e ambiguidades |
| 3 | Structural Noise Filter | Remove repetições, metáforas excessivas, bifurcações prematuras e termos decorativos |

**Saída**: `UncertaintyScanResult` com incertezas categorizadas por severidade.

### 5.2 QuestionVectorizer

Transforma perguntas candidatas em vetores de 6 dimensões e calcula métricas de convergência.

| Etapa | Nome | Função |
|:------|:-----|:--------|
| 4 | Question Generator | Gera perguntas candidatas de 10 tipos (definição, causalidade, comparação, validação, falsificação, operacionalização, métrica, impacto, sequência, integração) |
| 5 | Question Vectorization | Transforma cada pergunta em vetor Qv com 6 dimensões |
| 6 | Convergence Score | Calcula CS = URS + SVS - DRI - CCI |
| 7 | Optimal Selection | Seleciona Q* = argmax(CS) |
| 8 | Answer Direction Test | Verifica se a resposta provável ajuda a avançar |

**Saída**: `QuestionAnalysisResult` com pergunta ótima, justificativa e descartes.

### 5.3 Vetor da Pergunta (Qv)

Cada pergunta é representada por um vetor de 6 dimensões:

| Dimensão | Escala | Descrição |
|:---------|:-------|:----------|
| direction | 0-10 | Quão direcional é a pergunta |
| scope | 0-10 | Amplitude do escopo |
| depth | 0-10 | Profundidade investigativa |
| reduction_power | 0-10 | Poder de redução de incerteza |
| dispersion_risk | 0-10 | Risco de abrir ruído (MENOR é melhor) |
| cognitive_cost | 0-10 | Custo cognitivo (MENOR é melhor) |

## 6. Métricas

### 6.1 Uncertainty Reduction Score (URS)

```
URS = ReductionPower × (1 - Dispersion/10) × Direction/10
```

Mede quanto a pergunta reduz a incerteza. Escala: 0-10.

### 6.2 Structural Value Score (SVS)

```
SVS = (Depth × Scope) / 10
```

Mede quanto a pergunta atinge o núcleo estrutural. Escala: 0-10.

### 6.3 Dispersion Risk Index (DRI)

```
DRI = DispersionRisk (diretamente do vetor)
```

Mede o risco da pergunta abrir ruído excessivo. Escala: 0-10 (menor é melhor).

### 6.4 Cognitive Cost Index (CCI)

```
CCI = CognitiveCost (diretamente do vetor)
```

Mede o custo cognitivo da pergunta. Escala: 0-10 (menor é melhor).

### 6.5 Convergence Score (CS)

```
CS = URS + SVS - DRI - CCI
```

Métrica final de convergência. Escala: -20 a +20.

| CS | Interpretação |
|:--:|:--------------|
| ≥ 15 | Ótima — perg. com altíssimo poder de convergência |
| ≥ 10 | Forte — bom poder de convergência |
| ≥ 5 | Útil — reduz incerteza moderadamente |
| ≥ 0 | Moderada — valor limitado |
| ≥ -5 | Fraca — pode gerar mais ruído |
| < -5 | Dispersiva — amplia o espaço de incerteza |

## 7. Tipos de Pergunta

| Tipo | Padrão | Exemplo |
|:-----|:-------|:--------|
| Definição | "O que é", "qual é" | "O que é um scanner noológico?" |
| Causalidade | "Por que", "causa" | "Por que perguntas mal formuladas geram dispersão?" |
| Comparação | "Diferença", "versus" | "Qual a diferença entre resumo e compressão estrutural?" |
| Validação | "É válido", "funciona" | "O Convergence Score é válido para todos os tipos de pergunta?" |
| Falsificação | "E se não", "falso" | "Existe um contraexemplo onde o CS falha?" |
| Operacionalização | "Como implementar", "passo a passo" | "Como implementar o Uncertainty Scanner?" |
| Métrica | "Como medir", "quanto" | "Como medir a redução de incerteza?" |
| Impacto | "Impacto", "consequência" | "Qual o impacto de perguntas mal formuladas no consumo de tokens?" |
| Sequência | "Próximo", "depois" | "Qual o próximo passo após selecionar a pergunta ótima?" |
| Integração | "Integrar", "síntese" | "Como integrar o OQS ao pipeline de scanners existente?" |

## 8. Integração com o Ecossistema

### 8.1 Fluxo de Investigação Otimizado

```
Antes:
  Problema → Scanner Noológico → Scanner Teleológico → ... → Resposta

Depois (com OQS):
  Problema → OQS → Pergunta Ótima → Scanner Especializado → Resposta Direcionada
```

### 8.2 Ferramentas MCP

| Ferramenta | Descrição |
|:-----------|:----------|
| `eco_run_oqs_uncertainty_scan` | Escaneia incertezas de um problema |
| `eco_run_oqs_question_analyze` | Analisa e seleciona a pergunta ótima |

### 8.3 Integração com SPEC-045 (Potentiality Estimator)

O OQS pode atuar como **pré-processador** do Potentiality Estimator:
```
Problema → OQS → Pergunta Ótima → PotentialityEstimatorV2 → EPS v2
```

## 9. Critérios de Sucesso

| Critério | Métrica | Alvo |
|:---------|:--------|:-----|
| Cobertura de incertezas | Categorias detectadas | ≥ 4/5 tipos |
| Precisão da pergunta ótima | CS da pergunta selecionada | ≥ 5.0 |
| Filtragem de ruído | Elementos ruidosos identificados | ≥ 1 por 100 palavras |
| Testabilidade | CTs TDD | 12/12 passando |
| Integração MCP | Ferramentas registradas | 2/2 operacionais |

## 10. Evolução Planejada

| Versão | Melhorias |
|:-------|:----------|
| 1.0 | UncertaintyScanner + QuestionVectorizer + Convergence Score |
| 1.1 | Integração com LLM para geração automática de perguntas candidatas |
| 1.2 | Feedback loop: CS real vs CS previsto (aprendizado por reforço) |
| 2.0 | OQS auto-otimizável: perguntas que melhoram o próprio OQS |
