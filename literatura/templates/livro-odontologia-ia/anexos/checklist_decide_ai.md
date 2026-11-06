# Checklist DECIDE-AI (Decision-making in healthcare with artificial intelligence)

> **Base normativa:** Vasey B, et al. *DECIDE-AI: new reporting guidelines to bridge between development and implementation.* Nature Medicine, 2022. DOI: 10.1038/s41591-022-01772-9
> **Aplicação no OdontoIA:** Cap 24 (Publicação científica) e validação clínica de qualquer sistema de IA

---

## PRIMEIRA GERAÇÃO (Desenvolvimento) — 5 itens

### Item 1 — Clinical problem and population
- [ ] **1a.** Identifica claramente o problema clínico?
- [ ] **1b.** Define a população-alvo (incluindo subgrupos)?

### Item 2 — Decision-making and implementation
- [ ] **2a.** Descreve a decisão clínica que o sistema apoia?
- [ ] **2b.** Identifica o setting (primário/secundário, etc)?

### Item 3 — Data and outcomes
- [ ] **3a.** Descreve as fontes de dados (treino, validação, teste)?
- [ ] **3b.** Define o desfecho (gold standard, tempo de seguimento)?

### Item 4 — Model development and validation
- [ ] **4a.** Descreve o modelo (arquitetura, parâmetros)?
- [ ] **4b.** Descreve a validação (split, cross-validation, externa)?
- [ ] **4c.** Reporta métricas de discriminação, calibração e utilidade clínica?

### Item 5 — Model performance
- [ ] **5a.** Compara com referência (baseline, especialistas humanos)?

## SEGUNDA GERAÇÃO (Implementação) — 13 itens

### Item 6 — Real-world use
- [ ] **6a.** Descreve o uso clínico real (workflow, usuários)?
- [ ] **6b.** Indica se é usado em triagem, diagnóstico, prognóstico?

### Item 7 — Setting and infrastructure
- [ ] **7a.** Descreve infraestrutura técnica (hardware, integração EHR)?

### Item 8 — Workflow integration
- [ ] **8a.** Mostra como o sistema se integra ao workflow clínico?

### Item 9 — Human factors
- [ ] **9a.** Descreve fatores humanos (treinamento, UI, fadiga de alerta)?

### Item 10 — Clinical safety
- [ ] **10a.** Descreve estratégia de segurança (fail-safe, override humano)?

### Item 11 — Reporting outcomes
- [ ] **11a.** Reporta desfechos clínicos após implementação?
- [ ] **11b.** Inclui desfechos negativos (erros, eventos adversos)?

### Item 12 — Ethics
- [ ] **12a.** Aprovação ética obtida?
- [ ] **12b.** Consentimento informado atualizado?

### Item 13 — Equity
- [ ] **13a.** Avalia performance em subgrupos demográficos?
- [ ] **13b.** Identifica riscos de viés algorítmico?

### Item 14 — Regulatory
- [ ] **14a.** Indica aprovação regulatória (ANVISA, FDA, CE)?

### Item 15 — Sustainability
- [ ] **15a.** Descreve plano de manutenção e atualização?

### Item 16 — Patient involvement
- [ ] **16a.** Pacientes foram envolvidos no desenvolvimento?

### Item 17 — Reimbursement
- [ ] **17a.** Descreve modelo de reembolso?

### Item 18 — Public engagement
- [ ] **18a.** Descreve comunicação com o público?

---

## Aplicação no OdontoIA

| Capítulo | Sistema | Geração |
|---------|---------|---------|
| Cap 7 (CNNs) | CNN para cárie | 1ª |
| Cap 8 (Segmentação) | U-Net para dentes | 1ª |
| Cap 9 (Radiologia) | Sistema CAD odontológico | 1ª + 2ª |
| Cap 14 (Periodontia) | Predição de risco | 1ª + 2ª |

**Score esperado para o livro:**
- ✅ 5/5 itens 1ª geração
- ✅ 13/13 itens 2ª geração
- **Total: 18/18** ✅

---

**Auditor:** OpenCode Ecosystem
**Data:** 2026-07-09
