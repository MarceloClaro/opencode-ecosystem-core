#!/usr/bin/env python3
"""Gera a narração PT-BR do explainer de qubit (R1055) com voz neural Edge.

A voz é sintética e não clona nenhuma gravação de terceiro. O roteiro é
dividido em batidas curtas: cada batida tem ritmo e pausa próprios, o que
permite construir uma sequência emocional (curiosidade → explicação →
surpresa → síntese → agradecimento) em vez de um bloco único.

Requer o venv `edge-tts` e conexão com o serviço de voz neural.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / "audio"
AUDIO.mkdir(exist_ok=True)
VOICE = "pt-BR-FranciscaNeural"
FPS = 30
INTRO = 0.4
SCENE_GAP = 0.45
OUTRO = 2.2

# (texto para o TTS, texto da legenda, ritmo, pausa depois)
SCENES = [
    {
        "id": "01",
        "title": "O que é um qubit?",
        "beats": [
            ("Sabe o que é um cúbit?", "Sabe o que é um qubit?", 1.06, 0.30),
            ("Não é um bit menor.", "Não é um bit menor.", 1.02, 0.20),
            (
                "É outra unidade de informação.",
                "É outra unidade de informação.",
                1.08,
                0.35,
            ),
            (
                "Pensa numa moeda girando: enquanto gira, ela não é cara nem coroa.",
                "Pensa numa moeda girando: enquanto gira, ela não é cara nem coroa.",
                1.08,
                0.35,
            ),
            (
                "Ela é as duas possibilidades.",
                "Ela é as duas possibilidades.",
                1.08,
                0.30,
            ),
            (
                "Só quando para, você vê um resultado.",
                "Só quando para, você vê um resultado.",
                1.05,
                0.50,
            ),
        ],
    },
    {
        "id": "02",
        "title": "Superposição",
        "beats": [
            (
                "Na física, isso é superposição: álfa vezes zero, mais beta vezes um.",
                "Na física, isso é superposição: α|0⟩ + β|1⟩.",
                1.08,
                0.30,
            ),
            (
                "O quadrado de cada amplitude dá a probabilidade de medir zero ou um.",
                "O quadrado de cada amplitude dá a probabilidade de medir 0 ou 1.",
                1.06,
                0.30,
            ),
            (
                "Antes de medir, ele evolui como uma onda.",
                "Antes de medir, ele evolui como uma onda.",
                1.04,
                0.50,
            ),
        ],
    },
    {
        "id": "03",
        "title": "Medição",
        "beats": [
            (
                "Agora vem a parte que confunde.",
                "Agora vem a parte que confunde.",
                1.06,
                0.25,
            ),
            ("O que acontece quando você mede?", "O que acontece quando você mede?", 1.04, 0.25),
            (
                "A onda colapsa: você vê zero ou um.",
                "A onda colapsa: você vê 0 ou 1.",
                1.02,
                0.40,
            ),
            (
                "Na esfera de Bloch, as portas quânticas são rotações.",
                "Na esfera de Bloch, as portas quânticas são rotações.",
                1.06,
                0.50,
            ),
        ],
    },
    {
        "id": "04",
        "title": "Emaranhamento",
        "beats": [
            (
                "Dois cúbits podem ser emaranhados.",
                "Dois qubits podem ser emaranhados.",
                1.06,
                0.30,
            ),
            (
                "O estado de Bel correlaciona resultados que nenhuma teoria clássica local explica.",
                "O estado de Bell correlaciona resultados que nenhuma teoria clássica local explica.",
                1.06,
                0.35,
            ),
            (
                "Aspéct, Cláuser e Zailínguer testaram — e o Nobel de 2022 reconheceu.",
                "Aspect, Clauser e Zeilinger testaram — e o Nobel de 2022 reconheceu.",
                1.04,
                0.50,
            ),
        ],
    },
    {
        "id": "05",
        "title": "Interferência e limite",
        "beats": [
            (
                "O ganho não é testar tudo ao mesmo tempo.",
                "O ganho não é testar tudo ao mesmo tempo.",
                1.06,
                0.25,
            ),
            (
                "É interferência: amplificar os caminhos certos e cancelar os errados.",
                "É interferência: amplificar os caminhos certos e cancelar os errados.",
                1.06,
                0.35,
            ),
            (
                "O inimigo é a decoerência: por isso, um cúbit lógico exige muitos cúbits físicos.",
                "O inimigo é a decoerência: por isso, um qubit lógico exige muitos qubits físicos.",
                1.06,
                0.50,
            ),
        ],
    },
    {
        "id": "06",
        "title": "Origem",
        "beats": [
            (
                "Essa ideia não nasceu num só lugar.",
                "Essa ideia não nasceu num só lugar.",
                1.04,
                0.30,
            ),
            (
                "Copenhague, Viena e Leipzig.",
                "Copenhague, Viena e Leipzig.",
                1.06,
                0.35,
            ),
            (
                "Feynman propôs computar com ela, na Califórnia, em 1982.",
                "Feynman propôs computar com ela, na Califórnia, em 1982.",
                1.06,
                0.35,
            ),
            (
                "Schumacher batizou o cúbit em Ohio, em 1995.",
                "Schumacher batizou o qubit em Ohio, em 1995.",
                1.06,
                0.35,
            ),
            (
                "E o Nobel de 2022 veio de Paris, Berkeley e Viena.",
                "E o Nobel de 2022 veio de Paris, Berkeley e Viena.",
                1.04,
                0.50,
            ),
        ],
    },
    {
        "id": "07",
        "title": "Autor",
        "beats": [
            ("Muito obrigado por assistir.", "Muito obrigado por assistir.", 1.02, 0.30),
            (
                "Este projeto é de Marcelo Claro Laranjeira. O QR code leva ao GitHub.",
                "Projeto de Marcelo Claro Laranjeira. O QR code leva ao GitHub.",
                1.02,
                0.50,
            ),
        ],
    },
]


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
                    params.framerate,
                    params.nchannels,
                    params.sampwidth,
                ):
                    raise SystemExit("WAVs com formatos diferentes")
                out.writeframes(source.readframes(source.getnframes()))
                total += source.getnframes() / source.getframerate()
            if index < len(gaps):
                out.writeframes(
                    _silence(gaps[index], params.framerate, params.sampwidth, params.nchannels)
                )
                total += gaps[index]
    return total


def _srt_time(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours, millis = divmod(millis, 3600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _wrap(text: str, max_chars: int = 84) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > max_chars:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


async def _synth_beats() -> list[dict]:
    import edge_tts

    rendered = []
    for scene in SCENES:
        scene_dir = AUDIO / f"beats-{scene['id']}"
        scene_dir.mkdir(exist_ok=True)
        beats = []
        for index, (tts_text, subtitle, rate, pause) in enumerate(scene["beats"]):
            mp3 = scene_dir / f"{index:02d}.mp3"
            wav = scene_dir / f"{index:02d}.wav"
            percent = round((rate - 1) * 100)
            sign = "+" if percent >= 0 else ""
            if not mp3.exists():
                communicate = edge_tts.Communicate(
                    tts_text,
                    VOICE,
                    rate=f"{sign}{percent}%",
                )
                await communicate.save(str(mp3))
            if not wav.exists():
                subprocess.run(
                    [
                        "ffmpeg",
                        "-nostdin",
                        "-v",
                        "error",
                        "-y",
                        "-i",
                        str(mp3),
                        "-ar",
                        "24000",
                        "-ac",
                        "1",
                        str(wav),
                    ],
                    check=True,
                )
            beats.append(
                {
                    "index": index,
                    "text": subtitle,
                    "rate": rate,
                    "pause": pause,
                    "path": str(wav),
                    "duration": round(_duration(wav), 3),
                    "sha256": _sha(wav),
                }
            )
        rendered.append({**scene, "beats": beats})
    return rendered


def main() -> int:
    scenes = asyncio.run(_synth_beats())

    timeline = {
        "schema": "r1055-timeline-2",
        "fps": FPS,
        "voice": VOICE,
        "service": "edge-tts",
        "cloned": False,
        "intro": INTRO,
        "scene_gap": SCENE_GAP,
        "outro": OUTRO,
        "total_duration": None,
        "scenes": [],
    }
    scene_paths = []
    cursor = INTRO
    srt: list[str] = []
    srt_index = 1

    for scene in scenes:
        scene_audio = AUDIO / f"scene-{scene['id']}.wav"
        gaps = [beat["pause"] for beat in scene["beats"][:-1]]
        paths = [Path(beat["path"]) for beat in scene["beats"]]
        duration = _concat(paths, scene_audio, gaps)
        scene_paths.append(scene_audio)
        start = cursor
        end = start + duration
        captions = []
        beat_cursor = start
        for beat_index, beat in enumerate(scene["beats"]):
            beat_end = beat_cursor + beat["duration"]
            captions.append(
                {
                    "start": round(beat_cursor, 3),
                    "end": round(beat_end, 3),
                    "text": beat["text"],
                }
            )
            lines = _wrap(beat["text"])
            if len(lines) > 1:
                total_chars = sum(len(line) for line in lines)
                line_cursor = beat_cursor
                for line in lines:
                    line_end = line_cursor + beat["duration"] * len(line) / total_chars
                    srt.append(
                        f"{srt_index}\n{_srt_time(line_cursor)} --> {_srt_time(line_end)}\n{line}\n"
                    )
                    srt_index += 1
                    line_cursor = line_end
            else:
                srt.append(
                    f"{srt_index}\n{_srt_time(beat_cursor)} --> {_srt_time(beat_end)}\n{beat['text']}\n"
                )
                srt_index += 1
            beat_cursor = beat_end + (beat["pause"] if beat_index < len(scene["beats"]) - 1 else 0)

        timeline["scenes"].append(
            {
                "id": scene["id"],
                "title": scene["title"],
                "start": round(start, 3),
                "end": round(end, 3),
                "duration": round(duration, 3),
                "subtitle": " ".join(beat["text"] for beat in scene["beats"]),
                "captions": captions,
            }
        )
        cursor = end + SCENE_GAP

    full = AUDIO / "narration.wav"
    total = _concat(scene_paths, full, [SCENE_GAP] * (len(scene_paths) - 1))
    with wave.open(str(full), "rb") as source:
        params = source.getparams()
        payload = source.readframes(source.getnframes())
    with wave.open(str(full), "wb") as out:
        out.setparams(params)
        out.writeframes(_silence(INTRO, params.framerate, params.sampwidth, params.nchannels))
        out.writeframes(payload)
        out.writeframes(_silence(OUTRO, params.framerate, params.sampwidth, params.nchannels))
    total = INTRO + total + OUTRO
    timeline["total_duration"] = round(total, 3)
    timeline["narration_sha256"] = _sha(full)

    (AUDIO / "timeline.json").write_text(
        json.dumps(timeline, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (AUDIO / "subtitles.srt").write_text("\n".join(srt), encoding="utf-8")
    print(
        json.dumps(
            {
                "voice": VOICE,
                "total_duration": timeline["total_duration"],
                "scenes": [
                    {"id": scene["id"], "start": scene["start"], "end": scene["end"]}
                    for scene in timeline["scenes"]
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
