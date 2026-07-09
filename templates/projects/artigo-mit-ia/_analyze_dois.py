# -*- coding: utf-8 -*-
import re

with open(r'C:\Users\marce\.config\opencode\artigo-mit-ia\03-discussao-conclusao-referencias_corrigido.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the start of references
ref_start = None
for i, line in enumerate(lines):
    if '## Refer' in line:
        ref_start = i
        break

if ref_start is None:
    print("ERROR: References section not found!")
    exit(1)

# Each reference is on its own line, preceded by a blank line
ref_lines = []
for line in lines[ref_start+1:]:
    line = line.rstrip('\n')
    if line.strip():
        ref_lines.append(line)

print(f"Total references found: {len(ref_lines)}\n")

has_doi_url = 0
has_other_url = 0
no_url = 0

for i, ref in enumerate(ref_lines, 1):
    has_doi = 'doi.org/' in ref
    has_any_url = 'https://' in ref or 'http://' in ref
    
    if has_doi:
        status = 'DOI'
        has_doi_url += 1
    elif has_any_url:
        status = 'URL_SEM_DOI'
        has_other_url += 1
    else:
        status = 'SEM_URL'
        no_url += 1
    
    preview = ref[:150]
    # replace non-ascii for display
    safe = preview.encode('ascii', 'replace').decode('ascii')
    print(f"{i:2d}. [{status}] {safe}")

print(f"\n--- Resumo ---")
print(f"Com DOI:           {has_doi_url}")
print(f"Com URL (sem DOI):  {has_other_url}")
print(f"Sem URL:            {no_url}")
print(f"Total:              {len(ref_lines)}")
