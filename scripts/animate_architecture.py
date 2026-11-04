#!/usr/bin/env python3
"""R1056: Mermaid local → SVG/PNG/GIF, galeria e manifesto verificável.

Não instala pacotes, não usa serviços de render e não altera fontes Mermaid.
Requer Pillow, Node, Mermaid/Puppeteer já instalados e Chromium local.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont, ImageSequence, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[1]
FOLDER = 'docs/architecture/animated'
MANIFEST = FOLDER + '/manifest.json'
GALLERY = 'docs/architecture/ANIMATED.md'
RENDERER = 'scripts/render_mermaid_animation.cjs'
FENCE = re.compile(r'^```mermaid[^\S\n]*\n(.*?)^```[^\S\n]*$', re.M | re.S)
W, H, FRAMES, STEP_MS = 1280, 800, 80, 100
OUT_W, OUT_H = 1080, 675
PULSE_FRAMES = 10
BG, INK, MUTED, ACCENT = '#0b1220', '#edf5ff', '#b4c8de', '#5eead4'
BG_RGB = (11, 18, 32)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inside(root: Path, relative: str) -> Path:
    root = root.resolve()
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts or '\\' in relative or ':' in relative:
        raise ValueError(f'Caminho não confinado: {relative}')
    resolved = (root / p).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f'Symlink fora da raiz: {relative}')
    return resolved


def validate_source(source: str) -> None:
    if len(source.encode()) > 100_000:
        raise ValueError('Diagrama muito grande; usar síntese declarada e preservar original')
    if re.search(r'%%\{|^\s*(?:click\s|---)|<\s*(?:script|iframe|img|image|foreignObject)\b|(?:https?://|javascript:\S|data:\S)', source, re.I | re.M):
        raise ValueError('Diretiva, callback, HTML ativo ou URL não permitida')
    if not re.match(r'\s*(?:%%[^\n]*\n\s*)*(?:flowchart|graph|sequenceDiagram|stateDiagram|classDiagram|block-beta)\b', source):
        raise ValueError('Tipo de diagrama não suportado neste exportador')


def document_paths(root: Path) -> list[str]:
    paths = subprocess.check_output(['git', 'ls-files', '*.md'], cwd=root, text=True).splitlines()
    return sorted(p for p in paths if ('/' not in p or p.startswith('docs/'))
                  and p != GALLERY and not p.startswith(FOLDER + '/'))


def write_layer_summary(inventory_path: Path, destination: Path | None = None) -> str:
    """Resumo por camadas em grade; não substitui nem afirma o grafo integral."""
    inventory = json.loads(inventory_path.read_text(encoding='utf-8'))
    counts: dict[str, int] = {}
    for module in inventory['modules']:
        counts[module['layer']] = counts.get(module['layer'], 0) + 1
    lines = ['%% Síntese por camadas do inventário histórico R916; não é o grafo integral.',
             'block-beta', '  columns 3']
    for index, (layer, number) in enumerate(sorted(counts.items())):
        label = re.sub(r'[^\w -]', '', layer).replace('_', ' ')
        lines.append(f'  L{index}["{label}<br/>{number} módulos"]')
    text = '\n'.join(lines) + '\n'
    if destination is not None:
        destination.write_text(text)
    return text


def camera_window(geometry: dict, edges: list[dict], *, aspect: float,
                  margin: int = 46, min_zoom: float = 1.5) -> dict:
    """Recorte determinístico que contém as arestas ativas e respeita o canvas."""
    points = [p for edge in edges for p in edge.get('points', [])]
    if not points:
        width = max(geometry['width'], geometry['height'] * aspect)
        height = width / aspect
        return {'left': (geometry['width'] - width) / 2,
                'top': (geometry['height'] - height) / 2,
                'width': width, 'height': height,
                'zoom': geometry['width'] / width}
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    x0, x1 = min(xs) - margin, max(xs) + margin
    y0, y1 = min(ys) - margin, max(ys) + margin
    width = max(min_zoom, x1 - x0, (y1 - y0) * aspect)
    height = width / aspect
    if height < y1 - y0:
        height, width = y1 - y0, (y1 - y0) * aspect
    width, height = min(width, geometry['width']), min(height, geometry['height'])
    width = max(width, min(min_zoom, geometry['width']))
    height = width / aspect
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    left = min(max(0, cx - width / 2), max(0, geometry['width'] - width))
    top = min(max(0, cy - height / 2), max(0, geometry['height'] - height))
    return {'left': left, 'top': top, 'width': width, 'height': height,
            'zoom': geometry['width'] / width}


def camera_center(geometry: dict, center: tuple[float, float], *, aspect: float,
                  zoom: float = 2.8) -> dict:
    """Enquadra um nó de destino preservando o canvas e um zoom legível."""
    width = min(geometry['width'], geometry['width'] / max(1.0, zoom))
    height = width / aspect
    if height > geometry['height']:
        height, width = geometry['height'], geometry['height'] * aspect
    left = min(max(0, center[0] - width / 2), max(0, geometry['width'] - width))
    top = min(max(0, center[1] - height / 2), max(0, geometry['height'] - height))
    return {'left': left, 'top': top, 'width': width, 'height': height,
            'zoom': geometry['width'] / width}


def _interpolate(a: dict, b: dict, t: float) -> dict:
    t = t * t * (3 - 2 * t)
    return {k: a[k] + (b[k] - a[k]) * t for k in ('left', 'top', 'width', 'height')}


def node_sequence(geometry: dict) -> list[str]:
    """Ordem de leitura estável para diagramas sem arestas."""
    seen, labels = set(), []
    for node in geometry.get('nodes', []):
        label = node.get('label', '')
        if label and label not in seen:
            seen.add(label)
            labels.append(label)
    return sorted(labels, key=lambda label: (
        next(n.get('y', 0) for n in geometry['nodes'] if n.get('label') == label),
        next(n.get('x', 0) for n in geometry['nodes'] if n.get('label') == label),
        label))


def process_order(geometry: dict) -> list[dict]:
    """Arestas em ordem topológica; ciclos são quebrados por posição.

    O resultado é uma ordem de leitura declarada, não uma execução observada.
    """
    import heapq

    nodes = {}
    for node in geometry.get('nodes', []):
        label = node.get('label', '')
        if label and label not in nodes:
            nodes[label] = (float(node.get('y', 0)), float(node.get('x', 0)), label)
    incoming = {label: set() for label in nodes}
    outgoing = {label: set() for label in nodes}
    edges = [edge for edge in geometry.get('edges', []) if len(edge.get('points', [])) > 1]
    for index, edge in enumerate(edges):
        edge['_index'] = index
        source, target = edge.get('from_label', ''), edge.get('to_label', '')
        if source in nodes and target in nodes:
            incoming[target].add(edge['id'])
            outgoing[source].add(edge['id'])
    available = [(nodes[label][0], nodes[label][1], label) for label in nodes if not incoming[label]]
    heapq.heapify(available)
    order, placed = [], set()
    while len(order) < len(nodes):
        while available and available[0][2] in placed:
            heapq.heappop(available)
        if not available:
            # Ciclo: escolhe o nó restante de menor posição e continua.
            remaining = [(nodes[label][0], nodes[label][1], label) for label in nodes if label not in placed]
            heapq.heapify(remaining)
            _, _, label = heapq.heappop(remaining)
        else:
            _, _, label = heapq.heappop(available)
        if label in placed:
            continue
        placed.add(label)
        order.append(label)
        for edge_id in list(outgoing[label]):
            edge = next(item for item in edges if item['id'] == edge_id)
            target = edge.get('to_label', '')
            incoming[target].discard(edge_id)
            if target not in placed and not incoming[target]:
                heapq.heappush(available, (nodes[target][0], nodes[target][1], target))
    position = {label: index for index, label in enumerate(order)}
    unknown = len(order) + 1
    return sorted(edges, key=lambda edge: (
        max(position.get(edge.get('from_label'), unknown), position.get(edge.get('to_label'), unknown)),
        position.get(edge.get('from_label'), unknown),
        position.get(edge.get('to_label'), unknown),
        edge.get('_index', 0)))


def discover(root: Path, paths: list[str] | None = None, *, catalog: bool = True) -> list[dict]:
    """Identidade pelo código integral; títulos não alteram deduplicação."""
    found: dict[str, dict] = {}

    def add(source, title, origin):
        validate_source(source)
        sha = digest(source.encode())
        item = found.setdefault(sha, {'id': 'diagram-' + sha[:16], 'title': title,
                                     'source': source, 'source_sha256': sha, 'origins': []})
        item['origins'].append(origin)

    for name in paths if paths is not None else document_paths(root):
        text = inside(root, name).read_text(encoding='utf-8')
        for i, match in enumerate(FENCE.finditer(text), 1):
            headings = re.findall(r'^#{1,6}\s+(.+)$', text[:match.start()], re.M)
            title = re.sub(r'^\d+[.)]\s*', '', headings[-1]) if headings else name
            add(match[1], title, {'path': name, 'block': i})
    if catalog:
        cat = json.loads(inside(root, 'docs/architecture/flows.json').read_text())
        for entry in cat['flows']:
            path = 'docs/architecture/' + entry['file']
            add(inside(root, path).read_text(), entry['title'], {'path': path, 'flow_id': entry['id']})
        # O inventário antigo não é reescrito nem apresentado como execução atual.
        path = 'docs/architecture/architecture-inventory.json'
        inventory_path = inside(root, path)
        summary = write_layer_summary(inventory_path)
        add(summary, 'Inventário integral — síntese por camadas',
            {'path': path, 'kind': 'layer_summary', 'sha256': digest(inventory_path.read_bytes()),
             'full_source': 'docs/architecture/dependencies.mmd'})
    return list(found.values())


def inspect_gif(path: Path) -> dict:
    if path.stat().st_size > 3_000_000:
        raise ValueError(f'GIF acima de 3 MB: {path}')
    with Image.open(path) as im:
        if im.format != 'GIF' or im.n_frames < 2:
            raise ValueError(f'GIF não animado: {path}')
        if max(im.size) > 1920 or min(im.size) < 16:
            raise ValueError('Dimensões GIF fora do contrato')
        meta = {'width': im.width, 'height': im.height, 'frames': im.n_frames,
                'infinite_loop': im.info.get('loop') == 0, 'duration_ms': 0}
        for frame in ImageSequence.Iterator(im):
            frame.load()
            duration = frame.info.get('duration', 0)
            if duration < 20:
                raise ValueError('Quadro rápido demais ou duração ausente')
            meta['duration_ms'] += duration
        if meta['infinite_loop']:
            raise ValueError('Loop infinito não permitido')
    return meta


def _font(size, bold=False):
    return ImageFont.truetype(FONT.replace('.ttf', '-Bold.ttf') if bold else FONT, size)


def _wrap(draw, value, width, font, *, lines=3):
    rows, line = [], ''
    for word in value.split():
        candidate = (line + ' ' + word).strip()
        if draw.textlength(candidate, font=font) > width and line:
            rows.append(line)
            line = word
        else:
            line = candidate
    rows.append(line)
    if len(rows) > lines:
        rows = rows[:lines]
        rows[-1] = rows[-1].rstrip(' .') + '…'
    return '\n'.join(rows)


PANEL_LEFT, PANEL_TOP, PANEL_W, PANEL_H = 44, 124, 1192, 502


def _crop_view(image: Image.Image, geometry: dict, window: dict) -> Image.Image:
    """Recorta uma janela geométrica, preenchendo fora do raster com fundo."""
    scale = image.width / geometry['width']
    box_w = max(1, round(window['width'] * scale))
    box_h = max(1, round(window['height'] * scale))
    canvas = Image.new('RGB', (box_w, box_h), BG)
    x, y = round(-window['left'] * scale), round(-window['top'] * scale)
    canvas.paste(image, (x, y))
    if (box_w, box_h) != (PANEL_W, PANEL_H):
        canvas = canvas.resize((PANEL_W, PANEL_H), Image.Resampling.LANCZOS)
    return canvas


def _project(point, window: dict) -> tuple[float, float]:
    x = (point[0] - window['left']) / window['width'] * PANEL_W + PANEL_LEFT
    y = (point[1] - window['top']) / window['height'] * PANEL_H + PANEL_TOP
    return (x, y)


def _point_at(points: list, phase: float) -> tuple[float, float]:
    phase = min(1.0, max(0.0, phase))
    position = phase * (len(points) - 1)
    index = min(len(points) - 1, int(position))
    if index >= len(points) - 1:
        return tuple(points[-1])
    fraction = position - index
    a, b = points[index], points[index + 1]
    return (a[0] + (b[0] - a[0]) * fraction,
            a[1] + (b[1] - a[1]) * fraction)


def _pulse_overlay(geometry: dict, window: dict, order: list[dict], frame: int,
                   stagger: float) -> tuple[Image.Image, dict | None]:
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    active = None
    for index, edge in enumerate(order):
        start = index * stagger
        phase = (frame - start) / PULSE_FRAMES
        if not 0 <= phase <= 1:
            continue
        active = edge
        points = [_project(point, window) for point in edge['points']]
        head = _point_at(points, phase)
        trail_phase = [max(0.0, phase - step) for step in (0.0, 0.03, 0.06)]
        trail_points = [_point_at(points, value) for value in trail_phase]
        for back in range(len(trail_points) - 1):
            alpha = int(70 * (1 - back / len(trail_points)))
            draw.line([trail_points[back], trail_points[back + 1]],
                      fill=(94, 234, 212, alpha), width=max(2, 3 - back))
        radius = 6
        draw.ellipse((head[0] - radius, head[1] - radius, head[0] + radius, head[1] + radius),
                     fill=(94, 234, 212, 30))
        draw.ellipse((head[0] - 3.5, head[1] - 3.5, head[0] + 3.5, head[1] + 3.5),
                     fill=(94, 234, 212, 235), outline=(237, 245, 255, 255))
    return overlay, active


def _node_overlay(geometry: dict, window: dict, sequence: list[str], frame: int) -> tuple[Image.Image, str | None]:
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    if not sequence:
        return overlay, None
    slot = min(len(sequence) - 1, int(frame / FRAMES * len(sequence)))
    label = sequence[slot]
    node = next((item for item in geometry.get('nodes', []) if item.get('label') == label), None)
    if node is None:
        return overlay, None
    phase = (frame / FRAMES * len(sequence)) % 1
    strength = 1 - abs(phase - 0.5) * 2
    half_w = min(260.0, max(90.0, geometry['width'] / 3.2)) / 2
    half_h = min(90.0, max(36.0, geometry['height'] / 12)) / 2
    left, top = _project((node['x'] - half_w, node['y'] - half_h), window)
    right, bottom = _project((node['x'] + half_w, node['y'] + half_h), window)
    draw.rounded_rectangle((left, top, right, bottom), radius=14,
                           fill=(94, 234, 212, int(20 + 35 * strength)),
                           outline=(94, 234, 212, int(150 + 80 * strength)), width=3)
    return overlay, label


def animate(item: dict, folder: Path) -> dict:
    """Pulso percorre todas as arestas na ordem topológica; não inventa execução."""
    stem = folder / item['id']
    geom = json.loads(stem.with_suffix('.geometry.json').read_text())
    with Image.open(stem.with_suffix('.render.png')) as im:
        image = im.convert('RGB')
    edges = [e for e in geom.get('edges', []) if len(e['points']) > 1]
    order = process_order(geom)
    sequence = node_sequence(geom)
    count = len(order)
    stagger = (FRAMES - PULSE_FRAMES) / max(1, count - 1) if count else 0
    overview = camera_window(geom, [], aspect=PANEL_W / PANEL_H)
    peak = 1.0

    def camera(frame: int) -> dict:
        t = frame / (FRAMES - 1)
        zoom = 1 + (peak - 1) * math.sin(math.pi * t)
        width, height = overview['width'] / zoom, overview['height'] / zoom
        return {'left': overview['left'] + (overview['width'] - width) / 2,
                'top': overview['top'] + (overview['height'] - height) / 2,
                'width': width, 'height': height, 'zoom': zoom}

    frames = []
    for frame in range(FRAMES):
        window = camera(frame)
        out = Image.new('RGB', (W, H), BG)
        out.paste(_crop_view(image, geom, window), (PANEL_LEFT, PANEL_TOP))
        d = ImageDraw.Draw(out)
        d.text((44, 24), 'OPENCODE CORE   /   ATLAS ANIMADO', font=_font(15, True), fill=ACCENT)
        title = _wrap(d, item['title'], 1192, _font(27, True), lines=2)
        d.multiline_text((44, 53), title, font=_font(27, True), fill=INK, spacing=2)
        active = None
        if count:
            overlay, active = _pulse_overlay(geom, window, order, frame, stagger)
            out = Image.alpha_composite(out.convert('RGBA'), overlay).convert('RGB')
        else:
            overlay, active = _node_overlay(geom, window, sequence, frame)
            out = Image.alpha_composite(out.convert('RGBA'), overlay).convert('RGB')
        d = ImageDraw.Draw(out)
        d.line((44, 640, 1236, 640), fill='#29405b', width=1)
        if count:
            index = min(count - 1, max(0, int(frame / max(stagger, 1e-6))))
            current = order[index]
            caption = current.get('label', '').strip()
            pair = (current.get('from_label', '') + '  →  ' + current.get('to_label', '')).strip(' →')
            d.text((44, 660), f'PULSO NA ORDEM DO PROCESSO  {index + 1}/{count}',
                   font=_font(14, True), fill=ACCENT)
            text = pair + ('  [' + caption + ']' if caption else '')
        elif sequence:
            slot = min(len(sequence) - 1, int(frame / FRAMES * len(sequence)))
            d.text((44, 660), f'NÓS EM SEQUÊNCIA  {slot + 1}/{len(sequence)}',
                   font=_font(14, True), fill=ACCENT)
            text = f'{sequence[slot]} · destaque de leitura; não é execução.'
        else:
            d.text((44, 660), 'VISÃO COMPLETA  ·  fonte preservada', font=_font(14, True), fill=ACCENT)
            text = f"{len(geom.get('nodes', []))} nós visuais · GIF de 8 s, um ciclo. Abra o SVG para ampliar."
        d.multiline_text((44, 690), _wrap(d, text, 1192, _font(19), lines=2), font=_font(19), fill=INK, spacing=4)
        d.rectangle((44, 741, 44 + (W - 88) * frame / (FRAMES - 1), 744), fill=ACCENT)
        d.text((44, 757), 'Guia de leitura · não representa execução real · fonte e SVG completos na galeria',
               font=_font(16), fill=MUTED)
        frames.append(out)
    frames = [f.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS) for f in frames]
    # Paleta global elimina cintilação cromática entre frames.
    palette = frames[36].quantize(colors=128)
    paletted = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    path = stem.with_suffix('.gif')
    paletted[0].save(path, save_all=True, append_images=paletted[1:], duration=STEP_MS,
                     optimize=True, disposal=1)  # loop OMITIDO: um ciclo apenas
    frames[0].save(stem.with_suffix('.png'))
    stats = inspect_gif(path)
    if stats['duration_ms'] != FRAMES * STEP_MS:
        raise ValueError('Duração codificada diverge do plano')
    stats['pulse_edges'] = count
    stats['pulse_span_frames'] = round(PULSE_FRAMES + max(0, count - 1) * stagger, 2)
    return stats


def _artifact(root, path):
    return {'path': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size,
            'sha256': digest(path.read_bytes())}


def gallery(items: list[dict]) -> str:
    lines = ['# Atlas animado de arquitetura e fluxos — R1056–R1057', '',
             'Todos os diagramas do escopo têm GIF, PNG, SVG e Mermaid editável.',
             'A animação percorre as arestas na ordem topológica do desenho e destaca',
             'os nós sem arestas em sequência. É **guia de leitura**, não telemetria,',
             'execução observada ou garantia de que o caminho ocorra.', '',
             '**Acessibilidade:** a visualização padrão é estática. Abra o GIF apenas',
             'quando desejar movimento; ele executa um ciclo de 8 s, sem repetição',
             'infinita. Para repetir, recarregue o arquivo. Amplie o SVG para ler grafos densos.', '',
             '[README](../../README.md) · [Arquitetura](../../ARCHITECTURE.md) ·',
             '[Manifesto e hashes](animated/manifest.json) · [Reprodução](../../reports/r1057/README.md)', '',
             '## Cobertura', '',
             '| Vista | Animação | Sem movimento | Fonte |', '|---|---|---|---|']
    for i, item in enumerate(items, 1):
        name = item['id']
        title = html.escape(item['title'].replace('|', ' / '), quote=False)
        lines.append(f'| {i:02d}. {title} | [GIF](animated/{name}.gif) | [PNG](animated/{name}.png) · [SVG](animated/{name}.svg) | [Mermaid](animated/{name}.mmd) |')
    lines += ['', '## Prévias estáticas e origens', '']
    for item in items:
        name = item['id']
        title = html.escape(item['title'], quote=False)
        lines += [f"### {title}", '',
                  f'<a href="animated/{name}.gif"><img src="animated/{name}.png" alt="{html.escape(item["title"], quote=True)} — prévia estática; abrir GIF é opcional" width="100%" loading="lazy"></a>', '',
                  f'[Abrir animação](animated/{name}.gif) · [SVG ampliável](animated/{name}.svg) · [Mermaid](animated/{name}.mmd)', '',
                  'Origens: ' + '; '.join(f'[{html.escape(o["path"])}](../../{o["path"]})' + (f' (bloco {o["block"]})' if 'block' in o else '') for o in item['origins']) + '.', '']
    lines += ['## Limites de cobertura', '',
              'Escopo: Markdown rastreado na raiz e em `docs/`, mais os 22 fluxos',
              'do catálogo. Fontes duplicadas compartilham bytes e mídia. Históricos',
              'continuam históricos: animação não atualiza a auditoria R916 nem R808.',
              'O grafo integral recebe uma **síntese por camadas**, sem suas arestas;',
              '[711 módulos e relações originais](dependencies.svg) permanecem disponíveis.',
              'Specs, relatórios, fornecedores e livros não são reescritos por esta rodada.', '']
    return '\n'.join(lines)


def verify(root: Path) -> dict:
    root = root.resolve()
    manifest = json.loads(inside(root, MANIFEST).read_text())
    expected = discover(root)
    observed = manifest['diagrams']
    if [(i['source_sha256'], i['origins'], i['title']) for i in expected] != [(i['source_sha256'], i['origins'], i['title']) for i in observed]:
        raise ValueError('Cobertura ou fonte Mermaid divergente; regenere o atlas')
    for key in ('generator', 'renderer'):
        art = manifest[key]
        if digest(inside(root, art['path']).read_bytes()) != art['sha256']:
            raise ValueError(f'{key} alterado após geração')
    total = 0
    for item in observed:
        for kind, art in item['artifacts'].items():
            p = inside(root, art['path'])
            if p.stat().st_size != art['bytes'] or digest(p.read_bytes()) != art['sha256']:
                raise ValueError(f'Artefato divergente: {p}')
            if kind == 'gif':
                if inspect_gif(p) != item['gif']:
                    raise ValueError('Metadados GIF divergentes')
                total += p.stat().st_size
        if digest(inside(root, item['artifacts']['mmd']['path']).read_bytes()) != item['source_sha256']:
            raise ValueError('Fonte exportada divergente')
    if total > 60_000_000:
        raise ValueError('Orçamento agregado excedido')
    if inside(root, GALLERY).read_text() != gallery(observed):
        raise ValueError('Galeria divergente')
    return {'status': 'pass', 'diagrams': len(observed),
            'catalog_flows': sum('flow_id' in o for i in observed for o in i['origins']),
            'markdown_blocks': sum('block' in o for i in observed for o in i['origins']),
            'total_gif_bytes': total, 'external_validation': False}


def _row(root: Path, item: dict, folder: Path) -> dict:
    """Metadados de um diagrama a partir das mídias já existentes."""
    stats = inspect_gif(folder / (item['id'] + '.gif'))
    row = {k: v for k, v in item.items() if k != 'source'}
    row['gif'] = stats
    row['camera'] = {'zoom_min': item.get('zoom_min', 1.0),
                     'zoom_max': item.get('zoom_max', 1.0)}
    row['pulse'] = {'edges': item.get('pulse_edges'),
                    'span_frames': item.get('pulse_span_frames')}
    row['artifacts'] = {ext: _artifact(root, folder / (item['id'] + '.' + ext))
                        for ext in ['mmd', 'svg', 'png', 'gif']}
    return row


def _prune(folder: Path, items: list[dict]) -> None:
    """Remove somente derivados gerados que não pertencem à cobertura atual."""
    keep = {item['id'] for item in items}
    for path in folder.iterdir():
        if path.is_file() and path.name.startswith('diagram-'):
            stem = path.name.split('.', 1)[0]
            if stem not in keep:
                path.unlink()


def _write_manifest(root: Path, items: list[dict], output: list[dict]) -> dict:
    manifest = {'version': 2, 'spec': 'SPEC-935-R1057',
                'animation': 'process_pulse_reading_guide_not_execution',
                'generator': _artifact(root, root / 'scripts/animate_architecture.py'),
                'renderer': _artifact(root, root / RENDERER),
                'pillow_version': pillow_version,
                'font': {'name': 'DejaVuSans', 'sha256': digest(Path(FONT).read_bytes())},
                'diagrams': output}
    inside(root, GALLERY).write_text(gallery(output))
    inside(root, MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return verify(root)


def build(root: Path, *, only: str | None = None):
    root = root.resolve()
    items = discover(root)
    folder = inside(root, FOLDER)
    folder.mkdir(parents=True, exist_ok=True)
    selected = [i for i in items if only is None or i['id'] == only]
    if not selected:
        raise ValueError('ID de diagrama desconhecido')
    for item in selected:
        inside(root, FOLDER + '/' + item['id'] + '.mmd').write_text(item['source'])
    # Arquivo de requisição temporário; caminhos são todos confinados e gerados.
    with tempfile.TemporaryDirectory(prefix='atlas-', dir='/tmp/opencode') as tmp:
        request = Path(tmp) / 'request.json'
        request.write_text(json.dumps({'output': str(folder), 'diagrams': selected}))
        subprocess.run(['node', str(inside(root, RENDERER)), str(request)], check=True, timeout=600)
    output = []
    for item in selected:
        stats = animate(item, folder)
        item['zoom_min'], item['zoom_max'] = stats.get('zoom_min', 1.0), stats.get('zoom_max', 1.0)
        item['pulse_edges'], item['pulse_span_frames'] = stats.get('pulse_edges'), stats.get('pulse_span_frames')
        row = _row(root, item, folder)
        output.append(row)
        print(json.dumps({'rendered': item['id'], 'bytes': row['artifacts']['gif']['bytes']}), flush=True)
    if only:
        print('Prévia apenas: manifesto completo não foi atualizado.')
        return
    _prune(folder, items)
    print(json.dumps(_write_manifest(root, items, output), ensure_ascii=False))


def manifest_only(root: Path):
    """Atualiza galeria/manifesto a partir de mídias existentes, sem render."""
    root = root.resolve()
    items = discover(root)
    folder = inside(root, FOLDER)
    old_camera = {}
    manifest_path = inside(root, MANIFEST)
    if manifest_path.is_file():
        for row in json.loads(manifest_path.read_text(encoding='utf-8')).get('diagrams', []):
            old_camera[row.get('id')] = row.get('camera') or {
                'zoom_min': row.get('gif', {}).get('zoom_min', 1.0),
                'zoom_max': row.get('gif', {}).get('zoom_max', 1.0)}
    for item in items:
        item.update(old_camera.get(item['id'], {}))
        geometry_path = folder / (item['id'] + '.geometry.json')
        if geometry_path.is_file():
            geom = json.loads(geometry_path.read_text(encoding='utf-8'))
            count = len(process_order(geom))
            item['pulse_edges'] = count
            item['pulse_span_frames'] = round(
                PULSE_FRAMES + max(0, count - 1) * ((FRAMES - PULSE_FRAMES) / max(1, count - 1)), 2
            ) if count else 0
    _prune(folder, items)
    output = [_row(root, item, folder) for item in items]
    print(json.dumps(_write_manifest(root, items, output), ensure_ascii=False))


def reanimate(root: Path):
    """Recompõe GIF/PNG a partir de SVG/geometria existentes, sem navegador."""
    root = root.resolve()
    items = discover(root)
    folder = inside(root, FOLDER)
    output = []
    for item in items:
        stats = animate(item, folder)
        item['zoom_min'], item['zoom_max'] = stats.get('zoom_min', 1.0), stats.get('zoom_max', 1.0)
        item['pulse_edges'], item['pulse_span_frames'] = stats.get('pulse_edges'), stats.get('pulse_span_frames')
        output.append(_row(root, item, folder))
        print(json.dumps({'reanimated': item['id'], 'bytes': output[-1]['artifacts']['gif']['bytes']}), flush=True)
    _prune(folder, items)
    print(json.dumps(_write_manifest(root, items, output), ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--check', action='store_true')
    p.add_argument('--inventory', action='store_true')
    p.add_argument('--manifest', action='store_true', help='Atualiza manifesto/galeria sem renderizar')
    p.add_argument('--reanimate', action='store_true', help='Recompõe GIF/PNG sem reabrir o navegador')
    p.add_argument('--only', help='Render de prévia sem publicar manifesto')
    args = p.parse_args()
    try:
        if args.check:
            print(json.dumps(verify(args.root), ensure_ascii=False))
        elif args.inventory:
            print(json.dumps(discover(args.root), ensure_ascii=False, indent=2))
        elif args.manifest:
            manifest_only(args.root)
        elif args.reanimate:
            reanimate(args.root)
        else:
            build(args.root, only=args.only)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f'Atlas bloqueado: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
