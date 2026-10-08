"""Integration gate for the portable Colab clinical analysis."""

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "manuscript_assets"
original = json.loads((ROOT / "OdontoCA_v1_3_2_FULL_RESEARCH_COM_IMAGEM_FLUXOGRAMA_EXECUTED (3).ipynb").read_text())
upper = ["T55", "T54", "T53", "T52", "T51", "T61", "T62", "T63", "T64", "T65"]
lower = ["T85", "T84", "T83", "T82", "T81", "T71", "T72", "T73", "T74", "T75"]
scope = {"pd": pd, "np": np, "ARCHES": {"upper": upper, "lower": lower}, "__name__": "__main__"}
exec("".join(original["cells"][13]["source"]), scope)
exec((ASSETS / "colab_clinical_addendum.py").read_text(), scope)

local = json.loads((ASSETS / "real_clinical_internal_validation.json").read_text())
portable = json.loads(Path("/tmp/odonto_colab_addendum/real_clinical_internal_validation.json").read_text())
assert portable["analysis_status"] == "EXPLORATORY_INTERNAL_VALIDATION_ONLY"
assert (portable["analysis_rows"], portable["analysis_events"], portable["analysis_children"]) == (996, 83, 81)
assert portable["child_disjoint_outer_folds"]
for model in ("clinical_minimal", "clinical_spatial"):
    for metric in ("pr_auc", "roc_auc", "brier", "calibration_slope"):
        assert abs(portable["metrics"][model][metric] - local["metrics"][model][metric]) < 1e-10
print("PORTABLE_COLAB_ADDENDUM_PASS")
