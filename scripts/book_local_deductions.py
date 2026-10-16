"""R910: confere rastreabilidade editorial; não demonstra a semântica do texto."""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('Enunciado', 'Hipóteses', 'Lemas e dedução', 'Lean 4', 'Axiomas e alcance')
BLOCK = re.compile(r'\\begin\{formalizacao\}\{(F\d+)\}\{([^{}]+)\}(.*?)'
                   r'\\end\{formalizacao\}', re.S)
REF = re.compile(r'\\leanref\{([\w.]+)\}')


def validate_local_deductions(mapping: dict, texts: dict[str, str], audit: dict) -> dict:
    """Recusa omissões/nomes não auditados; a correspondência matemática exige leitura."""
    families = {f['id']: f for f in mapping['families']}
    errors, seen, used = [], set(), set()
    blocks = 0
    for source, text in texts.items():
        # Comentários não satisfazem o contrato de exposição visível.
        visible = re.sub(r'(?<!\\)%[^\n]*', '', text)
        parsed = list(BLOCK.finditer(visible))
        if visible.count(r'\begin{formalizacao}') != len(parsed):
            errors.append(f'Bloco local malformado: {source}')
        for match in parsed:
            fid, _, body = match.groups()
            family = families.get(fid)
            if family is None or family['kind'] == 'empirical_not_formalized':
                errors.append(f'Família inexistente ou empírica em bloco formal: {source}:{fid}')
                continue
            if source not in family['book_sources']:
                errors.append(f'Ocorrência não inventariada: {source}:{fid}')
            for field in FIELDS:
                label = r'\textbf{' + field + '.}'
                start = body.find(label)
                following = body[start+len(label):].split(r'\textbf{', 1)[0].strip()
                if start < 0 or not following:
                    errors.append(f'Campo ausente/vazio: {source}:{fid}:{field}')
            names = set(REF.findall(body))
            if not names or names - audit.keys():
                errors.append(f'Referência não auditada: {source}:{fid}:{sorted(names-audit.keys())}')
            if not names.intersection(family['theorems']):
                errors.append(f'Bloco sem proposição da família: {source}:{fid}')
            if r'\ref{sec:fundamentos-lean}' not in body:
                errors.append(f'Fundamentos lógicos sem remissão: {source}:{fid}')
            blocks += 1
            seen.add((fid, source))
            used.update(names)
    expected = {(f['id'], s) for f in families.values()
                if f['kind'] != 'empirical_not_formalized' for s in f['book_sources']}
    for fid, source in sorted(expected - seen):
        errors.append(f'Dedução local ausente: {source}:{fid}')
    if errors:
        raise ValueError('\n'.join(errors))
    return {'status': 'editorial_links_checked', 'local_blocks': blocks,
            'family_source_pairs': len(seen), 'referenced_declarations': len(used),
            'scope': 'Nomes, campos e ocorrências; não certifica a tradução semântica nem dados.'}


def main() -> None:
    mapping = json.loads((ROOT/'docs/book-math-map-r908.json').read_text())
    receipt = json.loads((ROOT/'docs/verification-book-lean-r908.json').read_text())
    audit = {n: ax for result in receipt['files'].values() for n, ax in result['axioms'].items()}
    texts = {str(p.relative_to(ROOT)): p.read_text() for p in (ROOT/'livro-core').glob('mod-*.tex')}
    print(json.dumps(validate_local_deductions(mapping, texts, audit), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
