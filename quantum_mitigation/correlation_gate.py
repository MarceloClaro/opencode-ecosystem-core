"""R1147 — gate de contraprovas de correlação em Lean 4 + Mathlib.

Reutiliza o gate generalizado de R1146, mas com o arquivo, os teoremas, as
contraprovas e as alegações da correlação. Fail-closed: sem compilação, sem
contraprova ou com axioma nativo, o gate não aceita.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import complex_proof_gate as base

CORRELATION_FILE = base.ROOT / "lean" / "quantum-cb" / "CorrelationCounterproof.lean"
CORRELATION_LOG = base.ROOT / "lean" / "quantum-cb" / "correlation_compile.log"
CORRELATION_OUTPUT = (
    base.ROOT
    / "harnesses"
    / "quantum-error-mitigation"
    / "resultados"
    / "r1147_correlation_layout"
    / "certificate.json"
)

CORRELATION_REQUIRED = (
    "marginals_equal",
    "joints_differ",
    "covariance_A_positive",
    "covariance_B_not_positive",
    "no_error_A_gt_B",
    "double_error_A_gt_B",
    "any_error_A_lt_B",
    "any_error_direction_reverses",
    "union_bound_not_tight",
    "marginals_do_not_determine_joint",
)
CORRELATION_COUNTERPROOFS = (
    "joints_differ",
    "covariance_B_not_positive",
    "any_error_direction_reverses",
)
CORRELATION_CLAIMS = (
    {
        "id": "identifiability",
        "theorem": "marginals_do_not_determine_joint",
        "counterproof": "joints_differ",
        "kind": "correlation",
    },
    {
        "id": "covariance_sign",
        "theorem": "covariance_A_positive",
        "counterproof": "covariance_B_not_positive",
        "kind": "correlation",
    },
    {
        "id": "fidelity_direction",
        "theorem": "no_error_A_gt_B",
        "counterproof": "any_error_direction_reverses",
        "kind": "direction",
    },
    {
        "id": "union_bound",
        "theorem": "union_bound_not_tight",
        "counterproof": "any_error_direction_reverses",
        "kind": "bound",
    },
)

LIMITS = (
    "Contraprova de correlação clássica em ℚ; não prova hardware, ruído real, "
    "crosstalk, drift ou vantagem. Mostra que marginais não determinam a junta "
    "e que a direção do erro do modelo independente depende do estatístico. "
    "O pareamento alegação↔contraprova é editorial e exige revisão humana."
)


def audit(claims=None, **kwargs) -> dict:
    return base.audit(
        CORRELATION_CLAIMS if claims is None else claims,
        lean_file=CORRELATION_FILE,
        required_theorems=CORRELATION_REQUIRED,
        counterproofs=CORRELATION_COUNTERPROOFS,
        round_id="R1147",
        limits=LIMITS,
        output=CORRELATION_OUTPUT,
        log_path=CORRELATION_LOG,
        **kwargs,
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Gate de contraprova de correlação (R1147)."
    )
    parser.add_argument("--no-compile", action="store_true")
    parser.add_argument("--timeout", type=int, default=1200)
    args = parser.parse_args(argv)
    report = audit(
        run_compile=not args.no_compile,
        write=True,
        timeout=args.timeout,
    )
    summary = {
        "gate": report["gate"],
        "compile": {
            key: report["compile"].get(key)
            for key in ("status", "returncode", "elapsed_seconds")
        },
        "claims": report["claims"],
        "certificate": report.get("certificate"),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if report["gate"]["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
