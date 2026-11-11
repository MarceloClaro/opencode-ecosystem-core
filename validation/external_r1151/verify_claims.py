#!/usr/bin/env python3
"""R1151 — verificação automatizada independente do pacote de validação.

Não é peer review, validação clínica ou de hardware. Confere:
- certificados Lean e hashes;
- hashes dos arquivos formais;
- relatório de catálogo e classificação de duplicatas;
- testes de runtime e N-of-1.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "validation" / "external_r1151"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def certificate_check(path: Path, theorem: str, counterproof: str, expected: str) -> dict:
    if not path.exists():
        return {"ok": False, "reason": "certificado ausente"}
    if sha256(path) != expected:
        return {"ok": False, "reason": "hash do certificado diverge"}
    certificate = json.loads(path.read_text(encoding="utf-8"))
    if not certificate.get("gate", {}).get("accepted"):
        return {"ok": False, "reason": "gate não aceitou"}
    axioms = certificate.get("axioms", {})
    statuses = {
        name: axioms.get(name, {}).get("classification", "not_reported")
        for name in (theorem, counterproof)
    }
    return {
        "ok": all(status == "kernel_checked" for status in statuses.values()),
        "statuses": statuses,
        "certificate_sha256": expected,
        "lean_file_sha256": certificate.get("lean_file", {}).get("sha256"),
    }


def test_check(paths: list[Path]) -> dict:
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.exists()]
    if missing:
        return {"ok": False, "reason": f"testes ausentes: {missing}"}
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *[str(path) for path in paths], "-q", "--tb=short"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "tail": (result.stdout or "").strip().splitlines()[-1:] or [],
    }


def main() -> int:
    claims = json.loads((PACKAGE / "claims.json").read_text(encoding="utf-8"))
    results = []
    for claim in claims["claims"]:
        claim_id = claim["id"]
        if claim_id == "formal_complex":
            check = certificate_check(
                ROOT / "harnesses/quantum-error-mitigation/resultados/r1146_complex_proofs/certificate.json",
                "interference",
                "relative_phase_not_one",
                "5bdad31fe568f8141b221ff4db4df2bbf50bad7f4da4f08ba687fdc86fb46168",
            )
            verdict = "supported" if check["ok"] else "insufficient"
            evidence = check
        elif claim_id == "formal_correlation":
            check = certificate_check(
                ROOT / "harnesses/quantum-error-mitigation/resultados/r1147_correlation_layout/certificate.json",
                "marginals_do_not_determine_joint",
                "joints_differ",
                "182cc5f1a86a3f1c87d3259ea95b6e4d51598a9e483d3a191ec1c84fcf6f6273",
            )
            verdict = "supported" if check["ok"] else "insufficient"
            evidence = check
        elif claim_id == "catalog_audit":
            report_path = ROOT / "reports/r1150/catalog_audit.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            ok = (
                report.get("report_sha256")
                == "c497a1b31104a687408e3e77cd694e3ef60c1505224eec8c629f220a29cbbf42"
                and report["duplicates"]["metadata_id_mismatches"] == []
                and report["near_duplicate_agents"] == []
                and report["drift"]["catalog_not_in_config"] == []
                and report["drift"]["config_not_in_catalog"] == []
            )
            verdict = "supported" if ok else "insufficient"
            evidence = {
                "ok": ok,
                "report_sha256": report.get("report_sha256"),
                "legacy_baseline_mismatches": len(
                    report["duplicates"]["legacy_baseline_mismatches"]
                ),
                "reviewed_near_duplicates": len(
                    report["reviewed_near_duplicates"]
                ),
            }
        elif claim_id in {"runtime_adapter", "n_of_1_unified"}:
            paths = (
                [
                    ROOT / "tests/test_r1148_runtime_contract.py",
                    ROOT / "tests/test_r1148_integration.py",
                ]
                if claim_id == "runtime_adapter"
                else [ROOT / "tests/test_r1150_n_of_1_consolidation.py"]
            )
            check = test_check(paths)
            verdict = "supported" if check["ok"] else "insufficient"
            evidence = check
        elif claim_id == "classification_pilot":
            verdict = "insufficient"
            evidence = {
                "reason": "dados sintéticos; nenhuma vantagem quântica demonstrada",
            }
        else:
            verdict = "insufficient"
            evidence = {
                "reason": "sem participante, ética, hardware ou peer review",
            }
        results.append({
            "id": claim_id,
            "verdict": verdict,
            "evidence": evidence,
            "claim_status": claim.get("status"),
        })

    overclaims = [item["id"] for item in results if item["verdict"] == "overclaim"]
    insufficient = [item["id"] for item in results if item["verdict"] == "insufficient"]
    automated_ids = {
        "formal_complex", "formal_correlation", "catalog_audit",
        "runtime_adapter", "n_of_1_unified",
    }
    reproducible = all(
        item["verdict"] == "supported"
        for item in results
        if item["id"] in automated_ids
    )
    payload = {
        "schema_version": 1,
        "round": "R1151",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "automated_verification": True,
        "peer_review": False,
        "clinical_validation": False,
        "hardware_validation": False,
        "reproducible_checks": reproducible,
        "claims": results,
        "overclaims": overclaims,
        "insufficient": insufficient,
        "limits": (
            "Verificação automatizada de hashes, certificados e testes. "
            "Não é peer review, validação clínica ou de hardware. "
            "Não promove confiança."
        ),
    }
    (PACKAGE / "verification_result.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Resultado da verificação independente — R1151",
        "",
        "**Natureza:** verificação automatizada de claims, não peer review.",
        "**Peer review:** não. **Clínica:** não. **Hardware:** não.",
        "",
        "| Claim | Veredito | Evidência |",
        "|---|---|---|",
    ]
    for item in results:
        lines.append(
            f"| `{item['id']}` | **{item['verdict']}** | "
            f"`{json.dumps(item['evidence'], ensure_ascii=False)}` |"
        )
    lines += [
        "",
        f"**Overclaims:** {overclaims or 'nenhum'}",
        f"**Claims insuficientes:** {insufficient or 'nenhuma'}",
        f"**Reprodutível:** {reproducible}",
        "",
        "Os executores externos Codex/Antigravity foram tentados, mas o roteador",
        "não atribuiu agente interno elegível; a revisão por subagente também",
        "foi bloqueada por assinatura de modelo. Portanto, a validação humana ou",
        "institucional permanece aberta.",
        "",
        "Limites: prova formal não é validação empírica; auditoria textual não é",
        "equivalência funcional; teste local não é peer review.",
    ]
    (PACKAGE / "review_result.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "reproducible": reproducible,
        "overclaims": overclaims,
        "insufficient": insufficient,
        "result": str(PACKAGE / "review_result.md"),
    }, indent=2, ensure_ascii=False))
    return 0 if reproducible else 1


if __name__ == "__main__":
    raise SystemExit(main())
