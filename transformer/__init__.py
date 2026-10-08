# -*- coding: utf-8 -*-
"""
Transformer Layer — Orquestração inspirada na arquitetura Transformer
=====================================================================
Mapeia conceitos do Transformer (Vaswani et al. 2017) para orquestração
multiagente, com inspiração direta nos repositórios:
- MarceloClaro/superhuman (Aletheia: gerar→verificar→revisar; IMO-GradingBench)
- MarceloClaro/deepmind-research (Perceiver, Hierarchical Transformer Memory, PrediNet)
- MarceloClaro/OpenCode_Ecosystem (camada MCI)

| Transformer            | Ecossistema                          |
|------------------------|--------------------------------------|
| Token embedding        | TaskEmbedder                         |
| Positional encoding    | Índice/prioridade da tarefa          |
| Multi-Head Attention   | AttentionRouter (4 cabeças)          |
| Cabeça cross-harness   | HarnessAttentionHead (5ª cabeça)     |
| Feed-Forward + resíduo | TransformerPipeline (gerar/revisar)  |
| Output head            | GradingHead (escala 0-7)             |
| KV-cache hierárquico   | HierarchicalMemory (HTM)             |
"""

from .embedder import TaskEmbedder, D_MODEL
from .attention import AttentionRouter
from .pipeline import TransformerPipeline, GradingHead, MAX_SCORE
from .memory import HierarchicalMemory
from .harness_head import (
    DEFAULT_HEAD_WEIGHTS,
    HarnessAttentionHead,
    HarnessRegistry,
    attach_to_router,
    license_score,
)

__all__ = [
    "TaskEmbedder", "D_MODEL",
    "AttentionRouter",
    "TransformerPipeline", "GradingHead", "MAX_SCORE",
    "HierarchicalMemory",
    "HarnessAttentionHead", "HarnessRegistry", "attach_to_router",
    "DEFAULT_HEAD_WEIGHTS", "license_score",
]

__version__ = "2.1.0"
