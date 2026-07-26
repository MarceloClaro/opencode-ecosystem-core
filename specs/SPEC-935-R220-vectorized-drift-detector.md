---
spec_id: SPEC-935-R220
title: "Detecção de Desvio de Alvo Vetorizada (Vectorized Goal Drift Detector)"
component: trust/vectorized_drift.py, trust/trust_engine.py
test_file: tests/test_r220_vectorized_drift_detector.py
status: green
---

# SPEC-935-R220 — Vectorized Goal Drift Detector
=================================================

## 1. Visão Geral
Esta especificação otimiza a detecção de deriva de objetivo (`GoalDriftDetector`) com cálculo vetorial acelerado (vetores de caracteres/n-gramas e interseção matricial rasa).

## 2. Requisitos Funcionais
- **Mapeamento Vetorial**: Converter sequências textuais de objetivo e contexto em vetores numéricos de frequência de caracteres/subpalavras.
- **Desempenho**: Reduzir a latência do cálculo de similaridade para sub-milissegundos.
- **Interface da Classe `VectorizedGoalDriftDetector`**:
  - `calculate_similarity(text1: str, text2: str) -> float`
  - `check_drift(goal: str, context: str, threshold: float = 0.15) -> Dict[str, Any]`
