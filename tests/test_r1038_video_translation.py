"""R1038 uses a fake translator; no model download or translation quality claim."""
import importlib.util
import json
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / 'integrations/video_translation.py'


def api():
    assert MODULE.is_file(), 'tradutor local ainda ausente'
    spec = importlib.util.spec_from_file_location('video_translation', MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def asr(segments, duration=10.0):
    return {'audio_sha256': 'a' * 64, 'duration': duration, 'language': 'tr',
            'segments': segments}


class Fake:
    def __init__(self, fail=None):
        self.calls = []
        self.fail = fail

    def translate_batch(self, texts, src_lang='tr', tgt_lang='pt'):
        self.calls.append((list(texts), src_lang, tgt_lang))
        if self.fail == 'count':
            return texts[:-1]
        if self.fail == 'empty':
            return [''] * len(texts)
        return ['PT:' + text for text in texts]


def write_asr(tmp_path, data):
    path = tmp_path / 'asr.json'
    path.write_text(json.dumps(data, ensure_ascii=False))
    return path


def test_build_units_keeps_timing_and_text():
    m = api()
    units = m.build_units(asr([
        {'start': 0, 'end': 2, 'text': 'Merhaba'},
        {'start': 2.5, 'end': 4, 'text': 'Nasılsın?'}]))
    assert [u['id'] for u in units] == ['U0001', 'U0002']
    assert units[1]['start'] == 2.5 and units[1]['end'] == 4
    assert units[0]['source_text'] == 'Merhaba'


def test_empty_segments_skipped_but_counted():
    m = api()
    units, skipped = m.build_units(asr([
        {'start': 0, 'end': 1, 'text': '  '},
        {'start': 1, 'end': 2, 'text': 'Olá'}]), return_skipped=True)
    assert len(units) == 1 and skipped == 1


@pytest.mark.parametrize('segment', [
    {'start': -1, 'end': 1, 'text': 'a'},
    {'start': 2, 'end': 1, 'text': 'a'},
    {'start': 0, 'end': 11, 'text': 'a'},
    {'start': float('nan'), 'end': 1, 'text': 'a'},
])
def test_invalid_segment_times_rejected(segment):
    with pytest.raises(ValueError):
        api().build_units(asr([segment]))


def test_translate_batch_preserves_order():
    m = api()
    units = m.build_units(asr([
        {'start': 0, 'end': 1, 'text': 'a'},
        {'start': 1, 'end': 2, 'text': 'b'}]))
    fake = Fake()
    out = m.translate_units(units, fake, batch_size=1)
    assert [u['translated_text'] for u in out] == ['PT:a', 'PT:b']
    assert len(fake.calls) == 2
    assert fake.calls[0][1:] == ('tr', 'pt')


def test_translator_wrong_count_and_empty_rejected():
    m = api()
    units = m.build_units(asr([{'start': 0, 'end': 1, 'text': 'a'}]))
    with pytest.raises(ValueError, match='count'):
        m.translate_units(units, Fake('count'))
    with pytest.raises(ValueError, match='empty'):
        m.translate_units(units, Fake('empty'))


@pytest.mark.parametrize('batch', [0, -1, True])
def test_bad_batch_size(batch):
    m = api()
    units = m.build_units(asr([{'start': 0, 'end': 1, 'text': 'a'}]))
    with pytest.raises(ValueError, match='batch'):
        m.translate_units(units, Fake(), batch_size=batch)


def test_missing_model_dir_rejected_before_import(tmp_path):
    with pytest.raises(ValueError, match='model'):
        api().M2M100Translator(tmp_path / 'missing')


def test_translate_asr_binds_hash_and_no_overwrite(tmp_path):
    m = api()
    source = write_asr(tmp_path, asr([
        {'start': 0, 'end': 1, 'text': 'a'},
        {'start': 1, 'end': 2, 'text': 'b'}]))
    out = tmp_path / 'translated.json'
    result = m.translate_asr(source, Fake(), out, model_meta={'name': 'fake'})
    assert result['status'] == 'translated_pending_review'
    assert result['source_asr_sha256'] == m.sha256_file(source)
    assert len(result['units']) == 2
    assert json.loads(out.read_text())['units'][0]['translated_text'] == 'PT:a'
    with pytest.raises(FileExistsError):
        m.translate_asr(source, Fake(), out, model_meta={'name': 'fake'})


def test_translate_asr_requires_segments(tmp_path):
    m = api()
    source = write_asr(tmp_path, {'audio_sha256': 'a' * 64, 'duration': 10})
    with pytest.raises(ValueError, match='segments'):
        m.translate_asr(source, Fake(), tmp_path / 'out.json', model_meta={'name': 'fake'})
