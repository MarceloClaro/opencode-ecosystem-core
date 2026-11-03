"""R1041: preparação, triagem e hooks locais. Preparado NÃO significa dublado.

Sem modelos carregados, subprocessos, rede ou aprovação perceptual automática.
Escritas confinadas em .dubbing-batch; snapshots imutáveis, lock e hashes.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
import fcntl
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import unicodedata
import wave

VERSION = 'R1041-1'
MAX_JSON = 32 * 1024 * 1024
ID = re.compile(r'[A-Za-z0-9_-]{1,80}')


def canonical(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False)


def digest(data):
    return hashlib.sha256(canonical(data).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def cache_key(inputs, parameters, version=VERSION):
    return digest({'inputs': inputs, 'parameters': parameters, 'version': version})


def confined_path(root, relative):
    root = Path(root).absolute()
    p = Path(relative)
    if p.is_absolute() or not p.parts or any(c in ('.', '..') for c in p.parts):
        raise ValueError('relative confined path required')
    target = root / p
    for node in (target, *target.parents):
        if node.is_symlink():
            raise ValueError('symlink not allowed')
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('path outside root')
    return target


def read_json(path):
    path = Path(path)
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_JSON:
        raise ValueError('JSON missing, symlink or too large')
    return json.loads(path.read_text(encoding='utf-8'),
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def write_new(path, data):
    with Path(path).open('x', encoding='utf-8') as stream:
        stream.write(canonical(data) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name}: finite number required')
    return float(value)


def partition_source(plan, asr):
    """One ASR segment -> one owner; context has IDs only and is not dubbed twice."""
    try:
        fps = float(Fraction(plan['fps']))
    except (TypeError, ValueError, ZeroDivisionError, KeyError) as exc:
        raise ValueError('invalid fps') from exc
    if not 0 < fps <= 240:
        raise ValueError('invalid fps')
    total = plan.get('total_frames')
    if type(total) is not int or total <= 0:
        raise ValueError('total_frames must be positive integer')
    source_parts = plan.get('segments')
    if not isinstance(source_parts, list) or not source_parts:
        raise ValueError('parts required')
    parts, ids, previous = [], set(), 0
    for item in source_parts:
        pid = item.get('id')
        a, b = item.get('start_frame'), item.get('end_frame')
        if not isinstance(pid, str) or not ID.fullmatch(pid) or pid in ids:
            raise ValueError('invalid or duplicate part ID')
        if type(a) is not int or type(b) is not int or a != previous or not a < b <= total:
            raise ValueError('frame coverage gap/overlap or invalid frames')
        ids.add(pid)
        previous = b
        parts.append({'part_id': pid, 'start_frame': a, 'end_frame': b,
                      'start_seconds': a / fps, 'end_seconds': b / fps,
                      'units': [], 'context_unit_ids': [],
                      'status': 'source_draft', 'blockers': ['source_review_pending',
                          'speaker_mapping_pending', 'translation_review_pending',
                          'performance_review_pending'],
                      'audiovisual_approved': False})
    if previous != total:
        raise ValueError('incomplete frame coverage')
    audio_end = number(asr.get('duration'), 'ASR duration')
    if abs(audio_end - total / fps) > 1.0:
        raise ValueError('ASR/plan duration mismatch')
    segments = asr.get('segments')
    if not isinstance(segments, list):
        raise ValueError('ASR segments required')
    units = []
    for idx, segment in enumerate(segments, 1):
        text = segment.get('text')
        if not isinstance(text, str) or not text.strip():
            raise ValueError('empty ASR segment: reconcile instead of silently skipping')
        a, b = number(segment.get('start'), 'start'), number(segment.get('end'), 'end')
        if not 0 <= a < b <= audio_end + 1e-6:
            raise ValueError('invalid ASR interval')
        mid = (a + b) / 2
        owner = next((p for p in parts if p['start_seconds'] <= mid < p['end_seconds']), None)
        if owner is None:
            raise ValueError('ASR unit outside video; explicit reconciliation required')
        crosses = a < owner['start_seconds'] or b > owner['end_seconds']
        unit = {'id': f'U{idx:05d}', 'start_source': a, 'end_source': b,
                'start_part': a - owner['start_seconds'],
                'end_part': b - owner['start_seconds'], 'source_text': text.strip(),
                'character_id': None, 'speaker': None, 'source_review': 'pending',
                'translation_review': 'pending', 'intent_review': 'pending',
                'translated_text': None, 'crosses_boundary': crosses,
                'source_asr_index': idx - 1,
                'low_confidence_word_count': sum(
                    1 for w in segment.get('words', [])
                    if number(w.get('probability', 0), 'probability') < 0.6)}
        owner['units'].append(unit)
        units.append(unit)
        if crosses and 'boundary_review_pending' not in owner['blockers']:
            owner['blockers'].append('boundary_review_pending')
    for p in parts:
        own_ids = {u['id'] for u in p['units']}
        p['context_unit_ids'] = [u['id'] for u in units if u['id'] not in own_ids
                                and u['end_source'] > p['start_seconds'] - 2
                                and u['start_source'] < p['end_seconds'] + 2]
        if not p['units']:
            p['blockers'].append('no_asr_requires_review')
    return parts


def tokens(text):
    if not isinstance(text, str):
        raise ValueError('text required')
    return re.findall(r'[^\W_]+', unicodedata.normalize('NFC', text).casefold())


def compare_transcript(expected, actual):
    a, b = tokens(expected), tokens(actual)
    if not a:
        raise ValueError('nonempty expected speech required')
    previous = list(range(len(b) + 1))
    for i, word in enumerate(a, 1):
        current = [i]
        for j, other in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1,
                               previous[j - 1] + (word != other)))
        previous = current
    return {'screen_pass': a == b, 'edit_distance': previous[-1],
            'expected_tokens': len(a), 'recognized_tokens': len(b),
            'audiovisual_approved': False,
            'reason': 'lexical_match_only' if a == b else 'asr_discrepancy_requires_review'}


def check_timing(*, start, samples, sample_rate, part_end, next_start=None):
    a = number(start, 'start')
    end = number(part_end, 'part_end')
    if type(samples) is not int or samples <= 0 or type(sample_rate) is not int or sample_rate <= 0:
        raise ValueError('positive sample count/rate required')
    if a < 0 or end <= a:
        raise ValueError('invalid slot')
    limit = end if next_start is None else min(end, number(next_start, 'next_start'))
    if limit <= a:
        raise ValueError('overlapping/nonordered start')
    duration = samples / sample_rate
    overrun = max(0.0, a + duration - limit)
    return {'screen_pass': overrun <= 1e-8, 'duration_seconds': duration,
            'overrun_seconds': overrun, 'end_seconds': a + duration,
            'limit_seconds': limit, 'audiovisual_approved': False}


def review_bound(review, subject):
    return (isinstance(review, dict) and review.get('status') == 'reviewed'
            and review.get('subject_sha256') == digest(subject)
            and bool(review.get('reviewer')) and bool(review.get('evidence')))


def preflight(stage, payload):
    """Fail closed. Editorial records are declarations, not proof of listening."""
    blockers = []
    if not isinstance(payload, dict):
        return {'allow': False, 'blockers': ['invalid_payload']}
    if stage == 'prepare':
        try:
            partition_source(payload['plan'], payload['asr'])
        except (ValueError, KeyError, TypeError, AttributeError):
            blockers.append('invalid_source_plan')
    elif stage in ('translate', 'tts'):
        units = payload.get('units')
        if not isinstance(units, list) or not units:
            blockers.append('nonempty_reviewed_units_required')
        else:
            for u in units:
                if not isinstance(u, dict):
                    blockers.append('invalid_unit')
                    continue
                uid = u.get('id', '?')
                source = {k: u.get(k) for k in ('source_text', 'start_source', 'end_source')}
                if not review_bound(u.get('source_review'), source):
                    blockers.append(f'{uid}:source_review_pending')
                if u.get('crosses_boundary') is not False:
                    blockers.append(f'{uid}:boundary_review_pending')
                if stage == 'tts':
                    target = {**source, 'translated_text': u.get('translated_text')}
                    if not review_bound(u.get('translation_review'), target):
                        blockers.append(f'{uid}:translation_review_pending')
                    voice = payload.get('voices', {}).get(u.get('character_id'))
                    if (not isinstance(voice, dict) or voice.get('integrity_checked') is not True
                            or voice.get('reference_sha256') != u.get('reference_sha256')
                            or not voice.get('reference_sha256') or not u.get('speaker')):
                        blockers.append(f'{uid}:voice_unresolved')
                    intent = {**target, 'character_id': u.get('character_id')}
                    if not review_bound(u.get('intent_review'), intent):
                        blockers.append(f'{uid}:intent_review_pending')
    elif stage in ('render', 'assemble'):
        # No promotion endpoint until signed/bound media receipts are implemented.
        blockers.append('media_release_not_implemented_requires_bound_audiovisual_receipts')
    else:
        blockers.append('unsupported_stage')
    return {'allow': not blockers, 'stage': stage, 'blockers': blockers,
            'perceptual_approval': False}


def guarded(stage, payload, action):
    """Actual pre-effect hook; exceptions deny and callback is not invoked."""
    try:
        verdict = preflight(stage, payload)
    except Exception as exc:
        raise ValueError('hook error: action blocked') from exc
    if verdict.get('allow') is not True:
        raise ValueError('hook blocked: ' + ','.join(verdict.get('blockers', [])))
    return action()


def _inputs(root):
    paths = ['parts-plan-final/segments.json', 'analysis/asr-tr.json']
    for rel in ['voices/voices.json', 'voices/voice-profiles.json', 'authorization.json']:
        if confined_path(root, rel).exists():
            paths.append(rel)
    return {rel: file_hash(confined_path(root, rel)) for rel in paths}


def _location(root):
    inputs = _inputs(root)
    key = cache_key(inputs, {'context_seconds': 2, 'ownership': 'midpoint'})
    rel = f'.dubbing-batch/{VERSION}/{key}'
    return inputs, rel, confined_path(root, rel)


@contextmanager
def locked(root):
    base = confined_path(root, '.dubbing-batch')
    base.mkdir(exist_ok=True)
    path = confined_path(root, '.dubbing-batch/lock')
    with path.open('a') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('another batch owns lock') from exc
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def _verified(root, run_dir, path, inputs):
    m = read_json(path / 'manifest.json')
    if m.get('inputs') != inputs or m.get('version') != VERSION:
        raise ValueError('input/version integrity mismatch')
    outputs = m.get('outputs')
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError('output integrity records missing')
    for rel, sha in outputs.items():
        target = confined_path(root, f'{run_dir}/{rel}')
        if not target.is_file() or file_hash(target) != sha:
            raise ValueError(f'output hash integrity mismatch: {rel}')
    return m


def prepare(root):
    root = Path(root)
    inputs, rel, out = _location(root)
    with locked(root):
        if out.exists():
            manifest = _verified(root, rel, out, inputs)
            return {**manifest['summary'], 'cache_hit': True, 'run_dir': rel}
        plan = read_json(confined_path(root, 'parts-plan-final/segments.json'))
        asr = read_json(confined_path(root, 'analysis/asr-tr.json'))

        def execute_preparation():
            parts = partition_source(plan, asr)
            (out / 'parts').mkdir(parents=True, exist_ok=False)
            outputs, counts = {}, Counter()
            for p in parts:
                name = f'parts/{p["part_id"]}.json'
                write_new(out / name, p)
                outputs[name] = file_hash(out / name)
                counts.update(p['blockers'])
            if _inputs(root) != inputs:
                raise ValueError('source changed during preparation; partial snapshot preserved')
            summary = {'status': 'prepared_not_dubbed', 'total_parts': len(parts),
                       'source_units': sum(len(p['units']) for p in parts),
                       'dubbed_parts': 0, 'approved_parts': 0,
                       'blocked_parts': len(parts), 'blocker_counts': dict(counts),
                       'models_loaded': 0, 'media_uploads': 0,
                       'token_savings_measured': False,
                       'next_action': 'review_source_and_map_global_characters',
                       'limitations': ['ASR drafts only; no new voice synthesis or rendering',
                                       'existing pilot renders are separate unapproved artifacts']}
            write_new(out / 'manifest.json', {'version': VERSION, 'inputs': inputs,
                      'outputs': outputs, 'summary': summary,
                      'part_ids': [p['part_id'] for p in parts]})
            return {**summary, 'cache_hit': False, 'run_dir': rel}

        return guarded('prepare', {'plan': plan, 'asr': asr}, execute_preparation)


def status(root):
    inputs, rel, out = _location(root)
    if not out.exists():
        return {'status': 'not_prepared', 'run_dir': rel, 'dubbed_parts': 0}
    m = _verified(root, rel, out, inputs)
    return {**m['summary'], 'run_dir': rel, 'integrity': 'hashes_match',
            'manifest_sha256': file_hash(out / 'manifest.json')}


def part(root, part_id):
    if not isinstance(part_id, str) or not ID.fullmatch(part_id):
        raise ValueError('invalid part ID')
    inputs, rel, out = _location(root)
    m = _verified(root, rel, out, inputs)
    if part_id not in m['part_ids']:
        raise ValueError('unknown part ID')
    p = read_json(out / 'parts' / f'{part_id}.json')
    # Only short rows; full text remains in the verified local artifact.
    return {'part_id': part_id, 'status': p['status'], 'blockers': p['blockers'],
            'unit_count': len(p['units']), 'unit_ids': [u['id'] for u in p['units']],
            'artifact': f'{rel}/parts/{part_id}.json',
            'tts_preflight': preflight('tts', p)}


def pilot_report(root):
    """Re-audit preserved final6 using actual WAV samples and historical ASR.

    Historical ASR is explicitly not a fresh independent listening test.
    """
    root = Path(root)
    manifest_path = confined_path(root, 'pilot-P0006/tts-manifest-final6.json')
    gate_path = confined_path(root, 'pilot-P0006/emotion-gate.json')
    manifest, old = read_json(manifest_path), read_json(gate_path)
    old_rows = {r['id']: r for r in old['rows']}
    turns = sorted(manifest['turns'], key=lambda r: r['start_part'])
    report_rows = []
    for i, t in enumerate(turns):
        audio = confined_path(root, t['artifact'])
        with wave.open(str(audio), 'rb') as wav:
            samples, rate = wav.getnframes(), wav.getframerate()
        timing = check_timing(start=t['start_part'], samples=samples, sample_rate=rate,
                              part_end=74.44, next_start=(turns[i+1]['start_part']
                              if i + 1 < len(turns) else None))
        row = old_rows.get(t['id'], {})
        lexical = compare_transcript(t['text'], row.get('asr', ''))
        actual_sha = file_hash(audio)
        hash_ok = actual_sha == t['sha256']
        report_rows.append({'id': t['id'], 'expected': t['text'],
            'historical_asr': row.get('asr'), 'asr_is_historical': True,
            'lexical': lexical, 'timing': timing, 'audio_sha256': actual_sha,
            'artifact_hash_matches': hash_ok,
            'technical_screen_pass': lexical['screen_pass'] and timing['screen_pass'] and hash_ok,
            'audiovisual_approved': False})
    summary = {'status': 'blocked_pending_correction_and_listening',
        'part_id': manifest['part_id'], 'total_turns': len(turns),
        'lexical_mismatches': [r['id'] for r in report_rows if not r['lexical']['screen_pass']],
        'timing_overruns': [r['id'] for r in report_rows if not r['timing']['screen_pass']],
        'hash_mismatches': [r['id'] for r in report_rows if not r['artifact_hash_matches']],
        'automatic_perceptual_approval': False,
        'limits': ['historical ASR only', 'no claim of listening or emotion recognition']}
    return {'summary': summary, 'rows': report_rows,
            'manifest_sha256': file_hash(manifest_path), 'historical_asr_sha256': file_hash(gate_path)}


def audit_pilot(root):
    return pilot_report(root)['summary']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['prepare', 'status', 'part', 'audit-pilot', 'advance'])
    parser.add_argument('--root', required=True)
    parser.add_argument('--part-id')
    parser.add_argument('--report')
    args = parser.parse_args(argv)
    if args.operation == 'prepare': result = prepare(args.root)
    elif args.operation == 'status': result = status(args.root)
    elif args.operation == 'part': result = part(args.root, args.part_id)
    elif args.operation == 'advance':
        prepared = prepare(args.root)
        result = {**prepared, 'status': 'blocked_before_tts',
                  'reason': 'source/speakers/translation/intent reviews are pending',
                  'tts_executed': False}
    else:
        full = pilot_report(args.root)
        if args.report:
            write_new(confined_path(args.root, args.report), full)
        result = full['summary']
    print(json.dumps(result, ensure_ascii=False))
    return 2 if args.operation == 'advance' else 0


if __name__ == '__main__':
    raise SystemExit(main())
