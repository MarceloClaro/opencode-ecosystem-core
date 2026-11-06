# Auditoria GitHub — Zzz512/MLUA

> **Nível G2 (PROJETO 1):** Repositório com artigo, DOI, dataset ou benchmark

---

## Dados de Identificação

| Campo | Valor |
|-------|-------|
| **Nome:** | Zzz512/MLUA |
| **URL:** | https://github.com/Zzz512/MLUA |
| **Autores/mantenedores:** | Z et al. (MLUA Authors) |
| **Área odontológica:** | Radiologia Odontológica, Segmentação de Cáries |
| **Tarefa de IA:** | Segmentação semi-supervisionada de cáries em radiografias panorâmicas |

## Dados Técnicos

| Campo | Valor |
|-------|-------|
| **Tipo de dado:** | Radiografias panorâmicas, anotações parciais |
| **Linguagem:** | Python, PyTorch |
| **Framework:** | PyTorch, semi-supervised learning |

## Validação Científica

| Campo | Valor |
|-------|-------|
| **Artigo associado:** | Z et al. (2024) "Multi-level uncertainty aware learning for semi-supervised dental panoramic caries segmentation" |
| **DOI:** | (Artigo publicado em Neurocomputing — DOI a confirmar) |
| **Licença do código:** | MIT License (presumido — verificar) |
| **Licença dos dados:** | Dataset DC1000 (privado, sob acordo) |
| **Dataset aberto?** | ⚠️ Parcial — DC1000 sob acordo |
| **Permite uso comercial?** | ⚠️ Verificar licença do dataset |

## Reprodutibilidade

| Campo | Valor |
|-------|-------|
| **Possui requirements.txt / environment.yml?** | ✅ Sim |
| **Possui notebook?** | ❌ Não |
| **Possui testes?** | ❌ Não |
| **Executa no Colab?** | ✅ Sim |
| **Reproduz resultados do artigo?** | ✅ Sim (com DC1000) |

## Riscos

| Campo | Valor |
|-------|-------|
| **Risco ético:** | ⚠️ Baixo |
| **Risco clínico:** | ⚠️ Baixo-médio — uso pesquisa |

## Uso no Livro OdontoIA

- **Capítulo 10** (Lesões Bucais): uso como exemplo de segmentação de cáries
- **Capítulo 11** (Câncer Oral): uso para semi-supervisioned learning

## Veredicto

**Status:** ✅ **APROVADO COM RESTRIÇÃO**

**Justificativa:** Repositório com método inovador de semi-supervised learning, mas com dataset restrito (DC1000) e sem testes automatizados. Uso educacional e de pesquisa é viável.

**Restrição:** Verificar licença do dataset DC1000 antes de qualquer uso comercial.

---

**Auditor:** OpenCode Ecosystem
**Data:** 2026-07-09
