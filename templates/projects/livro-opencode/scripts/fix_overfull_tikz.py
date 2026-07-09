#!/usr/bin/env python3
"""
Script para corrigir overfull boxes em TikZ pictures nos capítulos do livro.
Envolve tikzpictures muito largas em resizebox{\textwidth}{!}{...}
e adiciona escala a tikzpictures sem escala definida.
"""
import re, os

# Capítulo: [(linha_inicio, linha_fim, fator_escala)]
# Os fatores foram determinados pela magnitude do overfull
FIXES = {
    '13-capitulo6-token-economy.tex': [
        # 303pt overfull - cadeia de hashes (muito horizontal)
        (1120, 1144, 0.45),
        # 131pt overfull - sistema de staking
        (730, 748, 0.55),
        # 70pt overfull - outra figura larga
        (180, 195, 0.55),
        # 32pt overfull
        (170, 190, 0.65),
        # 27pt overfull
        (420, 435, 0.65),
    ],
    '15-capitulo8-dissertacao-banca.tex': [
        # 281pt overfull - percurso acadêmico
        (160, 180, 0.40),
        # 107pt overfull - pipeline artigos
        (1510, 1525, 0.50),
        # 74pt overfull
        (445, 470, 0.55),
        # 51pt overfull
        (1200, 1215, 0.60),
        # 39pt overfull
        (1372, 1385, 0.60),
        # 26pt overfull
        (1225, 1240, 0.65),
        # 23pt overfull
        (2005, 2020, 0.65),
    ],
    '10-capitulo3-opencode-arquitetura.tex': [
        # 138pt overfull
        (1180, 1195, 0.50),
        # 136pt overfull
        (2340, 2355, 0.50),
        # 79pt overfull
        (2315, 2330, 0.55),
        # 77pt overfull
        (545, 560, 0.55),
        # 48pt overfull
        (1140, 1155, 0.60),
        # 47pt overfull
        (535, 550, 0.60),
        # 26pt overfull
        (1185, 1198, 0.65),
    ],
    '12-capitulo5-trust-governanca.tex': [
        # 96pt overfull
        (515, 535, 0.50),
        # 93pt overfull
        (798, 815, 0.50),
        # 44pt overfull
        (690, 705, 0.60),
        # 37pt overfull
        (268, 280, 0.60),
        # 31pt overfull
        (1130, 1145, 0.65),
    ],
    '09-capitulo2-ia-agentes.tex': [
        # 93pt overfull
        (665, 680, 0.50),
        # 38pt overfull
        (1952, 1965, 0.60),
        # 30pt overfull
        (490, 505, 0.65),
    ],
    '08-capitulo1-mat-est.tex': [
        # 67pt overfull
        (225, 238, 0.55),
        # 42pt overfull
        (1082, 1095, 0.60),
        # 28pt overfull
        (288, 305, 0.65),
    ],
    '11-capitulo4-scanner-metacognicao.tex': [
        # 56pt overfull
        (1382, 1410, 0.55),
        # 45pt overfull
        (1903, 1920, 0.55),
        # 44pt overfull
        (1165, 1180, 0.55),
        # 44pt overfull
        (165, 176, 0.55),
        # 40pt overfull
        (1733, 1748, 0.60),
        # 37pt overfull
        (1425, 1440, 0.60),
        # 27pt overfull
        (210, 240, 0.65),
    ],
    '16-apendice-exercicios.tex': [
        # 23pt overfull
        (36, 50, 0.65),
    ],
    '18-apendice-codigos.tex': [
        # 71pt overfull (x2)
        (468, 480, 0.55),
    ],
}

CAPITULOS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'capitulos')

def find_tikzpicture_bounds(lines, start_search, end_search):
    """Find the begin/end of tikzpicture nearest to given line range."""
    best_start = -1
    best_end = -1
    
    for i in range(max(0, start_search - 10), min(len(lines), end_search + 10)):
        if '\\begin{tikzpicture}' in lines[i]:
            best_start = i
        if best_start > 0 and '\\end{tikzpicture}' in lines[i]:
            best_end = i
            if best_start >= start_search - 10 and best_end <= end_search + 10:
                return best_start, best_end
    
    return best_start, best_end

def add_scale_to_tikzpicture(line, scale):
    """Add scale parameter to tikzpicture begin."""
    # Check if already has options
    m = re.match(r'(.*\\begin\{tikzpicture\})(\[.*\])(.*)', line)
    if m:
        # Already has options - add scale
        opts = m.group(2).strip('[]')
        if 'scale=' not in opts:
            new_opts = f'[{opts}, scale={scale}, every node/.style={{scale={scale}}}]'
        else:
            new_opts = f'[scale={scale}, every node/.style={{scale={scale}}}, {opts}]'
        return f'{m.group(1)}{new_opts}{m.group(3)}'
    else:
        # No options yet
        m = re.match(r'(.*\\begin\{tikzpicture\})(.*)', line)
        return f'{m.group(1)}[scale={scale}, every node/.style={{scale={scale}}}]'

for filename, fixes in FIXES.items():
    filepath = os.path.join(CAPITULOS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Arquivo não encontrado: {filename}")
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    lines = content.split('\n')
    
    modified_count = 0
    for start_line, end_line, scale in fixes:
        # Convert from 1-indexed to 0-indexed
        s = start_line - 1
        e = end_line - 1
        
        # Find the actual tikzpicture bounds
        tikz_start, tikz_end = find_tikzpicture_bounds(lines, s, e)
        
        if tikz_start < 0 or tikz_end < 0:
            print(f"  {filename}:{start_line}-{end_line}: tikzpicture não encontrada")
            continue
        
        # Add scale to tikzpicture begin
        old_line = lines[tikz_start]
        new_line = add_scale_to_tikzpicture(old_line, scale)
        
        if old_line != new_line:
            lines[tikz_start] = new_line
            print(f"  {filename}:{tikz_start+1}: scale={scale} adicionado")
            modified_count += 1
        else:
            print(f"  {filename}:{tikz_start+1}: já tem scale, ignorado")
    
    if modified_count > 0:
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))
        print(f"  → {filename}: {modified_count} figura(s) corrigida(s)")
    
    print()

print("Concluído!")
