#!/usr/bin/env python3
"""Gera a narração PT-BR do explainer de qubit (R1055).

Usa um speaker embutido do XTTS v2, sem clonar a voz do vídeo de referência.
O script grava WAVs por cena, concatena com pausas, gera SRT/ASS e uma timeline
JSON que o Remotion consome. Requer o venv XTTS do operador.
"""
from __future__ import annotations

import json
import re
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / "audio"
AUDIO.mkdir(exist_ok=True)
SNAPSHOT = next(
    Path("/home/marceloclaro/.cache/huggingface/hub/models--tts-hub--XTTS-v2/snapshots").iterdir()
)
SPEAKER = "Sofia Hellen"
SPEED = 1.25
FPS = 30
INTRO = 0.6
GAP = 0.35
OUTRO = 2.5

SCENES = [
    {
        "id": "01",
        "title": "O que é um qubit?",
        "tts": "Um bit é zero ou um. Um cúbit pode ser os dois... mas não do jeito que a internet diz. Pense numa moeda girando: enquanto gira, ela não é cara nem coroa.",
        "subtitle": "Um bit é 0 ou 1. Um qubit pode ser os dois — mas não do jeito que a internet diz. Pense numa moeda girando: ela não é cara nem coroa.",
        "speed": 1.2,
    },
    {
        "id": "02",
        "title": "Superposição",
        "tts": "Na física, isso é superposição: alfa vezes zero, mais beta vezes um. As amplitudes ao quadrado dão as probabilidades. Antes de medir, o cúbit evolui como uma onda.",
        "subtitle": "Na física, isso é superposição: α|0⟩ + β|1⟩. As amplitudes ao quadrado dão as probabilidades. Antes de medir, o qubit evolui como onda.",
        "speed": 1.3,
    },
    {
        "id": "03",
        "title": "Medição",
        "tts": "Agora, a pergunta-chave: o que acontece quando você mede? A onda colapsa. Você não vê a superposição; vê zero ou um. Na esfera de Bloch, as portas quânticas são rotações.",
        "subtitle": "Agora, a pergunta-chave: o que acontece quando você mede? A onda colapsa. Você não vê a superposição; vê 0 ou 1. Na esfera de Bloch, as portas são rotações.",
        "speed": 1.25,
    },
    {
        "id": "04",
        "title": "Emaranhamento",
        "tts": "Dois cúbits podem ser emaranhados. O estado de Bell correlaciona os resultados de um jeito que nenhuma teoria clássica local explica. Aspect, Cláuser e Zailínguer testaram isso. O Nobel de 2022 reconheceu.",
        "subtitle": "Dois qubits podem ser emaranhados. O estado de Bell correlaciona resultados que nenhuma teoria clássica local explica. Aspect, Clauser e Zeilinger testaram isso. O Nobel de 2022 reconheceu.",
        "speed": 1.3,
    },
    {
        "id": "05",
        "title": "Interferência e limite",
        "tts": "E o ganho? Não é testar tudo ao mesmo tempo. É interferência: amplificar os caminhos certos e cancelar os errados. O inimigo é a decoerência. Por isso, um cúbit lógico exige muitos cúbits físicos.",
        "subtitle": "E o ganho? Não é testar tudo ao mesmo tempo. É interferência: amplificar caminhos certos e cancelar errados. O inimigo é a decoerência. Um qubit lógico exige muitos qubits físicos.",
        "speed": 1.3,
    },
    {
        "id": "06",
        "title": "Uma porta, não mágica",
        "tts": "Resumindo: superposição, medição, emaranhamento e interferência. Cúbit é uma porta, não mágica.",
        "subtitle": "Resumindo: superposição, medição, emaranhamento e interferência. Qubit é uma porta, não mágica.",
        "speed": 1.1,
    },
    {
        "id": "07",
        "title": "Autor",
        "tts": "Muito obrigado por assistir! Este projeto é de Marcelo Claro Laranjeira. Para acompanhar, acesse github ponto com, barra, Marcelo Claro.",
        "subtitle": "Muito obrigado por assistir! Projeto de Marcelo Claro Laranjeira. Acesse github.com/MarceloClaro.",
        "speed": 1.0,
    },
]

def _duration(path: Path) -> float:
    with wave.open(str(path), "rb") as handle:
        return handle.getnframes() / handle.getframerate()


def _silence(seconds: float, rate: int, width: int, channels: int) -> bytes:
    return b"\x00" * int(seconds * rate) * width * channels


def _concat(paths: list[Path], target: Path, gaps: list[float]) -> float:
    params = None
    total = 0.0
    with wave.open(str(target), "wb") as out:
        for index, path in enumerate(paths):
            with wave.open(str(path), "rb") as source:
                if params is None:
                    params = source.getparams()
                    out.setparams(params)
                elif (source.getframerate(), source.getnchannels(), source.getsampwidth()) != (
                    params.framerate, params.nchannels, params.sampwidth
                ):
                    raise SystemExit("WAVs com formatos diferentes")
                out.writeframes(source.readframes(source.getnframes()))
                total += source.getnframes() / source.getframerate()
            if index < len(gaps):
                out.writeframes(_silence(gaps[index], params.framerate, params.sampwidth, params.nchannels))
                total += gaps[index]
    return total


def _srt_time(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours, millis = divmod(millis, 3600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _split_subtitle(text: str, max_chars: int = 84) -> list[str]:
    pieces = [
        part.strip()
        for part in re.split(r"(?<=[.!?;:])\s+", text)
        if part.strip()
    ]
    expanded: list[str] = []
    for piece in pieces:
        if len(piece) <= max_chars:
            expanded.append(piece)
            continue
        parts = [
            part.strip()
            for part in re.split(r"(?<=,)\s+", piece)
            if part.strip()
        ]
        if len(parts) > 1:
            expanded.extend(parts)
        else:
            expanded.append(piece)

    chunks: list[str] = []
    current = ""
    for piece in expanded:
        candidate = f"{current} {piece}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = piece
        else:
            current = candidate
    if current:
        chunks.append(current)

    merged: list[str] = []
    for chunk in chunks:
        if merged and (len(chunk.split()) < 3 or len(merged[-1].split()) < 3):
            merged[-1] = f"{merged[-1]} {chunk}".strip()
        else:
            merged.append(chunk)

    final: list[str] = []
    for chunk in merged:
        if len(chunk) <= max_chars:
            final.append(chunk)
            continue
        current = ""
        for word in chunk.split():
            candidate = f"{current} {word}".strip()
            if current and len(candidate) > max_chars:
                final.append(current)
                current = word
            else:
                current = candidate
        if current:
            final.append(current)
    return final


def main() -> int:
    from TTS.api import TTS

    tts = TTS(
        model_path=str(SNAPSHOT / "model.pth"),
        config_path=str(SNAPSHOT / "config.json"),
        progress_bar=False,
    )
    paths = []
    for scene in SCENES:
        target = AUDIO / f"scene-{scene['id']}.wav"
        if not target.exists():
            tts.tts_to_file(
                text=scene["tts"],
                file_path=str(target),
                speaker=SPEAKER,
                language="pt",
                speed=float(scene.get("speed", SPEED)),
                temperature=0.88,
                top_p=0.92,
                top_k=60,
                repetition_penalty=10.0,
                enable_text_splitting=False,
            )
        scene["duration"] = round(_duration(target), 3)
        paths.append(target)

    gaps = [GAP] * (len(paths) - 1)
    full = AUDIO / "narration.wav"
    total = _concat(paths, full, gaps)
    # Prepend intro and append outro using a second pass.
    with wave.open(str(full), "rb") as src:
        params = src.getparams()
        payload = src.readframes(src.getnframes())
    with wave.open(str(full), "wb") as out:
        out.setparams(params)
        out.writeframes(_silence(INTRO, params.framerate, params.sampwidth, params.nchannels))
        out.writeframes(payload)
        out.writeframes(_silence(OUTRO, params.framerate, params.sampwidth, params.nchannels))
    total = INTRO + total + OUTRO

    timeline = {
        "fps": FPS,
        "speaker": SPEAKER,
        "speed": SPEED,
        "intro": INTRO,
        "outro": OUTRO,
        "total_duration": round(total, 3),
        "scenes": [],
    }
    cursor = INTRO
    srt = []
    index = 1
    for scene in SCENES:
        start = cursor
        end = start + scene["duration"]
        timeline["scenes"].append({
            "id": scene["id"],
            "title": scene["title"],
            "start": round(start, 3),
            "end": round(end, 3),
            "duration": scene["duration"],
            "subtitle": scene["subtitle"],
        })
        chunks = _split_subtitle(scene["subtitle"])
        weights = [max(1, len(chunk.split())) for chunk in chunks]
        total_weight = sum(weights)
        chunk_start = start
        for chunk, weight in zip(chunks, weights):
            chunk_end = chunk_start + scene["duration"] * weight / total_weight
            srt.append(f"{index}\n{_srt_time(chunk_start)} --> {_srt_time(chunk_end)}\n{chunk}\n")
            index += 1
            chunk_start = chunk_end
        cursor = end + GAP

    (AUDIO / "timeline.json").write_text(
        json.dumps(timeline, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (AUDIO / "subtitles.srt").write_text("\n".join(srt), encoding="utf-8")
    print(json.dumps({
        "total_duration": timeline["total_duration"],
        "scenes": [
            {"id": s["id"], "start": s["start"], "end": s["end"]}
            for s in timeline["scenes"]
        ],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
