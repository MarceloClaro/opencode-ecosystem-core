# -*- coding: utf-8 -*-
"""
Pacote academic — Pipeline Acadêmico Qualis A1
==============================================
MASWOS (orquestração de escrita científica multiagente), SEEKER (busca de
datasets/fontes) e AUTO_SCORE_QUALIS (scorer de manuscritos 0-10),
portados do OpenCode_Ecosystem original.
"""

from academic.maswos import MaswosPipeline, MaswosRun, MASWOS_STAGES, maswos_pipeline

__all__ = ["MaswosPipeline", "MaswosRun", "MASWOS_STAGES", "maswos_pipeline"]
