"""Autômato celular para progressão de cárie — SPEC-935-R898 §3.1.

Estados: H (saudável), C (cárie), F (restaurado), M (ausente).
A regra de transição é APRENDIDA dos dados (não imposta); a simulação é
DESCRITIVA e nunca causal (FR-011).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from . import topology as topo

STATES = ("H", "C", "F", "M")
CLAIM_LEVEL = "descritivo_nao_causal"
DISCLAIMER = (
    "Simulação descritiva de cenário — NÃO causal: não é evidência causal "
    "nem previsão clínica individual; revisão humana obrigatória."
)

FEATURE_COLS = [
    "neighbor_caries_count",
    "neighbor_caries_spatial",
    "is_molar",
    "dmfs_host",
    "Timepoint",
]


def extract_one_step(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona ``transition_class`` (H->H, H->C, C->C, C->H) — FR-004.

    Usa ``Status_Tooth`` → ``Future_Status_Tooth`` quando existir; caso
    contrário encadeia com o registro seguinte do mesmo dente/criança.
    """
    out = df.copy()
    if "Future_Status_Tooth" in out.columns:
        out["transition_class"] = (
            out["Status_Tooth"].astype(str) + "->" + out["Future_Status_Tooth"].astype(str)
        )
        return out
    out = out.sort_values(["HostID", "tooth_fdi", "Timepoint"])
    fut = out.groupby(["HostID", "tooth_fdi"])["Status_Tooth"].shift(-1)
    out["Future_Status_Tooth"] = fut
    out = out.dropna(subset=["Future_Status_Tooth"])
    out["transition_class"] = (
        out["Status_Tooth"].astype(str) + "->" + out["Future_Status_Tooth"].astype(str)
    )
    return out


def build_onset(df: pd.DataFrame) -> pd.DataFrame:
    """Painel one-step com marcação ``in_risk`` (Status == H) — FR-004."""
    one = extract_one_step(df)
    one["in_risk"] = one["Status_Tooth"].astype(str).eq("H")
    return one


def add_ca_features(df: pd.DataFrame, *, spatial_radius: float = 2.5) -> pd.DataFrame:
    """Features do autômato celular — FR-003.

    - ``neighbor_caries_count``: adjacentes de arco com cárie no mesmo
      momento (0..2).
    - ``neighbor_caries_spatial``: dentes com cárie dentro de ``spatial_radius``
      (usa X/Y/Z se disponíveis; fallback = features de arco).
    - ``is_molar``: subpopulacão de alto risco (achado do manuscrito).
    """
    out = df.copy()
    has_future = "Future_Status_Tooth" in out.columns
    if "transition_class" not in out.columns and has_future:
        out = extract_one_step(out)

    group_keys = [k for k in ("HostID", "Timepoint", "Month") if k in out.columns]
    time_key = "Timepoint" if "Timepoint" in out.columns else ("Month" if "Month" in out.columns else None)

    arc_counts: list[int] = []
    spatial_counts: list[int] = []
    has_xyz = all(c in out.columns for c in ("X", "Y", "Z"))
    tooth_col = "tooth_fdi" if "tooth_fdi" in out.columns else "Position_Tooth"

    if time_key is not None and tooth_col in out.columns:
        for _, grp in out.groupby(group_keys, dropna=False):
            status = {
                int(r[tooth_col]): str(r["Status_Tooth"])
                for _, r in grp.iterrows()
            }
            if has_xyz:
                coords = {
                    int(r[tooth_col]): (float(r["X"]), float(r["Y"]), float(r["Z"]))
                    for _, r in grp.iterrows()
                }
            else:
                coords = {}
            for _, r in grp.iterrows():
                t = int(r[tooth_col])
                arc_counts.append(topo.arc_caries_count(t, status))
                if has_xyz:
                    spatial_counts.append(
                        topo.spatial_caries_count(t, status, coords, spatial_radius)
                    )
        if not has_xyz:
            spatial_counts = list(arc_counts)
    else:
        # sem dimensão temporal: conta por ocorrência de C no dente
        status = {
            int(r[tooth_col]): str(r["Status_Tooth"])
            for _, r in out.iterrows()
        } if tooth_col in out.columns else {}
        arc_counts = [
            topo.arc_caries_count(int(r[tooth_col]), status)
            if tooth_col in out.columns else 0
            for _, r in out.iterrows()
        ]
        spatial_counts = list(arc_counts)

    out["neighbor_caries_count"] = np.asarray(arc_counts, dtype=int)
    out["neighbor_caries_spatial"] = np.asarray(spatial_counts, dtype=int)

    if tooth_col in out.columns:
        out["is_molar"] = out[tooth_col].map(lambda t: topo.is_molar(int(t)))
    else:
        out["is_molar"] = False

    if "neighbor_caries_count" not in out.columns:
        out["neighbor_caries_count"] = 0
    if not out["neighbor_caries_count"].between(0, 2).all():
        raise ValueError("neighbor_caries_count fora de 0..2")
    return out


@dataclass
class CARule:
    """Regra de transição H→C aprendida dos dados (logística / boosting)."""

    seed: int = 0
    model: Any = None
    features: list[str] = field(default_factory=list)

    def _design(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = []
        for c in FEATURE_COLS:
            if c in df.columns:
                cols.append(c)
        X = df[cols].copy()
        if "niche" in df.columns:
            dummies = pd.get_dummies(df["niche"].astype(str), prefix="niche", drop_first=True)
            X = pd.concat([X.reset_index(drop=True), dummies.reset_index(drop=True)], axis=1)
            cols += list(dummies.columns)
        X = X.astype(float).fillna(0.0)
        self.features = list(X.columns)
        return X

    def fit(self, df: pd.DataFrame) -> "CARule":
        if "transition_class" not in df.columns:
            df = extract_one_step(df)
        X = self._design(df)
        y = (df["transition_class"] == "H->C").astype(int).to_numpy()
        if len(np.unique(y)) < 2:
            # regime sem eventos: regra degenerada em constante da prevalência
            self.model = float(np.clip(y.mean(), 1e-4, 1 - 1e-4))
            return self
        from sklearn.linear_model import LogisticRegression

        self.model = LogisticRegression(max_iter=1000, random_state=self.seed)
        self.model.fit(X, y)
        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("CARule não ajustado: chame fit() primeiro")
        if isinstance(self.model, float):
            return np.full(len(df), self.model)
        X = self._design(df)
        X = X.reindex(columns=self.features, fill_value=0.0).astype(float).fillna(0.0)
        return self.model.predict_proba(X)[:, 1]


def simulate_evolution(
    states: pd.DataFrame | dict[str, Any],
    rule: CARule | None = None,
    steps: int = 1,
    seed: int = 0,
    risk_offset: float = 0.0,
) -> dict[str, Any]:
    """Evolução H→C por ``steps`` passos — FR-011 (descritiva, não causal)."""
    df = states.copy() if isinstance(states, pd.DataFrame) else pd.DataFrame(states)
    if "tooth_fdi" not in df.columns:
        raise ValueError("states precisa da coluna tooth_fdi")
    rng = np.random.default_rng(seed)
    frame = df.copy()
    if "Status_Tooth" not in frame.columns:
        frame["Status_Tooth"] = "H"
    if "HostID" not in frame.columns:
        frame["HostID"] = "SCENARIO"
    if "Timepoint" not in frame.columns:
        frame["Timepoint"] = 0
    history: list[dict[str, Any]] = []
    for step in range(1, steps + 1):
        frame["Timepoint"] = step
        feats = add_ca_features(frame)
        if rule is not None and rule.model is not None:
            p = rule.predict_proba(feats)
        else:
            base = np.where(feats["is_molar"].to_numpy(bool), 0.12, 0.04)
            p = base + risk_offset + 0.05 * feats["neighbor_caries_count"].to_numpy(float)
        for idx in frame.index:
            if str(frame.at[idx, "Status_Tooth"]) != "H":
                continue
            if rng.random() < float(np.clip(p[list(frame.index).index(idx)], 0, 1)):
                frame.at[idx, "Status_Tooth"] = "C"
                frame.at[idx, "Future_Status_Tooth"] = "C"
        history.append(
            {"step": step, "prevalence_caries": float((frame["Status_Tooth"] == "C").mean())}
        )
    return {
        "claim_level": CLAIM_LEVEL,
        "disclaimer": DISCLAIMER,
        "steps": steps,
        "history": history,
        "final": frame[["tooth_fdi", "Status_Tooth"]].to_dict("records"),
    }
