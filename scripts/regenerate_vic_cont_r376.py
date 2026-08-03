#!/usr/bin/env python3
"""
regenerate_vic_cont_r376.py — Regenera os fragmentos CONT-05..13 da edição
VictoriaRegia a partir de molambudos.md (decisão autoral R376: "o md é a nova
edição"), usando o motor do build_miolo.py + pós-processamento editorial:
  - ### header  -> \\subsection*{...}
  - {{Placeholder}} -> Placeholder (sem chaves duplas)
Backup prévio: Molambudos_VictoriaRegia/_archive/backup_R376/
"""
import re
import sys
from pathlib import Path

ROOT = Path('/home/marceloclaro/opencode-ecosystem-core')
sys.path.insert(0, str(ROOT / 'scripts'))

from build_miolo import parse_fragments, fragment_to_tex, MOLAMBUROS  # noqa: E402

VIC_FRAG = ROOT / 'projetos/molambudos/Molambudos_VictoriaRegia/fragmentos'


def postprocess(tex: str) -> str:
    # 1) Resolver placeholders duplos {{X}} -> X (o build escapa para \{\{X\}\})
    tex = re.sub(r'\\\{\\\{(.+?)\\\}\\\}', r'\1', tex)
    # 2) Converter \noindent \#\#\# X em \subsection*{X}
    tex = re.sub(r'\\noindent \\#\\#\\#\s*(.+)', r'\\subsection*{\1}', tex)
    return tex


def main():
    md_content = MOLAMBUROS.read_text(encoding='utf-8')
    header, fragments = parse_fragments(md_content)
    frag_map = {f['id']: f for f in fragments}
    ids = [f'CONT-{n:02d}' for n in range(5, 14)]
    missing = [i for i in ids if i not in frag_map]
    if missing:
        print('ERRO: faltam no md:', missing)
        sys.exit(1)
    for fid in ids:
        tex, subdir = fragment_to_tex(frag_map[fid])
        tex = postprocess(tex)
        out = VIC_FRAG / subdir / f'{fid}.tex'
        out.write_text(tex, encoding='utf-8')
        n_sec = tex.count('\\subsection*')
        print(f'  ok {fid} -> {out.name} ({len(tex.splitlines())} linhas, {n_sec} subsections)')


if __name__ == '__main__':
    main()
