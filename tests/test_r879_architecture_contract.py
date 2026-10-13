"""Conferência cruzada dos mapas reais com o snapshot que declaram."""
import ast
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "docs/architecture"


def read_blob(ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT,
                          capture_output=True, check=True).stdout.decode("utf-8")


def test_fluxos_correspondem_a_ancoras_reais_do_snapshot():
    inventory = json.loads((MAPS / "architecture-inventory.json").read_text())
    flows = json.loads((MAPS / "flows.json").read_text())["flows"]
    assert len({f["id"] for f in flows}) == 13
    parsed = {}
    for flow in flows:
        assert (MAPS / flow["file"]).is_file()
        assert flow["sources"] and flow["limitations"]
        for source in flow["sources"]:
            path = source["path"]
            assert not path.startswith((".mci_state/", ".opencode/rea/", "outputs/"))
            if path not in parsed:
                text = read_blob(inventory["git"]["commit"], path)
                tree = ast.parse(text) if path.endswith(".py") else None
                parsed[path] = (text, tree)
            text, tree = parsed[path]
            assert 1 <= source["line"] <= len(text.splitlines())
            if source.get("symbol") and tree is not None:
                name = source["symbol"].split(".")[-1]
                matches = [n for n in ast.walk(tree) if isinstance(
                    n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
                ) and n.name == name and n.lineno == source["line"]]
                assert matches, source


def test_html_embute_os_mesmos_catalogos_sem_dados_antigos():
    page = (ROOT / "docs/architecture_map.html").read_text()
    for identifier, file in [("inventory-data", "architecture-inventory.json"),
                             ("flows-data", "flows.json")]:
        match = re.search(rf'<script id="{identifier}" type="application/json">(.*?)</script>',
                          page, re.DOTALL)
        assert match
        expected = json.loads((MAPS / file).read_text())
        if identifier == "flows-data":
            expected = expected["flows"]
        assert json.loads(match.group(1)) == expected


def test_svg_completo_nao_omite_modulos_ou_pares_internos():
    inventory = json.loads((MAPS / "architecture-inventory.json").read_text())
    svg = ET.parse(MAPS / "dependencies.svg")
    groups = [g for g in svg.iter() if g.tag.endswith("}g")]
    nodes = [g for g in groups if g.get("class") == "node"]
    edges = [g for g in groups if g.get("class") == "edge"]
    assert {g.get("id") for g in nodes} == {m["id"] for m in inventory["modules"]}
    expected_pairs = {(e["source"], e["target"]) for e in inventory["edges"]}
    assert len(edges) == len(expected_pairs)
