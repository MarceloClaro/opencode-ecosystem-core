# ADR-011: Rupture Potential Index (SPEC-055)

**Status:** proposed
**Data:** 2026-06-25
**Autor:** Marcelo Claro Laranjeira; Coautor: Interlocutor Externo (HiddenGapTheory)
**Inspirado por:** Necessidade de complementar o EPS (viabilidade) com uma métrica de potencial de ruptura (risco-recompensa)

## Contexto

O PotentialityEstimator v2 (SPEC-045) calcula o Epistemic Potential Score (EPS) para priorizar oportunidades de pesquisa com base em viabilidade, alinhamento e impacto. Porém, o EPS é uma métrica **conservadora** — prioriza o que é viável e alinhado, não necessariamente o que tem potencial de **reconfigurar o campo**.

O ecossistema precisa de um índice complementar que capture **risco-recompensa assimétrica**:
- Oportunidades com alto potencial de ruptura podem ter baixa viabilidade imediata (alta incerteza)
- Ignorá-las pode ter alto custo de oportunidade a longo prazo
- A combinação EPS × RPI gera um portfólio balanceado entre exploração e explotação

Sem essa métrica, o ecossistema tende a um viés de **explotação** (otimizar o conhecido) em detrimento de **exploração** (investir no incerto).

## Decisão

Criar `SPEC-055-RupturePotentialIndex.md` como métrica complementar ao EPS, calculada como:

```
RPI = (DE × 0.30 + FT × 0.25 + RR × 0.25 - CO × 0.20) × 100

Onde:
  DE = Distância Epistemológica (quão diferente do mainstream)
  FT = Fertilidade Teórica (quantas teorias conecta)
  RR = Risco-Recompensa (impacto × (1 - incerteza))
  CO = Custo de Oportunidade (penalidade por ignorar)
```

A decisão composta usa matriz EPS × RPI com 4 quadrantes:
- **Ruptura Segura** (EPS ≥ 60, RPI ≥ 60): executar imediato
- **Ruptura Especulativa** (EPS < 60, RPI ≥ 60): research grant
- **Melhoria Incremental** (EPS ≥ 60, RPI < 60): executar condicional
- **Rotina** (EPS < 60, RPI < 60): baixa prioridade

## Consequências

**Positivas:**
- Balanceia exploração vs. explotação no roadmap de pesquisa
- Captura oportunidades que o EPS ignora por inviabilidade momentânea
- Gera portfólio diversificado de risco-recompensa
- Formaliza o "custo de oportunidade" como métrica explícita

**Negativas:**
- RPI é intrinsecamente mais incerto que EPS (mede potencial futuro)
- Pesos α₁-α₄ são subjetivos (literatura-grounded, mas não calibrados)
- Risco de superestimação: oportunidades "exóticas" com RPI alto mas inviabilidade real
- Depende de múltiplos scanners como input (acoplamento alto)

## Dependências
- SPEC-028 (NoologicalScanner) — densidades por dimensão
- SPEC-043 (PotentialityScanner) — DNA de capacidades
- SPEC-045 (PotentialityEstimator v2) — EPS
- SPEC-053 (CognitiveDiversityScanner) — HI
- SPEC-054 (EpistemicTopologyMapper) — DE, zonas de vazio

## Thresholds
- RPI ≥ 80 → Ruptura (pode redefinir o campo)
- RPI ≥ 60 → Transformação (muda significativamente)
- RPI ≥ 40 → Expansão (preenche lacuna importante)
- RPI < 40 → Incremento (melhoria marginal)
