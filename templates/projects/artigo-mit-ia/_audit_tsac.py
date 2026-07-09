# -*- coding: utf-8 -*-
"""TSAC Cross-File Audit - verifica consistencia de notas entre os 3 arquivos."""
import re, os
from collections import Counter

base = r'C:\Users\marce\.config\opencode\artigo-mit-ia'
files = {
    'f1': '01-introducao-referencial_corrigido.md',
    'f2': '02-metodologia-resultados_corrigido.md',
    'f3': '03-discussao-conclusao-referencias_corrigido.md'
}

all_defined = {}
all_used = {}

for fkey, fname in files.items():
    path = os.path.join(base, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tsac_marker = '## Notas TSAC'
    tsac_pos = content.find(tsac_marker)
    body = content[:tsac_pos] if tsac_pos >= 0 else content
    tsac_sec = content[tsac_pos + len(tsac_marker):] if tsac_pos >= 0 else ''
    
    body_refs = set()
    for m in re.finditer(r'\[\^(\d+)\]', body):
        body_refs.add(int(m.group(1)))
    
    def_refs = set()
    for m in re.finditer(r'\[\^(\d+)\]:?\s*', tsac_sec):
        nid = int(m.group(1))
        def_refs.add(nid)
        if nid not in all_defined:
            all_defined[nid] = fkey
    
    for ref in body_refs:
        if ref not in all_used:
            all_used[ref] = []
        all_used[ref].append(fkey)
    
    print('=== ' + fname + ' ===')
    print('  Chars: ' + str(len(content)) + ' | Body refs: ' + str(len(body_refs)) + ' | TSAC defs: ' + str(len(def_refs)))
    only_body = sorted(body_refs - def_refs)
    only_tsac = sorted(def_refs - body_refs)
    if only_body: print('  WARN refs sem def local: ' + str(only_body))
    if only_tsac: print('  WARN defs sem uso local: ' + str(only_tsac))
    print()

defined_set = set(all_defined.keys())
used_set = set(all_used.keys())
undefined = used_set - defined_set
unused = defined_set - used_set
def_counter = Counter()
for nid, fk in all_defined.items():
    def_counter[nid] += 1
dups = {k: v for k, v in def_counter.items() if v > 1}

print('=== CROSS-FILE AUDIT ===')
print('Unique refs: ' + str(len(used_set)) + ' | Unique defs: ' + str(len(defined_set)))
if undefined:   print('FAIL undefined refs: ' + str(sorted(undefined)))
else:           print('OK all refs defined')
if unused:      print('WARN unused defs: ' + str(sorted(unused)))
else:           print('OK all defs used')
if dups:
    print('FAIL duplicate defs: ' + str(dict(sorted(dups.items()))))
    for nid in sorted(dups.keys()):
        found_in = []
        for fkey, fname in files.items():
            p = os.path.join(base, fname)
            with open(p, encoding='utf-8') as f:
                c = f.read()
            if '## Notas TSAC' in c:
                sec = c[c.find('## Notas TSAC'):]
                if re.search(r'\[\^' + str(nid) + r'\]:?', sec):
                    found_in.append(fkey)
        print('  [^' + str(nid) + '] in: ' + str(found_in))
else:
    print('OK no duplicate defs')
