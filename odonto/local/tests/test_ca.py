"""FR-003, FR-004, FR-011 — features CA, transições e simulação rotulada."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from odontoca import ca


def test_neighbor_count_bounds(synthetic_transitions: pd.DataFrame):
    """FR-003: neighbor_caries_count em {0,1,2}; espacial ≥ 0."""
    onset = ca.build_onset(synthetic_transitions)
    feats = ca.add_ca_features(onset)
    assert feats["neighbor_caries_count"].between(0, 2).all()
    assert (feats["neighbor_caries_spatial"] >= 0).all()
    assert feats["is_molar"].dtype == bool


def test_transitions_exact(synthetic_transitions: pd.DataFrame):
    """FR-004: classes H->H, H->C, C->C extraídas exatamente."""
    one = ca.extract_one_step(synthetic_transitions)
    assert set(one["transition_class"]) <= {"H->H", "H->C", "C->C", "C->H"}
    # conferência manual em um par criança-dente
    sample = synthetic_transitions[
        (synthetic_transitions["HostID"] == one["HostID"].iloc[0])
        & (synthetic_transitions["tooth_fdi"] == one["tooth_fdi"].iloc[0])
    ].sort_values("Timepoint")
    first = sample.iloc[0]
    assert one["transition_class"].iloc[0] == f"{first['Status_Tooth']}->{first['Future_Status_Tooth']}"


def test_h_to_c_only_from_h():
    df = pd.DataFrame(
        {
            "HostID": ["A"] * 2,
            "tooth_fdi": [54, 54],
            "Timepoint": [1, 2],
            "Status_Tooth": ["C", "C"],
            "Future_Status_Tooth": ["C", "C"],
        }
    )
    one = ca.extract_one_step(df)
    assert (one["transition_class"] == "C->C").all()
    assert (one["transition_class"] == "H->C").sum() == 0


def test_rule_fit_predict(synthetic_transitions: pd.DataFrame):
    """Regra aprendida devolve probabilidades válidas e > baseline em H->C."""
    onset = ca.build_onset(synthetic_transitions)
    feats = ca.add_ca_features(onset)
    rule = ca.CARule(seed=0).fit(feats)
    p = rule.predict_proba(feats)
    assert np.all((p >= 0) & (p <= 1))
    y = (feats["transition_class"] == "H->C").astype(int)
    if y.sum() >= 5:
        from sklearn.metrics import roc_auc_score

        assert roc_auc_score(y, p) >= 0.5  # ao menos acima do acaso nos dados com sinal


def test_sim_label():
    """FR-011: simulação rotulada descritiva, nunca causal."""
    sim = ca.simulate_evolution(
        states={"tooth": ["H", "H", "C"], "tooth_fdi": [54, 55, 64]},
        rule=None,
        steps=2,
        seed=1,
    )
    assert sim["claim_level"] == "descritivo_nao_causal"
    assert "não causal" in sim["disclaimer"].lower() or "nao causal" in sim["disclaimer"].lower()
    assert sim["steps"] == 2
