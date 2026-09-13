# -*- coding: utf-8 -*-
"""Subpacote workbench: conectores de supervisão desktop (M4/M6—SPEC-935-R479/R480)."""

from .deepseek_gui import (
    DEFAULT_CORE_WORKSPACES,
    HARNESS_MODULE,
    DeepSeekGUIWorkbench,
)
from .scihubeva_frontend import (
    SCIHUBEVA_RESOLVER,
    SciHubEVARequest,
    SciHubEVAFrontend,
    launch_argv,
    validate_target,
)

__all__ = [
    "DEFAULT_CORE_WORKSPACES",
    "HARNESS_MODULE",
    "DeepSeekGUIWorkbench",
    "SCIHUBEVA_RESOLVER",
    "SciHubEVARequest",
    "SciHubEVAFrontend",
    "launch_argv",
    "validate_target",
]