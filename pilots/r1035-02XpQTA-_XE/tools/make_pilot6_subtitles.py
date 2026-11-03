#!/usr/bin/env python3
"""Build pilot PT-BR subtitles at line level from the reviewed fit dialogue."""
import json
import textwrap
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from integrations.video_cpu_pipeline import render_subtitles  # noqa: E402

dialogue = json.loads((ROOT / 'pilot-P0006/dialogue-dub-characters.json').read_text())
tts = json.loads((ROOT / 'pilot-P0006/tts-manifest-v2.json').read_text())
by_id = {unit['id']: unit for unit in tts['units']}
cues = []
for index, unit in enumerate(dialogue['units']):
    line = by_id[unit['id']]
    start = float(unit['start_part'])
    end = min(dialogue['part_duration_seconds'], start + float(line['final_seconds']))
    if index + 1 < len(dialogue['units']):
        next_start = float(dialogue['units'][index + 1]['start_part'])
        if next_start > start:
            end = min(end, next_start - 0.02)
    if end <= start:
        raise SystemExit(f'invalid cue: {unit["id"]}')
    text = '\n'.join(textwrap.wrap(unit['fit_text_pt'], width=42, break_long_words=False,
                                   break_on_hyphens=False))
    cues.append({'speaker': unit.get('character_id', unit['speaker']), 'start': round(start, 3),
                 'end': round(end, 3), 'text': text, 'words': [],
                 'cps': round(len(text.replace('\n', ' ')) / max(0.001, end - start), 2)})
content = render_subtitles(cues)
out = ROOT / 'pilot-P0006/subtitles-v2'
out.mkdir(parents=True, exist_ok=True)
for extension, text in content.items():
    path = out / f'subtitles.pt-BR.{extension}'
    if path.exists():
        raise SystemExit(f'refusing overwrite: {path}')
    path.write_text(text, encoding='utf-8')
(out / 'cues.json').write_text(json.dumps({
    'schema_version': 1,
    'part_id': dialogue['part_id'],
    'alignment': 'line_level_from_tts_manifest',
    'audio_bound': False,
    'cues': cues,
    'limitations': ['line-level subtitles, not word-level forced alignment',
                    'timing must be rechecked against the final mix',
                    'no audiovisual approval'],
}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'cues': len(cues), 'out': str(out)}, ensure_ascii=False))
