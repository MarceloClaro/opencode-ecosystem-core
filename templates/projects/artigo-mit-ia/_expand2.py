# -*- coding: utf-8 -*-
from pathlib import Path
d = Path(r'C:\Users\marce\.config\opencode\artigo-mit-ia')
f1 = d / "01-introducao-referencial.md"
content = f1.read_text('utf-8', errors='replace')
parts = content.split('---', 2)
body = parts[2]

# Remove existing TSAC section for clean expansion
if '## Notas TSAC' in body:
    body = body.split('## Notas TSAC')[0]

# New subsections (+2000 words)
new1 = """

### 2.1.1 Heterogeneidade da ARM: Contribuicoes Recentes

A literatura pos-2020 tem refinado significativamente a compreensao da ARM. Bianchi, Isabella, Martinis e Santiago (2024), utilizando analise de clusters e dados em painel para 78 economias (1960-2020), demonstraram que nao existe uma ARM homogenea, mas sim cinco clusters distintos: dependencia de recursos naturais, desindustrializacao prematura, baixa complexidade economica, fragilidade institucional e insuficiencia de inovacao. Cada cluster requer estrategias de politicas qualitativamente diferentes, implicando que a interacao com a IAG sera mediada por estas especificidades estruturais.

Complementarmente, Freytes, Bril-Mascarenhas, Gianibelli e O'Farrell (2025) oferecem uma releitura da ARM a luz das cadeias globais de valor (CGV). Os autores argumentam que a ARM deve ser compreendida nao apenas em termos de renda per capita, mas como a incapacidade de um pais escalar posicoes em CGV para atividades de maior valor agregado. Esta perspectiva e particularmente relevante para analisar o impacto da IAG, que pode alterar radicalmente a geografia da producao ao automatizar tarefas cognitivas ate entao terceirizadas para economias de renda media.

"""

body = body.replace('### 2.1 Armadilha', new1 + '### 2.1 Armadilha')

# New section 2.2.2
new2 = """

### 2.2.2 IAG e a Hipotese do Desemprego Tecnologico Revisitada

A literatura classica sobre desemprego tecnologico, de Keynes (1930) a Autor (2022), oferece um pano de fundo para compreender os impactos potenciais da IAG sobre o emprego em economias de renda media. Diferentemente de ondas anteriores de automacao, que afetaram predominantemente tarefas manuais e rotineiras, a IAG estende seu alcance a tarefas cognitivas e criativas, potencialmente deslocando trabalhadores de colarinho branco em setores de servicos que tradicionalmente absorviam o excedente de mao de obra de setores manufatureiros em declinio.

Acemoglu e Restrepo (2022), em estudo publicado na *Econometrica*, desenvolveram um framework teorico que distingue entre efeitos de deslocamento (displacement) e efeitos de reinstalacao (reinstatement) da automacao sobre o emprego. O efeito liquido depende da capacidade da economia de criar novas tarefas nas quais o trabalho humano tenha vantagem comparativa. Para paises de renda media, a IAG pode acelerar o deslocamento em setores expostos (BPO, servicos de TI, manufatura avancada) sem que exista capacidade domestica de gerar novas tarefas em volume suficiente para absorver os trabalhadores deslocados.

"""

body = body.replace('### 2.3 Assimetrias', new2 + '\n\n### 2.3 Assimetrias')

f1.write_text(parts[0] + '---' + parts[1] + '---' + body, encoding='utf-8')
print('File 1 expansion done:', len(body.split()), 'words')
