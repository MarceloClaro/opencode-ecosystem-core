# -*- coding: utf-8 -*-
"""
Pacote scanners — Pipeline de Diagnóstico (5 + opcionais)
=========================================================
Noológico, Teleológico, Evolutivo, Potentiality e Social Impact,
portados do OpenCode_Ecosystem original, unificados em DiagnosticPipeline.

Extensões opcionais:
- LegalImpactScanner (SPEC-924): visão jurídica de impacto para pesquisas e produções.
- LiteraryScanners (SPEC-935-R267): 8 visões críticas calibradas para literatura.
"""

from scanners.pipeline import DiagnosticPipeline, diagnostic_pipeline
from scanners.legal_impact_scanner import LegalImpactScanner
from scanners.literary_scanners import (
    CharacterPsychologyScanner,
    EthicalRepresentationScanner,
    IntertextualTheoryScanner,
    LITERARY_SCANNER_CLASSES,
    LiteraryInnovationScanner,
    NarrativeArchitectureScanner,
    ReaderResponseScanner,
    StyleVoiceScanner,
    SymbolicImageryScanner,
    literary_scanner_suite,
    run_literary_scanner_suite,
)
from scanners.literary_research_scanners import (
    ComparativeCorpusScanner,
    InternationalRigorScanner,
    LITERARY_RESEARCH_SCANNER_CLASSES,
    LiteraryBibliographyScanner,
    TheoreticalFrameworkScanner,
    literary_research_scanner_suite,
    run_literary_research_scanner_suite,
)

__all__ = [
    "DiagnosticPipeline", "diagnostic_pipeline", "LegalImpactScanner",
    "NarrativeArchitectureScanner", "CharacterPsychologyScanner",
    "StyleVoiceScanner", "SymbolicImageryScanner", "IntertextualTheoryScanner",
    "ReaderResponseScanner", "EthicalRepresentationScanner",
    "LiteraryInnovationScanner", "LITERARY_SCANNER_CLASSES",
    "run_literary_scanner_suite", "literary_scanner_suite",
    "LiteraryBibliographyScanner", "ComparativeCorpusScanner",
    "TheoreticalFrameworkScanner", "InternationalRigorScanner",
    "LITERARY_RESEARCH_SCANNER_CLASSES",
    "run_literary_research_scanner_suite", "literary_research_scanner_suite",
]
