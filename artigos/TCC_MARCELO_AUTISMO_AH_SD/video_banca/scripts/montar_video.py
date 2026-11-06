#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta o vídeo de banca: segmentos por cena, concatenação e legendas.

Fluxo:
1. cada cena vira um segmento de vídeo (slide estático + narração);
2. os segmentos são concatenados sem reencode (mesmos parâmetros);
3. as legendas de cada cena são deslocadas pelo offset acumulado e gravadas
   em ASS com estilo fixo (1920x1080), depois queimadas no vídeo final.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AUDIO = BASE / "audio"
SLIDES = BASE / "slides"
SEGS = BASE / "segments"
BUILD = BASE / "build"
FINAL = BASE / "Dupla_Excepcionalidade_Banca.mp4"

LEAD = 0.20   # silêncio antes da fala
TAIL = 0.20   # respiro depois da fala (o MP3 já traz ~0,9 s de cauda)
FPS = 30

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Legenda,Liberation Sans,35,&H00E8F1F5,&H00E8F1F5,&H003A1F0B,&H78000000,1,0,0,0,100,100,0,0,1,2.2,0,2,140,140,48,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=True, **kw)


def duracao(caminho: Path) -> float:
    out = run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(caminho),
    ]).stdout.strip()
    return float(out)


def parse_srt(caminho: Path) -> list[tuple[float, float, str]]:
    texto = caminho.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    blocos = re.split(r"\n\s*\n", texto.strip())
    cues = []
    for bloco in blocos:
        linhas = [l for l in bloco.split("\n") if l.strip()]
        if len(linhas) < 2:
            continue
        idx = 0
        if re.fullmatch(r"\d+", linhas[0].strip()):
            idx = 1
        if "-->" not in linhas[idx]:
            continue
        ini, fim = [p.strip() for p in linhas[idx].split("-->")]
        corpo = " ".join(linhas[idx + 1:]).strip()
        corpo = corpo.replace("{", "(").replace("}", ")")
        if corpo:
            cues.append((hms(ini), hms(fim), corpo))
    return cues


def hms(t: str) -> float:
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s.replace(",", "."))


def dividir(texto: str, limite: int = 120) -> list[str]:
    """Divide falas longas em blocos de no máximo `limite` caracteres."""
    if len(texto) <= limite:
        return [texto]
    partes, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if len(teste) <= limite or not atual:
            atual = teste
        else:
            partes.append(atual)
            atual = palavra
    if atual:
        partes.append(atual)
    return partes


def ass_para_srt_time(t: str) -> str:
    h, m, s = t.split(":")
    return f"{int(h):02d}:{m}:{s.replace('.', ',')}"


def ass_para_srt(ass_path: Path, srt_path: Path) -> int:
    """Exporta o ASS queimado como SRT equivalente (mesmos tempos e textos)."""
    eventos = [
        l for l in ass_path.read_text(encoding="utf-8").splitlines()
        if l.startswith("Dialogue:")
    ]
    blocos = []
    for i, ev in enumerate(eventos, 1):
        partes = ev.split(",", 9)
        ini = ass_para_srt_time(partes[1])
        fim = ass_para_srt_time(partes[2])
        texto = partes[9]
        blocos.append(f"{i}\n{ini} --> {fim}\n{texto}\n")
    srt_path.write_text("\n".join(blocos), encoding="utf-8")
    return len(blocos)


def ass_time(t: float) -> str:
    t = max(t, 0.0)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def montar_segmento(cena: dict, force: bool) -> Path:
    seg = SEGS / f"seg_{cena['index']:02d}.mp4"
    slide = SLIDES / f"{cena['id']}.png"
    audio = BASE / cena["mp3"]
    if seg.exists() and not force:
        print(f"    reutilizando {seg.name}")
        return seg
    if not slide.exists():
        raise SystemExit(f"slide ausente: {slide}")

    dur = LEAD + cena["duration"] + TAIL
    filtro = (
        f"[1:a]adelay={int(LEAD*1000)}:all=1,"
        f"apad=pad_dur={TAIL},"
        f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[a]"
    )
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-loop", "1", "-framerate", str(FPS), "-i", str(slide),
        "-i", str(audio),
        "-filter_complex", filtro,
        "-map", "0:v", "-map", "[a]",
        "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart",
        str(seg),
    ]
    run(cmd)
    print(f"    {seg.name}: {duracao(seg):.2f}s")
    return seg


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="refaz segmentos existentes")
    args = ap.parse_args()

    for d in (SEGS, BUILD):
        d.mkdir(exist_ok=True)

    cenas = json.loads((AUDIO / "durations.json").read_text(encoding="utf-8"))
    print(f"Cenas: {len(cenas)}")

    segmentos = []
    for cena in cenas:
        print(f"[{cena['index']:02d}/{len(cenas)}] {cena['id']}")
        segmentos.append(montar_segmento(cena, args.force))

    # concatenação
    lista = BUILD / "concat.txt"
    lista.write_text(
        "".join(f"file '{s.as_posix()}'\n" for s in segmentos), encoding="utf-8"
    )
    concatenado = BUILD / "concatenado.mp4"
    print("Concatenando...")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(lista),
        "-c", "copy", "-movflags", "+faststart", str(concatenado),
    ])
    print(f"    {duracao(concatenado):.2f}s")

    normalizado = BUILD / "normalizado.mp4"
    print("Normalizando áudio para -16 LUFS...")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(concatenado),
        "-c:v", "copy",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", str(normalizado),
    ])

    # legendas com offsets acumulados
    offset = 0.0
    linhas = [ASS_HEADER]
    total_cues = 0
    for cena, seg in zip(cenas, segmentos):
        dseg = duracao(seg)
        cues = parse_srt(BASE / cena["srt"])
        for i, (ini, fim, texto) in enumerate(cues):
            t0 = offset + LEAD + ini
            t1 = offset + LEAD + fim
            # não deixa a legenda invadir o respiro final do segmento
            limite = offset + dseg - 0.12
            t1 = min(t1, limite)
            if i + 1 < len(cues):
                proximo = offset + LEAD + cues[i + 1][0] - 0.06
                t1 = min(t1, proximo)
            if t1 <= t0 + 0.2:
                continue
            blocos = [texto]
            total_chars = sum(len(b) for b in blocos)
            cursor = t0
            for j, bloco in enumerate(blocos):
                frac = len(bloco) / total_chars
                dur = (t1 - t0) * frac
                b_ini = cursor
                b_fim = t1 if j == len(blocos) - 1 else cursor + dur - 0.05
                cursor += dur
                if b_fim - b_ini < 0.5:
                    continue
                linhas.append(
                    f"Dialogue: 0,{ass_time(b_ini)},{ass_time(b_fim)},Legenda,,0,0,0,,{bloco}"
                )
                total_cues += 1
        offset += dseg
    ass = BUILD / "legendas.ass"
    ass.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    srt_final = BASE / "legendas.srt"
    n_srt = ass_para_srt(ass, srt_final)
    print(f"Legendas: {total_cues} blocos no ASS, {n_srt} no SRT, offset final {offset:.2f}s")

    # burn-in e encode final
    print("Queimando legendas e gerando o MP4 final...")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(normalizado),
        "-vf", f"ass={ass.as_posix()}",
        "-c:v", "libx264", "-preset", "slow", "-crf", "19",
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "copy", "-movflags", "+faststart",
        str(FINAL),
    ])
    print(f"OK: {FINAL} ({duracao(FINAL):.2f}s, {FINAL.stat().st_size/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
