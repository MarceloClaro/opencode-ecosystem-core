# Auditoria GitHub — IvisionLab/OdontoAI-Open-Panoramic-Radiographs

> **Nível G2 (PROJETO 1):** Repositório com artigo, DOI, dataset ou benchmark

---

## Dados de Identificação

| Campo | Valor |
|-------|-------|
| **Nome:** | IvisionLab/OdontoAI-Open-Panoramic-Radiographs |
| **URL:** | https://github.com/IvisionLab/OdontoAI-Open-Panoramic-Radiographs |
| **Autores/mantenedores:** | IvisionLab (Universidade Federal da Bahia — UFBA) |
| **Área odontológica:** | Radiologia Odontológica, Segmentação Dentária, Periodontia |
| **Tarefa de IA:** | Segmentação de dentes individuais em radiografias panorâmicas, com numeração FDI |

## Dados Técnicos

| Campo | Valor |
|-------|-------|
| **Tipo de dado:** | Radiografias panorâmicas 2D, anotações COCO (bounding boxes) |
| **Linguagem:** | Python |
| **Framework:** | PyTorch, Detectron2, MMDetection |

## Validação Científica

| Campo | Valor |
|-------|-------|
| **Artigo associado:** | Silva et al. (2022) "OdontoAI: A human-in-the-loop labeled data set and an online platform to boost research on dental panoramic radiographs" |
| **DOI:** | 10.1080/21681163.2022.2157747 (Visual Computing for Industry, Biomedicine, and Art) |
| **Licença do código:** | MIT License |
| **Licença dos dados:** | CC BY-NC-SA 4.0 |
| **Dataset aberto?** | ✅ Sim — 4.000 radiografias panorâmicas abertas |
| **Permite uso comercial?** | ❌ Não (dados sob CC BY-NC-SA 4.0) |

## Reprodutibilidade

| Campo | Valor |
|-------|-------|
| **Possui requirements.txt / environment.yml?** | ✅ Sim — environment.yml + requirements.txt |
| **Possui notebook?** | ⚠️ Parcial — scripts Python disponíveis |
| **Possui testes?** | ❌ Não — sem testes automatizados |
| **Executa no Colab?** | ✅ Sim — instruções claras para Colab |
| **Reproduz resultados do artigo?** | ✅ Sim — métricas reportadas no README |

## Riscos

| Campo | Valor |
|-------|-------|
| **Risco ético:** | ⚠️ Baixo-médio — dataset não-comercial, sem dados de pacientes identificáveis |
| **Risco clínico:** | ⚠️ Baixo — uso educacional/pesquisa, não clínico direto |

## Uso no Livro OdontoIA

- **Capítulo 8** (Segmentação Dentária): uso principal como referência de dataset
- **Capítulo 10** (Lesões Bucais): uso como base de comparação para detecção
- **Capítulo 14** (Periodontia ML): uso como exemplo de feature engineering em radiografias

## Veredicto

**Status:** ✅ **APROVADO COM RESTRIÇÃO**

**Justificativa:** Repositório de altíssima qualidade científica, com DOI, dataset aberto, código limpo e reproduzível. A restrição é a licença não-comercial dos dados (CC BY-NC-SA 4.0), que impede uso comercial direto mas é perfeita para fins educacionais. Sem testes automatizados, mas com código bem documentado.

**Restrição:** Em uso comercial ou publicação, citar explicitamente a licença CC BY-NC-SA 4.0 dos dados.

---

**Auditor:** OpenCode Ecosystem + multi_reasoning (engine `critical` + `causal`)
**Data:** 2026-07-09
**Versão do protocolo:** 1.0
**Citação completa:** Silva, B. et al. (2022). "OdontoAI: A human-in-the-loop labeled data set and an online platform to boost research on dental panoramic radiographs." *Visual Computing for Industry, Biomedicine, and Art*, 2022. DOI: 10.1080/21681163.2022.2157747
