# -*- coding: utf-8 -*-
"""Subpacote sandbox: política declarativa de isolamento (M2/SPEC-935-R478)."""

from .declarative_policy import (
    DEFAULT_BIBLIOGRAPHIC_ENDPOINTS,
    SCIENTIFIC_TEMPLATE_YAML,
    DeclarativePolicy,
    PolicyDecision,
)

__all__ = [
    "DEFAULT_BIBLIOGRAPHIC_ENDPOINTS",
    "SCIENTIFIC_TEMPLATE_YAML",
    "DeclarativePolicy",
    "PolicyDecision",
]