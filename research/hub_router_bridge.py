# -*- coding: utf-8 -*-
"""
ResearchHub Router Bridge — Ponte de Conexão do ResearchHub ao Ecossistema
===========================================================================
Conecta o ResearchHub (PubMed, bioRxiv, CORE, Crossref, OpenAlex, etc.) ao
Blackboard A2A, ao MetaBus e ao Orquestrador MarceloClaro.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from mci.metabus import metabus
from mci.blackboard import blackboard
from research.hub import ResearchHub

logger = logging.getLogger("research.bridge")


class ResearchHubBridge:
    """Ponte de integração do ResearchHub no barramento A2A e MetaBus."""

    def __init__(self):
        pass

    def execute_and_publish(
        self,
        topic: str,
        max_papers: int = 5,
        download: bool = True,
        use_llm: bool = False,
    ) -> Dict[str, Any]:
        """Executa o pipeline de pesquisa e publica o resultado no Blackboard e MetaBus."""
        logger.info("Iniciando ponte de pesquisa unificada para o tema: %s", topic)
        hub = ResearchHub(topic)
        manifest = hub.run(max_papers=max_papers, download=download, use_llm=use_llm)

        # 1. Registro no Blackboard A2A para consumo por outros agentes
        metabus.publish_subsystem_event(
            "blackboard",
            "task.post",
            {
                "task_id": f"research-{hash(topic) % 10000}",
                "description": f"Pesquisa concluída para o tema: {topic}",
                "required_capabilities": ["research", "review"],
                "context": {
                    "topic": topic,
                    "folder": str(hub.folder),
                    "resumo": manifest.get("resumo", {}),
                    "manifest_path": str(Path(hub.folder) / "RESEARCH_MANIFEST.json"),
                },
            },
            source_agent="research_hub_bridge",
        )

        # 2. Publicação de evento no MetaBus
        metabus.publish_subsystem_event(
            "research_hub",
            "research.completed",
            {
                "topic": topic,
                "folder": str(hub.folder),
                "selected_papers": manifest.get("resumo", {}).get("artigos_selecionados", 0),
            },
            source_agent="research_hub_bridge",
        )

        manifest["bridge_status"] = "published_to_blackboard_and_metabus"
        return manifest


research_hub_bridge = ResearchHubBridge()
