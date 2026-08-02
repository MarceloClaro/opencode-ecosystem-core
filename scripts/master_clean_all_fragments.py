#!/usr/bin/env python3
"""
master_clean_all_fragments.py — Remove todas as duplicidades de datas/cabeçalhos
e ancora as capitulares rigorosamente no 1º parágrafo de cada fragmento (74/74).
"""

import os
import re
import shutil
from pathlib import Path

PROJ = Path('/home/marceloclaro/opencode-ecosystem-core/projetos/molambudos')
VIC_FRAG = PROJ / 'Molambudos_VictoriaRegia' / 'fragmentos'
CANON_FRAG = PROJ / 'fragmentos'

SECTION_COLORS = {
    'MEM': 'mem',
    'DOC': 'doc',
    'LUC': 'luc',
    'CONT': 'cont'
}

def get_color(fid):
    for k, v in SECTION_COLORS.items():
        if fid.startswith(k):
            return v
    return 'black'

def clean_fragment(fpath: Path):
    fid = fpath.stem
    color = get_color(fid)
    content = fpath.read_text(encoding='utf-8')
    lines = content.splitlines()
    
    # Step 1: Remove existing \lettrine calls so we start clean
    clean_lines = []
    for line in lines:
        line_no_ltr = re.sub(
            r'\\lettrine(\[[^\]]*\])?\{[^}]*\\textcolor\{[^}]*\}\{([^}]*)\}\}\{([^}]*)\}',
            r'\2\3',
            line
        )
        line_no_ltr = re.sub(
            r'\\lettrine(\[[^\]]*\])?\{([^}]*)\}\{([^}]*)\}',
            r'\2\3',
            line_no_ltr
        )
        clean_lines.append(line_no_ltr)
        
    lines = clean_lines
    
    # Step 2: Remove duplicate date/location header lines
    dedup_lines = []
    for i, l in enumerate(lines):
        s = l.strip()
        if s.startswith('\\noindent \\textit{') and s.endswith('}'):
            next_idx = i + 1
            while next_idx < len(lines) and not lines[next_idx].strip():
                next_idx += 1
            if next_idx < len(lines):
                next_s = lines[next_idx].strip()
                if next_s.startswith('\\noindent \\textbf{') or next_s.startswith('\\textbf{'):
                    continue
        dedup_lines.append(l)
        
    lines = dedup_lines
    
    # Step 3: Identify the VERY FIRST real narrative story paragraph
    target_idx = -1
    for i, l in enumerate(lines):
        s = l.strip()
        if not s:
            continue
        if any(s.startswith(x) for x in ['%', '\\section*', '\\markboth', '\\vspace', '\\rule', '\\hyperlink', '↪ Links', '---//---']):
            continue
        if '\\rule{' in s:
            continue
            
        plain = re.sub(r'^\\noindent\s*', '', s).strip()
        plain = re.sub(r'\\[a-zA-Z]+(\[.*?\])?(\{.*?\})?', '', plain).strip()
        plain = re.sub(r'[{}]', '', plain).strip()
        
        if not plain:
            continue
            
        # Check if line is a header/metadata line vs narrative story
        is_header = False
        if s.startswith('\\noindent \\textbf{19') or s.startswith('\\noindent \\textit{19') or s.startswith('\\noindent \\textbf{20') or s.startswith('\\noindent \\textit{20'):
            is_header = True
        elif plain.startswith('#') or plain.startswith('##') or plain.startswith('---'):
            is_header = True
        elif len(plain) < 65 and re.search(r'^(19\d\d|18\d\d|20\d\d|\d{2}/\d{2}|Notas|Hospital|Instituto|DSM|PARECER|DIAGNÓSTICO|REGISTRO|Data:|Período:|DOCUMENTO|TRANSCR|INSTR|ADENDO)', plain, re.IGNORECASE):
            is_header = True
        elif len(plain) < 55 and ('---' in plain or '1979' in plain or '2026' in plain or '1915' in plain or '1917' in plain) and not plain.startswith('Três') and not plain.startswith('Meu') and not plain.startswith('Eu'):
            is_header = True
        elif plain[0] in '#-/::':
            is_header = True
            
        if is_header:
            continue
            
        target_idx = i
        break
        
    # Fallback if no line matched strict filtering
    if target_idx == -1:
        for i, l in enumerate(lines):
            s = l.strip()
            if not s or any(s.startswith(x) for x in ['%', '\\section*', '\\markboth', '\\vspace', '\\rule', '\\hyperlink', '↪ Links', '---//---']):
                continue
            if '\\rule{' in s: continue
            plain = re.sub(r'^\\noindent\s*', '', s).strip()
            if plain and not re.search(r'^(19\d\d|18\d\d|20\d\d)', plain):
                target_idx = i
                break

    if target_idx != -1:
        # Check if opening line is short (< 120 chars) and merge with next paragraph
        l_text = lines[target_idx]
        plain_len = len(re.sub(r'\\[a-zA-Z]+(\[.*?\])?(\{.*?\})?', '', l_text))
        
        next_idx = target_idx + 1
        while next_idx < len(lines) and not lines[next_idx].strip():
            next_idx += 1
            
        if next_idx < len(lines) and lines[next_idx].strip().startswith('\\noindent') and not any(x in lines[next_idx] for x in ['\\rule', '\\vspace', '↪ Links', '---//---']):
            if plain_len < 120:
                next_para = lines[next_idx].strip()
                if next_para.startswith('\\noindent'):
                    next_para = next_para[9:].lstrip()
                lines[target_idx] = lines[target_idx].strip() + ' ' + next_para
                lines[next_idx] = ''
                
        # Now apply \lettrine to the first letter of lines[target_idx]
        line = lines[target_idx]
        ni = line.find('\\noindent')
        if ni != -1:
            indent = line[:ni]
            after = line[ni+9:].lstrip()
        else:
            indent = line[:len(line)-len(line.lstrip())]
            after = line.lstrip()
            
        cmd_m = re.match(r'^\\([a-zA-Z]+)\{(.*)', after)
        if cmd_m:
            cmd_name = cmd_m.group(1)
            rest_cmd = cmd_m.group(2)
            # Find first real word letter inside rest_cmd
            fl_m = re.search(r'([a-zA-Zà-úÀ-Ú0-9])', rest_cmd)
            if fl_m:
                fl_pos = fl_m.start()
                fl = fl_m.group(1)
                prefix_text = rest_cmd[:fl_pos]
                word_after = rest_cmd[fl_pos+1:]
                w_match = re.match(r'^([a-zA-Zà-úÀ-Ú0-9]*)(.*)', word_after)
                rw = w_match.group(1) if w_match else ''
                rest_text = w_match.group(2) if w_match else word_after
                ltr_code = rf'\lettrine[lines=2,depth=0,findent=3pt,nindent=0pt,lhang=0]{{\textcolor{{{color}}}{{{fl}}}}}{{{rw}}}'
                lines[target_idx] = indent + '\\' + cmd_name + '{' + prefix_text + ltr_code + rest_text
        else:
            fl_m = re.search(r'([a-zA-Zà-úÀ-Ú0-9])', after)
            if fl_m:
                fl_pos = fl_m.start()
                fl = fl_m.group(1)
                prefix_text = after[:fl_pos]
                word_after = after[fl_pos+1:]
                w_match = re.match(r'^([a-zA-Zà-úÀ-Ú0-9]*)(.*)', word_after)
                rw = w_match.group(1) if w_match else ''
                rest_text = w_match.group(2) if w_match else word_after
                ltr_code = rf'\lettrine[lines=2,depth=0,findent=3pt,nindent=0pt,lhang=0]{{\textcolor{{{color}}}{{{fl}}}}}{{{rw}}}'
                lines[target_idx] = indent + prefix_text + ltr_code + rest_text

    text = '\n'.join(lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    fpath.write_text(text, encoding='utf-8')
    rel = fpath.relative_to(VIC_FRAG)
    (CANON_FRAG / rel).write_text(text, encoding='utf-8')
    return target_idx != -1

def main():
    files = sorted(VIC_FRAG.glob('**/*.tex'))
    success = 0
    for f in files:
        if clean_fragment(f):
            success += 1
    print(f"✅ Master audit & cleaning concluído: {success}/{len(files)} fragmentos atualizados!")

if __name__ == '__main__':
    main()
