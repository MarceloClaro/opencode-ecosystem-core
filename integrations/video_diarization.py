"""R1044: diarização local com VAD Silero + ECAPA (SpeechBrain), sem modelos gated.

O resultado é uma hipótese: similaridade de embedding não prova identidade.
Locutor sem referência acima do limiar e da margem permanece bloqueado.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np

VERSION = 'R1044-1'


def _finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name}: finite number required')
    return float(value)


def merge_intervals(intervals, *, max_gap=0.2, min_duration=0.25):
    if not isinstance(intervals, list):
        raise ValueError('intervals list required')
    clean = []
    for item in intervals:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError('interval pair required')
        a, b = _finite(item[0], 'start'), _finite(item[1], 'end')
        if a < 0 or b <= a:
            raise ValueError('invalid interval')
        clean.append((a, b))
    clean.sort()
    merged = []
    for a, b in clean:
        if merged and a - merged[-1][1] <= max_gap:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return [(a, b) for a, b in merged if b - a >= min_duration]


def chunk_timestamps(intervals, *, max_window=2.0, min_window=0.4):
    if max_window <= 0 or min_window <= 0 or min_window > max_window:
        raise ValueError('invalid window sizes')
    chunks = []
    for a, b in merge_intervals(intervals, max_gap=0.2, min_duration=0.0):
        start = a
        while start < b - 1e-9:
            end = min(b, start + max_window)
            if end - start < min_window:
                if chunks:
                    chunks[-1] = (chunks[-1][0], max(chunks[-1][1], b))
                break
            chunks.append((round(start, 6), round(end, 6)))
            start = end
    return chunks


def normalize_vectors(vectors):
    array = np.asarray(vectors, dtype='float32')
    if array.ndim != 2 or array.shape[0] == 0 or array.shape[1] == 0:
        raise ValueError('2-D nonempty vectors required')
    if not np.isfinite(array).all():
        raise ValueError('finite vectors required')
    norms = np.linalg.norm(array, axis=1, keepdims=True)
    if np.any(norms <= 1e-12):
        raise ValueError('zero vector cannot be normalized')
    return array / norms


def online_cluster(vectors, *, threshold=0.65):
    if not 0 < threshold <= 1:
        raise ValueError('threshold in (0,1] required')
    array = normalize_vectors(vectors)
    labels = np.full(len(array), -1, dtype=int)
    centroids = []
    counts = []
    for index, vector in enumerate(array):
        if centroids:
            scores = [float(np.dot(vector, centroid)) for centroid in centroids]
            best = int(np.argmax(scores))
            if scores[best] >= threshold:
                labels[index] = best
                counts[best] += 1
                centroids[best] = ((centroids[best] * (counts[best] - 1) + vector)
                                   / counts[best])
                centroids[best] /= np.linalg.norm(centroids[best])
                continue
        labels[index] = len(centroids)
        centroids.append(vector.copy())
        counts.append(1)
    if not centroids:
        raise ValueError('no clusters')
    return labels, normalize_vectors(centroids)


def match_reference(vector, references, *, min_similarity=0.65, min_margin=0.05):
    if not references:
        return {'character_id': None, 'similarity': None, 'margin': None,
                'reason': 'no_references', 'verified': False}
    vector = normalize_vectors([vector])[0]
    rows = []
    for name, reference in references.items():
        ref = normalize_vectors([reference])[0]
        rows.append((float(np.dot(vector, ref)), name))
    rows.sort(reverse=True)
    best, name = rows[0]
    second = rows[1][0] if len(rows) > 1 else None
    margin = None if second is None else best - second
    if best < min_similarity:
        return {'character_id': None, 'similarity': best, 'margin': margin,
                'reason': 'low_similarity', 'verified': False}
    if margin is not None and margin < min_margin:
        return {'character_id': None, 'similarity': best, 'margin': margin,
                'reason': 'ambiguous_margin', 'verified': False}
    return {'character_id': name, 'similarity': best, 'margin': margin,
            'reason': 'matched_reference', 'verified': False}


def assign_speakers(chunks, mapping):
    rows = []
    for chunk in chunks:
        item = dict(chunk)
        found = mapping.get(chunk['cluster'])
        if found is None:
            found = mapping.get(str(chunk['cluster']), {})
        item['character_id'] = found.get('character_id')
        item['similarity'] = found.get('similarity')
        item['blocked'] = item['character_id'] is None
        item['verified'] = False
        rows.append(item)
    return rows


def decode_audio(path, *, start=None, end=None, sample_rate=16000):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('regular media file required')
    command = ['ffmpeg', '-nostdin', '-v', 'error']
    if start is not None:
        command += ['-ss', f'{_finite(start, "start"):.6f}']
    command += ['-i', str(path)]
    if end is not None:
        duration = _finite(end, 'end') - float(start or 0)
        if duration <= 0:
            raise ValueError('end must be after start')
        command += ['-t', f'{duration:.6f}']
    command += ['-vn', '-ac', '1', '-ar', str(sample_rate), '-f', 'f32le', 'pipe:1']
    proc = subprocess.run(command, capture_output=True, timeout=300, check=True)
    return np.frombuffer(proc.stdout, dtype='<f4').astype('float32')


def vad_intervals(audio, *, sample_rate=16000, min_silence=0.25, min_speech=0.25):
    try:
        import torch
        from silero_vad import get_speech_timestamps, load_silero_vad
    except ImportError as exc:
        raise ValueError('silero-vad/torch not installed') from exc
    model = load_silero_vad()
    timestamps = get_speech_timestamps(
        torch.from_numpy(np.asarray(audio, dtype='float32')), model,
        sampling_rate=sample_rate, min_silence_duration_ms=int(min_silence * 1000),
        min_speech_duration_ms=int(min_speech * 1000), return_seconds=True)
    return [(float(item['start']), float(item['end'])) for item in timestamps]


class SpeechBrainEncoder:
    name = 'speechbrain/spkrec-ecapa-voxceleb'

    def __init__(self, savedir, *, device='cpu', threads=4):
        try:
            import torch
            from speechbrain.inference.speaker import EncoderClassifier
        except ImportError as exc:
            raise ValueError('speechbrain/torch not installed') from exc
        torch.set_num_threads(threads)
        self._torch = torch
        self._model = EncoderClassifier.from_hparams(
            source=self.name, savedir=str(savedir), run_opts={'device': device})
        self.device = device
        self.sample_rate = 16000

    def embed(self, waveforms, *, batch_size=16):
        import torch
        rows = [np.asarray(w, dtype='float32') for w in waveforms]
        if any(w.ndim != 1 or len(w) < 400 for w in rows):
            raise ValueError('waveforms must be 1-D with at least 400 samples')
        outputs = []
        for offset in range(0, len(rows), batch_size):
            chunk = rows[offset:offset + batch_size]
            width = max(len(w) for w in chunk)
            padded = np.stack([np.pad(w, (0, width - len(w))) for w in chunk])
            batch = torch.from_numpy(padded)
            with torch.no_grad():
                vectors = self._model.encode_batch(batch).detach().cpu().numpy()
            outputs.append(vectors.reshape(len(chunk), -1))
        return normalize_vectors(np.concatenate(outputs, axis=0))


def diarize_audio(audio, encoder, references, *, sample_rate=16000,
                  cluster_threshold=0.65, min_similarity=0.65, min_margin=0.05,
                  max_window=2.0, min_window=0.4):
    intervals = vad_intervals(audio, sample_rate=sample_rate)
    chunks = chunk_timestamps(intervals, max_window=max_window, min_window=min_window)
    if not chunks:
        return {'status': 'no_speech', 'chunks': [], 'clusters': {},
                'blocked': True, 'verified': False}
    waveforms = []
    for start, end in chunks:
        a, b = int(round(start * sample_rate)), int(round(end * sample_rate))
        waveform = audio[a:b]
        if len(waveform) < 400:
            waveforms.append(np.pad(waveform, (0, 400 - len(waveform))))
        else:
            waveforms.append(waveform)
    vectors = encoder.embed(waveforms)
    labels, centroids = online_cluster(vectors, threshold=cluster_threshold)
    mapping = {}
    for cluster, centroid in enumerate(centroids):
        mapping[cluster] = match_reference(
            centroid, references, min_similarity=min_similarity, min_margin=min_margin)
    rows = []
    for (start, end), label in zip(chunks, labels):
        score = float(np.dot(normalize_vectors([vectors[len(rows)]])[0], centroids[label]))
        found = mapping[int(label)]
        rows.append({'start': start, 'end': end, 'cluster': int(label),
                     'cluster_similarity': round(score, 6),
                     'character_id': found['character_id'],
                     'similarity': found['similarity'],
                     'blocked': found['character_id'] is None,
                     'verified': False})
    return {'status': 'diarized_pending_review', 'chunks': rows,
            'clusters': {str(k): v for k, v in mapping.items()},
            'cluster_count': len(centroids), 'blocked': any(r['blocked'] for r in rows),
            'verified': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['vad', 'diarize'])
    parser.add_argument('--audio', required=True)
    parser.add_argument('--savedir', default='/home/marceloclaro/.cache/opencode-pilot/models/spkrec-ecapa-voxceleb')
    parser.add_argument('--out')
    parser.add_argument('--start', type=float)
    parser.add_argument('--end', type=float)
    parser.add_argument('--clusters', type=int, default=0)
    args = parser.parse_args(argv)
    audio = decode_audio(args.audio, start=args.start, end=args.end)
    if args.operation == 'vad':
        result = {'intervals': vad_intervals(audio)}
    else:
        encoder = SpeechBrainEncoder(args.savedir)
        result = diarize_audio(audio, encoder, {})
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        Path(args.out).write_text(text)
        print(json.dumps({'out': args.out, 'status': result.get('status')}))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
