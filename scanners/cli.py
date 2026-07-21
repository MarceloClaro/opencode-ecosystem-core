#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI do Pipeline de Diagnóstico — 5 Scanners
=============================================
Entrypoint dedicado para o comando /diagnose do OpenCode CLI.

Uso:
    python3 -m scanners.cli diagnose <arquivo>              # Varre arquivo
    python3 -m scanners.cli diagnose --domain ecosystem     # Varre ecossistema
    python3 -m scanners.cli diagnose --domain ecosystem --deep  # Modo completo
    python3 -m scanners.cli diagnose --domain ecosystem --json   # JSON puro
    python3 -m scanners.cli status                         # Status dos scanners
    python3 -m scanners.cli list                           # Lista scanners
"""

import argparse
import json
import os
import sys
import time
from typing import Any, Dict


# Garante path do projeto
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# ──────────────────────────────────────────────────────────────────────────────
# Scanners disponíveis
# ──────────────────────────────────────────────────────────────────────────────

SCANNER_INFO = {
    "noological": {
        "name": "Scanner Noológico",
        "desc": "Cobertura epistemológica — mapeia dimensões do conhecimento presentes/ausentes",
        "arquivo": "scanners/noological_scanner.py",
    },
    "teleological": {
        "name": "Scanner Teleológico",
        "desc": "Lacunas entre metas do ecossistema e capacidades reais dos agentes",
        "arquivo": "scanners/teleological_scanner.py",
    },
    "evolutionary": {
        "name": "Scanner Evolutivo",
        "desc": "Roadmap evolutivo — rotas de melhoria, trajetórias M1–M5",
        "arquivo": "scanners/evolutionary_pipeline.py",
    },
    "potentiality": {
        "name": "Scanner de Potencialidade",
        "desc": "Capacidades latentes, gaps de inovação e DNA do ecossistema",
        "arquivo": "scanners/potentiality_scanner.py",
    },
    "social": {
        "name": "Scanner de Impacto Social",
        "desc": "SROI, Teoria da Mudança, ODS, B-Impact Score",
        "arquivo": "scanners/social_impact_scanner.py",
    },
}

SCANNERS_ADICIONAIS = {
    "legal_impact": {
        "name": "Scanner de Impacto Jurídico",
        "desc": "Prontidão jurídica e ganho metacognitivo jurídico (SPEC-924)",
        "arquivo": "scanners/legal_impact_scanner.py",
    },
    "reversa": {
        "name": "Scanner de Engenharia Reversa",
        "desc": "Análise de código legado e extração de conhecimento",
        "arquivo": "scanners/reversa_scanner.py",
    },
}


# ──────────────────────────────────────────────────────────────────────────────
# Comando: list
# ──────────────────────────────────────────────────────────────────────────────

def cmd_list() -> None:
    """Lista os scanners disponíveis."""
    print("=" * 65)
    print("🔬 SCANNERS DISPONÍVEIS — Pipeline de Diagnóstico")
    print("=" * 65)
    for sid, info in {**SCANNER_INFO, **SCANNERS_ADICIONAIS}.items():
        status = "✅" if os.path.exists(os.path.join(ROOT, info["arquivo"])) else "❌"
        print(f"\n{status} {info['name']} ({sid})")
        print(f"   {info['desc']}")
        print(f"   Arquivo: {info['arquivo']}")


# ──────────────────────────────────────────────────────────────────────────────
# Comando: status
# ──────────────────────────────────────────────────────────────────────────────

def cmd_status() -> None:
    """Exibe status detalhado de cada scanner."""
    print("=" * 65)
    print("🔬 STATUS DOS SCANNERS")
    print("=" * 65)

    for sid, info in {**SCANNER_INFO, **SCANNERS_ADICIONAIS}.items():
        arquivo = os.path.join(ROOT, info["arquivo"])
        if os.path.exists(arquivo):
            tamanho = os.path.getsize(arquivo)
            with open(arquivo, "r", encoding="utf-8", errors="replace") as f:
                primeira_linha = f.readline().strip()
            linhas = sum(1 for _ in open(arquivo, "r", encoding="utf-8", errors="replace"))
            print(f"\n✅ {info['name']}")
            print(f"   Linhas: {linhas} | Tamanho: {tamanho:,} bytes")
            print(f"   Shebang: {primeira_linha if primeira_linha.startswith('#') else '(none)'}")
        else:
            print(f"\n❌ {info['name']} — ARQUIVO AUSENTE: {info['arquivo']}")


# ──────────────────────────────────────────────────────────────────────────────
# Comando: diagnose
# ──────────────────────────────────────────────────────────────────────────────

def cmd_diagnose(args: argparse.Namespace) -> None:
    """Executa o pipeline de diagnóstico."""
    from scanners import DiagnosticPipeline

    # Determina corpus
    if args.file:
        filepath = os.path.join(ROOT, args.file) if not os.path.isabs(args.file) else args.file
        if not os.path.exists(filepath):
            print(f"❌ Arquivo não encontrado: {filepath}", file=sys.stderr)
            sys.exit(1)
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            corpus = f.read()
        domain = args.domain or "geral"
    else:
        corpus = "ecosystem"
        domain = args.domain or "ecosystem"

    # Constrói pipeline
    pipeline = DiagnosticPipeline(domain=domain)
    t0 = time.time()

    if args.format == "texto":
        print(f"\n🔬 Pipeline de Diagnóstico — Domínio: {domain}")
        print(f"   Corpus: {'arquivo' if args.file else 'ecossistema auto-descoberto'}")
        if args.deep:
            print(f"   Modo PROFUNDO (roadmap evolutivo + sucessores)")
        print("=" * 65)

    try:
        result = pipeline.run(
            corpus=corpus,
            domain=domain,
            deep=args.deep,
            include_social=args.social or args.all,
            include_legal_impact=args.legal or args.all,
        )
    except Exception as e:
        print(f"❌ Erro no pipeline: {e}", file=sys.stderr)
        sys.exit(1)

    duracao = time.time() - t0

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # ── Formato texto (resumido) ───────────────────────────────────────────
    print(f"\n⏱  Duração: {duracao:.2f}s")
    print("=" * 65)

    noo = result.get("noological", {})
    teleo = result.get("teleological", {})
    evol = result.get("evolutionary", {})
    pot = result.get("potentiality", {})
    rev = result.get("reversa", {})

    # 1. Scanner Noológico
    if "error" in noo:
        print(f"\n❌ Scanner Noológico: erro — {noo['error']}")
    else:
        coverage = noo.get("coverage", 0)
        gaps = noo.get("gaps", [])
        status_cobertura = "✅" if coverage >= 80 else ("⚠️" if coverage >= 40 else "❌")
        print(f"\n{status_cobertura} Noológico — Cobertura: {coverage}% | {len(gaps)} gaps")
        if gaps and args.verbose:
            for g in gaps[:5]:
                print(f"     • {g}")

    # 2. Scanner Teleológico
    if "error" in teleo:
        print(f"❌ Teleológico: erro — {teleo['error']}")
    elif "skipped" in teleo:
        print(f"⏭  Teleológico: {teleo['skipped']}")
    else:
        score = teleo.get("score", 0)
        gaps_t = teleo.get("gaps", [])
        status_t = "✅" if score >= 0.8 else ("⚠️" if score >= 0.4 else "❌")
        print(f"{status_t} Teleológico — Score: {score:.2f} | {len(gaps_t)} gaps teleológicos")
        if gaps_t and args.verbose:
            for g in gaps_t[:5]:
                dim = g.get("dimension", g.get("dim_key", "?"))
                sev = g.get("severity", "?")
                desc = g.get("description", "")[:80]
                print(f"     • [{sev}] {dim}: {desc}")

    # 3. Potencialidade
    if "error" in pot:
        print(f"❌ Potencialidade: erro — {pot['error']}")
    else:
        tops = pot.get("top_latent", [])
        print(f"🔮 Potencialidade — {len(tops)} potenciais latentes detectados")
        if tops and args.verbose:
            for t in tops[:3]:
                print(f"     • {str(t)[:80]}")

    # 4. Evolutivo
    print(f"🧬 Evolutivo — {evol.get('total_gaps', 0)} gaps totais")
    rec = evol.get("recommendation", "")
    if rec and args.verbose:
        print(f"     Recomendação: {rec[:120]}")

    # 5. Engenharia Reversa
    if "error" in rev:
        print(f"❌ Eng. Reversa: erro — {rev['error']}")
    else:
        print(f"🔍 Eng. Reversa — Score: {rev.get('score', 'N/A')}")

    # 6. Impacto Social (se executado)
    if "social_impact" in result:
        si = result["social_impact"]
        if "error" in si:
            print(f"❌ Impacto Social: {si['error']}")
        else:
            print(f"🌍 Impacto Social — SROI: {si.get('sroi_ratio', 'N/A')}")

    # 7. Impacto Jurídico (se executado)
    if "legal_impact" in result:
        li = result["legal_impact"]
        if "error" in li:
            print(f"❌ Impacto Jurídico: {li['error']}")
        else:
            print(f"⚖️  Impacto Jurídico — Prontidão: {li.get('legal_readiness', 'N/A')}")

    # 8. Camadas do ecossistema (se disponível)
    if "ecosystem_layers" in result:
        layers = result["ecosystem_layers"]
        print(f"\n📐 Camadas do Ecossistema ({len(layers)}):")
        for name, data in sorted(layers.items())[:8]:
            pct = data.get("coverage_pct", 0)
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            print(f"     {bar} {name}: {pct}%")

    print(f"\n{'=' * 65}")
    print(f"🔬 Diagnóstico concluído em {duracao:.2f}s")


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="🔬 Pipeline de Diagnóstico — 5 Scanners",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python3 -m scanners.cli diagnose --domain ecosystem
  python3 -m scanners.cli diagnose --domain ecosystem --deep
  python3 -m scanners.cli diagnose --domain ecosystem --json
  python3 -m scanners.cli diagnose README.md --verbose
  python3 -m scanners.cli status
  python3 -m scanners.cli list
        """,
    )
    parser.add_argument("--format", choices=["texto", "json"], default="texto",
                        help="Formato de saída (padrão: texto)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Exibe detalhes dos gaps")

    subparsers = parser.add_subparsers(dest="comando", help="Comando")

    # diagnose
    p_diag = subparsers.add_parser("diagnose", help="Executa pipeline de diagnóstico")
    p_diag.add_argument("file", nargs="?", default=None,
                        help="Arquivo a escanear (opcional; default: ecossistema)")
    p_diag.add_argument("--domain", "-d", default=None,
                        help="Domínio de pesquisa (ex: ecosystem, machine_learning, psicologia)")
    p_diag.add_argument("--deep", action="store_true",
                        help="Modo profundo: roadmap evolutivo + priorização + sucessores")
    p_diag.add_argument("--social", action="store_true",
                        help="Incluir scanner de impacto social")
    p_diag.add_argument("--legal", action="store_true",
                        help="Incluir scanner de impacto jurídico")
    p_diag.add_argument("--all", action="store_true",
                        help="Incluir todos os scanners opcionais (social, legal)")

    # status / list
    subparsers.add_parser("status", help="Status dos scanners")
    subparsers.add_parser("list", help="Lista scanners disponíveis")

    args = parser.parse_args()

    if args.comando == "diagnose":
        cmd_diagnose(args)
    elif args.comando == "status":
        cmd_status()
    elif args.comando == "list":
        cmd_list()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
