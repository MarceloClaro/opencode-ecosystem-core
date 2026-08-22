# -*- coding: utf-8 -*-
"""
Harness Universal — agnóstico a modelo (SPEC-935-R435)
======================================================
Harness que orquestra produções autônomas usando qualquer modelo do OpenCode
(LiteRT-LM, Colibri, OpenAI, Zen/Go, DeepSeek via Zen) via ModelRouter.
Preserva compatibilidade com integrations.deepseek_harness como provider legado.
"""

from integrations.harness.universal_adapter import UniversalHarnessAdapter
from integrations.harness.universal_bridge import UniversalHarnessBridge, harness_bridge
from integrations.harness.universal_reasoning_loop import UniversalReasoningLoop
from integrations.harness.model_registry import HarnessModelRegistry

__all__ = [
    "UniversalHarnessAdapter",
    "UniversalHarnessBridge",
    "harness_bridge",
    "UniversalReasoningLoop",
    "HarnessModelRegistry",
]
