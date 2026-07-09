# -*- coding: utf-8 -*-
from pathlib import Path
d = Path(r'C:\Users\marce\.config\opencode\artigo-mit-ia')
f3 = d / '03-discussao-conclusão-referencias.md'
c3 = f3.read_text('utf-8', errors='replace')
m = '### 5.1 A Ambivalência Estrutural da IAG para a ARM'
if m in c3:
new = '\n\n### 5.1.1 IAG e a Nova Divisão Internacional do Trabalho Cognitivo\n\nA IAG pode estar reconfigurando a divisão internacional do trabalho em direção a uma nova divisão cognitiva. Se as economias avançadas concentrarem a capacidade de gerar e controlar a IA que automatiza o trabalho cognitivo, a posição dos países de renda média pode deteriorar-se.\n\nAutor (2022) distingue entre deslocamento e reinstalação de tarefas. Acemoglu e Johnson (2023) argumentam que a trajetória da mudança tecnológica reflete escolhas sociais. Rodrik (2024) adverte que a IAG pode acelerar a desindustrialização prematura ao automatizar tarefas de serviços.\n'
c3 = c3.replace(m, new + '\n' + m, 1)
f3.write_text(c3, encoding='utf-8')
body = c3.split('## Referências')[0] if '## Referências' in c3 else c3
print('File 3 expand OK. Body:', len(body.split()))
else:
print('Marker not found')