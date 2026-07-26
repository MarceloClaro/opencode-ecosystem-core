# -*- coding: utf-8 -*-
"""
OpenCode Colibri Integration — GLM-5.2 (744B MoE) Inference Engine
==================================================================
Integração com o runtime Colibri (fork de JustVugg/colibri), um motor de
inferência em C puro que executa GLM-5.2 (744B parâmetros MoE) em hardware
consumer com ~25 GB de RAM via streaming de especialistas do disco.

Repositório: https://github.com/MarceloClaro/colibri (fork)
Original:    https://github.com/JustVugg/colibri (19k+ estrelas)

Componentes:
  - ColibriBridge: detecção, inicialização e comunicação com o runtime
  - ColibriMCPServer: servidor MCP para uso como ferramenta OpenCode
  - Cliente da API compatível com OpenAI (via `./coli serve`)

Uso:
    from integrations.colibri import ColibriBridge
    bridge = ColibriBridge()
    if bridge.available:
        result = bridge.chat("Explique conceito")
"""

from __future__ import annotations

from integrations.colibri.bridge import ColibriBridge, COLI_CAPABILITIES

__all__ = ["ColibriBridge", "COLI_CAPABILITIES"]
