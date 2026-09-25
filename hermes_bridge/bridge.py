# -*- coding: utf-8 -*-
"""HermesBridge — fronteira inerte sem transporte (SPEC-935-R505).

O runtime Hermes (Nous Research) pode ser conectado futuramente por um
callback de transporte (CLI, RPC, MCP). SEM transporte configurado, o
dispatch é NO-OP. Este módulo NÃO importa nem depende do runtime Hermes.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


class HermesBridge:
    def __init__(self, transport: Optional[Any] = None):
        self._transport = transport

    def dispatch(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self._transport is None:
            return {"dispatched": False, "reason": "no_transport",
                    "event_type": event_type}
        return self._transport.send(event_type, payload)

    @property
    def connected(self) -> bool:
        return self._transport is not None