"""R911: contratos editoriais e conservação do grafo; não prova execução do Core."""
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "livro-core/atlas"
STATIC = ROOT / "docs/architecture-r911"
NODE = r"n_[0-9a-f]{20}"


def _module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def builder():
    return _module("r911_atlas_builder", "livro-core/gen_architecture_atlas.py")


@pytest.fixture(scope="module")
def exporters():
    return (_module("r911_static_dot", "scripts/build_architecture_maps.py"),
            _module("r911_static_mermaid", "scripts/build_mermaid_architecture.py"))


@pytest.fixture
def source_architectures():
    # Ler os dados autoritativos, não o manifesto gerado que poderia ocultar uma omissão.
    return sorted([entry for filename in ("data-orchestration.json", "data-science.json")
                   for entry in json.loads((ATLAS / filename).read_text())],
                  key=lambda entry: entry["id"])


@pytest.fixture(scope="module")
def snapshot():
    return json.loads((STATIC / "architecture-inventory.json").read_text())


def _dot_graph(text):
    nodes = re.findall(rf"^\s*({NODE})\s+\[", text, flags=re.M)
    pairs = re.findall(rf"^\s*({NODE})\s*->\s*({NODE})\s*;", text, flags=re.M)
    return nodes, pairs


def _mermaid_graph(text):
    # Analisar as declarações visuais, sem confiar nos comentários JSON do exportador.
    nodes = re.findall(rf'^\s*({NODE})\["', text, flags=re.M)
    pairs = re.findall(rf"^\s*({NODE})\s*-->\s*({NODE})\s*$", text, flags=re.M)
    return nodes, pairs


def _expected(snapshot):
    nodes = {module["id"] for module in snapshot["modules"]}
    pairs = {(edge["source_id"], edge["target_id"]) for edge in snapshot["edges"]}
    return nodes, pairs


def _assert_graph_conserved(nodes, pairs, expected_nodes, expected_pairs):
    # Contagem e conjunto são verificados: IDs duplicados não podem mascarar omissões.
    assert len(nodes) == len(expected_nodes)
    assert set(nodes) == expected_nodes
    assert len(pairs) == len(expected_pairs)
    assert set(pairs) == expected_pairs


def test_architectures_have_three_local_views(source_architectures):
    published = json.loads((ATLAS / "architectures.json").read_text())["architectures"]
    assert {entry["id"] for entry in published} == {f"AR{i:02}" for i in range(1, 19)}
    assert len(published) == len(source_architectures) == 18
    for entry in published:
        assert set(entry["views"]) == {"mental", "structure", "flow"}
        consumer = (ROOT / "livro-core" / (entry["chapters"][0] + ".tex")).read_text()
        for kind, filename in entry["views"].items():
            assert filename == f"{entry['id']}-{kind}.tex"
            assert (ATLAS / filename).is_file()
            assert r"\input{atlas/" + filename.removesuffix(".tex") + "}" in consumer
    assert r"\input{atlas/global}" in (ROOT / "livro-core/mod-01d-arquitetura.tex").read_text()


def test_authoritative_architectures_validate(builder, source_architectures):
    report = builder.validate_atlas(source_architectures, ROOT)
    assert report["architectures"] == 18
    assert report["views"] == 54
    assert report["sources"]
    for path, recorded in report["sources"].items():
        assert recorded["sha256"] == hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_rejects_missing_mental_branch(builder, source_architectures):
    source_architectures[0]["mental"].pop()
    with pytest.raises(ValueError, match="quatro ramos"):
        builder.validate_atlas(source_architectures, ROOT)


@pytest.mark.parametrize("field", ["no", "recovery"])
def test_rejects_flow_without_refusal_or_recovery(builder, source_architectures, field):
    source_architectures[0]["flow"][field] = "   "
    with pytest.raises(ValueError, match="recusa e recuperação"):
        builder.validate_atlas(source_architectures, ROOT)


def test_rejects_diagram_without_relationships(builder, source_architectures):
    source_architectures[0]["edges"] = []
    with pytest.raises(ValueError, match="Diagrama sem relação"):
        builder.validate_atlas(source_architectures, ROOT)


def test_rejects_nonexistent_source_symbol(builder, source_architectures):
    source_architectures[0]["components"][0]["symbol"] = "R911SymbolThatDoesNotExist"
    with pytest.raises(ValueError, match="Símbolo inexistente"):
        builder.validate_atlas(source_architectures, ROOT)


@pytest.mark.parametrize("field,value", [
    ("source", "component_not_in_diagram"),
    ("target", "component_not_in_diagram"),
    ("kind", "assumed_automatic_execution"),
])
def test_rejects_invalid_edge_endpoint_or_kind(builder, source_architectures, field, value):
    source_architectures[0]["edges"][0][field] = value
    with pytest.raises(ValueError, match="Extremo ou tipo"):
        builder.validate_atlas(source_architectures, ROOT)


@pytest.mark.parametrize("decision_after", [0, 1, 4, 6])
def test_rejects_gate_outside_intermediate_contract(builder, source_architectures, decision_after):
    source_architectures[0]["flow"]["decision_after"] = decision_after
    with pytest.raises(ValueError, match="decisão intermediária"):
        builder.validate_atlas(source_architectures, ROOT)


@pytest.mark.parametrize("decision_after", [2, 3])
def test_decision_is_one_based_and_precedes_next_step(builder, source_architectures, decision_after):
    entry = deepcopy(source_architectures[0])
    entry["flow"]["decision_after"] = decision_after
    rendered = builder.flow(entry)
    declared = re.findall(r"\\node\[[^\n]*?\]\s+\((s\d+|decision|refusal)\)", rendered)
    # s0 representa o primeiro passo. Após N passos, o gate antecede sN.
    assert declared.index(f"s{decision_after - 1}") < declared.index("decision")
    assert declared.index("decision") < declared.index(f"s{decision_after}")


@pytest.mark.parametrize("decision_after", [2, 3])
def test_flow_labels_yes_and_no_without_implicit_retry(builder, source_architectures, decision_after):
    entry = deepcopy(source_architectures[0])
    entry["flow"]["decision_after"] = decision_after
    rendered = builder.flow(entry)
    draws = [line for line in rendered.splitlines() if line.lstrip().startswith(r"\draw")]
    continuation = [line for line in draws if "(decision" in line and f"(s{decision_after}" in line]
    refusal = [line for line in draws if "(decision" in line and "(refusal" in line]
    assert len(continuation) == 1
    assert re.search(r"\{\s*sim\s*\}", continuation[0])
    assert len(refusal) == 1
    assert re.search(r"\{\s*não\s*\}", refusal[0])
    assert not any(re.search(r"\(refusal(?:\.[\w]+)?\).*\(decision", line) for line in draws)


def test_published_integral_exports_preserve_snapshot_independently(snapshot):
    expected_nodes, expected_pairs = _expected(snapshot)
    dot = (STATIC / "dependencies.dot").read_text()
    mermaid = (STATIC / "dependencies.mmd").read_text()
    correspondence = json.loads((STATIC / "mermaid-correspondence.json").read_text())
    _assert_graph_conserved(*_dot_graph(dot), expected_nodes, expected_pairs)
    _assert_graph_conserved(*_mermaid_graph(mermaid), expected_nodes, expected_pairs)
    _assert_graph_conserved([node["id"] for node in correspondence["nodes"]],
                            [(pair["source_id"], pair["target_id"]) for pair in correspondence["pairs"]],
                            expected_nodes, expected_pairs)
    expected_metadata = {(m["id"], m["module"], m["path"], m["sha256"]) for m in snapshot["modules"]}
    actual_metadata = {(m["id"], m["module"], m["path"], m["sha256"]) for m in correspondence["nodes"]}
    assert actual_metadata == expected_metadata
    # Pares únicos não podem apagar declarações AST repetidas em linhas diferentes.
    declarations = [edge for pair in correspondence["pairs"] for edge in pair["declarations"]]
    normalize = lambda rows: Counter(tuple(sorted(row.items())) for row in rows)
    assert normalize(declarations) == normalize(snapshot["edges"])
    assert correspondence["mermaid_sha256"] == hashlib.sha256(mermaid.encode()).hexdigest()
    assert correspondence["source_git"] == snapshot["git"]
    assert correspondence["counts"]["modules"] == len(expected_nodes)
    assert correspondence["counts"]["module_pairs"] == len(expected_pairs)
    assert correspondence["counts"]["ast_declarations"] == len(snapshot["edges"])


def test_snapshot_isolates_are_visible_in_all_formats(snapshot):
    expected_nodes, pairs = _expected(snapshot)
    incident = {node for pair in pairs for node in pair}
    isolates = expected_nodes - incident
    assert isolates, "Este snapshot contém módulos isolados e deve conservá-los"
    dot_nodes, _ = _dot_graph((STATIC / "dependencies.dot").read_text())
    mermaid_nodes, _ = _mermaid_graph((STATIC / "dependencies.mmd").read_text())
    manifest_nodes = {node["id"] for node in json.loads((STATIC / "mermaid-correspondence.json").read_text())["nodes"]}
    assert isolates <= set(dot_nodes)
    assert isolates <= set(mermaid_nodes)
    assert isolates <= manifest_nodes


def test_rendered_svg_preserves_every_node_and_pair(snapshot):
    graph = ET.parse(STATIC / "dependencies.svg").getroot()
    ns = {"s": "http://www.w3.org/2000/svg"}
    nodes, pairs = [], []
    for group in graph.findall(".//s:g", ns):
        title = group.find("s:title", ns)
        if group.get("class") == "node":
            nodes.append(title.text)
        elif group.get("class") == "edge":
            pairs.append(tuple(title.text.split("->")))
    _assert_graph_conserved(nodes, pairs, *_expected(snapshot))


def test_legend_is_separate_from_architecture(snapshot):
    mermaid = (STATIC / "dependencies.mmd").read_text()
    correspondence = json.loads((STATIC / "mermaid-correspondence.json").read_text())
    legend = re.search(r'  subgraph legend\["(.*?)\n  end', mermaid, flags=re.S)
    assert legend is not None
    assert "fora das contagens" in legend.group(1)
    assert "leg_importador" in legend.group(1) and "leg_dependencia" in legend.group(1)
    assert not re.search(NODE, legend.group(1))
    assert correspondence["legend_counted_as_architecture"] is False
    assert correspondence["counts"]["modules"] == len(snapshot["modules"])


def test_exporters_keep_isolated_module_and_two_declarations_of_one_pair(exporters):
    dot_exporter, mermaid_exporter = exporters
    modules = [{"id": f"n_{index:020x}", "module": name, "path": name + ".py",
                "package": "fixture", "layer": "fixture", "sha256": "0" * 64, "symbols": []}
               for index, name in enumerate(("alpha", "beta", "isolated"), start=1)]
    edges = [{"source_id": modules[0]["id"], "target_id": modules[1]["id"],
              "source": "alpha", "target": "beta", "path": "alpha.py", "line": line,
              "kind": "declared_import"} for line in (2, 9)]
    sample = {"modules": modules, "edges": edges, "git": {"commit": "a" * 40}, "limitations": []}
    expected_nodes = {f"n_{index:020x}" for index in (1, 2, 3)}
    expected_pairs = {(f"n_{1:020x}", f"n_{2:020x}")}
    _assert_graph_conserved(*_dot_graph(dot_exporter._dot(sample, overview=False)), expected_nodes, expected_pairs)
    mermaid = mermaid_exporter.render_mermaid(sample)
    _assert_graph_conserved(*_mermaid_graph(mermaid), expected_nodes, expected_pairs)
    manifest = mermaid_exporter.build_correspondence(sample, mermaid)
    assert len(manifest["nodes"]) == 3
    assert manifest["counts"]["module_pairs"] == 1
    assert manifest["counts"]["ast_declarations"] == 2
    assert [row["line"] for row in manifest["pairs"][0]["declarations"]] == [2, 9]
    isolated_declaration = next(line for line in mermaid.splitlines()
                                if line.lstrip().startswith(modules[2]["id"] + '["'))
    with pytest.raises(ValueError, match="diverge"):
        mermaid_exporter.build_correspondence(sample, mermaid.replace(isolated_declaration + "\n", ""))


def test_layer_matrix_accounts_for_every_snapshot_declaration(builder, snapshot):
    _, ledger = builder.layer_matrix(snapshot)
    layer_by_module = {module["module"]: module["layer"] for module in snapshot["modules"]}
    expected = Counter((layer_by_module[edge["source"]], layer_by_module[edge["target"]])
                       for edge in snapshot["edges"])
    actual = {(row["source"], row["target"]): row["declarations"] for row in ledger["counts"]}
    assert actual == dict(expected)
    assert sum(actual.values()) == len(snapshot["edges"])
    assert ledger["module_count"] == len(snapshot["modules"])
    assert set(ledger["layers"]) == set(layer_by_module.values())



def test_manifest_and_every_local_view_reproduce_authoritative_data(builder, source_architectures):
    manifest = json.loads((ATLAS / "architectures.json").read_text())
    published = manifest["architectures"]
    assert manifest["revision"] == "R911"
    assert manifest["static_layers_are_different_taxonomy"] is True
    assert len(published) == len(source_architectures)
    published_by_id = {entry["id"]: entry for entry in published}
    for source in source_architectures:
        entry = published_by_id[source["id"]]
        assert {key: value for key, value in entry.items() if key != "views"} == source
        for kind, filename in entry["views"].items():
            assert (ATLAS / filename).read_text() == builder.page(source, kind)


def test_global_views_and_matrix_reproduce_sources(builder, source_architectures, snapshot):
    published = (ATLAS / "global.tex").read_text()
    expected, ledger = builder.global_atlas(source_architectures, snapshot)
    assert published == expected
    assert json.loads((ATLAS / "layer-relations.json").read_text()) == ledger
    mental = builder.panorama(source_architectures)
    # Exigir IDs no mapa propriamente dito, não apenas no índice de navegação.
    assert Counter(re.findall(r"\bAR\d{2}(?=:)", mental)) == Counter({f"AR{i:02}": 1 for i in range(1, 19)})
    assert mental in published
    assert builder.process_map() in published
    assert builder.global_flow() in published
    matrix, matrix_ledger = builder.layer_matrix(snapshot)
    assert matrix in published
    assert len(matrix_ledger["layers"]) == 18
    for view in ("mental", "processes", "flow", "matrix"):
        assert r"\label{fig:global-" + view + "}" in published
    assert "instâncias próprias" in published
    assert "não uma única instância distribuída" in published


def test_lean_context_custody_includes_atlas_and_method_but_not_runtime_outputs():
    verifier = _module("r911_lean_custody", "scripts/verify_book_lean.py")
    context = {path.resolve().relative_to(ROOT) for path in verifier.context_sources()}
    expected = {path.relative_to(ROOT) for pattern in ("*.json", "*.tex")
                for path in ATLAS.glob(pattern)}
    expected.update(map(Path, (
        "livro-core/gen_architecture_atlas.py",
        "tests/test_r911_book_architecture_atlas.py",
        "specs/SPEC-935-R911-atlas-arquiteturas-livro.md",
        "docs/ARQUITETURAS_LIVRO_R911.md",
        "docs/superpowers/plans/2026-10-16-atlas-arquiteturas.md",
        "docs/architecture-r911/architecture-inventory.json",
    )))
    assert expected <= context
    assert not any("outputs" in path.parts or ".lake" in path.parts for path in context)


def test_changed_atlas_json_invalidates_custody_receipt(tmp_path):
    verifier = _module("r911_lean_receipt_fixture", "scripts/verify_book_lean.py")
    relative = Path("livro-core/atlas/data-orchestration.json")
    copied = tmp_path / relative
    copied.parent.mkdir(parents=True)
    source = json.loads((ROOT / relative).read_text())
    copied.write_text(json.dumps(source, ensure_ascii=False))
    # Fixture exclusivamente de custódia: não declara nova execução nem prova Lean.
    receipt = {"status": "fixture_custody_only", "context_files": {
        relative.as_posix(): {"sha256": verifier.file_sha256(copied)}
    }}
    assert verifier.receipt_matches_sources(receipt, tmp_path) is True
    source[0]["title"] += " — alteração posterior ao recibo"
    copied.write_text(json.dumps(source, ensure_ascii=False))
    assert verifier.receipt_matches_sources(receipt, tmp_path) is False
