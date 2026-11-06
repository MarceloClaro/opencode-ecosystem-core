#!/usr/bin/env python3
"""pipeline_ml_carie_tdd.py — Pipeline ML para predição de cárie com TDD."""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Dados sintéticos para demonstração
np.random.seed(42)
X = np.random.rand(200, 5)  # 5 features clínicas
y = (X[:, 0] * 0.6 + X[:, 1] * 0.3 + np.random.randn(200) * 0.1 > 0.5).astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X_train, y_train)
acc = model.score(X_test, y_test)
print(f"✅ Acurácia do modelo: {acc:.2%}")

# TDD
assert acc > 0.5, f"Acurácia muito baixa: {acc}"
assert model.n_estimators == 50
print("✅ Pipeline ML — TDD aprovado!")
