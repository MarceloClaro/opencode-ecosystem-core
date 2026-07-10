# -*- coding: utf-8 -*-
"""
Helpdesk — Diagnóstico Guiado (SPEC-935-R116)
================================================
Não é um sistema de tickets: é `doctor()` traduzido para sugestões de
correção em linguagem simples, para quem não conhece o jargão interno
do ecossistema (specs, loop specs, MetaBus, etc.).

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

from typing import Any, Dict, List

from marceloclaro.doctor import run_doctor

# Sugestão de correção em linguagem simples por nome de check do doctor().
_SUGGESTIONS = {
    "specs_formais": (
        "As especificações formais do projeto (arquivos specs/SPEC-935-R*.md) "
        "não carregaram. Confirme que a pasta 'specs/' existe e não foi "
        "movida/renomeada."
    ),
    "evolution_registry": (
        "O histórico de ciclos de evolução (evolution/cycles.json) parece "
        "menor do que deveria. Isso pode indicar perda de dados — evite "
        "chamar evolution_registry.record() até investigar; compare a "
        "contagem de entradas do arquivo com o esperado antes de continuar."
    ),
    "loop_specs": (
        "Nenhum loop foi registrado ainda nesta sessão, ou algum 'loop "
        "spec' está mal-formado (falta trigger, estado terminal, ou "
        "orçamento de iterações). Se for a primeira vez rodando o "
        "orquestrador nesta execução, isso é esperado — instancie "
        "MarceloClaroOrchestrator() para registrar o loop científico "
        "(scientific-discovery) automaticamente. Caso contrário, revise a "
        "definição do loop citada no detalhe do check."
    ),
    "memoria_metacognitiva": (
        "A memória compartilhada do sistema (.mci_state/) não está "
        "acessível. Verifique se a pasta existe e se você tem permissão "
        "de escrita nela."
    ),
    "opencode_config": (
        "O arquivo opencode.json está ausente, inválido ou sem o agente "
        "'marceloclaro'. Regenere com: python3 -m integrations.opencode_cli"
    ),
    "corrigendum": (
        "O CORRIGENDUM.md (documento de correção pública de alegações) "
        "não foi encontrado ou está vazio. Não é crítico, mas é uma boa "
        "prática de transparência — ver CORRIGENDUM.md para o formato."
    ),
    "external_clis": (
        "Uma ou mais CLIs externas (OpenCode, Antigravity/agy, Claude Code, "
        "Ollama) não foram encontradas no PATH. Rode o instalador da sua "
        "plataforma (installer/README.md) ou instale manualmente — o "
        "comando exato de cada uma aparece no detalhe do check."
    ),
}


def _suggestion_for(check_name: str, detail: str) -> str:
    base = _SUGGESTIONS.get(check_name, "Consulte o detalhe do check para mais contexto.")
    if check_name == "external_clis":
        # Acrescenta os comandos de instalação exatos das CLIs ausentes,
        # extraídos do próprio texto do check (já formatado por doctor.py).
        return f"{base}\n      Detalhe: {detail}"
    return base


def run_helpdesk() -> Dict[str, Any]:
    """Roda o diagnóstico estrutural (run_doctor) e anexa, para cada check
    que não passou (warn/fail), uma sugestão de correção em linguagem
    simples. Retorna um relatório pronto para exibição no CLI."""
    report = run_doctor()
    guidance: List[Dict[str, str]] = []
    for check in report["checks"]:
        if check["status"] in ("warn", "fail"):
            guidance.append({
                "check": check["name"],
                "status": check["status"],
                "problem": check["detail"],
                "suggestion": _suggestion_for(check["name"], check["detail"]),
            })

    if report["overall"] == "healthy":
        summary = "Tudo certo! Nenhuma pendência encontrada."
    elif report["overall"] == "degraded":
        summary = f"{len(guidance)} ponto(s) de atenção (não bloqueantes) encontrados — veja as sugestões abaixo."
    else:
        summary = f"{len(guidance)} problema(s) encontrados, incluindo falhas críticas — veja as sugestões abaixo."

    return {
        "overall": report["overall"],
        "summary": summary,
        "guidance": guidance,
        "doctor_report": report,
    }
