# -*- coding: utf-8 -*-
"""
Médico Virtual Supremo — Skill de Apoio Clínico Auditável v2.0

Skill do OpenCode Ecosystem para apoio à decisão clínica com pipeline
de raciocínio em 7 etapas, detecção de emergência, hipóteses diferenciais,
evidência rastreável e revisão humana obrigatória.
"""

import os
import sys

# Garante que a raiz do projeto está no path para importações absolutas
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

__all__ = [
    "MedicoVirtualSupremoSkill",
    "analisar",
    "validar_saida",
    "get_version",
    "get_modulos_disponiveis",
    "SKILL_VERSION",
]
