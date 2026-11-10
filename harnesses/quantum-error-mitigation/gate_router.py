#!/usr/bin/env python3
"""R1138: roteia um gate bloqueado para rota e evidência necessária.

Não executa hardware. Sem `--evidence`, mostra o estado fail-closed e os
campos que precisam ser preenchidos. Com evidência JSON, avalia a política.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from quantum_mitigation.gate_policy import evaluate

ROUTES = {
    "pec_2q": {
        "route": "GSPN/MLCB + gauge optimization",
        "evidence": ["gspn_model_validated", "heldout_error", "sampling_overhead"],
        "sources": ["10.1103/1pnv-t9px", "10.1103/4hbl-hpl3", "10.1103/69wc-gzl6"],
    },
    "zne": {
        "route": "layerwise Richardson extrapolation (LRE)",
        "evidence": ["lre_configurations", "residual", "heldout_stable"],
        "sources": ["10.1103/PhysRevA.110.062420"],
    },
    "layout": {
        "route": "paired randomized layout design",
        "evidence": ["n_pairs", "n_required", "randomized", "r1", "drift_resolved", "effect"],
        "sources": ["R1120", "R1124", "R1133"],
    },
    "cuts": {
        "route": "gauge; GSPN + MLCB, not direct identification",
        "evidence": ["gspn_self_consistent", "mlcb_applied"],
        "sources": ["10.1103/1pnv-t9px", "10.1103/4hbl-hpl3", "10.1103/69wc-gzl6"],
    },
}


def route(gate: str, evidence: dict | None = None) -> dict:
    if gate not in ROUTES:
        raise ValueError("gate deve ser pec_2q, zne, layout ou cuts")
    status = evaluate(evidence or {})[gate]
    return {
        "schema_version": 1,
        "gate": gate,
        "status": status,
        "route": ROUTES[gate]["route"],
        "required_evidence": ROUTES[gate]["evidence"],
        "sources": ROUTES[gate]["sources"],
        "hardware_executed": False,
        "rates_measured": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", required=True, choices=sorted(ROUTES))
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        evidence = None
        if args.evidence is not None:
            evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
            if not isinstance(evidence, dict):
                raise ValueError("evidência deve ser objeto JSON")
        payload = route(args.gate, evidence)
        text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        if args.out is not None:
            if args.out.exists():
                raise FileExistsError("destino existente; escolha outro")
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(text, encoding="utf-8")
        print(text, end="")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
