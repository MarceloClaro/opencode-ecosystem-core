# SPEC-021 — OpenCode SuperHuman Scientific Pipeline

## Objetivo
Evoluir o pipeline científico do OpenCode Ecosystem Core para superar o SuperHuman (Google DeepMind — Aletheia/AlphaGeometry) em **rigor científico completo**, não apenas em raciocínio matemático formal.

## Diferenciais sobre o SuperHuman

| Capacidade | SuperHuman (DeepMind) | OpenCode (+ esta SPEC) |
|---|---|---|
| Raciocínio matemático formal | ✅ AlphaGeometry / Aletheia | ✅ MASWOS + Reasoning Engines |
| Método científico completo | ❌ Só matemática | ✅ Hipótese → Experimento → Estatística → Refutação |
| Memória epistemológica | ❌ | ✅ EvidenceGraph (claim → evidência → confiança → história) |
| Calibração de confiança | ❌ | ✅ Brier score, ECE, abstention |
| Refutação adversarial | ❌ Só verificação | ✅ AdversarialReviewer tenta refutar ativamente |
| Governança ética | ❌ | ✅ EGS (Ethical Governance Scanner) |
| Benchmark científico | ❌ Só IMO | ✅ ScientificBenchmark (causal, experimental, estatístico) |
| Reprodutibilidade auditável | ❌ | ✅ Seeds fixas, lineage, replay determinístico |
| Auto-reflexão (Reflexion) | ❌ | ✅ Meta-cognição com registro de lições |
| Token economy para qualidade | ❌ | ✅ Staking/slashing por qualidade científica |

## Módulos a implementar/melhorar

### 1. EvidenceGraph (`mci/evidence_graph.py`) — NOVO
Grafo epistemológico que rastreia:
- `claim_id` → versões ao longo do tempo
- evidência a favor/contra por claim
- confiança calibrada histórica
- condições de validade
- histórico de revisões

### 2. HypothesisEngine — MELHORADO
- Geração de hipóteses falsificáveis
- Hipótese nula explícita
- Prior Bayesiano configurável
- Previsão de direção do efeito

### 3. ExperimentDesigner — MELHORADO
- Power analysis (tamanho amostral)
- Randomização estratificada
- Controle de confounders
- Múltiplos braços experimentais

### 4. StatisticalValidator — MELHORADO
- Testes paramétricos + não paramétricos
- Bayes Factor
- Correção de múltiplas comparações (Bonferroni, FDR)
- Tamanho de efeito (Cohen's d, eta², OR)

### 5. AdversarialReviewer — MELHORADO
- Simulação de p-hacking
- Detecção de confounders
- Teste de robustez (jackknife, bootstrap)
- Tentativa de refutação sistemática

### 6. ConfidenceCalibrator — MELHORADO
- Calibração por Brier score
- Expected Calibration Error (ECE)
- Abstention quando incerteza alta
- Atualização por feedback

### 7. ScientificReporter — MELHORADO
- Relatório LaTeX completo
- Reproducibility checklist
- Limitações e viés
- DOI e citações

### 8. ScientificBenchmark — NOVO
- Benchmark de inferência causal
- Benchmark de desenho experimental
- Benchmark de power analysis
- Benchmark de interpretação estatística
- Benchmark de detecção de viés

## Critérios de Aceitação
- [ ] EvidenceGraph funcional com persistência JSON
- [ ] Pipeline completo roda com melhoria de qualidade
- [ ] Benchmark com ≥10 tarefas documentadas
- [ ] Confidence calibration com ECE < 0.10
- [ ] Testes TDD passando (RED → GREEN → REFACTOR)

## Métricas de Sucesso
- Reprodutibilidade > 95%
- ECE (calibração) < 0.10
- Taxa de auto-refutação > 20% (descobre erros antes da saída final)
- Benchmark score > SuperHuman baseline
