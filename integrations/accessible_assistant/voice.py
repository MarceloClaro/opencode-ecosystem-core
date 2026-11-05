"""R1063 — voz local: microfone WSLg, ASR faster-whisper e TTS Edge."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import subprocess
import wave
from pathlib import Path

import numpy as np

PULSE_SERVER = "unix:/mnt/wslg/PulseServer"
PULSE_ENV = {**os.environ, "PULSE_SERVER": PULSE_SERVER}
ASR_PYTHON = Path("/home/marceloclaro/.cache/opencode-pilot/venvs/r1034-cpu/bin/python")
TTS_PYTHON = Path("/home/marceloclaro/.cache/opencode-pilot/venvs/edge-tts/bin/python")
CACHE = Path("~/.cache/opencode-pilot/accessible-tts").expanduser()


class VoiceError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def has_speech(path: Path, threshold: float = 250.0) -> bool:
    try:
        with wave.open(str(path), "rb") as stream:
            frames = stream.readframes(stream.getnframes())
    except (wave.Error, OSError):
        return False
    if not frames:
        return False
    samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
    if samples.size == 0:
        return False
    rms = float(np.sqrt(np.mean(samples * samples)))
    return rms >= threshold


def record_command(path: Path, seconds: int = 5) -> list[str]:
    return ["parecord", "--device=RDPSource", "--format=s16le", "--rate=16000",
            "--channels=1", "--file-format=wav", str(path)]


def record(seconds: int = 5, path: Path | None = None) -> Path:
    seconds = max(1, min(int(seconds), 30))
    target = Path(path or "/tmp/opencode/r1063-voice.wav")
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(["timeout", str(seconds + 1), *record_command(target, seconds)],
                                env=PULSE_ENV, capture_output=True, text=True,
                                timeout=seconds + 10, shell=False, check=False)
    except (subprocess.SubprocessError, OSError) as exc:
        raise VoiceError("RECORD_FAILED", "não foi possível gravar o microfone") from exc
    if result.returncode not in (0, 124):
        raise VoiceError("RECORD_FAILED", "parecord retornou erro")
    if not target.is_file() or target.stat().st_size < 1000:
        raise VoiceError("EMPTY_AUDIO", "microfone não produziu áudio")
    return target


def transcribe(path: Path) -> str:
    if not ASR_PYTHON.is_file():
        raise VoiceError("ASR_MISSING", "ambiente faster-whisper ausente")
    script = (
        "import json,sys\n"
        "from faster_whisper import WhisperModel\n"
        "m=WhisperModel('small',device='cpu',compute_type='int8',local_files_only=True)\n"
        "segs,_=m.transcribe(sys.argv[1],language='pt',vad_filter=True,beam_size=3)\n"
        "print(json.dumps({'text':' '.join(s.text.strip() for s in segs)}))\n"
    )
    try:
        result = subprocess.run([str(ASR_PYTHON), "-c", script, str(path)],
                                capture_output=True, text=True, timeout=180, shell=False)
    except (subprocess.SubprocessError, OSError) as exc:
        raise VoiceError("ASR_FAILED", "falha na transcrição") from exc
    if result.returncode != 0:
        raise VoiceError("ASR_FAILED", (result.stderr or "falha")[-500:])
    return json.loads(result.stdout.strip().splitlines()[-1]).get("text", "").strip()


def listen_once(seconds: int = 5) -> str:
    return transcribe(record(seconds))


def _tts_script(text: str, target: Path) -> str:
    return (
        "import asyncio,edge_tts\n"
        "async def main():\n"
        f"    await edge_tts.Communicate({text!r}, 'pt-BR-FranciscaNeural').save({str(target)!r})\n"
        "asyncio.run(main())\n"
    )


def speak(text: str) -> Path:
    text = (text or "").strip()
    if not text:
        raise VoiceError("TEXT_REQUIRED", "texto vazio")
    if len(text) > 2000:
        raise VoiceError("TEXT_TOO_LARGE", "texto acima de 2000 caracteres")
    CACHE.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    wav = CACHE / f"{digest}.wav"
    if not wav.is_file():
        mp3 = CACHE / f"{digest}.mp3"
        try:
            result = subprocess.run([str(TTS_PYTHON), "-c", _tts_script(text, mp3)],
                                    capture_output=True, text=True, timeout=120, shell=False)
        except (subprocess.SubprocessError, OSError) as exc:
            raise VoiceError("TTS_FAILED", "falha ao sintetizar voz") from exc
        if result.returncode != 0 or not mp3.is_file():
            raise VoiceError("TTS_FAILED", (result.stderr or "falha")[-500:])
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(mp3),
                        "-ar", "48000", "-ac", "2", str(wav)],
                       capture_output=True, timeout=60, shell=False, check=True)
    try:
        subprocess.run(["paplay", str(wav)], env=PULSE_ENV, capture_output=True,
                       timeout=120, shell=False, check=True)
    except (subprocess.SubprocessError, OSError) as exc:
        raise VoiceError("PLAYBACK_FAILED", "falha ao reproduzir áudio") from exc
    return wav
