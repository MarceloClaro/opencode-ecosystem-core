"""Instalador one-click: catálogo, seleção e recusa de apply sem confirmação."""
import importlib
import json
from pathlib import Path

import pytest


def api():
    return importlib.import_module('installer.oneclick.install')


def test_catalog_is_valid_and_has_groups():
    m = api()
    catalog = m.load_catalog()
    assert len(catalog['entries']) >= 15
    assert {'base', 'core-cli', 'media', 'science'} <= set(catalog['groups'])


def test_selection_by_group_and_only():
    m = api()
    catalog = m.load_catalog()
    base = m.requested(catalog, ['base'])
    assert base and all(row['group'] == 'base' for row in base)
    one = m.requested(catalog, None, 'opencode')
    assert [row['id'] for row in one] == ['opencode']
    with pytest.raises(ValueError):
        m.requested(catalog, ['nope'])
    with pytest.raises(ValueError):
        m.requested(catalog, None, 'nope')


def test_missing_command_is_reported_without_install():
    m = api()
    row = m.check_entry({'id': 'x', 'group': 'base',
                         'check': ['definitely-not-a-command-xyz', '--version']})
    assert row['installed'] is False and row['ok'] is False


def test_apply_without_yes_is_refused():
    m = api()
    assert m.main(['--apply', '--only', 'opencode']) == 2


def test_duplicate_id_rejected():
    m = api()
    data = {'schema_version': 1, 'groups': {'x': 'x'}, 'entries': [
        {'id': 'a', 'group': 'x', 'check': ['true'], 'license': 'MIT',
         'install': {'kind': 'manual', 'command': 'x'}},
        {'id': 'a', 'group': 'x', 'check': ['true'], 'license': 'MIT',
         'install': {'kind': 'manual', 'command': 'x'}}]}
    with pytest.raises(ValueError, match='duplicado'):
        m.validate_catalog(data)
