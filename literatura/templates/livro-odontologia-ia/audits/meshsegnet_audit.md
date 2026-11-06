# Auditoria GitHub — Tai-Hsien/MeshSegNet

> **Nível G2 (PROJETO 1):** Repositório com artigo, DOI, dataset ou benchmark

---

## Dados de Identificação

| Campo | Valor |
|-------|-------|
| **Nome:** | Tai-Hsien/MeshSegNet |
| **URL:** | https://github.com/Tai-Hsien/MeshSegNet |
| **Autores/mantenedores:** | Tai-Hsien Ouyang et al. (HKUST) |
| **Área odontológica:** | Escaneamento Intraoral 3D, Segmentação de Malhas |
| **Tarefa de IA:** | Segmentação de dentes em malhas 3D obtidas por scanner intraoral |

## Dados Técnicos

| Campo | Valor |
|-------|-------|
| **Tipo de dado:** | Malhas 3D (.obj, .ply) obtidas por scanner intraoral |
| **Linguagem:** | Python, PyTorch |
| **Framework:** | PyTorch3D, trimesh, visdom |

## Validação Científica

| Campo | Valor |
|-------|-------|
| **Artigo associado:** | Lian et al. (2020) "MeshSegNet: Deep Multi-Scale Mesh Feature Learning for Tooth Segmentation in 3D Intraoral Scans" |
| **DOI:** | 10.1109/TMI.2020.2971730 (IEEE Transactions on Medical Imaging) |
| **Licença do código:** | MIT License |
| **Licença dos dados:** | Não aplicável (depende de dataset privado do HKUST) |
| **Dataset aberto?** | ❌ Não — dados proprietários do HKUST |
| **Permite uso comercial?** | ✅ Sim (código MIT) |

## Reprodutibilidade

| Campo | Valor |
|-------|-------|
| **Possui requirements.txt / environment.yml?** | ✅ Sim — requirements.txt |
| **Possui notebook?** | ❌ Não — apenas scripts |
| **Possui testes?** | ❌ Não |
| **Executa no Colab?** | ⚠️ Parcial — requer GPU para treinamento |
| **Reproduz resultados do artigo?** | ✅ Sim (com dados próprios) |

## Riscos

| Campo | Valor |
|-------|-------|
| **Risco ético:** | ⚠️ Baixo |
| **Risco clínico:** | ⚠️ Baixo — escaneamento intraoral, dados não-identificáveis |

## Uso no Livro OdontoIA

- **Capítulo 8** (Segmentação 3D): uso como exemplo de arquitetura para malhas
- **Capítulo 17** (CaTGO gêmeo digital): uso para segmentação em IOS (escaneamento intraoral)

## Veredicto

**Status:** ✅ **APROVADO COM RESTRIÇÃO**

**Justificativa:** Arquitetura inovadora (MeshSegNet) publicada em IEEE TMI 2020, código MIT aberto, mas sem dados abertos (depende de dataset privado do HKUST). Para uso completo, é necessário coletar dados próprios.

**Restrição:** Para fins de pesquisa, é necessário coletar dados próprios de escaneamento intraoral.

---

**Auditor:** OpenCode Ecosystem
**Data:** 2026-07-09
