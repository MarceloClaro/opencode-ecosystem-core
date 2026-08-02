#!/usr/bin/env python3
"""
add_lettrine_vic.py — Adiciona letras capitulares (lettrine) aos fragmentos VictoriaRegia.

Estratégia:
- Lê fragmentos .tex da pasta canonical (fragmentos/) — já estão limpos
- Adiciona lettrine colorido ANTES da primeira palavra real (ignorando comandos LaTeX)
- Mantém o lettrine DENTRO do comando \textit{...} ou \textbf{...} se existir

Uso: python3 scripts/add_lettrine_vic.py
"""

import re
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parent.parent / 'projetos' / 'molambudos'
VIC_FRAG = PROJ / 'Molambudos_VictoriaRegia' / 'fragmentos'

SECTION_COLORS = {'MEM': 'mem', 'DOC': 'doc', 'LUC': 'luc', 'CONT': 'cont'}


def section_color(fid: str) -> str:
    for p, c in SECTION_COLORS.items():
        if fid.startswith(p):
            return c
    return 'black'


def find_first_real_word(text: str):
    """
    Encontra a primeira palavra real no texto, ignorando comandos LaTeX.
    
    Returns:
        (prefix, first_letter, rest_of_word, suffix)
        prefix = tudo antes da primeira palavra (comandos LaTeX, aspas, etc.)
        first_letter = primeira letra REAL (ignorando comandos)
        rest_of_word = resto da primeira palavra
        suffix = tudo após a primeira palavra
    """
    prefix = ''
    
    # Scan the text to find the first real character
    pos = 0
    while pos < len(text):
        c = text[pos]
        
        # Skip whitespace
        if c in ' \t\n\r':
            prefix += c
            pos += 1
            continue
        
        # Skip LaTeX commands
        if c == '\\' and pos + 1 < len(text) and text[pos+1].isalpha():
            # Find the end of the command name
            cmd_end = pos + 1
            while cmd_end < len(text) and text[cmd_end].isalpha():
                cmd_end += 1
            command = text[pos:cmd_end]
            
            # Check if this command takes an argument (braces)
            # Skip optional args too
            cmd_full = command
            temp_pos = cmd_end
            while temp_pos < len(text) and text[temp_pos] in ' \t':
                cmd_full += text[temp_pos]
                temp_pos += 1
            if temp_pos < len(text) and text[temp_pos] == '[':
                # Skip optional argument [ ... ]
                depth = 1
                cmd_full += '['
                temp_pos += 1
                while temp_pos < len(text) and depth > 0:
                    if text[temp_pos] == '[': depth += 1
                    elif text[temp_pos] == ']': depth -= 1
                    cmd_full += text[temp_pos]
                    temp_pos += 1
            if temp_pos < len(text) and text[temp_pos] == '{':
                # Skip mandatory argument { ... }
                depth = 1
                cmd_full += '{'
                temp_pos += 1
                while temp_pos < len(text) and depth > 0:
                    if text[temp_pos] == '{': depth += 1
                    elif text[temp_pos] == '}': depth -= 1
                    cmd_full += text[temp_pos]
                    temp_pos += 1
            
            prefix += cmd_full
            pos = temp_pos
            continue
        
        # Skip punctuation that's before the first word
        if c in '.,;:!?\\\'\"`‘’“”\u2018\u2019\u201c\u201d\u2013\u2014-–—':
            prefix += c
            pos += 1
            continue
        
        # Skip brackets and quotes
        if c in '[](){}':
            prefix += c
            pos += 1
            continue
        
        # Found a real character — extract the first word
        # Only stop at whitespace (let punctuation stay in the word)
        word = ''
        while pos < len(text) and text[pos] not in ' \t\n\r':
            word += text[pos]
            pos += 1
        
        if not word:
            prefix += text[pos]
            pos += 1
            continue
        
        # The word is the raw characters. For the lettrine:
        # first_letter = the first meaningful char (letter or digit)
        # rest_of_word = everything after first_letter to end of word
        # But we need to handle the case where there's LaTeX inside
        first = word[0]
        rest = word[1:]
        suffix = text[pos:]
        return prefix, first, rest, suffix
    
    return prefix, '', '', ''


def find_matching_brace(s: str, start: int) -> int:
    """Encontra a } correspondente à { na posição start."""
    depth = 1
    i = start + 1
    while i < len(s) and depth > 0:
        if s[i] == '{': depth += 1
        elif s[i] == '}': depth -= 1
        if depth == 0: return i
        i += 1
    return -1


def process_fragment(fpath: Path) -> bool:
    content = fpath.read_text('utf-8')
    fid = fpath.stem
    color = section_color(fid)
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        s = line.strip()
        if not s.startswith('\\noindent'):
            continue
        if '\\rule{' in s or '\\hyperlink' in s or '\\vspace' in s or s.startswith('\\noindent #') or s.startswith('#'):
            continue
            
        # Skip date/location headers and metadata lines (e.g., \textit{1915 --- ...})
        plain_line = re.sub(r'\\[a-zA-Z]+(\[.*?\])?(\{.*?\})?', '', s).strip()
        plain_line = re.sub(r'[{}]', '', plain_line).strip()
        
        # Header detection: if line is a date header or short metadata header
        if re.search(r'^(19\d\d|18\d\d|20\d\d|\d{2}/\d{2}|\textbf\{19|\textit\{19|Notas|Hospital|Instituto|DSM|PARECER|DIAGNÓSTICO|REGISTRO|#)', s):
            continue
        if len(plain_line) < 40 and re.search(r'\d{4}|Ceará|Quixeramobim|Barbacena|Colônia', plain_line):
            continue
        if not plain_line or plain_line[0].isdigit() or plain_line[0] in '#-/\\':
            continue
        if plain_line.startswith('#') or plain_line.startswith('##'):
            continue
            
        ni = s.find('\\noindent')
        after = s[ni + 9:].lstrip()
        indent = line[:len(line) - len(line.lstrip())]
        
        # Check if starts with \cmd{ (textit, textbf, etc.)
        cmd_m = re.match(r'\\([a-zA-Z]+)\{(.*)', after)
        
        if cmd_m:
            cmd_name = cmd_m.group(1)
            brace_pos = after.index('{')
            close_pos = find_matching_brace(after, brace_pos)
            
            if close_pos == -1:
                print(f"  ⚠️  {fid}: cant find matching brace")
                continue
            
            inner = after[brace_pos + 1:close_pos]
            after_cmd = after[close_pos + 1:]
            
            # Find first real word in inner text
            prefix, fl, rw, rest = find_first_real_word(inner)
            if not fl:
                print(f"  ⚠️  {fid}: no real word found in inner")
                continue
            
            # Build: \cmd{<prefix>{\renewcommand{...}\lettrine{fl}{rw}}<rest>}
            ltr_block = rf'\lettrine[lines=3,findent=2pt,nindent=4pt]{{\textcolor{{{color}}}{{{fl}}}}}{{{rw}}}'
            new_inner = prefix + ltr_block + rest
            new_after = '\\' + cmd_name + '{' + new_inner + '}' + after_cmd
        else:
            # Plain text
            prefix, fl, rw, rest = find_first_real_word(after)
            if not fl:
                print(f"  ⚠️  {fid}: no real word found")
                continue
            
            ltr_block = rf'\lettrine[lines=3,findent=2pt,nindent=4pt]{{\textcolor{{{color}}}{{{fl}}}}}{{{rw}}}'
            new_after = prefix + ltr_block + rest
        
        lines[i] = indent + new_after
        
        # Verify line brace balance
        if lines[i].count('{') != lines[i].count('}'):
            print(f"  ⚠️  MISMATCH line in {fid}: {lines[i]}")
            lines[i] = line  # revert
            continue
        
        print(f"  ✅ {fid}: {color}.{fl} ({rw[:15]})")
        content = '\n'.join(lines)
        fpath.write_text(content, 'utf-8')
        return True
    
    print(f"  ⚠️  {fid}: no content line found")
    return False


def main():
    ok = err = 0
    for sec in ['mem', 'doc', 'luc', 'cont']:
        for f in sorted((VIC_FRAG / sec).glob('*.tex')):
            name = f.stem
            if name.startswith('DOC-') and len(name) > 4:
                try:
                    if int(name[4:]) >= 20: continue
                except: pass
            if name.startswith('LUC-') and len(name) > 4:
                try:
                    if int(name[4:]) >= 13: continue
                except: pass
            try:
                if process_fragment(f):
                    ok += 1
            except Exception as e:
                print(f"  ❌ {name}: {e}")
                err += 1
    print(f"\n✅ {ok} lettrines applied, {err} errors")


if __name__ == '__main__':
    main()
