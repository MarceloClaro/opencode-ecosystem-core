"""R910: índice tipográfico determinístico de dependências realmente auditadas."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODES = {'propext': 'P', 'Classical.choice': 'C', 'Quot.sound': 'Q'}


def render_axiom_macros(receipt: dict, root: Path) -> str:
    if receipt.get('status') != 'machine_checked':
        raise ValueError('Recibo sem compilação aceita')
    lines = ['% R910: gerado de auditoria Lean; não editar manualmente.']
    for relative, result in sorted(receipt['files'].items()):
        path = root / relative
        if (not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != result['sha256']
                or result.get('status') != 'machine_checked' or result.get('returncode') != 0):
            raise ValueError('Fonte Lean diverge do recibo: ' + relative)
        names, audit = result['theorems'], result['axioms']
        if not names or set(names) != set(audit):
            raise ValueError('Auditoria de declarações incompleta')
        for name in sorted(names):
            unknown = set(audit[name]) - CODES.keys()
            if unknown:
                raise ValueError('Axioma não permitido: ' + repr(unknown))
            codes = ','.join(code for ax, code in CODES.items() if ax in audit[name]) or 'nenhum'
            lines.append(r'\expandafter\def\csname leanaxioms@' + name + r'\endcsname{' + codes + '}')
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path, default=ROOT/'docs/verification-book-lean-r908.json')
    args = parser.parse_args()
    text = render_axiom_macros(json.loads(args.receipt.read_text()), ROOT)
    (ROOT/'livro-core/lean-axiomas.tex').write_text(text)


if __name__ == '__main__':
    main()
