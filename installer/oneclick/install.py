#!/usr/bin/env python3
"""Instalador one-click do OpenCode Ecosystem Core.

Modo padrão: --check (não altera nada).
--apply exige --yes e só executa npm/pip/uv/venv; apt e scripts oficiais
(curl | bash) são apenas impressos para revisão do operador.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('catalog.json')
LOG_DIR = ROOT / 'reports' / 'installer'
SAFE_KINDS = {'npm', 'pip', 'uv', 'venv-pip', 'requirements'}


def load_catalog(path=CATALOG):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    return validate_catalog(data)


def validate_catalog(data):
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('catálogo inválido')
    entries = data.get('entries')
    if not isinstance(entries, list) or not entries:
        raise ValueError('entries obrigatórias')
    ids = set()
    for entry in entries:
        for key in ('id', 'group', 'check', 'install', 'license'):
            if key not in entry:
                raise ValueError(f'{entry.get("id", "?")}: campo {key} ausente')
        if entry['id'] in ids:
            raise ValueError(f'id duplicado: {entry["id"]}')
        ids.add(entry['id'])
        if not isinstance(entry['check'], list) or not entry['check']:
            raise ValueError(f'{entry["id"]}: check inválido')
        if entry['install'].get('kind') not in SAFE_KINDS | {'apt', 'manual'}:
            raise ValueError(f'{entry["id"]}: kind inválido')
        if entry['install']['kind'] in {'npm', 'pip', 'uv', 'venv-pip'} and not entry['install'].get('package'):
            raise ValueError(f'{entry["id"]}: package obrigatório')
        if entry['install']['kind'] == 'requirements' and not entry['install'].get('requirements'):
            raise ValueError(f'{entry["id"]}: requirements obrigatório')
    return data


def requested(catalog, groups=None, only=None):
    entries = catalog['entries']
    if only:
        wanted = {value.strip() for value in only.split(',') if value.strip()}
        unknown = wanted - {entry['id'] for entry in entries}
        if unknown:
            raise ValueError(f'ids desconhecidos: {sorted(unknown)}')
        return [entry for entry in entries if entry['id'] in wanted]
    if groups:
        wanted = set(groups)
        unknown = wanted - set(catalog.get('groups', {}))
        if unknown:
            raise ValueError(f'grupos desconhecidos: {sorted(unknown)}')
        return [entry for entry in entries if entry['group'] in wanted]
    return entries


def _resolve(command, cwd=ROOT):
    first = Path(command[0])
    if first.is_absolute():
        return str(first) if first.exists() else None
    if '/' in command[0]:
        candidate = Path(cwd) / first
        return str(candidate) if candidate.exists() else None
    return shutil.which(command[0])


def check_entry(entry, *, cwd=ROOT, timeout=5):
    workdir = Path(entry.get('cwd', cwd))
    if not workdir.is_absolute():
        workdir = ROOT / workdir
    executable = _resolve(entry['check'], workdir)
    if executable is None:
        return {'id': entry['id'], 'group': entry['group'], 'installed': False,
                'ok': False, 'version': None, 'error': 'comando ausente'}
    command = [executable, *entry['check'][1:]]
    try:
        proc = subprocess.run(command, cwd=str(workdir), capture_output=True, text=True,
                              stdin=subprocess.DEVNULL,
                              timeout=entry.get('timeout', timeout))
        output = (proc.stdout or proc.stderr or '').strip().splitlines()
        version = output[0][:160] if output else ''
        text = '\n'.join(output)
        expected = entry.get('ok_if')
        ok = proc.returncode == 0 or (isinstance(expected, str) and expected in text)
        return {'id': entry['id'], 'group': entry['group'], 'installed': True,
                'ok': ok, 'version': version,
                'error': None if ok else f'rc={proc.returncode}'}
    except subprocess.TimeoutExpired:
        return {'id': entry['id'], 'group': entry['group'], 'installed': True,
                'ok': True, 'version': 'instalado; versão não respondeu',
                'error': None}
    except OSError as exc:
        return {'id': entry['id'], 'group': entry['group'], 'installed': True,
                'ok': False, 'version': None, 'error': type(exc).__name__}


def _run(command, log, timeout=900):
    log.write('$ ' + ' '.join(command) + '\n')
    log.flush()
    try:
        proc = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=timeout)
        log.write(proc.stdout or '')
        log.write(proc.stderr or '')
        log.write(f'\n[rc={proc.returncode}]\n')
        log.flush()
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired) as exc:
        log.write(f'[erro] {type(exc).__name__}: {exc}\n')
        return False


def apply_entry(entry, log):
    install = entry['install']
    kind = install['kind']
    if kind == 'apt':
        log.write(f'[manual] sudo apt-get install -y {install["package"]}\n')
        return {'id': entry['id'], 'status': 'manual', 'command': f'sudo apt-get install -y {install["package"]}'}
    if kind == 'manual':
        log.write(f'[manual] {install["command"]}\n')
        return {'id': entry['id'], 'status': 'manual', 'command': install['command']}
    if kind == 'npm':
        npm = shutil.which('npm')
        if not npm:
            return {'id': entry['id'], 'status': 'blocked', 'reason': 'npm ausente'}
        ok = _run([npm, 'install', '-g', install['package']], log)
        return {'id': entry['id'], 'status': 'installed' if ok else 'failed'}
    if kind == 'pip':
        python = ROOT / '.venv/bin/python'
        command = [str(python if python.exists() else 'python3'), '-m', 'pip', 'install']
        if not python.exists():
            command.append('--user')
        command.append(install['package'])
        ok = _run(command, log)
        return {'id': entry['id'], 'status': 'installed' if ok else 'failed'}
    if kind == 'uv':
        uv = shutil.which('uv')
        if not uv:
            return {'id': entry['id'], 'status': 'blocked', 'reason': 'uv ausente'}
        ok = _run([uv, 'tool', 'install', install['package']], log)
        return {'id': entry['id'], 'status': 'installed' if ok else 'failed'}
    if kind == 'venv-pip':
        python = ROOT / '.venv/bin/python'
        if not python.exists():
            return {'id': entry['id'], 'status': 'blocked', 'reason': '.venv ausente'}
        ok = _run([str(python), '-m', 'pip', 'install', *install['package'].split()], log)
        return {'id': entry['id'], 'status': 'installed' if ok else 'failed'}
    if kind == 'requirements':
        python = ROOT / '.venv/bin/python'
        if not python.exists():
            ok = _run([sys.executable, '-m', 'venv', str(ROOT / '.venv')], log)
            if not ok:
                return {'id': entry['id'], 'status': 'failed', 'reason': 'venv'}
        requirements = ROOT / install['requirements']
        if not requirements.exists():
            return {'id': entry['id'], 'status': 'blocked', 'reason': 'requirements.txt ausente'}
        ok = _run([str(python), '-m', 'pip', 'install', '-r', str(requirements)], log)
        return {'id': entry['id'], 'status': 'installed' if ok else 'failed'}
    return {'id': entry['id'], 'status': 'blocked', 'reason': 'kind desconhecido'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='somente diagnóstico (padrão)')
    parser.add_argument('--apply', action='store_true', help='executa instalações seguras')
    parser.add_argument('--yes', action='store_true', help='confirma --apply')
    parser.add_argument('--group', action='append', default=[], help='grupo (repetível)')
    parser.add_argument('--only', help='ids separados por vírgula')
    parser.add_argument('--json', action='store_true', help='saída JSON')
    parser.add_argument('--catalog', default=str(CATALOG))
    args = parser.parse_args(argv)
    catalog = load_catalog(args.catalog)
    entries = requested(catalog, args.group or None, args.only)
    checks = [check_entry(entry) for entry in entries]
    if not args.apply:
        result = {'mode': 'check', 'count': len(checks),
                  'missing': [row['id'] for row in checks if not row['ok']],
                  'checks': checks,
                  'next': 'revise e rode --apply --yes (apt/scripts oficiais ficam manuais)'}
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else
              '\n'.join(f"{'OK ' if row['ok'] else 'MISS'} {row['id']:20} {row.get('version') or row.get('error')}" for row in checks))
        return 0
    if not args.yes:
        print('Recusado: --apply exige --yes. Nada foi alterado.')
        return 2
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    log_path = LOG_DIR / f'oneclick-{stamp}.log'
    results = []
    with log_path.open('w', encoding='utf-8') as log:
        log.write(f'# oneclick {stamp}\n')
        for entry in entries:
            current = check_entry(entry)
            if current['ok']:
                results.append({'id': entry['id'], 'status': 'already_ok'})
                continue
            results.append(apply_entry(entry, log))
    receipt = {'schema_version': 1, 'stamp': stamp, 'log': str(log_path.relative_to(ROOT)),
               'results': results, 'manual_required': [r for r in results if r['status'] == 'manual'],
               'failed': [r for r in results if r['status'] in {'failed', 'blocked'}]}
    receipt_path = LOG_DIR / f'oneclick-{stamp}.json'
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(receipt, ensure_ascii=False, indent=2) if args.json else
          json.dumps({'log': receipt['log'], 'receipt': str(receipt_path.relative_to(ROOT)),
                      'manual': len(receipt['manual_required']), 'failed': len(receipt['failed'])},
                     ensure_ascii=False))
    return 0 if not receipt['failed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
