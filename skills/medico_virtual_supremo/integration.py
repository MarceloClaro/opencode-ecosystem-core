# -*- coding: utf-8 -*-
"""
Interface de Integração CLI — Médico Virtual Supremo
======================================================
Camada unificada para integração com OpenCode CLI, Antigravity CLI e Claude CLI.
Fornece uma interface programática que os três CLIs consomem.

Uso:
    # OpenCode CLI (command template)
    python3 -m skills.medico_virtual_supremo.integration analisar <modo> <request>

    # Antigravity Bridge (delegate)
    python3 -m skills.medico_virtual_supremo.integration antigravity <modo> <request>

    # Claude CLI (tool call)
    python3 -m skills.medico_virtual_supremo.integration claude <modo> <request>
"""

import argparse
import json
import sys
import os
from typing import Any, Dict, Optional

# Garante path do projeto
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def analisar_caso(
    modo: str,
    request: str,
    patient: Optional[Dict[str, Any]] = None,
    clinical_data: Optional[Dict[str, Any]] = None,
    formato: str = "yaml",
) -> Dict[str, Any]:
    """
    Função principal de análise clínica — consumida por todos os CLIs.

    Args:
        modo: professional_cds | patient_education | research | simulation
        request: Descrição do caso clínico.
        patient: Dados demográficos opcionais.
        clinical_data: Dados clínicos opcionais.
        formato: 'yaml' (padrão) ou 'json' ou 'resumido'.

    Returns:
        Dict com resultado no formato solicitado.
    """
    from skills.medico_virtual_supremo.skill import MedicoVirtualSupremoSkill

    skill = MedicoVirtualSupremoSkill()
    resultado = skill.analisar(
        modo=modo,
        request=request,
        patient=patient or {},
        clinical_data=clinical_data or {},
    )

    corpo = resultado.get("resposta_medico_virtual_supremo", resultado)

    if formato == "resumido":
        return _resumir_resultado(corpo)
    return resultado


def _resumir_resultado(corpo: Dict[str, Any]) -> Dict[str, Any]:
    """Produz versão resumida para display em terminal."""
    meta = corpo.get("meta", {})
    safety = corpo.get("safety", {})
    clinico = corpo.get("clinical_summary", {})
    hipoteses = corpo.get("assessment", {}).get("hypotheses", [])
    auditoria = corpo.get("audit", {})
    plano = corpo.get("plan_for_human_review", {})

    return {
        "modo": meta.get("mode", "?"),
        "timestamp": meta.get("timestamp_utc", "?"),
        "emergencia": safety.get("emergency_detected", False),
        "problema": clinico.get("problem_representation", "")[:120],
        "hipoteses": [
            {
                "nome": h.get("name", "?")[:60],
                "status": h.get("status", "?"),
                "confianca": h.get("confidence", "?"),
            }
            for h in hipoteses[:3]
        ],
        "hipoteses_graves": [
            h.get("name", "?")
            for h in hipoteses
            if h.get("status") == "grave_não_perder"
        ],
        "acoes_imediatas": plano.get("immediate_actions", []),
        "sinais_alarme": plano.get("red_flags", [])[:3],
        "checks_ok": len(auditoria.get("checks_passed", [])),
        "checks_falha": len(auditoria.get("checks_failed", [])),
        "revisao_humana": auditoria.get("human_review_required", True),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Interface OpenCode CLI
# ──────────────────────────────────────────────────────────────────────────────

def cli_opencode(args: argparse.Namespace, patient=None, clinical_data=None) -> None:
    """Handler para o comando /medico do OpenCode CLI."""
    try:
        resultado = analisar_caso(
            modo=args.modo,
            request=args.request,
            patient=patient,
            clinical_data=clinical_data,
            formato=args.formato,
        )
        if args.formato == "resumido":
            _print_resumido(resultado)
        elif args.formato == "json":
            print(json.dumps(resultado, ensure_ascii=False, indent=2))
        else:
            # YAML-like output
            _print_yaml(resultado)
    except Exception as e:
        print(f"Erro na análise clínica: {e}", file=sys.stderr)
        sys.exit(1)


def _print_resumido(r: Dict[str, Any]) -> None:
    """Exibe resultado resumido formatado para terminal."""
    print("=" * 60)
    print(f"🏥 MÉDICO VIRTUAL SUPREMO — Análise Clínica")
    print("=" * 60)
    print(f"Modo:        {r['modo']}")
    print(f"Emergência:  {'🚨 SIM' if r['emergencia'] else '✅ Não'}")
    print(f"Problema:    {r['problema']}")
    print()
    if r['emergencia']:
        print("🚨 ATENÇÃO: Emergência detectada! Acione SAMU 192.")
        print()
    if r['hipoteses']:
        print("📋 Hipóteses:")
        for h in r['hipoteses']:
            status_icon = {"provável": "📌", "grave_não_perder": "🚨", "alternativa": "🔍"}
            icon = status_icon.get(h['status'], "•")
            print(f"  {icon} {h['nome']} ({h['status']}, confiança: {h['confianca']})")
    print()
    if r['acoes_imediatas']:
        print("⚡ Ações imediatas sugeridas:")
        for a in r['acoes_imediatas']:
            print(f"  → {a}")
    if r['sinais_alarme']:
        print("⚠️  Sinais de alarme:")
        for s in r['sinais_alarme']:
            print(f"  • {s}")
    print()
    print(f"✓ {r['checks_ok']} checks de segurança OK")
    if r['checks_falha']:
        print(f"✗ {r['checks_falha']} checks com falha — revisão prioritária")
    print(f"👤 Revisão humana: {'OBRIGATÓRIA' if r['revisao_humana'] else 'recomendada'}")
    print("=" * 60)


def _print_yaml(r: Dict[str, Any]) -> None:
    """Exibe resultado em formato YAML-like."""
    corpo = r.get("resposta_medico_virtual_supremo", r)

    def _print_dict(d, indent=0):
        prefix = "  " * indent
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, (dict, list)):
                    print(f"{prefix}{k}:")
                    _print_dict(v, indent + 1)
                else:
                    print(f"{prefix}{k}: {v}")
        elif isinstance(d, list):
            for item in d:
                if isinstance(item, dict):
                    print(f"{prefix}-")
                    _print_dict(item, indent + 2)
                else:
                    print(f"{prefix}- {item}")

    _print_dict(corpo)


# ──────────────────────────────────────────────────────────────────────────────
# Interface Antigravity CLI
# ──────────────────────────────────────────────────────────────────────────────

def cli_antigravity(args: argparse.Namespace, patient=None, clinical_data=None) -> None:
    """Handler para delegação Antigravity."""
    # Verifica se Antigravity está disponível
    try:
        from integrations.antigravity.bridge import AntigravityBridge
        bridge = AntigravityBridge()
    except ImportError:
        bridge = None

    if bridge and bridge.available:
        # Antigravity disponível: delega análise
        prompt = (
            f"Analise o seguinte caso clínico como Médico Virtual Supremo.\n"
            f"Modo: {args.modo}\n"
            f"Queixa: {args.request}\n"
            f"Paciente: {args.patient or 'não informado'}\n"
            f"Dados clínicos: {args.clinical_data or 'não informados'}\n"
            f"\nProduza saída no formato resposta_medico_virtual_supremo YAML."
        )
        result = bridge.delegate(prompt, agent="medico-virtual-supremo")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # Fallback: análise local
        print("Antigravity CLI não disponível — usando análise local.", file=sys.stderr)
        resultado = analisar_caso(args.modo, args.request, formato="resumido")
        _print_resumido(resultado)


# ──────────────────────────────────────────────────────────────────────────────
# Interface Claude CLI
# ──────────────────────────────────────────────────────────────────────────────

def cli_claude(args: argparse.Namespace, patient=None, clinical_data=None) -> None:
    """Handler para Claude CLI — produz saída formatada para Claude Code."""
    resultado = analisar_caso(
        modo=args.modo,
        request=args.request,
        formato="json",
    )

    # Claude prefere JSON estruturado
    output = {
        "tool": "medico-virtual-supremo",
        "version": "2.0.0",
        "result": resultado.get("resposta_medico_virtual_supremo", resultado),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


# ──────────────────────────────────────────────────────────────────────────────
# MetaBus Status
# ──────────────────────────────────────────────────────────────────────────────

def cli_metabus(args: argparse.Namespace) -> None:
    """Exibe status da integração MetaBus."""
    try:
        from skills.medico_virtual_supremo.metabus_integration import (
            status_metabus, obtermemoriametacognitiva
        )
        status = status_metabus()
        print("=" * 60)
        print("🧠 MetaBus — Status da Integração")
        print("=" * 60)
        print(f"Disponível: {'✅ SIM' if status.get('disponivel') else '❌ NÃO'}")
        if not status.get("disponivel"):
            print(f"Motivo: {status.get('motivo', 'desconhecido')}")
            return
        print(f"Memória episódica: {status.get('episodic_memory_size', '?')} entradas")
        print(f"Confiança geral (medico:skill): {status.get('confidence_medico_skill', 'N/A')}")
        print(f"Confiança segurança (medico:safety): {status.get('confidence_medico_safety', 'N/A')}")
        topicos = status.get("topicos_medico", {})
        if topicos:
            print(f"\nTópicos monitorados: {len(topicos)}")
            for k, v in sorted(topicos.items()):
                print(f"  {k}: {v:.3f}")

        # Últimas reflexões
        print("\n📝 Últimas reflexões na memória:")
        recentes = obtermemoriametacognitiva(limit=3)
        for r in recentes:
            ts = r.get("timestamp", "?")[11:19] if len(r.get("timestamp", "")) > 19 else r.get("timestamp", "?")
            ctx = r.get("context", "")[:60]
            score = r.get("score", "?")
            print(f"  [{ts}] score={score} | {ctx}")
    except ImportError as e:
        print(f"❌ MetaBus não disponível: {e}")
    except Exception as e:
        print(f"❌ Erro ao consultar MetaBus: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# CLI Entrypoint
# ──────────────────────────────────────────────────────────────────────────────

def _add_globais(p: argparse.ArgumentParser) -> None:
    """Adiciona argumentos globais a um parser (evita conflito de parents)."""
    p.add_argument(
        "--formato", choices=["yaml", "json", "resumido"], default="resumido",
        help="Formato de saída (padrão: resumido)",
    )
    p.add_argument(
        "--patient", type=str, default=None,
        help="Dados do paciente em JSON (opcional)",
    )
    p.add_argument(
        "--clinical-data", type=str, default=None,
        help="Dados clínicos em JSON (opcional)",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Médico Virtual Supremo — Interface de Integração CLI",
    )
    # NOTA: --formato, --patient e --clinical-data vão nos subparsers, não no main
    # para evitar conflito de defaults entre main e subparser.

    subparsers = parser.add_subparsers(dest="comando", help="CLI alvo")

    # OpenCode CLI
    p_oc = subparsers.add_parser("analisar", help="Analisar caso clínico (OpenCode CLI)")
    _add_globais(p_oc)
    p_oc.add_argument("modo", choices=["professional_cds", "patient_education", "research", "simulation"])
    p_oc.add_argument("request", type=str, help="Descrição do caso clínico")

    # Antigravity CLI
    p_ag = subparsers.add_parser("antigravity", help="Delegar para Antigravity CLI")
    _add_globais(p_ag)
    p_ag.add_argument("modo", choices=["professional_cds", "patient_education", "research", "simulation"])
    p_ag.add_argument("request", type=str, help="Descrição do caso clínico")

    # Claude CLI
    p_cl = subparsers.add_parser("claude", help="Produzir saída para Claude CLI")
    _add_globais(p_cl)
    p_cl.add_argument("modo", choices=["professional_cds", "patient_education", "research", "simulation"])
    p_cl.add_argument("request", type=str, help="Descrição do caso clínico")

    # Urgência
    p_ur = subparsers.add_parser("urgencia", help="Avaliar urgência/emergência")
    _add_globais(p_ur)
    p_ur.add_argument("request", type=str, help="Descrição dos sintomas")

    # MetaBus
    p_mb = subparsers.add_parser("metabus", help="Status da integração MetaBus")
    _add_globais(p_mb)

    args = parser.parse_args()

    # Parse JSON args
    patient = json.loads(args.patient) if getattr(args, 'patient', None) else None
    clinical_data = json.loads(args.clinical_data) if getattr(args, 'clinical_data', None) else None

    if args.comando == "analisar":
        cli_opencode(args, patient=patient, clinical_data=clinical_data)
    elif args.comando == "antigravity":
        cli_antigravity(args, patient=patient, clinical_data=clinical_data)
    elif args.comando == "claude":
        cli_claude(args, patient=patient, clinical_data=clinical_data)
    elif args.comando == "metabus":
        cli_metabus(args)
    elif args.comando == "urgencia":
        _avaliar_urgencia(args.request)
    else:
        parser.print_help()


def _avaliar_urgencia(request: str) -> None:
    """Avalia rapidamente se há urgência/emergência."""
    from skills.medico_virtual_supremo.skill import MedicoVirtualSupremoSkill
    skill = MedicoVirtualSupremoSkill()
    emergencia, motivo = skill._detectar_emergencia(request, {})
    if emergencia:
        print("🚨 EMERGÊNCIA DETECTADA")
        print(f"Motivo: {motivo}")
        print("Ação: Acionar SAMU 192 imediatamente.")
    else:
        print("✅ Nenhum sinal de emergência detectado.")
        print("Recomendação: Busque avaliação médica para diagnóstico completo.")


if __name__ == "__main__":
    main()
