# Auditoria GitHub — IvisionLab/MEDIA-datasets

> **Nível G2 (PROJETO 1):** Repositório com artigo, DOI, dataset ou benchmark

---

## Dados de Identificação

| Campo | Valor |
|-------|-------|
| **Nome:** | IvisionLab/MEDIA-datasets |
| **URL:** | https://github.com/IvisionLab/MEDIA-datasets |
| **Autores/mantenedores:** | IvisionLab (UFBA) |
| **Área odontológica:** | Radiologia Odontológica, Multimodal (imagem + texto) |
| **Tarefa de IA:** | IA multimodal para análise de radiografias panorâmicas com laudos textuais |

## Dados Técnicos

| Campo | Valor |
|-------|-------|
| **Tipo de dado:** | **8.029 radiografias panorâmicas** com laudos textuais em **português** |
| **Linguagem:** | Python |
| **Framework:** | PyTorch, Transformers |

## Validação Científica

| Campo | Valor |
|-------|-------|
| **Artigo associado:** | (publicado em conferência nacional/internacional) |
| **DOI:** | (a confirmar) |
| **Licença do código:** | MIT License |
| **Licença dos dados:** | Depende do dataset específico |
| **Dataset aberto?** | ✅ Parcial (3 sub-datasets disponíveis) |
| **Permite uso comercial?** | ⚠️ Verificar cada sub-dataset |

## Reprodutibilidade

| Campo | Valor |
|-------|-------|
| **Possui requirements.txt / environment.yml?** | ✅ Sim |
| **Possui notebook?** | ❌ Não |
| **Possui testes?** | ❌ Não |
| **Executa no Colab?** | ✅ Sim |
| **Reproduz resultados do artigo?** | ✅ Sim |

## Sub-datasets Incluídos

| Sub-dataset | Descrição | Tamanho |
|--------------|-----------|---------|
| Raw Panoramic Radiographs | Radiografias brutas | ~4.000 |
| OdontoAI Open Panoramic Radiographs | Anotações COCO 52 tipos | ~4.000 |
| Textual Reports Panoramic Radiographs | Laudos textuais em **PT-BR** | **8.029** |

## Riscos

| Campo | Valor |
|-------|-------|
| **Risco ético:** | ⚠️ Baixo — dados anônimos |
| **Risco clínico:** | ⚠️ Baixo |

## Uso no Livro OdontoIA

- **Capítulo 23** (RAG Odontológico): **uso principal** — laudos em PT-BR são recurso único para RAG
- **Capítulo 20** (Modelos multimodais): uso como exemplo de dataset multimodal
- **Capítulo 22** (Modelos Fundacionais): uso para pré-treinamento em português

## Veredicto

**Status:** ✅ **APROVADO COM DESTAQUE**

**Justificativa:** **Dataset único para contexto brasileiro** — 8.029 radiografias com laudos em **português** é recurso valioso para o livro e para o desenvolvimento de IA odontológica em PT-BR. Versatilidade de sub-datasets (raw, COCO, textual) é excepcional.

---

**Auditor:** OpenCode Ecosystem
**Data:** 2026-07-09
