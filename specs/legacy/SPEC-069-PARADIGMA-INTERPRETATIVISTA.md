# SPEC-069: Paradigma Interpretativista — Artefato de Conhecimento Epistêmico

**Status:** Active
**Versão:** 1.0.0
**Data:** 2026-07-02
**Categoria:** Paradigmas Epistemológicos
**Dimensão:** paradigmas
**Palavras-chave:** interpretativista, fenomenológico, qualitativo, subjetividade, hermenêutica

---

## 1. Problema

Paradigmas tem 25% de cobertura (2/8). O **Interpretativista** — focado na compreensão dos significados subjetivos e contextos sociais — está ausente.

## 2. Definição

Paradigma epistemológico que prioriza a compreensão (Verstehen) dos fenômenos sociais a partir da perspectiva dos atores, reconhecendo a natureza construída da realidade social e a subjetividade como dado legítimo.

## 3. Validação Cruzada

| Tipo | Regra | Peso |
|:-----|:------|:----:|
| enables | paradigmas.Interpretativista → metodos.Qualitativo fenomenológico | 0.90 |
| enables | paradigmas.Interpretativista → raciocinio.Abdutivo | 0.80 |
| co_occurs | paradigmas.Interpretativista ↔ dados.Dados qualitativos | 0.85 |
| requires | metodos.Pesquisa-ação → paradigmas.Interpretativista | 0.75 |

## 4. CTs

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SPEC-069 existe com campos obrigatórios | ✅ |
| CT-02 | Keywords incluem "interpretativista" e "fenomenológico" | ✅ |
| CT-03 | Skill paradigma-interpretativista registrada | ✅ |
| CT-04 | Regra enables para métodos qualitativos | ✅ |
