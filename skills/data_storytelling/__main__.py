# -*- coding: utf-8 -*-
"""CLI do Data Storytelling Auditável (SPEC-935-R1003).

    python3 -m skills.data_storytelling demo --out DIR
    python3 -m skills.data_storytelling audit spec.json
    python3 -m skills.data_storytelling caption spec.json --number 1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import (
    audit_chart,
    build_manifest,
    caption_from_spec,
    profile_dataset,
    recommend_chart,
    render_svg,
)
from .util import LIMITS, SCHEMA_VERSION

DEMO_ROWS = [
    {"ano": 2020, "cobertura": 41},
    {"ano": 2021, "cobertura": 52},
    {"ano": 2022, "cobertura": 63},
    {"ano": 2023, "cobertura": 74},
    {"ano": 2024, "cobertura": 83},
]

DEMO_SPEC: dict[str, Any] = {
    "chart": "bar",
    "title": "Cobertura passa de 41% para 83% em quatro anos",
    "subtitle": "Percentual de municípios com cobertura declarada, 2020–2024",
    "claim": "A cobertura passou de 41% para 83% entre 2020 e 2024.",
    "source": "Dados sintéticos (2024)",
    "note": (
        "Série sintética para demonstração; n = 5; período 2020–2024; "
        "nenhum dado real é usado."
    ),
    "legend": "Barras azuis: cobertura anual.",
    "alt_text": "Barras anuais de 41% em 2020 a 83% em 2024.",
    "sample_n": 5,
    "y": {"kind": "numeric", "zero": True, "unit": "%", "scale": "linear"},
    "x": {"kind": "temporal"},
    "category_count": 5,
    "series_count": 1,
    "design": "simulation",
    "sorting": "ascending",
    "intent": "comparison",
    "decimals": 0,
    "data": [
        {"label": "2020", "value": 41},
        {"label": "2021", "value": 52},
        {"label": "2022", "value": 63},
        {"label": "2023", "value": 74},
        {"label": "2024", "value": 83},
    ],
}


def _write_json(path: Path, payload: Any) -> str:
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")
    return text


def run_demo(out: Path) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    profile = profile_dataset(DEMO_ROWS)
    recommendation = recommend_chart(profile, intent="comparison")
    audit = audit_chart(DEMO_SPEC)
    if audit["status"] != "approved":
        raise SystemExit(
            "Demonstração reprovada na auditoria: "
            + json.dumps(audit["findings"], ensure_ascii=False)
        )
    caption = caption_from_spec(DEMO_SPEC, number=1, kind="Gráfico")
    svg = render_svg(DEMO_SPEC)

    dossier = {
        "schema_version": SCHEMA_VERSION,
        "kind": "data_storytelling_dossier",
        "spec": DEMO_SPEC,
        "profile": profile,
        "recommendation": recommendation,
        "audit": audit,
        "caption": caption,
        "limits": list(LIMITS),
    }

    artifacts: dict[str, str] = {}
    artifacts["dossie.json"] = _write_json(out / "dossie.json", dossier)
    artifacts["auditoria.json"] = _write_json(out / "auditoria.json", audit)
    artifacts["grafico.svg"] = svg
    (out / "grafico.svg").write_text(svg, encoding="utf-8")
    artifacts["legenda.md"] = caption["markdown"] + "\n"
    (out / "legenda.md").write_text(artifacts["legenda.md"], encoding="utf-8")

    manifest = build_manifest(
        artifacts,
        metadata={"spec": "SPEC-935-R1003", "demo": "dados sintéticos"},
    )
    _write_json(out / "MANIFESTO.json", manifest)
    return {
        "status": "ok",
        "out": str(out),
        "audit_status": audit["status"],
        "manifest_sha256": manifest["manifest_sha256"],
        "artifacts": [item["name"] for item in manifest["artifacts"]],
    }


def _load_spec(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("A especificação deve ser um objeto JSON.")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m skills.data_storytelling",
        description="Data storytelling auditável: perfil, gate, legenda, nota e selo.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("demo", help="Gera dossiê sintético verificável.")
    demo.add_argument("--out", type=Path, required=True, help="Diretório de saída.")

    audit = subparsers.add_parser("audit", help="Audita uma especificação JSON.")
    audit.add_argument("spec", type=Path)
    audit.add_argument("--json", action="store_true", help="Saída JSON (padrão).")

    caption = subparsers.add_parser("caption", help="Gera legenda de uma especificação.")
    caption.add_argument("spec", type=Path)
    caption.add_argument("--number", default="1")
    caption.add_argument("--kind", default="Gráfico")

    args = parser.parse_args(argv)
    if args.command == "demo":
        print(json.dumps(run_demo(args.out), ensure_ascii=False, indent=2))
        return 0
    if args.command == "audit":
        report = audit_chart(_load_spec(args.spec))
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if report["status"] in {"approved", "pass_with_notes"} else 1
    if args.command == "caption":
        bundle = caption_from_spec(
            _load_spec(args.spec), number=args.number, kind=args.kind
        )
        print(bundle["markdown"])
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
