# -*- coding: utf-8 -*-
"""
Pacote academic — Pipeline Acadêmico Qualis A1
==============================================
MASWOS (orquestração de escrita científica multiagente), SEEKER (busca de
datasets/fontes) e AUTO_SCORE_QUALIS (scorer de manuscritos 0-10),
portados do OpenCode_Ecosystem original.
"""

from academic.maswos import (MaswosPipeline, MaswosRun, MASWOS_STAGES,
                              maswos_pipeline, CLOUD_STAGES, CLOUD_TOPIC_KEYWORDS,
                              is_cloud_topic, run_maswos_cloud)

__all__ = ["MaswosPipeline", "MaswosRun", "MASWOS_STAGES", "maswos_pipeline",
           "CLOUD_STAGES", "CLOUD_TOPIC_KEYWORDS", "is_cloud_topic", "run_maswos_cloud"]
