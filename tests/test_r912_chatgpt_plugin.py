"""Pacote e launcher reais; instalação no host tem recibo separado."""
import importlib
import json
from pathlib import Path
import zipfile

import pytest


@pytest.fixture
def provider():
    return importlib.import_module('integrations.chatgpt_plugin')


@pytest.fixture
def core(tmp_path):
    root = tmp_path/'core com espaços'
    (root/'integrations').mkdir(parents=True)
    (root/'integrations/ecosystem_mcp.py').write_text('# fixture de localização, não servidor')
    (root/'.venv/bin').mkdir(parents=True)
    (root/'.venv/bin/python').write_text('# fixture de localização')
    return root


def test_windows_launcher_preserves_argument_boundaries(provider, core):
    config = provider.server_config(core, target='windows-wsl', distro='Ubuntu')
    assert config['type'] == 'stdio'
    assert config['command'] == 'wsl.exe'
    assert config['args'] == ['-d','Ubuntu','--cd',str(core),'--exec',str(core/'.venv/bin/python'),'-m','integrations.ecosystem_mcp']
    assert not {'shell','url','headers'} & config.keys()


def test_linux_launcher_uses_existing_core(provider, core):
    config = provider.server_config(core, target='linux')
    assert config['command'] == str(core/'.venv/bin/python')
    assert config['args'] == ['-m','integrations.ecosystem_mcp']
    assert config['cwd'] == str(core)


@pytest.mark.parametrize('target', ['unknown','cloud'])
def test_unknown_target_cannot_silently_create_remote_server(provider, core, target):
    with pytest.raises(ValueError):
        provider.server_config(core, target=target)


def test_missing_runtime_is_not_installation(provider, core):
    (core/'.venv/bin/python').unlink()
    with pytest.raises(ValueError, match='interpretador'):
        provider.server_config(core)


def test_missing_server_is_rejected(provider, core):
    (core/'integrations/ecosystem_mcp.py').unlink()
    with pytest.raises(ValueError, match='servidor'):
        provider.server_config(core)


def test_package_and_overlay_have_same_identity(provider, core, tmp_path):
    dest = tmp_path/'plugin'
    result = provider.build_plugin(core, dest)
    main = json.loads((dest/'plugin.json').read_text())
    overlay = json.loads((dest/'.codex-plugin/plugin.json').read_text())
    assert main['$schema'] == 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
    assert main['name'] == overlay['name'] == 'opencode-ecosystem-core'
    assert main['version'] == overlay['version']
    extension = main['extensions']['com.openai']
    assert extension['requires_local_executor'] is True
    assert len(extension['interface']['shortDescription']) <= 30
    mcp = json.loads((dest/'mcp.json').read_text())
    assert mcp['mcpServers']['ecosystem-core'] == provider.server_config(core)
    assert set(result['files']) == {'plugin.json','mcp.json','.mcp.json','.codex-plugin/plugin.json','skills/core-orchestrator/SKILL.md'}
    skill = (dest/'skills/core-orchestrator/SKILL.md').read_text()
    assert 'MarceloClaro' in skill and 'resultados' in skill
    assert 'ecosystem_text_spec' in skill and 'spec_id' in skill


def test_occupied_destination_is_preserved(provider, core, tmp_path):
    dest = tmp_path/'plugin';dest.mkdir();(dest/'user.txt').write_text('preservar')
    with pytest.raises(FileExistsError):
        provider.build_plugin(core, dest)
    assert (dest/'user.txt').read_text() == 'preservar'


def test_archive_contains_only_known_files_and_is_reproducible(provider, core, tmp_path):
    dest=tmp_path/'plugin';provider.build_plugin(core,dest)
    (dest/'.env').write_text('NEVER_PACKAGE_THIS')
    one=tmp_path/'one.zip';two=tmp_path/'two.zip'
    provider.archive_plugin(dest,one);provider.archive_plugin(dest,two)
    assert one.read_bytes() == two.read_bytes()
    with zipfile.ZipFile(one) as z:
        assert set(z.namelist()) == set(provider.PACKAGE_FILES)
        assert all(not n.startswith('/') and '..' not in Path(n).parts for n in z.namelist())
        assert b'NEVER_PACKAGE_THIS' not in b''.join(z.read(n) for n in z.namelist())


def test_archive_cannot_be_written_inside_package(provider, core, tmp_path):
    dest=tmp_path/'plugin';provider.build_plugin(core,dest)
    with pytest.raises(ValueError):provider.archive_plugin(dest,dest/'nested.zip')


def test_existing_archive_is_preserved(provider, core, tmp_path):
    dest = tmp_path/'plugin'; provider.build_plugin(core, dest)
    archive = tmp_path/'existing.zip'; archive.write_bytes(b'preservar arquivo')
    with pytest.raises(FileExistsError):
        provider.archive_plugin(dest, archive)
    assert archive.read_bytes() == b'preservar arquivo'


@pytest.mark.parametrize('target_exists', [False, True])
def test_archive_output_symlink_is_rejected(provider, core, tmp_path, target_exists):
    dest = tmp_path/'plugin'; provider.build_plugin(core, dest)
    target = tmp_path/'outside.zip'
    if target_exists:
        target.write_bytes(b'preservar destino')
    link = tmp_path/'linked.zip'; link.symlink_to(target)
    with pytest.raises(ValueError, match='simbólico'):
        provider.archive_plugin(dest, link)
    assert link.is_symlink()
    assert target.exists() is target_exists
    if target_exists:
        assert target.read_bytes() == b'preservar destino'
