# ADR-010: Epistemic Topology Mapper (SPEC-054)

**Status:** proposed
**Data:** 2026-06-25
**Autor:** Marcelo Claro Laranjeira; Coautor: Interlocutor Externo (HiddenGapTheory)
**Inspirado por:** Metáfora topológica (ilhas, continentes, zonas de vazio) para mapear o espaço do conhecimento produzido

## Contexto

Os scanners existentes analisam o conhecimento produzido em **dimensões discretas e independentes** — paradigmas, métodos, teorias, raciocínio — mas não projetam essas dimensões em um **espaço geométrico contínuo**. O ecossistema consegue listar o que está presente/ausente, mas não consegue responder perguntas relacionais como:

- "Qual a distância epistemológica entre dois artefatos?"
- "Onde estão as ilhas de conhecimento isoladas?"
- "Há zonas de vazio entre clusters de produção?"

Sem essa capacidade, o ecossistema opera com uma **visão escalar** do conhecimento — métricas de densidade, cobertura, alinhamento — mas não constrói uma **visão relacional** que permita navegar o espaço de conhecimento como um território.

## Decisão

Criar `SPEC-054-EpistemicTopologyMapper.md` como nova camada que:
1. **Projeta** o vetor 92D do NoologicalScanner em coordenadas 2D/3D (UMAP/t-SNE)
2. **Identifica** estruturas topológicas: continentes, ilhas, pontes, zonas de vazio
3. **Calcula** métricas: Distância Epistemológica (DE), Índice de Isolamento (II), Buraco Epistemológico (BE), Potencial de Ponte (PP)
4. **Exporta** coordenadas para visualização externa (D3.js, Plotly, Power BI)

O espaço projetado preserva relações topológicas: proximidade = similaridade epistemológica.

## Consequências

**Positivas:**
- Permite visualização intuitiva do espaço de conhecimento
- Identifica oportunidades de conexão entre clusters distantes
- Quantifica "zonas de vazio" como prioridades de exploração
- Complementa o CognitiveDiversityScanner com validação geométrica

**Negativas:**
- Projeção 2D sempre perde informação (preservação topológica < 1.0)
- UMAP/t-SNE têm parâmetros que afetam o resultado (não-determinístico)
- Depende de quantidade mínima de artefatos para projeção significativa

## Dependências
- SPEC-028 (NoologicalScanner) — vetor 92D de cobertura
- SPEC-053 (CognitiveDiversityScanner) — validação cruzada de clusters

## Métricas Principais
- **Preservação Topológica**: ≥ 0.85 (mantém 85% das relações de vizinhança)
- **DE (Distância Epistemológica)**: normalizada [0, 1]
- **II (Índice de Isolamento)**: II > 0.8 = ilha
- **BE (Buraco Epistemológico)**: prioridade proporcional à área × (1 - densidade)
