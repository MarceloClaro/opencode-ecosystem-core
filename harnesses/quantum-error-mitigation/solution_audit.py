#!/usr/bin/env python3
"""R1132-R1134: auditoria offline das rotas de desbloqueio.

Gera LRE, desenho pareado de layouts e auditoria gauge/PEC. Não executa
hardware, não acessa rede e não sobrescreve evidência.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from quantum_mitigation.gate_policy import evaluate as gate_evaluate
from quantum_mitigation.layout_design import build_preregistration
from quantum_mitigation.lre import synthetic_audit
from quantum_mitigation.solution_audit import audit as gauge_audit


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.out.exists():
            raise FileExistsError("destino existente; escolha outro")
        payload = {
            "schema_version": 1,
            "lre": synthetic_audit(),
            "layout": build_preregistration(n_pairs=32),
            "gauge_pec": gauge_audit(),
            "gates": gate_evaluate({}),
            "hardware_executed": False,
            "rates_measured": False,
            "limits": (
                "Rotas metodológicas offline; nenhuma execução no Baihua. "
                "PEC 2q, ZNE e layouts continuam condicionados a dados."
            ),
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "status": "written",
                    "path": str(args.out),
                    "hardware_executed": False,
                },
                ensure_ascii=False,
            )
        )
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
