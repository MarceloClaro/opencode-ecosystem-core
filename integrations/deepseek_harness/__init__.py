# -*- coding: utf-8 -*-
"""
DeepSeek Harness — ponte orquestrada (SPEC-935-R433)
=====================================================
Pacote que orquestra e escala as produções autônomas e metacognições do
DeepSeek Harness (`dsh`, deepseek-harness.zip) dentro do OpenCode Ecosystem Core.

Exporta a fachada `DeepSeekHarnessBridge` e o singleton `deepseek_harness_bridge`.
"""

from integrations.deepseek_harness.bridge import DeepSeekHarnessBridge, deepseek_harness_bridge
from integrations.deepseek_harness.inventory import DeepSeekHarnessInventory
from integrations.deepseek_harness.adapter import DeepSeekHarnessAdapter
from integrations.deepseek_harness.metacognition import DSHMetacognitionIngestor
from integrations.deepseek_harness.worker_pool import DeepSeekWorkerPool
from integrations.deepseek_harness.reasoning_loop import DeepSeekReasoningLoop

__all__ = [
    "DeepSeekHarnessBridge",
    "deepseek_harness_bridge",
    "DeepSeekHarnessInventory",
    "DeepSeekHarnessAdapter",
    "DSHMetacognitionIngestor",
    "DeepSeekWorkerPool",
    "DeepSeekReasoningLoop",
]
