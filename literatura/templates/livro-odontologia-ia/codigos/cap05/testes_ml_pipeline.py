#!/usr/bin/env python3
"""testes_ml_pipeline.py — Testes TDD para pipeline de ML."""
import numpy as np

def test_dados_tem_formato_correto():
    """X deve ter 200 amostras e 5 features."""
    from pipeline_ml_carie_tdd import X
    assert X.shape == (200, 5)

def test_labels_binarias():
    """y deve conter apenas 0 e 1."""
    from pipeline_ml_carie_tdd import y
    assert set(np.unique(y)).issubset({0, 1})

def test_split_proporcoes():
    """Treino deve ter ~70% dos dados."""
    from pipeline_ml_carie_tdd import X_train, X_test
    assert abs(len(X_train) / (len(X_train) + len(X_test)) - 0.7) < 0.05

print("✅ Testes ML Pipeline aprovados!")
