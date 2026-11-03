"""R1045: ASR large-v3 local por parte, com cache e retomada.

Não traduz, não diariza e não sintetiza. O modelo é carregado uma vez.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

VERSION = 'R1045-asr-1'


def cache_key(source_sha256, model, params):
    payload = json.dumps({'source': source_sha256, 'model': model,
                          'params': params, 'version': VERSION},
                         sort_keys=True, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name}: finite number required')
    return float(value)


def normalize_segments(segments):
    if not isinstance(segments, (list, tuple)):
        raise ValueError('segments list required')
    rows = []
    for segment in segments:
        text = segment.get('text')
        if not isinstance(text, str) or not text.strip():
            raise ValueError('empty ASR segment')
        start = _number(segment.get('start'), 'start')
        end = _number(segment.get('end'), 'end')
        if start < 0 or end <= start:
            raise ValueError('invalid ASR segment')
        rows.append({'start': round(start, 3), 'end': round(end, 3),
                     'text': text.strip()})
    return rows


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def transcribe_parts(root, model_dir, *, out_dir='.dubbing-asr-large',
                     limit=0, threads=8):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from integrations import dubbing_batch
    from faster_whisper import WhisperModel

    root = Path(root)
    status = dubbing_batch.status(root)
    batch_dir = dubbing_batch.confined_path(root, status['run_dir'])
    manifest = dubbing_batch.read_json(batch_dir / 'manifest.json')
    out = root / out_dir
    out.mkdir(exist_ok=True)
    tmp = Path('/tmp/opencode/asr-large')
    tmp.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(str(model_dir), device='cpu', compute_type='int8',
                         cpu_threads=threads, num_workers=1,
                         local_files_only=True)
    params = {'language': 'tr', 'beam_size': 1, 'vad_filter': True,
              'condition_on_previous_text': True, 'model': 'large-v3'}
    ids = manifest['part_ids'][:limit] if limit else manifest['part_ids']
    counts = {'parts': 0, 'cached': 0, 'segments': 0, 'words': 0}
    for pid in ids:
        source = dubbing_batch.confined_path(root, f'parts-final/parts/{pid}.mp4')
        target = out / f'{pid}.json'
        source_sha = _sha(source)
        key = cache_key(source_sha, 'large-v3', params)
        if target.exists():
            old = json.loads(target.read_text())
            if old.get('key') != key:
                raise ValueError(f'{pid}: ASR cache mismatch')
            counts['cached'] += 1
            continue
        wav = tmp / f'{pid}.wav'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(source),
                        '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le',
                        '-y', str(wav)], check=True, timeout=180)
        segments, info = model.transcribe(
            str(wav), language='tr', beam_size=1, vad_filter=True,
            word_timestamps=False, condition_on_previous_text=True)
        rows = normalize_segments([{'start': s.start, 'end': s.end, 'text': s.text}
                                   for s in segments])
        payload = {'schema_version': 1, 'version': VERSION, 'part_id': pid,
                   'key': key, 'source_sha256': source_sha, 'model': 'large-v3',
                   'language': info.language, 'language_probability': info.language_probability,
                   'segments': rows,
                   'status': 'asr_large_pending_source_review', 'verified': False,
                   'limitations': ['ASR is a draft; Turkish names/idioms may be wrong',
                                   'no native review']}
        with target.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
        counts['parts'] += 1
        counts['segments'] += len(rows)
        counts['words'] += sum(len(row['text'].split()) for row in rows)
        print(json.dumps({'part_id': pid, 'segments': len(rows),
                          'language_probability': round(info.language_probability, 3)}),
              flush=True)
        wav.unlink(missing_ok=True)
    print(json.dumps({'status': 'asr_large_complete_pending_review', **counts}))
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--model-dir', required=True)
    parser.add_argument('--out-dir', default='.dubbing-asr-large')
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--threads', type=int, default=8)
    args = parser.parse_args(argv)
    transcribe_parts(args.root, args.model_dir, out_dir=args.out_dir,
                     limit=args.limit, threads=args.threads)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
