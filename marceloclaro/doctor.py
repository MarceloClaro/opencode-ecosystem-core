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
