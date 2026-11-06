# Auditoria GitHub — MIC-DKFZ/ToothSeg

> **Nível G2 (PROJETO 1):** Repositório com artigo, DOI, dataset ou benchmark

---

## Dados de Identificação

| Campo | Valor |
|-------|-------|
| **Nome:** | MIC-DKFZ/ToothSeg |
| **URL:** | https://github.com/MIC-DKFZ/ToothSeg |
| **Autores/mantenedores:** | DKFZ (German Cancer Research Center), Medical Imaging Computing |
| **Área odontológica:** | Segmentação 3D em CBCT, Numeração Dentária |
| **Tarefa de IA:** | Segmentação 3D de dentes individuais em CBCT, com autocorreção |

## Dados Técnicos

| Campo | Valor |
|-------|-------|
| **Tipo de dado:** | Volumes 3D CBCT, anotações voxel-wise |
| **Linguagem:** | Python |
| **Framework:** | nnU-Net, PyTorch, MONAI |

## Validação Científica

| Campo | Valor |
|-------|-------|
| **Artigo associado:** | Said et al. (2025) "ToothSeg: A Self-Supervised Deep Learning Framework for Tooth Segmentation in CBCT" |
| **DOI:** | 10.1109/JBHI.2025.3650444 (IEEE Journal of Biomedical and Health Informatics) |
| **Licença do código:** | Apache-2.0 |
| **Licença dos dados:** | Não aplicável (usa datasets públicos como ToothFairy) |
| **Dataset aberto?** | ✅ Sim — depende do dataset ToothFairy |
| **Permite uso comercial?** | ✅ Sim (código Apache-2.0) |

## Reprodutibilidade

| Campo | Valor |
|-------|-------|
| **Possui requirements.txt / environment.yml?** | ✅ Sim — setup completo |
| **Possui notebook?** | ❌ Não — apenas scripts Python |
| **Possui testes?** | ⚠️ Parcial — unit tests internos |
| **Executa no Colab?** | ⚠️ Parcial — requer GPU |
| **Reproduz resultados do artigo?** | ✅ Sim — métricas reportadas |

## Riscos

| Campo | Valor |
|-------|-------|
| **Risco ético:** | ⚠️ Baixo — CBCT anonimizados |
| **Risco clínico:** | ⚠️ Baixo — uso pesquisa |

## Uso no Livro OdontoIA

- **Capítulo 8** (Segmentação Dentária): uso principal para CBCT 3D
- **Capítulo 17** (CaTGO gêmeo digital): uso como base para gêmeo digital periodontal

## Veredicto

**Status:** ✅ **APROVADO**

**Justificativa:** Repositório de altíssima qualidade do DKFZ (centro de pesquisa de classe mundial), código aberto (Apache-2.0), autocorreção inovadora, base científica sólida. Sem testes automatizados externos, mas código bem documentado.

---

**Auditor:** OpenCode Ecosystem
**Data:** 2026-07-09
