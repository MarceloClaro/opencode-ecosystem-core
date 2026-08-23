---
spec_id: SPEC-935-R446
title: Motor de Decisão Clínica por Grafos Bayesianos, Teoria dos Jogos e Ancoragem em Evidências Reais
component: integrations/medical, marceloclaro/orchestrator, marceloclaro/cli, doctor
status: green
round_id: R446
test_file: tests/test_r446_clinical_game_theory_graphs.py
---

# SPEC-935-R446: Motor de Decisão Clínica por Grafos Bayesianos, Teoria dos Jogos e Ancoragem em Evidências Reais

## 1. Metadados e Controle
- **ID da Especificação:** `SPEC-935-R446`
- **Ciclo de Evolução:** `R446` (Ciclo 264)
- **Status:** `GREEN` (Validado com TDD)
- **Data:** 2026-08-23
- **Autor:** Marcelo Claro & DeepMind Agentic Pair
- **Score:** 10.0 / 100
- **Testes Associados:** `tests/test_r446_clinical_game_theory_graphs.py`

---

## 2. Visão Geral e Motivação
A tomada de decisão médica lida fundamentalmente com **incerteza probabilística**, **recursos limitados** e **assimetria de risco** (onde o custo de não diagnosticar uma doença fatal é incomensuravelmente maior do que o custo de solicitar um exame confirmatório).

Esta especificação implementa no OpenCode Ecosystem Core um motor neuro-simbólico de **Investigação Clínica Avançada** combinando:
1. **Grafos de Decisão Bayesiana & Árvores Diagnósticas:** Modelagem de probabilidades pré-teste, razões de verossimilhança (*Likelihood Ratios* LR+/LR-) e pós-teste via nomograma de Fagan.
2. **Seleção Ótima de Exames por Entropia de Shannon:** Escolha do teste com maior Ganho de Informação ($IG$) que maximize a redução de incerteza diagnóstica com menor invasividade.
3. **Teoria dos Jogos (Médico vs. Natureza) & Minimax Regret:** Matrizes de Payoff que consideram sensibilidade, especificidade, tempo, custos e penalidade crítica de omissão (*Critical Miss Penalty*), aplicando o critério Minimax Regret de Savage (1951) para blindar doenças graves que não podem ser perdidas.
4. **Anamnese Guiada por Redução de Entropia:** Geração dinâmica de questionários de anamnese priorizados pelo poder discriminatório das perguntas.
5. **Verificação Lógica de Segurança via Z3 SMT Solver:** Checagem determinística de contraindicações biológicas, interações medicamentosas e regras de segurança clínica.
6. **Ancoragem em Literatura Médica Real:** Toda hipótese, teste e conduta é obrigatoriamente associada a diretrizes de consenso e artigos médicos reais (*PubMed, SciELO, The Lancet, NEJM, AHA/ACC, ESC, EULAR, KDIGO, GOLD, GINA*), com nível de evidência **GRADE / Oxford CEBM** e DOI verificável.

---

## 3. Arquitetura dos Módulos

```
integrations/medical/
├── __init__.py                      # Exportações canônicas
├── evidence_grounding.py            # Base de literatura médica real e RAG biomédico
├── clinical_game_theory.py          # Grafos de decisão, Shannon Entropy, Payoff Matrix & Minimax Regret
├── clinical_verifier.py             # Verificador de contraindicações e interações via Z3 SMT Solver
└── clinical_orchestrator_bridge.py  # Pipeline unificado e gerador de YAML resposta_medico_virtual_supremo
```

---

## 4. Formulação Matemática

### 4.1 Teorema de Bayes e Razão de Verossimilhança (LR)
$$\text{Odds}_{\text{pós-teste}} = \text{Odds}_{\text{pré-teste}} \times \text{LR}$$
$$P(D \mid T^+) = \frac{\text{Odds}_{\text{pós-teste}}}{1 + \text{Odds}_{\text{pós-teste}}}$$

### 4.2 Ganho de Informação de Shannon
$$H(D) = -\sum_{i=1}^n P(d_i) \log_2 P(d_i)$$
$$IG(T) = H(D) - \sum_{r \in \{+, -\}} P(T=r) H(D \mid T=r)$$

### 4.3 Matriz de Payoff e Critério Minimax Regret
Para a hipótese $d_i$ e conduta/exame $a_j$:
$$\text{Regret}(d_i, a_j) = \max_{k} \text{Payoff}(d_i, a_k) - \text{Payoff}(d_i, a_j)$$
$$a^* = \arg\min_{a_j} \max_{d_i} \text{Regret}(d_i, a_j)$$

---

## 5. Critérios de Aceitação e Testes
1. `test_bayesian_graph_probability_update`: Atualização exata de probabilidades pré para pós-teste.
2. `test_shannon_entropy_information_gain`: Escolha ótima do exame com maior $IG$.
3. `test_minimax_regret_prevents_critical_miss`: Priorização da investigação de doença grave mesmo com baixa probabilidade inicial.
4. `test_anamnesis_generation`: Estruturação de queixa principal, HDA, fatores de risco e perguntas priorizadas.
5. `test_z3_clinical_contraindication_check`: Detecção de contraindicações biológicas via Z3 (ex.: contraste em IRA).
6. `test_real_medical_evidence_grounding`: Ancoragem de hipóteses em artigos reais com DOI/PMID e nível GRADE.
7. `test_orchestrator_medical_methods`: Integração nativa no `MarceloClaroOrchestrator`.
8. `test_doctor_check_19_clinical_engine`: Doctor reporta 19 checks estruturais ativos.
