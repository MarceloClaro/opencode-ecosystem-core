import re, os

base = 'C:/Users/marce/.config/opencode/artigo-mit-ia'
f1 = os.path.join(base, '01-introducao-referencial_corrigido.md')
f2 = os.path.join(base, '02-metodologia-resultados_corrigido.md')
f3 = os.path.join(base, '03-discussao-conclusao-referencias_corrigido.md')
out = os.path.join(base, 'ARTIGO_COMPLETO.md')

orphaned = {1, 3, 7, 8, 9, 12, 31}

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def split_body_tsac(content):
    marker = '## Notas TSAC'
    pos = content.find(marker)
    if pos >= 0:
        return content[:pos], content[pos + len(marker):]
    return content, ''

def extract_notes(tsac_text):
    notes = []
    pos = 0
    while pos < len(tsac_text):
        m = re.search(r'\[\^(\d+)\]:', tsac_text[pos:])
        if not m:
            break
        nid = int(m.group(1))
        start = pos + m.start()
        next_pos = tsac_text.find('[^', start + m.end())
        if next_pos < 0:
            next_pos = len(tsac_text)
        note_text = tsac_text[start:next_pos].strip()
        if nid not in orphaned:
            notes.append((nid, note_text))
        pos = next_pos
    return notes

f1c = read_file(f1); f2c = read_file(f2); f3c = read_file(f3)
b1, t1 = split_body_tsac(f1c)
b2, t2 = split_body_tsac(f2c)
b3, t3 = split_body_tsac(f3c)

all_notes = extract_notes(t1) + extract_notes(t2) + extract_notes(t3)
all_notes.sort(key=lambda x: x[0])

output = []
output.append(b1.strip())
output.append('')
output.append(b2.strip())
output.append('')
output.append(b3.strip())
output.append('')
output.append('## Notas TSAC')
output.append('')
for nid, note_text in all_notes:
    output.append(note_text)
    output.append('')

text = '\n'.join(output)

body_part = text.split('## Notas TSAC')[0]
tsac_part = text.split('## Notas TSAC')[1] if '## Notas TSAC' in text else ''
used = len(re.findall(r'\[\^(\d+)\]', body_part))
defined = len(re.findall(r'\[\^(\d+)\]', tsac_part))

print('Used in body:', used)
print('Defined in TSAC:', defined)
print('Total size:', len(text), 'chars')
with open(out, 'w', encoding='utf-8') as f:
    f.write(text)
print('Written:', out)
