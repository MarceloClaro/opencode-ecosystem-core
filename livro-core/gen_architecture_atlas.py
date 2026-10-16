"""R911: atlas vetorial curado, separado do grafo integral de imports estáticos."""
from __future__ import annotations

import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
KINDS = {'call', 'event', 'data', 'structure', 'boundary'}
KIND_NAMES = {'call': 'chamada', 'event': 'evento', 'data': 'dado',
              'structure': 'estrutura', 'boundary': 'fronteira'}


def tex(value: str) -> str:
    chars = {'&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
             '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
             '^': r'\textasciicircum{}', '\\': r'\textbackslash{}',
             '→': r'$\to$', '≤': r'$\leq$', '≥': r'$\geq$',
             '×': r'$\times$', '–': '--', '—': '---', 'Δ': r'$\Delta$'}
    return ''.join(chars.get(c, c) for c in str(value))


def symbols(source: str) -> set[str]:
    tree = ast.parse(source)
    result = set()
    def visit(node, prefix=''):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                result.add(name)
                visit(child, name + '.')
            else:
                visit(child, prefix)
    visit(tree)
    return result


def validate_atlas(items: list[dict], root: Path = ROOT) -> dict:
    if len(items) != 18 or {a['id'] for a in items} != {f'AR{i:02}' for i in range(1, 19)}:
        raise ValueError('Exigir exatamente AR01--AR18, sem duplicação')
    source_info = {}
    cache = {}
    def check(ref):
        relative, symbol = ref['path'], ref['symbol']
        path = (root/relative).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file() or path.suffix != '.py':
            raise ValueError('Fonte Python ausente ou fora do projeto: ' + relative)
        if relative not in cache:
            cache[relative] = symbols(path.read_text())
        if symbol not in cache[relative]:
            raise ValueError(f'Símbolo inexistente: {relative}:{symbol}')
        source_info[relative] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    for a in items:
        for field in ('title', 'question', 'mechanism', 'example', 'limits'):
            if not a.get(field, '').strip():
                raise ValueError(f"Campo ausente: {a['id']}:{field}")
        if not a['chapters'] or any(not (root/'livro-core'/f'{c}.tex').is_file() for c in a['chapters']):
            raise ValueError('Capítulo consumidor inexistente: ' + a['id'])
        if len(a['mental']) != 4 or any(len(b['items']) != 3 for b in a['mental']):
            raise ValueError('Mapa mental exige quatro ramos de três conceitos')
        if len(a['components']) != 6 or len({c['id'] for c in a['components']}) != 6:
            raise ValueError('Diagrama exige seis responsabilidades distintas')
        ids = {c['id'] for c in a['components']}
        for c in a['components']:
            check(c)
        if not a['edges'] or len(a['edges']) > 8:
            raise ValueError('Diagrama sem relação ou com densidade acima do contrato A4')
        for edge in a['edges']:
            if edge['source'] not in ids or edge['target'] not in ids or edge['kind'] not in KINDS:
                raise ValueError('Extremo ou tipo de relação inválido: ' + a['id'])
            check(edge['evidence'])
        flow = a['flow']
        if len(flow['steps']) != 6 or flow['decision_after'] not in (2, 3):
            raise ValueError('Fluxo exige seis passos e decisão intermediária')
        if any(not flow.get(k, '').strip() for k in ('question', 'no', 'recovery')):
            raise ValueError('Fluxo precisa mostrar condição, recusa e recuperação')
        for ref in [*a['sources'], *flow['evidence']]:
            check(ref)
    return {'architectures': len(items), 'views': 3*len(items), 'sources': source_info,
            'scope': 'Fontes e contratos dos diagramas; não prova execução nem equivalência semântica.'}


STYLES = r'''
\tikzset{
 atlasnode/.style={draw=steel,fill=blueBg,rounded corners=2mm,align=center,
  text width=4cm,inner sep=5pt,font=\fontsize{9.5}{11.8}\selectfont,text=textmain},
 atlasroot/.style={atlasnode,fill=navy,text=white,text width=2.8cm,font=\fontsize{10}{12}\selectfont\bfseries},
 atlasdecision/.style={diamond,aspect=2.1,draw=amber,fill=amberBg,align=center,
  text width=3cm,inner sep=2pt,font=\fontsize{9.5}{11.5}\selectfont},
 atlascall/.style={-Stealth,draw=steel,thick},
 atlasevent/.style={-Stealth,draw=violet,dashed,thick},
 atlasdata/.style={-Stealth,draw=teal,densely dotted,thick},
 atlasstructure/.style={draw=slate,thick},
 atlasboundary/.style={-Stealth,draw=amber,dash dot,thick},
 atlasedgelabel/.style={fill=papel,inner sep=1.3pt,font=\fontsize{9}{10}\selectfont}
}
'''


def mental(a: dict) -> str:
    lines = [STYLES, r'\begin{tikzpicture}',
             r'\node[atlasroot] (root) at (0,0) {'+a['id']+r'\\'+tex(a['title'])+'};']
    for i, (x, y) in enumerate(((-4.5, 2.5), (4.5, 2.5), (-4.5, -2.5), (4.5, -2.5))):
        b = a['mental'][i]
        label = r'\textbf{'+tex(b['label'])+r'}\\'+r'\\'.join(tex(x) for x in b['items'])
        lines += [f'\n\\node[atlasnode] (branch{i}) at ({x},{y}) '+'{'+label+'};',
                  f'\\draw[atlasstructure] (root) -- (branch{i});']
    return '\n'.join(lines+[r'\end{tikzpicture}'])


def structure(a: dict) -> str:
    lines = [STYLES, r'\begin{tikzpicture}']
    positions = [(-4.3, 0), (4.3, 0), (-4.3, -3.0), (4.3, -3.0), (-4.3, -6.0), (4.3, -6.0)]
    indices = {c['id']: i for i, c in enumerate(a['components'])}
    multiplicities = Counter(tuple(sorted((e['source'], e['target']))) for e in a['edges'])
    for i, c in enumerate(a['components']):
        x, y = positions[i]
        lines.append(f'\\node[atlasnode] (c{i}) at ({x},{y}) '+'{'+r'\textbf{C'+str(i+1)+': '+tex(c['label'])+r'}\\'+tex(c['role'])+'};')
    for k, e in enumerate(a['edges']):
        i, j = indices[e['source']], indices[e['target']]
        x, y = positions[i]; xx, yy = positions[j]
        style = 'atlas'+e['kind']; label = f'node[atlasedgelabel,pos=.25]{{E{k+1}}}'
        if multiplicities[tuple(sorted((e['source'], e['target'])))] > 1:
            # Sentidos opostos ganham curvas distintas; não ocultar evento sob chamada.
            lines.append(f'\\draw[{style}] (c{i}) to[bend left=14] {label} (c{j});')
        elif i % 2 != j % 2:
            side, other = ('east', 'west') if x < xx else ('west', 'east')
            outangle, inangle = (0, 180) if x < xx else (180, 0)
            lines.append(f'\\draw[{style}] (c{i}.{side}) to[out={outangle},in={inangle}] {label} (c{j}.{other});')
        elif abs(i-j) == 2:
            side, other = ('south', 'north') if yy < y else ('north', 'south')
            lines.append(f'\\draw[{style}] (c{i}.{side}) -- {label} (c{j}.{other});')
        else:
            side = 'west' if x < 0 else 'east'; outer = -7.0 if x < 0 else 7.0
            lines.append(f'\\draw[{style}] (c{i}.{side}) -- ({outer},{y}) -- {label} ({outer},{yy}) -- (c{j}.{side});')
    return '\n'.join(lines+[r'\end{tikzpicture}'])


def flow(a: dict) -> str:
    f = a['flow']; lines = [STYLES, r'\begin{tikzpicture}']; previous = None
    for i, step in enumerate(f['steps']):
        name = f's{i}'
        placement = f',below=6mm of {previous}' if previous else ''
        lines.append(f'\\node[atlasnode,text width=5cm{placement}] ({name}) '+'{'+tex(step)+'};')
        if previous:
            lines.append(f'\\draw[atlascall] ({previous}) -- '+(r'node[right,font=\small]{sim} ' if previous == 'decision' else '')+f'({name});')
        previous = name
        if i + 1 == f['decision_after']:
            lines.append(f'\\node[atlasdecision,below=6mm of {previous}] (decision) '+'{'+tex(f['question'])+'};')
            lines.append(f'\\draw[atlascall] ({previous}) -- (decision);')
            lines.append(r'\node[atlasnode,fill=amberBg,text width=3.1cm,right=12mm of decision] (refusal) {'+r'\textbf{Recusa ou pendência}\\'+tex(f['no'])+'};')
            lines.append(r'\draw[atlasboundary] (decision.east) -- node[above,font=\small]{não} (refusal.west);')
            previous = 'decision'
    # O ramo não é desenhado como repetição automática; recuperação é instrução ao leitor.
    return '\n'.join(lines+[r'\end{tikzpicture}'])


def page(a: dict, kind: str) -> str:
    names = {'mental': 'Mapa mental', 'structure': 'Diagrama de arquitetura', 'flow': 'Fluxograma'}
    body = {'mental': mental, 'structure': structure, 'flow': flow}[kind](a)
    if kind == 'mental':
        how = 'Parta do centro e leia os quatro ramos. As linhas associam conceitos; não representam chamadas de funções.'
        why, limit = a['mechanism'], 'O agrupamento é didático; cada responsabilidade será localizada no diagrama e conferida no fluxo.'
    elif kind == 'structure':
        how = f'Localize as seis responsabilidades C1--C6. Os identificadores E1--E{len(a["edges"])} permitem conferir o significado de cada conexão na chave das relações.'
        why, limit = 'Separar componentes e tipos de relação ajuda a localizar onde uma dependência, um evento ou uma fronteira foi declarado.', a['limits']
    else:
        how = 'Siga a coluna como uma sequência explicativa da operação delimitada. No losango, compare as condições antes de avançar.'
        why, limit = a['example'], a['limits']+' Recuperação: '+a['flow']['recovery']
    lines = ['% R911: gerado; alterar dados e gerador, não esta prancha.', r'\clearpage' if kind != 'mental' else '',
             r'\refstepcounter{figure}\label{fig:'+a['id']+'-'+kind+'}',
             r'\noindent{\large\sffamily\bfseries\color{navy}'+a['id']+' · '+names[kind]+r'}\par\smallskip',
             r'\noindent\textbf{'+tex(a['title'])+r'}\par',
             r'\noindent\textit{'+tex(a['question'])+r'}\par\medskip',
             r'\begin{center}', body, r'\end{center}',
             r'{\small\textbf{Figura \thefigure.} '+tex(names[kind]+' — '+a['title'])+r'}\par\smallskip']
    if kind == 'structure':
        idx = {c['id']: i+1 for i, c in enumerate(a['components'])}
        relations = [f'E{k+1}: C{idx[e["source"]]}' + ' para ' + f'C{idx[e["target"]]} — '+e['label']+' ('+KIND_NAMES[e['kind']]+')' for k, e in enumerate(a['edges'])]
        lines += [r'{\footnotesize\textbf{Chave das relações.} '+r'; '.join(tex(s) for s in relations)+r'.}\par\smallskip']
    lines += [r'\noindent\textbf{Como funciona e por quê.} '+tex(how)+r'\par',
              r'\noindent\textbf{Justificativa.} '+tex(why)+r'\par',
              r'\noindent\textbf{Limite.} '+tex(limit)+r'\par\smallskip']
    refs = a['sources'][:2] if kind != 'flow' else a['flow']['evidence'][:2]
    for ref in refs:
        lines.append(r'\fontecore{'+ref['path']+'}{'+ref['symbol']+'}')
    return '\n'.join(lines)+'\n'


def layer_matrix(snapshot: dict) -> tuple[str, dict]:
    modules = {m['module']: m for m in snapshot['modules']}
    layers = sorted({m['layer'] for m in modules.values()})
    index = {x: i for i, x in enumerate(layers)}
    pairs = Counter((modules[e['source']]['layer'], modules[e['target']]['layer']) for e in snapshot['edges'])
    lines = [r'\begin{tikzpicture}[x=.66cm,y=.56cm,font=\fontsize{9}{10}\selectfont]']
    for i, name in enumerate(layers):
        lines += [f'\\node[rotate=90,anchor=west] at ({i+.5},.2) '+'{'+f'L{i+1:02}'+'};',
                  f'\\node[anchor=east] at (-.12,{-i-.5}) '+'{'+f'L{i+1:02}'+'};']
        for j, target in enumerate(layers):
            count = pairs[(name, target)]
            fill = 'blueBg' if count else 'white'
            lines.append(f'\\filldraw[fill={fill},draw=lineDark] ({j},{-i}) rectangle ({j+1},{-i-1});')
            if count:
                lines.append(f'\\node at ({j+.5},{-i-.5}) '+'{'+str(count)+'};')
    lines.append(r'\end{tikzpicture}')
    ledger = {'layers': layers, 'module_count': len(modules), 'declarations': len(snapshot['edges']),
              'counts': [{'source': s, 'target': t, 'declarations': n} for (s, t), n in sorted(pairs.items())]}
    return '\n'.join(lines), ledger


def panorama(items: list[dict]) -> str:
    """Mapa mental de todos os temas, sem inventar chamadas entre agrupamentos."""
    groups = [
        ('Entrada e extensões', ['AR01', 'AR12', 'AR17']),
        ('Coordenação', ['AR02', 'AR03', 'AR04']),
        ('Critérios e contratos', ['AR05', 'AR08', 'AR09']),
        ('Conhecimento situado', ['AR06', 'AR07', 'AR14']),
        ('Investigação', ['AR10', 'AR11', 'AR13']),
        ('Sustentação e publicação', ['AR15', 'AR16', 'AR18']),
    ]
    titles = {a['id']: a['title'] for a in items}
    lines = [STYLES, r'\begin{tikzpicture}',
             r'\node[atlasroot] (core) at (0,0) {Core\\18 temas\\três vistas};']
    for i, (name, ids) in enumerate(groups):
        x = -4.8 if i % 2 == 0 else 4.8
        y = 4.8 - (i//2)*4.8
        content = r'\textbf{'+tex(name)+r'}\\'+r'\\[3pt]'.join(
            tex(key+': '+titles[key]) for key in ids)
        lines.append(f'\\node[atlasnode,text width=4.1cm] (g{i}) at ({x},{y}) '+'{'+content+'};')
        lines.append(f'\\draw[atlasstructure] (core) -- (g{i});')
    return '\n'.join(lines+[r'\end{tikzpicture}'])


def process_map() -> str:
    """Fronteiras de instância: contrato comum não equivale a estado distribuído."""
    return STYLES + r'''
\begin{tikzpicture}
\node[atlasnode] (cli) at (-5,0) {\textbf{Processo CLI}\\Primário criado para a invocação};
\node[atlasnode] (mcp) at (0,0) {\textbf{Servidor MCP}\\Primário em cache no servidor};
\node[atlasnode] (web) at (5,0) {\textbf{Processo Streamlit}\\Primário em cache na aplicação};
\node[atlasroot,text width=5cm] (contract) at (0,-2.4) {MarceloClaroOrchestrator\\Contrato compartilhado; instâncias próprias};
\draw[atlasstructure] (cli.south) -- (contract.north west);
\draw[atlasstructure] (mcp.south) -- (contract.north);
\draw[atlasstructure] (web.south) -- (contract.north east);
\node[atlasnode] (direct) at (-4.3,-5) {\textbf{Operação direta}\\Exemplo: rea\_action chama ReaBridge};
\node[atlasnode] (delegated) at (4.3,-5) {\textbf{Trabalho delegado}\\CFP, atribuição e executor elegível};
\draw[atlascall] (contract.south west) -- node[atlasedgelabel,left]{D1} (direct.north);
\draw[atlascall] (contract.south east) -- node[atlasedgelabel,right]{D2} (delegated.north);
\node[atlasnode] (local) at (-4.3,-7.4) {\textbf{Blackboard e MetaBus}\\Estado e coordenação dentro do processo};
\node[atlasnode] (storage) at (4.3,-7.4) {\textbf{Registros persistidos}\\Conforme o contrato de cada operação};
\draw[atlasstructure] (delegated.west) -- (local.east);
\draw[atlasdata] (direct.south) -- node[atlasedgelabel,pos=.25]{D3} (storage.west);
\end{tikzpicture}
'''


def global_flow() -> str:
    """Percurso de uso e conferência, explicitamente separado de pipeline universal."""
    return STYLES + r'''
\begin{tikzpicture}
\node[atlasnode,text width=5cm] (entry) at (0,0) {Escolher entrada e operação\\CLI, MCP ou painel};
\node[atlasnode,text width=5cm,below=6mm of entry] (scope) {Conferir escopo, permissões\\e configuração exigidos pela operação};
\draw[atlascall] (entry) -- (scope);
\node[atlasdecision,below=6mm of scope] (route) {O caminho escolhido exige delegação?};
\draw[atlascall] (scope) -- (route);
\node[atlasnode,below left=6mm and 0mm of route] (direct) {\textbf{Não: operação direta}\\Exemplo: análise REA local};
\node[atlasnode,below right=6mm and 0mm of route] (task) {\textbf{Sim: trabalho A2A}\\CFP e condições do executor};
\draw[atlascall] (route.west) -| (direct.north);
\draw[atlascall] (route.east) -| (task.north);
\node[fit=(direct)(task),inner sep=0pt] (branches) {};
\node[atlasnode,text width=5.3cm,below=6mm of branches] (receipt) {Conferir retorno, recibo ou pendência\\Instalação e atribuição não provam execução};
\draw[atlascall] (direct.south) -- (receipt.north west);
\draw[atlascall] (task.south) -- (receipt.north east);
\node[atlasnode,text width=5.3cm,below=6mm of receipt] (review) {Aplicar testes e critérios pertinentes\\Decisão científica e editorial humana};
\draw[atlascall] (receipt) -- (review);
\end{tikzpicture}
'''


def global_atlas(items: list[dict], snapshot: dict) -> tuple[str, dict]:
    matrix, ledger = layer_matrix(snapshot)
    commit = snapshot['git']['commit']
    counts = snapshot['counts']
    lines = [r'\clearpage\section{Mapa completo: do panorama às arquiteturas locais}',
             r'\label{sec:atlas-integral-r911}',
             'Este atlas oferece três leituras complementares: conceitos no mapa mental, responsabilidades no diagrama e decisões no fluxograma. As 18 arquiteturas didáticas não são as 18 camadas classificadas por pasta, nem os oito andares editoriais: cada organização responde a uma pergunta diferente.',
             'O grafo integral acompanha o livro em formatos SVG, DOT e Mermaid. Preserva todos os '+str(counts['python_production_modules'])+' módulos Python classificados no snapshot '+r'\pth{'+commit[:12]+'}, incluindo os isolados, e '+str(counts['unique_module_pairs'])+' pares de importação em '+str(counts['declared_import_edges'])+' declarações AST. Import não demonstra execução. Arquivos históricos, testes, vendor e artefatos de domínio permanecem classificados separadamente; o livro Lean não é contado como módulo Python de produção.',
             r'\begin{descricao}\textbf{Legenda comum.} Azul cheio: chamada curada; roxo tracejado: evento; verde pontilhado: dado; cinza sem ponta: organização; âmbar traço-ponto: fronteira ou recusa. Linhas de mapa mental são associações conceituais. Nas vistas estáticas, a direção é importador para dependência. As cores não indicam qualidade ou prontidão.\end{descricao}',
             r'\subsection*{Roteiro das 18 arquiteturas}',r'{\small\begin{longtable}{p{1cm}p{7.2cm}p{5.5cm}}',
             r'\toprule ID & Arquitetura & Figuras de consulta \\ \midrule\endhead']
    for a in items:
        refs = [r'\hyperref[fig:'+a['id']+'-'+k+']{'+t+'}' for k, t in [('mental','mental'),('structure','estrutura'),('flow','fluxo')]]
        lines.append(a['id']+' & '+tex(a['title'])+' & '+', '.join(refs)+r' \\')
    lines += [r'\bottomrule\end{longtable}}',
              r'\clearpage\refstepcounter{figure}\label{fig:global-mental}',
              r'\subsection*{Mapa mental completo dos 18 temas}',
              r'\begin{center}', panorama(items), r'\end{center}',
              r'\noindent\textbf{Figura \thefigure.} Panorama conceitual do Core.\par',
              r'\noindent\textbf{Como funciona e por quê.} Reconheça os seis agrupamentos e seus 18 identificadores. Cada identificador leva às três pranchas locais do roteiro anterior.\par',
              r'\noindent\textbf{Justificativa.} O agrupamento distingue finalidades antes de detalhar dependências e decisões, reduzindo a necessidade de memorizar nomes de arquivos durante a primeira leitura.\par',
              r'\noindent\textbf{Limite.} As linhas associam conceitos e não estabelecem uma topologia de execução. O agrupamento é uma escolha editorial explicitada, não uma classificação inferida pelo programa.\par',
              r'\clearpage\refstepcounter{figure}\label{fig:global-processes}',
              r'\subsection*{Diagrama geral: entradas, instâncias e caminhos}',
              r'\begin{center}', process_map(), r'\end{center}',
              r'\noindent\textbf{Figura \thefigure.} Fronteiras do primário e dois caminhos distintos.\par',
              r'\noindent\textbf{Como funciona e por quê.} Os três processos usam a classe do primário, mas não uma única instância distribuída. D1 representa a chamada direta de REA; D2, a abertura de tarefa A2A; D3, a observação persistida pela operação REA.\par',
              r'\noindent\textbf{Justificativa.} Diferenciar contrato, processo e persistência impede interpretar o desenho como um barramento distribuído já implementado.\par',
              r'\noindent\textbf{Limite.} As ligações cinzas indicam organização. O diagrama seleciona relações; o índice, as 54 pranchas e o grafo estático completam o detalhamento, cada qual dentro do seu escopo.\par',
              r'\fontecore{integrations/ecosystem_mcp.py}{get_library_orchestrator}',
              r'\fontecore{marceloclaro/orchestrator.py}{MarceloClaroOrchestrator.rea_action}',
              r'\clearpage\refstepcounter{figure}\label{fig:global-flow}',
              r'\subsection*{Fluxograma geral de uso e conferência}',
              r'\begin{center}', global_flow(), r'\end{center}',
              r'\noindent\textbf{Figura \thefigure.} Percurso didático para selecionar e conferir uma operação.\par',
              r'\noindent\textbf{Como funciona e por quê.} A pergunta central distingue operação direta de trabalho delegado. Em ambos os caminhos, o leitor precisa conferir o resultado efetivamente obtido, inclusive erro ou pendência.\par',
              r'\noindent\textbf{Justificativa.} O recibo permite confrontar a intenção com a execução; testes e avaliação humana têm funções próprias.\par',
              r'\noindent\textbf{Limite.} Este é um roteiro de uso, não um pipeline universal executado automaticamente. Os gates concretos, a autenticação e os critérios de conclusão dependem do caminho descrito nas pranchas locais.\par',
              r'\fontecore{marceloclaro/orchestrator.py}{MarceloClaroOrchestrator.delegate}',
              r'\clearpage\refstepcounter{figure}\label{fig:global-matrix}',
              r'\subsection*{Matriz completa das relações entre camadas estáticas}',
              r'\noindent Cada linha é uma camada importadora; cada coluna, uma dependência. O número na célula conta declarações AST, inclusive relações internas na diagonal. Uma célula vazia significa que esse extrator não registrou import correspondente; não demonstra ausência de comunicação dinâmica.\par\medskip',
              r'\begin{center}',matrix,r'\end{center}',
              r'{\footnotesize\noindent\begin{tabularx}{\linewidth}{YYYY}\toprule ID & Camada & ID & Camada \\ \midrule']
    layers = ledger['layers']; half = (len(layers)+1)//2
    for i in range(half):
        j = i+half
        lines.append(f'L{i+1:02} & '+tex(layers[i])+f' & L{j+1:02} & '+tex(layers[j])+r' \\')
    lines += [r'\bottomrule\end{tabularx}}',
              r'\noindent\textbf{Como funciona e por quê.} A matriz conserva todos os totais entre as camadas do inventário. O SVG integral conserva os identificadores individuais, inclusive módulos sem arestas; por isso a leitura por camadas e a leitura por módulo não são intercambiáveis.\par',
              r'\noindent\textbf{Justificativa.} Agregar somente para a orientação evita imprimir centenas de nomes em caracteres minúsculos. A exportação vetorial permite ampliar o mapa integral sem perder os rótulos.\par',
              r'\noindent\textbf{Limite.} Imports dinâmicos e superfícies não Python têm limites próprios de extração; a matriz não inventa ligações para completar visualmente o desenho.\par',
              r'\fontecore{scripts/build_architecture_maps.py}{build_snapshot}',
              r'\clearpage\subsection*{Mapa integral para ampliação e inventário pesquisável}',
              r'\noindent\href{https://github.com/MarceloClaro/opencode-ecosystem-core/blob/codex/core-prontidao-rea/docs/architecture-r911/dependencies.svg}{Abrir o mapa vetorial completo por módulo}. Os arquivos locais estão em \pth{docs/architecture-r911/}: \pth{dependencies.svg}, \pth{dependencies.dot}, \pth{dependencies.mmd}, \pth{architecture-inventory.json} e \pth{mermaid-correspondence.json}. O último arquivo conserva a correspondência de nós e pares entre formatos, sem contar a legenda como arquitetura.\par',
              'CLI, servidor MCP e Streamlit podem manter instâncias próprias do mesmo contrato de primário. O cache compartilhado em um servidor não estabelece uma instância distribuída universal. MetaBus e Blackboard também têm estado de processo; persistência de alguns registros não torna todo o estado global.',
              r'\noindent\textbf{Percurso de leitura.} Localize o tema no índice; abra o mapa mental para reconhecer a pergunta; use C1--C6 para identificar responsabilidades; siga o fluxograma da operação delimitada e seu ramo de recusa. Depois confronte a fonte e o recibo da operação realmente executada.\par',
              r'\noindent\textbf{Fronteiras.} Uma operação REA direta não precisa passar por CFP. Uma tarefa atribuída ainda pode estar em \pth{pending_executor}. O workflow atual pode ter dependências em DAG e execução sequencial. Um gate SDD exige as condições do seu caminho e da especificação associada; não se desenha um portão universal que o código não implementa.\par',
              r'\fontecore{integrations/ecosystem_mcp.py}{get_library_orchestrator}',
              r'\fontecore{marceloclaro/orchestrator.py}{MarceloClaroOrchestrator.agent_profile_action}']
    return '\n\n'.join(lines)+'\n', ledger


def replace_block(path: Path, block: str) -> None:
    begin, end = '% BEGIN-R911-ATLAS', '% END-R911-ATLAS'
    text = path.read_text()
    if begin in text:
        if end not in text:
            raise ValueError('Bloco incompleto em '+str(path))
        text = re.sub(re.escape(begin)+r'.*?'+re.escape(end), lambda _: begin+'\n'+block+'\n'+end, text, flags=re.S)
    else:
        marker = '% R901-PONTE-FECHO'
        addition = '\n'+begin+'\n'+block+'\n'+end+'\n\n'
        text = text.replace(marker, addition+marker, 1) if marker in text else text.rstrip()+addition
    path.write_text(text)


def main(root: Path = ROOT) -> dict:
    out = root/'livro-core/atlas'; out.mkdir(exist_ok=True)
    items = sorted([a for name in ('data-orchestration.json', 'data-science.json')
                    for a in json.loads((out/name).read_text())], key=lambda a: a['id'])
    report = validate_atlas(items, root)
    for a in items:
        a['views'] = {k: f"{a['id']}-{k}.tex" for k in ('mental', 'structure', 'flow')}
        for k, filename in a['views'].items():
            (out/filename).write_text(page(a, k))
    snapshot = json.loads((root/'docs/architecture-r911/architecture-inventory.json').read_text())
    global_text, layer_ledger = global_atlas(items, snapshot)
    (out/'global.tex').write_text(global_text)
    (out/'layer-relations.json').write_text(json.dumps(layer_ledger, ensure_ascii=False, indent=2)+'\n')
    by_chapter = {}
    for a in items:
        by_chapter.setdefault(a['chapters'][0], []).append(a)
    for path in sorted((root/'livro-core').glob('mod-*.tex')):
        owned = by_chapter.get(path.stem, [])
        references = [a for a in items if path.stem in a['chapters'][1:]]
        block = ''
        if path.stem == 'mod-01d-arquitetura':
            block += r'\input{atlas/global}'+'\n'
        for a in owned:
            block += r'\clearpage\section{'+tex(a['title'])+' — leitura em três vistas}'+r'\label{arch:'+a['id']+'}'+'\n'
            for filename in a['views'].values():
                block += r'\input{atlas/'+filename.removesuffix('.tex')+'}\n'
        if references:
            block += '\n'+r'\begin{descricao}\textbf{Navegação visual.} '
            block += '; '.join(tex(a['title'])+r': seção~\ref{arch:'+a['id']+'}' for a in references)
            block += r'. Cada seção contém mapa mental, diagrama estrutural e fluxograma com fontes e limites.\end{descricao}'+'\n'
        if block:
            replace_block(path, block)
    payload = {'revision': 'R911', 'source_git': snapshot['git'], 'architectures': items,
               'source_validation': report, 'static_layers_are_different_taxonomy': True}
    (out/'architectures.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
    return report


if __name__ == '__main__':
    print(json.dumps(main(), ensure_ascii=False))
