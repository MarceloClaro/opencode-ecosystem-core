# -*- coding: utf-8 -*-
"""Roteador local de inferência (M3 — PAIR/SPEC-935-R478).

Conector que expõe endpoints PAIR (Personal-AI-Router, NVIDIA — Apache-2.0;
Ollama-compatible/OpenAI-compatible) como provedor adicional do doctor e do
roteamento de inferência dos agentes.

Ordem de prioridade (invariante da R471): local → PAIR → Ollama → OpenAI.

Segurança:
- opt-in: sem ``PAIR_BASE_URL``/``PAIR_ENDPOINTS`` o PAIR está inativo;
- ``pair_provider_status()`` reporta apenas definido/ausente — jamais valor;
- nenhuma chamada de rede é feita por este módulo; readiness é injetável.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

DEFAULT_ROUTE_PRIORITY: tuple = ("local", "pair", "ollama", "openai")

_ENV_PAIR_BASE_URL = "PAIR_BASE_URL"
_ENV_PAIR_ENDPOINTS = "PAIR_ENDPOINTS"


@dataclass
class InferenceRoute:
    """Recibo auditável de roteamento de inferência (M3)."""

    provider: str
    selected_order: List[str]
    fallback_used: bool
    priority: List[str]
    note: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "selected_order": list(self.selected_order),
            "fallback_used": self.fallback_used,
            "priority": list(self.priority),
            "note": self.note,
        }


def pair_configured() -> bool:
    """PAIR está configurado (opt-in via ambiente) sem expor valores."""
    return bool(os.environ.get(_ENV_PAIR_BASE_URL) or os.environ.get(_ENV_PAIR_ENDPOINTS))


def pair_provider_status() -> str:
    """Status textual para o doctor: nunca inclui host, porta ou credencial."""
    if pair_configured():
        return "PAIR definido (provedor de inferência da LAN habilitado)"
    return "PAIR ausente (roteamento local → Ollama → OpenAI, sem PAIR)"


class PairRouter:
    """Roteador determinístico e injetável de inferência.

    Recebe funções de readiness (sem rede aqui) e resolve na ordem
    ``local → pair → ollama → openai``. A ausência de um provedor nunca
    levanta exceção: degrada para o próximo e registra fallback.
    """

    def __init__(
        self,
        local_ready: Optional[Callable[[], bool]] = None,
        pair_base_url: Optional[str] = None,
        pair_ready: Optional[Callable[[], bool]] = None,
        ollama_ready: Optional[Callable[[], bool]] = None,
        openai_ready: Optional[Callable[[], bool]] = None,
    ) -> None:
        self._local_ready = local_ready or (lambda: False)
        self._pair_base_url = (
            pair_base_url
            if pair_base_url is not None
            else os.environ.get(_ENV_PAIR_BASE_URL) or os.environ.get(_ENV_PAIR_ENDPOINTS)
        )
        pair_cfg = pair_configured()
        self._pair_ready = pair_ready or (lambda: pair_cfg)
        self._ollama_ready = ollama_ready or (lambda: False)
        self._openai_ready = openai_ready or (lambda: False)

    def resolve(self) -> InferenceRoute:
        selected_order: List[str] = []
        for provider in DEFAULT_ROUTE_PRIORITY:
            selected_order.append(provider)
            if provider == "local" and self._local_ready():
                return InferenceRoute("local", selected_order, fallback_used=False,
                                      priority=list(DEFAULT_ROUTE_PRIORITY),
                                      note="Inferência local on-device.")
            if provider == "pair" and self._pair_base_url and self._pair_ready():
                return InferenceRoute("pair", selected_order, fallback_used=True,
                                      priority=list(DEFAULT_ROUTE_PRIORITY),
                                      note="Roteador PAIR da LAN selecionado (Ollama/OpenAI-compatible).")
            if provider == "ollama" and self._ollama_ready():
                return InferenceRoute("ollama", selected_order, fallback_used=True,
                                      priority=list(DEFAULT_ROUTE_PRIORITY),
                                      note="Ollama local selecionado.")
            if provider == "openai" and self._openai_ready():
                return InferenceRoute("openai", selected_order, fallback_used=True,
                                      priority=list(DEFAULT_ROUTE_PRIORITY),
                                      note="OpenAI (nuvem) selecionado como fallback.")
        return InferenceRoute("none", selected_order, fallback_used=True,
                              priority=list(DEFAULT_ROUTE_PRIORITY),
                              note="Nenhum provedor disponível: inferência desativada.")


default_pair_router = PairRouter()