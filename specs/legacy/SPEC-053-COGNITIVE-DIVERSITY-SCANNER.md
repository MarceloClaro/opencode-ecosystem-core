# SPEC-053: Cognitive Diversity Scanner — Detecção de Homogeneidade Cognitiva

**Status**: Draft
**Version**: 1.0
**Created**: 2026-06-25
**Author**: Marcelo Claro Laranjeira; Coautor: Interlocutor Externo (conceito original)
**Depends on**: SPEC-028 (NoologicalScanner), SPEC-030 (EvolutionaryScannerPipeline)

---

## 1. Problema

O NoologicalScanner (SPEC-028) detecta **ausências** — categorias do espaço de conhecimento que não foram exploradas. Porém, ele **não detecta homogeneidade cognitiva**: situações em que múltiplos artefatos cobrem o **mesmo território conceitual** usando perspectivas quase idênticas, gerando uma ilusão de diversidade onde há apenas replicação.

Um conjunto de artigos, dissertações ou pesquisas pode estar:
- **Tecnicamente correto** (aprovado por todos os validadores)
- **Bem fundamentado** (citações adequadas, metodologia sólida)
- **Mas cognitivamente homogêneo** (todos exploram variações da mesma tese central)

O ecossistema atual não diferencia entre:
- **Diversidade genuína**: múltiplas perspectivas sobre o mesmo fenômeno
- **Variação superficial**: mesmas premissas, mesmas metodologias, conclusões ligeiramente diferentes

## 2. Progressão Conceitual

```
ERRO → AUSÊNCIA → HOMOGENEIDADE → DIVERSIDADE
  v1      v3.0       SPEC-053        Ideal
```

| Fase | Scanner | Pergunta | Status |
|------|---------|----------|--------|
| Erro | Validadores TDD | "O que está errado?" | v1.0 |
| Ausência | NoologicalScanner | "O que não existe?" | v3.0 |
| **Homogeneidade** | **CognitiveDiversityScanner** | **"O que parece diferente mas é igual?"** | **SPEC-053** |
| Diversidade | (futuro) | "O que é genuinamente novo?" | TBD |

## 3. Arquitetura

```
INPUTS:
├── NoologicalScanner.scan()           → Cobertura por dimensão
├── EvolutionaryScannerPipeline        → Árvore de derivação de artefatos
├── Multiple artefatos (artigos, teses, outputs)
└── Metadados de similaridade textual e conceitual

PROCESSO:
├── [F1] Clusterização Conceitual
│   └── Agrupa artefatos por dimensões epistemológicas cobertas
│
├── [F2] Cálculo de Distância Cognitiva
│   ├── Distância paradigmática (paradigmas diferentes?)
│   ├── Distância metodológica (métodos diferentes?)
│   ├── Distância teórica (referenciais diferentes?)
│   └── Distância de raciocínio (modos de inferência diferentes?)
│
├── [F3] Índice de Homogeneidade (HI)
│   └── HI = 1 - (distância média observada / distância máxima possível)
│
├── [F4] Detecção de Câmaras de Eco
│   └── Identifica clusters onde HI > 0.8 (alta homogeneidade)
│
└── [F5] Geração de Recomendações de Diversificação
    └── Sugere dimensões sub-representadas para expandir

OUTPUTS:
├── DiversityReport (JSON + Markdown)
├── HomogeneityIndex por cluster
├── EchoChamberMap (visualização de clusters)
└── DiversificationRoadmap
```

## 4. Fórmulas

### 4.1 Distância Cognitiva entre Artefatos A e B

```
DC(A,B) = Σ w_i × d_i(A,B) / Σ w_i

Onde:
  w_i = peso da dimensão i (herdado do NoologicalScanner)
  d_i(A,B) = 0 se A e B compartilham a mesma categoria na dimensão i
             1 se A e B usam categorias diferentes na dimensão i
```

### 4.2 Índice de Homogeneidade (HI)

```
HI(cluster) = 1 - ( Σ DC(A,B) / (N × (N-1) / 2) / DC_max )

Onde:
  N = número de artefatos no cluster
  DC_max = distância máxima possível (10 dimensões × peso máximo)
  HI ∈ [0, 1]
  HI > 0.8 → Câmara de eco (alta homogeneidade)
  HI < 0.3 → Alta diversidade cognitiva
```

### 4.3 Recomendação de Diversificação

```
DiversificationScore(dimensão_i) = 
    w_i × (1 - densidade_atual_i) × (1 - HI_global)
    
Onde:
  w_i = peso adaptativo por domínio
  densidade_atual_i = cobertura atual da dimensão i
  HI_global = homogeneidade média do ecossistema
```

## 5. Casos de Teste (TDD)

### CT-4801: Clusterização de Artefatos com Mesmo Paradigma
**Given**: 3 artefatos que usam o mesmo paradigma positivista e métodos quantitativos
**When**: O scanner processa os 3 artefatos
**Then**: HI deve ser ≥ 0.8 (alta homogeneidade)

### CT-4802: Clusterização de Artefatos com Paradigmas Diferentes
**Given**: 3 artefatos com paradigmas diferentes (positivista, interpretativista, crítico)
**When**: O scanner processa os 3 artefatos
**Then**: HI deve ser ≤ 0.4 (diversidade cognitiva)

### CT-4803: Detecção de Variação Superficial vs. Genuína
**Given**: 2 artefatos com mesmo tema ("eficácia da TCC") mas métodos diferentes (RCT vs. grounded theory)
**When**: O scanner processa os 2 artefatos
**Then**: Distância metodológica = 1.0, HI ajustado deve refletir diversidade metodológica

### CT-4804: Câmara de Eco com 10+ Artefatos Homogêneos
**Given**: 10 artefatos sobre mesmo tema, mesma metodologia, mesmo referencial
**When**: O scanner processa o cluster
**Then**: Relatório deve marcar "ECHO_CHAMBER" e recomendar diversificação

### CT-4805: Recomendação de Dimensão Sub-representada
**Given**: Cluster homogêneo em paradigma (todos positivistas)
**When**: O scanner gera recomendações
**Then**: Deve sugerir exploração de paradigmas alternativos (fenomenológico, crítico)

### CT-4806: Respeito a Pesos Adaptativos por Domínio
**Given**: Domínio = "computacao" (peso teoria_jogos = 1.3)
**When**: O scanner calcula DiversificationScore
**Then**: teoria_jogos deve ter score proporcionalmente maior

### CT-4807: Cluster Vazio (Zero Artefatos)
**Given**: Nenhum artefato para analisar
**When**: O scanner inicia
**Then**: Deve retornar erro controlado "Nenhum artefato para clusterizar"

### CT-4808: Artefato Isolado (Singleton)
**Given**: Apenas 1 artefato no corpus
**When**: O scanner processa
**Then**: HI deve ser 1.0 (indefinido) com mensagem "Cluster insuficiente para análise de homogeneidade"

## 6. Integração com o Ecossistema

```
NoologicalScanner → CognitiveDiversityScanner → PotentialityEstimator v2
       │                      │                        │
       │                      │                        └→ EPS ajustado por diversidade
       │                      └→ DiversityReport ───────→ Roadmap de pesquisa
       └→ Ausências ─────────→ Input [F1]
```

- O CognitiveDiversityScanner **consume** outputs do NoologicalScanner (cobertura por dimensão)
- O PotentialityEstimator v2 **consume** o HI como fator de ajuste no EPS
- O EvolutionaryScannerPipeline **fornece** a árvore de derivação dos artefatos

## 7. Critérios de Aceitação

- [ ] 8/8 CTs implementados e passando (100%)
- [ ] HI calculado para clusters ≥ 3 artefatos
- [ ] Detecção de câmaras de eco com HI > 0.8
- [ ] Recomendações de diversificação acionáveis
- [ ] Documentação em FRAMEWORK.md atualizada
- [ ] Integração com NoologicalScanner testada
- [ ] Pesos adaptativos por domínio funcionando
