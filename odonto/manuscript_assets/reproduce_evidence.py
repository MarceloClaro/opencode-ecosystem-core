"""Reproduce auditable OdontoCA evidence without redistributing source records.

Run from the odonto directory: python3 manuscript_assets/reproduce_evidence.py
The published clinical supplement is cached in /tmp and never copied into the
manuscript directory. This script reports clinical cohort counts separately
from predictive performance on synthetic records.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from tempfile import gettempdir

import numpy as np
import pandas as pd
import requests
import scipy
import sklearn
from scipy.optimize import minimize, minimize_scalar
from scipy.special import expit, logit
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score


ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "OdontoCA_v1_3_2_FULL_RESEARCH_COM_IMAGEM_FLUXOGRAMA_EXECUTED (3).ipynb"
OUTPUT = ROOT / "manuscript_assets" / "evidence_v2.json"
SOURCE_URL = (
    "https://raw.githubusercontent.com/HuangShiLab/Single-tooth-ECC/"
    "e5868fe5664460c7aac1c5b6d7980776ad26b29c/"
    "Figures_and_Tables_in_Manuscript/Table_S1.xlsx"
)
SOURCE_COMMIT = "e5868fe5664460c7aac1c5b6d7980776ad26b29c"
SOURCE_SHA256 = "b7819fee81efbe2e227b7700c3cd86ce8bc6f7fe6f49da6214f4107d099184fa"


def clinical_reproduction(nb: dict) -> dict:
    path = Path(gettempdir()) / "OdontoCA_Table_S1_source.xlsx"
    if not path.exists():
        response = requests.get(SOURCE_URL, timeout=90)
        response.raise_for_status()
        path.write_bytes(response.content)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise RuntimeError(f"Clinical source hash changed: {digest}")

    meta = pd.read_excel(path, sheet_name="all_metadata")
    meta.columns = [str(col).strip() for col in meta.columns]
    upper = ["T55", "T54", "T53", "T52", "T51", "T61", "T62", "T63", "T64", "T65"]
    lower = ["T85", "T84", "T83", "T82", "T81", "T71", "T72", "T73", "T74", "T75"]
    scope = {"pd": pd, "np": np, "ARCHES": {"upper": upper, "lower": lower}}
    exec("".join(nb["cells"][13]["source"]), scope)
    _, composite, clean = scope["clean_single_tooth"](meta)
    transitions, consecutive, onset = scope["build_transitions"](clean)
    observed = {
        "metadata_rows": len(meta),
        "children": int(meta["HostID"].nunique()),
        "composite_T5161": len(composite),
        "single_tooth_rows": len(clean),
        "all_observed_transitions": len(transitions),
        "one_step_transitions": len(consecutive),
        "H_to_H": int(consecutive["transition_class"].eq("H->H").sum()),
        "H_to_C": int(consecutive["transition_class"].eq("H->C").sum()),
        "C_to_C": int(consecutive["transition_class"].eq("C->C").sum()),
        "C_to_H": int(consecutive["transition_class"].eq("C->H").sum()),
        "onset_rows": len(onset),
    }
    expected = scope["EXPECTED_COUNTS"]
    checks = {key: bool(observed[key] == value) for key, value in expected.items()}
    if not all(checks.values()):
        raise AssertionError(f"Clinical reproduction differs: {checks}")
    return {
        "status": "REPRODUCED_COUNTS_ONLY",
        "source_url": SOURCE_URL,
        "source_commit": SOURCE_COMMIT,
        "sha256": digest,
        "sheet": "all_metadata",
        "expected": expected,
        "observed": observed,
        "checks": checks,
        "onset_children": int(onset["child_id"].nunique()),
        "event_children": int(onset.loc[onset["progression_event"].eq(1), "child_id"].nunique()),
        "onset_event_fraction": float(onset["progression_event"].mean()),
        "scope_note": "No predictive model was fitted to these real clinical records.",
    }


def fit_calibration(y: np.ndarray, p: np.ndarray) -> dict:
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


def synthetic_reproduction(nb: dict, bootstraps: int = 1000) -> dict:
    scope = {"__name__": "__main__", "display": lambda *_args, **_kwargs: None}
    # Execute only the original offline CI path; never activate the real
    # microbiome, image, external validation or network-enabled profiles.
    cells = [5, 6, 10, 12, 13, 15, 17, 19, 20, 22, 24, 25]
    for index in cells:
        exec("".join(nb["cells"][index]["source"]), scope)
    y = np.asarray(scope["S_Y"], dtype=int)
    groups = np.asarray(scope["S_GROUPS"], dtype=str)
    fold = np.asarray(scope["S_FOLD"], dtype=int)
    predictions = {key: np.asarray(value, float) for key, value in scope["S_PREDS"].items()}
    predictions["ca_rule"] = np.asarray(scope["S_CA_PRED"], float)
    if not all(len(p) == len(y) and np.isfinite(p).all() for p in predictions.values()):
        raise AssertionError("Incomplete or nonfinite out-of-fold predictions")
    if pd.DataFrame({"child": groups, "fold": fold}).groupby("child")["fold"].nunique().max() != 1:
        raise AssertionError("Patient leakage across outer folds")
    if np.any((y != 0) & (y != 1)):
        raise AssertionError("Unexpected outcome labels")

    metrics = {}
    for name, p in predictions.items():
        metrics[name] = {
            "pr_auc": float(average_precision_score(y, p)),
            "roc_auc": float(roc_auc_score(y, p)),
            "brier": float(brier_score_loss(y, p)),
            "log_loss": float(log_loss(y, np.clip(p, 1e-6, 1 - 1e-6))),
            **fit_calibration(y, p),
        }

    children = np.unique(groups)
    child_rows = {child: np.flatnonzero(groups == child) for child in children}
    rng = np.random.default_rng(20260930)
    draws = {name: {"pr_auc": [], "roc_auc": [], "brier": []} for name in predictions}
    differences = {"pr_auc": [], "roc_auc": [], "brier": []}
    valid = 0
    for _ in range(bootstraps):
        sampled = rng.choice(children, size=len(children), replace=True)
        index = np.concatenate([child_rows[child] for child in sampled])
        yy = y[index]
        if len(np.unique(yy)) != 2:
            continue
        valid += 1
        for name, p in predictions.items():
            pp = p[index]
            draws[name]["pr_auc"].append(float(average_precision_score(yy, pp)))
            draws[name]["roc_auc"].append(float(roc_auc_score(yy, pp)))
            draws[name]["brier"].append(float(brier_score_loss(yy, pp)))
        for metric in differences:
            differences[metric].append(draws["combined"][metric][-1] - draws["clinical"][metric][-1])

    for name in predictions:
        for metric, values in draws[name].items():
            metrics[name][metric + "_ci95"] = [float(v) for v in np.quantile(values, [0.025, 0.975])]
    delta = {
        metric: {
            "estimate": float(metrics["combined"][metric] - metrics["clinical"][metric]),
            "ci95": [float(v) for v in np.quantile(values, [0.025, 0.975])],
        }
        for metric, values in differences.items()
    }
    return {
        "status": "RERUN_SYNTHETIC_CI_SMOKE",
        "seed": int(scope["CFG"].SEED),
        "n_children": len(children),
        "n_transitions": len(y),
        "n_events": int(y.sum()),
        "event_fraction": float(y.mean()),
        "outer_folds": int(len(np.unique(fold))),
        "child_disjoint_outer_folds": True,
        "bootstrap_requested": bootstraps,
        "bootstrap_valid": valid,
        "metrics": metrics,
        "combined_minus_clinical": delta,
        "scope_note": "All predictive metrics and intervals are synthetic only; bootstrap intervals condition on the simulated records and fitted out-of-fold predictions.",
    }


def main() -> None:
    nb = json.loads(NOTEBOOK.read_text())
    result = {
        "source_notebook": NOTEBOOK.name,
        "source_notebook_sha256": hashlib.sha256(NOTEBOOK.read_bytes()).hexdigest(),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "clinical_reproduction": clinical_reproduction(nb),
        "synthetic_reproduction": synthetic_reproduction(nb),
        "real_microbiome_status": "NOT_RUN",
        "image_model_status": "NOT_RUN",
        "external_validation_status": "NOT_PERFORMED",
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(OUTPUT)
    print(json.dumps({
        "clinical": result["clinical_reproduction"]["observed"],
        "synthetic_n": result["synthetic_reproduction"]["n_transitions"],
        "synthetic_events": result["synthetic_reproduction"]["n_events"],
        "synthetic_metrics": result["synthetic_reproduction"]["metrics"],
        "synthetic_delta": result["synthetic_reproduction"]["combined_minus_clinical"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
