"""R1045: motor XTTS com latentes em cache e lote de TTS por unidade.

Não traduz, não aprova voz e não renderiza vídeo. O texto já deve estar
traduzido; o ponto final é removido por `dubbing_synth`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from integrations import dubbing_batch, dubbing_synth

VERSION = 'R1045-tts-1'


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def build_units(prepared, assignment, translation, registry):
    if not isinstance(prepared, dict) or not isinstance(prepared.get('units'), list):
        raise ValueError('prepared units required')
    if not isinstance(assignment, dict) or not isinstance(assignment.get('units'), list):
        raise ValueError('assignment units required')
    if not isinstance(translation, dict) or not isinstance(translation.get('units'), list):
        raise ValueError('translation units required')
    characters = registry.get('characters') if isinstance(registry, dict) else None
    if not isinstance(characters, dict):
        raise ValueError('character registry required')
    cluster_to_char = {}
    for cid, record in characters.items():
        cluster = record.get('cluster')
        if type(cluster) is int:
            cluster_to_char[cluster] = cid
    assigned = {row.get('id'): row for row in assignment['units']}
    translated = {row.get('id'): row for row in translation['units']}
    units, skipped = [], []
    for unit in prepared['units']:
        uid = unit.get('id')
        row = assigned.get(uid)
        if row is None:
            skipped.append({'id': uid, 'reason': 'unassigned'})
            continue
        if row.get('blocked'):
            skipped.append({'id': uid, 'reason': 'blocked'})
            continue
        cluster = row.get('cluster')
        character = cluster_to_char.get(cluster)
        if character is None:
            skipped.append({'id': uid, 'reason': 'unmapped_cluster'})
            continue
        text = translated.get(uid, {}).get('translated_text')
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f'{uid}: translation missing')
        voice = characters[character]
        if not isinstance(voice.get('reference'), str) or not voice.get('sha256'):
            raise ValueError(f'{uid}: voice reference missing')
        units.append({'id': uid, 'character_id': character, 'speaker': character,
                      'translated_text': text.strip(),
                      'start_part': float(unit['start_part']),
                      'end_part': float(unit['end_part']),
                      'reference': voice['reference'],
                      'reference_sha256': voice['sha256']})
    units.sort(key=lambda item: item['start_part'])
    return units, skipped


class XttsEngine:
    name = 'xtts-v2'

    def __init__(self, snapshot, *, threads=4):
        try:
            import torch
            import TTS.tts.models.xtts as xtts
            from TTS.api import TTS
        except ImportError as exc:
            raise ValueError('XTTS/Torch not installed') from exc
        torch.set_num_threads(threads)

        def load_audio(path, sampling_rate):
            import librosa
            wav, _ = librosa.load(path, sr=sampling_rate, mono=True)
            return torch.from_numpy(wav).unsqueeze(0)

        xtts.load_audio = load_audio
        self._torch = torch
        self._tts = TTS(model_path=str(Path(snapshot) / 'model.pth'),
                        config_path=str(Path(snapshot) / 'config.json'),
                        progress_bar=False)
        self._model = self._tts.synthesizer.tts_model
        self._latents = {}

    def _conditioning(self, reference):
        key = _sha(reference)
        if key not in self._latents:
            self._latents[key] = self._model.get_conditioning_latents(audio_path=[reference])
        return self._latents[key]

    def synthesize(self, text, reference, params):
        gpt, speaker = self._conditioning(reference)
        seed = int(params.get('seed', 0))
        self._torch.manual_seed(seed)
        output = self._model.inference(
            text, 'pt', gpt, speaker,
            temperature=float(params.get('temperature', 0.75)),
            length_penalty=float(params.get('length_penalty', 1.0)),
            repetition_penalty=float(params.get('repetition_penalty', 10.0)),
            top_k=int(params.get('top_k', 50)),
            top_p=float(params.get('top_p', 0.85)),
            speed=float(params.get('speed', 1.0)),
            enable_text_splitting=False,
            max_new_tokens=int(params.get('max_new_tokens', 220)))
        audio = output['wav'] if isinstance(output, dict) else output
        return audio


def run_parts(root, snapshot, *, out_dir='.dubbing-takes', limit=0, speed=1.05):
    root = Path(root)
    status = dubbing_batch.status(root)
    batch_dir = dubbing_batch.confined_path(root, status['run_dir'])
    manifest = dubbing_batch.read_json(batch_dir / 'manifest.json')
    registry_path = dubbing_batch.confined_path(root, 'voices/auto-speakers.json')
    if not registry_path.exists():
        raise ValueError('auto-speakers registry missing; run clustering first')
    registry = json.loads(registry_path.read_text())
    voices = {cid: {'reference': rec['reference'], 'reference_sha256': rec['sha256']}
              for cid, rec in registry['characters'].items()}
    engine = XttsEngine(snapshot)
    out = root / out_dir
    out.mkdir(exist_ok=True)
    params = {'sample_rate': 24000, 'temperature': 0.75, 'length_penalty': 1.0,
              'repetition_penalty': 10.0, 'top_k': 50, 'top_p': 0.85,
              'speed': speed, 'seed': 1045, 'max_new_tokens': 220}
    ids = manifest['part_ids'][:limit] if limit else manifest['part_ids']
    summary = {'parts': 0, 'cached': 0, 'takes': 0, 'failures': 0,
               'skipped': 0, 'status': 'tts_batch_pending_review'}
    for pid in ids:
        target = out / f'{pid}.json'
        if target.exists():
            summary['cached'] += 1
            continue
        prepared = dubbing_batch.read_json(batch_dir / 'parts' / f'{pid}.json')
        assignment_path = root / '.dubbing-speakers' / f'{pid}.json'
        translation_path = root / '.dubbing-translation' / f'{pid}.json'
        if not assignment_path.exists() or not translation_path.exists():
            summary['skipped'] += 1
            continue
        assignment = json.loads(assignment_path.read_text())
        translation = json.loads(translation_path.read_text())
        units, skipped = build_units(prepared, assignment, translation, registry)
        result = dubbing_synth.synthesize_part(root, {'part_id': pid, 'units': units},
                                              voices, engine, params, VERSION)
        payload = {'schema_version': 1, 'part_id': pid, 'status': result['part_status'],
                   'units': len(units), 'skipped': skipped,
                   'failures': result['failures'], 'takes': result['takes'],
                   'params': params, 'verified': False,
                   'limitations': ['TTS only; no ASR, subtitle, mix or visual approval']}
        with target.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
        summary['parts'] += 1
        summary['takes'] += len(result['takes'])
        summary['failures'] += len(result['failures'])
        summary['skipped'] += len(skipped)
        print(json.dumps({'part_id': pid, 'takes': len(result['takes']),
                          'failures': len(result['failures']), 'skipped': len(skipped)}),
              flush=True)
    print(json.dumps(summary, ensure_ascii=False))
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--snapshot', required=True)
    parser.add_argument('--out-dir', default='.dubbing-takes')
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--speed', type=float, default=1.05)
    args = parser.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    run_parts(args.root, args.snapshot, out_dir=args.out_dir,
              limit=args.limit, speed=args.speed)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
