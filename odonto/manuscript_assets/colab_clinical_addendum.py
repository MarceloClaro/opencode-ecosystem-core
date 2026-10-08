"""Exploratory internal validation using the public OdontoCA source cohort.

The two candidate feature sets are fixed before examining model performance.
All preprocessing and regularisation selection occur within child-grouped
training folds. No microbiome or image data are used. Individual records and
identifiers are neither exported nor added to the manuscript directory.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from io import BytesIO
import sys
import requests

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score, brier_score_loss, log_loss,
    precision_recall_curve, roc_auc_score, roc_curve,
)
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from scipy.optimize import minimize, minimize_scalar
from scipy.special import expit, logit

SOURCE_COMMIT = "e5868fe5664460c7aac1c5b6d7980776ad26b29c"
SOURCE_URL = (
    "https://raw.githubusercontent.com/HuangShiLab/Single-tooth-ECC/"
    + SOURCE_COMMIT + "/Figures_and_Tables_in_Manuscript/Table_S1.xlsx"
)
SOURCE_SHA256 = "b7819fee81efbe2e227b7700c3cd86ce8bc6f7fe6f49da6214f4107d099184fa"


def fit_calibration(y, p):
    score = logit(np.clip(p, 1e-6, 1 - 1e-6))
    offset = minimize_scalar(
        lambda intercept: log_loss(y, expit(intercept + score), normalize=False),
        method="bounded", bounds=(-12, 12),
    )
    line = minimize(
        lambda coef: log_loss(y, expit(coef[0] + coef[1] * score), normalize=False),
        x0=np.array([0.0, 1.0]), method="BFGS",
    )
    if not np.isfinite(line.x).all():
        raise AssertionError("Nonfinite calibration coefficients")
    return {
        "mean_predicted": float(p.mean()),
        "observed_fraction": float(y.mean()),
        "calibration_in_the_large": float(offset.x),
        "calibration_slope": float(line.x[1]),
        "calibration_model_intercept": float(line.x[0]),
    }


OUT = Path(
    "/content/OdontoCA_v1_3/09_clinical_addendum"
    if "google.colab" in sys.modules else "/tmp/odonto_colab_addendum"
)
OUT.mkdir(parents=True, exist_ok=True)
SEED = 20260930
BOOTSTRAPS = 1000
FORBIDDEN = {
    "HostGroup", "host_group_source", "Future_Status_Tooth",
    "future_status_source_t", "Time_to_decay", "time_to_decay_source_t",
    "state_t1", "progression_event", "delta_months", "timepoint_t1",
}
FEATURE_SETS = {
    "clinical_minimal": {
        "cat": ["tooth_position"],
        "num": ["age_months_t", "host_dmfs_t", "neighbor_caries_count"],
    },
    "clinical_spatial": {
        "cat": ["tooth_position", "niche_icm", "niche_ul", "niche_lr", "niche_ap", "host_status_t"],
        "num": [
            "age_months_t", "host_dmfs_t", "neighbor_caries_count",
            "spatial_weighted_dmfs_t", "sum_dmfs_t", "sum_ns_dt_t", "sum_s_dt_t",
        ],
    },
}


def source_frame() -> tuple[pd.DataFrame, dict]:
    if not all(name in globals() for name in ("clean_single_tooth", "build_transitions")):
        raise RuntimeError("Execute as células anteriores de reconstrução longitudinal primeiro")
    response = requests.get(SOURCE_URL, timeout=90)
    response.raise_for_status()
    content = response.content
    digest = hashlib.sha256(content).hexdigest()
    if digest != SOURCE_SHA256:
        raise RuntimeError("O hash SHA-256 do suplemento clínico é diferente do auditado")
    meta = pd.read_excel(BytesIO(content), sheet_name="all_metadata")
    meta.columns = [str(col).strip() for col in meta.columns]
    _, _, clean = clean_single_tooth(meta)
    _, _, onset = build_transitions(clean)
    onset = onset.copy()
    onset["neighbor_caries_count"] = (
        onset["neighbor_prev_state_t"].eq("C").astype(int)
        + onset["neighbor_next_state_t"].eq("C").astype(int)
    )
    if len(onset) != 997 or int(onset["progression_event"].sum()) != 84:
        raise AssertionError("As contagens da coorte de origem não foram reproduzidas")
    zero_interval = onset.loc[onset["delta_months"].le(0)]
    frame = onset.loc[onset["delta_months"].gt(0)].reset_index(drop=True)
    if len(frame) != 996 or int(frame["progression_event"].sum()) != 83:
        raise AssertionError("A coorte analítica com seguimento positivo mudou")
    return frame, {
        "source_sha256": digest,
        "reproduced_eligible": 997,
        "reproduced_events": 84,
        "excluded_nonpositive_followup_interval": len(zero_interval),
        "excluded_events": int(zero_interval["progression_event"].sum()),
    }


def build_pipeline(categories: list[str], numeric: list[str]) -> Pipeline:
    try:
        onehot = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        onehot = OneHotEncoder(handle_unknown="ignore", sparse=False)
    prep = ColumnTransformer(
        [
            ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("onehot", onehot)]), categories),
            ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
        ],
        remainder="drop", sparse_threshold=0,
    )
    return Pipeline([
        ("prep", prep),
        ("model", LogisticRegression(penalty="l2", solver="liblinear", max_iter=5000)),
    ])


def interval(values: list[float]) -> list[float]:
    return [float(v) for v in np.quantile(values, [0.025, 0.975])]


def run() -> None:
    frame, source = source_frame()
    y = frame["progression_event"].to_numpy(dtype=int)
    groups = frame["child_id"].astype(str).to_numpy()
    for definition in FEATURE_SETS.values():
        if FORBIDDEN.intersection(definition["cat"] + definition["num"]):
            raise AssertionError("A future or outcome-derived variable entered the model")

    predictions = {name: np.full(len(frame), np.nan) for name in FEATURE_SETS}
    prevalence_reference = np.full(len(frame), np.nan)
    fold_assignment = np.full(len(frame), -1)
    fold_log = []
    outer = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    for fold, (train, test) in enumerate(outer.split(frame, y, groups)):
        if not set(groups[train]).isdisjoint(groups[test]):
            raise AssertionError("Child overlap across outer folds")
        if len(np.unique(y[test])) != 2:
            raise AssertionError("Outer test fold lacks one outcome class")
        prevalence_reference[test] = y[train].mean()
        inner = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=SEED + 100 + fold)
        log = {
            "fold": fold,
            "train_rows": len(train), "test_rows": len(test),
            "train_children": len(set(groups[train])), "test_children": len(set(groups[test])),
            "train_events": int(y[train].sum()), "test_events": int(y[test].sum()),
        }
        for name, definition in FEATURE_SETS.items():
            columns = definition["cat"] + definition["num"]
            search = GridSearchCV(
                build_pipeline(definition["cat"], definition["num"]),
                {"model__C": [0.01, 0.1, 1.0, 10.0]},
                scoring="average_precision", cv=inner, n_jobs=1,
                refit=True, error_score="raise",
            )
            search.fit(frame.iloc[train][columns], y[train], groups=groups[train])
            classes = search.best_estimator_.named_steps["model"].classes_
            positive = np.flatnonzero(classes == 1)
            if len(positive) != 1:
                raise AssertionError("Positive class is absent or ambiguous")
            predictions[name][test] = search.predict_proba(frame.iloc[test][columns])[:, int(positive[0])]
            log[name + "_C"] = search.best_params_["model__C"]
        fold_assignment[test] = fold
        fold_log.append(log)

    if pd.DataFrame({"child": groups, "fold": fold_assignment}).groupby("child")["fold"].nunique().max() != 1:
        raise AssertionError("Grouped validation invariant failed")
    if not all(np.isfinite(p).all() and ((p >= 0) & (p <= 1)).all() for p in predictions.values()):
        raise AssertionError("Invalid out-of-fold probability")

    metrics = {}
    for name, p in predictions.items():
        metrics[name] = {
            "pr_auc": float(average_precision_score(y, p)),
            "roc_auc": float(roc_auc_score(y, p)),
            "brier": float(brier_score_loss(y, p)),
            "log_loss": float(log_loss(y, np.clip(p, 1e-6, 1 - 1e-6))),
            **fit_calibration(y, p),
        }

    rng = np.random.default_rng(SEED + 1)
    children = np.unique(groups)
    child_indices = {child: np.flatnonzero(groups == child) for child in children}
    sampled_metrics = {name: {metric: [] for metric in ["pr_auc", "roc_auc", "brier"]} for name in predictions}
    sampled_deltas = {metric: [] for metric in ["pr_auc", "roc_auc", "brier"]}
    valid = 0
    for _ in range(BOOTSTRAPS):
        sampled = rng.choice(children, size=len(children), replace=True)
        index = np.concatenate([child_indices[child] for child in sampled])
        yy = y[index]
        if len(np.unique(yy)) != 2:
            continue
        valid += 1
        for name, p in predictions.items():
            pp = p[index]
            sampled_metrics[name]["pr_auc"].append(float(average_precision_score(yy, pp)))
            sampled_metrics[name]["roc_auc"].append(float(roc_auc_score(yy, pp)))
            sampled_metrics[name]["brier"].append(float(brier_score_loss(yy, pp)))
        for metric in sampled_deltas:
            sampled_deltas[metric].append(
                sampled_metrics["clinical_spatial"][metric][-1]
                - sampled_metrics["clinical_minimal"][metric][-1]
            )
    for name in metrics:
        for metric, values in sampled_metrics[name].items():
            metrics[name][metric + "_ci95"] = interval(values)
    differences = {
        metric: {
            "estimate": metrics["clinical_spatial"][metric] - metrics["clinical_minimal"][metric],
            "ci95": interval(values),
        }
        for metric, values in sampled_deltas.items()
    }

    report = {
        "analysis_status": "EXPLORATORY_INTERNAL_VALIDATION_ONLY",
        "source": source,
        "source_commit": SOURCE_COMMIT,
                "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "analysis_rows": len(frame),
        "analysis_events": int(y.sum()),
        "analysis_children": len(children),
        "event_children": int(frame.loc[frame["progression_event"].eq(1), "child_id"].nunique()),
        "event_fraction": float(y.mean()),
        "followup_months_median": float(frame["delta_months"].median()),
        "followup_months_iqr": [float(v) for v in frame["delta_months"].quantile([0.25, 0.75])],
        "followup_months_range": [float(frame["delta_months"].min()), float(frame["delta_months"].max())],
        "seed": SEED, "outer_folds": 5, "inner_folds": 3,
        "feature_sets": FEATURE_SETS,
        "fold_log": fold_log,
        "child_disjoint_outer_folds": True,
        "bootstrap_requested": BOOTSTRAPS, "bootstrap_valid": valid,
        "metrics": metrics,
        "prevalence_reference": {
            "brier": float(brier_score_loss(y, prevalence_reference)),
            "log_loss": float(log_loss(y, prevalence_reference)),
        },
        "spatial_minus_minimal": differences,
        "scope_note": (
            "This is internal validation in one public cohort with no external test, "
            "real microbiome alignment or image branch. Patient use is unsupported."
        ),
    }
    (OUT / "real_clinical_internal_validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))

    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), dpi=170)
    colors = {"clinical_minimal": "#25668c", "clinical_spatial": "#bf7924"}
    for name, p in predictions.items():
        precision, recall, _ = precision_recall_curve(y, p)
        fpr, tpr, _ = roc_curve(y, p)
        label = "Minimal clinical" if name == "clinical_minimal" else "Clinical + spatial"
        axes[0].plot(recall, precision, label=f"{label} (AP {metrics[name]['pr_auc']:.3f})", color=colors[name], lw=2)
        axes[1].plot(fpr, tpr, label=f"{label} (AUC {metrics[name]['roc_auc']:.3f})", color=colors[name], lw=2)
    axes[0].axhline(y.mean(), color="#777777", ls="--", label=f"Event fraction {y.mean():.3f}")
    axes[1].plot([0, 1], [0, 1], color="#777777", ls="--", label="Chance")
    axes[0].set(xlabel="Recall", ylabel="Precision", title="A. Precision–recall")
    axes[1].set(xlabel="False-positive rate", ylabel="True-positive rate", title="B. ROC")
    for ax in axes:
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.legend(loc="best", frameon=False, fontsize=8)
    fig.suptitle("Public clinical cohort: child-grouped internal out-of-fold predictions", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "Figure_2_real_internal_validation.png", bbox_inches="tight")
    fig.savefig(OUT / "Figure_2_real_internal_validation.pdf", bbox_inches="tight")
    plt.close(fig)

    # Descriptive calibration only: each point pools one fifth of observations
    # ordered by out-of-fold predicted probability, without outcome fitting.
    fig, ax = plt.subplots(figsize=(5.5, 5.0), dpi=170)
    max_bin_value = 0.0
    for name, p in predictions.items():
        ordered = np.argsort(p)
        bins = np.array_split(ordered, 5)
        mean_pred = [float(p[part].mean()) for part in bins]
        observed = [float(y[part].mean()) for part in bins]
        max_bin_value = max(max_bin_value, *mean_pred, *observed)
        label = "Minimal clinical" if name == "clinical_minimal" else "Clinical + spatial"
        ax.plot(mean_pred, observed, marker="o", color=colors[name], lw=2, label=label)
    axis_max = min(1.0, max_bin_value * 1.12)
    ax.plot([0, axis_max], [0, axis_max], ls="--", color="#777777", label="Ideal calibration")
    ax.set(xlim=(0, axis_max), ylim=(0, axis_max), xlabel="Mean predicted risk", ylabel="Observed event fraction",
           title="Internal calibration, five equal-count bins")
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    fig.subplots_adjust(left=0.19, right=0.98, top=0.93, bottom=0.15)
    fig.savefig(OUT / "Figure_3_real_internal_calibration.png", bbox_inches="tight")
    fig.savefig(OUT / "Figure_3_real_internal_calibration.pdf", bbox_inches="tight")
    plt.close(fig)

    print(json.dumps({
        "analysis_rows": report["analysis_rows"],
        "analysis_events": report["analysis_events"],
        "analysis_children": report["analysis_children"],
        "event_fraction": report["event_fraction"],
        "metrics": metrics,
        "prevalence_reference": report["prevalence_reference"],
        "spatial_minus_minimal": differences,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run()
