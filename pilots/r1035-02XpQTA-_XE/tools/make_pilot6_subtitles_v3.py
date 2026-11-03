#!/usr/bin/env python3
"""Turn-level PT-BR subtitles for the stem-based pilot, without overlaps."""
import json
import textwrap
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from integrations.video_cpu_pipeline import render_subtitles  # noqa: E402

turns = json.loads((ROOT / 'pilot-P0006/dialogue-turns.json').read_text())
tts = json.loads((ROOT / 'pilot-P0006/tts-manifest-v3.json').read_text())
by_id = {turn['id']: turn for turn in tts['turns']}
cues = []
for index, turn in enumerate(turns['turns']):
    line = by_id[turn['id']]
    start = float(turn['start_part'])
    end = min(turns['part_duration_seconds'], start + float(line['final_seconds']))
    if index + 1 < len(turns['turns']):
        next_start = float(turns['turns'][index + 1]['start_part'])
        if next_start > start:
            end = min(end, next_start - 0.02)
    if end <= start:
        raise SystemExit(f'invalid cue: {turn["id"]}')
    text = '\n'.join(textwrap.wrap(turn['fit_text_pt'], width=46,
                                   break_long_words=False, break_on_hyphens=False))
    cues.append({'speaker': turn['character_id'], 'start': round(start, 3),
                 'end': round(end, 3), 'text': text, 'words': [],
                 'cps': round(len(text.replace('\n', ' ')) / max(0.001, end - start), 2)})
content = render_subtitles(cues)
out = ROOT / 'pilot-P0006/subtitles-v3'
out.mkdir(parents=True, exist_ok=True)
for extension, text in content.items():
    path = out / f'subtitles.pt-BR.{extension}'
    if path.exists():
        raise SystemExit(f'refusing overwrite: {path}')
    path.write_text(text, encoding='utf-8')
(out / 'cues.json').write_text(json.dumps({
    'schema_version': 1,
    'part_id': turns['part_id'],
    'alignment': 'turn_level_from_tts_manifest_v3',
    'audio_bound': False,
    'cues': cues,
    'limitations': ['turn-level subtitles, not word-level forced alignment',
                    'timing must be rechecked against the final stem mix',
                    'no audiovisual approval'],
}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'cues': len(cues), 'out': str(out)}, ensure_ascii=False))
