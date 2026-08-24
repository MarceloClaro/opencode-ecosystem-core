# -*- coding: utf-8 -*-
"""
Médico Virtual Supremo — Skill de Apoio Clínico Auditável v2.1

Skill do OpenCode Ecosystem para apoio à decisão clínica com pipeline
de raciocínio em 7 etapas, detecção de emergência, hipóteses diferenciais,
evidência rastreável e revisão humana obrigatória.

O ponto de entrada ``analisar_simulacao`` cria obrigatoriamente um gêmeo digital
fictício, auxiliado pelo MiroFish e auditado pelo Reversa.
"""

import os
import sys

_skill_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_skill_dir, "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from skills.medico_virtual_supremo.skill import (
    MedicoVirtualSupremoSkill,
    analisar,
    validar_saida,
    get_version,
    get_modulos_disponiveis,
    SKILL_VERSION,
)
from skills.medico_virtual_supremo.digital_twin import (
    DigitalTwinResult,
    MedicalDigitalTwinEngine,
    ReversaMedicalReviewer,
    TwinState,
    attach_digital_twin_to_simulation,
)
from skills.medico_virtual_supremo.simulation import analisar_simulacao

__all__ = [
    "MedicoVirtualSupremoSkill",
    "analisar",
    "analisar_simulacao",
    "validar_saida",
    "get_version",
    "get_modulos_disponiveis",
    "SKILL_VERSION",
    "DigitalTwinResult",
    "MedicalDigitalTwinEngine",
    "ReversaMedicalReviewer",
    "TwinState",
    "attach_digital_twin_to_simulation",
]
