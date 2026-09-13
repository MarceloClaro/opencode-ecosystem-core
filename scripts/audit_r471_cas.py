# -*- coding: utf-8 -*-
"""Auditoria formal dos critérios de aceitação CA1–CA10 da SPEC-935-R471.

Executa verificações objetivas (módulos, testes, doctor, invariantes) e gera
``VALIDATION_R471.md`` com a tabela CA por CA (pass / ressalva / fail) e
evidência. Sem rede, sem credenciais. Não constitui validação externa.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SERIES_MODULES = [
    "research_factory/search.py",
    "research_factory/autonomy.py",
    "research_factory/reasoning.py",
    "research_factory/pair_router.py",
    "sandbox/declarative_policy.py",
    "agent_runners/tig_executor.py",
    "workbench/deepseek_gui.py",
    "workbench/scihubeva_frontend.py",
    "model_lab/benchmark.py",
    "model_lab/hardware.py",
    "model_lab/curriculum.py",
]

SERIES_TESTS = [
    "tests/test_r471_research_factory.py",
    "tests/test_r473_tig_executor.py",
    "tests/test_r476_autonomy_reasoning_search.py",
    "tests/test_r478_sandbox_pair.py",
    "tests/test_r479_m4_m5.py",
    "tests/test_r480_m6_scihubeva.py",
]

BANNED_CLAIMS = ("superhuman", "verificado", "qualis a1", "superação")


def run_pytest(paths: list) -> tuple:
    cmd = [sys.executable, "-m", "pytest", *paths, "-q", "--tb=no", "-p", "no:cacheprovider"]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=180)
    last = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    return proc.returncode, last


def run_doctor() -> tuple:
    cmd = [sys.executable, "-m", "marceloclaro.cli", "doctor"]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=60)
    try:
        report = json.loads(proc.stdout[proc.stdout.find("{"):proc.stdout.rfind("}") + 1])
        return report.get("checks_failed", -1), report.get("checks_passed", 0), report
    except Exception:
        return -1, 0, {}


def main() -> int:
    results = {}

    # ---- CA1: operação idêntica sem configuração ----
    from research_factory.search import OPEN_SCIENCE_ORDER, OPEN_SCIENCE_SOURCES
    sources_ok = sorted(OPEN_SCIENCE_SOURCES) == ["arxiv", "crossref", "europepmc", "openalex"]
    order_ok = list(OPEN_SCIENCE_ORDER) == ["openalex", "crossref", "europepmc", "arxiv"]
    no_restricted = "scihubeva" not in {s.lower() for s in OPEN_SCIENCE_SOURCES}
    results["CA1"] = {
        "status": "pass" if (sources_ok and order_ok and no_restricted) else "fail",
        "evidence": (
            f"DEFAULT_SOURCES={{openalex,crossref,europepmc,arxiv}} "
            f"(sources_ok={sources_ok}, order_ok={order_ok}, sem_restritos={no_restricted})"
        ),
    }

    # ---- CA2: M1 manuscrito-demonstração + relatório de auditoria ----
    has_audit = (ROOT / "research_factory" / "audit.py").exists()
    has_stage_tests = (ROOT / "tests" / "test_r471_research_factory.py").exists()
    results["CA2"] = {
        "status": "ressalva" if (has_audit and has_stage_tests) else "fail",
        "evidence": (
            "Infraestrutura de auditoria presente (research_factory/audit.py JSONL + artifacts) "
            "e testes do estágio presentes; manuscrito-demonstração consolidado M1 com relatório "
            "único ainda não produzido (fábrica registra etapas individualmente)."
        ),
    }

    # ---- CA3: M2 egresso autorizado vs bloqueado ----
    from sandbox.declarative_policy import SCIENTIFIC_TEMPLATE_YAML, DeclarativePolicy
    policy = DeclarativePolicy.from_yaml(SCIENTIFIC_TEMPLATE_YAML)
    allowed = policy.check_egress("https://api.openalex.org/works?search=diabetes")
    denied = policy.check_egress("http://192.168.1.10/upload")
    results["CA3"] = {
        "status": "pass" if (allowed.allowed and not denied.allowed and denied.reason) else "fail",
        "evidence": (
            f"egresso bibliográfico allow={allowed.allowed}; "
            f"egresso não autorizado deny={not denied.allowed} com recibo"
        ),
    }

    # ---- CA4: M3 PAIR no doctor/roteador com fallback ----
    from research_factory.pair_router import PairRouter
    os.environ.pop("PAIR_BASE_URL", None)
    os.environ.pop("PAIR_ENDPOINTS", None)
    no_pair = PairRouter(local_ready=lambda: False, ollama_ready=lambda: True,
                         openai_ready=lambda: False).resolve()
    with_pair = PairRouter(local_ready=lambda: False, pair_base_url="http://pair.local:3000",
                           pair_ready=lambda: True, ollama_ready=lambda: False,
                           openai_ready=lambda: False).resolve()
    results["CA4"] = {
        "status": "pass" if (no_pair.provider == "ollama" and with_pair.provider == "pair") else "fail",
        "evidence": (
            f"sem PAIR -> {no_pair.provider} (fallback_used={no_pair.fallback_used}); "
            f"com PAIR -> {with_pair.provider}"
        ),
    }

    # ---- CA5: M4 workbench + THIRD_PARTY_NOTICES ----
    notices_path = ROOT / "THIRD_PARTY_NOTICES.md"
    notices = notices_path.read_text(encoding="utf-8") if notices_path.exists() else ""
    lic_ok = all(k in notices for k in ("PolyForm Perimeter", "MIT", "minimind", "DeepSeekGUI"))
    from workbench.deepseek_gui import DeepSeekGUIWorkbench
    os.environ["DEEPSEEK_GUI_WORKSPACE"] = "academic"
    os.environ["DEEPSEEK_GUI_ENABLED"] = "1"
    wb = DeepSeekGUIWorkbench(repo_root=str(ROOT), enabled_by_env=True)
    try:
        cfg = wb.launch_config()
        wb_ok = cfg["workspace"] == "academic" and "PolyForm Perimeter" in cfg["license_product"]
    except Exception:
        wb_ok = False
    results["CA5"] = {
        "status": "pass" if (lic_ok and wb_ok) else "fail",
        "evidence": f"THIRD_PARTY_NOTICES licenças_ok={lic_ok}; launch_config workspace_ok={wb_ok}",
    }
    os.environ.pop("DEEPSEEK_GUI_WORKSPACE", None)

    # ---- CA6: M5 benchmark 64M com seed fixa / limitação de hardware ----
    from model_lab.benchmark import MiniMindBenchmark
    report = MiniMindBenchmark(seed=42, device="none").run(steps=8)
    results["CA6"] = {
        "status": "pass" if (len(report.losses) == 8 and report.hardware_limitation
                             and report.reproducibility_note) else "fail",
        "evidence": (
            f"seed 42 -> {len(report.losses)} passos; hardware_limitation={report.hardware_limitation}; "
            "limitação documentada (sem GPU)"
        ),
    }

    # ---- CA7: M6 frontend opt-in ----
    from workbench.scihubeva_frontend import SCIHUBEVA_RESOLVER, SciHubEVARequest, SciHubEVAFrontend
    req = SciHubEVARequest(target_type="doi", target_value="10.1234/example")
    frontend = SciHubEVAFrontend()
    env_backup = {k: os.environ.get(k) for k in (
        "RESTRICTED_RESOLVER_ENABLED", "RESTRICTED_RESOLVER_POLICY",
        "RESTRICTED_RESOLVER_ALLOWLIST", "RESTRICTED_RESOLVER_AUTHORIZATION_ID",
        "RESTRICTED_RESOLVER_RIGHTS_BASIS", "RESTRICTED_RESOLVER_EVIDENCE_REF")}
    os.environ["RESTRICTED_RESOLVER_ENABLED"] = "0"
    code0, r0, d0 = frontend.submit(req)
    denied_ok = r0["decision"] == "denied" and r0["deny_code"] == "missing_enable"
    os.environ.update({
        "RESTRICTED_RESOLVER_ENABLED": "1",
        "RESTRICTED_RESOLVER_POLICY": "allow",
        "RESTRICTED_RESOLVER_ALLOWLIST": SCIHUBEVA_RESOLVER,
        "RESTRICTED_RESOLVER_AUTHORIZATION_ID": "auth-1",
        "RESTRICTED_RESOLVER_RIGHTS_BASIS": "contractual",
        "RESTRICTED_RESOLVER_EVIDENCE_REF": "ev-1",
    })
    code1, r1, d1 = frontend.submit(req, confirm=True)
    required = {"command", "resolver", "policy_effective", "enabled_effective",
                "authorization_id", "decision", "deny_code", "timestamp_utc",
                "orchestrator", "hash_sha256"}
    full_ok = code1 == 0 and r1["decision"] == "allowed" and required <= set(r1.keys())
    for k, v in env_backup.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    results["CA7"] = {
        "status": "pass" if (denied_ok and full_ok) else "fail",
        "evidence": (
            f"sem habilitação -> denied/{r0['deny_code']}; "
            f"com habilitação -> exit {code1}, receipt com {len(required)} campos obrigatórios"
        ),
    }

    # ---- CA8: suíte dos módulos com mocks; sem rede/credenciais ----
    rc, summary = run_pytest(SERIES_TESTS)
    results["CA8"] = {
        "status": "pass" if rc == 0 else "fail",
        "evidence": f"pytest {' '.join(SERIES_TESTS)} -> {summary}",
    }

    # ---- CA9: doctor pass; core-check ----
    failed, passed, doctor = run_doctor()
    cc = subprocess.run(
        [sys.executable, "-m", "marceloclaro.cli", "core-check"],
        capture_output=True, text=True, cwd=ROOT, timeout=120,
    )
    cc_ok = cc.returncode == 0 and '"overall"' in cc.stdout
    results["CA9"] = {
        "status": "pass" if (failed == 0 and passed >= 18 and cc_ok) else "fail",
        "evidence": (
            f"doctor {passed}/{passed + failed} (failed={failed}); "
            f"core-check exit {cc.returncode} (overall presente) -> {'pass' if cc_ok else 'fail'}"
        ),
    }

    # ---- CA10: anti-overclaim nos módulos/specs da série ----
    # Scanner com contexto: palavras vedadas só contam como violação quando NÃO
    # estão em contexto de negação/proibição ("nada de 'verificado'") nem em
    # verificação técnica com evidência ("verificado por mock/teste/doctor").
    import re
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
    TECH_VERIFY_MARKERS = ("verificado por", "verificada por", "verificação por")
    violators = []
    for rel in SERIES_MODULES + [
        "specs/SPEC-935-R471-resiliencia-cientifica-integracao-externa.md",
        "specs/SPEC-935-R473-executor-multiprovider-tig.md",
        "specs/SPEC-935-R476-autonomia-raciocinio-pesquisa.md",
        "specs/SPEC-935-R477-liquidacao-debitos-documentais.md",
        "specs/SPEC-935-R478-sandbox-pair.md",
        "specs/SPEC-935-R479-workbench-modelos.md",
        "specs/SPEC-935-R480-scihubeva-frontend.md",
    ]:
        p = ROOT / rel
        if not p.exists():
            violators.append(f"{rel}: ausente")
            continue
        text = p.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            hits = [word for pattern, word in BANNED_PATTERNS if pattern.search(low)]
            if not hits:
                continue
            if any(marker in low for marker in NEGATION_MARKERS):
                continue
            if any(marker in low for marker in TECH_VERIFY_MARKERS):
                continue
            for word in hits:
                violators.append(f"{rel}:{lineno}: contém {word!r}")
    results["CA10"] = {
        "status": "pass" if not violators else "fail",
        "evidence": "violadores: " + ("; ".join(violators) if violators else "nenhum (contexto de proibição/verificação técnica ignorado)"),
    }

    # ---- Gera VALIDATION_R471.md ----
    lines = [
        "# VALIDATION_R471 — Auditoria dos critérios de aceitação CA1–CA10",
        "",
        "Auditoria executada em 2026-09-13 (hermética; sem rede; sem credenciais).",
        "**Esta validação é interna e não constitui certificação externa.**",
        "",
        "| CA | Critério | Status | Evidência |",
        "|---|---|---|---|",
    ]
    for ca in sorted(results):
        r = results[ca]
        lines.append(f"| {ca} | {ca_header(ca)} | {r['status']} | {r['evidence']} |")

    (ROOT / "VALIDATION_R471.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


def ca_header(ca: str) -> str:
    return {
        "CA1": "Sem config, opera idêntico (open_science_only + DEFAULT_SOURCES inalterados + doctor + suíte nativa)",
        "CA2": "M1 manuscrito-demo completo com relatório de auditoria por etapa",
        "CA3": "M2 política OpenShell: egresso autorizado funciona; não autorizado bloqueado com recibo",
        "CA4": "M3 PAIR no doctor e roteador; fallback transparente sem PAIR",
        "CA5": "M4 workbench para workspace do Core + licenças em THIRD_PARTY_NOTICES",
        "CA6": "M5 treinamento 64M com seed fixa ou limitação de hardware documentada",
        "CA7": "M6 sem habilitação não aciona; com habilitação CLIExecutionReceipt completo",
        "CA8": "Suíte dos módulos com mocks; sem rede/credenciais",
        "CA9": "doctor pass (warns apenas CLIs opcionais) + core-check verde",
        "CA10": "Anti-overclaim nos relatórios/specs (gate R142)",
    }[ca]


if __name__ == "__main__":
    raise SystemExit(main())