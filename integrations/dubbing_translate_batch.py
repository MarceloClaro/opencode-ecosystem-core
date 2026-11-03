"""R1045: tradução local em lote dos unidades preparadas.

Não sintetiza, não aprova tradução e não sobrescreve resultado existente.
Cache vinculado ao texto de origem; mudança de fonte bloqueia a retomada.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

VERSION = 'R1045-translate-1'


def _digest(value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def _validate_batch(size):
    if type(size) is not int or isinstance(size, bool) or not 1 <= size <= 64:
        raise ValueError('batch_size must be integer in [1, 64]')


def _units(document):
    units = document.get('units')
    if not isinstance(units, list):
        raise ValueError('units list required')
    clean = []
    for unit in units:
        text = unit.get('source_text')
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f'{unit.get("id")}: empty source text')
        start, end = unit.get('start_part'), unit.get('end_part')
        if (isinstance(start, bool) or isinstance(end, bool)
                or not isinstance(start, (int, float)) or not isinstance(end, (int, float))
                or not math.isfinite(start) or not math.isfinite(end) or end <= start):
            raise ValueError(f'{unit.get("id")}: invalid timing')
        clean.append({'id': unit.get('id'), 'source_text': text.strip(),
                      'start_part': float(start), 'end_part': float(end)})
    return clean


def translate_parts(parts_dir, translator, out_dir, *, batch_size=8,
                    src_lang='tr', tgt_lang='pt'):
    _validate_batch(batch_size)
    if not hasattr(translator, 'translate_batch'):
        raise ValueError('translator.translate_batch required')
    parts_dir = Path(parts_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(parts_dir.glob('*.json'))
    if not files:
        raise ValueError('no prepared parts')
    parts = cached = units_count = 0
    model_meta = translator.metadata() if hasattr(translator, 'metadata') else {}
    for path in files:
        document = json.loads(path.read_text())
        pid = document.get('part_id') or path.stem
        units = _units(document)
        source_sha = _digest(units)
        target = out_dir / f'{pid}.json'
        if target.exists():
            old = json.loads(target.read_text())
            if old.get('source_sha256') != source_sha:
                raise ValueError(f'{pid}: source changed; refusing cached translation')
            cached += 1
            continue
        translated = []
        for offset in range(0, len(units), batch_size):
            batch = units[offset:offset + batch_size]
            texts = [unit['source_text'] for unit in batch]
            result = translator.translate_batch(texts, src_lang=src_lang, tgt_lang=tgt_lang)
            if not isinstance(result, (list, tuple)) or len(result) != len(batch):
                raise ValueError(f'{pid}: translator count mismatch')
            for unit, text in zip(batch, result):
                if not isinstance(text, str) or not text.strip():
                    raise ValueError(f'{pid}: empty translation for {unit["id"]}')
                translated.append({**unit, 'translated_text': text.strip()})
        payload = {'schema_version': 1, 'version': VERSION, 'part_id': pid,
                   'source_sha256': source_sha, 'source_language': src_lang,
                   'target_language': tgt_lang, 'model': model_meta,
                   'status': 'machine_translation_pending_review',
                   'translation_verified': False, 'units': translated,
                   'limitations': ['machine translation; names, idioms, gender and humor may be wrong',
                                   'no native-speaker review']}
        with target.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
        parts += 1
        units_count += len(units)
        print(json.dumps({'part_id': pid, 'units': len(units)}), flush=True)
    return {'status': 'translated_pending_review', 'parts': parts,
            'cached': cached, 'units': units_count, 'out_dir': str(out_dir)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--model-dir', required=True)
    parser.add_argument('--out-dir', default='.dubbing-translation')
    parser.add_argument('--batch-size', type=int, default=8)
    parser.add_argument('--limit', type=int, default=0)
    args = parser.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from integrations import dubbing_batch
    from integrations.video_translation import M2M100Translator

    root = Path(args.root)
    status = dubbing_batch.status(root)
    parts_dir = dubbing_batch.confined_path(root, status['run_dir'] + '/parts')
    out = dubbing_batch.confined_path(root, args.out_dir)
    translator = M2M100Translator(args.model_dir, cpu_threads=4)
    result = translate_parts(parts_dir, translator, out, batch_size=args.batch_size)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
