"""Aceitação opcional com mídia real R1026; não versiona o vídeo nem o derivado.

Execute com R1046_REAL_MEDIA=1. Sem a variável, o teste é pulado para não
transformar um render de 20 s em obrigação de CI.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from integrations import video_editor as ve

pytestmark = pytest.mark.skipif(
    os.environ.get('R1046_REAL_MEDIA') != '1',
    reason='defina R1046_REAL_MEDIA=1 para o render real opcional')


def _frame_rgb(path, frame, width, height):
    data = subprocess.run(
        ['ffmpeg', '-nostdin', '-v', 'error', '-i', str(path), '-map', '0:v:0',
         '-vf', f'select=eq(n\\,{frame}),scale={width}:{height}',
         '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', 'pipe:1'],
        capture_output=True, check=True, timeout=120).stdout
    assert len(data) >= width * height * 3
    return data


def _mean_luma(data, width, x0, y0, x1, y1):
    total, count = 0, 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            offset = (y * width + x) * 3
            total += (2126 * data[offset] + 7152 * data[offset + 1]
                      + 722 * data[offset + 2]) // 10000
            count += 1
    return total / count


def test_quantum_multitrack_real_media(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    source = repo / 'pilots/r1026-quantum/source.mp4'
    card = repo / 'pilots/r1026-quantum/presenter-middle-card.mp4'
    if not source.is_file() or not card.is_file():
        pytest.skip('mídia R1026 ausente')
    work = tmp_path / 'work'
    work.mkdir()
    shutil.copy2(source, work / 'source.mp4')
    shutil.copy2(card, work / 'card.mp4')
    src_info = ve.probe_media(work / 'source.mp4')
    card_info = ve.probe_media(work / 'card.mp4', allow_silent=True)
    p = ve.project_from_probe('source.mp4', src_info, project_id='quantum-real')
    p['root'] = str(work)
    p['width'], p['height'] = 640, 360
    record = ve.project_from_probe('card.mp4', card_info, allow_silent=True)
    p['sources']['card.mp4'] = record['sources']['card.mp4']
    p['sources']['card.mp4']['has_audio'] = False
    p['tracks'] = [
        {'id': 'v1', 'kind': 'video', 'clips': [
            {'id': 'base', 'track': 'v1', 'source': 'source.mp4', 'in_frame': 0,
             'out_frame': 600, 'start_frame': 0, 'speed': 1, 'volume': 1,
             'color': {'brightness': .02, 'contrast': 1.05, 'saturation': 1.08}}]},
        {'id': 'v2', 'kind': 'video', 'clips': [
            {'id': 'card', 'track': 'v2', 'source': 'card.mp4', 'in_frame': 0,
             'out_frame': 600, 'start_frame': 0, 'speed': 1, 'volume': 1,
             'transform': {'width': 150, 'height': 188, 'x': 80, 'y': 60,
                           'opacity': .92, 'corner_radius': 18}}]},
        {'id': 'a1', 'kind': 'audio', 'clips': [
            {'id': 'voice', 'track': 'a1', 'source': 'source.mp4', 'in_frame': 0,
             'out_frame': 600, 'start_frame': 0, 'speed': 1, 'volume': 1}]}]
    output = work / 'quantum-real.mp4'
    plan = ve.plan(p, 'multitrack', {'output': str(output), 'preset': 'veryfast'})
    assert plan['expected_frames'] == 600
    assert any('conformed from 30/1' in warning for warning in plan['warnings'])
    result = ve.render(plan)
    receipt = json.loads(Path(result['receipt']).read_text())
    assert receipt['technical_checks_passed'] is True
    assert receipt['probe']['video']['frames'] == 600
    assert receipt['probe']['video']['fps'] == '30000/1001'
    assert receipt['probe']['audio']['sample_rate'] == 48000
    assert receipt['audiovisual_approved'] is False
    assert receipt['translation_accuracy_verified'] is False
    assert receipt['scientific_validity_verified'] is False
    assert receipt['output_sha256'] == ve.file_hash(output)
    # O cartão foi posicionado sobre a área clara do slide; a luminância cai
    # de forma mensurável, o que prova a composição sem julgar estética.
    original = _frame_rgb(source, 300, 640, 360)
    composed = _frame_rgb(output, 300, 640, 360)
    before = _mean_luma(original, 640, 80, 60, 230, 248)
    after = _mean_luma(composed, 640, 80, 60, 230, 248)
    assert after < before - 30, (before, after)
    # O canto do cartão é mascarado: permanece claro, enquanto o centro é escuro.
    corner = _mean_luma(composed, 640, 80, 60, 90, 70)
    center = _mean_luma(composed, 640, 145, 140, 165, 160)
    assert corner > 120 and center < 110 and corner > center + 50, (corner, center)
