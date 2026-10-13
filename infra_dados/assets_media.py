# -*- coding: utf-8 -*-
"""R832 — assets_media (infra_dados).
Keywords: assets/, illustrations, media, webapp, assets. Categoria: assets_media."""
from __future__ import annotations
import hashlib
def manifest(files=None) -> dict:
    files = list(files or [])
    h = hashlib.sha256("|".join(files).encode()).hexdigest()[:16]
    return {"files": files, "hash": h, "media": True, "assets": "assets_media"}
