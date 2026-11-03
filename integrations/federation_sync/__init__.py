# -*- coding: utf-8 -*-
"""R1012 — federação universal de plugins, MCPs e agentes sob MarceloClaro.

Camada passiva: inventário, triagem fail-closed, candidatos MCP desativados e
roteamento determinístico. Descoberta não é instalação; registro não é execução.
"""

from .model import ECOSYSTEMS, KINDS, STATUSES, FederatedItem, digest_items, slugify
from .sources import collect
from .store import build_candidates, load_items, load_registry, status, sync, verify
from .route import route
from .runtime import activate, activated_servers, deactivate, doctor as runtime_doctor, probe_all, smoke

__all__ = [
    "ECOSYSTEMS", "KINDS", "STATUSES", "FederatedItem", "digest_items", "slugify",
    "collect", "build_candidates", "load_items", "load_registry", "status", "sync",
    "verify", "route", "activate", "activated_servers", "deactivate",
    "runtime_doctor", "probe_all", "smoke",
]
