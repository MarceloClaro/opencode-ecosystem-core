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
    "literary": {
        "name": "Suíte de Scanners Literários",
        "desc": "8 visões literárias: narrativa, personagem, estilo, símbolos, teoria, leitor, ética e inovação",
        "arquivo": "scanners/literary_scanners.py",
    },
    "literary_research": {
        "name": "Suíte de Pesquisa Literária Internacional",
        "desc": "4 scanners: bibliografia, corpus comparativo, teoria e rigor internacional",
        "arquivo": "scanners/literary_research_scanners.py",
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

    # Determina número de runs (benchmark mode)
    benchmark_runs = args.benchmark or 1
    if benchmark_runs < 1:
        benchmark_runs = 1

    # Constrói pipeline (uma vez, reuso entre runs)
    pipeline = DiagnosticPipeline(domain=domain)

    if args.format == "texto" and benchmark_runs > 1:
        print(f"\n📊 Benchmark mode — {benchmark_runs} runs")
        print(f"{'='*65}")

    t0 = time.time()

    if args.format == "texto":
        print(f"\n🔬 Pipeline de Diagnóstico — Domínio: {domain}")
        print(f"   Corpus: {'arquivo' if args.file else 'ecossistema auto-descoberto'}")
        if args.deep:
            print(f"   Modo PROFUNDO (roadmap evolutivo + sucessores)")
        print("=" * 65)

    try:
        if benchmark_runs > 1:
            # Benchmark: múltiplas runs, coleta estatísticas
            durations = []
            timings_samples: list[dict] = []
            for i in range(benchmark_runs):
                run_t0 = time.time()
                result = pipeline.run(
                    corpus=corpus,
                    domain=domain,
                    deep=args.deep,
                    include_social=args.social or args.all,
                    include_legal_impact=args.legal or args.all,
                )
                run_dur = time.time() - run_t0
                durations.append(run_dur)
                timings_samples.append(result.get("timings", {}))
                if args.format == "texto":
                    print(f"   Run {i+1:2d}/{benchmark_runs}: {run_dur:.3f}s")
            import statistics
            avg = statistics.mean(durations)
            stdev = statistics.stdev(durations) if len(durations) > 1 else 0
            print(f"\n{'='*65}")
            print(f"📊 Benchmark: {benchmark_runs} runs")
            print(f"   Média: {avg:.3f}s | Desvio: {stdev:.3f}s | "
                  f"Min: {min(durations):.3f}s | Max: {max(durations):.3f}s")
            # Média dos timings por scanner
            if timings_samples:
                keys = set()
                for s in timings_samples:
                    keys.update(s.keys())
                print(f"\n   Timing médio por scanner:")
                for k in sorted(keys):
                    vals = [s.get(k, 0) for s in timings_samples]
                    avg_k = statistics.mean(vals)
                    pct = avg_k / avg * 100 if avg > 0 else 0
                    print(f"     {k:20s}: {avg_k:.3f}s ({pct:.0f}%)")
            print(f"{'='*65}\n")
        else:
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
    duracao_total = result.get("duration_s", duracao)
    print(f"\n⏱  Duração total: {duracao_total:.2f}s")
    timings = result.get("timings", {})
    if timings:
        timing_items = sorted(timings.items(), key=lambda x: x[1], reverse=True)
        parts = []
        for name, t in timing_items:
            if t >= 0.01:
                pct = (t / duracao_total * 100) if duracao_total > 0 else 0
                parts.append(f"{name}: {t:.2f}s ({pct:.0f}%)")
        if parts:
            print(f"   └─ {' | '.join(parts)}")
    print("=" * 65)

    noo = result.get("noological", {})
    teleo = result.get("teleological", {})
    evol = result.get("evolutionary", {})
    pot = result.get("potentiality", {})
    rev = result.get("reversa", {})
    rdmp = result.get("roadmap", {})
    epist = result.get("epistemic_opportunities", {})
    succ = result.get("successors", {})

    # ── 1. Scanner Noológico ──────────────────────────────────────────────
    if "error" in noo:
        print(f"\n❌ Noológico: erro — {noo['error']}")
    else:
        coverage = noo.get("coverage", 0)
        gaps = noo.get("gaps", [])
        status_c = "✅" if coverage >= 80 else ("⚠️" if coverage >= 40 else "❌")
        print(f"\n{status_c} Noológico — Cobertura: {coverage}% | {len(gaps)} gaps")
        if gaps and args.verbose:
            for g in gaps[:5]:
                print(f"     • {g}")

    # ── 2. Scanner Teleológico ────────────────────────────────────────────
    if "error" in teleo:
        print(f"❌ Teleológico: erro — {teleo['error']}")
    elif "skipped" in teleo:
        print(f"⏭  Teleológico: {teleo['skipped']}")
    else:
        score = teleo.get("score", 0)
        gaps_t = teleo.get("gaps", [])
        status_t = "✅" if score >= 0.8 else ("⚠️" if score >= 0.4 else "❌")
        print(f"{status_t} Teleológico — Score: {score:.2f} | {len(gaps_t)} gaps")
        if gaps_t and args.verbose:
            for g in gaps_t[:5]:
                dim = g.get("dimension", g.get("dim_key", "?"))
                sev = g.get("severity", "?")
                desc = g.get("description", "")[:80]
                print(f"     • [{sev}] {dim}: {desc}")

    # ── 3. Potencialidade ─────────────────────────────────────────────────
    if "error" in pot:
        print(f"❌ Potencialidade: erro — {pot['error']}")
    else:
        comps = pot.get("total_components", 0)
        caps = pot.get("total_capabilities", 0)
        core = pot.get("core_count", 0)
        miss = pot.get("missing_count", 0)
        tops = pot.get("top_latent", [])
        print(f"🔮 Potencialidade — {comps} componentes · {caps} capacidades · {core} core · {miss} lacunas")
        if tops and args.verbose:
            for t in tops[:5]:
                cap = t.get("capability", str(t))
                prio = t.get("priority", "")
                print(f"     • {cap} [{prio}]")

    # ── 4. Evolutivo ──────────────────────────────────────────────────────
    gaps_total = evol.get("total_gaps", 0)
    absents = evol.get("absent_categories", 0)
    teleo_gaps = evol.get("teleological_gaps", 0)
    print(f"🧬 Evolutivo — {gaps_total} gaps totais (noológicos: {absents}, teleológicos: {teleo_gaps})")
    rec = evol.get("recommendation", "")
    if rec:
        print(f"     → {rec[:150]}")

    # ── 5. Engenharia Reversa ─────────────────────────────────────────────
    if "error" in rev:
        print(f"❌ Eng. Reversa: erro — {rev['error']}")
    else:
        rscore = rev.get("score", "N/A")
        rfindings = rev.get("findings", [])
        rrecs = rev.get("recommendations", [])
        print(f"🔍 Eng. Reversa — Score: {rscore} | {len(rfindings)} achados | {len(rrecs)} recomendações")

    # ── 6. Impacto Social (se executado) ──────────────────────────────────
    if "social_impact" in result:
        si = result["social_impact"]
        if "error" in si:
            print(f"❌ Impacto Social: {si['error']}")
        else:
            print(f"🌍 Impacto Social — SROI: {si.get('sroi_ratio', 'N/A')}")

    # ── 7. Impacto Jurídico (se executado) ────────────────────────────────
    if "legal_impact" in result:
        li = result["legal_impact"]
        if "error" in li:
            print(f"❌ Impacto Jurídico: {li['error']}")
        else:
            lr = li.get("legal_readiness", "N/A")
            mg = li.get("metacognitive_gain_score", "N/A")
            print(f"⚖️  Impacto Jurídico — Prontidão: {lr} | Ganho metacognitivo: {mg}")

    # ── 7.5 Scanners Literários (domain=literary ou include_literary) ─────
    if "literary" in result:
        lit = result["literary"]
        if "error" in lit:
            print(f"❌ Literário: {lit['error']}")
        else:
            score = lit.get("literary_excellence_score", 0)
            grade = lit.get("grade", "N/A")
            count = lit.get("scanner_count", 0)
            print(f"📚 Literário — {count} scanners · Score: {score}/100 · Grau: {grade}")
            if args.verbose:
                for sid, payload in list(lit.get("results", {}).items())[:8]:
                    print(f"     • {sid}: {payload.get('score', 0)}/100 ({payload.get('grade', 'N/A')})")

    # ── 7.6 Pesquisa Literária Internacional ──────────────────────────────
    if "literary_research" in result:
        lrs = result["literary_research"]
        if "error" in lrs:
            print(f"❌ Pesquisa Literária: {lrs['error']}")
        else:
            score = lrs.get("international_research_rigor_score", 0)
            grade = lrs.get("grade", "N/A")
            count = lrs.get("scanner_count", 0)
            print(f"📖 Pesquisa Literária — {count} scanners · Rigor internacional: {score}/100 · Grau: {grade}")
            if args.verbose:
                for sid, payload in list(lrs.get("results", {}).items())[:4]:
                    print(f"     • {sid}: {payload.get('score', 0)}/100 ({payload.get('grade', 'N/A')})")

    # ── 8. Camadas do ecossistema (se disponível) ─────────────────────────
    if "ecosystem_layers" in result:
        layers = result["ecosystem_layers"]
        print(f"\n📐 Camadas do Ecossistema ({len(layers)}):")
        for name, data in sorted(layers.items())[:10]:
            pct = data.get("coverage_pct", 0)
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            print(f"     {bar} {name}: {pct}%")

    # ── 9. Roadmap Evolutivo (modo deep) ──────────────────────────────────
    if rdmp and "error" not in rdmp:
        print(f"\n🧭 Roadmap Evolutivo:")
        print(f"     Quick wins: {rdmp.get('quick_wins', 'N/A')} | "
              f"Fundações: {rdmp.get('foundations', 'N/A')} | "
              f"Fronteiras: {rdmp.get('frontiers', 'N/A')}")
        bns = rdmp.get("bottlenecks", [])
        if bns:
            print(f"     Gargalos ({len(bns)}):")
            for b in bns[:5]:
                print(f"       • {str(b)[:100]}")
        seq = rdmp.get("logical_sequence", [])
        if seq and args.verbose:
            print(f"     Sequência lógica ({len(seq)} passos):")
            for s in seq[:8]:
                print(f"       → {s}")

    # ── 10. Oportunidades Epistêmicas (modo deep) ─────────────────────────
    if epist and "error" not in epist:
        total_opps = epist.get("total", 0)
        bts = epist.get("breakthroughs", 0)
        print(f"\n💡 Oportunidades Epistêmicas: {total_opps} total | {bts} breakthrough")
        top_opps = epist.get("top", [])
        if top_opps and args.verbose:
            for opp in top_opps[:5]:
                print(f"     • {opp.get('label', opp.get('dimension', str(opp)))[:80]}")

    # ── 11. Sucessores (modo deep) ────────────────────────────────────────
    if succ and "error" not in succ:
        total_succ = succ.get("total", 0)
        imm = succ.get("immediate", 0)
        print(f"🔗 Sucessores: {total_succ} total | {imm} imediatos")
        top_succ = succ.get("top", [])
        if top_succ and args.verbose:
            for s in top_succ[:5]:
                print(f"     • {s.get('label', s.get('name', str(s)))[:80]}")

    print(f"\n{'=' * 65}")
    print(f"🔬 Diagnóstico concluído em {duracao_total:.2f}s")


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
    p_diag.add_argument("--benchmark", "-b", type=int, default=0, nargs="?",
                        const=5, metavar="N",
                        help="Modo benchmark: executa N runs (padrão: 5) e mostra média/desvio")
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
