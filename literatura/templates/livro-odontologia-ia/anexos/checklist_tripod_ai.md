# Checklist TRIPOD+AI (Transparent Reporting of a multivariable prediction model for Individual Prognosis Or Diagnosis — AI extension)

> **Base normativa:** Collins GS, et al. *TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods.* BMJ 2024. DOI: 10.1136/bmj-2023-078378
> **Aplicação no OdontoIA:** Cap 14 (Periodontia), Cap 16 (Periodontia), Cap 24 (Publicação)

---

## TÍTULO / ABSTRACT (Itens 1-2)
- [ ] **1.** Identifica o estudo como desenvolvimento e/ou validação de modelo preditivo?
- [ ] **2.** Fornece resumo estruturado (objetivo, desenho, setting, participantes, desfecho, análise estatística, resultados, conclusões)?

## INTRODUÇÃO (Itens 3a-3b)
- [ ] **3a.** Explica o contexto clínico e a necessidade do modelo?
- [ ] **3b.** Especifica o objetivo (desenvolvimento, validação ou ambos)?

## MÉTODOS (Itens 4-12)

### Item 4 — Source of data
- [ ] **4a.** Descreve a fonte dos dados (banco, registro, ensaio clínico)?
- [ ] **4b.** Especifica datas de início e fim do estudo?
- [ ] **4c.** Detalha o setting (primário/secundário, ambulatório/hospitalar)?

### Item 5 — Participants
- [ ] **5a.** Especifica critérios de elegibilidade (inclusão/exclusão)?
- [ ] **5b.** Descreve o tratamento dado a missing data?

### Item 6 — Outcome
- [ ] **6a.** Define claramente o desfecho primário?
- [ ] **6b.** Explica como e quando foi medido?

### Item 7 — Predictors
- [ ] **7a.** Lista todas as variáveis preditoras usadas?
- [ ] **7b.** Indica quando foram medidas em relação ao desfecho?

### Item 8 — Sample size
- [ ] **8a.** Justifica o tamanho amostral?
- [ ] **8b.** Indica como eventos por variável (EPV) foram calculados?

### Item 9 — Missing data
- [ ] **9a.** Descreve o tratamento de missing data (imputação, exclusão)?

### Item 10 — Statistical analysis — DEVELOPMENT
- [ ] **10a.** Especifica como as variáveis preditoras foram tratadas (categóricas, contínuas)?
- [ ] **10b.** Indica o tipo de modelo (regressão logística, random forest, rede neural)?
- [ ] **10c.** Descreve a seleção de variáveis?
- [ ] **10d.** Descreve o tratamento de overfitting (regularização, validação cruzada)?
- [ ] **10e.** Especifica o software usado?

### Item 11 — Statistical analysis — VALIDATION
- [ ] **11a.** Para validação: tipo (interna, externa, temporal, geográfica)?
- [ ] **11b.** Descreve as métricas de discriminação (AUC, sensibilidade, especificidade)?
- [ ] **11c.** Descreve as métricas de calibração (Hosmer-Lemeshow, calibration plot)?
- [ ] **11d.** Descreve métricas de decisão clínica (NRI, IDI)?

### Item 12 — Model presentation
- [ ] **12a.** Apresenta o modelo completo (equação, coeficientes)?
- [ ] **12b.** Para ML: apresenta importância das variáveis (SHAP, permutation importance)?

## RESULTADOS (Itens 13-17)

### Item 13 — Participants
- [ ] **13a.** Descreve o fluxo de participantes (excluídos, incluídos)?

### Item 14 — Model development
- [ ] **14a.** Apresenta o número de eventos e preditores?
- [ ] **14b.** Para desenvolvimento: apresenta discriminação e calibração no dataset de treino/validação?

### Item 15 — Model specification
- [ ] **15a.** Apresenta o modelo final (equação, fórmula)?

### Item 16 — Model performance
- [ ] **16a.** Apresenta performance com intervalos de confiança?
- [ ] **16b.** Compara modelos (simples vs complexo)?

### Item 17 — Model updating
- [ ] **17a.** Se aplicável: descreve como o modelo foi atualizado/reciclado?

## DISCUSSÃO (Itens 18-20)
- [ ] **18.** Interpreta os resultados no contexto clínico?
- [ ] **19.** Discute limitações (generalização, viés)?
- [ ] **20.** Discute implicações para prática clínica?

## OUTRAS INFORMAÇÕES (Itens 21-27)
- [ ] **21.** Fornece informações suplementares?
- [ ] **22.** Declara financiamento?
- [ ] **23.** Declara conflitos de interesse?
- [ ] **24.** Descreve disponibilidade do código?
- [ ] **25.** Descreve disponibilidade dos dados?
- [ ] **26.** Descreve aprovisionamento ético?
- [ ] **27.** Discute impacto em populações sub-representadas (equidade)?

---

## Aplicação no OdontoIA

| Capítulo | Modelo preditivo | Itens aplicáveis |
|----------|------------------|------------------|
| Cap 14 (Periodontia ML) | Risco periodontal | 4-12, 14, 16 |
| Cap 16 (Periodontia) | Predição progressão | 4-12, 14, 16 |
| Cap 24 (Publicação) | Checklist geral | Todos |

**Score esperado para o livro:**
- ✅ 27/27 itens do TRIPOD+AI atendidos

---

**Auditor:** OpenCode Ecosystem
**Data:** 2026-07-09
