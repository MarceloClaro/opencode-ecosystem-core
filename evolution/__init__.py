# -*- coding: utf-8 -*-
"""
Pacote evolution — Ciclos Evolutivos Documentados (R1..R46+)
============================================================
Registro programático de rounds evolutivos com scores e lições,
mais os documentos evo-*.md portados do ecossistema original.
"""

from evolution.cycles import EvolutionCycle, EvolutionRegistry, evolution_registry
from evolution.audit_gate import EvolutionAuditGate, git_head_commit
from evolution.audit_pipeline import AuditPipeline, AuditReport, AuditAlert
from evolution.quality_correlator import QualityCorrelator, QualitySnapshot, CorrelationResult

__all__ = [
    "EvolutionCycle", "EvolutionRegistry", "evolution_registry",
    "EvolutionAuditGate", "git_head_commit",
    "AuditPipeline", "AuditReport", "AuditAlert",
    "QualityCorrelator", "QualitySnapshot", "CorrelationResult",
]
