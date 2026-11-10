"""R1134 — auditoria de gauge e rota para PEC 2q / funções de corte.

O desenho de 13 funções é invariante às direções de corte, mas as 15
fidelidades individuais não são. A literatura de 2026 mostra que, com
aprendizagem autoconsistente do gate set, o gauge não deve bloquear
observáveis mitigados; a rota é GSPN/MLCB, não identificar as 2 funções de
corte isoladamente. Nada aqui executa hardware.
"""
from __future__ import annotations

import numpy as np

from .cb_learnability import pattern_graph
from .cb_rank_bounds import anticommutation_matrix
from .interleaved_cb import PAULIS_2Q, design_matrix

LIMITS = (
    "Auditoria offline. A invariância vale para as 13 funções do desenho; "
    "não prova invariância de PEC para qualquer observável. A rota GSPN/MLCB "
    "exige implementação, dados e validação; as 2 funções de corte não foram "
    "medidas."
)
SOURCES = {
    "gspn": {
        "title": "Efficient self-consistent learning of gate set Pauli noise",
        "doi": "10.1103/1pnv-t9px",
        "year": 2026,
    },
    "mlcb": {
        "title": "Multilayer cycle benchmarking for high-accuracy error characterization",
        "doi": "10.1103/4hbl-hpl3",
        "year": 2026,
    },
    "disambiguating": {
        "title": "Disambiguating Pauli noise in quantum computers",
        "doi": "10.1103/69wc-gzl6",
        "year": 2026,
    },
}


def cut_invariance(rates: dict, *, step: float = 1e-4) -> dict:
    if set(rates) != set(PAULIS_2Q):
        raise ValueError("taxas devem cobrir os 15 Paulis")
    if step <= 0:
        raise ValueError("step deve ser positivo")
    graph = pattern_graph("cz")
    vector = np.array(
        [graph["cut_basis"][0][label] for label in PAULIS_2Q], dtype=float
    )
    norm = np.linalg.norm(vector)
    if norm == 0:
        raise ValueError("vetor de corte nulo")
    unit = vector / norm
    gamma = np.array([rates[label] for label in PAULIS_2Q], dtype=float)
    shifted = gamma + step * unit
    if np.any(shifted < 0):
        shifted = gamma - step * unit
    if np.any(shifted < 0):
        raise ValueError("passo grande demais para manter taxas não negativas")
    design = design_matrix()
    before = design @ gamma
    after = design @ shifted
    learnable_change = float(np.max(np.abs(after - before)))
    full = anticommutation_matrix()
    fidelities = np.exp(-2.0 * (full @ gamma))
    shifted_fidelities = np.exp(-2.0 * (full @ shifted))
    fidelity_change = float(np.max(np.abs(shifted_fidelities - fidelities)))
    changed = int(np.sum(np.abs(shifted_fidelities - fidelities) > 1e-12))
    return {
        "step": float(step),
        "learnable_change": learnable_change,
        "fidelity_change": fidelity_change,
        "changed_fidelities": changed,
        "invariant_learnable": bool(learnable_change < 1e-12),
        "gauge_changes_full_channel": bool(fidelity_change > 1e-12),
        "note": (
            "As 13 funções não mudam; as 15 fidelidades individuais mudam. "
            "Isso é gauge, não erro numérico."
        ),
    }


def pec_readiness() -> dict:
    return {
        "direct_15_rate_pec_allowed": False,
        "reason": (
            "2 funções de corte não são identificadas pelo CB; a matriz D "
            "completa tem posto 15, mas o desenho SPAM-robusto aprende 13."
        ),
        "route": "gate set Pauli noise learning (GSPN) + MLCB + gauge optimization",
        "sources": SOURCES,
        "requirements": [
            "modelo do gate set incluindo SPAM, 1q e CZ",
            "aprendizagem autoconsistente e ansatz declarado",
            "otimização de gauge para o observável/overhead",
            "validação fora do conjunto de treino",
            "pré-registro e autorização antes de hardware",
        ],
        "not_claimed": [
            "que as 2 funções de corte tenham sido medidas",
            "que PEC 2q esteja desbloqueado",
            "que GSPN/MLCB tenham sido executados no Baihua",
        ],
    }


def audit(rates: dict | None = None, *, step: float = 1e-4) -> dict:
    if rates is None:
        rates = {label: 0.002 for label in PAULIS_2Q}
    return {
        "schema_version": 1,
        "gauge": cut_invariance(rates, step=step),
        "pec": pec_readiness(),
        "hardware_executed": False,
        "rates_measured": False,
        "limits": LIMITS,
    }
