"""Inferência com modelo salvo — SPEC-935-R898 FR-009."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def load_bundle(path: str | Path) -> dict[str, Any]:
    import joblib

    bundle = joblib.load(path)
    if not isinstance(bundle, dict) or "model" not in bundle:
        raise ValueError("bundle inválido: esperado dict com 'model'")
    return bundle


def align_features(df: pd.DataFrame, feature_names: list[str]) -> pd.DataFrame:
    X = df.copy()
    for c in X.columns:
        if X[c].dtype == object:
            X[c] = X[c].astype(str)
    X = pd.get_dummies(X, drop_first=True)
    X = X.reindex(columns=feature_names, fill_value=0.0)
    return X.astype(float).fillna(0.0)


def predict_to_csv(
    model_path: str | Path,
    csv_path: str | Path,
    out_path: str | Path,
) -> pd.DataFrame:
    """FR-009: probs em [0,1] gravadas em CSV."""
    bundle = load_bundle(model_path)
    df = pd.read_csv(csv_path)
    target = bundle.get("target")
    feature_names = bundle["feature_names"]
    usable = df.drop(columns=[target], errors="ignore")
    X = align_features(usable, feature_names)
    model = bundle["model"]
    proba = model.predict_proba(X)[:, 1]
    if not np.all((proba >= 0) & (proba <= 1)):
        raise ValueError("probabilidade fora de [0,1]")
    out_df = df.copy()
    out_df["proba_ensemble"] = proba
    out_df["pred_label"] = (proba >= float(bundle.get("threshold", 0.5))).astype(int)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    return out_df
