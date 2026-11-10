"""R1135 — política de gates revisada para PEC, ZNE, layouts e cortes.

Os gates antigos eram heurísticos e alguns confundiam métricas. Esta política
mantém o bloqueio por padrão e exige evidência declarada. Não executa
hardware nem mede taxas.
"""
from __future__ import annotations

LIMITS = (
    "Política offline e fail-closed. Aprovar um gate aqui não executa hardware; "
    "apenas declara quais evidências seriam necessárias. Nenhuma taxa foi medida."
)


def pec_gate(
    *,
    gspn_model_validated: bool,
    heldout_error: float | None,
    sampling_overhead: float | None,
    max_error: float = 0.01,
    max_overhead: float = 10.0,
) -> dict:
    reasons = []
    if not gspn_model_validated:
        reasons.append("modelo GSPN do gate set não validado")
    if heldout_error is None or heldout_error > max_error:
        reasons.append("erro em dados held-out ausente ou acima do limite")
    if sampling_overhead is None or sampling_overhead > max_overhead:
        reasons.append("overhead de amostragem ausente ou acima do limite")
    return {
        "gate": "PEC_2Q",
        "allowed": not reasons,
        "reasons": reasons,
        "route": "GSPN/MLCB + gauge optimization",
        "cuts_identified_required": False,
        "limits": LIMITS,
    }


def zne_gate(
    *,
    lre_configurations: int,
    min_configurations: int = 9,
    residual: float | None,
    max_residual: float = 0.005,
    heldout_stable: bool = False,
) -> dict:
    reasons = []
    if lre_configurations < min_configurations:
        reasons.append("configurações LRE insuficientes")
    if residual is None or residual > max_residual:
        reasons.append("resíduo do modelo LRE ausente ou acima do limite")
    if not heldout_stable:
        reasons.append("estimativa LRE não estável em held-out")
    return {
        "gate": "ZNE_LRE",
        "allowed": not reasons,
        "reasons": reasons,
        "monotonic_global_required": False,
        "limits": LIMITS,
    }


def layout_gate(
    *,
    n_pairs: int,
    n_required: int,
    randomized: bool,
    r1: float | None,
    r1_max: float = 0.05,
    drift_resolved: bool = False,
    effect: float | None,
    min_effect: float = 0.01,
) -> dict:
    reasons = []
    if n_pairs < n_required:
        reasons.append("n de pares abaixo do pré-registro")
    if not randomized:
        reasons.append("pares diferentes sem randomização")
    if r1 is None or r1 > r1_max:
        reasons.append("r1 físico ausente ou acima de 0,05")
    if not drift_resolved:
        reasons.append("drift não resolvido")
    if effect is None or abs(effect) < min_effect:
        reasons.append("efeito de layout ausente ou abaixo de 0,01")
    return {
        "gate": "LAYOUT_PAIRED",
        "allowed": not reasons,
        "reasons": reasons,
        "r1_is_covariate": True,
        "limits": LIMITS,
    }


def cut_gate(
    *,
    gspn_self_consistent: bool,
    mlcb_applied: bool,
    direct_identification: bool = False,
) -> dict:
    reasons = []
    if not gspn_self_consistent:
        reasons.append("aprendizagem autoconsistente do gate set ausente")
    if not mlcb_applied:
        reasons.append("MLCB não aplicado")
    return {
        "gate": "TWO_CUTS_GAUGE",
        "allowed": not reasons,
        "reasons": reasons,
        "identified": bool(direct_identification),
        "note": (
            "As 2 funções de corte são tratadas como gauge; o gate permite "
            "PEC via GSPN/MLCB, não identificação direta."
        ),
        "limits": LIMITS,
    }


def evaluate(evidence: dict) -> dict:
    evidence = evidence or {}
    pec = {
        "gspn_model_validated": False,
        "heldout_error": None,
        "sampling_overhead": None,
    }
    pec.update(evidence.get("pec_2q", {}))
    zne = {
        "lre_configurations": 0,
        "residual": None,
        "heldout_stable": False,
    }
    zne.update(evidence.get("zne", {}))
    layout = {
        "n_pairs": 0,
        "n_required": 1,
        "randomized": False,
        "r1": None,
        "drift_resolved": False,
        "effect": None,
    }
    layout.update(evidence.get("layout", {}))
    cuts = {
        "gspn_self_consistent": False,
        "mlcb_applied": False,
    }
    cuts.update(evidence.get("cuts", {}))
    return {
        "pec_2q": pec_gate(**pec),
        "zne": zne_gate(**zne),
        "layout": layout_gate(**layout),
        "cuts": cut_gate(**cuts),
        "hardware_executed": False,
        "rates_measured": False,
        "limits": LIMITS,
    }
