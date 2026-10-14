# -*- coding: utf-8 -*-
"""
Reflexion Middleware
====================
Implementa o padrão Reflexion (Shinn et al. 2023) acoplado ao MetaBus.
Permite que qualquer agente faça auto-reflexão pós-tarefa e gere aprendizados.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import logging
from typing import Dict, Any

from .metabus import metabus

logger = logging.getLogger("mci-reflexion")
logger.setLevel(logging.INFO)

class ReflexionEngine:
    """Motor que orquestra as reflexões metacognitivas pós-execução."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ReflexionEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # Ouve pedidos de reflexão vindos do Blackboard ou de Agentes
        metabus.subscribe("metacognition.reflect_request", self._handle_reflection)

    def _handle_reflection(self, event: Dict[str, Any]):
        """Gera uma reflexão baseada no resultado da tarefa."""
        payload = event.get("payload", {})
        agent_id = payload.get("agent_id", "unknown")
        context = payload.get("context", "")
        result = payload.get("result", "")
        success = payload.get("success", False)
        
        from .metacognitive_loop import MetacognitiveLoop

        try:
            report = MetacognitiveLoop(metabus).complete(
                task_id=payload.get("task_id", event.get("event_id", "unknown")),
                agent_id=agent_id, context=context, result=result,
                success=success is True, sdd_verification=payload.get("sdd_verification"))
        except Exception as error:
            metabus.publish("metacognition.failed", {
                "task_id": payload.get("task_id"), "agent_id": agent_id,
                "status": "degraded", "error_type": type(error).__name__,
                "confidence_promoted": False, "calibrated": False,
            }, source_agent="reflexion_engine")
            logger.warning("Reflexão não persistida: %s", type(error).__name__)
            return
        metabus.publish("metacognition.reflected", report, source_agent="reflexion_engine")
        logger.info("Reflexão contextual persistida para %s", agent_id)

# Instância global Singleton
reflexion_engine = ReflexionEngine()
