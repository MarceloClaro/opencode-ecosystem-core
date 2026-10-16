"""R901: estrutura editorial e proveniência das fontes autoritativas do livro.

Estes gates verificam relações e campos observáveis. Não medem aprendizagem,
fluidez de prosa, pertinência científica ou execução dos exemplos pelo leitor.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'livro-core'
TECHNICAL_MODULES = (
    'mod-01c-instalacao.tex', 'mod-01d-arquitetura.tex',
    'mod-02-orquestracao.tex', 'mod-03-memoria-mci.tex',
    'mod-04-qualidade-sdd.tex', 'mod-05-raciocinio.tex',
    'mod-06-ciencia.tex', 'mod-07-integracoes.tex',
    'mod-08-ecossistema.tex', 'mod-09-infra.tex',
    'mod-13-ativacao-agentes.tex', 'mod-15-epilogo-reproducao.tex',
    'mod-16-mapas-fluxogramas.tex',
)


def _arguments(text: str, start: int, count: int) -> list[str]:
    values = []
    cursor = start
    for _ in range(count):
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        assert cursor < len(text) and text[cursor] == '{', 'argumento de prática ausente'
        begin = cursor + 1
        depth = 1
        cursor += 1
        while cursor < len(text) and depth:
            if text[cursor] == '\\':
                cursor += 2
                continue
            if text[cursor] == '{':
                depth += 1
            elif text[cursor] == '}':
                depth -= 1
            cursor += 1
        assert depth == 0, 'argumento de prática não fechado'
        values.append(text[begin:cursor - 1].strip())
    return values


@pytest.mark.parametrize('module', TECHNICAL_MODULES)
def test_practice_has_six_nonempty_fields_in_each_technical_module(module):
    text = (BOOK / module).read_text(encoding='utf-8')
    marker = r'\praticacore'
    assert marker in text, f'{module}: prática guiada ausente'
    cursor = 0
    while (index := text.find(marker, cursor)) >= 0:
        values = _arguments(text, index + len(marker), 6)
        assert all(values), f'{module}: campo de prática vazio'
        cursor = index + len(marker)


def test_inventory_covers_authoritative_sources_with_current_hashes():
    inventory = json.loads((BOOK / 'inventario-core.json').read_text(encoding='utf-8'))
    required = {'main.tex', 'macros.tex', 'gen_mod10.py', 'gen_mod14_ativacao.py', 'gen_inventario.py'}
    for name in required:
        relative = f'livro-core/{name}'
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert inventory['sources'].get(relative, {}).get('sha256') == actual, relative
    configured = json.loads((ROOT / 'opencode.json').read_text(encoding='utf-8'))
    assert inventory['counts']['agents'] == len(configured['agent'])
    assert inventory['counts']['mcp_servers'] == len(configured['mcp'])
    assert inventory['counts']['commands'] == len(configured['command'])
    assert inventory['verification'] == 'source_inventory_only'


def test_argument_parser_rejects_incomplete_practice():
    with pytest.raises(AssertionError, match='ausente'):
        _arguments('{um}{dois}', 0, 6)
    with pytest.raises(AssertionError, match='fechado'):
        _arguments('{incompleto', 0, 1)


def test_argument_parser_preserves_nested_tex_and_escaped_braces():
    assert _arguments(r'{\pth{a.py}}{\{x\}}', 0, 2) == [r'\pth{a.py}', r'\{x\}']


def test_catalog_reconciles_canonical_file_identity_without_similarity():
    spec = importlib.util.spec_from_file_location('r901_catalog', BOOK / 'gen_mod10.py')
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    cards = {'Título editorial independente': {'_file': '/workspace/agents/catalog/scoped-writer.md'}}
    assert generator.reconciliar(cards, ['other-agent', 'scoped-writer']) == {
        'Título editorial independente': 'scoped-writer'}
    assert generator.reconciliar(cards, ['completely-unrelated']) == {}
