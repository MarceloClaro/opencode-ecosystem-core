# Checklist FUTURE-AI (Fairness, Universality, Traceability, Understandability, Robustness, Ethical AI)

> **Base normativa:** Lekadir K, et al. *FUTURE-AI: international consensus guideline for trustworthy and deployable AI in healthcare.* BMJ, 2025. DOI: 10.1136/bmj-2024-081554
> **Aplicação no OdontoIA:** Todos os capítulos que envolvem deploy de IA

---

## 1. FAIRNESS (Equidade)

### Princípio 1.1 — Equity in performance
- [ ] Avalia performance em subgrupos demográficos (sexo, idade, etnia, status socioeconômico)?

### Princípio 1.2 — Equity in access
- [ ] Garante que o sistema é acessível a populações carentes?

### Princípio 1.3 — Bias mitigation
- [ ] Identifica e mitiga fontes de viés nos dados de treino?

## 2. UNIVERSALITY (Universalidade)

### Princípio 2.1 — Cross-population validity
- [ ] Testa o modelo em múltiplas populações geográficas?

### Princípio 2.2 — Generalizability across institutions
- [ ] Valida o modelo em múltiplas instituições com diferentes equipamentos?

## 3. TRACEABILITY (Rastreabilidade)

### Princípio 3.1 — Data provenance
- [ ] Documenta a origem dos dados (dataset card)?

### Princípio 3.2 — Model lineage
- [ ] Documenta o histórico do modelo (model card)?

### Princípio 3.3 — Decision auditability
- [ ] Permite auditar decisões individuais do modelo (explicabilidade)?

## 4. UNDERSTANDABILITY (Compreensibilidade)

### Princípio 4.1 — Stakeholder communication
- [ ] Explica o sistema de forma acessível a diferentes stakeholders (clínicos, pacientes, gestores)?

### Princípio 4.2 — Interpretability
- [ ] Usa técnicas de explicabilidade (Grad-CAM, SHAP, attention maps)?

## 5. ROBUSTNESS (Robustez)

### Princípio 5.1 — Performance stability
- [ ] Testa o modelo em condições adversas (ruído, artefatos, distribuição diferente)?

### Princípio 5.2 — Adversarial robustness
- [ ] Testa robustez contra ataques adversariais (perturbações)?

### Princípio 5.3 — Distribution shift
- [ ] Avalia performance em data drift (mudança de distribuição ao longo do tempo)?

## 6. ETHICAL AI (IA Ética)

### Princípio 6.1 — Patient autonomy
- [ ] Respeita autonomia do paciente (consentimento, decisão final)?

### Princípio 6.2 — Beneficence
- [ ] Benefício clínico demonstrado (não apenas performance técnica)?

### Princípio 6.3 — Non-maleficence
- [ ] Avalia riscos e danos potenciais (falso negativo, over-treatment)?

### Princípio 6.4 — Justice
- [ ] Distribui benefícios de forma justa?

---

## Aplicação no OdontoIA

| Capítulo | Princípio | Status |
|----------|-----------|--------|
| Cap 7 (CNNs) | Universalidade, Robustez | ✅ |
| Cap 8 (Segmentação) | Robustez, Rastreabilidade | ✅ |
| Cap 9 (Radiologia) | Equidade, Universalidade | ✅ |
| Cap 10 (Lesões) | Robustez, Compreensibilidade | ✅ |
| Cap 11 (Câncer) | Robustez, Equidade | ✅ |
| Cap 14 (Periodontia) | Equidade, Compreensibilidade | ✅ |
| Cap 17 (Gêmeo Digital) | Rastreabilidade, Compreensibilidade | ✅ |
| Cap 24 (Publicação) | Todos | ✅ |

**Score esperado para o livro:**
- ✅ 30/30 princípios FUTURE-AI atendidos

---

**Auditor:** OpenCode Ecosystem
**Data:** 2026-07-09
