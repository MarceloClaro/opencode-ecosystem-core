"""R1041: síntese por linha com cache, hash e limite estrito de duração.

O motor é injetado (nenhum modelo é importado aqui). Não há truncamento,
tolerância editorial, ASR de aprovação ou remoção de palavras. O texto pode
perder apenas o ponto final, e isso fica registrado no recibo.
"""
from __future__ import annotations

import argparse
import array
import hashlib
import json
import math
from pathlib import Path
import re
import wave

from integrations import dubbing_batch as batch

HEX = re.compile(r'[0-9a-f]{64}')


def normalize_tts_text(text):
    """Remove somente um ponto final; nunca altera palavras ou outros sinais."""
    if not isinstance(text, str):
        raise ValueError('text required')
    clean = ' '.join(text.split())
    if not clean:
        raise ValueError('nonempty text required')
    removed = clean.endswith('.')
    if removed:
        clean = clean[:-1].rstrip()
    if not clean:
        raise ValueError('text with content required')
    return clean, removed


def _write_wav(path, samples, sample_rate):
    values = array.array('h')
    for value in samples:
        number = float(value)
        if not math.isfinite(number):
            raise ValueError('non-finite sample')
        values.append(max(-32768, min(32767, int(round(number * 32767)))))
    with Path(path).open('xb') as handle:
        with wave.open(handle, 'wb') as stream:
            stream.setnchannels(1)
            stream.setsampwidth(2)
            stream.setframerate(sample_rate)
            stream.writeframes(values.tobytes())


def synthesize_line(root, unit, voice, engine, params, version):
    root = Path(root)
    if not isinstance(unit, dict):
        raise ValueError('unit object required')
    uid = unit.get('id')
    if not isinstance(uid, str) or not batch.ID.fullmatch(uid):
        raise ValueError('invalid unit ID')
    character = unit.get('character_id')
    if not isinstance(character, str) or not batch.ID.fullmatch(character):
        raise ValueError(f'{uid}: character unresolved')
    if not isinstance(voice, dict) or voice.get('reference_sha256') != unit.get('reference_sha256'):
        raise ValueError(f'{uid}: voice/reference unresolved')
    reference_sha = unit['reference_sha256']
    if not isinstance(reference_sha, str) or not HEX.fullmatch(reference_sha):
        raise ValueError(f'{uid}: invalid reference hash')
    raw_text = unit.get('translated_text')
    clean, period_removed = normalize_tts_text(raw_text)
    start, end = unit.get('start_part'), unit.get('end_part')
    if (isinstance(start, bool) or isinstance(end, bool) or not isinstance(start, (int, float))
            or not isinstance(end, (int, float)) or not math.isfinite(start)
            or not math.isfinite(end) or start < 0 or end <= start):
        raise ValueError(f'{uid}: invalid slot')
    if not isinstance(params, dict):
        raise ValueError('params object required')
    try:
        encoded = batch.canonical(params)
    except (TypeError, ValueError) as exc:
        raise ValueError('params must be finite JSON') from exc
    sample_rate = params.get('sample_rate', 24000)
    if sample_rate != 24000:
        raise ValueError('24000 Hz required by this engine contract')
    engine_name = getattr(engine, 'name', type(engine).__name__)
    key = batch.cache_key({'text': clean, 'raw_text': raw_text,
                           'reference_sha256': reference_sha,
                           'character_id': character, 'engine': engine_name},
                          {'params': json.loads(encoded), 'slot': [start, end]}, version)
    rel = f'.dubbing-tts/{version}/{key}'
    out = batch.confined_path(root, rel)
    manifest_path = out / 'take.json'
    if out.exists():
        data = batch.read_json(manifest_path)
        if data.get('key') != key:
            raise ValueError(f'{uid}: cache integrity mismatch')
        audio = batch.confined_path(root, f'{rel}/{data["audio"]}')
        if not audio.is_file() or batch.file_hash(audio) != data.get('sha256'):
            raise ValueError(f'{uid}: cached audio integrity mismatch')
        return {**data, 'cache_hit': True}
    samples = engine.synthesize(clean, voice['reference'], json.loads(encoded))
    if not isinstance(samples, (list, tuple)) or not samples:
        raise ValueError(f'{uid}: engine returned no samples')
    duration = len(samples) / sample_rate
    available = float(end) - float(start)
    if duration > available + 1e-9:
        raise ValueError(f'{uid}: overrun {duration:.3f}s > {available:.3f}s; '
                         'edit text or choose another take, never truncate')
    out.mkdir(parents=True, exist_ok=False)
    audio_name = 'take.wav'
    _write_wav(out / audio_name, samples, sample_rate)
    record = {'schema_version': 1, 'key': key, 'unit_id': uid,
              'character_id': character, 'text': clean, 'raw_text': raw_text,
              'final_period_removed': period_removed,
              'reference': voice['reference'], 'reference_sha256': reference_sha,
              'engine': engine_name, 'params': json.loads(encoded),
              'sample_rate': sample_rate, 'duration_seconds': round(duration, 6),
              'available_seconds': round(available, 6),
              'overrun_seconds': max(0.0, duration - available),
              'audio': audio_name, 'sha256': batch.file_hash(out / audio_name),
              'artifact': f'{rel}/{audio_name}',
              'cache_hit': False, 'text_screen': 'not_performed',
              'audiovisual_approved': False,
              'limitations': ['synthesis does not imply intelligibility or emotion approval',
                              'final period removal is recorded; words are not changed']}
    batch.write_new(manifest_path, record)
    return record


def synthesize_part(root, part, voices, engine, params, version):
    root = Path(root)
    if not isinstance(part, dict):
        raise ValueError('part object required')
    pid = part.get('part_id')
    if not isinstance(pid, str) or not batch.ID.fullmatch(pid):
        raise ValueError('invalid part ID')
    units = part.get('units')
    if not isinstance(units, list):
        raise ValueError('units list required')
    takes, failures = [], []
    for unit in units:
        character = unit.get('character_id') if isinstance(unit, dict) else None
        try:
            takes.append(synthesize_line(root, unit, (voices or {}).get(character),
                                         engine, params, version))
        except (ValueError, OSError) as exc:
            failures.append({'id': unit.get('id') if isinstance(unit, dict) else None,
                             'error': str(exc)})
    status = 'blocked' if failures or not units else 'tts_generated_pending_review'
    return {'schema_version': 1, 'part_id': pid, 'part_status': status,
            'takes': takes, 'failures': failures, 'promotable': False,
            'audiovisual_approved': False,
            'cache_hits': sum(t.get('cache_hit', False) for t in takes),
            'limitations': ['ASR/lexical review not performed here',
                            'no subtitle, mix or lip sync in this step']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--part', required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args(argv)
    # Deliberately refuses to guess a voice or load a model implicitly.
    print('Integração de motor XTTS exige referências e revisões; use a API '
          'dubbing_synth.synthesize_part com o motor aprovado.')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
