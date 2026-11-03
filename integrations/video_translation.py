"""R1038 local dialogue translation with auditable timing units.

No synthesis, audio edit, subtitle approval or network download at run time.
The real adapter requires an explicitly downloaded local M2M100 directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

MODEL_NAME = 'facebook/m2m100_418M'
MODEL_LICENSE = 'MIT'


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{label}: finite number required')
    return float(value)


def build_units(asr, *, return_skipped=False):
    """Build segment-level units; empty text is skipped, not translated."""
    if not isinstance(asr, dict):
        raise ValueError('ASR object required')
    segments = asr.get('segments')
    if not isinstance(segments, list):
        raise ValueError('ASR segments list required')
    duration = _number(asr.get('duration'), 'ASR duration')
    if duration <= 0:
        raise ValueError('ASR duration must be positive')
    tolerance = 0.5
    units = []
    skipped = 0
    for segment in segments:
        if not isinstance(segment, dict):
            raise ValueError('segment object required')
        text = segment.get('text')
        if text is None or (isinstance(text, str) and not text.strip()):
            skipped += 1
            continue
        if not isinstance(text, str):
            raise ValueError('segment text must be a string')
        start = _number(segment.get('start'), 'segment start')
        end = _number(segment.get('end'), 'segment end')
        if start < 0 or end <= start or end > duration + tolerance:
            raise ValueError('segment time outside ASR duration')
        units.append({'id': f'U{len(units) + 1:04d}', 'start': start, 'end': end,
                      'source_text': text.strip()})
    if return_skipped:
        return units, skipped
    return units


def translate_units(units, translator, *, src_lang='tr', tgt_lang='pt', batch_size=8):
    if type(batch_size) is not int or isinstance(batch_size, bool) or not 1 <= batch_size <= 64:
        raise ValueError('batch_size must be an integer in [1, 64]')
    if not isinstance(units, list):
        raise ValueError('units list required')
    if not hasattr(translator, 'translate_batch'):
        raise ValueError('translator.translate_batch required')
    result = []
    for offset in range(0, len(units), batch_size):
        batch = units[offset:offset + batch_size]
        texts = [unit['source_text'] for unit in batch]
        translated = translator.translate_batch(texts, src_lang=src_lang, tgt_lang=tgt_lang)
        if not isinstance(translated, (list, tuple)) or len(translated) != len(batch):
            raise ValueError('translator count mismatch')
        clean = []
        for text in translated:
            if not isinstance(text, str) or not text.strip():
                raise ValueError('translator returned empty text')
            clean.append(text.strip())
        for unit, text in zip(batch, clean):
            result.append({**unit, 'translated_text': text})
    return result


class M2M100Translator:
    """Local-only adapter; construction fails before importing if files absent."""

    def __init__(self, model_dir, *, cpu_threads=4):
        if type(cpu_threads) is not int or isinstance(cpu_threads, bool) or not 1 <= cpu_threads <= 8:
            raise ValueError('cpu_threads must be an integer in [1, 8]')
        path = Path(model_dir)
        required = ['config.json', 'tokenizer_config.json']
        weights = ['pytorch_model.bin', 'model.safetensors', 'pytorch_model.bin.index.json']
        tokenizer = ['sentencepiece.bpe.model', 'vocab.json', 'tokenizer.json']
        if (not path.is_dir() or not all((path / name).is_file() for name in required)
                or not any((path / name).is_file() for name in weights)
                or not any((path / name).is_file() for name in tokenizer)):
            raise ValueError('local model directory incomplete; explicit files required')
        try:
            import torch
            from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
        except ImportError as exc:
            raise ValueError('translation runtime not installed') from exc
        self._torch = torch
        self._path = path.resolve()
        self._cpu_threads = cpu_threads
        torch.set_num_threads(cpu_threads)
        self._tokenizer = M2M100Tokenizer.from_pretrained(str(self._path), local_files_only=True)
        self._model = M2M100ForConditionalGeneration.from_pretrained(
            str(self._path), local_files_only=True)
        self._model.eval()

    def translate_batch(self, texts, src_lang='tr', tgt_lang='pt',
                        *, max_new_tokens=128, num_beams=1):
        if not isinstance(texts, (list, tuple)) or not texts:
            raise ValueError('nonempty text batch required')
        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ValueError('nonempty text strings required')
        if type(max_new_tokens) is not int or not 16 <= max_new_tokens <= 512:
            raise ValueError('max_new_tokens must be in [16, 512]')
        if type(num_beams) is not int or not 1 <= num_beams <= 8:
            raise ValueError('num_beams must be in [1, 8]')
        self._tokenizer.src_lang = src_lang
        encoded = self._tokenizer(list(texts), return_tensors='pt', padding=True,
                                  truncation=True, max_length=512)
        forced = self._tokenizer.get_lang_id(tgt_lang)
        with self._torch.no_grad():
            generated = self._model.generate(**encoded, forced_bos_token_id=forced,
                                             max_new_tokens=max_new_tokens,
                                             num_beams=num_beams)
        return [text.strip() for text in self._tokenizer.batch_decode(
            generated, skip_special_tokens=True)]

    def metadata(self):
        return {'name': MODEL_NAME, 'local_dir': str(self._path),
                'license': MODEL_LICENSE, 'device': 'cpu',
                'cpu_threads': self._cpu_threads, 'network': False}


def translate_asr(asr_path, translator, out, *, src_lang='tr', tgt_lang='pt',
                  batch_size=8, model_meta=None):
    source = Path(asr_path)
    if source.is_symlink() or not source.is_file():
        raise ValueError('ASR: existing regular file required')
    destination = Path(out)
    if destination.exists():
        raise FileExistsError(destination)
    try:
        asr = json.loads(source.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError('ASR unreadable') from exc
    units = build_units(asr)
    if not units:
        raise ValueError('no translation units; empty ASR')
    translated = translate_units(units, translator, src_lang=src_lang,
                                 tgt_lang=tgt_lang, batch_size=batch_size)
    result = {
        'schema_version': 1,
        'source_asr_sha256': sha256_file(source),
        'source_audio_sha256': asr.get('audio_sha256'),
        'source_language': asr.get('language'),
        'src_lang': src_lang,
        'tgt_lang': tgt_lang,
        'status': 'translated_pending_review',
        'model': model_meta or {},
        'unit_count': len(translated),
        'units': translated,
        'limitations': [
            'machine translation pending human review',
            'names, idioms, gender, address and humor may be wrong',
            'no synthesis, audio edit, subtitle approval or lip sync performed',
        ],
    }
    with destination.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--asr', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--model-dir', required=True)
    parser.add_argument('--src', default='tr')
    parser.add_argument('--tgt', default='pt')
    parser.add_argument('--batch-size', type=int, default=8)
    parser.add_argument('--cpu-threads', type=int, default=4)
    args = parser.parse_args(argv)
    translator = M2M100Translator(args.model_dir, cpu_threads=args.cpu_threads)
    result = translate_asr(args.asr, translator, args.out, src_lang=args.src,
                           tgt_lang=args.tgt, batch_size=args.batch_size,
                           model_meta=translator.metadata())
    print(json.dumps({'units': result['unit_count'], 'status': result['status'],
                      'out': str(Path(args.out).resolve())}))


if __name__ == '__main__':
    main()
