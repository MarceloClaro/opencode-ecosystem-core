"""R829: projeção somente de leitura da memória; CLI sem dependência de UI."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class NodeType(str, Enum):
    QUERY = 'consulta'
    MEMORY = 'memoria'
    CONTEXT = 'contexto'
    AGENT = 'agente'
    EVIDENCE = 'evidencia'
    RESPONSE = 'resposta'


class EdgeType(str, Enum):
    RETRIEVAL = 'recuperacao'
    EXECUTION = 'execucao'
    REFERENCE = 'referencia'
    REASONING = 'raciocinio'


def safe_text(value: Any, limit: int = 240) -> str:
    text = str(value if value is not None else '').encode('utf-8', errors='replace').decode('utf-8')
    return ''.join(' ' if c in '\n\r\t' else c for c in text
                   if c in '\n\r\t' or unicodedata.category(c) not in {'Cc', 'Cf'})[:limit]


def finite(value: Any, *, unit: bool = False) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError):
        return None
    return number if math.isfinite(number) and (not unit or 0 <= number <= 1) else None


def timestamp(value: Any) -> float | None:
    number = finite(value)
    if number is not None:
        return number
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return parsed.timestamp() if parsed.tzinfo else None
    except (ValueError, TypeError, OverflowError, OSError):
        return None


def node_id(prefix: str, value: Any) -> str:
    raw = safe_text(value, 2048)
    if len(raw) > 160:
        raw = raw[:140] + ':' + hashlib.sha256(raw.encode()).hexdigest()[:16]
    return prefix + raw


@dataclass
class NetworkNode:
    id: str
    node_type: NodeType
    label: str
    source: str
    timestamp: float | None = None
    relevance: float | None = None
    metadata: dict = field(default_factory=dict)
    synthetic: bool = False
    original_id: str = ''


@dataclass
class NetworkEdge:
    source: str
    target: str
    label: str
    weight: float | None = None
    timestamp: float | None = None
    synthetic: bool = False


class MemoryNetworkGraph:
    def __init__(self, max_nodes: int = 100, max_edges: int = 200, *, mode: str = 'observed'):
        if any(isinstance(n, bool) or not isinstance(n, int) or n < 1 or n > 2000
               for n in (max_nodes, max_edges)):
            raise ValueError('Quotas devem ser inteiros entre 1 e 2000.')
        self.max_nodes, self.max_edges = max_nodes, max_edges
        self.nodes: dict[str, NetworkNode] = {}
        self.edges: list[NetworkEdge] = []
        self.event_log: list[dict] = []
        self.mode = mode
        self.omitted_nodes = self.omitted_edges = 0

    def add_node(self, ident, kind, label, *, source='local', at=None, relevance=None,
                 metadata=None, synthetic=False, original_id=''):
        ident = safe_text(ident, 220)
        if ident in self.nodes:
            node = self.nodes[ident]
            if metadata:
                node.metadata.update(metadata)
            stamp = timestamp(at)
            if stamp is not None and (node.timestamp is None or stamp > node.timestamp):
                node.timestamp = stamp
            return node
        if not ident or len(self.nodes) >= self.max_nodes:
            self.omitted_nodes += 1
            return None
        node = NetworkNode(ident, NodeType(kind), safe_text(label), safe_text(source),
                           timestamp(at), finite(relevance, unit=True), metadata or {},
                           bool(synthetic), safe_text(original_id or ident))
        self.nodes[ident] = node
        return node

    def add_edge(self, source, target, kind=EdgeType.REFERENCE, *, weight=None, at=None, synthetic=False):
        label = safe_text(kind.value if isinstance(kind, Enum) else kind, 80)
        if source not in self.nodes or target not in self.nodes:
            return None
        if any((e.source, e.target, e.label) == (source, target, label) for e in self.edges):
            return None
        if len(self.edges) >= self.max_edges:
            self.omitted_edges += 1
            return None
        edge = NetworkEdge(source, target, label, finite(weight), timestamp(at), bool(synthetic))
        self.edges.append(edge)
        return edge

    def to_dict(self, now=None, activation_window=5):
        now = time.time() if now is None else now
        def active(stamp):
            return stamp is not None and 0 <= now - stamp <= activation_window
        return {
            'mode': self.mode, 'verification': 'local_observation' if self.mode == 'observed' else 'demonstration',
            'externally_validated': False, 'generated_at': now,
            'nodes': [{'id': n.id, 'type': n.node_type.value, 'label': n.label,
                       'source': n.source, 'timestamp': n.timestamp, 'relevance': n.relevance,
                       'metadata': n.metadata, 'synthetic': n.synthetic,
                       'original_id': n.original_id, 'active': active(n.timestamp),
                       'metric_calibrated': False} for n in self.nodes.values()],
            'edges': [{'source': e.source, 'target': e.target, 'label': e.label,
                       'weight': e.weight, 'timestamp': e.timestamp, 'active': active(e.timestamp),
                       'synthetic': e.synthetic} for e in self.edges],
            'events': self.event_log[-40:], 'warnings': [],
            'limits': {'max_nodes': self.max_nodes, 'max_edges': self.max_edges,
                       'activation_window_seconds': activation_window,
                       'omitted_nodes': self.omitted_nodes, 'omitted_edges': self.omitted_edges},
        }


class CoreMemoryNetworkSource:
    MAX_JSON_BYTES = 8 * 1024 * 1024
    MAX_EVENT_BYTES = 256 * 1024

    def __init__(self, root=ROOT, max_nodes=100, max_edges=200, *, clock=time.time):
        self.root = Path(root).resolve()
        self.max_nodes, self.max_edges, self.clock = max_nodes, max_edges, clock
        self._cache = {}

    def _read(self, path, warnings, *, lines=False):
        try:
            stat = path.stat()
            key = (stat.st_ino, stat.st_size, stat.st_mtime_ns)
            cached = self._cache.get(str(path))
            if cached and cached[0] == key:
                warnings.extend(cached[2])
                return cached[1]
            errors = []
            budget = self.MAX_EVENT_BYTES if lines else self.MAX_JSON_BYTES
            if not lines and stat.st_size > budget:
                raise ValueError('source_size_limit')
            with path.open('rb') as stream:
                offset = max(0, stat.st_size-budget) if lines else 0
                stream.seek(offset)
                raw = stream.read(budget)
            if lines:
                if offset:
                    raw = raw.split(b'\n', 1)[-1]
                    errors.append({'source': path.name, 'status': 'tail_window'})
                data = []
                for line in raw.splitlines()[-200:]:
                    try:
                        item = json.loads(line)
                        if isinstance(item, dict):
                            data.append(item)
                    except (ValueError, UnicodeError):
                        errors.append({'source': path.name, 'status': 'invalid_or_partial_line'})
            else:
                data = json.loads(raw)
                if not isinstance(data, dict):
                    raise ValueError('invalid_source_shape')
            self._cache[str(path)] = (key, data, errors)
            warnings.extend(errors)
            return data
        except (OSError, ValueError, UnicodeError):
            self._cache.pop(str(path), None)
            warnings.append({'source': path.name, 'status': 'unavailable_or_invalid'})
            return [] if lines else {}

    def snapshot(self, *, science_graph=None, registry=None):
        warnings = []
        # Um root explícito é um projeto independente, inclusive sob testes.
        # O override do Core só se aplica ao projeto padrão.
        state_path = Path(os.environ.get('MCI_STATE_DIR', self.root/'.mci_state')) if self.root == ROOT.resolve() else self.root/'.mci_state'
        memory = self._read(state_path/'shared_memory.json', warnings)
        events = self._read(state_path/'metabus_events.jsonl', warnings, lines=True)
        claims = self._read(self.root/'data/evidence_graph.json', warnings)
        graph = MemoryNetworkGraph(self.max_nodes, self.max_edges)
        # Eventos e evidências têm prioridade sobre cartões ociosos do catálogo.
        self._events(graph, events[-40:])
        self._science(graph, science_graph)
        episodic = memory.get('episodic', [])
        if isinstance(episodic, list):
            for item in episodic[-40:]:
                if not isinstance(item, dict) or not item.get('id'):
                    continue
                ident = node_id('memory:', item['id'])
                graph.add_node(ident, NodeType.MEMORY, item.get('context', item.get('type', 'Registro de memória')),
                               source='MetaBus episódico', at=item.get('timestamp'), original_id=item['id'])
                if item.get('agent_id'):
                    agent = node_id('agent:', item['agent_id'])
                    graph.add_node(agent, NodeType.AGENT, item['agent_id'], source='MetaBus', at=item.get('timestamp'))
                    graph.add_edge(agent, ident, 'registrou', at=item.get('timestamp'))
        semantic = memory.get('semantic', {})
        if isinstance(semantic, dict):
            for name, item in list(semantic.items())[:30]:
                graph.add_node(node_id('context:', name), NodeType.CONTEXT, name, source='MetaBus semântico',
                               metadata={'lesson': safe_text(item.get('lesson', '')) if isinstance(item, dict) else safe_text(item)})
        for cid, claim in list(claims.items())[-20:]:
            if not isinstance(claim, dict):
                continue
            versions = claim.get('versions', [])
            latest = versions[-1] if isinstance(versions, list) and versions and isinstance(versions[-1], dict) else {}
            nid = node_id('claim:', cid)
            graph.add_node(nid, NodeType.CONTEXT, latest.get('hypothesis', cid), source='EvidenceGraph MCI',
                           at=claim.get('updated_at'), original_id=cid)
            for direction in ('evidence_for', 'evidence_against'):
                evidence = claim.get(direction, [])
                for index, item in enumerate(evidence[:10] if isinstance(evidence, list) else []):
                    if not isinstance(item, dict):
                        continue
                    eid = node_id('claim.evidence:', str(cid)+':'+direction+':'+str(index))
                    graph.add_node(eid, NodeType.EVIDENCE, item.get('description', 'Evidência registrada'),
                                   source=safe_text(item.get('source', 'MCI')), at=item.get('timestamp'))
                    graph.add_edge(nid, eid, direction, at=item.get('timestamp'))
        for card in (registry or [])[:self.max_nodes]:
            if not isinstance(card, dict):
                continue
            aid = card.get('agent_id')
            if aid:
                graph.add_node(node_id('agent:', aid), NodeType.AGENT, card.get('name', aid), source='Blackboard',
                               metadata={'status': safe_text(card.get('status')),
                                         'internal_confidence': finite(card.get('confidence_score'), unit=True)})
        snap = graph.to_dict(now=self.clock())
        snap['warnings'] = warnings
        snap['limits']['event_tail_bytes'] = self.MAX_EVENT_BYTES
        snap['sources'] = ['MetaBus persistido', 'EvidenceGraph MCI'] + (['EvidenceGraph R102'] if science_graph is not None else [])
        return snap

    @staticmethod
    def _events(graph, events):
        for event in events:
            payload = event.get('payload')
            if not isinstance(payload, dict):
                continue
            topic, at = safe_text(event.get('topic'), 80), event.get('timestamp')
            origin = event.get('source')
            aid = payload.get('agent_id') or payload.get('assigned_to') or origin
            agent = node_id('agent:', aid) if aid else None
            if agent:
                graph.add_node(agent, NodeType.AGENT, aid, source='Evento MetaBus', at=at)
            if topic.startswith('memory.') and payload.get('query_id'):
                query = node_id('query:', payload['query_id'])
                if topic == 'memory.query':
                    graph.add_node(query, NodeType.QUERY, payload.get('query', 'Busca de memória'), source=topic, at=at)
                    if agent:
                        graph.add_edge(query, agent, 'consultou', at=at)
                elif topic == 'memory.retrieved':
                    records = payload.get('records', [])
                    for item in records[:20] if isinstance(records, list) else []:
                        if not isinstance(item, dict) or not item.get('id'):
                            continue
                        ident = node_id('context:' if item.get('kind') == 'semantic' else 'memory:', item['id'])
                        kind = NodeType.CONTEXT if item.get('kind') == 'semantic' else NodeType.MEMORY
                        graph.add_node(ident, kind, item.get('context', item['id']), source=topic, at=at, original_id=item['id'])
                        graph.add_edge(query, ident, EdgeType.RETRIEVAL, at=at)
                elif topic == 'memory.response':
                    response = node_id('response:', payload['query_id'])
                    graph.add_node(response, NodeType.RESPONSE, payload.get('answer', 'Busca concluída'), source=topic, at=at)
                    graph.add_edge(query, response, 'resultado lexical', at=at)
            task = node_id('task:', payload.get('task_id')) if payload.get('task_id') else None
            if task and topic == 'task.post':
                graph.add_node(task, NodeType.QUERY, payload.get('description', 'Consulta registrada'), source=topic, at=at)
                if agent:
                    graph.add_edge(task, agent, 'postou', at=at)
            elif task and topic in ('task.assigned', 'task.complete'):
                graph.add_node(task, NodeType.QUERY, 'Tarefa '+safe_text(payload['task_id']), source=topic, at=at)
                if agent:
                    graph.add_edge(task, agent, EdgeType.EXECUTION, at=at)
                if topic == 'task.complete':
                    rid = node_id('response:', payload['task_id'])
                    result = payload.get('result')
                    label = result if isinstance(result, str) else (result.get('answer') or result.get('conclusion') or result.get('status')) if isinstance(result, dict) else None
                    graph.add_node(rid, NodeType.RESPONSE, label or 'Resultado registrado', source=topic, at=at,
                                   metadata={'reported_status': safe_text(payload.get('status'))})
                    if agent:
                        graph.add_edge(agent, rid, 'relatou', at=at)
            graph.event_log.append({'id':safe_text(event.get('event_id')), 'topic':topic,
                                    'source':safe_text(origin), 'timestamp':timestamp(at)})

    @staticmethod
    def _science(graph, export):
        if export is None:
            return
        if hasattr(export, 'to_dict'):
            export = export.to_dict()
        if not isinstance(export, dict):
            return
        def items(name):
            data = export.get(name, {})
            return list(data.values()) if isinstance(data, dict) else data if isinstance(data, list) else []
        for item in items('entities')[:500]:
            if isinstance(item, dict) and item.get('id'):
                graph.add_node(node_id('r102.entity:',item['id']),NodeType.CONTEXT,item.get('name',item['id']),
                               source='EvidenceGraph R102',original_id=item['id'],
                               metadata={'entity_type':safe_text(item.get('type')), 'evidence_count':safe_text(item.get('evidence_count',''))})
        for item in items('evidence')[:500]:
            if isinstance(item, dict) and item.get('id'):
                graph.add_node(node_id('r102.evidence:',item['id']),NodeType.EVIDENCE,item.get('text',item['id']),
                               source=item.get('source','R102'),original_id=item['id'])
        for item in items('entities')[:500]:
            if isinstance(item, dict) and isinstance(item.get('evidence'),list):
                for eid in item['evidence'][:30]:
                    graph.add_edge(node_id('r102.entity:',item.get('id')),node_id('r102.evidence:',eid),'evidência associada')
        for item in items('relations')[:500]:
            if isinstance(item, dict):
                graph.add_edge(node_id('r102.entity:',item.get('source',item.get('source_id'))),
                               node_id('r102.entity:',item.get('target',item.get('target_id'))),
                               item.get('type',item.get('relation_type','relação')),weight=item.get('weight'))


class MemoryNetworkSimulator:
    def snapshot(self, query='Consulta de demonstração', *, now=None):
        now = time.time() if now is None else now
        graph = MemoryNetworkGraph(mode='demonstration')
        for ident, kind, label in [('q',NodeType.QUERY,query),('m',NodeType.MEMORY,'Fragmento demonstrativo'),
                                    ('c',NodeType.CONTEXT,'Conceito demonstrativo'),('a',NodeType.AGENT,'Agente demonstrativo'),
                                    ('e',NodeType.EVIDENCE,'Fonte fictícia — sem valor probatório'),('r',NodeType.RESPONSE,'Resposta simulada')]:
            graph.add_node(ident,kind,label,source='Demonstração',at=now,synthetic=True)
        for source,target in [('q','m'),('m','c'),('c','a'),('a','r'),('e','r')]:
            graph.add_edge(source,target,'fluxo simulado',at=now,synthetic=True)
        return graph.to_dict(now=now)


class MemoryNetworkVisualizer:
    def __init__(self, snapshot):
        self.snapshot = snapshot.to_dict() if isinstance(snapshot, MemoryNetworkGraph) else snapshot

    def render_ascii_graph(self, width=100, frame=0, color=False):
        snap = self.snapshot
        header = 'REDE DE MEMÓRIA — '+('DEMONSTRAÇÃO' if snap.get('mode')=='demonstration' else 'DADOS LOCAIS OBSERVADOS')
        lines = [header, 'Atividade = evento recente; pesos/relevância não são probabilidades calibradas.']
        colors = {'consulta':34,'memoria':32,'contexto':36,'agente':33,'evidencia':37,'resposta':35}
        shown_nodes = sorted(snap.get('nodes',[]),key=lambda n:(bool(n.get('active')),n.get('timestamp') or 0),reverse=True)[:35]
        for node in shown_nodes:
            relevance = node.get('relevance')
            bar = ('#'*round(relevance*10)).ljust(10,'-') if relevance is not None else 'não registrada'
            pulse = '*o*'[frame%3] if node.get('active') else '.'
            line = f"{pulse} [{node['type'][:9]:9}] {safe_text(node['label'],45):45} | relevância {bar}"
            lines.append((f"\x1b[{colors.get(node['type'],37)}m{line}\x1b[0m" if color else line)[:width+20])
        if not snap.get('nodes'):
            lines.append('Nenhum nó nas fontes consultadas. Não foi fabricado fluxo de consulta.')
        lines.append('Arestas registradas:')
        shown_ids = {n['id'] for n in shown_nodes}
        shown_edges = sorted((e for e in snap.get('edges',[]) if e['source'] in shown_ids and e['target'] in shown_ids),
                             key=lambda e:(bool(e.get('active')),e.get('timestamp') or 0),reverse=True)[:12]
        for edge in shown_edges:
            arrow = ('->', '=>', '~>')[frame%3] if edge.get('active') else '->'
            lines.append(f"  {safe_text(edge['source'],28)} {arrow} {safe_text(edge['target'],28)} ({safe_text(edge['label'],25)})")
        lines.append('Eventos recentes: '+', '.join(safe_text(e.get('topic'),50) for e in snap.get('events',[])[-4:]))
        limits=snap.get('limits',{})
        lines.append(f"Exibição: {len(shown_nodes)}/{len(snap.get('nodes',[]))} nós, {len(shown_edges)}/{len(snap.get('edges',[]))} arestas; inclusões omitidas {limits.get('omitted_nodes',0)}. Fontes com aviso: {len(snap.get('warnings',[]))}.")
        return '\n'.join(lines)


def main(argv=None):
    parser=argparse.ArgumentParser(description='Observa a rede persistida do Core; não inicia inferência.')
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--once',action='store_true')
    parser.add_argument('--json',action='store_true')
    parser.add_argument('--demo',action='store_true')
    parser.add_argument('--frames',type=int)
    parser.add_argument('--interval',type=float,default=.5)
    args=parser.parse_args(argv)
    if not math.isfinite(args.interval) or not .01 <= args.interval <= 60 or args.frames is not None and not 1<=args.frames<=10000:
        parser.error('Intervalo deve estar entre .01 e 60s; frames entre 1 e 10000.')
    tty=bool(sys.stdout.isatty())
    count=1 if args.once or args.json or not tty and args.frames is None else args.frames
    source=CoreMemoryNetworkSource(args.root)
    frame=0
    try:
        while count is None or frame<count:
            snap=MemoryNetworkSimulator().snapshot() if args.demo else source.snapshot()
            if args.json:
                print(json.dumps(snap,ensure_ascii=False,allow_nan=False))
            else:
                if tty:
                    sys.stdout.write('\x1b[2J\x1b[H')
                print(MemoryNetworkVisualizer(snap).render_ascii_graph(frame=frame,color=tty),flush=True)
            frame+=1
            if count is None or frame<count:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
