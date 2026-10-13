"""Monta a página offline a partir de inventário Git e SVGs locais R879."""
from __future__ import annotations

import argparse
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inert_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True).replace(
        "<", "\\u003c"
    ).replace(">", "\\u003e").replace("&", "\\u0026")


def checked_svg(text):
    text = re.sub(r"<\?xml.*?\?>", "", text, flags=re.DOTALL)
    text = re.sub(r"<!DOCTYPE[^>]*>", "", text, flags=re.DOTALL)
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise ValueError("SVG malformado") from exc
    if root.tag.split("}")[-1] != "svg":
        raise ValueError("Documento não é SVG")
    for node in root.iter():
        if node.tag.split("}")[-1].lower() in {"script", "image", "iframe", "object", "embed"}:
            raise ValueError("SVG contém código ativo ou recurso externo")
        for name, value in node.attrib.items():
            key = name.split("}")[-1].lower()
            if key.startswith("on"):
                raise ValueError("SVG contém handler ativo")
            if key in {"href", "src"} and not value.startswith("#"):
                raise ValueError("SVG referencia recurso fora do documento")
            if re.search(r"url\(\s*[\"']?(?!#)[\w/:]", value, re.IGNORECASE):
                raise ValueError("SVG contém URL externa")
        if node.text and re.search(r"@import|url\(\s*[\"']?(?!#)[\w/:]", node.text, re.IGNORECASE):
            raise ValueError("SVG contém CSS externo")
    return text.strip()


def render_page(inventory, overview_svg, dependencies_svg, flows):
    template = (ROOT / "docs/architecture/viewer-template.html").read_text()
    options, templates, metadata = [], [], []
    for flow in flows:
        identifier = flow["id"]
        if not re.fullmatch(r"[a-z0-9_-]+", identifier):
            raise ValueError("Identificador de fluxo inválido")
        options.append(f'<option value="{identifier}">{html.escape(flow["title"])}</option>')
        templates.append(f'<template id="flow-{identifier}">{checked_svg(flow["svg"])}</template>')
        metadata.append({k: v for k, v in flow.items() if k != "svg"})
    replacements = {"__SNAPSHOT_JSON__": inert_json(inventory), "__FLOWS_JSON__": inert_json(metadata),
                    "__OVERVIEW_SVG__": checked_svg(overview_svg),
                    "__DEPENDENCIES_SVG__": checked_svg(dependencies_svg),
                    "__FLOW_OPTIONS__": "\n".join(options), "__FLOW_TEMPLATES__": "\n".join(templates)}
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    return template


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT / "docs/architecture")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/architecture_map.html")
    args = parser.parse_args()
    folder = args.directory
    inventory = json.loads((folder / "architecture-inventory.json").read_text())
    flows = json.loads((folder / "flows.json").read_text())["flows"]
    for flow in flows:
        flow["svg"] = (folder / flow["file"]).with_suffix(".svg").read_text()
    overview = folder / "curated-overview.svg"
    if not overview.is_file():
        overview = folder / "overview.svg"
    content = render_page(inventory, overview.read_text(),
                          (folder / "dependencies.svg").read_text(), flows)
    args.output.write_text(content, encoding="utf-8")
    print(f"Página local: {args.output}; {len(flows)} fluxos; {len(content.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
