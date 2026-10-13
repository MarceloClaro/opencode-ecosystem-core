"""R869: processos locais reais de transporte; nenhuma inferência é executada."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import subprocess
import sys
from threading import Event, Thread
import time

import pytest

from integrations.execution_control import ExecutionCancelled, cancellation_scope
from integrations.harness_runtime import HarnessRuntime


READER = (
    'import hashlib,json,sys,time;time.sleep(0.25);'
    'raw=sys.stdin.buffer.read();'
    'print(json.dumps({"text":raw.decode("utf-8"),"bytes":len(raw),'
    '"sha256":hashlib.sha256(raw).hexdigest(),"argv":sys.argv[1:]},ensure_ascii=False))'
)


def _read(prompt):
    try:
        process = HarnessRuntime._run_cli(
            [sys.executable, '-c', READER, 'controlled-reader'], input=prompt,
            timeout=5, text=True, encoding='utf-8', errors='strict', shell=False,
        )
    except subprocess.TimeoutExpired:
        return None
    assert process.returncode == 0
    return json.loads(process.stdout)


def test_prompt_unicode_vai_pela_entrada_padrao():
    prompt = "Árvore, ação, 你好, 🙂; texto literal com 'aspas' e $variável.\nSegunda linha."
    report = _read(prompt)
    assert report is not None, 'processo não recebeu EOF pela entrada padrão'
    assert report['text'] == prompt
    assert report['argv'] == ['controlled-reader']
    assert report['sha256'] == hashlib.sha256(prompt.encode('utf-8')).hexdigest()


def test_prompt_grande_preserva_bytes_apos_communicate_retornar_timeout(monkeypatch):
    prompt = ('ação 你好 🙂\n' * 100_000) + 'FIM NÃO DUPLICADO'
    original = subprocess.Popen.communicate
    interrupted = []
    def observed(process, *args, **kwargs):
        try:
            return original(process, *args, **kwargs)
        except subprocess.TimeoutExpired:
            interrupted.append(True)
            raise
    monkeypatch.setattr(subprocess.Popen, 'communicate', observed)
    report = _read(prompt)
    assert report is not None
    assert interrupted, 'fixture precisa atravessar retomada real de communicate'
    assert report['bytes'] == len(prompt.encode('utf-8'))
    assert report['sha256'] == hashlib.sha256(prompt.encode('utf-8')).hexdigest()
    assert report['text'] == prompt


def test_entrada_vazia_fecha_pipe_sem_bloquear():
    report = _read('')
    assert report is not None
    assert report['text'] == '' and report['bytes'] == 0


def test_executor_controlado_recebe_contexto_sem_prompt_em_argv(tmp_path, monkeypatch):
    runtime = HarnessRuntime(repo_root=tmp_path)
    executable = tmp_path / 'codex-controlled'
    recorded = tmp_path / 'transport.json'
    executable.write_text(
        f'#!{sys.executable}\nimport json,sys\nfrom pathlib import Path\n'
        'context=sys.stdin.read()\n'
        f'Path({str(recorded)!r}).write_text(json.dumps({{"input":context,"argv":sys.argv[1:]}}))\n'
        'print(json.dumps({"type":"item.completed","item":{"type":"agent_message",'
        '"text":context}},ensure_ascii=False))\n'
        'print(json.dumps({"type":"turn.completed","usage":{}}))\n'
    )
    executable.chmod(0o700)
    monkeypatch.setattr(runtime, '_resolve_cli', lambda name: str(executable))
    prompt = 'CONTEXTO DE FIXTURE ÁRVORE 你好 🙂'
    result = runtime.execute('codex', prompt, timeout=5)
    actual = json.loads(recorded.read_text())
    assert result['success'] is True
    assert prompt in actual['input'] and prompt in result['output']
    assert prompt not in actual['argv']
    assert actual['argv'][actual['argv'].index('--sandbox') + 1] == 'read-only'
    assert actual['argv'][-1] == '-'


def test_cancelamento_antes_da_cli_nao_inicia_processo(tmp_path):
    marker = tmp_path / 'unexpected-start'
    program = f'from pathlib import Path;Path({str(marker)!r}).write_text("started")'
    event = Event()
    event.set()
    rejected = False
    with cancellation_scope(event):
        try:
            HarnessRuntime._run_cli([sys.executable, '-c', program], input='fixture', timeout=5)
        except ExecutionCancelled:
            rejected = True
    assert rejected is True and not marker.exists()


def test_cancelamento_durante_envio_encerra_processo(tmp_path):
    started = tmp_path / 'started.pid'
    program = (
        'import os,time;from pathlib import Path;'
        f'Path({str(started)!r}).write_text(str(os.getpid()));time.sleep(10)'
    )
    event = Event()
    def cancel_when_started():
        deadline = time.monotonic() + 3
        while not started.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        event.set()
    monitor = Thread(target=cancel_when_started)
    monitor.start()
    rejected = False
    try:
        with cancellation_scope(event):
            try:
                HarnessRuntime._run_cli([sys.executable, '-c', program], input='ação\n' * 200_000,
                                       timeout=5, text=True, encoding='utf-8')
            except ExecutionCancelled:
                rejected = True
    finally:
        monitor.join(timeout=4)
    assert rejected is True and started.exists()
    if Path('/proc').is_dir():
        pid = started.read_text()
        assert not Path('/proc', pid).exists()


@pytest.mark.skipif(os.name != 'posix', reason='conversão WSL→Windows só ocorre fora do Windows nativo')
@pytest.mark.parametrize('repository', ['/home/user/programa com espaços', '/mnt/c/Users/user/programa com espaços'])
def test_caminho_windows_permanece_canonico(monkeypatch, repository):
    runtime = object.__new__(HarnessRuntime)
    runtime.repo_root = Path(repository)
    monkeypatch.setenv('WSL_DISTRO_NAME', 'Ubuntu')
    actual = runtime._execution_root('/mnt/c/Apps/codex.exe')
    parsed = PureWindowsPath(actual)
    expected = (PureWindowsPath('C:/').joinpath(*Path(repository).parts[3:])
                if repository.startswith('/mnt/c/') else
                PureWindowsPath('//wsl.localhost/Ubuntu').joinpath(*Path(repository).parts[1:]))
    assert parsed.is_absolute() is True
    assert actual == str(parsed) == str(expected)
