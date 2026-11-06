#!/usr/bin/env python3
"""Renderiza um mapa-múndi escuro a partir do Natural Earth 110m (domínio público).

Fonte: world-atlas@2 (TopoJSON derivado do Natural Earth, domínio público).
O mapa é equirretangular e serve de base para a cena de origem geográfica.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
TOPO = Path("/tmp/opencode/maps/countries-110m.json")
OUT = ROOT / "editor-workspace/remotion-smoke/public/r1055-world-map.png"
COPY = ROOT / "pilots/r1055-qubit/assets/r1055-world-map.png"
W = 4096
LAT_MAX, LAT_MIN = 64.0, -55.0
H = round(W * (LAT_MAX - LAT_MIN) / 360.0)


def decode_arcs(topo: dict) -> list[list[tuple[float, float]]]:
    scale = topo["transform"]["scale"]
    translate = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        points = []
        for dx, dy in arc:
            x += dx
            y += dy
            points.append((x * scale[0] + translate[0], y * scale[1] + translate[1]))
        arcs.append(points)
    return arcs


def ring_points(ring: list[int], arcs: list[list[tuple[float, float]]]) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for index in ring:
        if index >= 0:
            segment = arcs[index]
        else:
            segment = list(reversed(arcs[~index]))
        if points and segment and points[-1] == segment[0]:
            points.extend(segment[1:])
        else:
            points.extend(segment)
    return points


def to_xy(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    return [((lon + 180.0) / 360.0 * W, (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * H) for lon, lat in points]


def main() -> int:
    topo = json.loads(TOPO.read_text(encoding="utf-8"))
    arcs = decode_arcs(topo)
    geometries = topo["objects"]["countries"]["geometries"]

    # Fundo em gradiente vertical (oceano profundo).
    gradient = Image.new("RGB", (W, H), "#07111D")
    draw = ImageDraw.Draw(gradient)
    for y in range(H):
        t = y / max(H - 1, 1)
        r = int(7 + 5 * t)
        g = int(17 + 10 * t)
        b = int(29 + 14 * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    gradient.save("/tmp/opencode/maps/base-gradient.png")

    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200, frameon=False)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    ax.set_facecolor("none")

    # Graticula.
    for lon in range(-180, 181, 30):
        x = (lon + 180) / 360 * W
        ax.plot([x, x], [0, H], color="#4C6C8C", alpha=0.10, linewidth=0.7, zorder=1)
    for lat in range(-60, 61, 30):
        y = (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * H
        ax.plot([0, W], [y, y], color="#4C6C8C", alpha=0.10, linewidth=0.7, zorder=1)

    for feature in geometries:
        if feature["type"] == "Polygon":
            polygons = [feature["arcs"]]
        elif feature["type"] == "MultiPolygon":
            polygons = feature["arcs"]
        else:
            continue
        for polygon in polygons:
            for ring in polygon:
                points = to_xy(ring_points(ring, arcs))
                if len(points) < 3:
                    continue
                ax.add_patch(
                    MplPolygon(
                        points,
                        closed=True,
                        facecolor="#1B3044",
                        edgecolor="#3F6383",
                        linewidth=0.55,
                        alpha=0.98,
                        zorder=2,
                    )
                )

    fig.savefig(
        "/tmp/opencode/maps/land.png",
        transparent=True,
        dpi=200,
        pad_inches=0,
    )
    plt.close(fig)

    with Image.open("/tmp/opencode/maps/base-gradient.png").convert("RGBA") as base:
        with Image.open("/tmp/opencode/maps/land.png").convert("RGBA") as land:
            base.alpha_composite(land)
            composed = base.convert("RGB")
            OUT.parent.mkdir(parents=True, exist_ok=True)
            composed.save(OUT, optimize=True)
            COPY.parent.mkdir(parents=True, exist_ok=True)
            composed.save(COPY, optimize=True)
    print(OUT, OUT.stat().st_size)
    print(COPY, COPY.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
