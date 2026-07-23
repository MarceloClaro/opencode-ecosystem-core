# -*- coding: utf-8 -*-
"""Ponto de entrada seguro para simulações com gêmeo digital obrigatório."""
from __future__ import annotations

from typing import Any, Dict, Optional

from skills.medico_virtual_supremo.digital_twin import (
    MedicalDigitalTwinEngine,
    attach_digital_twin_to_simulation,
)
from skills.medico_virtual_supremo.skill import MedicoVirtualSupremoSkill


def analisar_simulacao(
    request: str,
    *,
    patient: Optional[Dict[str, Any]] = None,
    clinical_data: Optional[Dict[str, Any]] = None,
    engine: Optional[MedicalDigitalTwinEngine] = None,
) -> Dict[str, Any]:
    """Executa caso fictício e sempre anexa um gêmeo digital auditável.

    Esta função é o ponto de entrada canônico para treinamento e pesquisa por
    simulação. Entradas que representem pessoa real devem usar outro modo e não
    recebem trajetórias preditivas.
    """
    patient = patient or {}
    clinical_data = clinical_data or {}
    result = MedicoVirtualSupremoSkill().analisar(
        modo="simulation",
        request=request,
        patient=patient,
        clinical_data=clinical_data,
    )
    return attach_digital_twin_to_simulation(
        result,
        request=request,
        patient=patient,
        clinical_data=clinical_data,
        engine=engine,
    )


__all__ = ["analisar_simulacao"]
