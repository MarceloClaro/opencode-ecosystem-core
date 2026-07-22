# -*- coding: utf-8 -*-
"""
LiteRT-LM Skill — Google AI Edge On-Device LLM Inference
=========================================================
Integração do LiteRT-LM v0.14 ao OpenCode Ecosystem Core.

Uso:
    from skills.litert_lm.skill import LiteRTLMSkill
    skill = LiteRTLMSkill()
    models = skill.list_models()
    response = skill.run("gemma-4-E2B-it", "Olá!")
"""

from .skill import LiteRTLMSkill
from .chat import ChatSession
from .model_manager import ModelManager, ModelInfo, ModelNotFoundError

__all__ = (
    "LiteRTLMSkill",
    "ChatSession",
    "ModelManager",
    "ModelInfo",
    "ModelNotFoundError",
)
