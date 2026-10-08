"""Focused tests for train-only calibration of grouped predictions."""

import numpy as np
from scipy.special import expit, logit
from sklearn.model_selection import StratifiedGroupKFold

from calibrated_clinical_prediction import apply_recalibration, corrected_group_splits, fit_recalibrators


def test_intercept_recalibration_corrects_constant_log_odds_shift():
    p = np.tile(np.array([0.08, 0.18, 0.35, 0.60]), 250)
    rng = np.random.default_rng(11)
    y = rng.binomial(1, expit(logit(p) - 0.45))
    fitted = fit_recalibrators(y, p)
    q = apply_recalibration(p, fitted["intercept_only"])
    assert abs(q.mean() - y.mean()) < 1e-5
    assert np.all(np.diff(q[:4]) > 0)


def test_recalibration_does_not_change_input_predictions():
    p = np.array([0.04, 0.15, 0.3, 0.8] * 100)
    before = p.copy()
    y = np.tile(np.array([0, 0, 1, 1]), 100)
    fitted = fit_recalibrators(y, p)
    for method in ("intercept_only", "intercept_and_slope"):
        q = apply_recalibration(p, fitted[method])
        assert np.isfinite(q).all() and ((q > 0) & (q < 1)).all()
    assert np.array_equal(p, before)


def test_corrected_group_split_matches_fixed_sklearn_implementation():
    groups = np.repeat(np.arange(30), 4)
    y = np.tile(np.array([0, 0, 0, 1]), 30)
    x = np.zeros((len(y), 1))
    expected = list(StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=17).split(x, y, groups))
    observed = corrected_group_splits(x, y, groups, n_splits=5, seed=17)
    for (_, e), (_, o) in zip(expected, observed):
        assert np.array_equal(e, o)
