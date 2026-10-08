"""Integration gate: portable corrected Colab cell matches local analysis."""

import json
from pathlib import Path

from build_calibrated_colab_addendum import portable_code
from real_clinical_prediction import (
    BOOTSTRAPS, FEATURE_SETS, FORBIDDEN, SEED,
    build_pipeline, interval, source_frame,
)
from reproduce_evidence import fit_calibration


ASSETS = Path(__file__).resolve().parent
scope = {
    "__name__": "odonto_colab_test",
    "BOOTSTRAPS": BOOTSTRAPS, "FEATURE_SETS": FEATURE_SETS,
    "FORBIDDEN": FORBIDDEN, "SEED": SEED,
    "build_pipeline": build_pipeline, "interval": interval,
    "source_frame": source_frame, "fit_calibration": fit_calibration,
}
exec(portable_code(), scope)
local = json.loads((ASSETS / "calibrated_clinical_internal_validation_corrected_sklearn190.json").read_text())
portable = json.loads(Path("/tmp/odonto_colab_calibrated/calibrated_clinical_internal_validation_corrected_sklearn190.json").read_text())
assert portable["split_policy"] == "corrected_permuted_groups"
assert (portable["analysis_rows"], portable["analysis_events"], portable["analysis_children"]) == (996, 83, 81)
for name in FEATURE_SETS:
    for method in ("uncalibrated", "intercept_only", "intercept_and_slope"):
        for metric in ("pr_auc", "roc_auc", "brier", "log_loss"):
            assert abs(portable["metrics"][name][method][metric] - local["metrics"][name][method][metric]) < 1e-10
print("PORTABLE_CALIBRATED_COLAB_PASS")
