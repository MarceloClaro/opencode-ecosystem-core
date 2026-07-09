# ADR-001: Adoção de Plataformas Open-Source para Gêmeos Digitais Odontológicos

| Campo | Valor |
|-------|-------|
| **ID** | ADR-001 |
| **Data** | 2026-06-21 |
| **Status** | Aceito |
| **Autor** | Marcelo Claro Laranjeira |
| **Especificação** | SPEC-032 (Scanner Axiológico) |

## Contexto

O desenvolvimento de gêmeos digitais odontológicos requer um ecossistema de ferramentas para processamento de imagem (CBCT), modelagem geométrica (malhas 3D), simulação biomecânica (FEA) e visualização. Existem duas abordagens: software proprietário (custos elevados, caixa-preta) e plataformas open-source (transparentes, customizáveis).

## Decisão

Adotar exclusivamente plataformas open-source:

| Camada | Ferramenta | Função |
|--------|-----------|--------|
| Processamento de Imagem | 3D Slicer, ITK, OpenCV | Segmentação CBCT |
| Geometria Computacional | MeshLab, Blender | Limpeza e remeshing |
| Simulação Biomecânica | Calculix, FEniCS, OpenFOAM | FEA e CFD |
| Modelagem Neuromuscular | OpenSim | ATM e musculatura |
| Orquestração Multiagente | OpenCode Ecosystem | Pipeline completo |

## Consequências

**Positivas:**
- Custo zero de licenciamento
- Reprodutibilidade metodológica total
- Auditoria algorítmica transparente
- Comunidade ativa e atualizações frequentes

**Negativas:**
- Curva de aprendizado mais íngreme
- Integração entre ferramentas requer middleware

## Compliance

- ABNT NBR ISO/IEC 3173 (padronização de gêmeos digitais)
- RDC 657/2022 ANVISA (Software como Dispositivo Médico)
