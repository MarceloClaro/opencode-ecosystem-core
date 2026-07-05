# SPEC-068: Paradigma Positivista — Artefato de Conhecimento Epistêmico

**Status:** Active
**Versão:** 1.0.0
**Data:** 2026-07-02
**Categoria:** Paradigmas Epistemológicos
**Dimensão:** paradigmas
**Palavras-chave:** positivista, empirismo, quantitativo, experimental, falseabilidade

---

## 1. Problema

Paradigmas tem 25% de cobertura (2/8). O **Positivista** — base do método científico clássico com hipóteses falseáveis, experimentos controlados e generalização estatística — está ausente.

## 2. Definição

Paradigma epistemológico que postula a existência de uma realidade objetiva e mensurável, priorizando dados empíricos, replicabilidade e falseabilidade de hipóteses via método hipotético-dedutivo.

## 3. Validação Cruzada

| Tipo | Regra | Peso |
|:-----|:------|:----:|
| enables | paradigmas.Positivista → metodos.Quantitativo experimental | 0.90 |
| enables | paradigmas.Positivista → raciocinio.Dedutivo | 0.85 |
| co_occurs | paradigmas.Positivista ↔ dados.Dados epidemiológicos | 0.80 |
| requires | metodos.Meta-análise → paradigmas.Positivista | 0.70 |

## 4. CTs

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SPEC-068 existe com campos obrigatórios | ✅ |
| CT-02 | Keywords incluem "positivista" e "falseabilidade" | ✅ |
| CT-03 | Skill paradigma-positivista registrada | ✅ |
| CT-04 | Regra enables para métodos quantitativos | ✅ |
