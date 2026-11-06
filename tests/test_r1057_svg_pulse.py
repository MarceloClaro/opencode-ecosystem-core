"""R1057: SVG primário, fonte Mermaid auditável e pulso processual."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def animate():
    from scripts import animate_architecture
    return animate_architecture


def svgify():
    from scripts import svgify_markdown
    return svgify_markdown


def geometry():
    return {
        "nodes": [
            {"label": "A", "x": 10, "y": 10},
            {"label": "B", "x": 10, "y": 80},
            {"label": "C", "x": 200, "y": 80},
            {"label": "D", "x": 100, "y": 150},
        ],
        "edges": [
            {"id": "e1", "from_label": "A", "to_label": "B", "points": [[10, 10], [10, 80]]},
            {"id": "e2", "from_label": "A", "to_label": "C", "points": [[10, 10], [200, 80]]},
            {"id": "e3", "from_label": "B", "to_label": "D", "points": [[10, 80], [100, 150]]},
            {"id": "e4", "from_label": "C", "to_label": "D", "points": [[200, 80], [100, 150]]},
        ],
    }


def test_process_order_is_topological():
    order = animate().process_order(geometry())
    assert [edge["id"] for edge in order] == ["e1", "e2", "e3", "e4"]
    positions = {edge["id"]: index for index, edge in enumerate(order)}
    for first in order:
        for second in order:
            if first is not second and first["to_label"] == second["from_label"]:
                assert positions[first["id"]] < positions[second["id"]]


def test_cycle_is_deterministic_and_complete():
    g = geometry()
    g["edges"] = [
        {"id": "a", "from_label": "A", "to_label": "B", "points": [[10, 10], [10, 80]]},
        {"id": "b", "from_label": "B", "to_label": "A", "points": [[10, 80], [10, 10]]},
    ]
    first = animate().process_order(g)
    second = animate().process_order(g)
    assert [edge["id"] for edge in first] == [edge["id"] for edge in second]
    assert {edge["id"] for edge in first} == {"a", "b"}


def test_node_sequence_for_diagrams_without_edges():
    g = {"nodes": [{"label": "C", "x": 200, "y": 80}, {"label": "A", "x": 10, "y": 10}, {"label": "B", "x": 10, "y": 80}], "edges": []}
    assert animate().node_sequence(g) == ["A", "B", "C"]


def test_svgify_replaces_only_outside_core_flowcharts(tmp_path):
    code = "flowchart LR\n A[Entrada] --> B[Saída]\n"
    sha = hashlib.sha256(code.encode()).hexdigest()
    item = {"id": "diagram-" + sha[:16], "title": "Entrada e saída", "source_sha256": sha, "origins": []}
    folder = tmp_path / "docs/architecture/animated"
    folder.mkdir(parents=True)
    for ext in ("svg", "png", "gif", "mmd"):
        (folder / (item["id"] + "." + ext)).write_text("<svg/>\n" if ext == "svg" else "")
    (folder / "manifest.json").write_text(json.dumps({"diagrams": [item]}))
    doc = tmp_path / "docs/GUIDE.md"
    core = f"<!-- core-flowcharts:start -->\n```mermaid\n{code}```\n<!-- core-flowcharts:end -->\n"
    doc.write_text("# Guia\n\n" + core + "\n```mermaid\n" + code + "```\n")
    mod = svgify()
    summary = mod.run(tmp_path, check=False)
    text = doc.read_text()
    assert summary["replaced"] == 1
    assert text.count("<!-- svg-presentation:") == 1
    assert core in text  # bloco gerado pelo sync permanece intocado
    assert "Fonte Mermaid (auditoria)" in text
    before = text
    assert mod.run(tmp_path, check=True)["changed"] is False
    assert doc.read_text() == before


def test_svgify_preserves_unknown_source_and_check_does_not_write(tmp_path):
    doc = tmp_path / "README.md"
    doc.write_text("# X\n\n```mermaid\nflowchart LR\n A-->B\n```\n")
    summary = svgify().run(tmp_path, check=True)
    assert summary["changed"] is False
    assert summary["unmatched"] == ["README.md"]
    assert "```mermaid" in doc.read_text()


def test_svgify_relative_paths_from_docs(tmp_path):
    code = "flowchart LR\n A-->B\n"
    sha = hashlib.sha256(code.encode()).hexdigest()
    item = {"id": "diagram-" + sha[:16], "title": "Teste", "source_sha256": sha, "origins": []}
    folder = tmp_path / "docs/architecture/animated"
    folder.mkdir(parents=True)
    for ext in ("svg", "png", "gif", "mmd"):
        (folder / (item["id"] + "." + ext)).write_text("")
    (folder / "manifest.json").write_text(json.dumps({"diagrams": [item]}))
    doc = tmp_path / "docs/X.md"
    doc.write_text("```mermaid\n" + code + "```\n")
    svgify().run(tmp_path, check=False)
    assert f'src="architecture/animated/{item["id"]}.svg"' in doc.read_text()


def test_manifest_declares_process_pulse_and_svg_primary():
    manifest = json.loads((ROOT / "docs/architecture/animated/manifest.json").read_text())
    assert manifest["spec"] == "SPEC-935-R1057"
    assert manifest["animation"] == "process_pulse_reading_guide_not_execution"
    assert manifest["diagrams"]
    assert all("pulse" in row for row in manifest["diagrams"])
