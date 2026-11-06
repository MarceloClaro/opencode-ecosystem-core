#!/usr/bin/env python3
"""Reconstrói os assets externos do piloto R1059 sem tocar no vídeo aprovado.

Baixa apenas a camada Terrain do EOX::Maps (WMS público) e confere a sequência
de frames exportada pelo Motion Canvas. Não instala pacotes nem renderiza.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "editor-workspace/remotion-smoke/public"
OUT = ROOT / "pilots/r1059-roraima/out"
WMS = "https://tiles.maps.eox.at/wms"
BBOX = "-84,-57,-30,29"
EXPECTED = 300


def fetch_terrain() -> dict:
    query = urllib.parse.urlencode({
        "service": "WMS", "request": "GetMap", "version": "1.1.1",
        "layers": "terrain", "styles": "", "srs": "EPSG:4326",
        "bbox": BBOX, "width": "1440", "height": "2560", "format": "image/jpeg",
    })
    url = f"{WMS}?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": "R1059-pilot/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read(15_000_000)
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("Resposta não é JPEG")
    target = PUBLIC / "r1059-terrain.jpg"
    target.write_bytes(data)
    return {
        "file": str(target.relative_to(ROOT)),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "source": "EOX::Maps Terrain (WMS)",
        "bbox": [-84, -57, -30, 29],
        "crs": "EPSG:4326",
        "attribution": "EOX::Maps Terrain; dados OSM, Natural Earth, NASA e outros",
    }


def check_frames() -> dict:
    folder = PUBLIC / "r1059-tepui"
    files = sorted(folder.glob("*.png"))
    if len(files) != EXPECTED:
        raise ValueError(f"Esperados {EXPECTED} frames; encontrados {len(files)}")
    for index, path in enumerate(files):
        if path.name != f"{index:06d}.png":
            raise ValueError(f"Sequência não contínua em {path.name}")
    return {"frames": len(files), "folder": str(folder.relative_to(ROOT))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-frames", action="store_true")
    parser.add_argument("--skip-download", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    result = {}
    if not args.skip_download:
        result["terrain"] = fetch_terrain()
    if args.check_frames:
        result["frames"] = check_frames()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
