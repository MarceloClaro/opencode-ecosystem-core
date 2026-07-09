#!/usr/bin/env python3
import sys, json, re
from pathlib import Path
sys.path.insert(0, '.')
from auto_score_qualis import score_manuscript, RUBRIC

r = score_manuscript('_pipeline_work')
for k, v in r['criterios'].items():
    print(f'{k}: {v}/10  ({RUBRIC[k]["desc"]})')

print(f'\nTotal: {r["total"]}/100')

for md_file in sorted(Path('_pipeline_work').rglob('*.md')):
    content = md_file.read_text(encoding='utf-8', errors='ignore')
    print(f'\n--- {md_file.name} ---')
    print(f'  Chars: {len(content)}')
    print(f'  Words: {len(content.split())}')
    print(f'  [^: {content.count("[^")}')
    print(f'  doi.org: {content.count("doi.org")}')
    print(f'  Disponivel em:: {content.count("Disponivel em:")}')
    print(f'  DOIs: {len(re.findall(r"10\.\d{4,}", content))}')
    print(f'  ABNT: {content.count("ABNT")}')
    print(f'  NBR: {content.count("NBR 6023") + content.count("NBR 6028")}')
