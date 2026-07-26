---
spec_id: SPEC-935-R223
title: "Scanner de Raciocínio Científico (Scientific Reasoning Scanner)"
component: scanners/scientific_reasoning_scanner.py
test_file: tests/test_r223_scientific_reasoning_scanner.py
status: green
---

# SPEC-935-R223 — Scanner de Raciocínio Científico
=================================================

## 1. Visão Geral
Esta especificação introduz o **`ScientificReasoningScanner`**, um scanner dedicado a auditar, medir e aprimorar a qualidade metodológica, o rigor de hipóteses e a força das evidências em manuscritos e preprints.

## 2. Dimensoes de Análise (Rigor Científico)
1. **Falsificabilidade Popperiana (Popperian Falsifiability)**: Avalia se as hipóteses apresentadas possuem critérios claros de invalidação empírica.
2. **Consistência Metodológica (Methodological Soundness)**: Detecta presenças de grupo de controle, amostragem e isolamento de variáveis de confusão (confounding variables).
3. **Análise de Vieses & Falácias (Bias & Fallacy Detection)**: Identifica apelos à autoridade, correlação vs. causalidade indevida e viés de confirmação.
4. **Índice de Rigor Científico (Scientific Rigor Index - SRI 0-100)**: Score ponderado consolidado com recomendações de aprimoramento.

## 3. Interface da Classe `ScientificReasoningScanner`
- `scan_text(text: str) -> Dict[str, Any]`
- `evaluate_hypothesis(hypothesis: str) -> Dict[str, Any]`
