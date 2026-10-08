"""Independent, reproducible audit of the OdontoCA v1.3 research notebook.

The original notebook is read, never modified. Synthetic predictive performance
and real clinical cohort reconstruction are kept in separate output files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NOTEBOOK = ROOT / "OdontoCA_v1_3_2_FULL_RESEARCH_COM_IMAGEM_FLUXOGRAMA_EXECUTED (3).ipynb"
S1_URL = (
    "https://raw.githubusercontent.com/HuangShiLab/Single-tooth-ECC/"
    "main/Figures_and_Tables_in_Manuscript/Table_S1.xlsx"
)
EXCLUDED = {
    "progression_event", "state_t1", "state_code_t1", "dmfs_tooth_t1",
    "future_status_source_t", "time_to_decay_source_t", "host_status_t1",
    "host_dmfs_t1", "sample_id_t1", "timepoint_t1",
}
COMPACT_FEATURES = ["molar", "neighbor_caries_count", "host_dmfs_t", "age_months_t"]


def notebook_namespace() -> dict:
    """Load the exact data-generation and model definitions from named cells."""
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    # dataclasses resolves annotations through sys.modules[__module__].
    namespace: dict = {"__name__": "__main__"}
    for cell in (5, 6, 10, 13, 15, 19, 20, 22, 24):
        source = "".join(notebook["cells"][cell]["source"])
        exec(compile(source, f"{NOTEBOOK.name}:cell_{cell}", "exec"), namespace)
    return namespace


def assert_disjoint(train_groups, test_groups) -> None:
    overlap = set(train_groups).intersection(test_groups)
    if overlap:
        raise AssertionError(f"Groups shared across train and test: {sorted(overlap)}")


def metric_row(name: str, y: np.ndarray, p: np.ndarray) -> dict:
    p = np.asarray(p, dtype=float)
    if not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise AssertionError(f"Invalid predictions for {name}")
    return {
        "model": name,
        "n": int(len(y)),
        "events": int(np.sum(y)),
        "prevalence": float(np.mean(y)),
        "PR_AUC": float(average_precision_score(y, p)),
        "ROC_AUC": float(roc_auc_score(y, p)),
        "Brier": float(brier_score_loss(y, p)),
        "LogLoss": float(log_loss(y, np.clip(p, 1e-8, 1 - 1e-8))),
        "mean_predicted_risk": float(np.mean(p)),
        "observed_minus_predicted": float(np.mean(y) - np.mean(p)),
    }


def cluster_bootstrap(
    y: np.ndarray, groups: np.ndarray, predictions: dict[str, np.ndarray],
    repeats: int, seed: int,
) -> pd.DataFrame:
    """Percentile CIs conditional on already fitted OOF predictions, not refitted CIs."""
    rng = np.random.default_rng(seed)
    children = np.unique(groups)
    indices = {child: np.flatnonzero(groups == child) for child in children}
    samples = {name: [] for name in predictions}
    valid = 0
    for _ in range(repeats):
        sampled = rng.choice(children, size=len(children), replace=True)
        idx = np.concatenate([indices[child] for child in sampled])
        yy = y[idx]
        if len(np.unique(yy)) != 2:
            continue
        valid += 1
        for name, pred in predictions.items():
            p = pred[idx]
            samples[name].append((
                average_precision_score(yy, p), roc_auc_score(yy, p),
                brier_score_loss(yy, p), np.mean(yy) - np.mean(p),
            ))
    if valid < repeats * .9:
        raise AssertionError(f"Only {valid}/{repeats} valid cluster resamples")
    rows = []
    for name, values in samples.items():
        array = np.asarray(values)
        for col, metric in enumerate(("PR_AUC", "ROC_AUC", "Brier", "observed_minus_predicted")):
            low, high = np.quantile(array[:, col], [.025, .975])
            rows.append({
                "model": name, "metric": metric, "ci95_low": float(low),
                "ci95_high": float(high), "valid_resamples": valid,
                "interval_type": "child_cluster_percentile_conditional_on_OOF_predictions",
            })
    return pd.DataFrame(rows)


def run_synthetic(namespace: dict, repeats: int) -> dict:
    seed = namespace["CFG"].SEED
    clean = namespace["make_synthetic_clean"](seed)
    _, _, onset = namespace["build_transitions"](clean)
    onset = namespace["add_ca_features"](onset)
    counts = namespace["synthetic_micro_counts"](onset, seed)

    ca_metrics, ca_pred, ca_fold = namespace["ca_oof"](onset, 3, seed)
    frame, y, groups, original, fold_id, original_folds = namespace["nested_oof_three_models"](
        onset, counts, 3, 2, seed,
    )
    y = np.asarray(y, int)
    groups = np.asarray(groups, str)
    if not np.array_equal(ca_fold, fold_id):
        raise AssertionError("CA and nested models used different outer folds")

    x = frame.assign(molar=frame["niche_icm"].eq("molar").astype(int))[COMPACT_FEATURES]
    if EXCLUDED.intersection(x.columns):
        raise AssertionError("Future outcome leaked into compact feature set")
    n_folds = namespace["safe_group_splits"](y, groups, 3)
    outer = StratifiedGroupKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    compact = np.full(len(y), np.nan)
    fold_prior = np.full(len(y), np.nan)
    assignments = np.zeros(len(y), dtype=int)
    audit_rows = []
    for fold, (tr, te) in enumerate(outer.split(x, y, groups)):
        assert_disjoint(groups[tr], groups[te])
        if not np.array_equal(np.flatnonzero(fold_id == fold), te):
            raise AssertionError(f"Original fold assignment mismatch at fold {fold}")
        assignments[te] += 1
        # Jeffreys-smoothed prior learned from the training children only.
        fold_prior[te] = (np.sum(y[tr]) + .5) / (len(tr) + 1)
        inner_n = namespace["safe_group_splits"](y[tr], groups[tr], 2)
        inner = StratifiedGroupKFold(
            n_splits=inner_n, shuffle=True, random_state=seed + 100 + fold,
        )
        for inner_tr, inner_val in inner.split(x.iloc[tr], y[tr], groups[tr]):
            assert_disjoint(groups[tr][inner_tr], groups[tr][inner_val])
        pipe = Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(penalty="l2", solver="liblinear", max_iter=5000)),
        ])
        search = GridSearchCV(
            pipe, {"clf__C": [.01, .1, 1.0, 10.0]},
            scoring="average_precision", cv=inner, n_jobs=1, error_score="raise",
        )
        search.fit(x.iloc[tr], y[tr], groups=groups[tr])
        positive_index = np.flatnonzero(search.best_estimator_.classes_ == 1)
        if len(positive_index) != 1:
            raise AssertionError("Positive class is missing")
        compact[te] = search.predict_proba(x.iloc[te])[:, int(positive_index[0])]
        audit_rows.append({
            "fold": fold, "children_train": len(np.unique(groups[tr])),
            "children_test": len(np.unique(groups[te])), "rows_train": len(tr),
            "rows_test": len(te), "events_train": int(sum(y[tr])),
            "events_test": int(sum(y[te])), "prior_train_only": float(fold_prior[te][0]),
            "compact_best_C": search.best_params_["clf__C"],
            "train_test_child_overlap": len(set(groups[tr]) & set(groups[te])),
            "inner_folds": inner_n,
        })
    if not np.all(assignments == 1) or not np.isfinite(compact).all():
        raise AssertionError("Incomplete or repeated OOF assignments")

    preds = {
        "fold_prior": fold_prior,
        "CA_rule_original": np.asarray(ca_pred),
        "clinical_original": np.asarray(original["clinical"]),
        "micro_original": np.asarray(original["micro"]),
        "combined_original": np.asarray(original["combined"]),
        "clinical_compact_prespecified": compact,
    }
    metrics = pd.DataFrame([metric_row(name, y, p) for name, p in preds.items()])
    ci = cluster_bootstrap(y, groups, preds, repeats, seed + 271)
    rows = frame[["child_id", "transition_id", "progression_event"]].copy()
    rows["fold"] = fold_id
    for name, p in preds.items():
        rows[name] = p
    checks = pd.DataFrame([
        {"check": "outer_child_disjoint", "pass": all(r["train_test_child_overlap"] == 0 for r in audit_rows)},
        {"check": "each_OOF_row_once", "pass": bool(np.all(assignments == 1))},
        {"check": "all_predictions_finite", "pass": all(np.isfinite(p).all() for p in preds.values())},
        {"check": "positive_class_named", "pass": True},
        {"check": "future_columns_excluded", "pass": not bool(EXCLUDED.intersection(x.columns))},
        {"check": "duplicate_odontogram_rejected", "pass": test_duplicate_rejected(namespace)},
        {"check": "overlap_guard_detects_mutation", "pass": test_group_overlap_guard()},
    ])
    if not checks["pass"].all():
        raise AssertionError("Audit test failed: " + checks.to_json(orient="records"))

    metrics.to_csv(HERE / "synthetic_metrics.csv", index=False)
    ci.to_csv(HERE / "synthetic_cluster_ci.csv", index=False)
    pd.DataFrame(audit_rows).to_csv(HERE / "synthetic_fold_audit.csv", index=False)
    rows.to_csv(HERE / "synthetic_oof_predictions.csv", index=False)
    checks.to_csv(HERE / "audit_checks.csv", index=False)
    summary = {
        "profile": "synthetic_CI_SMOKE",
        "seed": seed,
        "children": int(len(np.unique(groups))),
        "transitions": int(len(y)), "events": int(sum(y)),
        "event_prevalence": float(np.mean(y)),
        "outer_folds": n_folds, "inner_folds": 2,
        "cluster_bootstraps_requested": repeats,
        "cluster_bootstrap_note": "Uncertainty conditional on OOF predictions; models were not refitted.",
        "notebook_sha256": hashlib.sha256(NOTEBOOK.read_bytes()).hexdigest(),
        "ca_original_metrics": ca_metrics,
        "original_fold_rows": original_folds.to_dict(orient="records"),
    }
    (HERE / "synthetic_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return {"metrics": metrics, "ci": ci, "checks": checks, "summary": summary}


def test_duplicate_rejected(namespace: dict) -> bool:
    item = {"patient_id": "P", "visit_id": 1, "tooth_fdi": "55", "state": "H"}
    try:
        namespace["build_odontogram"]([item, item])
    except AssertionError:
        return True
    return False


def test_group_overlap_guard() -> bool:
    try:
        assert_disjoint(["child_1"], ["child_1"])
    except AssertionError:
        return True
    return False


def run_real_clinical(namespace: dict) -> dict:
    """Reproduce cohort reconstruction only; no real-data model is evaluated."""
    target = HERE / "Table_S1.xlsx"
    if not target.exists():
        response = requests.get(S1_URL, timeout=120)
        response.raise_for_status()
        target.write_bytes(response.content)
    metadata = pd.read_excel(target, sheet_name="all_metadata")
    metadata.columns = [str(c).strip() for c in metadata.columns]
    tooth_map, composite, clean = namespace["clean_single_tooth"](metadata)
    transitions, one, onset = namespace["build_transitions"](clean)
    observed = {
        "metadata_rows": len(metadata),
        "children": metadata["HostID"].nunique(),
        "composite_T5161": len(composite),
        "single_tooth_rows": len(clean),
        "all_observed_transitions": len(transitions),
        "one_step_transitions": len(one),
        "H_to_H": int(one["transition_class"].eq("H->H").sum()),
        "H_to_C": int(one["transition_class"].eq("H->C").sum()),
        "C_to_C": int(one["transition_class"].eq("C->C").sum()),
        "C_to_H": int(one["transition_class"].eq("C->H").sum()),
        "onset_rows": len(onset),
    }
    expected = namespace["EXPECTED_COUNTS"]
    checks = {name: observed[name] == val for name, val in expected.items()}
    report = {
        "source_url": S1_URL,
        "table_s1_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "observed": observed,
        "notebook_expected": expected,
        "all_counts_match": all(checks.values()),
        "count_checks": checks,
        "model_metrics_calculated": False,
        "qiita_join_verified": False,
    }
    (HERE / "real_clinical_reproduction.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstraps", type=int, default=1000)
    parser.add_argument("--real-clinical", action="store_true")
    args = parser.parse_args()
    HERE.mkdir(parents=True, exist_ok=True)
    namespace = notebook_namespace()
    synthetic = run_synthetic(namespace, args.bootstraps)
    print(synthetic["metrics"].to_string(index=False))
    print("\nChecks:", synthetic["checks"]["pass"].sum(), "of", len(synthetic["checks"]))
    if args.real_clinical:
        clinical = run_real_clinical(namespace)
        print("Real clinical cohort:", json.dumps(clinical["observed"], ensure_ascii=False))
        print("Count reconstruction matches original:", clinical["all_counts_match"])


if __name__ == "__main__":
    main()
