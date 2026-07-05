# SPEC-067: Neurociências — Domínio de Conhecimento Cruzado

**Status:** Active
**Versão:** 1.0.0
**Data:** 2026-07-02
**Categoria:** Domínios de Conhecimento Cruzados
**Dimensão:** dominios
**Palavras-chave:** neurociências, cérebro, neural, cognitivo, fMRI, EEG

---

## 1. Problema

Domínios Cruzados tem apenas 10% de cobertura (1/10). Neurociências é o domínio com maior potencial de impacto (EPS 62.8) e habilita `dados.Dados neurobiológicos`.

## 2. Definição

Domínio interdisciplinar que estuda o sistema nervoso, incluindo neurociência cognitiva, computacional, clínica e molecular.

## 3. CTs

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SPEC-067 existe com definição do domínio | ✅ |
| CT-02 | Regra enables para dados neurobiológicos | ✅ |
| CT-03 | Palavras-chave incluem neurociência e fMRI | ✅ |

## 4. Integração

- `dominios.Neurociências` → enables → `dados.Dados neurobiológicos`
- `dominios.Neurociências` → co_occurs → `niveis_analise.Neurobiológico`
- `dominios.Psicofarmacologia` → requires → `dominios.Neurociências`
