# -*- coding: utf-8 -*-
"""
Pacote scanners — Pipeline de Diagnóstico (5 + opcionais)
=========================================================
Noológico, Teleológico, Evolutivo, Potentiality e Social Impact,
portados do OpenCode_Ecosystem original, unificados em DiagnosticPipeline.

Extensões opcionais:
- LegalImpactScanner (SPEC-924): visão jurídica de impacto para pesquisas e produções.
"""

from scanners.pipeline import DiagnosticPipeline, diagnostic_pipeline
from scanners.legal_impact_scanner import LegalImpactScanner

__all__ = ["DiagnosticPipeline", "diagnostic_pipeline", "LegalImpactScanner"]
