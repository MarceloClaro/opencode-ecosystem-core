#!/usr/bin/env python3
"""R1125: manifesto, simulação e análise de CB; nenhum acesso ao hardware."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from quantum_mitigation.cycle_benchmarking import (
    PAULIS_2Q, analyze_cycle_benchmarking, build_manifest, simulate_manifest,
)
from quantum_mitigation.cb_rank_bounds import audit as rank_audit
from quantum_mitigation.cb_learnability import audit as learnability_audit
from quantum_mitigation.interleaved_cb import (
    audit as interleaved_audit,
    build_preregistration,
    noise_audit as interleaved_noise_audit,
)


def read_json_strict(path: Path) -> dict:
    """Rejeita entradas ambíguas antes de perder informação no parser."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"chave JSON duplicada: {key}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError(f"constante JSON não finita: {value}")

    if path.stat().st_size > 16*1024*1024:
        raise ValueError("JSON excede orçamento local de 16 MiB")
    result = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                        parse_constant=invalid_constant)
    if not isinstance(result, dict):
        raise ValueError("objeto JSON exigido")
    return result


def _write_new(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8") as stream:
        stream.write(text)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "plan",
            "simulate",
            "analyze",
            "rank",
            "learnability",
            "interleaved",
            "interleaved-noise",
            "preregister",
        ),
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--data", type=Path)
    parser.add_argument("--bootstrap", type=int, default=200)
    args = parser.parse_args(argv)
    try:
        if args.out.exists():
            raise FileExistsError("destino existente; escolha outro, não sobrescrever evidência")
        if args.command == "plan":
            payload = build_manifest()
        elif args.command == "rank":
            payload = rank_audit()
        elif args.command == "learnability":
            payload = learnability_audit()
        elif args.command == "interleaved":
            payload = interleaved_audit()
        elif args.command == "interleaved-noise":
            payload = interleaved_noise_audit()
        elif args.command == "preregister":
            payload = build_preregistration()
        else:
            if args.manifest is None:
                raise ValueError("--manifest obrigatório")
            manifest = read_json_strict(args.manifest)
            if args.command == "simulate":
                # Modelo sintético declarado, não substitui counts reais.
                rates = {p: (i+1)*.0002 for i, p in enumerate(PAULIS_2Q)}
                payload = simulate_manifest(manifest, rates)
            else:
                if args.data is None:
                    raise ValueError("--data obrigatório")
                data = read_json_strict(args.data)
                payload = analyze_cycle_benchmarking(manifest, data, n_bootstrap=args.bootstrap)
        _write_new(args.out, payload)
        print(json.dumps({"status": "written", "path": str(args.out),
                          "hardware_executed": False, "pec_hardware_allowed": False}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc), "hardware_executed": False}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
