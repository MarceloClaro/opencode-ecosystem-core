# ADR-009: Cognitive Diversity Scanner (SPEC-053)

**Status:** proposed
**Data:** 2026-06-25
**Autor:** Marcelo Claro Laranjeira; Coautor: Interlocutor Externo (HiddenGapTheory)
**Inspirado por:** Reflexão sobre homogeneidade cognitiva em produção acadêmica — "soluções diferentes ou apenas variantes da mesma linha?"

## Contexto

O ecossistema detecta **ausências** (NoologicalScanner, SPEC-028) mas não detecta **homogeneidade cognitiva** — quando múltiplos artefatos cobrem o mesmo território conceitual com perspectivas quase idênticas. Um conjunto de artigos pode estar tecnicamente correto, bem fundamentado, mas cognitivamente homogêneo — todos exploram variações da mesma tese central.

Sem essa detecção, o ecossistema pode:
- Confundir **quantidade** com **diversidade** ("temos 10 artigos sobre o tema" quando são 10 variações da mesma ideia)
- Deixar de identificar **câmaras de eco** onde um paradigma domina sem concorrência
- Alocar recursos em **replicação** onde deveria alocar em **exploração**

## Decisão

Criar `SPEC-053-CognitiveDiversityScanner.md` como nova camada analítica que:
1. **Clusteriza** artefatos por perfil epistemológico (herdado do NoologicalScanner)
2. **Calcula** Índice de Homogeneidade (HI) para cada cluster
3. **Detecta** câmaras de eco (HI > 0.8)
4. **Recomenda** diversificação para dimensões sub-representadas

O HI é calculado como: `HI = 1 - distância_média_observada / distância_máxima_possível`

## Consequências

**Positivas:**
- Diferencia diversidade genuína de variação superficial
- Permite ao PotentialityEstimator v2 ajustar EPS por homogeneidade
- Gera recomendações acionáveis de diversificação

**Negativas:**
- Depende do NoologicalScanner para taxonomia de dimensões
- Clusters pequenos (< 3 artefatos) não produzem HI significativo
- Risco de falso positivo: artefatos que parecem homogêneos mas são complementares

## Dependências
- SPEC-028 (NoologicalScanner) — taxonomia de 10 dimensões × 92 categorias
- SPEC-030 (EvolutionaryScannerPipeline) — árvore de derivação
- SPEC-045 (PotentialityEstimator v2) — consumo do HI
- SPEC-054 (EpistemicTopologyMapper) — validação geométrica de clusters

## Thresholds
- HI > 0.8 → Câmara de eco (alerta vermelho)
- HI 0.6-0.8 → Baixa diversidade (recomendar diversificação)
- HI 0.3-0.6 → Diversidade moderada (monitorar)
- HI < 0.3 → Alta diversidade (saudável)
