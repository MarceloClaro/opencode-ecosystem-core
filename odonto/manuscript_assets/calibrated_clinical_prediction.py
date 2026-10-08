"""Nested, child-grouped evaluation of train-only probability recalibration.

The prior Colab output is reproduced separately under scikit-learn 1.6.1.
Here, an explicit corrected split policy is stable across 1.6.1 and 1.9.0.
Only aggregate statistics and figures are written; no individual predictions
or patient identifiers leave this process.
"""

from __future__ import annotations

# Figures are rendered at 300 dpi to meet the journal artwork requirement.

import json
import platform
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy.optimize import minimize, minimize_scalar
from scipy.special import expit, logit
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold

from real_clinical_prediction import (
    BOOTSTRAPS,
    FEATURE_SETS,
    FORBIDDEN,
    SEED,
    build_pipeline,
    interval,
    source_frame,
)
from reproduce_evidence import fit_calibration


OUT = Path(__file__).resolve().parent
METHODS = ("uncalibrated", "intercept_only", "intercept_and_slope")
VERSION_TAG = sklearn.__version__.replace(".", "")
SPLIT_POLICY = "corrected_permuted_groups"


def corrected_group_splits(X, y, groups, n_splits: int, seed: int):
    """Reproduce the corrected shuffle algorithm across sklearn versions.

    Permuting numeric group labels before shuffle=False yields the same stable
    tie order as the corrected shuffle=True implementation, while retaining
    the label-to-group mapping in affected older versions.
    """
    _, group_inverse = np.unique(groups, return_inverse=True)
    permutation = np.arange(int(group_inverse.max()) + 1)
    np.random.RandomState(seed).shuffle(permutation)
    inverse_permutation = np.empty_like(permutation)
    inverse_permutation[permutation] = np.arange(permutation.size)
    relabelled = inverse_permutation[group_inverse]
    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=False)
    return list(splitter.split(X, y, relabelled))


def _score(p: np.ndarray) -> np.ndarray:
    return logit(np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6))


def fit_recalibrators(y: np.ndarray, p: np.ndarray) -> dict[str, dict[str, float]]:
    """Fit two monotone maps using training-only cross-fitted probabilities."""
    y = np.asarray(y, dtype=int)
    x = _score(p)
    if len(np.unique(y)) != 2 or not np.isfinite(x).all():
        raise ValueError("Calibration training data need both outcomes and finite scores")
    offset = minimize_scalar(
        lambda a: log_loss(y, expit(a + x), normalize=False),
        method="bounded", bounds=(-12, 12),
    )
    if not offset.success:
        raise RuntimeError("Intercept recalibration failed")
    # The positive slope constraint keeps the map monotone in risk.
    line = minimize(
        lambda ab: log_loss(y, expit(ab[0] + ab[1] * x), normalize=False),
        x0=np.array([float(offset.x), 1.0]),
        method="L-BFGS-B", bounds=[(-12, 12), (0.05, 3.0)],
    )
    if not line.success or not np.isfinite(line.x).all():
        raise RuntimeError("Intercept-and-slope recalibration failed")
    return {
        "intercept_only": {"intercept": float(offset.x), "slope": 1.0},
        "intercept_and_slope": {
            "intercept": float(line.x[0]), "slope": float(line.x[1]),
        },
    }


def apply_recalibration(p: np.ndarray, parameters: dict[str, float]) -> np.ndarray:
    return expit(parameters["intercept"] + parameters["slope"] * _score(p))


def _metrics(y: np.ndarray, p: np.ndarray) -> dict[str, float]:
    return {
        "pr_auc": float(average_precision_score(y, p)),
        "roc_auc": float(roc_auc_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, np.clip(p, 1e-6, 1 - 1e-6))),
        **fit_calibration(y, p),
    }


def _reliability(ax, y: np.ndarray, p: np.ndarray, label: str, color: str) -> None:
    boundaries = np.unique(np.quantile(p, np.linspace(0, 1, 9)))
    if len(boundaries) < 3:
        return
    bins = np.digitize(p, boundaries[1:-1], right=True)
    px = [p[bins == k].mean() for k in range(len(boundaries) - 1) if (bins == k).any()]
    py = [y[bins == k].mean() for k in range(len(boundaries) - 1) if (bins == k).any()]
    ax.plot(px, py, "o-", lw=1.5, ms=4, label=label, color=color)


def _figures(y: np.ndarray, predictions: dict[str, dict[str, np.ndarray]], metrics: dict) -> None:
    colors = {"clinical_minimal": "#25668c", "clinical_spatial": "#bf7924"}
    labels = {"clinical_minimal": "Minimal clinical", "clinical_spatial": "Clinical + spatial"}
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), dpi=300)
    for name, variants in predictions.items():
        p = variants["uncalibrated"]
        precision, recall, _ = precision_recall_curve(y, p)
        fpr, tpr, _ = roc_curve(y, p)
        axes[0].plot(recall, precision, label=f"{labels[name]} (AP {metrics[name]['uncalibrated']['pr_auc']:.3f})", color=colors[name], lw=2)
        axes[1].plot(fpr, tpr, label=f"{labels[name]} (AUC {metrics[name]['uncalibrated']['roc_auc']:.3f})", color=colors[name], lw=2)
    axes[0].axhline(y.mean(), ls="--", color="#777", label=f"Event fraction {y.mean():.3f}")
    axes[1].plot([0, 1], [0, 1], ls="--", color="#777", label="Chance")
    axes[0].set(xlabel="Recall", ylabel="Precision", title="A. Precision–recall")
    axes[1].set(xlabel="False-positive rate", ylabel="True-positive rate", title="B. ROC")
    for ax in axes:
        ax.legend(fontsize=8)
        ax.grid(alpha=0.15)
        # Pin the ticks to the plotted range. The automatic locator emitted a
        # tick at -0.2, which lies OUTSIDE xlim=(-0.05, 1.05); matplotlib still
        # drew its label, and it spilled left out of the axes and collided with
        # the neighbouring panel's rightmost tick label ("-0.2" over "1.0").
        ax.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    fig.tight_layout()
    fig.savefig(OUT / f"Figure_2_discrimination_corrected_sklearn{VERSION_TAG}.png", dpi=600, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), dpi=300)
    method_labels = {
        "uncalibrated": "Original", "intercept_only": "Intercept updated",
        "intercept_and_slope": "Intercept and slope updated",
    }
    method_colors = {
        "uncalibrated": "#69747c", "intercept_only": "#25668c",
        "intercept_and_slope": "#bf7924",
    }
    for ax, (name, variants) in zip(axes, predictions.items()):
        ax.plot([0, 0.5], [0, 0.5], ls="--", color="#333", lw=1, label="Ideal")
        for method, p in variants.items():
            _reliability(ax, y, p, method_labels[method], method_colors[method])
        ax.set(xlim=(0, 0.5), ylim=(0, 0.5), xlabel="Mean predicted risk", ylabel="Observed event fraction", title=labels[name])
        ax.grid(alpha=0.15)
        ax.legend(fontsize=7)
        ax.set_xticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])   # no tick outside xlim
        ax.set_yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
    fig.tight_layout()
    fig.savefig(OUT / f"Figure_3_calibration_corrected_sklearn{VERSION_TAG}.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


def run() -> dict:
    if sklearn.__version__ not in ("1.6.1", "1.9.0"):
        raise RuntimeError("This version sensitivity requires scikit-learn 1.6.1 or 1.9.0")
    frame, source = source_frame()
    y = frame["progression_event"].to_numpy(dtype=int)
    groups = frame["child_id"].astype(str).to_numpy()
    if any(FORBIDDEN.intersection(d["cat"] + d["num"]) for d in FEATURE_SETS.values()):
        raise AssertionError("Future/outcome-derived variable entered the model")
    predictions = {
        name: {method: np.full(len(y), np.nan) for method in METHODS}
        for name in FEATURE_SETS
    }
    fold_ids = np.full(len(y), -1)
    folds = []
    prevalence = np.full(len(y), np.nan)
    outer_splits = corrected_group_splits(frame, y, groups, n_splits=5, seed=SEED)
    for fold, (train, test) in enumerate(outer_splits):
        if not set(groups[train]).isdisjoint(groups[test]) or len(np.unique(y[test])) != 2:
            raise AssertionError("Outer child separation or outcome balance failed")
        prevalence[test] = y[train].mean()
        fold_ids[test] = fold
        detail = {
            "fold": fold, "train_rows": len(train), "test_rows": len(test),
            "train_children": len(set(groups[train])), "test_children": len(set(groups[test])),
            "train_events": int(y[train].sum()), "test_events": int(y[test].sum()),
        }
        splits = corrected_group_splits(
            frame.iloc[train], y[train], groups[train],
            n_splits=3, seed=SEED + 100 + fold,
        )
        if any(not set(groups[train][a]).isdisjoint(groups[train][b]) for a, b in splits):
            raise AssertionError("Inner child separation failed")
        for name, definition in FEATURE_SETS.items():
            columns = definition["cat"] + definition["num"]
            xtrain, xtest = frame.iloc[train][columns], frame.iloc[test][columns]
            search = GridSearchCV(
                build_pipeline(definition["cat"], definition["num"]),
                {"model__C": [0.01, 0.1, 1.0, 10.0]},
                scoring="average_precision", cv=splits, n_jobs=1,
                refit=True, error_score="raise",
            )
            search.fit(xtrain, y[train])
            chosen_c = search.best_params_["model__C"]
            positive = np.flatnonzero(search.best_estimator_.classes_ == 1)
            if len(positive) != 1:
                raise AssertionError("Positive outcome class is ambiguous")
            raw_test = search.predict_proba(xtest)[:, int(positive[0])]
            predictions[name]["uncalibrated"][test] = raw_test

            # Calibration sees only cross-fitted predictions from this outer TRAIN.
            inner_oof = np.full(len(train), np.nan)
            for a, b in splits:
                model = build_pipeline(definition["cat"], definition["num"])
                model.set_params(model__C=chosen_c)
                model.fit(xtrain.iloc[a], y[train][a])
                positive_inner = np.flatnonzero(model.classes_ == 1)
                if len(positive_inner) != 1:
                    raise AssertionError("Inner positive class is ambiguous")
                inner_oof[b] = model.predict_proba(xtrain.iloc[b])[:, int(positive_inner[0])]
            if not np.isfinite(inner_oof).all():
                raise AssertionError("Incomplete inner cross-fitting")
            recalibrators = fit_recalibrators(y[train], inner_oof)
            for method, params in recalibrators.items():
                predictions[name][method][test] = apply_recalibration(raw_test, params)
            detail[name + "_C"] = chosen_c
            detail[name + "_calibration"] = recalibrators
        folds.append(detail)

    if (fold_ids < 0).any() or pd.DataFrame({"child": groups, "fold": fold_ids}).groupby("child")["fold"].nunique().max() != 1:
        raise AssertionError("Outer grouped OOF coverage failed")
    if any(not np.isfinite(p).all() or ((p < 0) | (p > 1)).any() for v in predictions.values() for p in v.values()):
        raise AssertionError("Invalid external-fold probability")
    metrics = {name: {method: _metrics(y, p) for method, p in variants.items()} for name, variants in predictions.items()}

    # Paired child bootstrap conditions on the already cross-fitted predictions.
    rng = np.random.default_rng(SEED + 1)
    children = np.unique(groups)
    child_indices = {child: np.flatnonzero(groups == child) for child in children}
    differences = {
        name: {method: {metric: [] for metric in ("brier", "log_loss")}
               for method in METHODS if method != "uncalibrated"}
        for name in FEATURE_SETS
    }
    valid = 0
    for _ in range(BOOTSTRAPS):
        sampled = rng.choice(children, size=len(children), replace=True)
        index = np.concatenate([child_indices[child] for child in sampled])
        yy = y[index]
        if len(np.unique(yy)) != 2:
            continue
        valid += 1
        for name, variants in predictions.items():
            raw = variants["uncalibrated"][index]
            for method in differences[name]:
                calibrated = variants[method][index]
                differences[name][method]["brier"].append(float(brier_score_loss(yy, calibrated) - brier_score_loss(yy, raw)))
                differences[name][method]["log_loss"].append(float(log_loss(yy, calibrated) - log_loss(yy, raw)))
    delta_report = {
        name: {
            method: {
                metric: {
                    "estimate": metrics[name][method][metric] - metrics[name]["uncalibrated"][metric],
                    "ci95": interval(values),
                }
                for metric, values in by_metric.items()
            }
            for method, by_metric in by_method.items()
        }
        for name, by_method in differences.items()
    }
    report = {
        "analysis_status": "EXPLORATORY_INTERNAL_VALIDATION_ONLY",
        "source": source,
        "runtime": {
            "python": platform.python_version(), "numpy": np.__version__,
            "pandas": pd.__version__, "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "analysis_rows": len(y), "analysis_events": int(y.sum()),
        "analysis_children": len(children),
        "event_children": len(np.unique(groups[y == 1])),
        "event_fraction": float(y.mean()),
        "seed": SEED, "outer_folds": 5, "inner_folds": 3,
        "split_policy": SPLIT_POLICY,
        "fold_log": folds,
        "metrics": metrics,
        "prevalence_reference": {
            "brier": float(brier_score_loss(y, prevalence)),
            "log_loss": float(log_loss(y, prevalence)),
        },
        "calibration_minus_uncalibrated": delta_report,
        "bootstrap_requested": BOOTSTRAPS, "bootstrap_valid": valid,
        "scope_note": "Cross-fitted internal calibration within 81 children; no external validation or clinical use.",
    }
    path = OUT / f"calibrated_clinical_internal_validation_corrected_sklearn{VERSION_TAG}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    _figures(y, predictions, metrics)
    print(json.dumps({"metrics": metrics, "calibration_minus_uncalibrated": delta_report}, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    run()
