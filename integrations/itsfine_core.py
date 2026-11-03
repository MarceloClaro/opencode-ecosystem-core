"""R923: adaptador original para ITS-FINE instalado; autonomia somente de diagnóstico.

Não importa código upstream no processo do Core, não instala/treina/autoriza,
não modifica política nem invoca skills. Integridade é local, não atestação do host.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time

VERSION = '0.0.15'
SPEC_ID = 'SPEC-935-R923'
MAX_FILES = 512
MAX_BYTES = 16 * 1024 * 1024
MAX_OUTPUT = 262144
SKILLS = {f'fine-{name}' for name in ('start','help','objective','environment','model',
    'dataset','config','metric','train','evaluate','export','deliver','resume','colab','kaggle')}


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False,
                      separators=(',', ':')).encode('utf-8')


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _flags():
    return {'training_executed': False, 'inference_executed': False,
            'policy_modified': False, 'externally_validated': False,
            'human_approval_required': True, 'confidence_promoted': False}


def _read(path, limit=MAX_BYTES):
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Symlink recusado na instalação ITS-FINE')
    try:
        # O_NOFOLLOW só no último arquivo não protege uma troca do diretório
        # pai. O leitor comum ancora cada componente em dir_fd sem seguir links.
        from integrations.local_plugin_extraction import _regular_stream
        with _regular_stream(Path(path)) as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or not 0 <= before.st_size <= limit:
                raise ValueError('Arquivo ITS-FINE inválido ou excessivo')
            raw = stream.read(limit + 1)
            after = os.fstat(stream.fileno())
    except OSError as exc:
        raise ValueError('Arquivo ITS-FINE indisponível') from exc
    if len(raw) > limit or (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError('Arquivo ITS-FINE alterado durante leitura')
    return raw


def _json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('JSON ITS-FINE com chave duplicada')
            result[key] = value
        return result
    def invalid(_value):
        raise ValueError('Número JSON não finito')
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)
    except (UnicodeError, RecursionError) as exc:
        raise ValueError('JSON ITS-FINE inválido') from exc


def validate_config(config):
    fields = {'status': set(), 'plan': {'run_id'},
              'verify': set(), 'engines_status': set(),
              'install_plan': {'archive_path'}, 'install': {'plan', 'confirm', 'timeout_seconds'},
              'engine_plan': {'engine'}, 'engine_prepare': {'plan', 'confirm', 'timeout_seconds'},
              'run': {'plan', 'max_steps', 'timeout_seconds', 'cancelled'}}
    if (not isinstance(config, dict) or config.get('operation') not in fields or
            set(config) - fields[config['operation']] - {'operation'}):
        raise ValueError('Operação/campos ITS-FINE desconhecidos')
    result = dict(config)
    if result['operation'] in {'run','install','engine_prepare'} and not isinstance(result.get('plan'), dict):
        raise ValueError('Plano ITS-FINE obrigatório')
    if result['operation'] == 'install_plan' and not isinstance(result.get('archive_path'),str):
        raise ValueError('TGZ fixado obrigatório')
    if result['operation'] == 'engine_plan' and result.get('engine') not in {'hf-peft','hf-encoder','hf-tts'}:
        raise ValueError('Motor ITS-FINE desconhecido')
    return result


class ItsFineCore:
    def __init__(self, root):
        lexical = Path(os.path.abspath(root))
        if any(p.is_symlink() for p in (lexical, *lexical.parents)):
            raise ValueError('Raiz ITS-FINE simbólica recusada')
        self.root = lexical.resolve(strict=True)

    def _path(self, relative):
        if (not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative or
                any(ord(c) < 32 for c in relative) or
                any(part in {'', '.', '..'} for part in relative.split('/')) or
                Path(relative).is_absolute()):
            raise ValueError('Caminho ITS-FINE não canônico')
        path = self.root / relative
        if any(p.is_symlink() for p in (path, *path.parents)) or not path.resolve().is_relative_to(self.root):
            raise ValueError('Caminho ITS-FINE fora do escopo')
        return path

    def _inspection(self):
        manifest_raw = _read(self._path('.its-fine/install-manifest.json'), 2 * 1024 * 1024)
        manifest = _json(manifest_raw)
        if not isinstance(manifest, dict):
            raise ValueError('Manifesto ITS-FINE deve ser objeto')
        files = manifest.get('files')
        if (manifest.get('version') != VERSION or not isinstance(files, dict) or
                not 1 <= len(files) <= MAX_FILES or '.its-fine/bin/fine.py' not in files):
            raise ValueError('Versão/manifesto ITS-FINE não admitidos')
        total = 0
        for relative, expected in files.items():
            if not isinstance(expected, str) or not re.fullmatch(r'[a-f0-9]{64}', expected):
                raise ValueError('Hash ITS-FINE inválido')
            # Somente os diretórios declarados pelo instalador auditado.
            if not isinstance(relative, str) or not relative.startswith(('.its-fine/', '.agents/skills/', '.claude/skills/', '.kiro/skills/')):
                raise ValueError('Arquivo gerenciado fora do escopo ITS-FINE')
            data = _read(self._path(relative), 4 * 1024 * 1024)
            total += len(data)
            if total > MAX_BYTES or _sha(data) != expected:
                raise ValueError('Integridade ITS-FINE divergente')
        policy_raw = _read(self._path('.its-fine/policy.json'), 131072)
        if not isinstance(_json(policy_raw), dict):
            raise ValueError('Política ITS-FINE inválida; edição pertence ao usuário')
        return {'installed': True, 'integrity_ok': True, 'version': VERSION,
                'verification': 'local_file_hashes_only', 'managed_files': len(files),
                'manifest_sha256': _sha(manifest_raw), 'policy_sha256': _sha(policy_raw),
                'runtime_scope': 'installed_not_training_or_model_readiness', **_flags()}

    def status(self):
        try:
            return self._inspection()
        except (OSError, ValueError, TypeError, AttributeError):
            return {'installed': (self.root / '.its-fine/install-manifest.json').is_file(),
                    'integrity_ok': False, 'verification': 'local_file_hashes_only',
                    'status': 'missing_or_integrity_failed', **_flags()}

    def verify(self):
        """Verificador confinado do Core; não delega ao verificador upstream."""
        return {**self.status(), 'verifier': 'core_component_confined',
                'upstream_tests_executed': False}

    def install_plan(self, archive_path):
        from integrations.itsfine_lifecycle import installation_plan
        return installation_plan(self.root, archive_path)

    def install(self, plan, confirm=False, timeout_seconds=120):
        from integrations.itsfine_lifecycle import install_pinned
        return install_pinned(self.root, plan, confirm, timeout_seconds)

    def engine_plan(self, engine):
        from integrations.itsfine_lifecycle import engine_plan
        return engine_plan(self.root, engine)

    def engine_prepare(self, plan, confirm=False, timeout_seconds=1200):
        from integrations.itsfine_lifecycle import prepare_engine
        return prepare_engine(self.root, plan, confirm, timeout_seconds)

    def engines_status(self):
        from integrations.itsfine_lifecycle import engines_status
        return engines_status(self.root)

    def plan(self, run_id=None):
        if run_id is not None and (not isinstance(run_id, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}', run_id)):
            raise ValueError('run_id ITS-FINE inválido')
        inspected = self._inspection()
        plan = {'spec_id': SPEC_ID, 'root': str(self.root), 'version': VERSION,
                'manifest_sha256': inspected['manifest_sha256'], 'policy_sha256': inspected['policy_sha256'],
                'run_id': run_id, 'actions': ['verify', 'engines'] + (['route'] if run_id else []),
                'execution_started': False, 'autonomy_scope': 'fixed_read_only_diagnostics', **_flags()}
        plan['plan_sha256'] = _sha(_canonical(plan))
        return plan

    def run_safe(self, plan, max_steps=3, timeout_seconds=30, cancelled=False):
        if (type(max_steps) is not int or not 1 <= max_steps <= 3 or
                type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds) or
                not 0 < timeout_seconds <= 120 or type(cancelled) is not bool):
            raise ValueError('Limites/cancelamento ITS-FINE inválidos')
        if not isinstance(plan, dict) or _canonical(plan) != _canonical(self.plan(plan.get('run_id'))):
            raise ValueError('Plano ITS-FINE adulterado ou obsoleto')
        deadline = time.monotonic() + timeout_seconds
        result = {'spec_id': SPEC_ID, 'status': 'cancelled' if cancelled else 'awaiting_human',
                  'plan_sha256': plan['plan_sha256'], 'steps_executed': 0, 'processes_executed': 0,
                  'next_skill': 'fine-start', 'receipts': [], 'execution_started': False, **_flags()}
        if cancelled:
            return result
        for action in plan['actions']:
            if result['steps_executed'] >= max_steps:
                result['status'] = 'partial'
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                result['status'] = 'timeout'
                break
            current = self._inspection()
            if any(current[key] != plan[key] for key in ('manifest_sha256', 'policy_sha256')):
                raise ValueError('Instalação/política mudou durante a execução')
            result['execution_started'] = True
            if action == 'verify':
                result['receipts'].append({'action': action, 'verification': 'local_file_hashes_only'})
            else:
                from integrations.itsfine_lifecycle import run_bounded, _public_process
                argv = [sys.executable, str(self._path('.its-fine/bin/fine.py')), '--root', str(self.root), action]
                if action == 'route':
                    argv.append(plan['run_id'])
                # Nenhuma opção, URL, shell ou caminho livre vem do plano.
                try:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        result['status'] = 'timeout'; break
                    completed = run_bounded(argv, cwd=self.root, timeout_seconds=remaining,
                                            max_output_bytes=MAX_OUTPUT)
                    result['processes_executed'] += int(completed['process_started'])
                except OSError:
                    result['status'] = 'failed'
                    break
                stdout, stderr = completed['stdout'], completed['stderr']
                result['receipts'].append({'action': action, **_public_process(completed), 'scope': 'read_only_cli'})
                if completed['status'] != 'completed' or completed['returncode'] != 0:
                    result['status'] = 'timeout' if completed['status']=='timeout' else 'failed'
                    result['stop_reason'] = completed['status']
                    break
                try:
                    data = _json(stdout)
                    if not isinstance(data, dict):
                        raise ValueError('Resposta de diagnóstico inválida')
                    if action == 'route':
                        next_skill = data.get('next')
                        if next_skill is not None and next_skill not in SKILLS:
                            raise ValueError('Próxima skill desconhecida')
                        result['next_skill'] = next_skill
                    else:
                        result['engines_catalogued'] = sorted(key for key in data if key in {'hf-peft', 'hf-encoder', 'hf-tts'})
                except (ValueError, TypeError):
                    result['status'] = 'failed'
                    break
            result['steps_executed'] += 1
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('status', 'verify', 'plan', 'run', 'engines-status',
        'install-plan', 'install', 'engine-plan', 'prepare-engine'))
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--run-id')
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--engine', choices=('hf-peft','hf-encoder','hf-tts'))
    parser.add_argument('--confirm', action='store_true')
    parser.add_argument('--timeout', type=float)
    args = parser.parse_args(argv)
    try:
        service = ItsFineCore(args.root)
        if args.operation in {'status','verify','engines-status'}:
            result = getattr(service,args.operation.replace('-','_'))()
        elif args.operation in {'install-plan','install'}:
            if args.archive is None: raise ValueError('TGZ obrigatório')
            result = service.install_plan(args.archive)
            if args.operation == 'install':
                result = service.install(result, confirm=args.confirm, timeout_seconds=args.timeout if args.timeout is not None else 120)
        elif args.operation in {'engine-plan','prepare-engine'}:
            if args.engine is None: raise ValueError('Motor obrigatório')
            result = service.engine_plan(args.engine)
            if args.operation == 'prepare-engine':
                result = service.engine_prepare(result, confirm=args.confirm, timeout_seconds=args.timeout if args.timeout is not None else 1200)
        else:
            result = service.plan(args.run_id)
            if args.operation == 'run':
                result = service.run_safe(result)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result.get('integrity_ok', True) and result.get('status') not in {
            'failed','timeout','partial','installation_failed','preparation_failed'} else 1
    except (OSError, ValueError):
        print(json.dumps({'status': 'blocked', 'reason': 'installation_or_plan_invalid', **_flags()}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
