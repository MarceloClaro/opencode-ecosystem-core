# -*- coding: utf-8 -*-
"""Gerador do mapa completo do ecossistema (nós + vetores)."""

from __future__ import annotations

import ast
import json
import re
import warnings
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Node:
    id: str
    label: str
    kind: str
    path: str = ""
    logical_group: str = ""
    layer: str = ""


@dataclass(frozen=True)
class Vector:
    source: str
    target: str
    kind: str
    note: str = ""


DISCOVERY_RULES = [
    ("marceloclaro/**/*.py", "module", "orchestration"),
    ("mci/oqs/**/*.py", "module", "scientific_governance"),
    ("mci/vsee/**/*.py", "module", "scientific_governance"),
    ("mci/egs/**/*.py", "module", "scientific_governance"),
    ("mci/pipeline/**/*.py", "module", "scientific_governance"),
    ("mci/**/*.py", "module", "mci"),
    ("sdd/**/*.py", "module", "sdd_tdd"),
    ("transformer/**/*.py", "module", "transformer"),
    ("trust/**/*.py", "module", "trust_economy"),
    ("economy/**/*.py", "module", "trust_economy"),
    ("scanners/**/*.py", "module", "diagnostics"),
    ("academic/**/*.py", "module", "academic"),
    ("reasoning/**/*.py", "module", "reasoning"),
    ("rag/**/*.py", "module", "rag"),
    ("legal/**/*.py", "module", "legal"),
    ("research/**/*.py", "module", "research"),
    ("benchmarks/scientific_reasoning/**/*.py", "benchmark", "benchmarks"),
    ("illustrations/**/*.py", "module", "illustrations"),
    ("publishing/**/*.py", "module", "publishing"),
    ("gametheory/**/*.py", "module", "gametheory"),
    ("mirofish/**/*.py", "module", "mirofish"),
    ("agents/catalog/*.md", "agent", "agents_catalog"),
    ("specs/SPEC-*.md", "spec", "specs"),
    ("schemas/*.json", "schema", "schemas"),
    ("tests/test_*.py", "test", "tests"),
    ("README.md", "doc", "docs"),
    ("ARCHITECTURE.md", "doc", "docs"),
    ("CHANGELOG.md", "doc", "docs"),
    ("RELEASE_NOTES.md", "doc", "docs"),
    ("CHANGELOG_EXECUTIVO_2026-07-06.md", "doc", "docs"),
    ("diagram.mmd", "diagram", "docs"),
]


LAYER_NODES = [
    Node("actor_user_cli", "Usuário / CLI", "actor", logical_group="entrypoint", layer="external"),
    Node("layer_orchestration", "Orquestração", "layer", logical_group="control", layer="orchestration"),
    Node("layer_sdd_tdd", "SDD + TDD", "layer", logical_group="quality", layer="sdd_tdd"),
    Node("layer_transformer", "Transformer Layer", "layer", logical_group="routing", layer="transformer"),
    Node("layer_mci", "Metacognitive Interconnect", "layer", logical_group="memory", layer="mci"),
    Node("layer_scientific_governance", "Scientific Governance Pipeline", "layer", logical_group="science", layer="scientific_governance"),
    Node("layer_trust_economy", "Trust + Token Economy", "layer", logical_group="governance", layer="trust_economy"),
    Node("layer_diagnostics", "Diagnostics", "layer", logical_group="analysis", layer="diagnostics"),
    Node("layer_reasoning", "Reasoning", "layer", logical_group="formal_reasoning", layer="reasoning"),
    Node("layer_rag", "Scientific RAG", "layer", logical_group="grounding", layer="rag"),
    Node("layer_legal", "Legal Reasoning", "layer", logical_group="legal_reasoning", layer="legal"),
    Node("layer_research", "Research", "layer", logical_group="research", layer="research"),
    Node("layer_benchmarks", "Benchmarks", "layer", logical_group="evaluation", layer="benchmarks"),
    Node("layer_illustrations", "Illustrations", "layer", logical_group="visualization", layer="illustrations"),
    Node("layer_publishing", "Publishing", "layer", logical_group="publishing", layer="publishing"),
    Node("layer_agents_catalog", "Agents Catalog", "layer", logical_group="agents", layer="agents_catalog"),
    Node("layer_specs", "Specifications", "layer", logical_group="documentation", layer="specs"),
    Node("layer_schemas", "Schemas", "layer", logical_group="contracts", layer="schemas"),
    Node("layer_tests", "Tests", "layer", logical_group="verification", layer="tests"),
    Node("layer_docs", "Docs", "layer", logical_group="documentation", layer="docs"),
]


FLOW_EDGES = [
    ("actor_user_cli", "marceloclaro/orchestrator.py", "control_flow", "comandos chegam ao orquestrador"),
    ("marceloclaro/orchestrator.py", "sdd/spec_engine.py", "control_flow", "cria/consulta specs"),
    ("marceloclaro/orchestrator.py", "sdd/tdd_runner.py", "control_flow", "executa ciclo TDD"),
    ("marceloclaro/orchestrator.py", "mci/metabus.py", "control_flow", "registra reflexões e eventos"),
    ("marceloclaro/orchestrator.py", "mci/blackboard.py", "control_flow", "delegação A2A via Blackboard"),
    ("marceloclaro/orchestrator.py", "trust/trust_engine.py", "control_flow", "gate comportamental"),
    ("marceloclaro/orchestrator.py", "economy/token_economy.py", "control_flow", "staking/slashing"),
    ("marceloclaro/orchestrator.py", "scanners/pipeline.py", "control_flow", "diagnóstico do ecossistema"),
    ("marceloclaro/orchestrator.py", "academic/maswos.py", "control_flow", "pipeline acadêmico"),
    ("marceloclaro/orchestrator.py", "reasoning/engines.py", "control_flow", "raciocínio formal"),
    ("marceloclaro/orchestrator.py", "mci/metacognitive_evaluator.py", "control_flow", "benchmark metacognitivo SPEC-920"),
    ("marceloclaro/orchestrator.py", "rag/scientific.py", "control_flow", "grounding científico via RAG"),
    ("marceloclaro/orchestrator.py", "mci/pipeline/scientific_governance_pipeline.py", "control_flow", "pipeline científico com governança"),
    ("marceloclaro/orchestrator.py", "research/hub.py", "control_flow", "pipeline de pesquisa"),
    ("marceloclaro/orchestrator.py", "illustrations/mira_engine.py", "control_flow", "ilustrações/metáforas"),
    ("marceloclaro/orchestrator.py", "publishing/production.py", "control_flow", "produção científica"),
    ("mci/pipeline/scientific_governance_pipeline.py", "mci/oqs/__init__.py", "control_flow", "etapa OQS"),
    ("mci/pipeline/scientific_governance_pipeline.py", "mci/orchestration.py", "control_flow", "núcleo científico"),
    ("mci/pipeline/scientific_governance_pipeline.py", "mci/vsee/router.py", "control_flow", "etapa VSEE"),
    ("mci/pipeline/scientific_governance_pipeline.py", "mci/egs/__init__.py", "control_flow", "etapa EGS"),
    ("mci/orchestration.py", "mci/evidence_graph.py", "data_flow", "persistência epistemológica"),
    ("mci/metabus.py", "mci/metacognitive_evaluator.py", "data_flow", "traços e reflexões para avaliação metacognitiva"),
    ("rag/scientific.py", "benchmarks/scientific_reasoning/superhuman_suite.py", "data_flow", "grounding alimenta readiness científico"),
    ("research/pipelines/run_research_batch.py", "mci/oqs/__init__.py", "control_flow", "runner invoca OQS"),
    ("research/pipelines/run_research_batch.py", "mci/orchestration.py", "control_flow", "runner invoca núcleo científico"),
    ("research/pipelines/run_research_batch.py", "mci/vsee/router.py", "control_flow", "runner invoca VSEE"),
    ("research/pipelines/run_research_batch.py", "mci/egs/__init__.py", "control_flow", "runner invoca EGS"),
    ("research/pipelines/analyze_research_batch.py", "research/pipelines/run_research_batch.py", "data_flow", "análise do raw/summary do runner"),
    ("research/pipelines/analyze_research_batch.py", "research/results/reports/final_report_template.md", "data_flow", "preenche template final"),
    # Legal reasoning module (SPEC-921)
    ("marceloclaro/orchestrator.py", "legal/__init__.py", "control_flow", "raciocínio jurídico brasileiro SPEC-921"),
    ("legal/syllogism.py", "legal/balancing.py", "data_flow", "subsunção alimenta ponderação"),
    ("legal/syllogism.py", "legal/constitutional.py", "data_flow", "controle de constitucionalidade via interpretação"),
    ("legal/precedents.py", "legal/syllogism.py", "data_flow", "ratio decidendi informa subsunção"),
    ("legal/argumentation.py", "legal/syllogism.py", "data_flow", "scoring valida consistência da subsunção"),
]


def _node_id_from_path(rel_path: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", rel_path).strip("_")


def _collect_files() -> List[Node]:
    nodes: Dict[str, Node] = {n.id: n for n in LAYER_NODES}
    seen_paths = set()
    for pattern, kind, layer in DISCOVERY_RULES:
        for path in sorted(ROOT.glob(pattern)):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel in seen_paths:
                continue
            seen_paths.add(rel)
            nodes[_node_id_from_path(rel)] = Node(
                id=_node_id_from_path(rel),
                label=path.stem,
                kind=kind,
                path=rel,
                layer=layer,
            )
    return list(nodes.values())


def _layer_id(layer: str) -> str:
    return f"layer_{layer}"


def _containment_vectors(nodes: List[Node]) -> List[Vector]:
    vectors: List[Vector] = []
    for node in nodes:
        if node.path and node.layer:
            layer_id = _layer_id(node.layer)
            if any(n.id == layer_id for n in LAYER_NODES):
                vectors.append(Vector(layer_id, node.id, "contains", f"{node.layer} contém {node.path}"))
    return vectors


def _resolve_import(module_name: str) -> Optional[str]:
    if not module_name:
        return None
    path_py = ROOT / (module_name.replace(".", "/") + ".py")
    if path_py.exists():
        return path_py.relative_to(ROOT).as_posix()
    path_pkg = ROOT / module_name.replace(".", "/") / "__init__.py"
    if path_pkg.exists():
        return path_pkg.relative_to(ROOT).as_posix()
    return None


def _import_vectors(nodes: List[Node]) -> List[Vector]:
    node_by_path = {n.path: n.id for n in nodes if n.path}
    vectors: List[Vector] = []
    for node in nodes:
        if not node.path or not node.path.endswith(".py"):
            continue
        source_path = ROOT / node.path
        try:
            source = source_path.read_text(encoding="utf-8")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(source)
        except Exception:
            continue
        for child in ast.walk(tree):
            target_path = None
            if isinstance(child, ast.Import):
                for alias in child.names:
                    target_path = _resolve_import(alias.name)
                    if target_path and target_path in node_by_path:
                        vectors.append(Vector(node.id, node_by_path[target_path], "imports", alias.name))
            elif isinstance(child, ast.ImportFrom):
                target_path = _resolve_import(child.module or "")
                if target_path and target_path in node_by_path:
                    vectors.append(Vector(node.id, node_by_path[target_path], "imports", child.module or ""))
    return vectors


def _parse_spec_frontmatter(spec_path: Path) -> Dict[str, Any]:
    text = spec_path.read_text(encoding="utf-8")
    match = re.search(r"```yaml\n(.*?)\n```", text, re.DOTALL)
    if not match:
        return {}
    meta: Dict[str, Any] = {}
    lines = match.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("spec_id:"):
            meta["spec_id"] = line.split(":", 1)[1].strip()
        elif line.startswith("depends_on:"):
            raw = line.split(":", 1)[1].strip().strip("[]")
            meta["depends_on"] = [x.strip() for x in raw.split(",") if x.strip()]
        elif line.startswith("module:"):
            meta.setdefault("modules", []).append(line.split(":", 1)[1].strip())
        elif line.startswith("modules:"):
            i += 1
            while i < len(lines) and lines[i].lstrip().startswith("-"):
                meta.setdefault("modules", []).append(lines[i].split("-", 1)[1].strip())
                i += 1
            continue
        i += 1
    return meta


def _module_path_to_target(module_path: str, node_by_path: Dict[str, str]) -> Optional[str]:
    module_path = module_path.strip()
    if module_path in node_by_path:
        return node_by_path[module_path]
    if module_path.endswith("/"):
        prefix = module_path.rstrip("/")
        layer_map = {
            "integrations": "layer_integrations",
            "reasoning": "layer_reasoning",
            "agents": "layer_agents_catalog",
            "scanners": "layer_diagnostics",
            "publishing": "layer_publishing",
            "research": "layer_research",
            "rag": "layer_rag",
            "legal": "layer_legal",
            "illustrations": "layer_illustrations",
            "schemas": "layer_schemas",
        }
        return layer_map.get(prefix)
    return None


def _spec_vectors(nodes: List[Node]) -> List[Vector]:
    node_by_path = {n.path: n.id for n in nodes if n.path}
    spec_nodes = [n for n in nodes if n.kind == "spec" and n.path]
    spec_id_to_node: Dict[str, str] = {}
    for node in spec_nodes:
        meta = _parse_spec_frontmatter(ROOT / node.path)
        if meta.get("spec_id"):
            spec_id_to_node[meta["spec_id"]] = node.id
    vectors: List[Vector] = []
    for node in spec_nodes:
        meta = _parse_spec_frontmatter(ROOT / node.path)
        for dep in meta.get("depends_on", []):
            if dep in spec_id_to_node:
                vectors.append(Vector(node.id, spec_id_to_node[dep], "depends_on", dep))
        for module_path in meta.get("modules", []):
            target = _module_path_to_target(module_path, node_by_path)
            if target:
                vectors.append(Vector(node.id, target, "documents", module_path))
    return vectors


def _manual_flow_vectors(nodes: List[Node]) -> List[Vector]:
    node_by_path = {n.path: n.id for n in nodes if n.path}
    vectors: List[Vector] = []
    for source, target, kind, note in FLOW_EDGES:
        source_id = node_by_path.get(source, source)
        target_id = node_by_path.get(target, target)
        if any(n.id == source_id for n in nodes) and any(n.id == target_id for n in nodes):
            vectors.append(Vector(source_id, target_id, kind, note))
    return vectors


def _dedup_vectors(vectors: Iterable[Vector]) -> List[Vector]:
    seen = set()
    result = []
    for v in vectors:
        key = (v.source, v.target, v.kind, v.note)
        if key not in seen:
            seen.add(key)
            result.append(v)
    return result


def build_ecosystem_map() -> Dict[str, Any]:
    nodes = _collect_files()
    vectors = []
    vectors.extend(_containment_vectors(nodes))
    vectors.extend(_import_vectors(nodes))
    vectors.extend(_spec_vectors(nodes))
    vectors.extend(_manual_flow_vectors(nodes))
    vectors = _dedup_vectors(vectors)

    node_kind_counts = Counter(n.kind for n in nodes)
    vector_kind_counts = Counter(v.kind for v in vectors)

    return {
        "summary": {
            "node_count": len(nodes),
            "vector_count": len(vectors),
            "node_kinds": dict(sorted(node_kind_counts.items())),
            "vector_kinds": dict(sorted(vector_kind_counts.items())),
        },
        "nodes": [asdict(n) for n in sorted(nodes, key=lambda x: (x.kind, x.path or x.id))],
        "vectors": [asdict(v) for v in sorted(vectors, key=lambda x: (x.kind, x.source, x.target))],
    }


def render_ecosystem_map_markdown(graph: Dict[str, Any]) -> str:
    lines = [
        "# Mapa Completo do Ecossistema — Nós e Vetores",
        "",
        f"- Nós: **{graph['summary']['node_count']}**",
        f"- Vetores: **{graph['summary']['vector_count']}**",
        "",
        "## Taxonomia de Nós",
        "",
        "| kind | quantidade |",
        "|---|---:|",
    ]
    for kind, count in graph["summary"]["node_kinds"].items():
        lines.append(f"| {kind} | {count} |")
    lines.extend([
        "",
        "## Taxonomia de Vetores",
        "",
        "| kind | quantidade |",
        "|---|---:|",
    ])
    for kind, count in graph["summary"]["vector_kinds"].items():
        lines.append(f"| {kind} | {count} |")
    lines.extend([
        "",
        "## Diagrama de Alto Nível",
        "",
        "```mermaid",
        "graph TD",
        "  actor_user_cli[Usuário / CLI] --> orchestrator_py[marceloclaro/orchestrator.py]",
        "  orchestrator_py --> spec_engine_py[sdd/spec_engine.py]",
        "  orchestrator_py --> tdd_runner_py[sdd/tdd_runner.py]",
        "  orchestrator_py --> metabus_py[mci/metabus.py]",
        "  orchestrator_py --> blackboard_py[mci/blackboard.py]",
        "  orchestrator_py --> trust_engine_py[trust/trust_engine.py]",
        "  orchestrator_py --> token_economy_py[economy/token_economy.py]",
        "  orchestrator_py --> metaeval_py[mci/metacognitive_evaluator.py]",
        "  orchestrator_py --> rag_py[rag/scientific.py]",
        "  orchestrator_py --> sgp_py[mci/pipeline/scientific_governance_pipeline.py]",
        "  sgp_py --> oqs_init_py[mci/oqs/__init__.py]",
        "  sgp_py --> orchestration_py[mci/orchestration.py]",
        "  sgp_py --> vsee_router_py[mci/vsee/router.py]",
        "  sgp_py --> egs_init_py[mci/egs/__init__.py]",
        "  orchestration_py --> evidence_graph_py[mci/evidence_graph.py]",
        "  metabus_py --> metaeval_py",
        "  rag_py --> superhuman_suite_py[benchmarks/scientific_reasoning/superhuman_suite.py]",
        "```",
        "",
        "## Inventário de Nós",
        "",
        "| id | kind | layer | path/logical_group |",
        "|---|---|---|---|",
    ])
    for node in graph["nodes"]:
        path_or_group = node.get("path") or node.get("logical_group") or ""
        lines.append(f"| {node['id']} | {node['kind']} | {node.get('layer','')} | {path_or_group} |")
    lines.extend([
        "",
        "## Inventário de Vetores",
        "",
        "| source | target | kind | note |",
        "|---|---|---|---|",
    ])
    for vector in graph["vectors"]:
        lines.append(f"| {vector['source']} | {vector['target']} | {vector['kind']} | {vector.get('note','')} |")
    return "\n".join(lines)


def save_ecosystem_map_artifacts(
    json_path: str = "maps/ecosystem_map_2026-07-06.json",
    markdown_path: str = "MAPA_ECOSSISTEMA_COMPLETO_2026-07-06.md",
) -> Dict[str, str]:
    graph = build_ecosystem_map()
    json_file = ROOT / json_path
    md_file = ROOT / markdown_path
    json_file.parent.mkdir(parents=True, exist_ok=True)
    md_file.parent.mkdir(parents=True, exist_ok=True)
    json_file.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    md_file.write_text(render_ecosystem_map_markdown(graph), encoding="utf-8")
    return {
        "json": json_file.relative_to(ROOT).as_posix(),
        "markdown": md_file.relative_to(ROOT).as_posix(),
    }


__all__ = [
    "build_ecosystem_map",
    "render_ecosystem_map_markdown",
    "save_ecosystem_map_artifacts",
]
