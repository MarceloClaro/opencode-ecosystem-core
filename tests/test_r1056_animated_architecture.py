"""R1056: cobertura, segurança e evidência das animações documentais."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def module():
    from scripts import animate_architecture as mod
    return mod


def test_discovery_deduplicates_and_keeps_every_occurrence(tmp_path):
    code = 'flowchart LR\n A[Entrada] --> B[Saída]\n'
    (tmp_path / 'README.md').write_text('# Um\n```mermaid\n' + code + '```\n')
    (tmp_path / 'docs').mkdir()
    (tmp_path / 'docs/X.md').write_text('# Dois\n```mermaid\n' + code + '```\n')
    found = module().discover(tmp_path, ['README.md', 'docs/X.md'], catalog=False)
    assert len(found) == 1
    assert len(found[0]['origins']) == 2
    assert found[0]['source'] == code
    assert found[0]['source_sha256'] == hashlib.sha256(code.encode()).hexdigest()


@pytest.mark.parametrize('path', ['../secret', '/etc/passwd', 'docs/../../secret'])
def test_path_escape_rejected(tmp_path, path):
    with pytest.raises(ValueError):
        module().inside(tmp_path, path)


def test_symlink_escape_rejected(tmp_path):
    (tmp_path / 'link').symlink_to('/etc/passwd')
    with pytest.raises(ValueError):
        module().inside(tmp_path, 'link')


@pytest.mark.parametrize('source', [
    '%%{init: {securityLevel: "loose"}}%%\nflowchart LR\nA-->B',
    'flowchart LR\nA-->B\nclick A "https://example.org"',
    'flowchart LR\nA["<script>alert(1)</script>"]',
])
def test_unsafe_mermaid_rejected(source):
    with pytest.raises(ValueError):
        module().validate_source(source)


def test_real_inventory_covers_catalog_and_published_blocks():
    items = module().discover(ROOT)
    catalog = json.loads((ROOT / 'docs/architecture/flows.json').read_text())
    origins = [o for item in items for o in item['origins']]
    covered = {o['path'] for o in origins}
    assert all('docs/architecture/' + f['file'] in covered for f in catalog['flows'])
    assert {'README.md', 'ARCHITECTURE.md', 'docs/README.md'} <= covered
    assert sum('block' in o for o in origins) >= 45


def test_gif_validation_rejects_static_and_checks_duration(tmp_path):
    p = tmp_path / 'test.gif'
    a = Image.new('RGB', (32, 32), 'white')
    a.save(p)
    with pytest.raises(ValueError):
        module().inspect_gif(p)
    b = Image.new('RGB', (32, 32), 'black')
    a.save(p, save_all=True, append_images=[b], duration=[500, 500])
    meta = module().inspect_gif(p)
    assert meta['frames'] == 2
    assert meta['duration_ms'] == 1000
    assert meta['infinite_loop'] is False


def test_delivery_manifest_has_real_media_and_no_source_drift():
    result = module().verify(ROOT)
    assert result['status'] == 'pass'
    assert result['catalog_flows'] == 22
    assert result['diagrams'] >= 30
    assert result['total_gif_bytes'] <= 60_000_000


def test_camera_crop_focuses_edge_and_stays_inside_canvas():
    crop = module().camera_window(
        {'width': 1200, 'height': 600},
        [{'points': [[500, 280], [560, 300], [620, 320]]}],
        aspect=1192 / 502,
    )
    assert 100 < crop['width'] <= 1200
    assert crop['width'] / crop['height'] == pytest.approx(1192 / 502, rel=1e-3)
    assert 0 <= crop['left'] <= 1200 - crop['width']
    assert 0 <= crop['top'] <= 600 - crop['height']
    cx, cy = crop['left'] + crop['width'] / 2, crop['top'] + crop['height'] / 2
    assert abs(cx - 560) < 1
    assert abs(cy - 300) < 1
    assert crop['zoom'] >= 1.5


def test_layer_summary_is_a_legible_grid_not_a_single_row(tmp_path):
    inventory = ROOT / 'docs/architecture/architecture-inventory.json'
    module().write_layer_summary(inventory, tmp_path / 'layers.mmd')
    code = (tmp_path / 'layers.mmd').read_text()
    assert code.startswith('%%') and 'block-beta' in code
    assert 'columns 3' in code
    assert code.count('["') >= 18
    assert 'não é o grafo integral' in code
