"""Gates de fonte e conservação editorial; não medem aprendizagem ou estética."""
from pathlib import Path
import importlib.util
import re

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'livro-core'


def test_prose_tables_can_wrap_inside_the_local_width():
    bad = []
    for path in BOOK.glob('mod-*.tex'):
        if re.search(r'\\begin\{tabular\}\{l{2,}\}', path.read_text()):
            bad.append(path.name)
    assert not bad, f'Colunas textuais sem quebra de linha: {bad}'


def test_catalog_didactic_template_uses_generation_metrics():
    spec = importlib.util.spec_from_file_location('r907_catalog', BOOK / 'gen_mod10.py')
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    # Inventário diferente do atual: números publicados precisam acompanhar a entrada.
    text = generator.render_catalog_didactic({
        'N': 8, 'F': 8, 'S': 3, 'EXACT': 5, 'SLUG': 2, 'ALIAS': 1,
        'TOP1': 4, 'TOP2': 2, 'TOPSUM': 6, 'CATS': 3,
        'NAIVE_PERCENT': '62,5', 'TOP_PERCENT': '75', 'MEAN': '2,7',
    })
    assert 'Apêndice Didático: Cobertura documental' in text
    assert '$N = 8$' in text and '$F = 8$' in text
    assert r'\frac{8 - 3}{8}' in text
    assert '312' not in text
    assert not re.search(r'@[A-Z_]+@', text)
