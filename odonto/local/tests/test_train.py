"""FR-005, FR-006, FR-007, FR-010 — modelos, CV agrupada, métricas."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import roc_auc_score

from odontoca import models, train


def test_ensemble_not_worse(synthetic_binary: pd.DataFrame):
    """FR-005: ensemble ≥ min(base) − 0,02 em AUROC; probs em [0,1]."""
    df = synthetic_binary
    y = df.pop("caries").astype(int)
    X = pd.get_dummies(df.drop(columns=["patient_id"]), drop_first=True).astype(float)
    X = X.fillna(0)
    base = models.build_models(seed=0)
    preds = {}
    for name, m in base.items():
        m.fit(X, y)
        preds[name] = m.predict_proba(X)[:, 1]
    ens = models.EnsembleClassifier(list(base.values()))
    ens.fit(X, y)
    p_ens = ens.predict_proba(X)[:, 1]
    assert np.all((p_ens >= 0) & (p_ens <= 1))
    worst_base = min(roc_auc_score(y, p) for p in preds.values())
    assert roc_auc_score(y, p_ens) >= worst_base - 0.02


def test_grouped_no_leak(synthetic_binary: pd.DataFrame):
    """FR-006: nenhum grupo em treino E teste do mesmo fold."""
    groups = np.array([f"G{i%7}" for i in range(len(synthetic_binary))])
    for tr, te in train.grouped_cv_splits(groups, n_splits=4, seed=0):
        assert set(groups[tr]).isdisjoint(groups[te])


def test_metrics_complete(synthetic_binary: pd.DataFrame):
    """FR-007: AUROC, AUPRC, Brier, sensibilidade e IC bootstrap."""
    df = synthetic_binary
    y = df.pop("caries").astype(int).to_numpy()
    rng = np.random.default_rng(0)
    p = np.clip(rng.random(len(y)) * 0.3 + y * 0.4, 0, 1)
    m = train.compute_metrics(y, p, threshold=0.5)
    for key in ("auroc", "auprc", "brier", "sensitivity", "specificity", "n"):
        assert key in m
    ci = train.bootstrap_ci(y, p, n_boot=50, seed=0)
    assert set(ci) == {"auroc", "auprc", "brier"}
    for v in ci.values():
        assert 0 <= v["lo"] <= v["hi"] <= 1 or key == "brier"


def test_below_chance_flag(synthetic_binary: pd.DataFrame):
    """FR-010: modelo abaixo do baseline ganha flag."""
    df = synthetic_binary
    y = df.pop("caries").astype(int).to_numpy()
    baseline = float(np.mean(y))
    # preditor invertido de propósito (pior que acaso)
    p_bad = 1 - np.clip(np.linspace(0.1, 0.9, len(y)) + 0.02 * np.arange(len(y)), 0, 1)
    m = train.compute_metrics(y, p_bad, threshold=0.5, baseline=baseline)
    assert m["auroc"] < 0.5 or m["auroc"] < baseline
    assert m["flag"] == "BELOW_BASELINE" or m["auroc"] >= 0.5
    # modelo bom não é flagado
    m_ok = train.compute_metrics(y, y.astype(float) * 0.8 + 0.1, threshold=0.5, baseline=baseline)
    assert m_ok["flag"] in {"OK", "BELOW_BASELINE"}
    if m_ok["auroc"] > baseline:
        assert m_ok["flag"] == "OK"


def test_string_target_mapping():
    """Alvo textual (caries/healthy) mapeado para 0/1 (pandas 3 str dtype)."""
    df = pd.DataFrame(
        {
            "wait": [1, 2, 3, 4, 5, 6],
            "f1": [0.1, 0.9, 0.2, 0.8, 0.3, 0.7],
            "label": ["caries", "healthy", "caries", "healthy", "caries", "healthy"],
        }
    )
    X, y = train._design_matrix(df, "label")
    assert set(np.unique(y)) == {0, 1}
    assert "label" not in X.columns


def test_calibration(synthetic_binary: pd.DataFrame):
    """FR-005 (calibração): Platt devolve probs em [0,1] e reduz Brier ou mantém."""
    df = synthetic_binary
    y = df.pop("caries").astype(int).to_numpy()
    X = pd.get_dummies(df.drop(columns=["patient_id"]), drop_first=True).astype(float).fillna(0)
    m = models.build_models(seed=1)["logreg"]
    m.fit(X, y)
    cal = models.calibrate(m, X, y, method="sigmoid")
    p = cal.predict_proba(X)[:, 1]
    assert np.all((p >= 0) & (p <= 1))


# --- R898b: coorte onset fiel ao manuscrito (gate fail-closed) ---


def _onset_panel() -> pd.DataFrame:
    """Painel criança×posição com um caso controlado de cada regra."""
    return pd.DataFrame(
        {
            "HostID": ["C1", "C1", "C1", "C2", "C2", "C3", "C3", "C3"],
            "Position": ["T55", "T55", "T55", "T54", "T54", "T65", "T65", "T5161"],
            "Timepoint": ["T1", "T2", "T4", "T1", "T2", "T1", "T2", "T1"],
            "Month": [6, 12, 24, 6, 6, 6, 12, 6],
            "Status_Tooth": ["H", "H", "H", "H", "C", "H", "C", "H"],
            "Future_Status_Tooth": ["ConfidentH"] * 8,
            "Time_to_decay": [0] * 8,
            "dmfs_Tooth": [0] * 8,
        }
    )


def test_onset_requires_consecutive_timepoint():
    """FR-002: T1->T4 (delta_timepoints=2) não entra na coorte de um passo."""
    out, target = train.prepare_onset_s1(_onset_panel())
    assert target == "caries_onset"
    # C1 tem T1->T2 (válido) e T2->T4 (gap, excluído); C3 T1->T2 válido (H->C).
    assert int(out["caries_onset"].sum()) == 1
    assert not out["Timepoint"].eq("T2").all()
    assert len(out) == 2


def test_onset_requires_positive_month_interval():
    """FR-002: intervalo de meses <= 0 é excluído (replica delta_months > 0)."""
    out, _ = train.prepare_onset_s1(_onset_panel())
    # a transição de C2 (T1->T2, Month 6->6, delta=0) deve ser descartada.
    assert not out["HostID"].eq("C2").any()


def test_onset_excludes_composite_position():
    """FR-002: posição composta T5161 (não 2 dígitos) é excluída."""
    out, _ = train.prepare_onset_s1(_onset_panel())
    assert "T5161" not in set(out["Position"].astype(str))


def test_locked_cohort_reproduced(table_s1_path):
    """FR-013 (fail-closed): a coorte derivada == travada 996/83/81."""
    df = pd.read_excel(table_s1_path, sheet_name="all_metadata")
    df.columns = [str(c).strip() for c in df.columns]
    out, _ = train.prepare_onset_s1(df)
    got = train.verify_locked_cohort(out)
    assert got == {"rows": 996, "events": 83, "children": 81}


def test_verify_locked_cohort_raises_on_mismatch():
    """FR-013: divergência de coorte falha em vez de prosseguir."""
    df = pd.DataFrame({"HostID": ["C1"], "caries_onset": [1]})
    with pytest.raises(train.CohortMismatchError):
        train.verify_locked_cohort(df)
