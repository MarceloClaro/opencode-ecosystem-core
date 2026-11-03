"""Modelos + ensemble + calibração — SPEC-935-R898 §3.2 (incrementos 1/2/5)."""
from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def build_models(seed: int = 0) -> dict[str, Any]:
    """Baseline diverso para o ensemble (Kang et al. 2024; Väyrynen 2024)."""
    return {
        "logreg": make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000, random_state=seed),
        ),
        "histgb": HistGradientBoostingClassifier(
            max_depth=4, learning_rate=0.08, max_iter=300, random_state=seed
        ),
        "rf": RandomForestClassifier(
            n_estimators=200, min_samples_leaf=3, random_state=seed, n_jobs=-1
        ),
    }


class EnsembleClassifier:
    """Média de probabilidades de modelos diversificados (incremento #1)."""

    def __init__(self, estimators: list[Any]):
        self.estimators = list(estimators)

    def fit(self, X: Any, y: Any) -> "EnsembleClassifier":
        for est in self.estimators:
            est.fit(X, y)
        return self

    def predict_proba(self, X: Any) -> np.ndarray:
        if not self.estimators:
            raise RuntimeError("ensemble vazio")
        acc = None
        for est in self.estimators:
            p = est.predict_proba(X)[:, 1]
            acc = p if acc is None else acc + p
        mean_p = acc / len(self.estimators)
        return np.column_stack([1 - mean_p, mean_p])

    def predict(self, X: Any) -> np.ndarray:
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


def calibrate(model: Any, X: Any, y: Any, method: str = "sigmoid") -> Any:
    """Calibração Platt/isotônica (incremento #5); devolve estimator com
    ``predict_proba`` em [0,1]."""
    from sklearn.calibration import CalibratedClassifierCV

    cv = min(3, max(2, int(np.min(np.bincount(np.asarray(y, dtype=int))))))
    cal = CalibratedClassifierCV(model, method=method, cv=cv)
    cal.fit(X, y)
    return cal
