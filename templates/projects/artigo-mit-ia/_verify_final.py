import re
base = 'C:/Users/marce/.config/opencode/artigo-mit-ia'
with open(base + '/ARTIGO_COMPLETO.md', 'r', encoding='utf-8') as f:
    text = f.read()

print('=== FINAL VERIFICATION ===')
sections = re.findall(r'^##\s+\d+\.\s+(.+)$', text, re.MULTILINE)
print('Sections:', len(sections))
for s in sections:
    print('  -', s.strip()[:60])

body = text.split('## Notas TSAC')[0]
tsac_all = text.split('## Notas TSAC')[1]
tsac = tsac_all.split('## Refer')[0] if '## Refer' in tsac_all else tsac_all
refs = set(int(m.group(1)) for m in re.finditer(r'\[\^(\d+)\]', body))
defs = set(int(m.group(1)) for m in re.finditer(r'\[\^(\d+)\]', tsac))
missing = refs - defs
unused = defs - refs
print('\nTSAC:', len(refs), 'refs,', len(defs), 'defs')
print('Ref IDs:', sorted(refs))
if missing: print('MISSING:', sorted(missing))
if unused: print('UNUSED:', sorted(unused))

bad = text.count(chr(65533))
print('\nEncoding:', bad, 'replacement characters')
print('Total chars:', len(text))
print('YAML:', text.startswith('---'))

# Check for section numbering issues
for m in re.finditer(r'^(#{2,3})\s+(.+)$', text, re.MULTILINE):
    level, title = m.groups()
    t = title.strip()
    count = len(re.findall(r'^' + re.escape(level) + r'\s+' + re.escape(t) + r'$', text, re.MULTILINE))
    if count > 1:
        print('DUPLICATE SECTION:', level, t, '(' + str(count) + 'x)')

# Check sub-section ordering (5.1 vs 5.1.1)
sec5_lines = []
lines = text.split('\n')
in_sec5 = False
for i, line in enumerate(lines):
    if line.startswith('## 5.'):
        in_sec5 = True
    elif line.startswith('## 6.') or line.startswith('## Notas') or line.startswith('## Refer'):
        in_sec5 = False
    if in_sec5 and line.strip().startswith('### '):
        sec5_lines.append((i, line.strip()))
print('\nSection 5 ordering:')
for ln, l in sec5_lines:
    print(f'  L{ln}: {l}')
