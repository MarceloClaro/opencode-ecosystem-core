# -*- coding: utf-8 -*-
"""
MetaBus Integration — Médico Virtual Supremo
=============================================
Conector entre a skill médica e o barramento metacognitivo global (MetaBus).
Publica eventos, reflexões e métricas de confiança para o ecossistema OpenCode.

Tópicos publicados no MetaBus:
  - medico.analysis.started       → Início da análise clínica
  - medico.analysis.completed     → Análise concluída com sucesso
  - medico.emergency.detected     → Emergência detectada
  - medico.prescription.refused   → Prescrição autônoma recusada
  - medico.hypotheses.generated   → Hipóteses diferenciais geradas
  - medico.validation.cross       → Validação cruzada executada
  - medico.error                  → Erro durante análise

Reflexões registradas:
  - Pós-análise com score baseado em checks de segurança
  - Pós-emergência com severidade
  - Pós-recusa de prescrição

Confidence ledger:
  - medico:skill                  → Confiança geral da skill
  - medico:safety                 → Performance dos checks de segurança
  - medico:hypothesis_generation  → Qualidade das hipóteses
  - medico:emergency_detection    → Precisão da detecção de emergência
"""

import json
import time
import logging
from typing import Any, Dict, List, Optional

try:
    from mci.metabus import metabus
    METABUS_DISPONIVEL = True
except ImportError:
    METABUS_DISPONIVEL = False
    metabus = None

logger = logging.getLogger("medico-metabus")
logger.setLevel(logging.INFO)

SUBSYSTEM = "medico"

# ──────────────────────────────────────────────────────────────────────────────
# Publicação de eventos
# ──────────────────────────────────────────────────────────────────────────────


def publicar_evento(
    event_name: str,
    payload: Dict[str, Any],
    source_agent: str = "medico-virtual-supremo",
) -> int:
    """Publica um evento no MetaBus, se disponível."""
    if not METABUS_DISPONIVEL:
        return 0
    try:
        return metabus.publish_subsystem_event(
            subsystem=SUBSYSTEM,
            event_name=event_name,
            payload=payload,
            source_agent=source_agent,
        )
    except Exception as e:
        logger.warning(f"Erro ao publicar evento {event_name}: {e}")
        return 0


def analysis_started(
    modo: str,
    run_id: str,
    request_resumo: str,
    patient_resumo: Optional[str] = None,
) -> int:
    """Publica evento de início de análise."""
    return publicar_evento("analysis.started", {
        "modo": modo,
        "run_id": run_id,
        "request_preview": request_resumo[:120],
        "patient_preview": (patient_resumo or "não informado")[:60],
        "timestamp": time.time(),
    })


def analysis_completed(
    modo: str,
    run_id: str,
    hipoteses_count: int,
    checks_passed: int,
    checks_failed: int,
    emergencia: bool,
    duracao_segundos: float,
) -> int:
    """Publica evento de análise concluída."""
    return publicar_evento("analysis.completed", {
        "modo": modo,
        "run_id": run_id,
        "hipoteses_count": hipoteses_count,
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "emergencia_detectada": emergencia,
        "duracao_segundos": round(duracao_segundos, 3),
        "sucesso": checks_failed == 0,
    })


def emergency_detected(
    run_id: str,
    motivo: str,
    modo: str,
) -> int:
    """Publica evento de emergência detectada."""
    return publicar_evento("emergency.detected", {
        "run_id": run_id,
        "motivo": motivo,
        "modo": modo,
        "severidade": "alta",
        "timestamp": time.time(),
    })


def prescription_refused(
    run_id: str,
    motivo: str,
    modo: str,
) -> int:
    """Publica evento de recusa de prescrição autônoma."""
    return publicar_evento("prescription.refused", {
        "run_id": run_id,
        "motivo": motivo,
        "modo": modo,
        "timestamp": time.time(),
    })


def hypotheses_generated(
    run_id: str,
    hipoteses: List[Dict[str, Any]],
    sindrome: str,
) -> int:
    """Publica evento de geração de hipóteses."""
    return publicar_evento("hypotheses.generated", {
        "run_id": run_id,
        "sindrome": sindrome,
        "hipoteses_count": len(hipoteses),
        "hipoteses_graves": [
            h.get("name") for h in hipoteses
            if h.get("status") == "grave_não_perder"
        ],
        "confiancas": {
            h.get("name", "?"): h.get("confidence", "?")
            for h in hipoteses
        },
    })


def cross_validation_executed(
    run_id: str,
    especialistas_consultados: int,
    consenso: bool,
    conflitos: int,
) -> int:
    """Publica evento de validação cruzada."""
    return publicar_evento("validation.cross", {
        "run_id": run_id,
        "especialistas_consultados": especialistas_consultados,
        "consenso": consenso,
        "conflitos": conflitos,
    })


def error_occurred(
    run_id: str,
    erro: str,
    modo: Optional[str] = None,
) -> int:
    """Publica evento de erro."""
    return publicar_evento("error", {
        "run_id": run_id,
        "erro": str(erro)[:200],
        "modo": modo or "desconhecido",
    })


# ──────────────────────────────────────────────────────────────────────────────
# Reflexões (MetacognitiveMemory)
# ──────────────────────────────────────────────────────────────────────────────


def registrar_reflexao(
    agent_id: str,
    task_context: str,
    reflection: str,
    score: float,
) -> Optional[str]:
    """Registra uma reflexão pós-execução na memória metacognitiva."""
    if not METABUS_DISPONIVEL:
        return None
    try:
        return metabus.memory.add_reflection(
            agent_id=agent_id,
            task_context=task_context,
            reflection=reflection,
            score=score,
        )
    except Exception as e:
        logger.warning(f"Erro ao registrar reflexão: {e}")
        return None


def refletir_analise(
    run_id: str,
    modo: str,
    checks_passed: int,
    checks_failed: int,
    hipoteses_count: int,
    emergencia: bool,
) -> Optional[str]:
    """Registra reflexão automática pós-análise."""
    score = 1.0 - (checks_failed / max(checks_passed + checks_failed, 1))
    contexto = (
        f"Análise clínica modo={modo} | "
        f"{hipoteses_count} hipóteses | "
        f"{checks_passed}/{checks_passed + checks_failed} checks OK | "
        f"emergência={emergencia}"
    )
    reflexao = (
        f"Análise {'bem-sucedida' if score >= 0.8 else 'com ressalvas'}. "
        f"{checks_passed} checks de segurança passaram, {checks_failed} falharam. "
        f"{'Emergência detectada - fluxo interrompido.' if emergencia else ''}"
    )
    return registrar_reflexao(
        agent_id=f"medico-virtual-supremo:{run_id[:8]}",
        task_context=contexto,
        reflection=reflexao,
        score=score,
    )


def refletir_emergencia(
    run_id: str,
    motivo: str,
    modo: str,
) -> Optional[str]:
    """Registra reflexão para eventos de emergência."""
    return registrar_reflexao(
        agent_id=f"medico-virtual-supremo:emergencia:{run_id[:8]}",
        task_context=f"Emergência modo={modo} | motivo: {motivo[:100]}",
        reflection=f"Emergência clínica detectada: {motivo}. Fluxo normal interrompido para priorizar atendimento presencial.",
        score=0.0,  # Emergência é um evento crítico, score baixo = atenção
    )


# ──────────────────────────────────────────────────────────────────────────────
# Confidence Ledger (MetacognitiveMemory)
# ──────────────────────────────────────────────────────────────────────────────


def atualizar_confianca(topic_key: str, score: float) -> Optional[float]:
    """Atualiza o confidence ledger da skill no MetaBus."""
    if not METABUS_DISPONIVEL:
        return None
    try:
        return metabus.memory.update_topic_confidence(
            topic_key=topic_key,
            score=score,
        )
    except Exception as e:
        logger.warning(f"Erro ao atualizar confiança {topic_key}: {e}")
        return None


def atualizar_confianca_skill(checks_passed: int, checks_total: int) -> Optional[float]:
    """Atualiza confiança geral da skill baseada nos checks."""
    score = checks_passed / max(checks_total, 1)
    return atualizar_confianca("medico:skill", score)


def atualizar_confianca_seguranca(checks_passed: int, checks_total: int) -> Optional[float]:
    """Atualiza confiança no subsistema de segurança."""
    score = checks_passed / max(checks_total, 1)
    return atualizar_confianca("medico:safety", score)


# ──────────────────────────────────────────────────────────────────────────────
# Lições Semânticas (MetacognitiveMemory)
# ──────────────────────────────────────────────────────────────────────────────


def registrar_licao(
    topic: str,
    lesson: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Registra uma lição aprendida na memória semântica."""
    if not METABUS_DISPONIVEL:
        return None
    try:
        return metabus.memory.upsert_semantic_topic(
            topic=topic,
            lesson=lesson,
            metadata=metadata,
        )
    except Exception as e:
        logger.warning(f"Erro ao registrar lição {topic}: {e}")
        return None


def registrar_licao_apos_analise(
    modo: str,
    checks_failed: List[str],
    sindrome: str,
) -> None:
    """Registra lições aprendidas baseadas nos resultados da análise."""
    if checks_failed:
        registrar_licao(
            topic=f"medico:falhas:{modo}",
            lesson=f"Check falhou: {checks_failed[0][:80]}",
            metadata={"sindrome": sindrome, "modo": modo},
        )

    if sindrome and sindrome != "inespecífico":
        registrar_licao(
            topic="medico:sindromes_frequentes",
            lesson=f"Síndrome {sindrome} analisada no modo {modo}",
            metadata={"sindrome": sindrome, "modo": modo},
        )


# ──────────────────────────────────────────────────────────────────────────────
# Utilitário: status da integração
# ──────────────────────────────────────────────────────────────────────────────


def status_metabus() -> Dict[str, Any]:
    """Retorna o status da integração com o MetaBus."""
    if not METABUS_DISPONIVEL:
        return {
            "disponivel": False,
            "motivo": "mci.metabus não encontrado — MetaBus não disponível",
        }

    try:
        memoria = metabus.memory
        ledger = dict(memoria.confidence_ledger)
        topicos_medico = {
            k: v for k, v in ledger.items()
            if k.startswith("medico:")
        }
        return {
            "disponivel": True,
            "episodic_memory_size": len(memoria.episodic),
            "topicos_medico": topicos_medico,
            "confidence_medico_skill": ledger.get("medico:skill", 0.5),
            "confidence_medico_safety": ledger.get("medico:safety", 0.5),
        }
    except Exception as e:
        return {
            "disponivel": True,
            "erro_consulta": str(e)[:100],
        }


def obtermemoriametacognitiva(
    query: str = "",
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Busca na memória metacognitiva compartilhada."""
    if not METABUS_DISPONIVEL:
        return []
    try:
        if query:
            return metabus.search_memory(query=query, limit=limit)
        return metabus.memory.get_recent_context(limit=limit)
    except Exception as e:
        logger.warning(f"Erro ao buscar memória: {e}")
        return []
