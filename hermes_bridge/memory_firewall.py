# -*- coding: utf-8 -*-
"""MemoryFirewall — memória contextualiza, mas não estabelece OBSERVED
(SPEC-935-R505).

Regras (ReversaFeynman / Hermes Bridge v1):
    Hermes memory      != OBSERVED
    memory confidence  != OBSERVED
    user model         != OBSERVED
    session summary    != OBSERVED
Aceita apenas INFERRED | UNVERIFIED | BLOCKED. `scope=personalization`
permanece isolado de autoridade de evidência.
"""
from __future__ import annotations

from hermes_bridge.contracts import MemoryEvent

ALLOWED_STATES = {"INFERRED", "UNVERIFIED", "BLOCKED"}


class MemoryFirewallError(Exception):
    pass


class MemoryFirewall:
    def accept(self, event: MemoryEvent) -> MemoryEvent:
        if event.epistemic_state == "OBSERVED":
            raise MemoryFirewallError(
                "memória nunca pode carregar estado OBSERVED (firewall epistemológico)"
            )
        if event.epistemic_state not in ALLOWED_STATES:
            raise MemoryFirewallError(
                f"estado {event.epistemic_state!r} inválido para memória"
            )
        event.isolated_from_evidence = event.scope == "personalization"
        return event