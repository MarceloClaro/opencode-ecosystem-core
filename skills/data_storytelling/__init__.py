# -*- coding: utf-8 -*-
"""Data Storytelling Auditável — SPEC-935-R1003.

Transforma dados em narrativa visual com legenda, fonte e nota verificáveis.
Tudo é determinístico, offline e selado por SHA-256.
"""

from .captions import build_caption, caption_from_spec, validate_caption
from .manifest import build_manifest, verify_manifest
from .profiling import profile_dataset, recommend_chart
from .render import render_svg
from .rules import audit_chart, audit_narrative
from .util import SCHEMA_VERSION, DataStoryError, format_number_ptbr

__all__ = [
    "SCHEMA_VERSION",
    "DataStoryError",
    "audit_chart",
    "audit_narrative",
    "build_caption",
    "build_manifest",
    "caption_from_spec",
    "format_number_ptbr",
    "profile_dataset",
    "recommend_chart",
    "render_svg",
    "validate_caption",
    "verify_manifest",
]
