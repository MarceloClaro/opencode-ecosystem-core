#!/usr/bin/env python3
"""R1057: apresenta SVG e mantém a fonte Mermaid recolhida para auditoria.

Não altera o bloco gerado por `sync_readme_flowcharts.py`, não remove fontes e
não usa rede. O SVG é a visualização primária; o bloco Mermaid fica em
`<details>` e continua disponível para leitura e para os testes históricos.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FOLDER = 'docs/architecture/animated'
MANIFEST = FOLDER + '/manifest.json'
GALLERY = 'docs/architecture/ANIMATED.md'
FENCE = re.compile(r'^```mermaid[^\S\n]*\n(.*?)^```[^\S\n]*$', re.M | re.S)
START = '<!-- core-flowcharts:start -->'
END = '<!-- core-flowcharts:end -->'
MARK = '<!-- svg-presentation:'


def _inside(root: Path, relative: str) -> Path:
    root = root.resolve()
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts or '\\' in relative or ':' in relative:
        raise ValueError(f'Caminho não confinado: {relative}')
    resolved = (root / p).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f'Symlink fora da raiz: {relative}')
    return resolved


def _paths(root: Path) -> list[Path]:
    candidates = [root / 'README.md', root / 'ARCHITECTURE.md']
    docs = root / 'docs'
    if docs.is_dir():
        candidates.extend(sorted(docs.rglob('*.md')))
    return [p for p in candidates if p.is_file() and p.relative_to(root).as_posix() != GALLERY]


def _relative(root: Path, path: Path, document: Path) -> str:
    return os.path.relpath(path, document.parent).replace(os.sep, '/')


def _replacement(root: Path, item: dict, source: str, document: Path) -> str:
    folder = root / FOLDER
    name = item['id']
    svg = _relative(root, folder / (name + '.svg'), document)
    gif = _relative(root, folder / (name + '.gif'), document)
    png = _relative(root, folder / (name + '.png'), document)
    mmd = _relative(root, folder / (name + '.mmd'), document)
    title = html.escape(item.get('title', name), quote=True)
    body = source if source.endswith('\n') else source + '\n'
    return (
        f'{MARK}{name} -->\n'
        f'<img src="{svg}" alt="{title} — diagrama estático" width="100%">\n\n'
        f'<sub>[GIF]({gif}) · [PNG]({png}) · [Fonte Mermaid]({mmd})</sub>\n\n'
        '<details>\n<summary>Fonte Mermaid (auditoria)</summary>\n\n'
        f'```mermaid\n{body}```\n\n</details>'
    )


def _inside_core_block(text: str, position: int) -> bool:
    start, end = text.find(START), text.find(END)
    return start != -1 and end != -1 and start < position < end


def run(root: Path, *, check: bool = False) -> dict:
    root = root.resolve()
    manifest_path = _inside(root, MANIFEST)
    by_source = {}
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        by_source = {row['source_sha256']: row for row in manifest['diagrams']}
    replaced = 0
    changed_files: list[str] = []
    unmatched: list[str] = []
    for document in _paths(root):
        relative = document.relative_to(root).as_posix()
        text = document.read_text(encoding='utf-8')
        pieces = []
        cursor = 0
        found = False
        for match in FENCE.finditer(text):
            source = match.group(1)
            sha = hashlib.sha256(source.encode()).hexdigest()
            item = by_source.get(sha)
            if item is None:
                if relative not in unmatched:
                    unmatched.append(relative)
                continue
            if _inside_core_block(text, match.start()):
                continue
            prefix = text[max(0, match.start() - 500):match.start()]
            if MARK in prefix:
                continue
            pieces.append(text[cursor:match.start()])
            pieces.append(_replacement(root, item, source, document))
            cursor = match.end()
            replaced += 1
            found = True
        if not found:
            continue
        pieces.append(text[cursor:])
        updated = ''.join(pieces)
        if updated != text:
            changed_files.append(relative)
            if not check:
                document.write_text(updated, encoding='utf-8')
    return {'changed': bool(changed_files), 'replaced': replaced,
            'files': changed_files, 'unmatched': unmatched, 'check': check}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    try:
        summary = run(args.root, check=args.check)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Apresentação SVG bloqueada: {error}', file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False))
    return int(args.check and summary['changed'])


if __name__ == '__main__':
    raise SystemExit(main())
