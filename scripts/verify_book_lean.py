"""R908: execução real do Lean, auditoria de axiomas e custódia das fontes.

Não há fallback sintático. Use somente fontes de prova de confiança: o Lean
elabora programas e táticas. As fontes do livro são mantidas neste repositório.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
TOOLCHAIN = 'leanprover/lean4:v4.34.1'
MATHLIB_REV = 'd13f23b723b8a846827a245b89c10fc7d3f11612'
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def lean_tokens(source: str) -> str:
    """Apaga comentários aninhados e strings, conservando quebras de linha."""
    out, i, depth = [], 0, 0
    while i < len(source):
        if depth:
            if source.startswith('/-', i):
                depth += 1; i += 2
            elif source.startswith('-/', i):
                depth -= 1; i += 2
            else:
                out.append('\n' if source[i] == '\n' else ' '); i += 1
        elif source.startswith('/-', i):
            depth = 1; i += 2
        elif source.startswith('--', i):
            end = source.find('\n', i)
            i = len(source) if end < 0 else end
        elif source[i] == '"':
            i += 1
            while i < len(source):
                if source[i] == '\\':
                    i += 2
                elif source[i] == '"':
                    i += 1; break
                else:
                    out.append('\n' if source[i] == '\n' else ' '); i += 1
        else:
            out.append(source[i]); i += 1
    return ''.join(out)


def source_policy_errors(source: str) -> list[str]:
    tokens = lean_tokens(source)
    forbidden = ('sorry', 'admit', 'axiom', 'sorryAx', 'unsafe', 'native_decide')
    errors = [f'termo não permitido: {word}' for word in forbidden
              if re.search(r'\b' + re.escape(word) + r'\b', tokens)]
    if re.search(r'#(?:eval|exec|print)\b|\b(?:run_tac|run_cmd)\b', tokens):
        errors.append('execução/comando de auditoria embutido na fonte de prova')
    return errors


def theorem_names(source: str) -> list[str]:
    """Convenção dos módulos do livro: um namespace e declarações nomeadas."""
    tokens = lean_tokens(source)
    namespaces = re.findall(r'^namespace\s+([\w.]+)\s*$', tokens, re.M)
    if len(namespaces) != 1:
        raise ValueError('Cada módulo do livro exige exatamente um namespace explícito')
    prefix = namespaces[0] + '.'
    names = re.findall(r'^(?:theorem|lemma)\s+([\w\u2080-\u209f]+)\b', tokens, re.M)
    declarations = re.findall(r'\b(?:theorem|lemma)\b', tokens)
    if len(declarations) != len(names):
        raise ValueError('Declaração fora do formato auditável: theorem/lemma público no início da linha')
    if not names or len(names) != len(set(names)):
        raise ValueError('Teoremas ausentes ou nomes duplicados')
    return [prefix + name for name in names]


def receipt_matches_sources(receipt: dict, root: Path) -> bool:
    files = {**receipt.get('files', {}), **receipt.get('context_files', {})}
    for relative, item in files.items():
        path = (root / relative).resolve()
        if (not path.is_relative_to(root.resolve()) or not path.is_file()
                or file_sha256(path) != item.get('sha256')):
            return False
    return bool(files)


def checked_dependency(path: Path, revision: str) -> dict:
    actual = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'],
                                     text=True, timeout=10).strip()
    dirty = subprocess.check_output(['git', '-C', str(path), 'status', '--porcelain',
                                    '--untracked-files=no'], text=True, timeout=10).strip()
    if actual != revision or dirty:
        raise ValueError(f'Dependência divergente ou modificada: {path.name}')
    return {'revision': actual, 'tracked_worktree_clean': True}


def context_sources() -> list[Path]:
    return sorted({*ROOT.glob('livro-core/*.tex'), *ROOT.glob('livro-core/gen*.py'),
                   ROOT/'livro-core/lean/lean-toolchain', ROOT/'livro-core/lean/lakefile.toml',
                   ROOT/'livro-core/lean/lake-manifest.json', Path(__file__).resolve(),
                   ROOT/'tests/test_r908_book_lean.py', ROOT/'docs/VERIFICACAO_FORMAL_LIVRO_R908.md',
                   ROOT/'docs/book-math-map-r908.json', ROOT/'README.md',
                   ROOT/'specs/SPEC-935-R908-livro-provas-lean4.md',
                   ROOT/'docs/superpowers/plans/2026-10-15-livro-lean4.md'})


def validate_math_map(mapping: dict, known_names: set[str]) -> dict:
    families = mapping['families']
    ids = [f['id'] for f in families]
    if not families or len(ids) != len(set(ids)):
        raise ValueError('Inventário vazio ou famílias duplicadas')
    formal = 0
    for family in families:
        names = family['theorems']
        if family['kind'] == 'empirical_not_formalized':
            if names:
                raise ValueError('Observação empírica não recebe prova de ocorrência')
        else:
            formal += 1
            if not names or set(names) - known_names:
                raise ValueError(f"Prova inexistente na matriz: {family['id']}")
        if not family['hypotheses_and_limits'] or not family['book_sources']:
            raise ValueError('Família sem hipótese ou fonte')
        for name in family['book_sources']:
            if not (ROOT/name).is_file():
                raise ValueError(f'Fonte do livro ausente: {name}')
    return {'families': len(families), 'formal_model_families': formal,
            'empirical_families_outside_proof_claim': len(families)-formal}


def parse_axioms(output: str, names: list[str]) -> dict[str, list[str]]:
    found = {}
    pattern = r"'([^']+)'\s+(?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)"
    for match in re.finditer(pattern, output):
        name = match[1]
        if name in found:
            raise ValueError(f'Auditoria duplicada: {name}')
        axioms = [s.strip() for s in (match[2] or '').split(',') if s.strip()]
        if set(axioms) - ALLOWED_AXIOMS:
            raise ValueError(f'Dependências não permitidas em {name}: {axioms}')
        found[name] = axioms
    if set(found) != set(names):
        raise ValueError(f'Auditoria incompleta: ausentes={sorted(set(names)-set(found))}')
    return found


def run_lean(source: str, project: Path, *, timeout: int = 180,
             audit_names: list[str] | None = None) -> dict:
    """Compila uma fonte e, opcionalmente, inspeciona cada teorema no mesmo processo."""
    errors = source_policy_errors(source)
    if errors:
        return {'status': 'rejected_source', 'returncode': None, 'errors': errors}
    lake = Path.home() / '.elan/bin/lake'
    if not lake.is_file() or not (project / '.lake/packages/mathlib').is_dir():
        return {'status': 'environment_unavailable', 'returncode': None,
                'errors': ['Lean/Mathlib local indisponível; não foi executada prova']}
    code = source + '\n' + '\n'.join(f'#print axioms {n}' for n in audit_names or []) + '\n'
    env = dict(os.environ, ELAN_TOOLCHAIN=TOOLCHAIN)
    fd, temporary = tempfile.mkstemp(suffix='.lean', prefix='book-r908-', dir=project)
    started = time.monotonic()
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(code)
        command = [str(lake), 'env', 'lean', temporary]
        try:
            proc = subprocess.run(command, cwd=project, env=env, capture_output=True,
                                  text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'returncode': None,
                    'errors': [f'Prazo de {timeout}s excedido']}
        output = proc.stdout + proc.stderr
        result = {'status': 'compiler_rejected' if proc.returncode else 'machine_checked',
                  'returncode': proc.returncode, 'seconds': round(time.monotonic()-started, 3),
                  'output': output, 'command': ['lake', 'env', 'lean', '<source-and-axiom-audit>']}
        if proc.returncode == 0 and audit_names:
            try:
                result['axioms'] = parse_axioms(output, audit_names)
            except ValueError as exc:
                result.update(status='audit_rejected', errors=[str(exc)])
        return result
    finally:
        Path(temporary).unlink(missing_ok=True)


def verify(project: Path, files: list[Path], output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, ELAN_TOOLCHAIN=TOOLCHAIN)
    lean = Path.home() / '.elan/bin/lean'
    version = subprocess.check_output([str(lean), '--version'], env=env, text=True, timeout=20).strip()
    revision = subprocess.check_output(['git', '-C', str(project / '.lake/packages/mathlib'),
                                        'rev-parse', 'HEAD'], text=True, timeout=10).strip()
    if revision != MATHLIB_REV:
        raise ValueError(f'Mathlib diferente da revisão fixada: {revision}')
    if 'version 4.34.1,' not in version:
        raise ValueError(f'Lean diferente da versão fixada: {version}')
    if (project/'lean-toolchain').read_text().strip() != TOOLCHAIN:
        raise ValueError('Toolchain do projeto de compilação divergente')
    expected_lock = json.loads((ROOT/'livro-core/lean/lake-manifest.json').read_text())
    actual_lock = json.loads((project/'lake-manifest.json').read_text())
    actual_revisions = {p['name']: p['rev'] for p in actual_lock['packages']}
    dependencies = {}
    for package in expected_lock['packages']:
        name, rev = package['name'], package['rev']
        if actual_revisions.get(name) != rev:
            raise ValueError(f'Lockfile do projeto divergente: {name}')
        dependencies[name] = checked_dependency(project/'.lake/packages'/name, rev)
    actual_lean = Path(subprocess.check_output(
        [str(Path.home()/'.elan/bin/elan'), 'which', 'lean'], env=env, text=True, timeout=20).strip())
    context = {p.relative_to(ROOT).as_posix(): {'sha256': file_sha256(p)} for p in context_sources()}
    report = {'status': 'machine_checked', 'lean_version': version,
              'toolchain': TOOLCHAIN, 'mathlib_revision': revision,
              'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'allowed_foundational_axioms': sorted(ALLOWED_AXIOMS),
              'verification_scope': 'declarações Lean e hipóteses explícitas; não valida dados empíricos nem IEEE-754',
               'external_validation': False, 'files': {}, 'context_files': context,
               'environment': {'dependencies': dependencies, 'lean_binary_sha256': file_sha256(actual_lean),
                               'project_config_sha256': {p: file_sha256(project/p) for p in
                                   ('lean-toolchain', 'lakefile.toml', 'lake-manifest.json')}}}
    for path in files:
        before = file_sha256(path)
        source = path.read_text(encoding='utf-8')
        names = theorem_names(source)
        result = run_lean(source, project, audit_names=names)
        (output_dir / (path.stem + '.log')).write_text(result.get('output', str(result)), encoding='utf-8')
        relative = path.resolve().relative_to(ROOT).as_posix()
        report['files'][relative] = {**result, 'sha256': before, 'theorems': names}
        if result['status'] != 'machine_checked' or file_sha256(path) != before:
            report['status'] = 'rejected'
    controls = {
        'positive': 'import Mathlib\ntheorem control_ok : (2 : ℚ) + 3 = 5 := by norm_num',
        'false_equality': 'import Mathlib\ntheorem control_bad : (2 : ℚ) + 3 = 6 := by norm_num',
        'open_proof': 'import Mathlib\ntheorem control_hole : False := by sorry',
        'invented_axiom': 'import Mathlib\naxiom invented : False',
        'mutated_ema': 'import Mathlib\ntheorem wrong_ema : (7/10 : ℚ)*(1/2)+(3/10)*(9/10)=32/50 := by norm_num',
    }
    report['controls'] = {name: run_lean(code, project) for name, code in controls.items()}
    expected = {'positive': 'machine_checked', 'false_equality': 'compiler_rejected',
                 'open_proof': 'rejected_source', 'invented_axiom': 'rejected_source',
                 'mutated_ema': 'compiler_rejected'}
    if any(report['controls'][name]['status'] != status for name, status in expected.items()):
        report['status'] = 'rejected'
    if not receipt_matches_sources(report, ROOT):
        report['status'] = 'rejected'
    mapping = json.loads((ROOT/'docs/book-math-map-r908.json').read_text())
    report['mapping'] = validate_math_map(mapping, {
        n for item in report['files'].values() for n in item['theorems']})
    report['theorem_count'] = sum(len(r['theorems']) for r in report['files'].values())
    (output_dir / 'receipt.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=ROOT/'livro-core/lean')
    parser.add_argument('--output', type=Path, default=ROOT/'outputs/core-r908/lean')
    args = parser.parse_args(argv)
    files = sorted((ROOT/'livro-core/lean').glob('*.lean'))
    if not files:
        raise SystemExit('Nenhuma fonte Lean do livro foi encontrada')
    # Um erro de ambiente nunca deixa um recibo anterior aprovado neste destino.
    args.output.mkdir(parents=True, exist_ok=True)
    try:
        report = verify(args.project.resolve(), files, args.output)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        (args.output/'receipt.json').write_text(json.dumps(
            {'status': 'rejected', 'error': str(exc), 'external_validation': False},
            ensure_ascii=False, indent=2)+'\n')
        print(f'Verificação recusada: {exc}')
        return 1
    print(json.dumps({k: report[k] for k in ('status', 'theorem_count', 'lean_version', 'mathlib_revision')}, ensure_ascii=False))
    return int(report['status'] != 'machine_checked')


if __name__ == '__main__':
    raise SystemExit(main())
