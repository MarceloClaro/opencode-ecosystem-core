"""R1047: contrato da narração, legendas e manifesto da dublagem R1026."""
import importlib.util
import json
from pathlib import Path

import pytest

from integrations import video_editor as ve

ROOT = Path(__file__).resolve().parents[1]
DUB = ROOT / 'pilots/r1026-quantum/r1047-dub'
BUILD = DUB / 'build_dub.py'


def load_build():
    spec = importlib.util.spec_from_file_location('r1047_build', BUILD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_narration_contract_covers_explanation_and_consent():
    data = json.loads((DUB / 'narration.pt-BR.json').read_text())
    assert data['language'] == 'pt-BR'
    assert 1.0 <= data['speed'] <= 1.3
    assert 0 < data['start_seconds'] < data['max_end_seconds'] <= 20
    segments = data['segments']
    assert [item['id'] for item in segments] == [1, 2, 3, 4]
    assert all(item['tts_text'].strip() for item in segments)
    assert all(len(item['subtitle_lines']) <= 2 for item in segments)
    text = ' '.join(item['tts_text'] for item in segments).lower()
    assert '100' in text or 'cem' in text
    assert 'menores' in text and 'maiores' in text
    assert 'simul' in text and 'problema' in text
    assert 'declarou consentimento' in data['consent']
    assert 'CPML' in data['model_license']


def test_subtitle_writer_uses_real_timing_and_no_overlap(tmp_path):
    build = load_build()
    events = [
        {'start': 1.5, 'end': 3.0, 'lines': ['Primeira linha', 'segunda linha']},
        {'start': 3.2, 'end': 5.0, 'lines': ['Outra linha', 'final']},
    ]
    srt, ass = build.write_subtitles(events, tmp_path)
    srt_text = srt.read_text()
    assert '00:00:01,500 --> 00:00:03,000' in srt_text
    assert 'Primeira linha\nsegunda linha' in srt_text
    assert '0:00:01.50' in ass.read_text()
    assert events[0]['end'] < events[1]['start']


def test_build_does_not_reference_presenter_card():
    text = BUILD.read_text()
    assert 'presenter-middle-card' not in text
    assert 'presenter-card.mp4' not in text
    assert "'card_present': False" in text


def test_manifest_contract_when_output_exists():
    manifest_path = DUB / 'out/manifest.json'
    if not manifest_path.is_file():
        pytest.skip('saída R1047 ainda não gerada')
    manifest = json.loads(manifest_path.read_text())
    claims = manifest['claims']
    assert claims['presenter_card_present'] is False
    assert claims['audiovisual_approved'] is False
    assert claims['translation_human_reviewed'] is False
    assert claims['scientific_validity_verified'] is False
    assert claims['published'] is False
    assert isinstance(claims['lip_sync_resynchronized'], bool)
    if not claims['lip_sync_resynchronized']:
        assert any('NÃO foi re-sincronizada' in item
                   for item in manifest['limitations'])
    assert manifest['subtitle']['cps_max'] <= 17
    video = Path(manifest['video']['path'])
    if not video.is_file():
        pytest.skip('MP4 R1047 ausente')
    info = ve.probe_media(video)
    assert info['video']['width'] == 1920
    assert info['video']['height'] == 1080
    assert info['video']['frames'] == 600
    assert info['video']['fps'] == '30/1'
    assert info['audio']['sample_rate'] == 48000
    assert info['audio']['channels'] == 2
