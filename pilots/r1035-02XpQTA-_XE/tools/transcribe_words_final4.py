#!/usr/bin/env python3
"""Word-level ASR of final4 dialogue for per-turn validation."""
import json
from pathlib import Path
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / 'pilot-P0006/render-final4/dialogue-processed.wav'
MODEL = '/home/marceloclaro/.cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120'
model = WhisperModel(MODEL, device='cpu', compute_type='int8', cpu_threads=4,
                     num_workers=1, local_files_only=True)
segments, info = model.transcribe(str(AUDIO), language='pt', word_timestamps=True,
                                  vad_filter=False, beam_size=3,
                                  condition_on_previous_text=True)
words = []
for segment in segments:
    for word in (segment.words or []):
        words.append({'start': round(word.start, 3), 'end': round(word.end, 3),
                      'text': word.word.strip()})
payload = {'schema_version': 1, 'language': info.language,
           'duration': round(info.duration, 3), 'words': words}
(ROOT / 'pilot-P0006/render-final4/dialogue-words.json').write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'words': len(words), 'language': info.language}))
