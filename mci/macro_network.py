"""R1050: macro-rede read-only de orquestração, skills, evidência e gates.

Não executa agentes, não chama rede e não promove confiança. O grafo é uma
projeção auditável dos arquivos locais; arestas não são prova de execução.
"""
from __future__ import annotations

import argparse
from collections import deque
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KDENSE = ROOT / "external/kdense-scientific-agent-skills/CATALOG.json"


def _skill_dirs():
    base = ROOT / ".opencode/skills"
    return sorted(p.name for p in base.iterdir()
                  if p.is_dir() and (p / "SKILL.md").is_file())


def _agents():
    base = ROOT / "agents/catalog"
    return sorted(p.stem for p in base.glob("*.md") if p.is_file())


class MacroNetwork:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self._build()

    def _add(self, identifier, kind, label=None, **extra):
        self.nodes.append({"id": identifier, "type": kind,
                           "label": label or identifier, **extra})

    def _edge(self, source, target, relation):
        self.edges.append({"source": source, "target": target,
                           "relation": relation})

    def _build(self):
        self._add("orchestrator:marceloclaro", "orchestrator", "MarceloClaro")
        for gate, label in (
            ("metacognitive", "Gate metacognitivo R1050"),
            ("council", "Conselho científico R989/R1050"),
            ("video_qa", "QC de vídeo R1049"),
            ("research_lab", "Laboratório isolado R1049"),
        ):
            self._add(f"gate:{gate}", "gate", label)
            self._edge("orchestrator:marceloclaro", f"gate:{gate}", "governed_by")
        for agent in _agents():
            self._add(f"agent:{agent}", "agent", agent)
            self._edge("orchestrator:marceloclaro", f"agent:{agent}", "delegates")
        for skill in _skill_dirs():
            self._add(f"skill:{skill}", "skill", skill)
            self._edge("orchestrator:marceloclaro", f"skill:{skill}", "exposes")
        if not KDENSE.is_file():
            return
        catalog = json.loads(KDENSE.read_text(encoding="utf-8"))
        categories = catalog.get("categories") or {}
        for category, count in sorted(categories.items()):
            self._add(f"kdense-category:{category}", "scientific_category",
                      category, count=count)
            self._edge("skill:kdense-ciencia-seletiva",
                       f"kdense-category:{category}", "routes_to")
            self._edge(f"kdense-category:{category}", "gate:metacognitive",
                       "governed_by")
        for item in catalog.get("skills", []):
            identifier = f"kdense:{item['skill']}"
            self._add(identifier, "scientific_skill", item["skill"],
                      category=item["category"],
                      license_class=item.get("license_class"),
                      mirrored=item.get("mirrored"),
                      adapter=bool(item.get("original_adapter_md")),
                      risk_flags=item.get("risk_flags", []))
            self._edge(f"kdense-category:{item['category']}", identifier,
                       "contains")
            self._edge(identifier, "gate:metacognitive", "governed_by")
        for edge in (
            ("skill:rigor-academico-chgagne", "gate:council", "gated_by"),
            ("skill:superpowers-sdd-tdd", "gate:metacognitive", "gated_by"),
            ("skill:video-director-qa", "gate:video_qa", "gated_by"),
            ("skill:laboratorio-pesquisa-isolado", "gate:research_lab", "gated_by"),
            ("skill:kdense-adaptacoes-originais", "gate:council", "gated_by"),
        ):
            if any(node["id"] == edge[0] for node in self.nodes):
                self._edge(*edge)

    def neighbors(self, node_id, relation=None):
        if not any(node["id"] == node_id for node in self.nodes):
            raise ValueError("nó ausente")
        result = []
        for edge in self.edges:
            if edge["source"] == node_id and (relation is None or edge["relation"] == relation):
                result.append({**edge, "direction": "out"})
            elif edge["target"] == node_id and (relation is None or edge["relation"] == relation):
                result.append({**edge, "direction": "in"})
        return result

    def path(self, source, target, max_depth=5):
        if type(max_depth) is not int or not 1 <= max_depth <= 10:
            raise ValueError("profundidade deve ser 1..10")
        adjacency = {}
        for edge in self.edges:
            adjacency.setdefault(edge["source"], []).append(edge["target"])
        queue = deque([(source, [source])])
        seen = {source}
        while queue:
            node, trail = queue.popleft()
            if node == target:
                return trail
            if len(trail) - 1 >= max_depth:
                continue
            for nxt in adjacency.get(node, []):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, trail + [nxt]))
        return None

    def risk_summary(self):
        flags = {}
        categories = {}
        for node in self.nodes:
            if node["type"] == "scientific_skill":
                categories[node["category"]] = categories.get(node["category"], 0) + 1
                for flag in node.get("risk_flags", []):
                    flags[flag] = flags.get(flag, 0) + 1
        return {"risk_flags": dict(sorted(flags.items())),
                "categories": dict(sorted(categories.items()))}

    def snapshot(self):
        counts = {}
        for node in self.nodes:
            counts[node["type"]] = counts.get(node["type"], 0) + 1
        return {
            "schema_version": 1,
            "root": str(ROOT),
            "nodes": self.nodes,
            "edges": self.edges,
            "counts": dict(sorted(counts.items())),
            "risk": self.risk_summary(),
            "policy": {
                "read_only": True,
                "network": False,
                "execution_proof": False,
                "edge_is_not_inference": True,
                "confidence_promoted": False,
            },
        }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["summary", "snapshot", "path", "neighbors"])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--source")
    parser.add_argument("--target")
    parser.add_argument("--node")
    parser.add_argument("--max-depth", type=int, default=5)
    args = parser.parse_args(argv)
    network = MacroNetwork()
    if args.command == "summary":
        snap = network.snapshot()
        print(json.dumps({"counts": snap["counts"], "risk": snap["risk"],
                          "policy": snap["policy"]}, ensure_ascii=False, indent=2))
    elif args.command == "snapshot":
        snap = network.snapshot()
        text = json.dumps(snap, ensure_ascii=False, indent=2) + "\n"
        if args.out:
            args.out.write_text(text, encoding="utf-8")
            print(json.dumps({"status": "written", "out": str(args.out),
                              "nodes": len(snap["nodes"]), "edges": len(snap["edges"])},
                             ensure_ascii=False))
        else:
            print(text)
    elif args.command == "path":
        if not args.source or not args.target:
            raise SystemExit("--source e --target obrigatórios")
        print(json.dumps({"path": network.path(args.source, args.target,
                                               args.max_depth)}, ensure_ascii=False))
    else:
        if not args.node:
            raise SystemExit("--node obrigatório")
        print(json.dumps(network.neighbors(args.node), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
