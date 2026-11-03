"""R924: composição de instalação fixa e ambientes de dependências; nunca treina.

As cópias upstream gerenciadas não são modificadas. Planos não autorizam execução;
efeitos exigem confirm=True. Recibos locais não autenticam o dono do host.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import selectors
import shutil
import signal
import subprocess
import sys
import tarfile
import time

from integrations.itsfine_core import ItsFineCore, VERSION, _canonical, _json, _read, _sha

DIST_SRI = 'sha512-LpfBJTaZaGBOpH6u1A8DzrsIGFxMjpWL7ZqaVAv8CNeoNtaE+sLxw9DmMiGyfHMlB4UHqDmU9dF8JNpqLSm7hw=='
GROUP = {'hf-peft': 'text', 'hf-encoder': 'text', 'hf-tts': 'voice'}
MAX_PROCESS_OUTPUT = 262144


def _flags():
    return {'training_executed': False, 'model_weights_downloaded': False,
            'policy_modified': False, 'externally_validated': False, 'confidence_promoted': False}


def _seal(value):
    return {**value, 'plan_sha256': _sha(_canonical(value))}


def _root(value):
    return ItsFineCore(value)


def _policy(service):
    path = service._path('.its-fine/policy.json')
    return _sha(_read(path, 131072)) if path.exists() else None


def _positive_timeout(value, maximum=3600):
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 < value <= maximum:
        raise ValueError('invalid_timeout')


def run_bounded(argv, *, cwd, timeout_seconds, max_output_bytes=MAX_PROCESS_OUTPUT, env=None):
    """Linux/POSIX: drena pipes com teto real e fecha o grupo de processos próprio."""
    _positive_timeout(timeout_seconds)
    if (os.name != 'posix' or not isinstance(argv, list) or not argv or
            any(not isinstance(a, str) or '\x00' in a for a in argv) or
            type(max_output_bytes) is not int or not 1 <= max_output_bytes <= 4 * 1024 * 1024):
        raise ValueError('invalid_bounded_process')
    start = time.monotonic(); deadline = start + timeout_seconds
    output = {'stdout': bytearray(), 'stderr': bytearray()}
    status = 'completed'; process = None; group_closed = False
    with selectors.DefaultSelector() as selector:
        try:
            process = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, start_new_session=True)
            for name in output:
                stream = getattr(process, name); os.set_blocking(stream.fileno(), False)
                selector.register(stream, selectors.EVENT_READ, name)
            while selector.get_map():
                if time.monotonic() >= deadline:
                    status = 'timeout'; break
                if process.poll() is not None and not group_closed:
                    try: os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError: pass
                    group_closed = True
                for key, _ in selector.select(min(0.05, max(0, deadline - time.monotonic()))):
                    used = sum(len(v) for v in output.values())
                    chunk = os.read(key.fd, min(65536, max_output_bytes - used + 1))
                    if not chunk:
                        selector.unregister(key.fileobj); key.fileobj.close(); continue
                    allowed = max_output_bytes - used
                    output[key.data].extend(chunk[:allowed])
                    if len(chunk) > allowed:
                        status = 'output_limit'; break
                if status != 'completed': break
            if status == 'completed' and process.poll() is None:
                try: process.wait(timeout=max(0.001, deadline-time.monotonic()))
                except subprocess.TimeoutExpired: status = 'timeout'
        except OSError:
            status = 'launch_failed'
        finally:
            if process is not None:
                try:
                    if not group_closed:
                        try: os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError: pass
                    process.wait(timeout=5)
                    group_closed = True
                except subprocess.TimeoutExpired:
                    status = 'cleanup_incomplete'
                    group_closed = False
                finally:
                    for stream in (process.stdout, process.stderr):
                        if stream is not None and not stream.closed: stream.close()
    return {'status': status, 'returncode': process.returncode if process else None,
            **{key: bytes(value) for key, value in output.items()},
            'process_group_closed': group_closed, 'process_started': process is not None}


def _public_process(result):
    return {key: result[key] for key in ('status', 'returncode', 'process_group_closed', 'process_started')} | {
        'stdout_sha256': _sha(result['stdout']), 'stderr_sha256': _sha(result['stderr']),
        'output_bytes': len(result['stdout']) + len(result['stderr'])}


def audit_distribution(archive_path):
    path = Path(archive_path).absolute()
    raw = _read(path, 4 * 1024 * 1024)
    sri = 'sha512-' + base64.b64encode(hashlib.sha512(raw).digest()).decode('ascii')
    if sri != DIST_SRI:
        raise ValueError('distribution_sri_mismatch')
    paths = set(); total = 0; metadata = None
    try:
        with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
            for member in archive:
                name = member.name
                pure = PurePosixPath(name)
                if (len(paths) >= 256 or name in paths or not name.startswith('package/') or
                        '\\' in name or ':' in name or pure.is_absolute() or
                        name != pure.as_posix() or any(p in {'.', '..'} for p in pure.parts) or
                        not (member.isfile() or member.isdir())):
                    raise ValueError('unsafe_distribution_member')
                paths.add(name); total += member.size
                if total > 4 * 1024 * 1024 or member.size < 0:
                    raise ValueError('distribution_size_limit')
                if name == 'package/package.json':
                    if not member.isfile() or member.size > 65536:
                        raise ValueError('invalid_distribution_metadata')
                    metadata = _json(archive.extractfile(member).read(65537))
    except (tarfile.TarError, EOFError, OSError) as exc:
        raise ValueError('invalid_distribution_archive') from exc
    if not isinstance(metadata, dict) or metadata.get('name') != '@sandeco/itsfine' or metadata.get('version') != VERSION:
        raise ValueError('distribution_identity_mismatch')
    tests = ['tests/install.test.mjs'] if metadata.get('scripts', {}).get('test') else []
    present = [test for test in tests if 'package/' + test in paths]
    return {'version': VERSION, 'sri_verified': True, 'sri': sri,
            'archive_sha256': _sha(raw), 'members': len(paths), 'expanded_bytes': total,
            'declared_upstream_tests': tests, 'present_upstream_tests': present,
            'upstream_tests_status': 'present_not_executed' if tests and len(present) == len(tests) else 'not_shipped',
            'upstream_tests_executed': False, 'license_declared': metadata.get('license'), **_flags()}


def installation_plan(root, archive_path):
    service = _root(root); path = Path(archive_path).absolute(); audit = audit_distribution(path)
    argv = ['npm', 'exec', '--yes', '--offline', '--package', str(path), '--', 'itsfine', 'install',
            '--target', str(service.root), '--engines', 'opencode', '--yes', '--no-deps']
    return _seal({'kind': 'itsfine_pinned_install', 'root': str(service.root), 'archive_path': str(path),
        'archive_sha256': audit['archive_sha256'], 'sri': audit['sri'], 'version': VERSION,
        'policy_sha256': _policy(service), 'argv': argv, 'execution_started': False, **_flags()})


def install_pinned(root, plan, confirm=False, timeout_seconds=120):
    _positive_timeout(timeout_seconds, 600)
    if confirm is not True or not isinstance(plan, dict):
        raise ValueError('explicit_install_confirmation_required')
    service = _root(root)
    expected = installation_plan(root, plan.get('archive_path', ''))
    if _canonical(plan) != _canonical(expected):
        raise ValueError('stale_or_forged_install_plan')
    env = {**os.environ, 'npm_config_ignore_scripts': 'true', 'NPM_CONFIG_IGNORE_SCRIPTS': 'true',
           'npm_config_audit': 'false', 'ITSFINE_SKIP_REGISTRY': '1', 'NO_COLOR': '1', 'CI': '1',
           'PYTHONDONTWRITEBYTECODE': '1'}
    env.pop('NODE_OPTIONS', None)
    process = run_bounded(expected['argv'], cwd=service.root, timeout_seconds=timeout_seconds, env=env)
    after_policy = _policy(service)
    unchanged = expected['policy_sha256'] is not None and after_policy == expected['policy_sha256']
    created = expected['policy_sha256'] is None and after_policy is not None
    safe_creation = False
    if created:
        data = _json(_read(service._path('.its-fine/policy.json'),131072))
        permissions = {'allow_process','allow_data_to_harness','allow_external_generator',
                       'allow_data_transfer','allow_colab','allow_kaggle'}
        lists = {'external_generator_endpoints','transfer_destinations','protected_data_paths'}
        known = permissions | lists | {'schema_version','require_isolated_executor'}
        safe_creation = (isinstance(data,dict) and not set(data)-known
            and type(data.get('schema_version',1)) is int and data.get('schema_version',1)==1
            and all(data.get(key,False) is False for key in permissions)
            and all(data.get(key,[])==[] for key in lists)
            and type(data.get('require_isolated_executor',False)) is bool)
    status = service.status()
    ok = process['status'] == 'completed' and process['returncode'] == 0 and status['integrity_ok'] and (unchanged or safe_creation)
    return {**_flags(), 'status': 'installed_verified' if ok else 'installation_failed', 'plan_sha256': plan['plan_sha256'],
            'process': _public_process(process), 'verification': status,
            'policy_preserved': unchanged, 'policy_created': created,
            'policy_modified': after_policy != expected['policy_sha256'] and not safe_creation}


def _python312():
    value = shutil.which('python3.12')
    if not value:
        raise ValueError('python_312_unavailable')
    return str(Path(value).resolve(strict=True))


def _lock(service, group):
    path = service._path(f'integrations/itsfine-locks/{group}-py312.txt')
    raw = _read(path, 2 * 1024 * 1024)
    try: text = raw.decode('utf-8')
    except UnicodeError as exc: raise ValueError('invalid_engine_lock') from exc
    if ('--hash=sha256:' not in text or '==' not in text or
            re.search(r'(?m)^\s*(?:-e\b|-r\b|--editable|--trusted-host|--find-links|--config-settings)', text)):
        raise ValueError('unhashed_or_unsafe_engine_lock')
    for url in re.findall(r'https?://[^\s\\]+', text):
        from urllib.parse import urlsplit
        if urlsplit(url).scheme != 'https' or urlsplit(url).hostname not in {'pypi.org', 'files.pythonhosted.org', 'download.pytorch.org'}:
            raise ValueError('untrusted_engine_index')
    return path, _sha(raw)


def engine_plan(root, engine):
    if not isinstance(engine, str) or engine not in GROUP:
        raise ValueError('unknown_engine')
    service = _root(root); service._inspection()
    group = GROUP[engine]; lock, lock_sha = _lock(service, group)
    descriptor = _read(service._path(f'.its-fine/engines/{engine}/engine.json'), 131072)
    meta = _json(descriptor)
    if not isinstance(meta, dict) or meta.get('engine') != engine or meta.get('version') != VERSION:
        raise ValueError('engine_identity_mismatch')
    relative = '.its-fine/venv' if group == 'text' else '.its-fine/venvs/hf-tts'
    environment = service._path(relative)
    return _seal({'kind': 'itsfine_engine_dependencies', 'root': str(service.root), 'engine': engine,
        'group': group, 'environment': str(environment), 'lock_path': str(lock), 'lock_sha256': lock_sha,
        'engine_sha256': _sha(descriptor), 'policy_sha256': _policy(service), 'python': _python312(),
        'python_version_required': '3.12', 'uv': shutil.which('uv'),
        'execution_started': False, **_flags()})


def _probe_program(group):
    modules = (['torch', 'transformers', 'peft', 'datasets', 'accelerate', 'safetensors', 'pymupdf', 'numpy']
               if group == 'text' else ['torch', 'torchaudio', 'transformers', 'peft', 'accelerate',
                   'safetensors', 'librosa', 'soundfile', 'jiwer', 'onnxruntime', 'av', 'faster_whisper', 'qwen_tts'])
    return ('import importlib,json,sys\n'
        'from importlib import metadata\n'
        f'modules={modules!r}\n'
        'for name in modules: importlib.import_module(name)\n'
        'import torch\n'
        'torch.set_num_threads(1)\n'
        'layer=torch.nn.Linear(3,2); x=torch.ones(1,3,requires_grad=True); loss=layer(x).square().sum(); loss.backward()\n'
        'assert x.grad is not None and torch.isfinite(x.grad).all()\n'
        'versions={d.metadata["Name"].lower():d.version for d in metadata.distributions()}\n'
        'assert sys.version_info[:2]==(3,12)\n'
        'gpu=bool(torch.cuda.is_available()); gpu_ok=False\n'
        'if gpu:\n'
        '    a=torch.ones(1,device="cuda",requires_grad=True); a.square().sum().backward(); gpu_ok=bool(torch.isfinite(a.grad).all())\n'
        'print("ITSFINE_CORE_PROBE="+json.dumps({"python":sys.version.split()[0],"cpu_probe_passed":True,"accelerator_available":gpu,'
        '"gpu_probe_passed":gpu_ok,"torch":torch.__version__,"versions":versions,"training_executed":False,"model_weights_downloaded":False}))\n')


def _probe_data(raw):
    for line in reversed(raw.splitlines()):
        if line.startswith(b'ITSFINE_CORE_PROBE='):
            data = _json(line.split(b'=',1)[1])
            if isinstance(data,dict) and data.get('cpu_probe_passed') is True and str(data.get('python','')).startswith('3.12.'):
                return data
    raise ValueError('environment_probe_failed')


def _probe_env():
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1',
           'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1', 'HF_HUB_DISABLE_TELEMETRY': '1'}
    env.pop('PYTHONPATH', None)
    return env


def _write(path, value):
    from academic.adversarial_research.service import _write_json
    _write_json(path, value)


def prepare_engine(root, plan, confirm=False, timeout_seconds=1200):
    _positive_timeout(timeout_seconds)
    if confirm is not True or not isinstance(plan, dict):
        raise ValueError('explicit_engine_confirmation_required')
    service = _root(root); expected = engine_plan(root, plan.get('engine'))
    if _canonical(plan) != _canonical(expected) or not expected['uv']:
        raise ValueError('stale_or_forged_engine_plan')
    directory = service._path(str(Path(expected['environment']).relative_to(service.root)))
    marker = directory / 'core-environment.json'
    if directory.exists() and not marker.is_file():
        raise ValueError('foreign_environment_preserved')
    if marker.exists() and _json(_read(marker, 65536)).get('root') != str(service.root):
        raise ValueError('foreign_environment_preserved')
    deadline = time.monotonic() + timeout_seconds
    commands = []
    if not directory.exists():
        directory.parent.mkdir(parents=True, exist_ok=True)
        commands.append([expected['uv'], '--no-config', 'venv', '--python', expected['python'], str(directory)])
    python = directory / 'bin/python'
    commands.extend([
        [expected['uv'], '--no-config', 'pip', 'sync', '--python', str(python), '--require-hashes',
         '--index-strategy', 'unsafe-best-match', expected['lock_path']],
        [expected['uv'], '--no-config', 'pip', 'check', '--python', str(python)],
        [str(python), '-I', '-c', _probe_program(expected['group'])],
    ])
    processes = []; probe = None; status = 'preparation_failed'
    for index, argv in enumerate(commands):
        remaining = deadline - time.monotonic()
        if remaining <= 0: break
        # Política e lock são revalidados sem alterar as decisões do usuário.
        if _policy(service) != expected['policy_sha256'] or _lock(service, expected['group'])[1] != expected['lock_sha256']:
            raise ValueError('inputs_changed_during_preparation')
        env = {**os.environ, 'UV_NO_PROGRESS': '1', 'PIP_DISABLE_PIP_VERSION_CHECK': '1',
               'PYTHONDONTWRITEBYTECODE': '1', 'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1',
               'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1', 'HF_HUB_DISABLE_TELEMETRY': '1'}
        env.pop('PYTHONPATH', None)
        result = run_bounded(argv, cwd=service.root, timeout_seconds=remaining, env=env)
        processes.append(_public_process(result))
        if result['status'] != 'completed' or result['returncode'] != 0: break
        if index == 0 and 'venv' in argv:
            _write(marker, {'kind': 'core_itsfine_environment_v1', 'root': str(service.root),
                            'group': expected['group'], 'python_version': '3.12'})
        if index == len(commands) - 1:
            try: probe = _probe_data(result['stdout'])
            except ValueError: break
            if not isinstance(probe, dict) or probe.get('cpu_probe_passed') is not True: break
            status = 'dependencies_verified_cpu'
    policy_changed = _policy(service) != expected['policy_sha256']
    if policy_changed: status = 'preparation_failed'
    ready = status == 'dependencies_verified_cpu'
    receipt = {'schema_version': 1, 'engine': expected['engine'], 'group': expected['group'],
        'root': str(service.root), 'environment': str(directory), 'lock_sha256': expected['lock_sha256'],
        'engine_sha256': expected['engine_sha256'], 'policy_sha256': expected['policy_sha256'],
        'python_fingerprint': _sha(_read(python.resolve(strict=True), 32 * 1024 * 1024)) if python.exists() else None,
        'status': status, 'dependencies_ready': ready, 'cpu_probe_passed': ready,
        'accelerator_available': bool(ready and probe.get('accelerator_available')),
        'training_ready': bool(ready and probe.get('accelerator_available') and probe.get('gpu_probe_passed')),
        'processes': processes, 'probe': probe if ready else None, **_flags(),
        'policy_modified': policy_changed}
    receipt['receipt_sha256'] = _sha(_canonical(receipt))
    _write(service._path(f'.its-fine/core/engines/{expected["engine"]}.json'), receipt)
    return receipt


def engines_status(root):
    service = _root(root); rows = []; probes = {}
    for engine, group in GROUP.items():
        row = {'engine': engine, 'status': 'not_prepared', 'dependencies_ready': False,
               'cpu_probe_passed': False, 'accelerator_available': False, 'training_ready': False}
        receipt_path = service._path(f'.its-fine/core/engines/{engine}.json')
        if receipt_path.exists():
            try:
                receipt = _json(_read(receipt_path, 2 * 1024 * 1024))
                expected = engine_plan(root, engine)
                if (not isinstance(receipt, dict) or receipt.get('engine') != engine or
                        receipt.get('receipt_sha256') != _sha(_canonical({k:v for k,v in receipt.items() if k != 'receipt_sha256'})) or
                        any(receipt.get(k) != expected[k] for k in ('lock_sha256', 'engine_sha256', 'policy_sha256', 'environment'))):
                    raise ValueError('receipt_invalid')
                python = Path(expected['environment']) / 'bin/python'
                if not python.is_file(): row['status'] = 'environment_missing'
                elif _sha(_read(python.resolve(strict=True), 32 * 1024 * 1024)) != receipt.get('python_fingerprint'):
                    row['status'] = 'receipt_invalid'
                else:
                    marker = Path(expected['environment']) / 'core-environment.json'
                    owner = _json(_read(marker,65536))
                    if owner.get('root') != str(service.root) or owner.get('group') != group:
                        raise ValueError('foreign_environment_preserved')
                    if receipt.get('dependencies_ready') is not True:
                        row['status'] = 'not_prepared'
                    else:
                        key = (str(python), group)
                        if key not in probes:
                            result = run_bounded([str(python),'-I','-c',_probe_program(group)],cwd=service.root,
                                timeout_seconds=120,env=_probe_env())
                            if result['status']!='completed' or result['returncode']!=0:
                                raise ValueError('environment_probe_failed')
                            probes[key] = _probe_data(result['stdout'])
                        live = probes[key]
                        row.update(status='dependencies_verified_cpu', dependencies_ready=True,
                            cpu_probe_passed=True, accelerator_available=live['accelerator_available'],
                            training_ready=bool(live['accelerator_available'] and live['gpu_probe_passed']),
                            verification='live_imports_cpu_gradient_no_weights')
            except (ValueError, OSError, TypeError, KeyError):
                row['status'] = 'receipt_invalid'
        rows.append(row)
    return {'status': 'engine_environments_inspected', 'engines': rows,
            'verification': 'locks_and_receipts_not_model_benchmark', **_flags()}
