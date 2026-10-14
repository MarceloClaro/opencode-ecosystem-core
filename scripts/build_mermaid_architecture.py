#!/usr/bin/env python3
"""R881: exportação determinística e sem perdas do inventário Git/AST."""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

NODE_ID = re.compile(r"n_[a-f0-9]{20}\Z")
COLORS = ("#e2f4f5", "#edf0f7", "#fff1dd", "#e9f3e5", "#f3e8f4", "#fce9e6")


def _json(value: object) -> str:
    text = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    # Even inside comments, never expose raw Mermaid directives or HTML tags.
    return text.replace("%", "\\u0025").replace("<", "\\u003c").replace(">", "\\u003e")


def _label(value: str) -> str:
    named = {'"': "quot", "<": "lt", ">": "gt", "&": "amp"}
    return "".join(
        f"#{named[char]};" if char in named else
        f"#{ord(char)};" if char in "#[]{}%\\\n\r\t" else char
        for char in str(value)
    )


def _normalized(snapshot: dict) -> tuple[list, dict]:
    modules = sorted(snapshot["modules"], key=lambda item: item["path"])
    identifiers, paths, names = set(), set(), set()
    for module in modules:
        identifier, path, name = module["id"], module["path"], module["module"]
        if not NODE_ID.fullmatch(identifier) or identifier in identifiers or path in paths or name in names:
            raise ValueError("Módulo com identificador, caminho ou nome inválido/duplicado.")
        identifiers.add(identifier)
        paths.add(path)
        names.add(name)
    indexed = {module["id"]: module for module in modules}
    pairs = defaultdict(list)
    for edge in snapshot["edges"]:
        source, target = edge["source_id"], edge["target_id"]
        if source not in indexed or target not in indexed:
            raise ValueError("Dependência aponta para módulo desconhecido.")
        if (edge["source"] != indexed[source]["module"] or
                edge["target"] != indexed[target]["module"] or
                edge["path"] != indexed[source]["path"] or
                edge["kind"] != "declared_import" or
                type(edge["line"]) is not int or edge["line"] < 1):
            raise ValueError("Declaração incompatível com seus módulos de origem/destino.")
        pairs[(source, target)].append(edge)
    return modules, {pair: sorted(declarations, key=lambda d: (d["line"], _json(d)))
                     for pair, declarations in sorted(pairs.items())}


def _counts(modules: list, pairs: dict) -> dict:
    return {"modules": len(modules), "module_pairs": len(pairs),
            "ast_declarations": sum(map(len, pairs.values())),
            "symbols": sum(len(m.get("symbols", [])) for m in modules),
            "packages": len({m["package"] for m in modules}),
            "layers": len({m["layer"] for m in modules})}


def render_mermaid(snapshot: dict) -> str:
    modules, pairs = _normalized(snapshot)
    layers = sorted({module["layer"] for module in modules})
    layer_index = {layer: index for index, layer in enumerate(layers)}
    counts = _counts(modules, pairs)
    lines = [
        "%% R881 — inventário estrutural integral; sem inferência de execução.",
        "%% snapshot " + _json(snapshot["git"]),
        "%% counts " + _json(counts),
        "%% Renderização integral: usar mermaid-render-config.json (maxEdges/maxTextSize).",
        "flowchart LR",
    ]
    for module in modules:
        lines.append("%% module-metadata " + _json(module))
    for (source, target), declarations in pairs.items():
        lines.append("%% edge-metadata " + _json({"source_id": source, "target_id": target,
                                                   "declarations": declarations}))
    packages = defaultdict(list)
    for module in modules:
        packages[module["package"]].append(module)
    for package, members in sorted(packages.items()):
        package_id = "pkg_" + hashlib.sha256(package.encode()).hexdigest()[:20]
        package_layers = ", ".join(sorted({m["layer"] for m in members}))
        lines.append(f'  subgraph {package_id}["{_label(package)} — {_label(package_layers)}"]')
        for module in members:
            symbols = module.get("symbols", [])
            classes = sum(s["kind"] == "class" for s in symbols)
            functions = len(symbols) - classes
            label = f'{_label(module["path"])}<br/>{classes} classes · {functions} funções'
            lines.append(f'    {module["id"]}["{label}"]:::layer{layer_index[module["layer"]]}')
        lines.append("  end")
    for source, target in pairs:
        lines.append(f"  {source} --> {target}")
    lines.extend([
        '  subgraph legend["Legenda — fora das contagens da arquitetura"]',
        '    leg_importador["Módulo importador"] --> leg_dependencia["Dependência declarada"]',
        '    leg_isolado["Módulo isolado: preservado mesmo sem par interno"]',
        f'    leg_contagens["{counts["modules"]} módulos · {counts["module_pairs"]} pares · {counts["ast_declarations"]} declarações AST"]',
        f'    leg_simbolos["{counts["symbols"]} símbolos nos comentários JSON; classes/funções nos rótulos"]',
        '    leg_limites["Import estático não comprova chamada, autenticação, inferência ou qualidade"]',
        '    leg_escopo["Escopo Python de produção; vendor, história, testes e superfícies lexicais fora deste grafo"]',
        '    leg_fonte["Fonte: architecture-inventory.json; IDs e hashes preservados nos metadados"]',
    ])
    for layer in layers:
        index = layer_index[layer]
        lines.append(f'    leg_layer{index}["Camada: {_label(layer)}"]:::layer{index}')
    lines.append("  end")
    for index in range(len(layers)):
        lines.append(f"  classDef layer{index} fill:{COLORS[index % len(COLORS)]},stroke:#41677a,color:#102d3a")
    for limitation in snapshot.get("limitations", []):
        lines.append("%% limitation " + _json(limitation))
    return "\n".join(lines) + "\n"


def build_correspondence(snapshot: dict, mermaid_text: str) -> dict:
    # Canonical comparison rejects omissions, changed metadata and directives.
    # Cross-format graph sets are independently compared in the regression test.
    if mermaid_text != render_mermaid(snapshot):
        raise ValueError("Mermaid diverge da exportação integral canônica.")
    modules, pairs = _normalized(snapshot)
    return {
        "schema_version": "r881.v1", "source_git": snapshot["git"],
        "counts": _counts(modules, pairs),
        "mermaid_sha256": hashlib.sha256(mermaid_text.encode()).hexdigest(),
        "nodes": [{"id": m["id"], "path": m["path"], "module": m["module"],
                   "sha256": m["sha256"]} for m in modules],
        "pairs": [{"source_id": source, "target_id": target,
                   "declarations": declarations} for (source, target), declarations in pairs.items()],
        "legend_counted_as_architecture": False,
        "scope": "Importações Python declaradas no snapshot, sem atestar execução.",
    }


def write_artifacts(snapshot, output, *, check=False, correspondence=None):
    output = Path(output)
    if correspondence is not None and output.resolve() == Path(correspondence).resolve():
        raise ValueError("Mermaid e manifesto precisam de destinos distintos.")
    text = render_mermaid(snapshot)
    manifest = build_correspondence(snapshot, text)
    expected = {output: text.encode("utf-8")}
    if correspondence is not None:
        expected[Path(correspondence)] = (json.dumps(manifest, ensure_ascii=False,
                                                     sort_keys=True, indent=2) + "\n").encode("utf-8")
    if check:
        if any(not path.is_file() or path.read_bytes() != content for path, content in expected.items()):
            raise ValueError("Artefato ausente ou divergente; regenere a partir do inventário.")
    else:
        for path, content in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--correspondence", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        snapshot = json.loads(args.inventory.read_text(encoding="utf-8"))
        manifest = write_artifacts(snapshot, args.output, check=args.check,
                                   correspondence=args.correspondence)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Erro de exportação: {error}", file=sys.stderr)
        return 1
    print(json.dumps(manifest["counts"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
