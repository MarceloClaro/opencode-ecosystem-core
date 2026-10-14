"""R881: paridade estrutural, proveniência e rejeição de omissões em Mermaid."""
import copy
import importlib.util
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def builder():
    source = ROOT / "scripts/build_mermaid_architecture.py"
    spec = importlib.util.spec_from_file_location("r881_mermaid", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def snapshot():
    return {
        "schema_version": "r879.v1",
        "git": {"commit": "a" * 40, "tree": "b" * 40, "requested_ref": "fixture"},
        "modules": [
            {"id": "n_" + "1" * 20, "path": "pkg/a.py", "module": "pkg.a", "package": "pkg", "layer": "interfaces", "sha256": "a" * 64, "symbols": [{"kind": "function", "name": "run", "line": 1, "end_line": 2}]},
            {"id": "n_" + "2" * 20, "path": "pkg/b.py", "module": "pkg.b", "package": "pkg", "layer": "interfaces", "sha256": "b" * 64, "symbols": []},
            {"id": "n_" + "3" * 20, "path": "extra/alone.py", "module": "extra.alone", "package": "extra", "layer": "modulos_adicionais", "sha256": "c" * 64, "symbols": []},
        ],
        "edges": [
            {"source_id": "n_" + "1" * 20, "target_id": "n_" + "2" * 20, "source": "pkg.a", "target": "pkg.b", "path": "pkg/a.py", "line": line, "kind": "declared_import"}
            for line in (5, 9)
        ],
        "limitations": ["Imports declarados não provam execução."],
    }


def graph_sets(text):
    nodes = set(re.findall(r'^\s*(n_[a-f0-9]{20})\["', text, re.MULTILINE))
    edges = set(re.findall(r'^\s*(n_[a-f0-9]{20}) --> (n_[a-f0-9]{20})\s*$', text, re.MULTILINE))
    return nodes, edges


def comments(text, prefix):
    return [json.loads(line[len(prefix):]) for line in text.splitlines() if line.startswith(prefix)]


def test_every_module_including_isolated_and_unique_pair_preserved(builder, snapshot):
    text = builder.render_mermaid(snapshot)
    nodes, edges = graph_sets(text)
    assert nodes == {module["id"] for module in snapshot["modules"]}
    assert edges == {(edge["source_id"], edge["target_id"]) for edge in snapshot["edges"]}
    assert text.count('subgraph pkg_') == 2
    assert 'leg_importador' in text and 'leg_dependencia' in text


def test_all_ast_declarations_and_symbols_survive_deduplication(builder, snapshot):
    text = builder.render_mermaid(snapshot)
    edges = comments(text, "%% edge-metadata ")
    modules = comments(text, "%% module-metadata ")
    assert len(edges) == 1
    assert edges[0]["declarations"] == snapshot["edges"]
    assert {entry["id"]: entry["symbols"] for entry in modules} == {entry["id"]: entry["symbols"] for entry in snapshot["modules"]}
    assert {entry["id"]: entry["sha256"] for entry in modules} == {entry["id"]: entry["sha256"] for entry in snapshot["modules"]}


def test_reordering_input_never_changes_output(builder, snapshot):
    reordered = copy.deepcopy(snapshot)
    reordered["modules"].reverse()
    reordered["edges"].reverse()
    assert builder.render_mermaid(reordered) == builder.render_mermaid(snapshot)
    assert builder.build_correspondence(reordered, builder.render_mermaid(reordered)) == builder.build_correspondence(snapshot, builder.render_mermaid(snapshot))


def test_labels_are_escaped_and_cannot_inject_nodes_or_directives(builder, snapshot):
    payload = 'x"]\nEVIL["<script>bad</script> & #quoted# \\ %%{init:bad}%%'
    snapshot["modules"][2].update(module=payload, package=payload, layer=payload, path='x"\\\n.py')
    text = builder.render_mermaid(snapshot)
    node_lines = [line for line in text.splitlines() if re.match(r'\s*n_[a-f0-9]{20}\[', line)]
    assert len(node_lines) == 3
    assert '#quot;' in text and '#lt;' in text and '#gt;' in text and '#amp;' in text
    assert not any(line.startswith('EVIL') for line in text.splitlines())
    assert not any('%%{init:' in line for line in node_lines)


def test_json_comments_cannot_activate_mermaid_directives(builder, snapshot):
    payload = "%%{init: {'theme':'dark'}}%% <script>bad</script>"
    snapshot["git"]["requested_ref"] = payload
    snapshot["limitations"] = [payload]
    snapshot["modules"][2]["module"] = payload
    text = builder.render_mermaid(snapshot)
    assert "%%{init:" not in text
    assert "<script>" not in text
    assert comments(text, "%% snapshot ")[0]["requested_ref"] == payload
    assert comments(text, "%% limitation ") == [payload]
    assert next(m for m in comments(text, "%% module-metadata ")
                if m["id"] == snapshot["modules"][2]["id"])["module"] == payload


@pytest.mark.parametrize("mutation", ["duplicate_id", "duplicate_path", "unknown_target", "unsafe_id", "wrong_source"])
def test_malformed_snapshots_fail_closed(builder, snapshot, mutation):
    if mutation == "duplicate_id":
        snapshot["modules"][1]["id"] = snapshot["modules"][0]["id"]
    elif mutation == "duplicate_path":
        snapshot["modules"][1]["path"] = snapshot["modules"][0]["path"]
    elif mutation == "unknown_target":
        snapshot["edges"][0]["target_id"] = "n_" + "f" * 20
    elif mutation == "unsafe_id":
        snapshot["modules"][2]["id"] = 'bad"] --> EVIL'
    else:
        snapshot["edges"][0]["source"] = "different.module"
    with pytest.raises(ValueError):
        builder.render_mermaid(snapshot)


@pytest.mark.parametrize("mutation", ["node", "edge", "provenance"])
def test_correspondence_rejects_missing_node_edge_or_metadata(builder, snapshot, mutation):
    original = builder.render_mermaid(snapshot)
    if mutation == "node":
        changed = "\n".join(line for line in original.splitlines() if not re.match(r'\s*n_33333333333333333333\[', line)) + "\n"
    elif mutation == "edge":
        changed = "\n".join(line for line in original.splitlines() if 'n_11111111111111111111 --> n_22222222222222222222' not in line) + "\n"
    else:
        changed = original.replace('"line":5', '"line":6')
    with pytest.raises(ValueError):
        builder.build_correspondence(snapshot, changed)


def test_check_detects_tampering_without_modifying_files(builder, snapshot, tmp_path):
    destination = tmp_path / "dependencies.mmd"
    manifest = tmp_path / "mermaid-correspondence.json"
    builder.write_artifacts(snapshot, destination, correspondence=manifest)
    assert builder.main(["--inventory", str(_inventory(tmp_path, snapshot)), "--output", str(destination), "--correspondence", str(manifest), "--check"]) == 0
    destination.write_text(destination.read_text().replace('n_11111111111111111111 --> n_22222222222222222222', ''), encoding="utf-8")
    before = destination.read_bytes()
    assert builder.main(["--inventory", str(tmp_path / "inventory.json"), "--output", str(destination), "--correspondence", str(manifest), "--check"]) == 1
    assert destination.read_bytes() == before


@pytest.mark.parametrize("alias", [False, True])
def test_identical_output_destinations_rejected_without_writing(builder, snapshot, tmp_path, alias):
    destination = tmp_path / "dependencies.mmd"
    destination.write_text("preservar", encoding="utf-8")
    manifest = destination
    if alias:
        manifest = tmp_path / "manifest.json"
        manifest.symlink_to(destination)
    with pytest.raises(ValueError):
        builder.write_artifacts(snapshot, destination, correspondence=manifest)
    assert destination.read_text(encoding="utf-8") == "preservar"


def _inventory(tmp_path, snapshot):
    path = tmp_path / "inventory.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")
    return path


def test_current_snapshot_mermaid_json_svg_sets_are_identical(builder):
    snapshot = json.loads((ROOT / "docs/architecture/architecture-inventory.json").read_text())
    text = builder.render_mermaid(snapshot)
    nodes, edges = graph_sets(text)
    assert len(nodes) == 677
    assert len(edges) == 935
    assert len(snapshot["edges"]) == 1051
    modules_metadata = comments(text, "%% module-metadata ")
    assert sum(len(entry["symbols"]) for entry in modules_metadata) == 6432
    assert text.count('subgraph pkg_') == 45
    svg = ET.parse(ROOT / "docs/architecture/dependencies.svg").getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}
    svg_nodes = {node.attrib["id"] for node in svg.findall('.//svg:g[@class="node"]', ns)}
    svg_edges = {tuple(edge.find('svg:title', ns).text.split('->')) for edge in svg.findall('.//svg:g[@class="edge"]', ns)}
    assert nodes == svg_nodes == {module["id"] for module in snapshot["modules"]}
    assert edges == svg_edges == {(edge["source_id"], edge["target_id"]) for edge in snapshot["edges"]}
    manifest = builder.build_correspondence(snapshot, text)
    assert manifest["counts"] == {"modules": 677, "module_pairs": 935, "ast_declarations": 1051, "symbols": 6432, "packages": 45, "layers": 18}


def test_published_mermaid_manifest_and_rendered_svg_preserve_the_graph(builder):
    directory = ROOT / "docs/architecture"
    assert builder.main(["--inventory", str(directory / "architecture-inventory.json"),
                         "--output", str(directory / "dependencies.mmd"),
                         "--correspondence", str(directory / "mermaid-correspondence.json"),
                         "--check"]) == 0
    expected_nodes, expected_edges = graph_sets((directory / "dependencies.mmd").read_text())
    svg = ET.parse(directory / "dependencies-mermaid.svg").getroot()
    nodes, edges = set(), set()
    for element in svg.iter():
        match = re.search(r'flowchart-(n_[a-f0-9]{20})-\d+$', element.get("id", ""))
        if match:
            nodes.add(match.group(1))
        match = re.fullmatch(r'L_(n_[a-f0-9]{20})_(n_[a-f0-9]{20})_\d+', element.get("data-id", ""))
        if match:
            edges.add(match.groups())
    assert nodes == expected_nodes
    assert edges == expected_edges
