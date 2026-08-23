# Ciclo de Evolução 264 (R446) — Motor de Investigação Clínica por Grafos Bayesianos, Teoria dos Jogos e Evidências Reais

## 1. Identificação
- **Ciclo:** `R446` (Ciclo 264)
- **Especificação:** `specs/SPEC-935-R446-clinical-game-theory-diagnostic-graphs.md`
- **Componentes:** `integrations/medical/`, `marceloclaro/orchestrator.py`, `marceloclaro/cli.py`, `marceloclaro/doctor.py`
- **Data:** 2026-08-23
- **Status:** `GREEN` (100% dos testes aprovados)

---

## 2. Objetivos
Implementar no ecossistema uma esteira neuro-simbólica de **Investigação Clínica Avançada** fundamentada em artigos médicos reais e diretrizes de consenso internacional (*PubMed, SciELO, The Lancet, NEJM, AHA/ACC, ESC, EULAR, KDIGO, Surviving Sepsis*), estruturada em 4 pilares:
1. **Grafos de Decisão Bayesiana & Razão de Verossimilhança (LR+/LR-)**: Atualização de probabilidades pré e pós-teste via nomograma de Fagan.
2. **Entropia de Shannon & Ganho de Informação ($IG$)**: Seleção propedêutica ótima para redução de incerteza diagnóstica.
3. **Teoria dos Jogos (Médico vs. Natureza) & Minimax Regret**: Matrizes de Payoff que ponderam sensibilidade, especificidade, custos, tempo e a penalidade crítica de omissão (*Critical Miss Penalty*) para blindar doenças graves.
4. **Verificação Lógica de Segurança via Z3 SMT Solver**: Checagem determinística de contraindicações renais, gestacionais, alergias e interações medicamentosas.

---

## 3. Entregas e Módulos Criados
- `integrations/medical/evidence_grounding.py`: Base curada de evidências reais com DOIs, PMIDs e níveis GRADE/Oxford CEBM.
- `integrations/medical/clinical_game_theory.py`: `DiagnosticDecisionGraph`, `ShannonEntropyEngine`, `ClinicalGameTheoryEngine` e `ClinicalAnamnesisGenerator`.
- `integrations/medical/clinical_verifier.py`: `ClinicalSafetyVerifier` integrado ao Z3 SMT Solver.
- `integrations/medical/clinical_orchestrator_bridge.py`: `ClinicalInvestigationPipeline` formatado no padrão YAML `resposta_medico_virtual_supremo`.
- `marceloclaro/orchestrator.py`: Métodos `investigate_clinical_case`, `generate_clinical_anamnesis` e `evaluate_diagnostic_decision_graph`.
- `marceloclaro/cli.py`: Subcomando `python3 -m marceloclaro.cli clinical "<queixa>" [--mode professional_cds|patient_education]`.
- `marceloclaro/doctor.py`: Check estrutural 19 (`clinical_game_theory_engine`).
- `tests/test_r446_clinical_game_theory_graphs.py`: Suíte de testes TDD com 9/9 testes aprovados (100% GREEN).

---

## 4. Validação de Testes
```bash
.venv/bin/pytest tests/test_r446_clinical_game_theory_graphs.py -v
============================== 9 passed in 5.09s ===============================
```
