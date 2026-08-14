#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera SOURCE_MANIFEST.json com os hashes dos arquivos originais (R408)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

AUDIT_DIR = Path(__file__).resolve().parents[1]

FILES = [
    {
        "name": "artigo_arm_QUALIS_A1_MASTER.docx.md",
        "path": "/mnt/c/Users/marce/Downloads/artigo_arm_QUALIS_A1_MASTER.docx.md",
        "sha256": "df829326937baee115899a5070b1d8e50a234d3b1d127106fbf39ef5d24d7378",
        "role": "manuscrito auditado (somente leitura)",
        "access": "read_only",
    },
    {
        "name": "Ficha_Tecnica_Medico_Virtual_Supremo_v4.pdf",
        "path": "/mnt/c/Users/marce/Downloads/Ficha_Tecnica_Medico_Virtual_Supremo_v4.pdf",
        "sha256": "8e7dcb47b397a4c53a42c69a0a10b4da06ab6e3e92b4ffbfe040c5f8291a67b5",
        "role": "ficha técnica de protótipo clínico — NÃO valida o artigo econômico",
        "access": "read_only",
    },
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    records = []
    ok = True
    for f in FILES:
        path = Path(f["path"])
        actual = sha256(path) if path.exists() else None
        match = actual == f["sha256"] if actual else False
        ok = ok and match
        records.append({**f, "hash_atual": actual, "hash_confere": match})

    manifest = {
        "spec": "SPEC-935-R408",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": (
            "Os originais no volume Windows são somente leitura e não foram "
            "modificados. A ficha clínica é um protótipo/PoC e não valida o "
            "artigo econômico."
        ),
        "files": records,
        "all_hashes_match": ok,
    }
    out = AUDIT_DIR / "SOURCE_MANIFEST.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"SOURCE_MANIFEST.json gerado. all_hashes_match={ok}")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
