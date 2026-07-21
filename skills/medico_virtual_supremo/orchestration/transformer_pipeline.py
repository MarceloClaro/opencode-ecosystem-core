# -*- coding: utf-8 -*-
"""
Pipeline Transformer de Orquestração Clínica
===============================================
Arquitetura de atenção multi-cabeça para roteamento de casos clínicos.

O pipeline funciona como um "transformer" clínico:
  - Query: representação do problema (síndrome, gravidade, especialidade suspeita)
  - Keys: perfis de competência dos especialistas registrados
  - Values: capacidades específicas de cada especialista
  - Atenção: similaridade semântica entre caso e especialista
  - Saída: ranking de especialistas com pesos de confiança

Inspirado no Transformer Architecture do OpenCode (SPEC-004).
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class EspecialistaProfile:
    """
    Perfil de um especialista médico para roteamento.

    Attributes:
        id: Identificador único do especialista.
        nome: Nome legível.
        especialidade: Especialidade principal.
        palavras_chave: Termos associados à especialidade.
        peso_urgencia: Preferência para casos urgentes (0-1).
        capacidades: Lista de capacidades/campos de atuação.
    """
    id: str
    nome: str
    especialidade: str
    palavras_chave: List[str]
    peso_urgencia: float = 0.5
    capacidades: List[str] = field(default_factory=list)
    confianca: float = 0.8


@dataclass
class AttentionRoutingResult:
    """
    Resultado do roteamento por atenção.

    Attributes:
        caso_id: Identificador do caso processado.
        especialistas_ranqueados: Lista de (especialista, peso_atenção).
        especialista_principal: Especialista com maior peso.
        score_urgencia: Score de urgência do caso (0-1).
        justificativa: Explicação do roteamento.
        todos_especialistas_consultados: Número total de especialistas.
    """
    caso_id: str
    especialistas_ranqueados: List[Tuple[EspecialistaProfile, float]]
    especialista_principal: Optional[EspecialistaProfile]
    score_urgencia: float = 0.0
    justificativa: str = ""
    todos_especialistas_consultados: int = 0


# ──────────────────────────────────────────────────────────────────────────────
# Feature Extractors — Extração de características do caso
# ──────────────────────────────────────────────────────────────────────────────

# Mapeamento semântico: síndrome → especialidades relevantes
SINDROME_TO_ESPECIALIDADES = {
    "respiratório": ["pneumologia", "infectologia", "clinica_geral"],
    "cardíaco": ["cardiologia", "clinica_geral"],
    "neurológico": ["neurologia", "clinica_geral"],
    "gastrointestinal": ["gastroenterologia", "clinica_geral"],
    "infeccioso": ["infectologia", "clinica_geral"],
    "renal": ["nefrologia", "clinica_geral"],
    "dermatológico": ["dermatologia", "clinica_geral"],
    "ortopédico": ["ortopedia", "reumatologia", "clinica_geral"],
    "endócrino": ["endocrinologia", "clinica_geral"],
    "psiquiátrico": ["psiquiatria", "neurologia", "clinica_geral"],
    "oncológico": ["oncologia", "clinica_geral"],
    "autoimune": ["reumatologia", "imunologia", "clinica_geral"],
    "inespecífico": ["clinica_geral"],
}


class ClinicalTransformerPipeline:
    """
    Pipeline Transformer de Orquestração Clínica.

    Responsável por receber um caso clínico e roteá-lo ao(s) especialista(s)
    mais adequado(s) usando um mecanismo de atenção baseado em similaridade
    semântica entre a representação do caso e os perfis dos especialistas.
    """

    def __init__(self):
        self._especialistas: Dict[str, EspecialistaProfile] = {}
        self._extractors: List[Tuple[str, Callable]] = []
        self._historico: List[AttentionRoutingResult] = []
        self._registrar_feature_extractors_padrao()

    def registrar_especialista(self, perfil: EspecialistaProfile) -> None:
        """Registra um especialista no pipeline."""
        self._especialistas[perfil.id] = perfil
        logger.info(f"Especialista registrado: {perfil.nome} ({perfil.especialidade})")

    def registrar_especialistas_lote(
        self, perfis: List[EspecialistaProfile]
    ) -> None:
        """Registra múltiplos especialistas de uma vez."""
        for p in perfis:
            self.registrar_especialista(p)

    def _registrar_feature_extractors_padrao(self) -> None:
        """Registra extractors de características padrão."""
        self._extractors = [
            ("sindrome", self._extrair_sindrome),
            ("urgencia", self._extrair_urgencia),
            ("especialidade_suspeita", self._extrair_especialidade_suspeita),
            ("gravidade", self._extrair_gravidade),
        ]

    def _extrair_sindrome(self, caso: Dict[str, Any]) -> str:
        """Extrai a síndrome do caso com matching tolerante a flexões de gênero."""
        problema = caso.get("clinical_summary", {}).get("problem_representation", "")
        problema_lower = problema.lower()

        # Matching direto por substring (tolerante a gênero gramatical)
        for sindrome in SINDROME_TO_ESPECIALIDADES:
            sindrome_lower = sindrome.lower()
            # Verifica substring exata
            if sindrome_lower in problema_lower:
                return sindrome
            # Verifica raiz (remove diferenças de gênero: o/a)
            raiz = sindrome_lower.rstrip("oã")
            if raiz and raiz in problema_lower:
                return sindrome

        request = caso.get("request", "")
        request_lower = request.lower()
        sinais = {
            "respiratório": ["falta de ar", "tosse", "dispneia", "expectoração", "chiado no peito"],
            "cardíaco": ["dor no peito", "palpitação", "dor torácica", "edema",
                         "coração", "parada cardíaca"],
            "neurológico": ["cefaleia", "tontura", "confusão", "desmaio", "convulsão",
                            "avc", "acidente vascular", "derrame"],
            "infeccioso": ["febre", "calafrio", "infecção", "pus", "sepse"],
            "gastrointestinal": ["dor abdominal", "náusea", "vômito", "diarreia"],
        }
        for sindrome, termos in sinais.items():
            if any(t in request_lower for t in termos):
                return sindrome
        return "inespecífico"

    def _extrair_urgencia(self, caso: Dict[str, Any]) -> float:
        """Calcula score de urgência (0-1)."""
        safety = caso.get("safety", {})
        if safety.get("emergency_detected", False):
            return 1.0

        request = caso.get("request", "")
        termos_urgencia = [
            "urgente", "emergência", "grave", "intenso", "súbito", "repentino",
            "piora rápida", "deterioração", "socorro",
        ]
        score = sum(1 for t in termos_urgencia if t in request.lower())
        return min(1.0, score * 0.2)

    def _extrair_especialidade_suspeita(self, caso: Dict[str, Any]) -> Optional[str]:
        """Extrai especialidade suspeita do caso."""
        hipoteses = caso.get("assessment", {}).get("hypotheses", [])
        if not hipoteses:
            return None
        primeira = hipoteses[0].get("name", "").lower()
        mapa = {
            "cardiol": "cardiologia",
            "coronar": "cardiologia",
            "neurol": "neurologia",
            "avc": "neurologia",
            "pneum": "pneumologia",
            "infect": "infectologia",
            "gastro": "gastroenterologia",
            "nefrol": "nefrologia",
        }
        for termo, esp in mapa.items():
            if termo in primeira:
                return esp
        return None

    def _extrair_gravidade(self, caso: Dict[str, Any]) -> float:
        """Extrai gravidade do caso (0-1)."""
        safety = caso.get("safety", {})
        if safety.get("emergency_detected", False):
            return 1.0
        hipoteses = caso.get("assessment", {}).get("hypotheses", [])
        for h in hipoteses:
            if h.get("status") == "grave_não_perder":
                return 0.8
        return 0.3

    # ──────────────────────────────────────────────────────────────────────────
    # Atenção Multi-Cabeça (Simplificada)
    # ──────────────────────────────────────────────────────────────────────────

    def _calcular_atencao(
        self, features: Dict[str, Any], especialista: EspecialistaProfile
    ) -> float:
        """
        Calcula peso de atenção entre um caso e um especialista.

        Usa similaridade de cosseno simplificada entre:
        - Vetor de características do caso
        - Vetor de perfil do especialista
        """
        score = 0.0
        num_fatores = 0

        # 1. Similaridade por síndrome
        sindrome = features.get("sindrome", "inespecífico")
        especialidades_relevantes = SINDROME_TO_ESPECIALIDADES.get(sindrome, ["clinica_geral"])
        if especialista.especialidade in especialidades_relevantes:
            score += 0.4
        elif "clinica_geral" in especialidades_relevantes and especialista.especialidade == "clinica_geral":
            score += 0.2
        num_fatores += 1

        # 2. Similaridade por palavra-chave
        request = str(features.get("request_raw", "")).lower()
        correspondencias = sum(1 for kw in especialista.palavras_chave if kw.lower() in request)
        if correspondencias > 0:
            score += min(0.3, correspondencias * 0.1)
        num_fatores += 1

        # 3. Ajuste por urgência
        urgencia = features.get("urgencia", 0.0)
        score += especialista.peso_urgencia * urgencia * 0.2
        num_fatores += 1

        # 4. Especialidade suspeita
        esp_suspeita = features.get("especialidade_suspeita")
        if esp_suspeita and esp_suspeita == especialista.especialidade:
            score += 0.3
        num_fatores += 1

        return score / num_fatores if num_fatores > 0 else 0.0

    # ──────────────────────────────────────────────────────────────────────────
    # Pipeline Principal
    # ──────────────────────────────────────────────────────────────────────────

    def processar(
        self,
        caso: Dict[str, Any],
        top_k: int = 3,
    ) -> AttentionRoutingResult:
        """
        Processa um caso clínico e retorna o ranking de especialistas.

        Args:
            caso: Dicionário completo do caso (saída da skill principal).
            top_k: Número de especialistas no ranking final.

        Returns:
            AttentionRoutingResult com o ranking.
        """
        caso_id = str(hash(str(caso.get("request", ""))))[:12]

        # Extrair features
        features: Dict[str, Any] = {
            "request_raw": caso.get("request", ""),
            "clinical_summary": caso.get("clinical_summary", {}),
        }
        for nome, extractor in self._extractors:
            features[nome] = extractor(caso)

        if not self._especialistas:
            # Fallback: sem especialistas registrados
            return AttentionRoutingResult(
                caso_id=caso_id,
                especialistas_ranqueados=[],
                especialista_principal=None,
                score_urgencia=features.get("urgencia", 0.0),
                justificativa="Nenhum especialista registrado no pipeline",
                todos_especialistas_consultados=0,
            )

        # Calcular atenção para cada especialista
        scores = []
        for esp in self._especialistas.values():
            peso = self._calcular_atencao(features, esp)
            peso *= esp.confianca  # Ajustar pela confiança histórica
            scores.append((esp, peso))

        # Ordenar por peso (decrescente)
        scores.sort(key=lambda x: x[1], reverse=True)

        # Selecionar top-K
        top = scores[:top_k]
        principal = top[0][0] if top else None
        justificativa = self._gerar_justificativa(features, top)

        resultado = AttentionRoutingResult(
            caso_id=caso_id,
            especialistas_ranqueados=top,
            especialista_principal=principal,
            score_urgencia=features.get("urgencia", 0.0),
            justificativa=justificativa,
            todos_especialistas_consultados=len(self._especialistas),
        )

        self._historico.append(resultado)
        return resultado

    def _gerar_justificativa(
        self,
        features: Dict[str, Any],
        top: List[Tuple[EspecialistaProfile, float]],
    ) -> str:
        """Gera justificativa textual para o roteamento."""
        if not top:
            return "Nenhum especialista disponível para roteamento"
        sindrome = features.get("sindrome", "não identificada")
        principal = top[0]
        partes = [
            f"Paciente com síndrome {sindrome}",
            f"roteado para {principal[0].nome} (peso: {principal[1]:.2f})",
        ]
        if len(top) > 1:
            alternativas = [f"{e.nome} ({p:.2f})" for e, p in top[1:]]
            partes.append(f"Alternativas: {'; '.join(alternativas)}")
        if features.get("urgencia", 0) > 0.7:
            partes.append("ALTA URGÊNCIA — priorizar atendimento")
        return " | ".join(partes)

    def historico(self, limit: int = 10) -> List[AttentionRoutingResult]:
        """Histórico de processamentos."""
        return self._historico[-limit:]

    def get_especialistas(self) -> Dict[str, EspecialistaProfile]:
        """Retorna todos os especialistas registrados."""
        return dict(self._especialistas)

    def resumo_pipeline(self) -> Dict[str, Any]:
        """Resumo do estado do pipeline."""
        return {
            "especialistas_registrados": len(self._especialistas),
            "casos_processados": len(self._historico),
            "especialistas": {
                eid: {
                    "nome": p.nome,
                    "especialidade": p.especialidade,
                    "peso_urgencia": p.peso_urgencia,
                }
                for eid, p in self._especialistas.items()
            },
        }


# ──────────────────────────────────────────────────────────────────────────────
# Perfis Padrão de Especialistas
# ──────────────────────────────────────────────────────────────────────────────

PERFIS_ESPECIALISTAS_PADRAO = [
    EspecialistaProfile(
        id="medico-cardiologista",
        nome="Médico Cardiologista",
        especialidade="cardiologia",
        palavras_chave=[
            "coração", "cardíaco", "ecg", "eletro", "troponina", "iam",
            "angina", "dor no peito", "palpitação", "arritmia", "ic",
            "insuficiência cardíaca", "síncope", "hipertensão",
        ],
        peso_urgencia=0.9,
        capacidades=["ecg", "ecocardiograma", "teste ergométrico", "cateterismo"],
    ),
    EspecialistaProfile(
        id="medico-neurologista",
        nome="Médico Neurologista",
        especialidade="neurologia",
        palavras_chave=[
            "neurológico", "avc", "cefaleia", "enxaqueca", "convulsão",
            "epilepsia", "tontura", "vertigem", "demência", "alzheimer",
            "parkinson", "neuropatia", "acidente vascular",
        ],
        peso_urgencia=0.8,
        capacidades=["neurologia clínica", "eeg", "punção lombar"],
    ),
    EspecialistaProfile(
        id="medico-infectologista",
        nome="Médico Infectologista",
        especialidade="infectologia",
        palavras_chave=[
            "infecção", "infeccioso", "febre", "sepse", "antibiótico",
            "antimicrobiano", "bacteriana", "viral", "fungo", "hiv",
            "tuberculose", "meningite", "pneumonia",
        ],
        peso_urgencia=0.7,
        capacidades=["infectologia", "microbiologia", "antibioticoterapia"],
    ),
    EspecialistaProfile(
        id="medico-radiologista",
        nome="Médico Radiologista",
        especialidade="radiologia",
        palavras_chave=[
            "raio-x", "radiografia", "tomografia", "tc", "rm", "ressonância",
            "ultrassom", "usg", "mamografia", "laudo", "imagem",
            "achado incidental", "contraste",
        ],
        peso_urgencia=0.6,
        capacidades=["radiologia", "ultrassonografia", "tomografia", "ressonância"],
    ),
    EspecialistaProfile(
        id="medico-clinico-geral",
        nome="Médico Clínico Geral",
        especialidade="clinica_geral",
        palavras_chave=[
            "clínico", "geral", "revisão", "checkup", "preventivo",
            "encaminhamento", "orientação",
        ],
        peso_urgencia=0.5,
        capacidades=["clínica geral", "prevenção", "triagem", "encaminhamento"],
        confianca=0.95,  # Clínico geral tem alta confiança como fallback
    ),
]


def criar_pipeline_padrao() -> ClinicalTransformerPipeline:
    """Cria pipeline transformer com todos os especialistas padrão."""
    pipeline = ClinicalTransformerPipeline()
    pipeline.registrar_especialistas_lote(PERFIS_ESPECIALISTAS_PADRAO)
    return pipeline
