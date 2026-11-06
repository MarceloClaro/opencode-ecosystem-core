#!/usr/bin/env python3
"""Regenera os 3 grafos do Molambudos a partir dos fragmentos reais."""

import os, re, subprocess
from pathlib import Path

BASE = Path(__file__).parent.parent
FRAG_DIR = BASE / 'fragmentos'
OUT_DIR = BASE / 'misc'

def extrair_rotas():
    """Extrai as rotas reais dos fragmentos."""
    rotas = {}
    ids = set()
    for f in sorted(FRAG_DIR.rglob('*.tex')):
        nome = f.stem
        ids.add(nome)
        content = f.read_text(encoding='utf-8')
        for line in content.split('\n'):
            if 'Rotas:' in line:
                destinos = re.findall(r'\\rota\{([^}]+)\}', line)
                if destinos:
                    rotas[nome] = destinos
                    break
    ids.add('Epilogo')
    return rotas, ids

def cluster_id(nome):
    """Define o cluster de cada fragmento."""
    if nome.startswith('MEM-') and int(nome.split('-')[1]) <= 7:
        return 0, 'Sertão'
    elif nome.startswith('MEM-') and int(nome.split('-')[1]) >= 8:
        return 1, 'Colônia'
    elif nome.startswith('DOC-') and int(nome.split('-')[1]) in list(range(1,8))+list(range(10,28)):
        return 2, 'Diário de Oliveira e Laudos'
    elif nome.startswith('DOC-') and int(nome.split('-')[1]) in [8,9,22,23,24,25]:
        return 3, 'Investigação Lúcia'
    elif nome.startswith('LUC-'):
        return 3, 'Investigação Lúcia'
    elif nome.startswith('CONT-'):
        return 4, 'Contaminação'
    elif nome == 'Epilogo':
        return 5, 'Epílogo'
    return -1, 'Outros'

def cor_tipo(nome):
    if nome.startswith('MEM-'): return '#8B4513'
    elif nome.startswith('DOC-'): return '#2F4F4F'
    elif nome.startswith('LUC-'): return '#4B0082'
    elif nome.startswith('CONT-'): return '#8B0000'
    elif nome == 'Epilogo': return '#DAA520'
    return '#666666'

def gerar_grafo_narrativo(rotas, ids):
    """Grafo 1: Mapa completo de rotas entre fragmentos — versão visual melhorada."""
    total_rotas = sum(len(v) for v in rotas.values())
    
    # Paleta de cores dos clusters (fundo suave para cada grupo)
    # (name, bg_light, fg_dark)
    cl_colors = {
        0: ('Sertão', '#F5F0E6', '#8B4513'),
        1: ('Colônia', '#EDE8DE', '#2F4F4F'),
        2: ('Diário de Oliveira e Laudos', '#E6ECE4', '#2F4F4F'),
        3: ('Investigação Lúcia', '#EAE4F0', '#4B0082'),
        4: ('Contaminação', '#F0E4E4', '#8B0000'),
        5: ('Epílogo', '#F5F0DC', '#B8962E'),
    }
    
    lines = []
    lines.append('digraph Molambudos {')
    lines.append('  rankdir=LR; bgcolor="#F5EED7"; pad=0.5; dpi=150;')
    lines.append('  nodesep=0.4; ranksep=1.5; splines=line;')
    lines.append('  fontname="Palatino"; labelloc=t; labeljust=l; fontsize=34; fontcolor="#2B2117";')
    lines.append(f'  label=<<b>MOLAMBUDOS — Mapa de Rotas</b><br/><font point-size="14" color="#5b4a2f">{len(ids)-1} fragmentos · {total_rotas} rotas · 5 partes</font>>;')
    lines.append('  node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=9,')
    lines.append('        fontcolor="white", color="white", penwidth=2, margin="0.08,0.04", height=0.28, width=1.1];')
    lines.append('  edge [color="#9c8a6a", penwidth=0.5, arrowsize=0.35, fontname="Helvetica", fontsize=7, fontcolor="#6b5a3f"];')
    
    # Agrupa nós por cluster
    clusters = {}
    for nome in sorted(rotas.keys()):
        cid, cname = cluster_id(nome)
        if cid not in clusters:
            clusters[cid] = {'name': cname, 'nodes': []}
        clusters[cid]['nodes'].append(nome)
    clusters[5] = {'name': 'Epílogo', 'nodes': ['Epilogo']}
    
    # Clusters com estilo visual melhorado
    for cid in sorted(clusters.keys()):
        if cid == 5:
            cname, bg, fg = cl_colors[5]
            lines.append(f'  subgraph cluster_epilogo {{')
            lines.append(f'    label="◆  {cname}"; fontsize=14; fontcolor="#7a6b30";')
            lines.append(f'    style="rounded"; color="#DAA520"; bgcolor="{bg}30"; fontname="Palatino-Italic";')
            lines.append(f'    "Epilogo" [fillcolor="#DAA520", fontcolor="#2B2117", penwidth=2, label="Epílogo\\nO ciclo recomeça"];')
            lines.append('  }')
            continue
        cname, bg, fg = cl_colors[cid]
        c = clusters[cid]
        # Ícone temático para cada cluster
        icones = {0: '✦', 1: '◆', 2: '▣', 3: '◈', 4: '⚠'}
        icon = icones.get(cid, '●')
        lines.append(f'  subgraph cluster_{cid} {{')
        lines.append(f'    label="{icon}  {cname}"; fontsize=14; fontcolor="{fg}";')
        lines.append(f'    style="rounded,dashed"; color="{fg}"; bgcolor="{bg}"; fontname="Palatino";')
        lines.append(f'    margin=16;')
        def sort_key_frag(x):
            prefix = x.split('-')[0]
            suffix = x.split('-')[1] if '-' in x else '0'
            try:
                num = int(suffix)
            except ValueError:
                # Non-numeric suffixes: assign high numbers to sort after numbered ones
                order = {'Contraprova': 90, 'Entrevista': 91, 'Escolha': 92}
                num = order.get(suffix, 99)
            return (num, prefix)
        for nome in sorted(c['nodes'], key=sort_key_frag):
            fill = cor_tipo(nome)
            lines.append(f'    "{nome}" [fillcolor="{fill}", penwidth=2];')
        lines.append('  }')
    
    # Legenda compacta e elegante
    lines.append('  subgraph cluster_legenda { label="Tipos de fragmento"; fontsize=12; fontcolor="#5b4a2f"; style="rounded"; color="#b7a381"; bgcolor="#FAF5E8"; fontname="Palatino"; margin=12;')
    lines.append('    "leg_MEM" [label="MEM  Memórias de Joaquim", fillcolor="#8B4513", width=2.2, penwidth=2];')
    lines.append('    "leg_DOC" [label="DOC  Documentos oficiais", fillcolor="#2F4F4F", width=2.2, penwidth=2];')
    lines.append('    "leg_LUC" [label="LUC  Investigação de Lúcia", fillcolor="#4B0082", width=2.2, penwidth=2];')
    lines.append('    "leg_CONT" [label="CONT  Contaminação do leitor", fillcolor="#8B0000", width=2.2, penwidth=2];')
    lines.append('    leg_MEM->leg_DOC->leg_LUC->leg_CONT [style=invis]; }')
    
    # Arestas
    for origem, destinos in sorted(rotas.items()):
        for d in destinos:
            if d in ids:
                lines.append(f'  "{origem}" -> "{d}";')
    
    lines.append('}')
    return '\n'.join(lines)


def gerar_grafo_enredo():
    """Grafo 2: Estrutura conceitual em 3 atos — formato retrato."""
    return '''digraph Enredo {
  rankdir=TB; bgcolor="#F5EED7"; pad=0.4; dpi=150; splines=curved; ratio=auto; size="8,10!";
  fontname="Palatino"; labelloc=t; fontsize=28; fontcolor="#2B2117";
  label=<<b>MOLAMBUDOS</b><br/><font point-size="14" color="#5b4a2f">Estrutura Narrativa — 3 Atos</font>>;
  node [shape="box", style="filled,rounded", fontname="Helvetica", fontsize=11, fontcolor="white", penwidth=2, margin="0.12,0.06", height=0.35, width=1.8];
  edge [penwidth=1.5, arrowsize=0.5, color="#5b4a2f"];

  /* ATO I — clusters com margem extra para evitar sobreposição */
  subgraph cluster_ato1 { label="ATO I — O Trauma"; fontsize=14; fontcolor="#8B4513"; style="rounded,dashed"; color="#8B4513"; fontname="Palatino-Bold"; bgcolor="#F5E6D0"; margin=22;
    node [fillcolor="#8B4513", height=0.48, width=2.0];
    "Seca 1853" [label="Seca de 1853\\nA entidade nasce"];
    "Seca 1915" [label="Seca de 1915\\nJoaquim encontra a entidade"];
    "Aceite" [label="O pacto na vala\\nMenino de 8 anos"];
  }

  /* ATO II */
  subgraph cluster_ato2 { label="ATO II — Institucionalização"; fontsize=14; fontcolor="#2F4F4F"; style="rounded,dashed"; color="#2F4F4F"; fontname="Palatino-Bold"; bgcolor="#E8E0D0"; margin=22;
    node [fillcolor="#2F4F4F", height=0.48, width=2.0];
    "Colonia" [label="62 anos no Colônia\\nO diário como testemunha"];
    "Exumacao" [label="Exumação (1979)\\nO diário é encontrado"];
    "Oliveira" [label="Dr. Heitor Oliveira\\nO médico que leu e foi lido"];
  }

  /* ATO III */
  subgraph cluster_ato3 { label="ATO III — O Ciclo"; fontsize=14; fontcolor="#8B0000"; style="rounded,dashed"; color="#8B0000"; fontname="Palatino-Bold"; bgcolor="#E8D0D0"; margin=22;
    node [fillcolor="#8B0000", height=0.48, width=2.0];
    "Lucia" [label="Dra. Lúcia Menezes\\nPaciente 1.262"];
    "Contaminacao" [label="Contaminação do leitor\\nPaciente 1.263"];
    "Ciclo" [label="O ciclo recomeça\\nA cada leitor"];
  }

  /* Arestas com label (não xlabel) + posicionamento explícito para não colidir com nós */
  "Seca 1853" -> "Seca 1915" [label="62 anos", fontsize=8, fontcolor="#5b4a2f", labeldistance=2.5, labelangle=-15];
  "Seca 1915" -> "Aceite" [label="fome como portal", fontsize=8, fontcolor="#5b4a2f", labeldistance=2.5, labelangle=-15];
  "Aceite" -> "Colonia" [label="institucionalização", fontsize=8, fontcolor="#5b4a2f", labeldistance=2.5, labelangle=-15];
  "Colonia" -> "Exumacao" [label="o diário emerge", fontsize=8, fontcolor="#5b4a2f", labeldistance=2.5, labelangle=-15];
  "Exumacao" -> "Oliveira" [label="leitura = contágio", fontsize=8, fontcolor="#5b4a2f", labeldistance=2.5, labelangle=-15];
  "Oliveira" -> "Lucia" [label="entrega 47 anos depois", fontsize=8, fontcolor="#5b4a2f", labeldistance=2.5, labelangle=-15];
  "Lucia" -> "Contaminacao" [label="o diário é lido de novo", fontsize=8, fontcolor="#5b4a2f", labeldistance=2.5, labelangle=-15];
  "Contaminacao" -> "Ciclo" [style=dashed, color="#8B0000", fontcolor="#8B0000", label="∞", fontsize=12, labeldistance=2.5];
  /* Aresta dourada — cor escura para legibilidade, label reposicionado para evitar colisão com nós */
  "Ciclo" -> "Seca 1853" [style=dotted, color="#B8962E", fontcolor="#8B6914", label="o ciclo recomeça", fontsize=8, constraint=false, labeldistance=6, labelangle=60];
}'''


def gerar_grafo_linear():
    """Grafo 3: Percurso linear — versão visual mais rica e equilibrada."""
    return '''digraph Linear {
  rankdir=LR; bgcolor="#F5EED7"; pad=0.4; dpi=150; splines=ortho; nodesep=0.8; ranksep=1.6;
  fontname="Palatino"; labelloc=t; fontsize=32; fontcolor="#2B2117";
  label=<<b>MOLAMBUDOS — Leitura Linear</b><br/><font point-size="14" color="#5b4a2f">{len(ids)-1} fragmentos em ordem cronológico-narrativa recomendada</font>>;
  node [shape="box", style="filled,rounded", fontname="Helvetica", fontsize=11, fontcolor="white",
        penwidth=2.5, margin="0.18,0.12", height=0.5];
  edge [penwidth=3, arrowsize=0.8, color="#5b4a2f", fontname="Palatino-Italic", fontsize=10, fontcolor="#5b4a2f"];
  
  /* --- SERTÃO (1914-1917) --- */
  subgraph cluster_sertao { label="✦  SERTÃO  1914–1917"; fontsize=15; fontcolor="#8B4513";
    style="rounded,dashed"; color="#8B4513"; bgcolor="#F5E6D0"; fontname="Palatino-Bold"; margin=18;
    node [fillcolor="#8B4513"];
    "Sertao" [label="SERTÃO\\n9 fragmentos\\nA infância de Joaquim", shape=box, height=0.6, width=2.4];
  }
  
  /* --- COLÔNIA (1917-1979) --- */
  subgraph cluster_colonia { label="◆  COLÔNIA  1917–1979"; fontsize=15; fontcolor="#2F4F4F";
    style="rounded,dashed"; color="#2F4F4F"; bgcolor="#E8E0D0"; fontname="Palatino-Bold"; margin=18;
    node [fillcolor="#2F4F4F"];
    "Colonia" [label="COLÔNIA\\n16 fragmentos\\n62 anos de internação", height=0.6, width=2.4];
  }
  
  /* --- DIÁRIO DE OLIVEIRA (1979) --- */
  subgraph cluster_diario { label="▣  DIÁRIO DE OLIVEIRA  1979"; fontsize=15; fontcolor="#2F4F4F";
    style="rounded,dashed"; color="#2F4F4F"; bgcolor="#D5E0D8"; fontname="Palatino-Bold"; margin=18;
    node [fillcolor="#2F4F4F"];
    "Diario" [label="DIÁRIO + LAUDOS\\n25 fragmentos\\nA exumação e seus ecos", height=0.6, width=2.4];
  }
  
  /* --- INVESTIGAÇÃO LÚCIA (2026) --- */
  subgraph cluster_lucia { label="◈  INVESTIGAÇÃO LÚCIA  2026"; fontsize=15; fontcolor="#4B0082";
    style="rounded,dashed"; color="#4B0082"; bgcolor="#DCD0E8"; fontname="Palatino-Bold"; margin=18;
    node [fillcolor="#4B0082"];
    "Lucia" [label="INVESTIGAÇÃO\\n20 fragmentos\\nPaciente 1.262", height=0.6, width=2.4];
  }
  
  /* --- CONTAMINAÇÃO (VOCÊ) --- */
  subgraph cluster_cont { label="⚠  CONTAMINAÇÃO  VOCÊ"; fontsize=15; fontcolor="#8B0000";
    style="rounded,dashed"; color="#8B0000"; bgcolor="#E8D0D0"; fontname="Palatino-Bold"; margin=18;
    node [fillcolor="#8B0000"];
    "Contaminacao" [label="CONTAMINAÇÃO\\n13 fragmentos\\nPaciente 1.263", height=0.6, width=2.4];
  }
  
  /* --- EPÍLOGO --- */
  subgraph cluster_epilogo { label="◇  EPÍLOGO"; fontsize=15; fontcolor="#7a6b30";
    style="rounded"; color="#DAA520"; bgcolor="#F0E8C8"; fontname="Palatino-Bold"; margin=18;
    node [fillcolor="#DAA520", fontcolor="#2B2117"];
    "Epilogo" [label="EPÍLOGO\\nO ciclo recomeça\\nSempre", height=0.6, width=2.4];
  }
  
  /* Arestas com label (não xlabel) + posicionamento explícito */
  "Sertao" -> "Colonia" [label="Joaquim é internado aos 11 anos", fontsize=9, fontcolor="#5b4a2f", labeldistance=2.5, labelangle=-15];
  "Colonia" -> "Diario" [label="exumação de 1979 revela o diário", fontsize=9, fontcolor="#5b4a2f", labeldistance=2.5, labelangle=-15];
  "Diario" -> "Lucia" [label="material entregue a Lúcia em 2026", fontsize=9, fontcolor="#5b4a2f", labeldistance=2.5, labelangle=-15];
  "Lucia" -> "Contaminacao" [label="a leitura contamina a investigadora", fontsize=9, fontcolor="#5b4a2f", labeldistance=2.5, labelangle=-15];
  "Contaminacao" -> "Epilogo" [label="você é o próximo paciente", fontsize=9, fontcolor="#8B0000", labeldistance=2.5, labelangle=-15];
  /* Aresta dourada — cor escura, label reposicionado para não sobrepor */
  "Epilogo" -> "Sertao" [style=dashed, color="#B8962E", fontcolor="#8B6914", label="o ciclo sempre recomeça", fontsize=9, labeldistance=5, labelangle=45];
}'''


def render_dot(dot_content, nome):
    """Renderiza DOT para PNG."""
    dot_path = OUT_DIR / f'{nome}.dot'
    png_path = OUT_DIR / f'{nome}.png'
    dot_path.write_text(dot_content, encoding='utf-8')
    result = subprocess.run(
        ['dot', '-Tpng', '-Gdpi=150', str(dot_path), '-o', str(png_path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ERRO: {result.stderr}")
    else:
        size_kb = os.path.getsize(png_path) / 1024
        print(f"  ✅ {nome}.png ({size_kb:.0f} KB)")


if __name__ == '__main__':
    print("=== REGENERAÇÃO DOS GRAFOS ===")
    rotas, ids = extrair_rotas()
    print(f"Fragmentos: {len(ids)} | Rotas: {sum(len(v) for v in rotas.values())}")

    print("\n1. Grafo Narrativo (rotas entre fragmentos)...")
    render_dot(gerar_grafo_narrativo(rotas, ids), 'grafo_narrativo')

    print("\n2. Grafo do Enredo (3 atos)...")
    render_dot(gerar_grafo_enredo(), 'grafo_enredo')

    print("\n3. Grafo de Leitura Linear...")
    render_dot(gerar_grafo_linear(), 'grafo_leitura_linear')

    print("\n✅ Todos os grafos regenerados.")
