# -*- coding: utf-8 -*-
"""
Plugins de Validação Cruzada — Médico Virtual Supremo
=======================================================
Plugins que operam sobre o pipeline clínico para validar, cruzar
e verificar consistência de diagnósticos, hipóteses e evidências.
"""
from skills.medico_virtual_supremo.plugins.cross_validation import (
    CrossValidationPlugin,
    DifferentialValidator,
    EvidenceCrosscheck,
    CrossValidationReport,
)
