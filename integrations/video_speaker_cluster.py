"""R1045: agrupa locutores entre partes e extrai referências provisórias.

Similaridade de embedding não prova identidade. Cada cluster vira um
`char_auto_XX` com referência própria e `verified: false`; nomes humanos ficam
para revisão. Não sintetiza voz.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np

VERSION = 'R1045-1'


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name}: finite number required')
    return float(value)


def choose_references(rows, labels, *, min_duration=0.8):
    if not isinstance(rows, list) or not rows:
        raise ValueError('rows required')
    labels = np.asarray(labels)
    if labels.shape[0] != len(rows):
        raise ValueError('label count mismatch')
    chosen = {}
    for row, label in zip(rows, labels):
        vector = np.asarray(row.get('vector'), dtype='float32')
        if vector.ndim != 1 or np.linalg.norm(vector) <= 1e-12:
            raise ValueError('nonzero vector required')
        start = _number(row.get('start'), 'start')
        end = _number(row.get('end'), 'end')
        if end <= start:
            raise ValueError('invalid segment')
        duration = end - start
        key = int(label)
        if key not in chosen or duration > chosen[key]['duration']:
            chosen[key] = {'index': row.get('index'), 'part_id': row.get('part_id'),
                           'start': start, 'end': end, 'duration': round(duration, 6),
                           'low_confidence': duration < min_duration}
    return chosen


def assign_units(units, segments, *, min_overlap=0.5, min_margin=0.1):
    if not isinstance(units, list) or not isinstance(segments, list):
        raise ValueError('units and segments lists required')
    clean = []
    for segment in segments:
        a = _number(segment.get('Start'), 'Start')
        b = _number(segment.get('End'), 'End')
        cluster = segment.get('cluster')
        if a < 0 or b <= a or type(cluster) is not int:
            raise ValueError('invalid segment')
        clean.append((a, b, cluster))
    rows = []
    for unit in units:
        if not isinstance(unit, dict):
            raise ValueError('unit object required')
        start = _number(unit.get('start_part'), 'unit start')
        end = _number(unit.get('end_part'), 'unit end')
        if end <= start:
            raise ValueError('invalid unit')
        start, end = max(0.0, start), end
        overlap = {}
        for a, b, cluster in clean:
            left, right = max(start, a), min(end, b)
            if right > left:
                overlap[cluster] = overlap.get(cluster, 0.0) + (right - left)
        if not overlap:
            rows.append({'id': unit.get('id'), 'cluster': None, 'coverage': 0.0,
                         'margin': 0.0, 'blocked': True, 'reason': 'no_overlap'})
            continue
        ordered = sorted(overlap.items(), key=lambda item: item[1], reverse=True)
        cluster, best = ordered[0]
        second = ordered[1][1] if len(ordered) > 1 else 0.0
        duration = end - start
        coverage = best / duration
        margin = (best - second) / duration
        blocked = coverage < min_overlap or (len(ordered) > 1 and margin < min_margin)
        reason = ('low_coverage' if coverage < min_overlap else
                  'ambiguous' if blocked else 'assigned')
        rows.append({'id': unit.get('id'), 'cluster': cluster,
                     'coverage': round(coverage, 6), 'margin': round(margin, 6),
                     'blocked': blocked, 'reason': reason})
    return rows


def match_clusters(centroids, references, *, min_similarity=0.65, min_margin=0.05):
    rows = {}
    for index, centroid in enumerate(np.asarray(centroids, dtype='float32')):
        vector = centroid / max(np.linalg.norm(centroid), 1e-12)
        scored = []
        for name, reference in references.items():
            ref = np.asarray(reference, dtype='float32')
            ref = ref / max(np.linalg.norm(ref), 1e-12)
            scored.append((float(np.dot(vector, ref)), name))
        scored.sort(reverse=True)
        best, name = scored[0] if scored else (None, None)
        second = scored[1][0] if len(scored) > 1 else None
        margin = None if second is None else best - second
        accepted = (best is not None and best >= min_similarity
                    and (margin is None or margin >= min_margin))
        rows[index] = {'nearest_known': name if accepted else None,
                       'similarity': None if best is None else round(best, 6),
                       'margin': None if margin is None else round(margin, 6)}
    return rows


def build_auto_speakers(references, matches, *, model, threshold):
    characters = {}
    for order, (cluster, ref) in enumerate(sorted(references.items()), 1):
        cid = f'char_auto_{order:02d}'
        match = matches.get(int(cluster), {})
        characters[cid] = {'reference': ref['path'], 'sha256': ref['sha256'],
                           'cluster': int(cluster), 'duration_seconds': ref['duration'],
                           'part_id': ref.get('part_id'), 'start': ref.get('start'),
                           'end': ref.get('end'),
                           'nearest_known': match.get('nearest_known'),
                           'similarity': match.get('similarity'),
                           'low_confidence': bool(ref.get('low_confidence')),
                           'verified': False, 'identity_verified': False}
    if len({c['sha256'] for c in characters.values()}) != len(characters):
        raise ValueError('duplicate reference hash across clusters')
    return {'schema_version': 1, 'status': 'provisional_unverified',
            'model': model, 'cluster_threshold': threshold,
            'characters': characters,
            'limitations': ['clusters are embedding hypotheses, not identity',
                            'references are extracted from the source',
                            'names/gender/age require human review']}


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def decode_segment(path, start, end, *, sample_rate=24000):
    start = _number(start, 'start')
    end = _number(end, 'end')
    if end <= start:
        raise ValueError('invalid segment')
    command = ['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{start:.6f}',
               '-i', str(path), '-t', f'{end - start:.6f}', '-vn', '-ac', '1',
               '-ar', str(sample_rate), '-f', 'f32le', 'pipe:1']
    proc = subprocess.run(command, capture_output=True, timeout=180, check=True)
    audio = np.frombuffer(proc.stdout, dtype='<f4').astype('float32')
    if len(audio) < 400:
        raise ValueError('segment too short for reference')
    return audio


def write_wav(path, audio, sample_rate=24000):
    import soundfile as sf
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), audio, sample_rate, subtype='PCM_16')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--out-dir', default='.dubbing-speakers')
    parser.add_argument('--threshold', type=float, default=0.55)
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--out-registry', default='voices/auto-speakers.json')
    parser.add_argument('--savedir', default='/home/marceloclaro/.cache/opencode-pilot/models/spkrec-ecapa-voxceleb')
    args = parser.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from integrations import dubbing_batch, video_diarization

    root = Path(args.root)
    diar = root / '.dubbing-diarization'
    files = sorted(diar.glob('*.json'))
    if args.limit:
        files = files[:args.limit]
    if not files:
        raise SystemExit('no diarization files')
    encoder = video_diarization.SpeechBrainEncoder(args.savedir)
    out = root / args.out_dir
    emb_dir = out / 'embeddings'
    emb_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in files:
        data = json.loads(path.read_text())
        pid = data['part_id']
        source = dubbing_batch.confined_path(root, f'parts-final/parts/{pid}.mp4')
        key = dubbing_batch.digest({'source': _sha(source), 'model': encoder.name,
                                    'version': VERSION})
        cache = emb_dir / f'{pid}.json'
        if cache.exists():
            cached = json.loads(cache.read_text())
            if cached.get('key') != key:
                raise ValueError(f'{pid}: embedding cache mismatch')
            items = cached['items']
        else:
            audio = video_diarization.decode_audio(source)
            waves, meta = [], []
            for index, segment in enumerate(data['segments']):
                start, end = float(segment['Start']), float(segment['End'])
                a, b = int(round(start * 16000)), int(round(end * 16000))
                wave = audio[a:b]
                if len(wave) < 400:
                    wave = np.pad(wave, (0, 400 - len(wave)))
                waves.append(wave)
                meta.append({'index': index, 'start': start, 'end': end,
                             'speaker': int(segment['Speaker'])})
            vectors = encoder.embed(waves) if waves else np.zeros((0, 192), dtype='float32')
            items = [{**m, 'vector': [round(float(x), 6) for x in v]}
                     for m, v in zip(meta, vectors)]
            with cache.open('x', encoding='utf-8') as stream:
                stream.write(json.dumps({'key': key, 'part_id': pid, 'items': items},
                                        ensure_ascii=False) + '\n')
        for item in items:
            rows.append({'part_id': pid, 'index': item['index'], 'start': item['start'],
                         'end': item['end'], 'speaker': item['speaker'],
                         'vector': np.asarray(item['vector'], dtype='float32')})
        print(json.dumps({'part_id': pid, 'segments': len(items), 'cached': cache.exists()}))
    if not rows:
        raise SystemExit('no segments to cluster')
    labels, centroids = video_diarization.online_cluster(
        [row['vector'] for row in rows], threshold=args.threshold)
    references = choose_references(rows, labels)
    # Known reference embeddings, if available; only a candidate label.
    known = {}
    registry_path = root / 'voices/voices.json'
    if registry_path.exists():
        registry = json.loads(registry_path.read_text())
        for cid, record in registry.get('characters', {}).items():
            try:
                audio = video_diarization.decode_audio(root / record['reference'])
                known[cid] = encoder.embed([audio])[0]
            except Exception:
                continue
    matches = match_clusters(centroids, known) if known else {}
    ref_dir = root / 'voices/auto-references'
    ref_dir.mkdir(parents=True, exist_ok=True)
    built = {}
    for cluster, ref in references.items():
        source = dubbing_batch.confined_path(
            root, f'parts-final/parts/{ref["part_id"]}.mp4')
        target = ref_dir / f'cluster-{int(cluster):02d}.wav'
        if not target.exists():
            audio = decode_segment(source, ref['start'], ref['end'], sample_rate=24000)
            write_wav(target, audio, 24000)
        built[int(cluster)] = {**ref, 'path': str(target.relative_to(root)),
                               'sha256': _sha(target)}
    registry = build_auto_speakers(built, matches, model=encoder.name,
                                   threshold=args.threshold)
    target = root / args.out_registry
    if target.exists():
        raise SystemExit(f'refusing overwrite: {target}')
    target.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n')
    # Assign clusters to units.
    cluster_map = {(row['part_id'], row['index']): int(labels[index])
                   for index, row in enumerate(rows)}
    assigned = {}
    for path in files:
        data = json.loads(path.read_text())
        segments = [{'Start': s['Start'], 'End': s['End'],
                     'cluster': cluster_map[(data['part_id'], i)]}
                    for i, s in enumerate(data['segments'])]
        units = assign_units(data['units'], segments)
        assigned[data['part_id']] = units
        (out / f'{data["part_id"]}.json').write_text(json.dumps({
            'schema_version': 1, 'part_id': data['part_id'], 'units': units,
            'status': 'clustered_pending_review', 'verified': False},
            ensure_ascii=False, indent=2) + '\n')
    summary = {'status': 'clustered_pending_review', 'parts': len(files),
               'segments': len(rows), 'clusters': len(centroids),
               'blocked_units': sum(1 for rows_ in assigned.values() for r in rows_ if r['blocked']),
               'characters': len(registry['characters']),
               'registry': str(target.relative_to(root)), 'verified': False}
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
