# -*- coding: utf-8 -*-
"""Subpacote model_lab: modelos pequenos reprodutíveis (M5/SPEC-935-R479)."""

from .benchmark import MiniMindBenchmark, ReproducibilityReport
from .curriculum import MINIMIND_STAGES, MODEL_CONFIG, MiniMindCurriculum
from .hardware import HardwareProbe

__all__ = [
    "MINIMIND_STAGES",
    "MODEL_CONFIG",
    "MiniMindBenchmark",
    "MiniMindCurriculum",
    "HardwareProbe",
    "ReproducibilityReport",
]