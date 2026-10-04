# -*- coding: utf-8 -*-
"""Hooks do Core (SPEC-935-R653): engine fail-closed + política deny-list."""

from .engine import EVENTS, HookMatcher, run_hooks
from .policy import audit_log, check_bash, default_matchers

__all__ = ["EVENTS", "HookMatcher", "run_hooks", "audit_log",
           "check_bash", "default_matchers"]
