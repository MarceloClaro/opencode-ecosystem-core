# -*- coding: utf-8 -*-
"""
lock_final_model.py — Trava e exporta o modelo final para uso clínico
======================================================================
Contexto (SPEC-935-R645 / ciclo R645)
--------------------------------------
O manuscrito OdontoCA hoje e um estudo de desenvolvimento+validacao interna
exploratoria, sem modelo final. Para que ele possa ser enquadrado como
ESTUDO DE PREDICAO CLINICA e submetido a validacao externa, exige-se um
artefato de modelo travado, com hiperparametros escolhidos, recalibracao
encaixada e os metadados necessarios para inferencia independente.

ESCOLHA DO MODELO PRIMARIO (decisao registrada, nao.default)
----------------------------------------------------------
O primario e `clinical_minimal`. Razao: e o unico conjunto cujos preditores sao
todos plausivelmente disponiveis numa consulta de rotina de cárie da primeira
infancia (posicao dentaria, idade em meses, dmfs do hospedeiro, numero de
dentes adjacentes cariados). O conjunto `clinical_spatial` scored point estimate
superior (AUC 0.737 vs 0.686), porem o manuscrito declara que:
  (a) a superioridade NAO foi estabelecida (IC da diferenca inclui zero), e
  (b) os preditores espaciais derivados NAO foram reconstruidos e sua
      disponibilidade prospectiva exige verificacao independente.
Escolher o espacial por performance observada seria selecao data-driven e
elevaria o risco de viés (PROBAST+AI, dominio Analysis). Portanto o espacial e
exportado como candidato SECUNDARIO/exploratorio, nao como modelo primario.

ANTI-OVERCLAIM (obrigatorio)
---------------------------
As metricas deste script sao APPARENTES (resubstituicao) ou cross-fitted na
mesma coorte. NENHUMA delas e validacao externa. O script grava esse aviso no
model card. Desempenho clinicamente utilizavel permanece indeterminado ate
uma coorte externa independente (ver external_validation_protocol.md).
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV

sys.path.insert(0, str(Path(__file__).resolve().parent))

from calibrated_clinical_prediction import corrected_group_splits, fit_recalibrators
from real_clinical_prediction import (
    FEATURE_SETS,
    FORBIDDEN,
    SEED,
    build_pipeline,
    source_frame,
)

OUT = Path(__file__).resolve().parent
PRIMARY = "clinical_minimal"
SECONDARY = "clinical_spatial"
C_GRID = [0.01, 0.1, 1.0, 10.0]

# Trava fail-closed na coorte usada no manuscrito.
EXPECTED = {"rows": 996, "events": 83, "children": 81}
BUNDLE_PATH = OUT / "odontoca_clinical_model.joblib"
CARD_PATH = OUT / "odontoca_clinical_model_card.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cross_fitted_probabilities(frame, definition, chosen_c, y, groups):
    """OOF probabilities via grouped CV, child-disjoint, on the full cohort."""
    columns = definition["cat"] + definition["num"]
    oof = np.full(len(y), np.nan)
    for train, test in corrected_group_splits(frame, y, groups, n_splits=5, seed=SEED):
        if not set(groups[train]).isdisjoint(groups[test]):
            raise AssertionError("Child leakage in cross-fitting")
        model = build_pipeline(definition["cat"], definition["num"])
        model.set_params(model__C=chosen_c)
        model.fit(frame.iloc[train][columns], y[train])
        oof[test] = model.predict_proba(frame.iloc[test][columns])[:, 1]
    if np.isnan(oof).any():
        raise AssertionError("Cross-fitted probabilities incomplete")
    return oof


def select_c(frame, definition, y, groups):
    """Hyperparameter selection by grouped inner CV on average precision."""
    columns = definition["cat"] + definition["num"]
    splits = corrected_group_splits(frame, y, groups, n_splits=5, seed=SEED)
    search = GridSearchCV(
        build_pipeline(definition["cat"], definition["num"]),
        {"model__C": C_GRID},
        scoring="average_precision",
        cv=splits,
        n_jobs=1,
        refit=True,
        error_score="raise",
    )
    search.fit(frame[columns], y)
    return float(search.best_params_["model__C"]), [float(v) for v in search.cv_results_["mean_test_score"]]


def apparent_metrics(y, p):
    return {
        "average_precision": round(float(average_precision_score(y, p)), 6),
        "roc_auc": round(float(roc_auc_score(y, p)), 6),
        "brier": round(float(brier_score_loss(y, p)), 6),
        "log_loss": round(float(log_loss(y, p)), 6),
    }


def main() -> dict:
    frame, source = source_frame()
    y = frame["progression_event"].to_numpy(dtype=int)
    groups = frame["child_id"].astype(str).to_numpy()

    observed = {
        "rows": int(len(frame)),
        "events": int(y.sum()),
        "children": int(len(set(groups))),
    }
    if observed != EXPECTED:
        raise SystemExit(
            f"FAIL-CLOSED: coorte {observed} != manuscripto {EXPECTED}. "
            "Nao travar modelo sobre coorte divergente."
        )
    if any(FORBIDDEN.intersection(d["cat"] + d["num"]) for d in FEATURE_SETS.values()):
        raise SystemExit("FAIL-CLOSED: variavel de desfecho/futuro entrou no modelo")

    artifacts = {}
    for name in (PRIMARY, SECONDARY):
        definition = FEATURE_SETS[name]
        chosen_c, cv_scores = select_c(frame, definition, y, groups)
        oof_raw = cross_fitted_probabilities(frame, definition, chosen_c, y, groups)
        recal = fit_recalibrators(y, oof_raw)["intercept_and_slope"]

        columns = definition["cat"] + definition["num"]
        final = build_pipeline(definition["cat"], definition["num"])
        final.set_params(model__C=chosen_c)
        final.fit(frame[columns], y)
        p_apparent = final.predict_proba(frame[columns])[:, 1]

        artifacts[name] = {
            "definition": definition,
            "chosen_c": chosen_c,
            "cv_mean_average_precision_by_c": dict(zip(map(str, C_GRID), cv_scores)),
            "recalibration": recal,
            "final_pipeline": final,
            "oof_raw": oof_raw,
            "apparent": apparent_metrics(y, p_apparent),
        }

    primary = artifacts[PRIMARY]
    bundle = {
        "primary_model": PRIMARY,
        "role_note": (
            "clinical_minimal is primary because all its predictors are plausibly "
            "available at a routine visit; clinical_spatial superiority was not "
            "established and its derived predictors were not reconstructed."
        ),
        "feature_sets": {
            k: {"cat": v["cat"], "num": v["num"]} for k, v in FEATURE_SETS.items()
        },
        "selected_C": {k: v["chosen_c"] for k, v in artifacts.items()},
        "recalibration": {k: v["recalibration"] for k, v in artifacts.items()},
        "pipelines": {k: v["final_pipeline"] for k, v in artifacts.items()},
        "required_columns": {
            k: v["definition"]["cat"] + v["definition"]["num"] for k, v in artifacts.items()
        },
        "source": source,
        "seed": SEED,
        "locked_utc": datetime.now(timezone.utc).isoformat(),
        "versions": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "pandas": pd.__version__,
        },
    }
    joblib.dump(bundle, BUNDLE_PATH)

    from calibrated_clinical_prediction import apply_recalibration

    card = {
        "model_name": "OdontoCA clinical risk model (per-tooth, next recorded visit)",
        "primary_model": PRIMARY,
        "secondary_exploratory_model": SECONDARY,
        "cohort": observed,
        "event_prevalence": round(observed["events"] / observed["rows"], 6),
        "outcome": "progression_event: H->C at the next recorded consecutive visit (2-5 months)",
        "source_data": source,
        "seed": SEED,
        "versions": bundle["versions"],
        "models": {
            k: {
                "selected_C": v["chosen_c"],
                "cv_mean_average_precision_by_C": v["cv_mean_average_precision_by_c"],
                "features": FEATURE_SETS[k]["cat"] + FEATURE_SETS[k]["num"],
                "recalibration_intercept_and_slope": v["recalibration"],
                "apparent_metrics_OPTIMISTIC": v["apparent"],
                "cross_fitted_uncalibrated_metrics": apparent_metrics(y, v["oof_raw"]),
                "cross_fitted_recalibrated_metrics": apparent_metrics(
                    y, apply_recalibration(v["oof_raw"], v["recalibration"])
                ),
            }
            for k, v in artifacts.items()
        },
        "interpretation_warning": (
            "Apparent metrics are resubstitution and therefore optimistic. Cross-fitted "
            "metrics reuse the same 81 children as development. NEITHER is external "
            "validation. Clinical utility remains undetermined until an independent "
            "external cohort is scored with this locked artifact."
        ),
        "hyperparameter_selection_disclosure": (
            "C was selected ONCE on the full cohort by grouped CV average precision "
            f"(chosen C = {artifacts[PRIMARY]['chosen_c']}). The manuscript instead chose C "
            "inside each outer fold and therefore reports a stricter, non-inflated internal "
            "estimate. The cross-fitted AUC/AP in this card are consequently optimistic "
            "relative to the manuscript (0.753 vs 0.686 for the primary model). For "
            "performance reporting, cite the manuscript's fold-wise estimates, not this card."
        ),
        "performance_to_report": (
            f"Manuscript pooled out-of-fold estimate for {PRIMARY}: AUROC 0.686 "
            "(95% CI 0.618-0.754), average precision 0.166 (95% CI 0.120-0.246), "
            "Brier 0.0806 uncalibrated / 0.0745 after intercept-and-slope recalibration."
        ),
        "intended_use": (
            "Research use only. Not for clinical decision-making. Not a medical device. "
            "No decision threshold was pre-specified; the model must not be used to "
            "trigger treatment."
        ),
        "known_limitations": [
            "No external or temporal validation.",
            "No independent outcome adjudication.",
            "Only 83 outcome events; 20% events-per-parameter rule not assessable.",
            "Prediction horizon is the next recorded visit (2-5 months), not a fixed time.",
            "No fairness or subgroup performance analysis.",
            "No net-benefit / decision-curve analysis.",
        ],
        "artifact": {
            "path": BUNDLE_PATH.name,
            "sha256": sha256_file(BUNDLE_PATH),
            "size_bytes": BUNDLE_PATH.stat().st_size,
        },
    }
    CARD_PATH.write_text(json.dumps(card, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(
        {
            "cohort": observed,
            "primary_C": primary["chosen_c"],
            "primary_apparent_OPTIMISTIC": primary["apparent"],
            "primary_cross_fitted_recalibrated": card["models"][PRIMARY][
                "cross_fitted_recalibrated_metrics"
            ],
            "artifact_sha256": card["artifact"]["sha256"],
            "card": CARD_PATH.name,
        },
        indent=2,
        ensure_ascii=False,
    ))
    return card


if __name__ == "__main__":
    main()
