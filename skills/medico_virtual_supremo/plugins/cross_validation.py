# -*- coding: utf-8 -*-
"""
Plugins de Validação Cruzada — Implementação
===============================================
Validação multi-agente, diferencial e de evidências para o pipeline clínico.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Modelos de Dados
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class CrossValidationReport:
    """Relatório de validação cruzada multi-agente."""

    caso_id: str
    num_especialistas_consultados: int = 0
    consenso_geral: bool = False
    conflitos: List[Dict[str, Any]] = field(default_factory=list)
    hipoteses_priorizadas: List[Dict[str, Any]] = field(default_factory=list)
    diagnosticos_divergentes: List[str] = field(default_factory=list)
    recomendacoes_conflitantes: List[str] = field(default_factory=list)
    score_confianca_geral: float = 0.0
    summary: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# CrossValidationPlugin — Validação Multi-Agente
# ──────────────────────────────────────────────────────────────────────────────


class CrossValidationPlugin:
    """
    Coordena a validação cruzada entre múltiplos agentes especialistas.

    Funciona como um "colegiado" clínico virtual: cada especialista
    analisa o caso independentemente e o plugin consolida os resultados,
    detectando consenso, divergências e conflitos.
    """

    def __init__(self):
        self._especialistas: Dict[str, Dict[str, Any]] = {}
        self._historico: List[CrossValidationReport] = []

    def registrar_especialista(
        self,
        especialidade: str,
        capacidades: List[str],
        regras: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Registra um especialista para validação cruzada."""
        self._especialistas[especialidade] = {
            "especialidade": especialidade,
            "capacidades": capacidades,
            "regras": regras or {},
            "confianca": 0.8,
        }

    def validar(
        self,
        caso: Dict[str, Any],
        especialistas_ativos: Optional[List[str]] = None,
    ) -> CrossValidationReport:
        """
        Executa validação cruzada sobre um caso clínico.

        Args:
            caso: Dicionário com dados do caso (hipoteses, evidencias, plano).
            especialistas_ativos: Lista de especialidades para consultar.
                                 None = todos registrados.

        Returns:
            CrossValidationReport com consenso e conflitos.
        """
        caso_id = hashlib.md5(str(caso.get("request", "")).encode()).hexdigest()[:12]
        report = CrossValidationReport(caso_id=caso_id)

        ativos = especialistas_ativos or list(self._especialistas.keys())
        hipoteses = caso.get("assessment", {}).get("hypotheses", [])
        evidencias = caso.get("evidence", [])

        # Simular consulta a cada especialista
        for esp in ativos:
            if esp not in self._especialistas:
                logger.warning(f"Especialista '{esp}' não registrado")
                continue
            report.num_especialistas_consultados += 1

            perfil = self._especialistas[esp]
            # Verificar conflitos com as hipóteses
            for h in hipoteses:
                conflito = self._verificar_conflito(perfil, h)
                if conflito:
                    report.conflitos.append(conflito)

            # Verificar consistência das evidências
            for ev in evidencias:
                conflito_ev = self._verificar_evidencia(perfil, ev)
                if conflito_ev:
                    report.conflitos.append(conflito_ev)

        # Consolidar
        report.conflitos = self._deduplicar_conflitos(report.conflitos)
        report.consenso_geral = len(report.conflitos) == 0
        report.score_confianca_geral = self._calcular_confianca(report)

        if report.consenso_geral:
            report.summary = (
                f"Consenso entre {report.num_especialistas_consultados} "
                f"especialistas. Score de confiança: {report.score_confianca_geral:.1%}"
            )
        else:
            report.summary = (
                f"{len(report.conflitos)} conflito(s) detectado(s) entre "
                f"{report.num_especialistas_consultados} especialistas. "
                f"Revisão humana prioritária recomendada."
            )

        report.hipoteses_priorizadas = self._priorizar_hipoteses(hipoteses, report.conflitos)
        self._historico.append(report)
        return report

    def _verificar_conflito(
        self, perfil: Dict[str, Any], hipotese: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Verifica se uma hipótese conflita com o perfil do especialista."""
        # Conflito: hipótese fora da área de atuação do especialista
        nome_hip = hipotese.get("name", "").lower()
        capacidades = [c.lower() for c in perfil["capacidades"]]

        # Se a hipótese menciona uma especialidade diferente, marcar conflito
        map_esp_hipotese = {
            "cardíaco": "cardiologia",
            "coronariana": "cardiologia",
            "avc": "neurologia",
            "acidente vascular": "neurologia",
            "tumor": "oncologia",
            "câncer": "oncologia",
            "pneumonia": "pneumologia",
            "infecção": "infectologia",
            "sepse": "infectologia",
        }

        for termo, especialidade in map_esp_hipotese.items():
            if termo in nome_hip:
                # Se nenhuma capacidade do perfil corresponde, é conflito
                if not any(especialidade in cap for cap in capacidades):
                    # Mas pode ser que o especialista esteja fazendo um diagnóstico diferencial
                    if hipotese.get("status") == "grave_não_perder":
                        return None  # Hipóteses graves são sempre válidas
                    return {
                        "tipo": "fora_da_especialidade",
                        "especialista": perfil["especialidade"],
                        "hipotese": hipotese.get("name"),
                        "detalhe": f"Hipótese '{hipotese['name']}' fora da área '{perfil['especialidade']}'",
                        "severidade": "baixa",
                    }
        return None

    def _verificar_evidencia(
        self, perfil: Dict[str, Any], evidencia: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Verifica consistência de uma evidência."""
        claim = evidencia.get("claim", "").lower()
        fonte = evidencia.get("source", "").lower()

        # Evidência sem fonte
        if not fonte or fonte in ["a validar", "não informada"]:
            return {
                "tipo": "evidencia_sem_fonte",
                "especialista": perfil["especialidade"],
                "detalhe": f"Evidência '{evidencia.get('claim', '')[:50]}' sem fonte verificável",
                "severidade": "alta",
            }

        # Evidência com fonte genérica demais
        fontes_genericas = ["diretriz", "guideline", "literatura"]
        if any(fg in fonte for fg in fontes_genericas) and len(fonte) < 20:
            return {
                "tipo": "fonte_generica",
                "especialista": perfil["especialidade"],
                "detalhe": f"Fonte genérica: '{fonte}'",
                "severidade": "média",
            }

        return None

    def _deduplicar_conflitos(
        self, conflitos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove conflitos duplicados."""
        vistos: Set[str] = set()
        unicos = []
        for c in conflitos:
            chave = hashlib.md5(str(c).encode()).hexdigest()
            if chave not in vistos:
                vistos.add(chave)
                unicos.append(c)
        return unicos

    def _calcular_confianca(self, report: CrossValidationReport) -> float:
        """Calcula score de confiança geral baseado em conflitos."""
        if report.num_especialistas_consultados == 0:
            return 0.0
        conflitos_graves = sum(
            1 for c in report.conflitos if c.get("severidade") == "alta"
        )
        conflitos_medios = sum(
            1 for c in report.conflitos if c.get("severidade") == "média"
        )
        desconto = (conflitos_graves * 0.3) + (conflitos_medios * 0.1)
        return max(0.0, min(1.0, 0.9 - desconto))

    def _priorizar_hipoteses(
        self, hipoteses: List[Dict[str, Any]], conflitos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Re-prioriza hipóteses com base nos conflitos detectados."""
        nomes_conflito = {
            c.get("hipotese", "").lower() for c in conflitos if c.get("hipotese")
        }
        for h in hipoteses:
            if h.get("name", "").lower() in nomes_conflito:
                h["_conflito_validacao"] = True
                h["confidence"] = self._rebaixar_confianca(h.get("confidence", "baixa"))
        return hipoteses

    def _rebaixar_confianca(self, confianca: str) -> str:
        ordem = {"alta": "moderada", "moderada": "baixa", "baixa": "baixa"}
        return ordem.get(confianca, "baixa")

    def historico(self, limit: int = 5) -> List[CrossValidationReport]:
        """Retorna histórico de validações."""
        return self._historico[-limit:]


# ──────────────────────────────────────────────────────────────────────────────
# DifferentialValidator — Validador de Hipóteses Diferenciais
# ──────────────────────────────────────────────────────────────────────────────


class DifferentialValidator:
    """
    Valida a completude e qualidade das hipóteses diferenciais.

    Verifica:
    - Cobertura dos principais grupos de doenças
    - Hipóteses graves devidamente listadas
    - Dados críticos ausentes identificados
    - Raciocínio explícito para cada hipótese
    """

    GRUPOS_OBRIGATORIOS = [
        "infeccioso",
        "neoplásico",
        "vascular",
        "inflamatório",
        "tóxico/metabólico",
    ]

    def __init__(self):
        self._validacoes: List[Dict[str, Any]] = []

    def validar(
        self,
        hipoteses: List[Dict[str, Any]],
        sindrome: str,
        dados_disponiveis: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Valida a lista de hipóteses diferenciais.

        Args:
            hipoteses: Lista de dicionários de hipóteses.
            sindrome: Síndrome identificada (respiratório, cardíaco, etc.).
            dados_disponiveis: Lista de dados clínicos disponíveis.

        Returns:
            Dict com resultado da validação.
        """
        resultado = {
            "valido": True,
            "score": 1.0,
            "alertas": [],
            "grupos_cobertos": [],
            "grupos_faltando": [],
            "recomendacoes": [],
        }

        dados = dados_disponiveis or []

        # Verificar 1: Hipóteses para grupos obrigatórios
        grupos_na_hipotese = self._extrair_grupos(hipoteses)
        for grupo in self.GRUPOS_OBRIGATORIOS:
            if grupo in grupos_na_hipotese:
                resultado["grupos_cobertos"].append(grupo)
            else:
                resultado["grupos_faltando"].append(grupo)

        if resultado["grupos_faltando"]:
            resultado["alertas"].append(
                f"Grupos não contemplados: {', '.join(resultado['grupos_faltando'])}"
            )
            resultado["score"] -= 0.1 * len(resultado["grupos_faltando"])

        # Verificar 2: Hipótese grave não_perder existe?
        tem_grave = any(
            h.get("status") == "grave_não_perder" for h in hipoteses
        )
        if not tem_grave:
            resultado["alertas"].append(
                "Nenhuma hipótese 'grave_não_perder' listada"
            )
            resultado["score"] -= 0.2

        # Verificar 3: Cada hipótese tem confiança declarada?
        sem_confianca = sum(
            1 for h in hipoteses if not h.get("confidence")
        )
        if sem_confianca:
            resultado["alertas"].append(
                f"{sem_confianca} hipótese(s) sem nível de confiança"
            )
            resultado["score"] -= 0.05 * sem_confianca

        # Verificar 4: Missing evidence identificado?
        sem_missing = sum(
            1 for h in hipoteses if not h.get("missing_evidence")
        )
        if sem_missing:
            resultado["alertas"].append(
                f"{sem_missing} hipótese(s) sem identificação de dados necessários"
            )

        # Verificar 5: Dados disponíveis vs. necessários
        for h in hipoteses:
            for m in h.get("missing_evidence", []):
                if m in dados:
                    resultado["alertas"].append(
                        f"Dado '{m}' já disponível mas listado como ausente em '{h.get('name', '?')}'"
                    )
                    resultado["score"] -= 0.05

        # Recomendações
        if resultado["grupos_faltando"]:
            resultado["recomendacoes"].append(
                "Considere incluir hipóteses para grupos não contemplados"
            )
        if resultado["score"] < 0.7:
            resultado["recomendacoes"].append("Revisão clínica prioritária necessária")

        resultado["valido"] = resultado["score"] >= 0.6
        resultado["score"] = max(0.0, min(1.0, resultado["score"]))
        self._validacoes.append(resultado)
        return resultado

    def _extrair_grupos(self, hipoteses: List[Dict[str, Any]]) -> Set[str]:
        """Extrai grupos de doenças das hipóteses."""
        grupos: Set[str] = set()
        mapa_termos = {
            "infeccioso": ["infecção", "infecciosa", "viral", "bacteriana", "sepse",
                           "pneumonia", "meningite", "tuberculose", "hiv"],
            "neoplásico": ["tumor", "neoplasia", "câncer", "carcinoma", "linfoma",
                           "metástase", "massa"],
            "vascular": ["avc", "acidente vascular", "tromboembolismo", "isquemia",
                         "hemorragia", "trombose", "embolia"],
            "inflamatório": ["inflamatório", "autoimune", "artrite", "vasculite",
                             "lúpus", "doença inflamatória"],
            "tóxico/metabólico": ["intoxicação", "distúrbio metabólico", "desequilíbrio",
                                  "toxicidade", "diabético"],
        }
        for h in hipoteses:
            nome = h.get("name", "").lower()
            for grupo, termos in mapa_termos.items():
                if any(t in nome for t in termos):
                    grupos.add(grupo)
        return grupos

    def ultimas_validacoes(self, limit: int = 5) -> List[Dict[str, Any]]:
        return self._validacoes[-limit:]


# ──────────────────────────────────────────────────────────────────────────────
# EvidenceCrosscheck — Verificação de Evidências
# ──────────────────────────────────────────────────────────────────────────────


class EvidenceCrosscheck:
    """
    Verifica a consistência interna e externa das evidências citadas.

    Checagens:
    - Fonte citada vs. claim (coerência)
    - Duplicidade de evidências
    - Evidências contraditórias
    - Aplicabilidade ao caso
    """

    def __init__(self):
        self._checks: List[Dict[str, Any]] = []

    def verificar(
        self, evidencias: List[Dict[str, Any]], hipoteses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executa verificação cruzada de evidências.

        Args:
            evidencias: Lista de evidências do caso.
            hipoteses: Lista de hipóteses para contexto.

        Returns:
            Dict com resultado da verificação.
        """
        resultado = {
            "valido": True,
            "score": 1.0,
            "alertas": [],
            "evidencias_verificadas": len(evidencias),
            "duplicatas": [],
            "contradicoes": [],
            "sem_aplicabilidade": [],
        }

        if not evidencias:
            resultado["alertas"].append("Nenhuma evidência citada")
            resultado["score"] = 0.3
            resultado["valido"] = False
            self._checks.append(resultado)
            return resultado

        # 1. Detectar duplicatas (mesmo claim mesma fonte)
        vistos: Set[str] = set()
        for ev in evidencias:
            chave = f"{ev.get('claim', '')}|{ev.get('source', '')}"
            if chave in vistos:
                resultado["duplicatas"].append(ev.get("claim", "")[:50])
                resultado["alertas"].append(f"Evidência duplicada: {ev.get('claim', '')[:50]}")
                resultado["score"] -= 0.05
            vistos.add(chave)

        # 2. Aplicabilidade
        for ev in evidencias:
            apl = ev.get("applicability", "não informada")
            if apl == "não informada":
                resultado["sem_aplicabilidade"].append(ev.get("claim", "")[:50])
                resultado["score"] -= 0.05

        # 3. Evidências contraditórias (mesmo tema, claims opostos)
        claims_por_tema: Dict[str, List[str]] = {}
        for ev in evidencias:
            tema = ev.get("claim", "")[:30]
            if tema not in claims_por_tema:
                claims_por_tema[tema] = []
            claims_por_tema[tema].append(ev.get("claim", ""))

        for tema, claims in claims_por_tema.items():
            if len(claims) >= 2:
                # Verificar se há contradição semântica simples
                for i, c1 in enumerate(claims):
                    for c2 in claims[i + 1:]:
                        if self._sao_contraditorias(c1, c2):
                            resultado["contradicoes"].append({
                                "claim_1": c1[:60],
                                "claim_2": c2[:60],
                            })
                            resultado["alertas"].append(f"Contradição detectada: {c1[:40]} vs {c2[:40]}")
                            resultado["score"] -= 0.15

        resultado["score"] = max(0.0, min(1.0, resultado["score"]))
        resultado["valido"] = resultado["score"] >= 0.5
        self._checks.append(resultado)
        return resultado

    def _sao_contraditorias(self, c1: str, c2: str) -> bool:
        """Verifica se duas claims são contraditórias."""
        c1l, c2l = c1.lower(), c2.lower()
        pares_contrarios = [
            ("recomenda", "contraindica"),
            ("eficaz", "ineficaz"),
            ("benefício", "risco"),
            ("aumenta", "reduz"),
            ("melhora", "piora"),
            ("indicado", "contraindicado"),
            ("positivo", "negativo"),
            ("favorável", "desfavorável"),
        ]
        for a, b in pares_contrarios:
            if (a in c1l and b in c2l) or (b in c1l and a in c2l):
                # Mesmo tema?
                tema1 = c1l[:20]
                tema2 = c2l[:20]
                if tema1 == tema2 or abs(len(tema1) - len(tema2)) < 5:
                    return True
        return False

    def relatorio(self) -> Dict[str, Any]:
        """Relatório consolidado das verificações."""
        if not self._checks:
            return {"status": "sem_verificacoes"}
        total = len(self._checks)
        valido = sum(1 for c in self._checks if c["valido"])
        return {
            "total_verificacoes": total,
            "validas": valido,
            "inconsistentes": total - valido,
            "score_medio": sum(c["score"] for c in self._checks) / total,
        }
