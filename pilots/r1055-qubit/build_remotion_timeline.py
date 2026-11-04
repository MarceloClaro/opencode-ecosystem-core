#!/usr/bin/env python3
"""Gera a timeline TypeScript do explainer de qubit a partir do áudio e do SRT.

Além dos limites de cena, cada cena recebe blocos de legenda com início e fim
em frames, derivados de `subtitles.srt`. O Remotion exibe um bloco por vez,
reduzindo a carga de leitura em relação a uma legenda estática longa.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIO = ROOT / "pilots/r1055-qubit/audio"
timeline = json.loads((AUDIO / "timeline.json").read_text(encoding="utf-8"))
fps = timeline["fps"]
total_frames = round(timeline["total_duration"] * fps)


def _srt_seconds(value: str) -> float:
    match = re.fullmatch(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", value.strip())
    if not match:
        raise ValueError(f"timestamp inválido: {value}")
    hours, minutes, seconds, millis = (int(part) for part in match.groups())
    return hours * 3600 + minutes * 60 + seconds + millis / 1000


def parse_srt(path: Path) -> list[dict]:
    blocks = []
    for raw in re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip()):
        lines = [line for line in raw.splitlines() if line.strip()]
        if len(lines) < 3:
            continue
        start, end = lines[1].split("-->")
        blocks.append({
            "start": _srt_seconds(start),
            "end": _srt_seconds(end),
            "text": " ".join(lines[2:]).strip(),
        })
    return blocks


captions = parse_srt(AUDIO / "subtitles.srt")
scenes = []
for index, scene in enumerate(timeline["scenes"]):
    start = round(scene["start"] * fps)
    end = round(scene["end"] * fps)
    if index == len(timeline["scenes"]) - 1:
        end = total_frames
    if scene.get("captions"):
        scene_captions = [
            {
                "startFrame": max(start, round(caption["start"] * fps)),
                "endFrame": min(end, round(caption["end"] * fps)),
                "text": caption["text"],
            }
            for caption in scene["captions"]
            if caption["end"] > scene["start"] and caption["start"] < scene["end"]
        ]
    else:
        scene_captions = [
            {
                "startFrame": max(start, round(block["start"] * fps)),
                "endFrame": min(end, round(block["end"] * fps)),
                "text": block["text"],
            }
            for block in captions
            if block["end"] > scene["start"] and block["start"] < scene["end"]
        ]
    scenes.append({
        "id": scene["id"],
        "title": scene["title"],
        "subtitle": scene["subtitle"],
        "startFrame": start,
        "endFrame": end,
        "captions": scene_captions,
    })

lines = [
    "// Gerado por pilots/r1055-qubit/build_remotion_timeline.py",
    f"export const FPS = {fps};",
    f"export const TOTAL_FRAMES = {total_frames};",
    "export type Caption = {",
    "  startFrame: number;",
    "  endFrame: number;",
    "  text: string;",
    "};",
    "export type Scene = {",
    "  id: string;",
    "  title: string;",
    "  subtitle: string;",
    "  startFrame: number;",
    "  endFrame: number;",
    "  captions: Caption[];",
    "};",
    "",
    "export const SCENES: Scene[] = [",
]
for scene in scenes:
    body = [
        "  {",
        f"    id: {json.dumps(scene['id'])},",
        f"    title: {json.dumps(scene['title'], ensure_ascii=False)},",
        f"    subtitle: {json.dumps(scene['subtitle'], ensure_ascii=False)},",
        f"    startFrame: {scene['startFrame']}, endFrame: {scene['endFrame']},",
        "    captions: [",
    ]
    for caption in scene["captions"]:
        body.append(
            "      {"
            f"startFrame: {caption['startFrame']}, endFrame: {caption['endFrame']}, "
            f"text: {json.dumps(caption['text'], ensure_ascii=False)}"
            "},"
        )
    body += ["    ],", "  },"]
    lines.extend(body)
lines.append("];")
target = ROOT / "editor-workspace/remotion-smoke/src/r1055-qubit/timeline.ts"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(target)
print("total_frames", total_frames, "scenes", len(scenes), "captions", len(captions))
