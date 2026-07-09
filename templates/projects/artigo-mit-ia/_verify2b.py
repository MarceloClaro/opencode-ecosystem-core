# -*- coding: utf-8 -*-
with open(r'C:\Users\marce\.config\opencode\artigo-mit-ia\02-metodologia-resultados_corrigido.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all [^56] positions
import re
positions = [(m.start(), m.end(), content[max(0,m.start()-20):m.end()+50]) for m in re.finditer(r'\[\^56\]', content)]
print(f'Found {len(positions)} [^56] instances:')
for i, (start, end, ctx) in enumerate(positions):
    print(f'  #{i}: pos {start}-{end}: ...{ctx}...')

# Find where TSAC section is
tsac_start = content.find('## Notas TSAC')
if tsac_start >= 0:
    # Look for the last [^xx] after the TSAC header
    tsac_content = content[tsac_start:]
    last_note = list(re.finditer(r'\[\^\d+\]', tsac_content))[-1]
    print(f'\nLast TSAC note: {last_note.group()} at offset {last_note.start()}')
    print(f'TSAC content after last note: "{tsac_content[last_note.end():].strip()[:100]}"')
    
    # Now find what's at the end of the file
    end_of_tsac = tsac_content[last_note.end():].strip()
    print(f'\nAfter last TSAC definition, remaining: "{end_of_tsac[:200]}"')
