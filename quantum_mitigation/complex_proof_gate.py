"""R1146 — gate de inovação com provas e contraprovas complexas em Lean 4/Mathlib.

O gate é fail-closed e auditável:

- exige que cada alegação tenha um teorema e uma contraprova nomeada;
- compila o arquivo Lean com `lake env lean`;
- lê `#print axioms` e classifica cada teorema;
- aceita apenas provas kernel-checked (propext, Classical.choice, Quot.sound);
- bloqueia `sorry`/`admit`/`axiom`, `sorryAx`, axiomas nativos e teoremas ausentes.

Não prova hardware, calibração, ruído, canal quântico, vantagem ou resultado
experimental. O pareamento alegação↔contraprova é editorial e exige revisão
humana.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN_PROJECT = ROOT / "livro-core" / "lean"
LEAN_FILE = ROOT / "lean" / "quantum-cb" / "ComplexProofs.lean"
DEFAULT_LOG = ROOT / "lean" / "quantum-cb" / "complex_compile.log"
DEFAULT_OUTPUT = (
    ROOT
    / "harnesses"
    / "quantum-error-mitigation"
    / "resultados"
    / "r1146_complex_proofs"
    / "certificate.json"
)

STANDARD_AXIOMS = frozenset({"propext", "Classical.choice", "Quot.sound"})
NATIVE_AXIOMS = frozenset({"Lean.ofReduceBool", "Lean.trustCompiler"})
FORBIDDEN_TOKENS = ("sorry", "admit")

THEOREM_RE = re.compile(
    r"^\s*(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)", re.MULTILINE
)
AXIOM_DECL_RE = re.compile(r"^\s*axiom\b", re.MULTILINE)
AXIOM_LINE_RE = re.compile(r"'([^']+)' depends on axioms: \[([^\]]*)\]")
NO_AXIOM_LINE_RE = re.compile(r"'([^']+)' does not depend on any axioms")

REQUIRED_THEOREMS = (
    "normSq_global_phase",
    "normSq_conj",
    "born_nonneg",
    "born_le_one",
    "interference",
    "phaseGate_unitary",
    "scaling_changes_normSq",
    "relative_phase_not_one",
    "no_negative_normSq",
)
COUNTERPROOFS = (
    "scaling_changes_normSq",
    "relative_phase_not_one",
    "no_negative_normSq",
)
DEFAULT_CLAIMS = (
    {
        "id": "global_phase",
        "theorem": "normSq_global_phase",
        "counterproof": "relative_phase_not_one",
        "kind": "invariance",
    },
    {
        "id": "born_rule",
        "theorem": "born_nonneg",
        "counterproof": "no_negative_normSq",
        "kind": "probability",
    },
    {
        "id": "interference",
        "theorem": "interference",
        "counterproof": "scaling_changes_normSq",
        "kind": "coherence",
    },
    {
        "id": "phase_gate",
        "theorem": "phaseGate_unitary",
        "counterproof": "scaling_changes_normSq",
        "kind": "unitary",
    },
)

LIMITS = (
    "Prova algébrica em Lean 4 + Mathlib; não prova hardware, calibração, "
    "ruído, canal quântico, vantagem quântica ou resultado experimental. "
    "O pareamento alegação↔contraprova é editorial e exige revisão humana. "
    "Aceitar o gate não promove confiança nem autoriza execução."
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strip_comments(text: str) -> str:
    """Remove comentários de linha e de bloco (aninhados) do Lean."""
    output: list[str] = []
    index = 0
    depth = 0
    while index < len(text):
        if text.startswith("/-", index):
            depth += 1
            index += 2
        elif text.startswith("-/", index) and depth:
            depth -= 1
            index += 2
        elif depth:
            index += 1
        elif text.startswith("--", index):
            newline = text.find("\n", index)
            if newline == -1:
                break
            index = newline
        else:
            output.append(text[index])
            index += 1
    return "".join(output)


def _theorem_blocks(code: str) -> dict[str, str]:
    matches = list(THEOREM_RE.finditer(code))
    blocks: dict[str, str] = {}
    for position, match in enumerate(matches):
        end = matches[position + 1].start() if position + 1 < len(matches) else len(code)
        blocks[match.group(1)] = code[match.start():end]
    return blocks


def scan_source(
    text: str,
    *,
    required_theorems=REQUIRED_THEOREMS,
    counterproofs=COUNTERPROOFS,
) -> dict:
    code = strip_comments(text)
    theorems = THEOREM_RE.findall(code)
    forbidden = [
        token for token in FORBIDDEN_TOKENS
        if re.search(rf"\b{token}\b", code)
    ]
    if AXIOM_DECL_RE.search(code):
        forbidden.append("axiom")
    blocks = _theorem_blocks(code)
    counterproof_shape = {
        name: ("≠" in blocks.get(name, "") or "¬" in blocks.get(name, ""))
        for name in counterproofs
    }
    return {
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "theorems": sorted(theorems),
        "missing": [name for name in required_theorems if name not in theorems],
        "forbidden": sorted(set(forbidden)),
        "counterproofs_present": [
            name for name in counterproofs if name in theorems
        ],
        "counterproofs_missing": [
            name for name in counterproofs if name not in theorems
        ],
        "counterproof_shape": counterproof_shape,
    }


def _short_name(name: str) -> str:
    return name.rsplit(".", 1)[-1]


def parse_axioms(output: str) -> dict[str, list[str]]:
    axioms: dict[str, list[str]] = {}
    for name, body in AXIOM_LINE_RE.findall(output):
        axioms[_short_name(name)] = [
            item.strip() for item in body.split(",") if item.strip()
        ]
    for name in NO_AXIOM_LINE_RE.findall(output):
        axioms.setdefault(_short_name(name), [])
    return axioms


def classify_axioms(axioms: list[str]) -> str:
    names = set(axioms)
    if "sorryAx" in names:
        return "blocked"
    if names & NATIVE_AXIOMS:
        return "native"
    if names <= STANDARD_AXIOMS:
        return "kernel_checked"
    return "review_required"


def compile_lean(
    *,
    lean_file: Path = LEAN_FILE,
    timeout: int = 1200,
) -> dict:
    lean_file = Path(lean_file)
    if shutil.which("lake") is None:
        return {
            "status": "blocked",
            "reason": "lake ausente",
            "returncode": None,
            "output": "",
            "elapsed_seconds": None,
            "sha256": sha256_file(lean_file) if lean_file.exists() else None,
            "log_path": None,
        }
    relative = os.path.relpath(lean_file, LEAN_PROJECT)
    started = time.perf_counter()
    try:
        result = subprocess.run(
            ["lake", "env", "lean", relative],
            cwd=LEAN_PROJECT,
            capture_output=True,
            text=True,
            timeout=int(timeout),
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "blocked",
            "reason": f"timeout após {timeout}s",
            "returncode": None,
            "output": (exc.stdout or "") + (exc.stderr or ""),
            "elapsed_seconds": time.perf_counter() - started,
            "sha256": sha256_file(lean_file),
            "log_path": None,
        }
    output = (result.stdout or "") + (result.stderr or "")
    return {
        "status": "compiled" if result.returncode == 0 else "blocked",
        "reason": None if result.returncode == 0 else "lean retornou erro",
        "returncode": result.returncode,
        "output": output,
        "elapsed_seconds": time.perf_counter() - started,
        "sha256": sha256_file(lean_file),
        "log_path": None,
    }


def audit(
    claims=None,
    *,
    compilation: dict | None = None,
    run_compile: bool = True,
    write: bool = False,
    output: Path = DEFAULT_OUTPUT,
    timeout: int = 1200,
    lean_file: Path = LEAN_FILE,
    required_theorems=REQUIRED_THEOREMS,
    counterproofs=COUNTERPROOFS,
    round_id: str = "R1146",
    limits: str = LIMITS,
    log_path: Path = DEFAULT_LOG,
) -> dict:
    lean_file = Path(lean_file)
    if claims is None:
        claim_list = list(DEFAULT_CLAIMS) if lean_file == LEAN_FILE else []
    else:
        claim_list = list(claims)
    source = lean_file.read_text(encoding="utf-8")
    scan = scan_source(
        source,
        required_theorems=required_theorems,
        counterproofs=counterproofs,
    )
    if compilation is None:
        compilation = (
            compile_lean(lean_file=lean_file, timeout=timeout)
            if run_compile
            else {
                "status": "not_run",
                "reason": "compilação não solicitada",
                "returncode": None,
                "output": "",
                "elapsed_seconds": None,
                "sha256": scan["sha256"],
                "log_path": None,
            }
        )
    parsed = parse_axioms(compilation.get("output", ""))
    axioms = {
        name: {
            "axioms": parsed.get(name, []),
            "classification": classify_axioms(parsed.get(name, []))
            if name in parsed
            else "not_reported",
        }
        for name in required_theorems
    }
    claim_rows = []
    for claim in claim_list:
        theorem = claim.get("theorem")
        counterproof = claim.get("counterproof")
        reasons = []
        if theorem not in scan["theorems"]:
            reasons.append(f"theorem ausente: {theorem}")
        if not counterproof:
            reasons.append("counterproof não declarada")
        elif counterproof not in scan["theorems"]:
            reasons.append(f"counterproof ausente: {counterproof}")
        elif not scan["counterproof_shape"].get(counterproof, False):
            reasons.append(
                f"counterproof sem forma de negação: {counterproof}"
            )
        theorem_status = axioms.get(theorem, {}).get(
            "classification", "not_reported"
        )
        counter_status = axioms.get(counterproof, {}).get(
            "classification", "not_reported"
        )
        if theorem_status != "kernel_checked":
            reasons.append(f"theorem status: {theorem_status}")
        if counter_status != "kernel_checked":
            reasons.append(f"counterproof status: {counter_status}")
        claim_rows.append({
            "id": claim.get("id"),
            "kind": claim.get("kind"),
            "theorem": theorem,
            "theorem_status": theorem_status,
            "counterproof": counterproof,
            "counterproof_status": counter_status,
            "accepted": not reasons,
            "reasons": reasons,
        })
    unreported = [name for name in required_theorems if name not in parsed]
    non_kernel = {
        name: entry["classification"]
        for name, entry in axioms.items()
        if entry["classification"] != "kernel_checked"
    }
    accepted = (
        compilation.get("status") == "compiled"
        and not scan["forbidden"]
        and not scan["missing"]
        and not scan["counterproofs_missing"]
        and not unreported
        and not non_kernel
        and all(row["accepted"] for row in claim_rows)
    )
    try:
        lean_path = str(lean_file.relative_to(ROOT))
    except ValueError:
        lean_path = str(lean_file)
    report = {
        "schema_version": 1,
        "round": round_id,
        "lean_file": {
            "path": lean_path,
            "sha256": scan["sha256"],
        },
        "compile": {
            key: compilation.get(key)
            for key in (
                "status",
                "reason",
                "returncode",
                "elapsed_seconds",
                "sha256",
                "log_path",
            )
        },
        "source_scan": scan,
        "axioms": axioms,
        "claims": claim_rows,
        "gate": {
            "accepted": bool(accepted),
            "unreported_theorems": unreported,
            "non_kernel_theorems": non_kernel,
            "blocked_claims": sum(
                1 for row in claim_rows if not row["accepted"]
            ),
            "counterproofs_required": list(counterproofs),
        },
        "limits": limits,
        "hardware_executed": False,
        "externally_validated": False,
        "confidence_promoted": False,
    }
    if write:
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        canonical_log = Path(log_path)
        canonical_log.parent.mkdir(parents=True, exist_ok=True)
        canonical_log.write_text(
            compilation.get("output", ""), encoding="utf-8"
        )
        harness_log = output.parent / "compile.log"
        harness_log.write_text(compilation.get("output", ""), encoding="utf-8")
        try:
            report["compile"]["log_path"] = str(
                harness_log.relative_to(ROOT)
            )
        except ValueError:
            report["compile"]["log_path"] = str(harness_log)
        try:
            report["compile"]["canonical_log_path"] = str(
                canonical_log.relative_to(ROOT)
            )
        except ValueError:
            report["compile"]["canonical_log_path"] = str(canonical_log)
        report["compile"]["log_sha256"] = hashlib.sha256(
            harness_log.read_bytes()
        ).hexdigest()
        output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        try:
            certificate_path = str(output.relative_to(ROOT))
        except ValueError:
            certificate_path = str(output)
        report["certificate"] = {
            "path": certificate_path,
            "sha256": sha256_file(output),
        }
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Gate de prova/contraprova complexa em Lean 4 + Mathlib (R1146)."
    )
    parser.add_argument("--no-compile", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--timeout", type=int, default=1200)
    args = parser.parse_args(argv)
    report = audit(
        run_compile=not args.no_compile,
        write=True,
        output=Path(args.output),
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
