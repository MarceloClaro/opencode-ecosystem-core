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
        success = payload.get("success", True)
        
        # Em um sistema real, isso chamaria o LLM (Ollama) para gerar a reflexão.
        # Aqui, simulamos a extração de lições baseada no sucesso/falha.
        
        if success:
            reflection = f"O agente {agent_id} concluiu a tarefa com sucesso. Estratégia utilizada foi eficaz."
            score = 1.0
            lesson = f"Contexto '{context[:30]}...' resolvido adequadamente."
        else:
            reflection = f"O agente {agent_id} falhou na tarefa. A abordagem inicial não produziu o resultado esperado."
            score = 0.2
            lesson = f"Evitar a mesma abordagem para '{context[:30]}...'."
            
        # 1. Salva na memória episódica
        ref_id = metabus.memory.add_reflection(
            agent_id=agent_id,
            task_context=context,
            reflection=reflection,
            score=score
        )
        
        # 2. Extrai lições para a memória semântica (tópico genérico por enquanto)
        topic = "general_execution"
        if topic not in metabus.memory.semantic:
            metabus.memory.semantic[topic] = {"lessons": []}
            
        if lesson not in metabus.memory.semantic[topic]["lessons"]:
            metabus.memory.semantic[topic]["lessons"].append(lesson)
            
        metabus.memory._save()
        
        # 3. Publica que a reflexão foi concluída
        metabus.publish("metacognition.reflected", {
            "reflection_id": ref_id,
            "agent_id": agent_id,
            "score": score,
            "new_confidence": metabus.memory.confidence_ledger.get(agent_id)
        }, source_agent="reflexion_engine")
        
        logger.info(f"Reflexão gerada para {agent_id} (Score: {score})")

# Instância global Singleton
reflexion_engine = ReflexionEngine()
