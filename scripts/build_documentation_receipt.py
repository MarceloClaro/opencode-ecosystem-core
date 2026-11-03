"""R919: manifesto documental atual; hashes não são recibos de execução.

Uso: python3 -m scripts.build_documentation_receipt [--check].
Sem rede, inferência, atualização de fontes ou importação de código inventariado.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile

from scripts.build_architecture_maps import build_snapshot

DEFAULT_OUTPUT = 'docs/verification-documentation-r916-ollama-quantizacao.json'
ARTIFACT_PATHS = (
    'README.md', 'docs/architecture_map.html',
    'docs/architecture/architecture-inventory.json', 'docs/architecture/flows.json',
    'docs/architecture/dependencies.mmd', 'docs/architecture/mermaid-correspondence.json',
    'docs/architecture/dependencies-mermaid.svg', 'docs/architecture/dependencies.svg',
    'docs/architecture/overview.dot', 'docs/architecture/overview.svg',
    'docs/architecture/curated-overview.svg', 'docs/architecture/viewer-template.html',
    'docs/ARQUITETURA_COMPLETA_CORE_R916.md', 'docs/ESTADO_ATUAL_CORE_R916.md',
    'docs/architecture/MODELOS_E_ECONOMIA_DE_TOKENS_R916.md',
    'docs/architecture/QUANTIZACAO_LOCAL_GITHUB_R916.md',
)


def _path(root: Path, relative: str) -> Path:
    if (not isinstance(relative, str) or not relative or
            any(ord(char) < 32 for char in relative) or '\\' in relative or ':' in relative or
            any(part in {'', '.', '..'} for part in relative.split('/')) or
            PurePosixPath(relative).is_absolute()):
        raise ValueError('Caminho relativo não canônico')
    path = root / relative
    if any(part.is_symlink() for part in (path, *path.parents) if part != root):
        raise ValueError(f'Symlink recusado: {relative}')
    if not path.resolve().is_relative_to(root):
        raise ValueError(f'Caminho fora da raiz: {relative}')
    return path


def _digest(root: Path, relative: str) -> dict:
    path = _path(root, relative)
    if not path.is_file():
        raise ValueError(f'Artefato ausente ou não regular: {relative}')
    data = path.read_bytes()
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def collect_receipt(root: Path) -> dict:
    root = Path(root).resolve(strict=True)
    artifacts = {name: _digest(root, name) for name in ARTIFACT_PATHS}
    inventory = json.loads(_path(root, 'docs/architecture/architecture-inventory.json').read_text(encoding='utf-8'))
    catalog = json.loads(_path(root, 'docs/architecture/flows.json').read_text(encoding='utf-8'))
    git = inventory['git']
    if git.get('source') != 'worktree':
        raise ValueError('Recibo atual exige inventário worktree')
    current = build_snapshot(root, ref=git.get('requested_ref', 'HEAD'), source='worktree')
    if current != inventory:
        raise ValueError('Inventário obsoleto; regenere contra as fontes atuais')
    source = catalog.get('source', {})
    if (source.get('mode') != 'worktree' or source.get('base_commit') != git['commit'] or
            source.get('worktree_sha256') != git['worktree_sha256']):
        raise ValueError('Catálogo não corresponde ao inventário worktree')
    flows = catalog['flows']
    if not isinstance(flows, list) or not flows:
        raise ValueError('Catálogo de fluxos vazio ou inválido')
    ids, files, rows = set(), set(), []
    manifest = {row['path']: row for row in git['source_manifest']}
    for flow in flows:
        identifier, relative = flow['id'], flow['file']
        if not isinstance(identifier, str) or not re.fullmatch(r'[a-z0-9_-]+', identifier) or identifier in ids:
            raise ValueError('ID de fluxo inválido ou duplicado')
        ids.add(identifier)
        source_path = 'docs/architecture/' + relative
        path = _path(root, source_path)
        if not relative.startswith('flows/') or path.suffix != '.mmd' or source_path in files:
            raise ValueError('Fonte Mermaid inválida ou duplicada')
        files.add(source_path)
        svg_path = str(PurePosixPath(source_path).with_suffix('.svg'))
        for name in (source_path, svg_path):
            artifacts[name] = _digest(root, name)
        for anchor in flow['sources']:
            entry = manifest.get(anchor['path'])
            if entry is None or anchor.get('sha256') != entry.get('sha256'):
                raise ValueError('Âncora ausente ou divergente do manifesto worktree')
        rows.append({'id': identifier, 'source_path': source_path, 'svg_path': svg_path,
                     'source_sha256': artifacts[source_path]['sha256'],
                     'svg_sha256': artifacts[svg_path]['sha256']})
    config = json.loads(_path(root, 'opencode.json').read_text(encoding='utf-8'))
    if config.get('model') != 'ollama-local/llama3.2':
        raise ValueError('Modelo padrão difere do baseline declarado; revisão explícita necessária')
    if any(_digest(root, name) != row for name, row in artifacts.items()):
        raise ValueError('Artefato alterado durante a coleta')
    return {
        'schema': 'documentation-artifact-receipt-v1', 'review': 'R916/R918/R919',
        'verification_scope': 'current_artifact_hashes_not_runtime_or_render_execution',
        'source': {key: git[key] for key in ('commit', 'source', 'worktree_sha256')},
        'counts': {**inventory['counts'], 'flows': len(rows),
                   'source_anchors': sum(len(flow['sources']) for flow in flows)},
        'render_manifest': rows, 'artifacts': artifacts,
        'externally_validated': False, 'model_default_changed': False,
        'limitations': [
            'Hashes de SVG existentes não comprovam renderização nesta rodada.',
            'Não comprova testes, inferência, qualidade de modelos ou validação externa.',
            'Inventário cobre fontes rastreadas; não incorpora fontes não rastreadas.',
            'Recibos históricos e seus resultados não foram promovidos a atuais.',
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', default=DEFAULT_OUTPUT, help='Caminho docs/verification-documentation-*.json')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        output = _path(root, args.output)
        if (output.parent != root / 'docs' or not output.name.startswith('verification-documentation-') or
                output.suffix != '.json' or args.output in ARTIFACT_PATHS):
            raise ValueError('Destino deve ser recibo documental separado dos artefatos')
        if not output.parent.is_dir():
            raise ValueError('Diretório de destino ausente')
        receipt = collect_receipt(root)
        if args.check:
            equal = output.is_file() and json.loads(output.read_text(encoding='utf-8')) == receipt
            print('Recibo corresponde aos artefatos atuais.' if equal else 'Recibo ausente ou divergente.')
            return 0 if equal else 1
        descriptor, name = tempfile.mkstemp(dir=output.parent, prefix='.documentation-receipt-', suffix='.tmp')
        try:
            with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
                json.dump(receipt, stream, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
                stream.write('\n')
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, output)
        finally:
            Path(name).unlink(missing_ok=True)
        print(f'Recibo de hashes: {args.output}; {receipt["counts"]["flows"]} fluxos.')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Erro de recibo: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
