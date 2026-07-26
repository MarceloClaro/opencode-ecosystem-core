# -*- coding: utf-8 -*-
"""
Lazy Agent Catalog Loader — Carregamento Preguiçoso de Cartões de Agentes
==========================================================================
Indexa os arquivos de cartões de agentes em `agents/catalog/*.md` sem ler
seus conteúdos inteiramente no startup. A leitura e o parse do markdown ocorrem
sob demanda com cache LRU.
"""

from __future__ import annotations

import os
import glob
from functools import lru_cache
from typing import Dict, List, Optional, Any

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_DIR = os.path.join(REPO_ROOT, "agents", "catalog")


class LazyAgentCatalog:
    """Gerenciador com carregamento preguiçoso para o catálogo de agentes."""

    def __init__(self, catalog_dir: str = CATALOG_DIR):
        self.catalog_dir = catalog_dir
        self._index: Dict[str, str] = {}
        self._build_index()

    def _build_index(self) -> None:
        """Constrói o índice rápido de nomes de agentes -> caminhos dos arquivos."""
        self._index.clear()
        if os.path.exists(self.catalog_dir):
            for path in glob.glob(os.path.join(self.catalog_dir, "*.md")):
                filename = os.path.basename(path)
                agent_id = filename.replace(".md", "").replace("_", "-")
                self._index[agent_id] = path

    def list_agents(self) -> List[str]:
        """Retorna a lista de IDs de agentes disponíveis no catálogo."""
        return sorted(list(self._index.keys()))

    @lru_cache(maxsize=256)
    def load_agent_card(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Lê o cartão de agente em disco sob demanda com cache LRU."""
        path = self._index.get(agent_id)
        if not path or not os.path.exists(path):
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "agent_id": agent_id,
                "path": path,
                "content": content,
                "size_bytes": len(content),
            }
        except Exception:
            return None

    def clear_cache(self) -> None:
        """Limpa o cache de cartões carregados."""
        self.load_agent_card.cache_clear()


lazy_agent_catalog = LazyAgentCatalog()
