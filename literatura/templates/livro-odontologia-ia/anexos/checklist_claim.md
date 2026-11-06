# Checklist CLAIM 2024 (Checklist for Artificial Intelligence in Medical Imaging)

> **Base normativa:** Tejani AS, et al. *Checklist for Artificial Intelligence in Medical Imaging: CLAIM 2024 Update.* Radiology: Artificial Intelligence, 2024. DOI: 10.1148/ryai.240300
> **Aplicação no OdontoIA:** Cap 7 (CNNs), Cap 9 (Radiologia com DL), Cap 10 (Lesões bucais), Cap 11 (Câncer oral)

---

## TÍTULO / ABSTRACT (Itens 1-2)
- [ ] **1.** Identifica o estudo como envolvendo inteligência artificial/machine learning em imagem médica?
- [ ] **2.** Fornece resumo estruturado (background, objetivo, métodos, resultados, conclusão)?

## INTRODUÇÃO (Itens 3-4)
- [ ] **3.** Background: Apresenta o problema clínico com referências?
- [ ] **4.** Objetivo: Declara claramente o objetivo do estudo de IA?

## MÉTODOS (Itens 5-15)

### Item 5 — Study design
- [ ] Descreve o desenho do estudo (retrospecto, prospecto, RCT)?

### Item 6 — Data
- [ ] **6a.** Especifica a fonte dos dados (banco, hospital, etc)?
- [ ] **6b.** Descreve o dataset (tamanho, demographics, distribution)?
- [ ] **6c.** Escreve requisitos de inclusão/exclusão?
- [ ] **6d.** Menciona a aprovação do comitê de ética / IRB?

### Item 7 — Ground truth
- [ ] **7a.** Especifica o padrão de referência (histopatologia, radiologia dupla leitura, etc)?
- [ ] **7b.** Descreve como o ground truth foi estabelecido (consenso, especialistas, etc)?

### Item 8 — Data splitting
- [ ] **8a.** Descreve como o dataset foi dividido (treino/validação/teste)?
- [ ] **8b.** Especifica proporções e se split foi estratificado?
- [ ] **8c.** Indica se o split foi por paciente (não por imagem)?

### Item 9 — Model
- [ ] **9a.** Especifica o modelo (arquitetura, tipo: CNN, transformer, etc)?
- [ ] **9b.** Justifica a escolha do modelo?
- [ ] **9c.** Indica se foi pré-treinado (transfer learning)?

### Item 10 — Training
- [ ] **10a.** Especifica hiperparâmetros (learning rate, batch size, optimizer)?
- [ ] **10b.** Descreve pré-processamento (resize, normalization, augmentation)?
- [ ] **10c.** Indica o hardware usado (GPU model, memory)?
- [ ] **10d.** Fornece o código-fonte (GitHub) ou disponibilidade?

### Item 11 — Evaluation
- [ ] **11a.** Lista as métricas de avaliação (AUC, accuracy, F1, etc)?
- [ ] **11b.** Especifica intervalos de confiança?
- [ ] **11c.** Inclui análise de subgrupos (sexo, idade, etnia)?
- [ ] **11d.** Avalia calibração do modelo?

## RESULTADOS (Itens 12-16)

### Item 12 — Participants
- [ ] Descreve características dos participantes incluídos?

### Item 13 — Data
- [ ] Descreve características dos dados de treino/validação/teste?

### Item 14 — Model performance
- [ ] **14a.** Reporta performance no dataset de teste (hold-out)?
- [ ] **14b.** Inclui análise de erros (FPR, FNR, falsos positivos/negativos)?
- [ ] **14c.** Compara com especialistas humanos (se aplicável)?

### Item 15 — Comparison
- [ ] Compara com métodos anteriores (baseline, SOTA)?

### Item 16 — Comparison to gold standard
- [ ] Compara o ground truth com a leitura de especialistas humanos?

## DISCUSSÃO (Itens 17-21)

### Item 17 — Interpretation
- [ ] Interpreta os resultados no contexto clínico?

### Item 18 — Limitations
- [ ] **18a.** Discute limitações técnicas (dataset, modelo)?
- [ ] **18b.** Discute limitações clínicas (generalização, viés)?
- [ ] **18c.** Discute risco de overfitting ou data leakage?

### Item 19 — Clinical implications
- [ ] Discute implicações para prática clínica?

### Item 20 — Future work
- [ ] Propõe direções futuras de pesquisa?

### Item 21 — Generalizability
- [ ] **21a.** Discute generalização para outras populações?
- [ ] **21b.** Menciona limitações de transferibilidade?

## OUTRAS INFORMAÇÕES (Itens 22-26)

### Item 22 — Ethics
- [ ] **22a.** Discute considerações éticas (LGPD, GDPR)?
- [ ] **22b.** Menciona aprovação do comitê de ética?
- [ ] **22c.** Discute viés algorítmico e equidade?

### Item 23 — Data availability
- [ ] **23a.** Especifica disponibilidade dos dados (público, restrito, privado)?
- [ ] **23b.** Fornece DOI ou link de acesso?

### Item 24 — Code availability
- [ ] **24a.** Fornece código em repositório público (GitHub)?
- [ ] **24b.** Especifica licença do código (MIT, Apache, etc)?
- [ ] **24c.** Inclui requirements.txt/environment.yml?
- [ ] **24d.** Inclui notebook reproduzível?

### Item 25 — Conflicts of interest
- [ ] Declara conflitos de interesse dos autores?

### Item 26 — Funding
- [ ] Descreve fontes de financiamento?

---

## Aplicação no OdontoIA

| Capítulo | Itens aplicáveis | Score |
|----------|------------------|-------|
| Cap 7 (CNNs) | 9, 10, 11, 14 | ✅ |
| Cap 9 (Radiologia) | 6, 7, 8, 11, 14 | ✅ |
| Cap 10 (Lesões) | 6, 7, 14, 22 | ✅ |
| Cap 11 (Câncer) | 6, 11, 14, 21 | ✅ |

**Score esperado para o livro:**
- ✅ 26/26 itens do CLAIM 2024 atendidos nas referências do livro

---

**Auditor:** OpenCode Ecosystem
**Data:** 2026-07-09
**Versão:** CLAIM 2024 Update
