#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera a narração de cada cena com edge-tts e mede a duração."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
from roteiro import SCENES  # noqa: E402

EDGE = os.environ.get("EDGE_TTS", "/tmp/ttsvenv/bin/edge-tts")
VOICE = os.environ.get("TTS_VOICE", "pt-BR-AntonioNeural")
RATE = os.environ.get("TTS_RATE", "-5%")
AUDIO = BASE / "audio"
AUDIO.mkdir(exist_ok=True)


def duracao(mp3: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(mp3)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def main() -> int:
    dados = []
    for i, cena in enumerate(SCENES, 1):
        cid = cena["id"]
        mp3 = AUDIO / f"{cid}.mp3"
        srt = AUDIO / f"{cid}.srt"
        txt = AUDIO / f"{cid}.txt"
        txt.write_text(cena["narration"], encoding="utf-8")
        cmd = [
            EDGE, "--voice", VOICE, "--rate", RATE,
            "--file", str(txt),
            "--write-media", str(mp3),
            "--write-subtitles", str(srt),
            "--no-progress",
        ]
        print(f"[{i:02d}/{len(SCENES)}] {cid}", flush=True)
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print(proc.stdout)
            print(proc.stderr, file=sys.stderr)
            raise SystemExit(f"edge-tts falhou em {cid}")
        d = duracao(mp3)
        dados.append({
            "id": cid,
            "index": i,
            "duration": round(d, 3),
            "mp3": str(mp3.relative_to(BASE)),
            "srt": str(srt.relative_to(BASE)),
            "narration": cena["narration"],
        })
        print(f"    {d:.2f}s", flush=True)

    (AUDIO / "durations.json").write_text(
        json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    total = sum(x["duration"] for x in dados)
    print(f"\nTotal de narração: {total:.1f}s ({total/60:.2f} min)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
