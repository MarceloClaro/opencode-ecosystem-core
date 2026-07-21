# -*- coding: utf-8 -*-
"""
Pipeline Transformer de Orquestração Clínica — Médico Virtual Supremo
=======================================================================
Implementa roteamento multi-cabeça (attention-based) para distribuir casos
clínicos aos especialistas adequados, seguindo a arquitetura Transformer
do OpenCode Ecosystem (SPEC-004, SPEC-005, SPEC-934).
"""
from skills.medico_virtual_supremo.orchestration.transformer_pipeline import (
    ClinicalTransformerPipeline,
    AttentionRoutingResult,
    EspecialistaProfile,
)
