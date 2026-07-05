# SPEC-055: Rupture Potential Index — Índice de Potencial de Ruptura Epistemológica

**Status**: Draft
**Version**: 1.0
**Created**: 2026-06-25
**Author**: Marcelo Claro Laranjeira; Coautor: Interlocutor Externo (conceito original)
**Depends on**: SPEC-028 (NoologicalScanner), SPEC-043 (PotentialityScanner), SPEC-045 (PotentialityEstimator v2), SPEC-048 (CognitiveDiversityScanner), SPEC-049 (EpistemicTopologyMapper)

---

## 1. Problema

O PotentialityEstimator v2 (SPEC-045) calcula o **Epistemic Potential Score (EPS)** para priorizar oportunidades de pesquisa. Porém, o EPS prioriza o que é **viável e alinhado** — não necessariamente o que tem **potencial de reconfigurar o campo**.

O ecossistema precisa de um índice complementar que responda:

- *"Esta oportunidade apenas preenche uma lacuna, ou pode redefinir o campo?"*
- *"Qual o custo de oportunidade de NÃO explorar esta direção?"*
- *"Esta linha de pesquisa reforça o paradigma dominante ou pode rompê-lo?"*
- *"Qual o risco de investir em algo que pode não gerar retorno imediato?"*

O Rupture Potential Index (RPI) não substitui o EPS — **complementa-o**, adicionando uma dimensão de **risco-recompensa assimétrica** (alta recompensa potencial, alta incerteza).

## 2. Progressão Conceitual

```
VIABILIDADE → ALINHAMENTO → POTENCIAL → RUPTURA
SPEC-043     SPEC-029     SPEC-045   SPEC-055
```

| Fase | Métrica | Pergunta | Status |
|------|---------|----------|--------|
| Viabilidade | DNA Match | "O ecossistema suporta?" | v1.0 |
| Alinhamento | TA | "Está alinhado com objetivos?" | v2.0 |
| Potencial | EPS | "Vale a pena investir?" | v2.0 |
| **Ruptura** | **RPI** | **"Pode reconfigurar o campo?"** | **SPEC-055** |

## 3. Arquitetura

```
INPUTS:
├── NoologicalScanner.scan()           → Ausências e densidades
├── CognitiveDiversityScanner          → HI (homogeneidade do campo)
├── EpistemicTopologyMapper            → Distâncias topológicas
├── PotentialityEstimator v2           → EPS por oportunidade
├── EvolutionaryScannerPipeline        → Impactos em cascata
└── Custos estimados de exploração (recursos, tempo, especialistas)

PROCESSO:
├── [F1] Cálculo de Distância Epistemológica (DE)
│   └── Quão distante a oportunidade está do centro de gravidade atual
│
├── [F2] Cálculo de Fertilidade Teórica (FT)
│   └── Quantas conexões interdisciplinares a oportunidade permite
│
├── [F3] Cálculo de Risco-Recompensa (RR)
│   ├── Recompensa: impacto potencial se bem-sucedida
│   ├── Risco: probabilidade de insucesso (incerteza inerente)
│   └── RR = recompensa × (1 - risco)
│
├── [F4] Cálculo do Custo de Oportunidade (CO)
│   └── O que se perde ao NÃO explorar esta direção
│
├── [F5] Cálculo do Rupture Potential Index (RPI)
│   └── Combinação ponderada dos fatores acima
│
└── [F6] Classificação
    ├── RPI ≥ 80 → Ruptura (pode redefinir o campo)
    ├── RPI ≥ 60 → Transformação (muda significativamente)
    ├── RPI ≥ 40 → Expansão (preenche lacuna importante)
    └── RPI < 40 → Incremento (melhoria marginal)

OUTPUTS:
├── RPI_Report (JSON + Markdown)
├── OpportunityPortfolio (matriz risco x recompensa)
├── RuptureCandidates (oportunidades com RPI ≥ 80)
└── CostBenefitAnalysis (comparativo EPS vs RPI)
```

## 4. Fórmulas

### 4.1 Distância Epistemológica (DE)

```
DE(oportunidade_O) = ||v_centro_gravidade - v_O||₂

Onde:
  v_centro_gravidade = vetor médio de todos os artefatos existentes
  v_O = vetor da oportunidade proposta
  DE normalizado para [0, 1]
  
  Quanto maior DE, mais "distante" do mainstream → maior potencial de ruptura
```

### 4.2 Fertilidade Teórica (FT)

```
FT(oportunidade_O) = Σ_{t ∈ T} conexões(O, t) / |T|

Onde:
  T = conjunto de teorias no ecossistema
  conexões(O, t) = 1 se O pode ser investigado via teoria t, 0 caso contrário
  
  FT alto → oportunidade que conecta múltiplos referenciais teóricos
```

### 4.3 Risco-Recompensa (RR)

```
RR(oportunidade_O) = reward(O) × (1 - risk(O))

Onde:
  reward(O) = impacto potencial estimado (EPS-like, normalizado para [0,1])
  risk(O) = incerteza inerente (1 - densidade_do_dominio, normalizado)
  
  RR alto → alta recompensa com baixo risco (raridade)
  RR baixo → baixa recompensa ou alto risco (a maioria)
```

### 4.4 Custo de Oportunidade (CO)

```
CO(oportunidade_O) = Σ_{alternativas_A ≠ O} EPS(A) × similaridade(O, A)

Onde:
  alternativas_A = outras oportunidades de pesquisa
  similaridade(O, A) = 1 - DE(O, A)
  
  CO alto → ignorar esta oportunidade custa caro (muitas alternativas similares com alto EPS)
  CO baixo → há alternativas melhores e diferentes
```

### 4.5 Rupture Potential Index (RPI)

```
RPI = (DE × α₁ + FT × α₂ + RR × α₃ - CO × α₄) / (α₁ + α₂ + α₃ + α₄) × 100

Onde:
  α₁ = 0.30 (peso da distância epistemológica — "quão diferente")
  α₂ = 0.25 (peso da fertilidade teórica — "quanto conecta")
  α₃ = 0.25 (peso do risco-recompensa — "vale o risco")
  α₄ = 0.20 (peso do custo de oportunidade — penalidade por ignorar)
  
  RPI ∈ [0, 100]
```

### 4.6 Decisão Composta EPS × RPI

```
┌─────────────────────────────────────────────────┐
│           │ EPS alto (≥ 60) │ EPS baixo (< 60)  │
├───────────┼─────────────────┼───────────────────┤
│ RPI alto  │ RUPTURA SEGURA   │ RUPTURA ESPECULATIVA │
│ (≥ 60)    │ Executar imediato│ Research Grant      │
├───────────┼─────────────────┼───────────────────┤
│ RPI baixo │ MELHORIA       │ ROTINA              │
│ (< 60)    │ Incremental     │ Baixa prioridade    │
└─────────────────────────────────────────────────┘
```

## 5. Casos de Teste (TDD)

### CT-5001: Oportunidade no Centro de Gravidade
**Given**: Oportunidade idêntica ao centro de gravidade do ecossistema
**When**: O RPI é calculado
**Then**: DE = 0, RPI deve ser < 30 (baixo potencial de ruptura)

### CT-5002: Oportunidade na Periferia Extrema
**Given**: Oportunidade em dimensão não explorada (DE = 1.0)
**When**: O RPI é calculado
**Then**: DE = 1.0, RPI deve ser ≥ 60 (alto potencial se FT e RR acompanharem)

### CT-5003: Alta Fertilidade Teórica (conecta 5+ teorias)
**Given**: Oportunidade que pode ser investigada por 5+ referenciais teóricos diferentes
**When**: FT é calculado
**Then**: FT ≥ 0.8, deve contribuir positivamente para RPI

### CT-5004: Baixa Fertilidade Teórica (conecta 1 teoria)
**Given**: Oportunidade vinculada a apenas 1 referencial teórico
**When**: FT é calculado
**Then**: FT ≤ 0.2, contribuição limitada ao RPI

### CT-5005: Custo de Oportunidade Alto (muitas alternativas similares)
**Given**: 3 alternativas similares com EPS alto (≥ 70 cada)
**When**: CO é calculado para uma delas
**Then**: CO ≥ 0.7, RPI deve ser penalizado (reduzido)

### CT-5006: Risco-Recompensa Favorável (baixo risco, alta recompensa)
**Given**: Oportunidade em domínio denso (risco baixo) com alto impacto potencial
**When**: RR é calculado
**Then**: RR ≥ 0.7, deve contribuir positivamente para RPI

### CT-5007: Risco-Recompensa Desfavorável (alto risco, baixa recompensa)
**Given**: Oportunidade em domínio vazio (risco alto) com baixo impacto potencial
**When**: RR é calculado
**Then**: RR ≤ 0.3, RPI reduzido

### CT-5008: Classificação Correta no Portfolio
**Given**: 4 oportunidades com perfis diferentes (Ruptura, Transformação, Expansão, Incremento)
**When**: O classificador RPI processa as 4
**Then**: Cada uma deve ser classificada na categoria correta conforme thresholds

## 6. Integração com o Ecossistema

```
NoologicalScanner ────────────────────────────────────────┐
CognitiveDiversityScanner ────────────────────────────────┤
EpistemicTopologyMapper ──────────────────────────────────┤
EvolutionaryScannerPipeline ──────────────────────────────┤
PotentialityEstimator v2 ─────────────────────────────────┤
                                                         ▼
                                                  RPI Calculator
                                                         │
                                                         ▼
                                           ┌─────────────────────────┐
                                           │   Portfolio Matrix      │
                                           │   EPS × RPI             │
                                           │                        │
                                           │  Ruptura  │ Especulativo│
                                           │  Segura   │             │
                                           │───────────┼─────────────┤
                                           │  Melhoria │  Rotina     │
                                           │  Incr.    │             │
                                           └─────────────────────────┘
                                                         │
                                                         ▼
                                              ResearchRoadmap v3
                                         (priorizado por EPS × RPI)
```

- RPI **complementa** o EPS — não o substitui
- A matriz EPS × RPI gera 4 quadrantes de decisão
- O roadmap de pesquisa v3 será priorizado por EPS × RPI combinado
- RPI pode ser usado como filtro para submissão de grants

## 7. Critérios de Aceitação

- [ ] 8/8 CTs implementados e passando (100%)
- [ ] RPI calculado para oportunidades com DE, FT, RR, CO
- [ ] Matriz EPS × RPI gerando 4 quadrantes de decisão
- [ ] Classificação correta (Ruptura ≥ 80, Transformação ≥ 60, Expansão ≥ 40, Incremento < 40)
- [ ] Penalização por custo de oportunidade funcionando
- [ ] Documentação em FRAMEWORK.md atualizada
- [ ] Pesos α₁-α₄ configuráveis por domínio
