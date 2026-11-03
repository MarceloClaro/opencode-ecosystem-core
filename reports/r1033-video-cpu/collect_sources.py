"""Read-only public research; saves text receipts, never executes fetched code."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import http.client
import json
from pathlib import Path
import re
import urllib.request
import urllib.error

BASE = Path(__file__).resolve().parent
RECEIPTS = BASE / "sources"
REPOS = {
    "manim": "ManimCommunity/manim",
    "remotion": "remotion-dev/remotion",
    "faster-whisper": "SYSTRAN/faster-whisper",
    "whisper-cpp": "ggml-org/whisper.cpp",
    "pyannote": "pyannote/pyannote-audio",
    "whisperx": "m-bain/whisperX",
    "stable-ts": "jianfch/stable-ts",
    "coqui": "coqui-ai/TTS",
    "chatterbox": "resemble-ai/chatterbox",
    "openvoice": "myshell-ai/OpenVoice",
    "piper": "OHF-Voice/piper1-gpl",
    "pyvideotrans": "pyvideotrans/pyvideotrans",
    "videolingo": "Huanshere/VideoLingo",
    "sonitranslate": "R3gm/SoniTranslate",
    "musetalk": "TMElyralab/MuseTalk",
    "latentsync": "bytedance/LatentSync",
    "audio-separator": "nomadkaraoke/python-audio-separator",
}


def get(id_, url, suffix="txt"):
    record = {"id": id_, "url": url, "retrieved_at": datetime.now(timezone.utc).isoformat()}
    file = RECEIPTS / f"{id_}.{suffix}"
    receipt = RECEIPTS / f"{id_}.receipt.json"
    if file.exists():
        content = file.read_bytes()
        if receipt.exists():
            return json.loads(receipt.read_text()), content
        record.update(
            retrieved_at=datetime.fromtimestamp(file.stat().st_mtime, timezone.utc).isoformat(),
            acquisition_note="Recovered from completed save before collector interruption; timestamp from file mtime, no second request.",
            file=str(file.relative_to(BASE)), bytes=len(content), sha256=hashlib.sha256(content).hexdigest(),
        )
        receipt.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        return record, content
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "OpenCode-readonly-research/1.0"})
        with urllib.request.urlopen(request, timeout=35) as response:
            content = response.read(10_000_001)
            if len(content) > 10_000_000:
                raise ValueError("Public text exceeds 10 MB research limit")
            record["http_status"] = response.status
            record["final_url"] = response.url
        file.write_bytes(content)
        record.update(file=str(file.relative_to(BASE)), bytes=len(content), sha256=hashlib.sha256(content).hexdigest())
        receipt.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        return record, content
    except (OSError, http.client.HTTPException, ValueError) as error:
        record["error"] = str(error)
        receipt.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        return record, b""


def repo_source(item):
    id_, repo = item
    records = []
    record, raw = get(id_ + "-repo", "https://api.github.com/repos/" + repo, "json")
    records.append(record)
    if not raw:
        return records
    meta = json.loads(raw)
    branch = meta.get("default_branch", "main")
    # README names queried from GitHub, not guessed from local implementation.
    record, raw = get(id_ + "-readme-meta", "https://api.github.com/repos/" + repo + "/readme", "json")
    records.append(record)
    if raw:
        readme = json.loads(raw)
        if readme.get("download_url"):
            record, _ = get(id_ + "-readme", readme["download_url"], "md")
            records.append(record)
    return records


if __name__ == "__main__":
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    records = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for group in pool.map(repo_source, REPOS.items()):
            records.extend(group)
    extras = {
        "xtts-model": "https://huggingface.co/coqui/XTTS-v2/raw/main/README.md",
        "pyannote-model": "https://huggingface.co/pyannote/speaker-diarization-community-1/raw/main/README.md",
        "chatterbox-model": "https://huggingface.co/ResembleAI/chatterbox/raw/main/README.md",
        "ffmpeg-filters": "https://ffmpeg.org/ffmpeg-filters.html",
        "ffmpeg-legal": "https://ffmpeg.org/legal.html",
        "remotion-license": "https://raw.githubusercontent.com/remotion-dev/remotion/main/LICENSE.md",
        "playlist-page": "https://www.youtube.com/playlist?list=PL2dcm-6042EC788TGxgH3qWF7MjpoJIv9",
    }
    for id_, url in extras.items():
        record, _ = get(id_, url)
        records.append(record)
    (BASE / "source-index.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
    for record in records:
        print(record["id"], record.get("http_status", record.get("error")), record.get("bytes", 0))
