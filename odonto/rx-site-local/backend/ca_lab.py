"""Autômatos celulares REAIS (descritivos) — SPEC-935-R900 FR-008/FR-009.

Envolve ``odontoca.ca`` sem alterá-lo. Duas regras:
- ``prior``: heurística declarada (molar 0,12 / não-molar 0,04 + vizinhança);
- ``fitted``: ``CARule`` ajustado nas transições H→C reais do Table_S1.

NUNCA causal: o retorno traz ``claim_level = descritivo_nao_causal``.
"""
from __future__ import annotations

from typing import Any

from .paths import ensure_import_path

ensure_import_path()

PERMANENT_FDI = [f"{q}{n}" for q in ("1", "2", "3", "4") for n in range(1, 9)]
CLAIM_LEVEL = "descritivo_nao_causal"

_rule_cache: dict[str, Any] = {}


def build_states(n_teeth: int = 32) -> Any:
    """Cenário inicial: arco de ``n_teeth`` dentes saudáveis (H)."""
    import pandas as pd

    n_teeth = max(1, min(int(n_teeth), len(PERMANENT_FDI)))
    teeth = [int(t) for t in PERMANENT_FDI[:n_teeth]]
    return pd.DataFrame(
        {
            "tooth_fdi": teeth,
            "Status_Tooth": "H",
            "HostID": "SCENARIO",
            "Timepoint": 0,
            "dmfs_host": 0.0,
        }
    )


def fitted_rule():
    """``CARule`` ajustado nas transições H→C reais (cache por processo)."""
    if "rule" in _rule_cache:
        return _rule_cache["rule"]
    import numpy as np
    import pandas as pd
    from odontoca import ca as ca_mod, data as data_mod, train as train_mod
    from .paths import resolve_table_s1

    frame = data_mod.load_table_s1(resolve_table_s1())
    onset, _target = train_mod.prepare_onset_s1(frame)
    onset = onset.copy()
    # `Status_Tooth` é LEAK e foi removido; o subconjunto de risco é H por construção.
    onset["Status_Tooth"] = "H"
    if "dmfs_Host" in onset.columns:
        onset["dmfs_host"] = onset["dmfs_Host"]
    onset["Future_Status_Tooth"] = np.where(onset["caries_onset"].to_numpy() == 1, "C", "H")
    onset["transition_class"] = "H->" + onset["Future_Status_Tooth"].astype(str)
    feats = ca_mod.add_ca_features(onset)
    feats["Timepoint"] = pd.to_numeric(
        feats["Timepoint"].astype(str).str.extract(r"(\d+)")[0], errors="coerce"
    ).fillna(0)
    rule = ca_mod.CARule(seed=0).fit(feats)
    _rule_cache["rule"] = rule
    _rule_cache["n_events"] = int(onset["caries_onset"].sum())
    return rule


def simulate(
    *,
    steps: int = 3,
    seed: int = 0,
    n_teeth: int = 32,
    rule: str = "prior",
) -> dict[str, Any]:
    """Simulação descritiva H→C. ``rule`` ∈ {prior, fitted}."""
    from odontoca import ca as ca_mod

    steps = max(1, min(int(steps), 20))
    rule = "fitted" if str(rule).lower() in {"fitted", "fit", "aprendida"} else "prior"
    states = build_states(n_teeth)
    rule_obj = None
    if rule == "fitted":
        rule_obj = fitted_rule()
    result = ca_mod.simulate_evolution(states, rule=rule_obj, steps=steps, seed=int(seed))
    result.update(
        {
            "real": True,
            "mock": False,
            "rule": rule,
            "n_teeth": int(len(states)),
            "seed": int(seed),
            "evidence": (
                "regra ajustada no Table_S1 (transições H→C reais)"
                if rule == "fitted"
                else "regra heurística declarada (molar 0,12 / não-molar 0,04 + vizinhança)"
            ),
        }
    )
    return result


def demo() -> dict[str, Any]:
    """Cenário reprodutível para render inicial (seed fixo)."""
    return simulate(steps=3, seed=7, n_teeth=32, rule="prior")
