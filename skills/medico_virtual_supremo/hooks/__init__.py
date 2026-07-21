# -*- coding: utf-8 -*-
"""
Sistema de Hooks Clínicos — Médico Virtual Supremo
====================================================
Hooks são funções de pré/pós-processamento executadas em pontos específicos
do pipeline de raciocínio clínico (7 etapas).

Cada hook recebe um contexto (dict) e retorna o contexto modificado.
Hooks são registrados por nome e executados em ordem de prioridade.
"""
from skills.medico_virtual_supremo.hooks.clinical_hooks import (
    ClinicalHookManager,
    ClinicalHook,
    criar_hook_manager_padrao,
)
