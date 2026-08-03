#!/usr/bin/env python3
"""
clean_headers_and_lettrines.py — Remove duplicatas de cabeçalho de data e ajusta
lettrines nos parágrafos narrativos sem sobreposição de texto.
"""

import os
import re
import shutil
from pathlib import Path

PROJ = Path('/home/marceloclaro/opencode-ecosystem-core/projetos/molambudos')
VIC_FRAG = PROJ / 'Molambudos_VictoriaRegia' / 'fragmentos'
CANON_FRAG = PROJ / 'fragmentos'

def main():
    files = sorted(VIC_FRAG.glob('**/*.tex'))
    cleaned_cnt = 0

    for f in files:
        content = f.read_text(encoding='utf-8')
        lines = content.splitlines()
        
        # 1. Remove duplicate consecutive date headers (e.g., repeated "1915 --- ..." lines)
        new_lines = []
        for i, l in enumerate(lines):
            if l.strip() and new_lines and l.strip() == new_lines[-1].strip():
                continue
            new_lines.append(l)
            
        lines = new_lines
        
        # 2. Find lettrine line and check if short
        lettrine_idx = -1
        for i, l in enumerate(lines):
            if '\\lettrine' in l:
                lettrine_idx = i
                break
                
        if lettrine_idx != -1:
            l_text = lines[lettrine_idx]
            plain_text = re.sub(r'\\[a-zA-Z]+(\[.*?\])?(\{.*?\})?', '', l_text)
            
            # If paragraph is short (< 120 chars), merge with next paragraph
            next_idx = lettrine_idx + 1
            while next_idx < len(lines) and not lines[next_idx].strip():
                next_idx += 1
                
            if next_idx < len(lines) and lines[next_idx].strip().startswith('\\noindent') and not any(x in lines[next_idx] for x in ['\\rule', '\\vspace', '↪ Links', '---//---']):
                if len(plain_text) < 120:
                    next_para = lines[next_idx].strip()[9:].lstrip()
                    lines[lettrine_idx] = lines[lettrine_idx].strip() + ' ' + next_para
                    lines[next_idx] = ''
                    
            # Update lettrine parameters to lines=2,depth=0,findent=3pt,nindent=0pt,lhang=0
            def replace_lettrine(match):
                prefix = match.group(1) or ''
                arg1 = match.group(2)
                arg2 = match.group(3)
                return r'\lettrine[lines=2,depth=0,findent=3pt,nindent=0pt,lhang=0]{' + arg1 + '}{' + arg2 + '}'
                
            lines[lettrine_idx] = re.sub(r'\\lettrine(\[[^\]]*\])?\{([^}]*)\}\{([^}]*)\}', replace_lettrine, lines[lettrine_idx])
            
        text = '\n'.join([l for l in lines if l is not None])
        text = re.sub(r'\n{3,}', '\n\n', text)
        f.write_text(text, encoding='utf-8')
        rel = f.relative_to(VIC_FRAG)
        (CANON_FRAG / rel).write_text(text, encoding='utf-8')
        cleaned_cnt += 1

    print(f"✅ {cleaned_cnt} fragmentos higienizados: duplicatas de data removidas e sobreposição corrigida!")

if __name__ == '__main__':
    main()
