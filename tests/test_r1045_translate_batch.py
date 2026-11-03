"""R1045: tradução em lote retomável, sem sobrescrever e sem aprovar qualidade."""
import importlib
import json
from pathlib import Path

import pytest


def api():
    return importlib.import_module('integrations.dubbing_translate_batch')


class Fake:
    def __init__(self):
        self.calls = []

    def translate_batch(self, texts, src_lang='tr', tgt_lang='pt'):
        self.calls.append(list(texts))
        return [f'PT:{text}' for text in texts]


def parts(tmp_path):
    d = tmp_path / 'parts'
    d.mkdir()
    (d / 'p1.json').write_text(json.dumps({
        'part_id': 'p1', 'units': [
            {'id': 'U1', 'source_text': 'Merhaba', 'start_part': 0.0, 'end_part': 1.0},
            {'id': 'U2', 'source_text': 'Nasılsın', 'start_part': 1.0, 'end_part': 2.0}]}))
    return d


def test_translate_and_resume(tmp_path):
    m = api()
    d = parts(tmp_path)
    fake = Fake()
    out = tmp_path / 'out'
    first = m.translate_parts(d, fake, out, batch_size=2)
    assert first['parts'] == 1 and first['units'] == 2
    data = json.loads((out / 'p1.json').read_text())
    assert [u['translated_text'] for u in data['units']] == ['PT:Merhaba', 'PT:Nasılsın']
    assert data['status'] == 'machine_translation_pending_review'
    second = m.translate_parts(d, fake, out, batch_size=2)
    assert second['cached'] == 1
    assert len(fake.calls) == 1


def test_source_change_blocks_cached_output(tmp_path):
    m = api()
    d = parts(tmp_path)
    fake = Fake()
    out = tmp_path / 'out'
    m.translate_parts(d, fake, out)
    (d / 'p1.json').write_text(json.dumps({
        'part_id': 'p1', 'units': [
            {'id': 'U1', 'source_text': 'Değişti', 'start_part': 0.0, 'end_part': 1.0}]}))
    with pytest.raises(ValueError, match='source'):
        m.translate_parts(d, fake, out)


def test_empty_text_is_not_silently_translated(tmp_path):
    m = api()
    d = tmp_path / 'parts'
    d.mkdir()
    (d / 'p1.json').write_text(json.dumps({
        'part_id': 'p1', 'units': [
            {'id': 'U1', 'source_text': ' ', 'start_part': 0.0, 'end_part': 1.0}]}))
    with pytest.raises(ValueError, match='empty'):
        m.translate_parts(d, Fake(), tmp_path / 'out')
