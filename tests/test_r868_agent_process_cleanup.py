"""R868: cliente controlado, sem modelo/REA real; filhos não sobrevivem à chamada."""
from __future__ import annotations

import os
from pathlib import Path
import signal
import subprocess
import sys
from threading import Event, Thread
import time

import pytest

from integrations.execution_control import cancellation_scope


def _owned_children(marker):
    found = []
    for path in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            command = path.read_bytes()
            state = (path.parent / 'stat').read_text().split(') ', 1)[1].split()[0]
            if str(marker).encode() in command and state != 'Z':
                found.append(int(path.parent.name))
        except (OSError, IndexError, ValueError):
            continue
    return found


@pytest.fixture
def controlled_client(tmp_path, monkeypatch):
    from integrations import rea_assistant as module
    if sys.platform != 'linux' or not Path('/proc').is_dir():
        pytest.skip('contraprova de processos Linux/WSL; produto bloqueia sem namespace')
    module.setup_local_agent(root=tmp_path, model='controlled-fixture')
    started = tmp_path / 'owned-child-started'
    continued = tmp_path / 'owned-child-continued'
    mode = tmp_path / 'mode'
    mode.write_text('timeout')
    child = (
        'import signal,time;from pathlib import Path;'
        'signal.signal(signal.SIGTERM,signal.SIG_IGN);'
        f'Path({str(started)!r}).write_text("started");'
        'time.sleep(0.75);'
        f'Path({str(continued)!r}).write_text("continued");time.sleep(10)'
    )
    binary = tmp_path / 'opencode'
    binary.write_text(
        f'#!{sys.executable}\n'
        'import json,os,subprocess,sys,time\nfrom pathlib import Path\n'
        f'mode=Path({str(mode)!r}).read_text()\n'
        'debug=sys.argv[1:]==["debug","config"]\n'
        'if debug and mode!="debug-timeout":\n'
        ' print(os.environ["OPENCODE_CONFIG_CONTENT"],flush=True)\n'
        ' sys.exit(0)\n'
        f'child=subprocess.Popen([{sys.executable!r},"-c",{child!r}],'
        'stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)\n'
        'deadline=time.monotonic()+3\n'
        f'while not Path({str(started)!r}).exists() and time.monotonic()<deadline:time.sleep(0.01)\n'
        'if mode=="normal":\n'
        ' print(json.dumps({"type":"tool_use","part":{"tool":"rea-local-assistant_core_rea_status",'
        '"state":{"status":"completed","output":json.dumps({"success":True,"guard":{"success":True},'
        '"installation":{"available":True}})}}}),flush=True)\n'
        ' sys.exit(0)\n'
        'time.sleep(10)\n'
    )
    binary.chmod(0o700)
    monkeypatch.setenv('OPENCODE_BIN', str(binary))
    monkeypatch.setattr(module, 'CLIENT_RUN_TIMEOUT', 0.4, raising=False)
    monkeypatch.setattr(module, 'CLIENT_CONFIG_TIMEOUT', 0.4, raising=False)
    # A contrapróva permanece funcional na implementação anterior: a única
    # instrumentação limita seus 300/70 segundos, sem alterar sua limpeza.
    original_run = subprocess.run
    def bounded_run(command, **kwargs):
        if command and command[0] == str(binary):
            kwargs['timeout'] = 0.4
        return original_run(command, **kwargs)
    monkeypatch.setattr(module.subprocess, 'run', bounded_run)
    try:
        yield module, tmp_path, mode, started, continued
    finally:
        # Apenas filhos desta fixture; nunca enumera processos para remoção
        # genérica, e o marcador absoluto é exclusivo do diretório temporário.
        for pid in _owned_children(continued):
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def _call(module, root, **kwargs):
    try:
        return module.launch_local_agent(root=root, **kwargs)
    except subprocess.TimeoutExpired:
        return {'success': False, 'error_code': 'legacy_timeout_exception'}


def _assert_no_survivor(marker):
    assert _owned_children(marker) == [], 'filho independente sobreviveu ao cliente'
    time.sleep(0.8)
    assert marker.exists() is False, 'filho executou após a chamada terminar'


def test_timeout_encerra_cliente_e_filho_em_sessao_independente(controlled_client):
    module, root, mode, started, marker = controlled_client
    report = _call(module, root, prompt='Fixture controlada, sem modelo')
    assert started.exists()
    _assert_no_survivor(marker)
    assert report['success'] is False and report['error_code'] == 'timeout'


def test_debug_config_timeout_encerra_descendentes(controlled_client):
    module, root, mode, started, marker = controlled_client
    mode.write_text('debug-timeout')
    report = _call(module, root, check_only=True)
    assert started.exists()
    _assert_no_survivor(marker)
    assert report['success'] is False and report['error_code'] == 'timeout'


def test_saida_normal_do_lider_encerra_filho_independente(controlled_client):
    module, root, mode, started, marker = controlled_client
    mode.write_text('normal')
    report = _call(module, root, prompt='Fixture controlada de prontidão')
    assert started.exists()
    _assert_no_survivor(marker)
    assert report['success'] is True
    assert report['verification'] == 'executed_readiness_tool_only'


def test_cancelamento_antes_do_cliente_nao_inicia_processos(controlled_client):
    module, root, mode, started, marker = controlled_client
    event = Event()
    event.set()
    with cancellation_scope(event):
        report = _call(module, root, prompt='Fixture cancelada')
    assert started.exists() is False
    _assert_no_survivor(marker)
    assert report['success'] is False and report['error_code'] == 'cancelled'


def test_cancelamento_durante_cliente_aguarda_limpeza(controlled_client):
    module, root, mode, started, marker = controlled_client
    event = Event()
    def cancel_when_started():
        deadline = time.monotonic() + 3
        while not started.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        event.set()
    monitor = Thread(target=cancel_when_started)
    monitor.start()
    try:
        with cancellation_scope(event):
            report = _call(module, root, prompt='Fixture com cancelamento')
    finally:
        monitor.join(timeout=4)
    assert started.exists()
    _assert_no_survivor(marker)
    assert report['success'] is False and report['error_code'] == 'cancelled'


def test_modo_interativo_tambem_limpa_no_cancelamento(controlled_client):
    module, root, mode, started, marker = controlled_client
    event = Event()
    def cancel_when_started():
        deadline = time.monotonic() + 3
        while not started.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        event.set()
    monitor = Thread(target=cancel_when_started)
    monitor.start()
    try:
        with cancellation_scope(event):
            report = _call(module, root)
    finally:
        monitor.join(timeout=4)
    assert started.exists()
    _assert_no_survivor(marker)
    assert report['success'] is False and report['error_code'] == 'cancelled'


def test_cliente_bloqueia_sem_namespace_linux(controlled_client, monkeypatch):
    module, root, mode, started, marker = controlled_client
    mode.write_text('normal')
    monkeypatch.setattr(module.sys, 'platform', 'unsupported-test-platform')
    report = _call(module, root, check_only=True)
    assert started.exists() is False
    assert report['success'] is False
    assert report['error_code'] == 'client_process_isolation_unavailable'
