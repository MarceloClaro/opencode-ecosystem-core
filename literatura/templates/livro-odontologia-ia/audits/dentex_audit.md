# Auditoria GitHub — ibrahimethemhamamci/DENTEX

> **Nível G2 (PROJETO 1):** Repositório com artigo, DOI, dataset ou benchmark

---

## Dados de Identificação

| Campo | Valor |
|-------|-------|
| **Nome:** | ibrahimethemhamamci/DENTEX |
| **URL:** | https://github.com/ibrahimethemhamamci/DENTEX |
| **Autores/mantenedores:** | Ibrahim Ethem Hamamci (ETH Zurich) et al. |
| **Área odontológica:** | Radiologia Odontológica, Detecção Dentária, Diagnóstico |
| **Tarefa de IA:** | Detecção de dentes anormais, enumeração dentária (FDI), diagnóstico (cárie, cárie profunda, lesão periapical, dente impactado) |

## Dados Técnicos

| Campo | Valor |
|-------|-------|
| **Tipo de dado:** | Radiografias panorâmicas, anotações multi-nível (quadrante, quadrante+enumeração, quadrante+enumeração+diagnóstico) |
| **Linguagem:** | Python |
| **Framework:** | PyTorch, nnDetection, nnU-Net |

## Validação Científica

| Campo | Valor |
|-------|-------|
| **Artigo associado:** | Hamamci et al. (2024) "DENTEX: An Automated Detection Pipeline for Dental Diseases and Anomalies" |
| **DOI:** | 10.1109/ISBI60581.2024.10586618 (ISBI 2024) |
| **Licença do código:** | MIT License |
| **Licença dos dados:** | CC BY-NC-SA 4.0 |
| **Dataset aberto?** | ✅ Sim — disponível no Hugging Face |
| **Permite uso comercial?** | ❌ Não (dados sob CC BY-NC-SA 4.0) |

## Reprodutibilidade

| Campo | Valor |
|-------|-------|
| **Possui requirements.txt / environment.yml?** | ✅ Sim — instructions claras |
| **Possui notebook?** | ✅ Sim — notebooks Jupyter |
| **Possui testes?** | ❌ Não — sem testes automatizados |
| **Executa no Colab?** | ✅ Sim — instruções específicas |
| **Reproduz resultados do artigo?** | ✅ Sim — métricas no README |

## Riscos

| Campo | Valor |
|-------|-------|
| **Risco ético:** | ⚠️ Baixo — dados anônimos, aprovação ética obtida |
| **Risco clínico:** | ⚠️ Baixo-médio — uso pesquisa, não clínico direto |

## Uso no Livro OdontoIA

- **Capítulo 9** (Radiologia com DL): uso principal como benchmark
- **Capítulo 10** (Lesões Bucais): uso para detecção de cáries
- **Capítulo 11** (Câncer Oral): uso para detecção de lesões malignas

## Veredicto

**Status:** ✅ **APROVADO COM RESTRIÇÃO**

**Justificativa:** Benchmark MICCAI 2024 de altíssima qualidade, código limpo, três níveis de anotação (quadrante, quadrante+enumeração, quadrante+enumeração+diagnóstico). Sem testes automatizados no repo, mas com notebooks completos. A restrição é a licença não-comercial dos dados.

**Restrição:** Em uso comercial, citar CC BY-NC-SA 4.0 e considerar licença separada para dados.

---

**Auditor:** OpenCode Ecosystem
**Data:** 2026-07-09
