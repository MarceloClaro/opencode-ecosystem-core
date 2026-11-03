"""R1044: diarização local com Nemotron 3 Diarization (não gated).

Atribui unidades ASR a locutores com cobertura e margem; ambiguidade bloqueia.
Não sintetiza voz, não traduz e não prova identidade real.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

VERSION = 'R1044-1'
MODEL_ID = 'nvidia/Nemotron-3-Diarization'


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name}: finite number required')
    return float(value)


def cache_key(source_sha256, model_id, version):
    payload = json.dumps({'source': source_sha256, 'model': model_id,
                          'version': version}, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(payload.encode()).hexdigest()


def assign_units(units, segments, *, min_overlap=0.3, min_margin=0.15):
    if not isinstance(units, list):
        raise ValueError('units list required')
    if not isinstance(segments, list):
        raise ValueError('segments list required')
    clean_segments = []
    for segment in segments:
        if not isinstance(segment, dict):
            raise ValueError('segment object required')
        a = _number(segment.get('Start'), 'segment Start')
        b = _number(segment.get('End'), 'segment End')
        speaker = segment.get('Speaker')
        if a < 0 or b <= a or type(speaker) is not int or speaker < 0:
            raise ValueError('invalid segment')
        clean_segments.append((a, b, speaker))
    rows = []
    for unit in units:
        if not isinstance(unit, dict):
            raise ValueError('unit object required')
        raw_start = _number(unit.get('start_part'), 'unit start')
        raw_end = _number(unit.get('end_part'), 'unit end')
        if raw_end <= raw_start:
            raise ValueError('invalid unit interval')
        # Units crossing a part boundary are clipped to this part; the
        # neighbouring part owns the outside portion.
        start, end = max(0.0, raw_start), raw_end
        if end <= start:
            rows.append({'id': unit.get('id'), 'speaker': None,
                         'coverage': 0.0, 'margin': 0.0, 'blocked': True,
                         'reason': 'outside_part', 'verified': False})
            continue
        duration = end - start
        overlap = {}
        for a, b, speaker in clean_segments:
            left, right = max(start, a), min(end, b)
            if right > left:
                overlap[speaker] = overlap.get(speaker, 0.0) + (right - left)
        ordered = sorted(overlap.items(), key=lambda item: item[1], reverse=True)
        if not ordered:
            rows.append({'id': unit.get('id'), 'speaker': None,
                         'coverage': 0.0, 'margin': 0.0, 'blocked': True,
                         'reason': 'no_overlap', 'verified': False})
            continue
        speaker, best = ordered[0]
        second = ordered[1][1] if len(ordered) > 1 else 0.0
        coverage = best / duration
        margin = (best - second) / duration
        blocked = coverage < min_overlap or (len(ordered) > 1 and margin < min_margin)
        reason = ('low_coverage' if coverage < min_overlap else
                  'ambiguous' if blocked else 'assigned')
        rows.append({'id': unit.get('id'), 'speaker': speaker,
                     'coverage': round(coverage, 6), 'margin': round(margin, 6),
                     'blocked': blocked, 'reason': reason, 'verified': False})
    return rows


class NemotronDiarizer:
    def __init__(self, model_id=MODEL_ID, *, device='cpu', threads=4):
        try:
            import torch
            from transformers import AutoModelForAudioFrameClassification, AutoProcessor
        except ImportError as exc:
            raise ValueError('transformers/torch not installed') from exc
        torch.set_num_threads(threads)
        self._torch = torch
        self.model_id = model_id
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModelForAudioFrameClassification.from_pretrained(model_id)
        self.model.eval()
        self.device = device

    def diarize(self, audio):
        import numpy as np
        waveform = np.asarray(audio, dtype='float32')
        if waveform.ndim != 1 or len(waveform) < 1600:
            raise ValueError('mono 16 kHz waveform required')
        inputs = self.processor(waveform, sampling_rate=16000, return_tensors='pt')
        with self._torch.inference_mode():
            logits = self.model(**inputs).logits
        segments = self.processor.extract_speaker_dict(
            logits, inputs.get('attention_mask'))[0]
        return segments

    def diarize_file(self, path):
        from integrations.video_diarization import decode_audio
        return self.diarize(decode_audio(path))


def source_sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def write_new(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--out-dir', default='.dubbing-diarization')
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--model', default=MODEL_ID)
    args = parser.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from integrations import dubbing_batch

    root = Path(args.root)
    status = dubbing_batch.status(root)
    batch_dir = dubbing_batch.confined_path(root, status['run_dir'])
    manifest = dubbing_batch.read_json(batch_dir / 'manifest.json')
    model = NemotronDiarizer(args.model)
    out_dir = root / args.out_dir
    out_dir.mkdir(exist_ok=True)
    parts = manifest['part_ids'][:args.limit] if args.limit else manifest['part_ids']
    counts = {'parts': 0, 'cached': 0, 'units': 0, 'blocked': 0, 'speakers': 0}
    for pid in parts:
        source = dubbing_batch.confined_path(root, f'parts-final/parts/{pid}.mp4')
        target = out_dir / f'{pid}.json'
        sha = source_sha(source)
        key = cache_key(sha, args.model, VERSION)
        if target.exists():
            old = json.loads(target.read_text())
            if old.get('key') == key and old.get('source_sha256') == sha:
                counts['cached'] += 1
                continue
            raise ValueError(f'{pid}: existing diarization does not match source/model')
        part = dubbing_batch.read_json(batch_dir / 'parts' / f'{pid}.json')
        segments = model.diarize_file(source)
        rows = assign_units(part['units'], segments)
        payload = {'schema_version': 1, 'version': VERSION, 'part_id': pid,
                   'model': args.model, 'source_sha256': sha, 'key': key,
                   'segments': segments, 'units': rows,
                   'status': 'diarized_pending_review', 'verified': False,
                   'limitations': ['speaker indices are local to this part',
                                   'identity is not inferred from speaker index',
                                   'overlap/ambiguity blocks TTS assignment']}
        write_new(target, payload)
        counts['parts'] += 1
        counts['units'] += len(rows)
        counts['blocked'] += sum(1 for row in rows if row['blocked'])
        counts['speakers'] += len({s['Speaker'] for s in segments})
        print(json.dumps({'part_id': pid, 'segments': len(segments),
                          'units': len(rows), 'blocked': sum(1 for r in rows if r['blocked'])}),
              flush=True)
    print(json.dumps({'status': 'diarization_complete_pending_review', **counts}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
