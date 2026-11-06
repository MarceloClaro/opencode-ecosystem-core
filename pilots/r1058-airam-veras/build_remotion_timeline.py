#!/usr/bin/env python3
"""Gera a timeline TypeScript do R1058 a partir de audio/timeline.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT.parents[1] / "editor-workspace/remotion-smoke/src/r1058-airam/timeline.ts"


def q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def main() -> int:
    data = json.loads((ROOT / "audio/timeline.json").read_text(encoding="utf-8"))
    fps = data["fps"]
    lines = [
        "// Gerado por pilots/r1058-airam-veras/build_remotion_timeline.py",
        "export const FPS = 30;",
        f"export const TOTAL_FRAMES = {data['total_frames']};",
        "",
        "export type Caption = {startFrame:number; endFrame:number; text:string};",
        "export type Scene = {id:string; title:string; kicker:string; startFrame:number; endFrame:number; captions:Caption[]};",
        "",
        "export const SCENES: Scene[] = [",
    ]
    for scene in data["scenes"]:
        start = round(scene["start"] * fps)
        end = round(scene["end"] * fps)
        captions = ", ".join(
            "{startFrame:%d, endFrame:%d, text:%s}"
            % (round(c["start"] * fps), round(c["end"] * fps), q(c["text"]))
            for c in scene["captions"]
        )
        lines.append(
            "  {id:%s, title:%s, kicker:%s, startFrame:%d, endFrame:%d, captions:[%s]},"
            % (q(scene["id"]), q(scene["title"]), q(scene["kicker"]), start, end, captions)
        )
    lines.append("];")
    lines.append("")
    meta = json.loads((ROOT / "assets/map-meta.json").read_text(encoding="utf-8"))
    lines.append("export const MAP = " + json.dumps(meta, ensure_ascii=False) + " as const;")
    skills = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
    lines.append("")
    lines.append("export const SKILLS = " + json.dumps(skills, ensure_ascii=False) + " as const;")
    TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"target": str(TARGET), "frames": data["total_frames"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
