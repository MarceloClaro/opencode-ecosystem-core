# -*- coding: utf-8 -*-
with open(r'C:\Users\marce\.config\opencode\artigo-mit-ia\02-metodologia-resultados_corrigido.md', 'r', encoding='utf-8') as f:
    content = f.read()
tsac_pos = content.find('## Notas TSAC')
after = content[tsac_pos + len('## Notas TSAC'):]
end_of_content = content.rstrip()
tsac_end = content.rfind('[^56]')
if tsac_end > 0:
    after_tsac = content[tsac_end + 5:].rstrip()
    print(f'Content after last TSAC entry: "{after_tsac[:200]}"')
    print(f'Total file length: {len(content)}')
    print(f'Last TSAC entry ends at: {tsac_end + 5}')
    print(f'Content ends at: {len(content)}')
    # Check if there's text after end of TSAC section
    remaining = content[tsac_end + 5:]
    print(f'Remaining chars: {len(remaining)}')
    print(f'Remaining text (first 100): "{remaining[:100]}"')
