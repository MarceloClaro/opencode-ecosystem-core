"""Fixtures compartilhadas — SPEC-935-R898."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SOURCE_XLSX = (
    Path(__file__).resolve().parents[2]
    / "manuscript_assets" / "robust_audit" / "Table_S1.xlsx"
)


@pytest.fixture(scope="session")
def table_s1_path() -> Path:
    if not SOURCE_XLSX.exists():
        pytest.skip("Table_S1.xlsx ausente")
    return SOURCE_XLSX


@pytest.fixture()
def synthetic_transitions(seed: int = 20261015) -> pd.DataFrame:
    """Painel criança×dente×tempo sintético COM sinal realista de cárie.

    Molares decíduos ganham evento H->C com probabilidade maior; vizinhos com
    cárie aumentam o risco (sinal que o autômato celular deve capturar).
    """
    rng = np.random.default_rng(seed)
    molars = [54, 55, 64, 65, 74, 75, 84, 85]
    rows = []
    for child in range(1, 41):
        teeth = rng.choice([54, 55, 64, 65, 74, 75, 84, 85, 51, 61], size=6, replace=False)
        base_caries = rng.random() < 0.3
        for tooth in teeth:
            state = "C" if (base_caries and rng.random() < 0.5) else "H"
            for t in (1, 2, 3):
                nxt = state
                if state == "H":
                    risk = 0.08 + (0.20 if int(tooth) in molars else 0.0)
                    risk += 0.15 * sum(
                        1 for o in teeth if abs(int(o) - int(tooth)) <= 1 and rng.random() < 0.4
                    )
                    if rng.random() < risk:
                        nxt = "C"
                rows.append(
                    {
                        "HostID": f"CHILD_{child:02d}",
                        "tooth_fdi": int(tooth),
                        "Timepoint": t,
                        "Month": 6 * t,
                        "Status_Tooth": state,
                        "Future_Status_Tooth": nxt,
                        "niche": "Incisor" if int(tooth) % 10 <= 2 else "Molar",
                        "dmfs_host": int(rng.integers(0, 8)),
                    }
                )
                state = nxt
    return pd.DataFrame(rows)


@pytest.fixture()
def synthetic_binary(seed: int = 42) -> pd.DataFrame:
    """Dataset tabular binário com alvo detectável para CLI/predict."""
    rng = np.random.default_rng(seed)
    n = 400
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    p = 1 / (1 + np.exp(-(1.2 * x1 + 0.8 * x2 - 1.0)))
    return pd.DataFrame(
        {
            "patient_id": [f"P{i:04d}" for i in range(n)],
            "age": rng.integers(5, 70, n),
            "tooth_position": rng.choice([54, 55, 64, 65], n),
            "neighbor_caries_count": rng.integers(0, 3, n),
            "dmfs_host": rng.integers(0, 10, n),
            "caries": (rng.random(n) < p).astype(int),
        }
    )
