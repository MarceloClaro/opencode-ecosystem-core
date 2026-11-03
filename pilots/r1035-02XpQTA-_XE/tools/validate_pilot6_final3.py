#!/usr/bin/env python3
"""Quality gate for final3: ASR similarity, duration, peak, click/high-band spike."""
import difflib
import json
import re
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
TURNS = json.loads((ROOT / 'pilot-P0006/dialogue-turns-reviewed.json').read_text())
TTS = json.loads((ROOT / 'pilot-P0006/tts-manifest-final3.json').read_text())
ASR = json.loads((ROOT / 'pilot-P0006/render-final3/dialogue-asr.json').read_text())
by_id = {t['id']: t for t in TTS['turns']}


def words(text):
    return re.findall(r'[a-zà-ÿ0-9]+', text.lower())


def similarity(expected, transcript):
    return difflib.SequenceMatcher(None, words(expected), words(transcript)).ratio()


def audio_metrics(path):
    x, sr = sf.read(str(path), dtype='float32', always_2d=True)
    x = x.mean(axis=1)
    peak = float(np.max(np.abs(x))) if len(x) else 0.0
    diff = float(np.max(np.abs(np.diff(x)))) if len(x) > 1 else 0.0
    # 10 ms high-band energy; a click/sibilance spike stands out
    ratios = []
    for start in range(0, max(1, len(x) - int(0.01 * sr)), int(0.01 * sr)):
        seg = x[start:start + int(0.01 * sr)]
        if len(seg) < 32:
            continue
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), 1 / sr)
        total = spec.sum() + 1e-12
        ratios.append(float(spec[(freqs >= 6000) & (freqs <= 12000)].sum() / total))
    return {'duration': len(x) / sr, 'peak': peak, 'max_diff': diff,
            'max_high_band_ratio': max(ratios) if ratios else 0.0}


rows = []
for turn in TURNS['turns']:
    item = by_id[turn['id']]
    start = float(turn['start_part'])
    end = start + max(float(item['final_seconds']), float(turn['slot_seconds']))
    texts = []
    for segment in ASR['segments']:
        mid = (segment['start'] + segment['end']) / 2
        if start - 0.10 <= mid <= end + 0.10:
            texts.append(segment['text'].strip())
    transcript = ' '.join(texts)
    sim = similarity(turn['fit_text_pt'], transcript)
    metrics = audio_metrics(ROOT / item['artifact'])
    checks = {
        'similarity_ok': sim >= 0.45,
        'duration_ok': metrics['duration'] <= float(item['available_seconds']) + 0.35,
        'peak_ok': metrics['peak'] < 0.99,
        'click_ok': metrics['max_high_band_ratio'] <= 0.55 and metrics['max_diff'] <= 0.55,
    }
    rows.append({'id': turn['id'], 'character_id': turn['character_id'],
                 'expected': turn['fit_text_pt'], 'asr': transcript,
                 'similarity': round(sim, 3), 'duration': round(metrics['duration'], 3),
                 'available': float(item['available_seconds']),
                 'peak': round(metrics['peak'], 4),
                 'max_high_band_ratio': round(metrics['max_high_band_ratio'], 3),
                 'max_diff': round(metrics['max_diff'], 4),
                 'checks': checks, 'passed': all(checks.values())})
report = {
    'schema_version': 1, 'part_id': TURNS['part_id'],
    'gate': {'min_similarity': 0.45, 'max_overrun_seconds': 0.35,
             'max_peak': 0.99, 'max_high_band_ratio': 0.55, 'max_diff': 0.55},
    'passed': sum(row['passed'] for row in rows), 'total': len(rows),
    'rows': rows,
    'limitations': ['ASR similarity is a proxy, not listening approval',
                    'high-band ratio can flag sibilance as well as clicks',
                    'names may lower similarity'],
}
(ROOT / 'pilot-P0006/quality-gate-final3.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n')
for row in rows:
    flag = 'OK' if row['passed'] else 'FAIL'
    bad = [k for k, v in row['checks'].items() if not v]
    print(f"{flag} {row['id']} {row['character_id']:14} sim={row['similarity']:.2f} "
          f"dur={row['duration']:.2f}/{row['available']:.2f} "
          f"hb={row['max_high_band_ratio']:.2f} diff={row['max_diff']:.2f} {bad}")
    if not row['passed']:
        print('  EXP:', row['expected'])
        print('  ASR:', row['asr'])
print(json.dumps({'passed': report['passed'], 'total': report['total']}))
