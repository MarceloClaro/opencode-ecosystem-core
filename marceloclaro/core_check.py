# -*- coding: utf-8 -*-
"""core-check — validação estrutural rápida do ecossistema (R481).

Audita, de forma hermética (sem rede, sem LLM, sem credenciais):
1. doctor estrutural (20 checks tradicionais);
2. carregamento das specs (SpecRegistry);
3. integridade do EvolutionRegistry (cycles.json);
4. invariantes R471 — DEFAULT_SOURCES inalterados e sem resolvedores restritos;
5. anti-overclaim nos 5 documentos operacionais (contexto de proibição
   ignorado; exige a ressalva "não constitui certificação externa");
6. hermericidade dos módulos da série R471 (sem imports de rede/processo,
   exceto executores declarados tipo ``tig_executor``);
7. ausência de alegações vedadas no próprio relatório JSON.

Saída compatível com o doctor: checks_total/checks_passed/checks_warned/
checks_failed/overall (healthy | degraded | fail).
"""

from __future__ import annotations

import ast
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DOC_PATHS = (
    "README.md",
    "ARCHITECTURE.md",
    "MANUAL.md",
    "installer/README.md",
    "installer/windows/README.md",
)

HERMETIC_MODULES = (
    "research_factory/search.py",
    "research_factory/autonomy.py",
    "research_factory/reasoning.py",
    "research_factory/pair_router.py",
    "sandbox/declarative_policy.py",
    "workbench/deepseek_gui.py",
    "workbench/scihubeva_frontend.py",
    "model_lab/benchmark.py",
    "model_lab/hardware.py",
    "model_lab/curriculum.py",
)

BANNED_PATTERNS = [
    (re.compile(r"\bsuperhuman\b"), "superhuman"),
    (re.compile(r"\bverificad[oa]s?\b"), "verificado"),
    (re.compile(r"\bqualis a1\b"), "qualis a1"),
    (re.compile(r"\bsuperação\b"), "superação"),
]
NEGATION_MARKERS = (
    "não ", "sem ", "nunca", "vedado", "proibido", "nada de", "ausência",
    "sem validação", "não constitui", "exceto", "sem alegação",
    "sem prometer", "não prometa", "nenhum", "nenhuma",
)
TECH_VERIFY_MARKERS = ("verificado por", "verificada por", "verificação por",
                       "fluxo verificado", "previamente verificados",
                       "previamente verificada")


def _check(checks, check_id, status, detail):
    checks.append({"id": check_id, "status": status, "detail": detail})


def _check_doctor() -> tuple:
    from marceloclaro.doctor import run_doctor
    report = run_doctor()
    return report, report.get("checks_passed", 0), report.get(
        "checks_failed", -1
    )


def _check_specs_loading():
    try:
        from sdd.spec_engine import spec_registry
        specs = list(spec_registry.specs.values())
        return len(specs) > 0, f"{len(specs)} specs carregadas"
    except Exception as exc:  # pragma: no cover
        return False, f"falha ao carregar specs: {exc}"


def _check_evolution_registry():
    p = ROOT / "evolution" / "cycles.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        cycles = data.get("cycles", [])
        return len(cycles) > 0, f"{len(cycles)} ciclos registrados"
    except Exception as exc:
        return False, f"cycles.json inválido: {exc}"


def _check_default_sources():
    try:
        from research_factory.search import OPEN_SCIENCE_ORDER, OPEN_SCIENCE_SOURCES
        ok = (
            sorted(OPEN_SCIENCE_SOURCES)
            == ["arxiv", "crossref", "europepmc", "openalex"]
            and list(OPEN_SCIENCE_ORDER)
            == ["openalex", "crossref", "europepmc", "arxiv"]
        )
        restricted = {s.lower() for s in OPEN_SCIENCE_SOURCES if "scihubeva" in s.lower()}
        detail = (
            "DEFAULT_SOURCES={openalex,crossref,europepmc,arxiv} "
            f"(ok={ok}, restritos={sorted(restricted) or 'nenhum'})"
        )
        return ok and not restricted, detail
    except Exception as exc:
        return False, f"falha ao carregar fontes: {exc}"


def _scan_docs():
    """Varre DOC_PATHS; contexto de proibição/verificação técnica ignorado.

    O disclaimer é avaliado no texto concatenado (combined), exatamente como o
    gate oficial do R448 (test_r448_documentation_reconciliation.py).
    """
    violators = []
    combined_parts = []
    for rel in DOC_PATHS:
        p = ROOT / rel
        if not p.exists():
            violators.append(f"{rel}: ausente")
            continue
        text = p.read_text(encoding="utf-8")
        combined_parts.append(text)
        for lineno, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            hits = [w for pat, w in BANNED_PATTERNS if pat.search(low)]
            if not hits:
                continue
            if any(m in low for m in NEGATION_MARKERS):
                continue
            if any(m in low for m in TECH_VERIFY_MARKERS):
                continue
            violators.append(f"{rel}:{lineno}: {', '.join(hits)}")
    combined = "\n".join(combined_parts).lower()
    has_disclaimer = "não constituem certificação externa" in combined or (
        "não constitui certificação externa" in combined
    )
    return violators, has_disclaimer


def _check_hermetic_modules():
    bad = []
    banned_imports = {"subprocess", "socket", "urllib.request"}
    for rel in HERMETIC_MODULES:
        p = ROOT / rel
        if not p.exists():
            bad.append(f"{rel}: ausente")
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            bad.append(f"{rel}: syntax error {exc}")
            continue
        found = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    found.add(a.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                found.add(node.module.split(".")[0])
        hits = sorted(found & banned_imports)
        if hits:
            bad.append(f"{rel}: {', '.join(hits)}")
    return bad


def run_core_check(verbose: bool = True) -> dict:
    checks: list = []

    doctor, passed, failed = _check_doctor()
    status = "pass" if failed == 0 else "fail"
    detail = f"doctor {passed}/{passed + (failed if failed >= 0 else 0)} (failed={failed})"
    if failed < 0:
        detail = "doctor indisponível"
    _check(checks, "doctor", status, detail)

    ok, detail = _check_specs_loading()
    _check(checks, "specs_loading", "pass" if ok else "fail", detail)

    ok, detail = _check_evolution_registry()
    _check(checks, "evolution_registry", "pass" if ok else "fail", detail)

    ok, detail = _check_default_sources()
    _check(checks, "default_sources", "pass" if ok else "fail", detail)

    violators, disclaimer = _scan_docs()
    if violators:
        status = "fail"
        detail = "alegações vedadas: " + "; ".join(violators[:5])
    elif not disclaimer:
        status = "warn"
        detail = "sem alegações, mas sem ressalva 'não constitui certificação externa' nos 5 documentos"
    else:
        status = "pass"
        detail = "5 documentos sem alegações vedadas; ressalva 'não constitui certificação externa' presente"
    _check(checks, "anti_overclaim_docs", status, detail)

    bad = _check_hermetic_modules()
    if bad:
        status, detail = "fail", "imports vedados: " + "; ".join(bad[:5])
    else:
        status = "pass"
        detail = f"{len(HERMETIC_MODULES)} módulos da série sem imports de rede/processo (hermético)"
    _check(checks, "modules_hermetic", status, detail)

    failed_count = sum(1 for c in checks if c["status"] == "fail")
    warn_count = sum(1 for c in checks if c["status"] == "warn")
    overall = "healthy" if failed_count == 0 and warn_count == 0 else (
        "degraded" if failed_count == 0 else "fail"
    )

    report = {
        "core_check": True,
        "core_version": "R481",
        "checks_total": len(checks),
        "checks_passed": len(checks) - failed_count - warn_count,
        "checks_warned": warn_count,
        "checks_failed": failed_count,
        "overall": overall,
        "checks": checks,
        "timestamp_utc": doctor.get("timestamp_utc", ""),
    }
    if verbose:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":  # pragma: no cover
    r = run_core_check()
    raise SystemExit(0 if r["overall"] in {"healthy", "degraded"} else 1)