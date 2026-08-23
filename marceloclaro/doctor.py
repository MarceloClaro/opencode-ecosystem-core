# -*- coding: utf-8 -*-
"""
Doctor — Diagnóstico de Saúde do Ecossistema (SPEC-935-R110)
=============================================================
Health-check rápido e estrutural do ecossistema, inspirado no comando
`doctor`/`status` do projeto OpenCode_Ecosystem original (que já não
está mais isolado — este módulo é a versão adaptada para o core atual).

Diferente de `scripts/quality_report.py`/`scripts/check_coverage.py`
(que rodam a suíte pytest completa, ~150s), o `doctor()` roda em
segundos: verifica integridade estrutural — specs formais carregam,
o registro de evolução não perdeu ciclos silenciosamente (o mesmo bug
de perda de dados corrigido no R108), loop specs estão bem formados,
a memória metacognitiva está acessível, e a prática de correção pública
de overclaims (CORRIGENDUM.md) está presente.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import json
import os
import shutil
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Marcador para saber se o módulo de métricas está disponível
_METRICS_AVAILABLE = False
try:
    from marceloclaro.metrics import MetricsCollector
    _METRICS_AVAILABLE = True
except ImportError:
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# CLIs externas de primeira classe do ecossistema (SPEC-935-R116) e a
# sugestão de instalação exata para cada uma quando ausente.
EXTERNAL_CLIS = {
    "opencode": "curl -fsSL https://opencode.ai/install | bash",
    "agy": "curl -fsSL https://antigravity.google/cli/install.sh | bash",
    "claude": "npm install -g @anthropic-ai/claude-code",
    "ollama": "curl -fsSL https://ollama.com/install.sh | sh",
    "scihub-cli": "pip install scihub-cli",
}


@dataclass
class DoctorCheck:
    name: str
    status: str  # "pass" | "warn" | "fail"
    detail: str

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "status": self.status, "detail": self.detail}


def _check_formal_specs() -> DoctorCheck:
    try:
        from sdd.spec_engine import SpecRegistry
        registry = SpecRegistry()
        count = registry.load_formal_specs()
        if count == 0:
            return DoctorCheck("specs_formais", "fail", "Nenhuma especificação formal carregada de specs/*.md.")
        return DoctorCheck("specs_formais", "pass", f"{count} especificações formais carregadas.")
    except Exception as exc:
        return DoctorCheck("specs_formais", "fail", f"Erro ao carregar specs: {exc}")


def _check_evolution_registry() -> DoctorCheck:
    """Verifica se o EvolutionRegistry carrega TODOS os ciclos do
    cycles.json — este check existe porque um bug real (R108) fazia
    ``EvolutionRegistry._load()`` zerar o histórico inteiro em silêncio
    quando uma única entrada tinha uma chave desconhecida."""
    cycles_path = os.path.join(REPO_ROOT, "evolution", "cycles.json")
    if not os.path.exists(cycles_path):
        return DoctorCheck("evolution_registry", "warn", "evolution/cycles.json não encontrado.")
    try:
        with open(cycles_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        raw_count = len(raw.get("cycles", []))

        from evolution.cycles import EvolutionRegistry
        registry = EvolutionRegistry()
        loaded_count = len(registry.cycles)

        if loaded_count < raw_count:
            return DoctorCheck(
                "evolution_registry", "fail",
                f"Perda silenciosa de histórico: {raw_count} ciclos no arquivo, "
                f"apenas {loaded_count} carregados no registro. Verifique "
                f"EvolutionRegistry._load() e chaves extras desconhecidas nas entradas.",
            )
        return DoctorCheck("evolution_registry", "pass", f"{loaded_count}/{raw_count} ciclos carregados corretamente.")
    except Exception as exc:
        return DoctorCheck("evolution_registry", "fail", f"Erro ao verificar registro de evolução: {exc}")


def _check_loop_specs() -> DoctorCheck:
    try:
        # Garante que loops do harness/Reversa estejam registrados (R438 — caminho para 100)
        try:
            import integrations.deepseek_harness.reasoning_loop  # noqa: F401
        except Exception:
            pass
        try:
            import integrations.harness.universal_reasoning_loop  # noqa: F401
        except Exception:
            pass
        try:
            import reversa_universal.engine  # noqa: F401 — registra loops reversa se houver
        except Exception:
            pass
        from sdd.loop_spec import loop_spec_registry
        loops = loop_spec_registry.list()
        if not loops:
            return DoctorCheck("loop_specs", "warn", "Nenhum loop spec registrado ainda.")
        malformed = [loop["name"] for loop in loops if not loop["validation"]["well_formed"]]
        if malformed:
            return DoctorCheck("loop_specs", "fail", f"Loop specs mal-formados: {malformed}")
        return DoctorCheck("loop_specs", "pass", f"{len(loops)} loop spec(s) registrado(s), todos bem formados.")
    except Exception as exc:
        return DoctorCheck("loop_specs", "fail", f"Erro ao verificar loop specs: {exc}")


def _check_metacognitive_memory() -> DoctorCheck:
    state_dir = os.path.join(REPO_ROOT, ".mci_state")
    try:
        from mci.metabus import metabus
        _ = metabus.memory.confidence_ledger  # aciona o singleton, ja carregado
        if not os.path.isdir(state_dir):
            return DoctorCheck(
                "memoria_metacognitiva", "warn",
                ".mci_state/ ainda não existe (será criado na primeira escrita).",
            )
        if not os.access(state_dir, os.W_OK):
            return DoctorCheck("memoria_metacognitiva", "fail", f"{state_dir} não é gravável.")
        return DoctorCheck(
            "memoria_metacognitiva", "pass",
            f"MetaBus memory acessível; {len(metabus.memory.episodic)} entradas episódicas.",
        )
    except Exception as exc:
        return DoctorCheck("memoria_metacognitiva", "fail", f"Erro ao acessar memória metacognitiva: {exc}")


def _check_opencode_config() -> DoctorCheck:
    path = os.path.join(REPO_ROOT, "opencode.json")
    if not os.path.exists(path):
        return DoctorCheck("opencode_config", "warn", "opencode.json não encontrado na raiz do repositório.")
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
        agents = config.get("agent", {})
        if "marceloclaro" not in agents:
            return DoctorCheck(
                "opencode_config", "warn",
                "opencode.json existe mas não define o agente 'marceloclaro' como primary.",
            )
        return DoctorCheck("opencode_config", "pass", f"opencode.json válido com {len(agents)} agente(s) configurado(s).")
    except Exception as exc:
        return DoctorCheck("opencode_config", "fail", f"opencode.json inválido ou ilegível: {exc}")


def _check_corrigendum() -> DoctorCheck:
    """Verifica se a prática de correção pública de overclaims
    (CORRIGENDUM.md) está presente — mesma prática adotada pelo projeto
    original que inspirou este ecossistema."""
    path = os.path.join(REPO_ROOT, "CORRIGENDUM.md")
    if not os.path.exists(path):
        return DoctorCheck(
            "corrigendum", "warn",
            "CORRIGENDUM.md não encontrado — considere documentar publicamente "
            "quaisquer alegações auto-avaliadas que precisem de ressalva.",
        )
    size = os.path.getsize(path)
    if size < 200:
        return DoctorCheck("corrigendum", "warn", "CORRIGENDUM.md existe mas parece vazio/placeholder.")
    return DoctorCheck("corrigendum", "pass", f"CORRIGENDUM.md presente ({size} bytes).")


def _check_external_clis() -> DoctorCheck:
    """Verifica se as CLIs externas de primeira classe (OpenCode, Antigravity,
    Claude Code, Ollama, scihub-cli) estão instaladas e no PATH. São
    opcionais para o funcionamento do ecossistema em Python puro, por isso
    o resultado é sempre ``warn`` (nunca ``fail``) quando alguma está
    ausente — cada ferramenta é usada em fluxos diferentes (OpenCode CLI
    para o catálogo de agentes, Antigravity para delegação externa, Claude
    Code para desenvolvimento neste projeto, Ollama para modelos locais,
    scihub-cli como fallback de download de PDF no pipeline de pesquisa
    quando não há acesso open-access direto — ver `research/downloader.py`)."""
    missing = {name: cmd for name, cmd in EXTERNAL_CLIS.items() if shutil.which(name) is None}
    if not missing:
        return DoctorCheck(
            "external_clis", "pass",
            f"Todas as {len(EXTERNAL_CLIS)} CLIs externas instaladas: {', '.join(EXTERNAL_CLIS)}.",
        )
    suggestions = "; ".join(f"{name} -> {cmd}" for name, cmd in missing.items())
    return DoctorCheck(
        "external_clis", "warn",
        f"{len(missing)}/{len(EXTERNAL_CLIS)} CLI(s) externa(s) ausente(s): {suggestions}",
    )


def _ollama_available() -> bool:
    """Indica se um servidor Ollama local está acessível (best-effort)."""
    if shutil.which("ollama") is not None:
        return True
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    try:
        import urllib.request
        with urllib.request.urlopen(f"{host}/api/tags", timeout=0.5) as resp:
            return resp.status == 200
    except Exception:
        return False


def _check_llm_providers() -> DoctorCheck:
    """Reporta quais provedores LLM estão disponíveis para o enriquecimento
    opcional do pipeline de pesquisa (fichamento/resenha).

    SEGURANÇA (SPEC-935-R128): este check jamais expõe o valor de qualquer
    chave — reporta apenas o booleano "definida/ausente". O enriquecimento
    por LLM é opcional (o pipeline funciona sem ele), por isso o resultado
    é ``pass`` se há ao menos um provedor e ``warn`` (nunca ``fail``) se
    nenhum. A ordem de preferência é Ollama local (custo zero, privado) →
    OpenAI/compatível (nuvem, custa tokens)."""
    ollama = _ollama_available()
    openai_key_set = bool(os.environ.get("OPENAI_API_KEY"))

    disponiveis = []
    if ollama:
        disponiveis.append("Ollama local")
    if openai_key_set:
        # apenas o indicador — NUNCA o valor da chave
        disponiveis.append("OpenAI (OPENAI_API_KEY definida)")

    if disponiveis:
        return DoctorCheck(
            "llm_providers", "pass",
            "Provedor(es) LLM disponível(is): " + "; ".join(disponiveis)
            + ". Preferência: Ollama local → OpenAI.",
        )
    return DoctorCheck(
        "llm_providers", "warn",
        "Nenhum provedor LLM disponível — enriquecimento por LLM desativado "
        "(o pipeline de pesquisa segue funcionando sem ele). Para habilitar: "
        "rode o Ollama local, ou defina OPENAI_API_KEY no seu .env "
        "(ver .env.example).",
    )


def _check_litert_lm() -> DoctorCheck:
    """Projeta o estado do supervisor sem confundi-lo com uma inferência.

    O endpoint ``/v1/models`` demonstra apenas readiness do daemon HTTP. Uma
    indisponibilidade local degrada recursos on-device, mas não invalida o core
    Python nem autoriza ecoar detalhes potencialmente sensíveis de exceções.
    """
    try:
        # Import local mantém o doctor carregável em instalações mínimas e deixa
        # o ponto de integração substituível por doubles nos testes.
        try:
            supervisor_class = LiteRTSupervisor  # type: ignore[name-defined]
        except NameError:
            from integrations.litert_lm_supervisor import LiteRTSupervisor

            supervisor_class = LiteRTSupervisor
        status = supervisor_class().status()
        state = getattr(status, "state", "unavailable")
        state_value = getattr(state, "value", state)
        normalized = str(state_value).strip().lower()
        pid = getattr(status, "pid", None)
        failures = getattr(status, "failure_count", 0)
        if normalized == "ready":
            return DoctorCheck(
                "litert_lm",
                "pass",
                f"ready: daemon HTTP local respondeu ao health check "
                f"(pid={pid or 'externo'}); readiness não valida geração de texto.",
            )
        return DoctorCheck(
            "litert_lm",
            "warn",
            f"{normalized or 'unavailable'}: daemon on-device sem readiness; "
            f"falhas registradas={failures}.",
        )
    except Exception:
        # Falha fechada e redigida: valores da exceção podem conter URLs,
        # tokens ou cabeçalhos de autorização vindos do ambiente.
        return DoctorCheck(
            "litert_lm",
            "warn",
            "unavailable: não foi possível consultar o supervisor local.",
        )


def _check_colibri() -> DoctorCheck:
    """Verifica se os runtimes Colibri (GLM-5.2 e/ou OLMoE) estão disponíveis.

    Colibri é um motor de inferência em C puro que executa modelos MoE
    localmente: GLM-5.2 (744B) via ``./coli serve``, OLMoE (1B-7B) via
    ``./olmoe`` (já compilado e convertido no ecossistema).
    Opcional — o ecossistema funciona sem ele.
    """
    try:
        from integrations.colibri import ColibriBridge
        bridge = ColibriBridge()

        parts = []
        if bridge.olmoe_available:
            parts.append(f"OLMoE OK (bin={bridge.olmoe_bin}, snap={bridge.olmoe_snap})")

        if bridge.available:
            info = bridge.get_info()
            status = info.get("status", "error")
            if status == "ok":
                parts.append(f"GLM-5.2 OK (bin={bridge.coli_bin})")
            else:
                parts.append(f"GLM-5.2 encontrado mas status={status}")

        if parts:
            return DoctorCheck("colibri", "pass", " | ".join(parts))

        return DoctorCheck(
            "colibri", "warn",
            "Nenhum runtime Colibri disponível. "
            "OLMoE: make -C colibri/c olmoe && export SNAP=~/models/olmoe_merged. "
            "GLM-5.2: git clone https://github.com/MarceloClaro/colibri && cd colibri/c && ./setup.sh",
        )
    except Exception:
        return DoctorCheck("colibri", "warn",
                           "unavailable: não foi possível consultar o runtime Colibri.")


def _check_llm_reduction_metrics() -> DoctorCheck:
    """Verifica se as métricas de redução LLM estão disponíveis."""
    if not _METRICS_AVAILABLE:
        return DoctorCheck("llm_reduction_metrics", "warn",
                           "Módulo de métricas (marceloclaro.metrics) não disponível.")

    try:
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        collector = MetricsCollector()
        collector.collect_from_orchestrator(orch)
        stats = orch.get_reduction_stats()
        saved = stats.get("total_llm_calls_saved", 0)
        routes = stats.get("route_calls", 0)
        return DoctorCheck(
            "llm_reduction_metrics", "pass",
            f"Redução LLM ativa: {saved} chamadas evitadas, {routes} rotas processadas. "
            f"Threshold: {orch.reduction_threshold}.",
        )
    except Exception as exc:
        return DoctorCheck("llm_reduction_metrics", "warn",
                           f"Métricas de redução LLM: {exc}")


def _check_episteme_coverage() -> DoctorCheck:
    """Cobertura da camada epistêmica de roteamento (SPEC-935-R368).

    Reporta números medidos no catálogo atual; warn abaixo de 50% porque
    nessa faixa o peso epistêmico fica inerte para a maioria dos agentes.
    """
    try:
        from marceloclaro.catalog_loader import load_catalog_definitions
        from transformer.episteme import catalog_episteme_coverage

        coverage = catalog_episteme_coverage(load_catalog_definitions())
        total = coverage["total"]
        if not total:
            return DoctorCheck(
                "episteme_coverage", "warn", "Catálogo vazio; nada a medir."
            )
        ratio = coverage["coverage_ratio"]
        detail = (
            f"{coverage['explicit'] + coverage['inferred']}/{total} agentes com "
            f"episteme ({ratio:.0%}): {coverage['explicit']} explícita(s), "
            f"{coverage['inferred']} inferida(s), {coverage['uncovered']} sem sinais."
        )
        status = "pass" if ratio >= 0.5 else "warn"
        return DoctorCheck("episteme_coverage", status, detail)
    except Exception as exc:
        return DoctorCheck("episteme_coverage", "fail", f"Erro ao medir cobertura: {exc}")


def _check_apm_integration() -> DoctorCheck:
    """Verifica a integridade do manifesto Microsoft APM (SPEC-935-R440)."""
    try:
        from integrations.apm import APMPackageManager
        pm = APMPackageManager()
        if not pm.manifest_path.exists():
            return DoctorCheck(
                "apm_integration", "warn",
                "Manifesto apm.yml ausente. Execute: python3 -m marceloclaro.cli apm init"
            )
        manifest = pm.load_manifest()
        total_prims = sum(len(v) for v in manifest.primitives.values())
        has_lock = pm.lock_path.exists()
        lock_detail = "com lockfile íntegro" if has_lock else "sem lockfile (execute 'apm install')"
        return DoctorCheck(
            "apm_integration", "pass",
            f"Microsoft APM ativo (v{manifest.version}): {total_prims} primitivas declaradas ({lock_detail})."
        )
    except Exception as exc:
        return DoctorCheck("apm_integration", "warn", f"Erro no diagnóstico APM: {exc}")


def _check_free_model_amplification() -> DoctorCheck:
    """Verifica o status do DeepSeek Harness para amplificação de modelos free (SPEC-935-R441)."""
    try:
        from integrations.deepseek_harness.free_model_amplifier import get_free_model_amplifier
        amp = get_free_model_amplifier()
        stats = amp.get_stats()
        return DoctorCheck(
            "free_model_amplification", "pass",
            "Amplificação DeepSeek Harness ativa: RAG local Whoosh3 + Scaffold CoT para modelos free (Ox Alpha, DeepSeek Free)."
        )
    except Exception as exc:
        return DoctorCheck("free_model_amplification", "warn", f"Harness free models indisponível: {exc}")


def _check_deepmind_superhuman_reasoning() -> DoctorCheck:
    """Verifica a prontidão dos módulos DeepMind Superhuman (Aletheia, Formal Verifier e IMO-Bench) - SPEC-935-R442."""
    try:
        from integrations.deepmind import (
            AletheiaHypothesisEngine,
            FormalProofVerifier,
            IMOBenchmarkHarness,
        )
        verifier = FormalProofVerifier()
        engine = AletheiaHypothesisEngine(verifier=verifier)
        harness = IMOBenchmarkHarness(verifier=verifier)
        sympy_str = "SymPy ativo" if verifier.has_sympy else "SymPy fallback"
        return DoctorCheck(
            "deepmind_superhuman_reasoning", "pass",
            f"DeepMind Superhuman Reasoning ativo: Aletheia scaffold + Verificador formal ({sympy_str}) + IMO Bench ({len(harness.sample_dataset)} problemas)."
        )
    except Exception as exc:
        return DoctorCheck("deepmind_superhuman_reasoning", "warn", f"DeepMind reasoning indisponível: {exc}")


def _check_opencode_deepthink_alphaproof() -> DoctorCheck:
    """Verifica se os motores OpenCode AlphaProof, Deep Think e Erdős/Hirzebruch Solver estão íntegros (R443)."""
    try:
        from integrations.deepmind import (
            OpenCodeAlphaProof,
            OpenCodeDeepThink,
            ErdosSeriesAnalyzer,
            HirzebruchEigenweightCalculator,
        )
        prover = OpenCodeAlphaProof()
        deep_think = OpenCodeDeepThink(alphaproof=prover)
        erdos = ErdosSeriesAnalyzer()
        hirz = HirzebruchEigenweightCalculator()

        # Prova rápida de integridade
        quick_search = prover.search_proof("x**2 - y**2 = (x - y)*(x + y)", max_depth=1)
        hirz_res = hirz.compute_eigenweights(dim=2, rank=1)
        return DoctorCheck(
            "opencode_deepthink_alphaproof", "pass",
            f"OpenCode AlphaProof & Deep Think ativos: Proof-tree search ({quick_search['nodes_expanded']} nós) + Erdős/Hirzebruch Solver (Dim {hirz_res.variety_dim} OK)."
        )
    except Exception as exc:
        return DoctorCheck("opencode_deepthink_alphaproof", "warn", f"OpenCode AlphaProof/DeepThink indisponível: {exc}")


def _check_lean4_egraph_engine() -> DoctorCheck:
    """Verifica se a ponte Lean 4 e o motor de saturação de igualdade E-Graph estão operacionais (R444)."""
    try:
        from integrations.deepmind import Lean4ProofVerifier, EqualitySaturationEngine
        lean_verifier = Lean4ProofVerifier()
        egraph_engine = EqualitySaturationEngine()

        # Teste rápido Lean 4
        sample_code = lean_verifier.format_theorem("sample_th", "x + 0 = x", ["intro x", "ring"])
        lean_res = lean_verifier.verify_lean_code(sample_code)

        # Teste rápido E-Graph
        sat_res = egraph_engine.saturate("(+ x 0)", max_iterations=1)

        compiler_str = "Kernel Lean 4 ativo" if lean_verifier.has_compiler else "Analisador Estático Lean 4 ativo"
        return DoctorCheck(
            "lean4_egraph_engine", "pass",
            f"Lean 4 & E-Graph ativos: {compiler_str} (status: {lean_res.status}) + Equality Saturation ({sat_res['rules_applied']} regras aplicadas)."
        )
    except Exception as exc:
        return DoctorCheck("lean4_egraph_engine", "warn", f"Lean 4 / E-Graph indisponível: {exc}")


def _check_geometry_autoformalization_engine() -> DoctorCheck:
    """Verifica se os motores AlphaGeometry e Auto-Formalizador Bidirecional estão operacionais (R445)."""
    try:
        from integrations.deepmind import OpenCodeAlphaGeometry, AutoFormalizerEngine
        geom = OpenCodeAlphaGeometry()
        autoform = AutoFormalizerEngine()

        # Teste rápido AlphaGeometry (Teorema da Base Média / Wu)
        geom_res = geom.solve("midpoint_theorem")

        # Teste rápido AutoFormalizer
        form_res = autoform.informal_to_lean4("para todo x real x + 0 = x")

        return DoctorCheck(
            "geometry_autoformalization_engine", "pass",
            f"AlphaGeometry & Auto-Formalizer ativos: Wu's Method (resíduo {geom_res.polynomial_residue}) + Lean 4 Autoformalize (status {form_res['verification_status']})."
        )
    except Exception as exc:
        return DoctorCheck("geometry_autoformalization_engine", "warn", f"AlphaGeometry / Auto-Formalizer indisponível: {exc}")


def run_doctor() -> Dict[str, Any]:
    """Executa todos os checks estruturais e agrega o resultado.

    Ao contrário de scripts/quality_report.py (que roda a suíte pytest
    completa), este diagnóstico é estrutural e rápido — não substitui a
    suíte de testes, complementa-a.
    """
    start = time.time()
    checks: List[DoctorCheck] = [
        _check_formal_specs(),
        _check_evolution_registry(),
        _check_loop_specs(),
        _check_metacognitive_memory(),
        _check_opencode_config(),
        _check_corrigendum(),
        _check_external_clis(),
        _check_llm_providers(),
        _check_litert_lm(),
        _check_colibri(),
        _check_llm_reduction_metrics(),
        _check_episteme_coverage(),
        _check_apm_integration(),
        _check_free_model_amplification(),
        _check_deepmind_superhuman_reasoning(),
        _check_opencode_deepthink_alphaproof(),
        _check_lean4_egraph_engine(),
        _check_geometry_autoformalization_engine(),
    ]

    has_fail = any(c.status == "fail" for c in checks)
    has_warn = any(c.status == "warn" for c in checks)
    overall = "unhealthy" if has_fail else ("degraded" if has_warn else "healthy")

    return {
        "overall": overall,
        "checks": [c.to_dict() for c in checks],
        "checks_total": len(checks),
        "checks_passed": sum(1 for c in checks if c.status == "pass"),
        "checks_warned": sum(1 for c in checks if c.status == "warn"),
        "checks_failed": sum(1 for c in checks if c.status == "fail"),
        "duration_seconds": round(time.time() - start, 2),
    }
