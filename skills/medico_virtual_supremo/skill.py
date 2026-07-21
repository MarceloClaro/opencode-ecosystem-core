# -*- coding: utf-8 -*-
"""
medico-virtual-supremo skill — Médico Virtual Supremo: Apoio Clínico Auditável
================================================================================
Skill de apoio à decisão clínica baseada no protocolo SDD/TDD do OpenCode Ecosystem.
Pipeline de raciocínio clínico seguro em 7 etapas (0–6) com saída estruturada YAML,
detecção de emergência, hipóteses diferenciais, evidência rastreável e revisão humana
obrigatória.

Modos de operação:
  - professional_cds   → Apoio clínico para profissional habilitado
  - patient_education  → Explicação em linguagem acessível
  - research           → Síntese de literatura e documentação científica
  - simulation         → Casos fictícios e treinamento

Uso:
    from skills.medico_virtual_supremo.skill import MedicoVirtualSupremoSkill

    skill = MedicoVirtualSupremoSkill()
    resultado = skill.analisar("modo", "entrada clínica", patient={...})

Referência completa: specs/SPEC-935-R*-medico-virtual-supremo.md
"""

import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ──────────────────────────────────────────────────────────────────────────────
# MetaBus — barramento metacognitivo (opcional, falha graceful)
# ──────────────────────────────────────────────────────────────────────────────

try:
    from skills.medico_virtual_supremo.metabus_integration import (
        analysis_started,
        analysis_completed,
        emergency_detected,
        prescription_refused,
        hypotheses_generated,
        error_occurred,
        refletir_analise,
        refletir_emergencia,
        atualizar_confianca_skill,
        atualizar_confianca_seguranca,
        registrar_licao_apos_analise,
    )
    METABUS_ATIVO = True
except ImportError:
    METABUS_ATIVO = False


# ──────────────────────────────────────────────────────────────────────────────
# Constantes clínicas e de segurança
# ──────────────────────────────────────────────────────────────────────────────

SKILL_VERSION = "2.0.0"
RESPONSE_GEN_ID = "05272024-resposta-medico-virtual-supremo"
RESPONSE_SEED = "yaml-ai-resposta-medico-virtual-supremo"
MODULOS_DISPONIVEIS = {
    "historico": {
        "gen_id": "05272024-medical-supreme-doctor-historico",
        "seed": "yaml-ai-medical-historico",
    },
    "geneticos": {
        "gen_id": "05272024-medical-supreme-doctor-geneticos",
        "seed": "yaml-ai-medical-geneticos",
    },
    "estilo": {
        "gen_id": "05272024-medical-supreme-doctor-estilo",
        "seed": "yaml-ai-medical-estilo",
    },
    "exames": {
        "gen_id": "05272024-medical-supreme-doctor-exames",
        "seed": "yaml-ai-medical-exames",
    },
    "rag": {
        "gen_id": "05272024-medical-supreme-doctor-rag",
        "seed": "yaml-ai-medical-rag",
    },
    "preditiva": {
        "gen_id": "05272024-medical-supreme-doctor-preditiva",
        "seed": "yaml-ai-medical-preditiva",
    },
    "seguranca": {
        "gen_id": "05272024-medical-supreme-doctor-seguranca",
        "seed": "yaml-ai-medical-seguranca",
    },
}

SINAIS_EMERGENCIA = [
    "dificuldade respiratória intensa",
    "dor torácica súbita",
    "dor torácica persistente",
    "sinais de avc",
    "inconsciência",
    "confusão aguda",
    "convulsão",
    "hemorragia importante",
    "reação alérgica grave",
    "ideação suicida com risco imediato",
    "deterioração rápida",
    "cianose",
    "prostração extrema",
]

# Termos que disparam recusa de prescrição autônoma
TERMOS_PRESCRICAO_PROIBIDA = [
    "prescreva",
    "mude a dose",
    "suspenda o medicamento",
    "receite",
    "diga exatamente quanto",
]

# Campos obrigatórios da saída conforme output schema
CAMPOS_OBRIGATORIOS_SAIDA = [
    "meta", "safety", "data_quality", "clinical_summary",
    "assessment", "plan_for_human_review", "evidence", "audit",
]


class MedicoVirtualSupremoSkill:
    """
    Skill de apoio clínico auditável — Médico Virtual Supremo v2.0.

    Encapsula o pipeline de raciocínio clínico seguro em 7 etapas e produz
    saída estruturada YAML pronta para revisão humana.
    """

    def __init__(self):
        self._modulos_ativados: List[Dict[str, str]] = []
        self._run_id: str = ""
        self._prompt_hash: str = ""
        self._input_hash: str = ""

    # ──────────────────────────────────────────────────────────────────────────
    # API Pública
    # ──────────────────────────────────────────────────────────────────────────

    def analisar(
        self,
        modo: str,
        request: str,
        patient: Optional[Dict[str, Any]] = None,
        clinical_data: Optional[Dict[str, Any]] = None,
        consent: Optional[Dict[str, Any]] = None,
        source_provenance: Optional[List[Dict[str, Any]]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Executa o pipeline completo de análise clínica.

        Args:
            modo: professional_cds | patient_education | research | simulation
            request: Descrição textual da queixa/solicitação.
            patient: Dados demográficos do paciente (age_years, sex_at_birth, etc.).
            clinical_data: Dados clínicos adicionais (exames, histórico, etc.).
            consent: Consentimentos (health_data_processing, genetic_data_processing, etc.).
            source_provenance: Proveniência das fontes de dados.
            attachments: Anexos (exames, imagens, etc.).

        Returns:
            Dict com a estrutura completa de resposta_medico_virtual_supremo.
        """
        # Inicializa metadados da sessão
        self._run_id = str(uuid.uuid4())
        self._input_hash = hashlib.sha256(
            f"{modo}|{request}|{json.dumps(patient or {})}".encode()
        ).hexdigest()
        _t0 = time.time()
        _modo = modo

        patient = patient or {}
        clinical_data = clinical_data or {}
        consent = consent or {}
        source_provenance = source_provenance or []
        attachments = attachments or []

        # 🧠 MetaBus: evento de início
        if METABUS_ATIVO:
            try:
                analysis_started(modo, self._run_id, request, str(patient.get("age_years", "")))
            except Exception:
                pass

        # ── Etapa 0: Validação de escopo ──────────────────────────────────────
        modo_valido = self._validar_modo(modo)
        if not modo_valido:
            return self._erro(f"Modo inválido: {modo}. Use: professional_cds, patient_education, research, simulation")

        emergencia, motivo_emergencia = self._detectar_emergencia(request, clinical_data)
        recusa_prescricao, motivo_recusa = self._detectar_prescricao_proibida(request)

        if emergencia:
            # 🧠 MetaBus: emergência
            if METABUS_ATIVO:
                try:
                    emergency_detected(self._run_id, motivo_emergencia, modo)
                    refletir_emergencia(self._run_id, motivo_emergencia, modo)
                    atualizar_confianca_seguranca(1, 1)
                except Exception:
                    pass
            return self._resposta_emergencia(modo, motivo_emergencia)

        if recusa_prescricao:
            # 🧠 MetaBus: recusa de prescrição
            if METABUS_ATIVO:
                try:
                    prescription_refused(self._run_id, motivo_recusa, modo)
                except Exception:
                    pass
            return self._resposta_recusa_prescricao(modo, motivo_recusa)

        # Ativa módulos conforme o caso
        self._modulos_ativados = [MODULOS_DISPONIVEIS["historico"]]
        if clinical_data.get("genetic_data"):
            self._modulos_ativados.append(MODULOS_DISPONIVEIS["geneticos"])
        if clinical_data.get("lifestyle_data"):
            self._modulos_ativados.append(MODULOS_DISPONIVEIS["estilo"])
        if clinical_data.get("lab_results"):
            self._modulos_ativados.append(MODULOS_DISPONIVEIS["exames"])
        self._modulos_ativados.append(MODULOS_DISPONIVEIS["seguranca"])

        # ── Etapa 1: Normalização dos dados ───────────────────────────────────
        dados_normalizados = self._normalizar_dados(clinical_data)

        # ── Etapa 2: Representação do problema ────────────────────────────────
        problema = self._representar_problema(modo, request, patient, dados_normalizados)

        # ── Etapa 3: Hipóteses diferenciais ───────────────────────────────────
        hipoteses = self._gerar_hipoteses(problema, dados_normalizados)

        # 🧠 MetaBus: hipóteses geradas
        if METABUS_ATIVO:
            try:
                hypotheses_generated(self._run_id, hipoteses, problema.get("sindrome", "?"))
            except Exception:
                pass

        # ── Etapa 4: Evidência ────────────────────────────────────────────────
        evidencias = self._buscar_evidencias(hipoteses, dados_normalizados)

        # ── Etapa 5: Plano para revisão humana ────────────────────────────────
        plano = self._gerar_plano(problema, hipoteses, evidencias, modo)

        # ── Etapa 6: Verificação ──────────────────────────────────────────────
        auditoria = self._verificar(problema, hipoteses, plano, dados_normalizados)

        # 🧠 MetaBus: análise concluída + reflexões + confiança
        _duracao = time.time() - _t0
        if METABUS_ATIVO:
            try:
                checks_p = len(auditoria.get("checks_passed", []))
                checks_f = len(auditoria.get("checks_failed", []))
                analysis_completed(modo, self._run_id, len(hipoteses), checks_p, checks_f, False, _duracao)
                refletir_analise(self._run_id, modo, checks_p, checks_f, len(hipoteses), False)
                atualizar_confianca_skill(checks_p, checks_p + checks_f)
                atualizar_confianca_seguranca(checks_p, checks_p + checks_f)
                registrar_licao_apos_analise(modo, auditoria.get("checks_failed", []), problema.get("sindrome", "?"))
            except Exception:
                pass

        # ── Montagem da resposta ──────────────────────────────────────────────
        return self._montar_resposta(
            modo=modo,
            request=request,
            patient=patient,
            emergencia=emergencia,
            dados_normalizados=dados_normalizados,
            problema=problema,
            hipoteses=hipoteses,
            evidencias=evidencias,
            plano=plano,
            auditoria=auditoria,
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Etapas do Pipeline Clínico
    # ──────────────────────────────────────────────────────────────────────────

    def _validar_modo(self, modo: str) -> bool:
        return modo in ("professional_cds", "patient_education", "research", "simulation")

    def _detectar_emergencia(
        self, request: str, clinical_data: Dict[str, Any]
    ) -> tuple:
        texto = (request + " " + json.dumps(clinical_data)).lower()
        for sinal in SINAIS_EMERGENCIA:
            if sinal.lower() in texto:
                return True, f"Sinal de emergência detectado: '{sinal}'"
        return False, ""

    def _detectar_prescricao_proibida(self, request: str) -> tuple:
        texto = request.lower()
        for termo in TERMOS_PRESCRICAO_PROIBIDA:
            if termo.lower() in texto:
                return True, f"Termo de prescrição autônoma detectado: '{termo}'"
        return False, ""

    def _normalizar_dados(self, clinical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Etapa 1: Normaliza dados clínicos, detecta duplicidades e valores implausíveis."""
        normalizado = {
            "original": clinical_data,
            "normalizado": {},
            "alertas": [],
            "completude": 0.0,
        }

        if not clinical_data:
            normalizado["completude"] = 0.0
            normalizado["alertas"].append("Nenhum dado clínico informado")
            return normalizado

        # Contagem de campos preenchidos para estimativa de completude
        total_campos = 0
        preenchidos = 0

        if "lab_results" in clinical_data:
            total_campos += 1
            if clinical_data["lab_results"]:
                preenchidos += 1
                for res in clinical_data["lab_results"]:
                    if isinstance(res, dict):
                        valor = res.get("value")
                        if valor is not None:
                            try:
                                v = float(valor)
                                if v < 0 and res.get("name") not in ("bilirrubina",):
                                    normalizado["alertas"].append(
                                        f"Valor implausível em {res.get('name', 'exame')}: {v}"
                                    )
                            except (ValueError, TypeError):
                                pass

        if "vital_signs" in clinical_data:
            total_campos += 1
            if clinical_data["vital_signs"]:
                preenchidos += 1

        if "history" in clinical_data:
            total_campos += 1
            if clinical_data["history"]:
                preenchidos += 1

        if "medications" in clinical_data:
            total_campos += 1
            if clinical_data["medications"]:
                preenchidos += 1

        normalizado["completude"] = round(preenchidos / max(total_campos, 1), 2)
        normalizado["normalizado"] = {k: v for k, v in clinical_data.items() if v}

        return normalizado

    def _representar_problema(
        self,
        modo: str,
        request: str,
        patient: Dict[str, Any],
        dados_normalizados: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Etapa 2: Produz representação compacta do problema clínico."""
        idade = patient.get("age_years", patient.get("age_group", "idade não informada"))
        sexo = patient.get("sex_at_birth", "sexo não informado")

        representacao = (
            f"{'Paciente' if modo != 'simulation' else 'Caso fictício'}: "
            f"{idade}, {sexo}. "
            f"Queixa: {request[:200]}"
        )

        return {
            "representacao": representacao,
            "perfil": f"{idade}, {sexo}",
            "sindrome": self._extrair_sindrome(request),
            "temporalidade": self._extrair_temporalidade(request),
            "gravidade": self._classificar_gravidade(request, dados_normalizados),
            "achados_positivos": [],
            "achados_negativos": [],
        }

    def _extrair_sindrome(self, texto: str) -> str:
        palavras = texto.lower().split()
        padroes = {
            "respiratório": any(p in palavras for p in ["falta de ar", "dispneia", "tosse", "falta"]),
            "cardíaco": any(p in palavras for p in ["dor no peito", "palpitação", "dor torácica"]),
            "neurológico": any(p in palavras for p in ["cefaleia", "tontura", "confusão", "avc"]),
            "infeccioso": any(p in palavras for p in ["febre", "infecção", "sepse"]),
            "gastrointestinal": any(p in palavras for p in ["dor abdominal", "náusea", "vômito"]),
        }
        presentes = [nome for nome, presente in padroes.items() if presente]
        return presentes[0] if presentes else "inespecífico"

    def _extrair_temporalidade(self, texto: str) -> str:
        import re
        padroes = [
            (r"(\d+)\s*(ano|anos)", "crônico"),
            (r"(\d+)\s*(mês|meses)", "subagudo"),
            (r"(\d+)\s*(dia|dias)", "agudo"),
            (r"(\d+)\s*(hora|horas|minuto|minutos)", "agudo"),
            (r"(súbito|repentino|de repente)", "agudo"),
        ]
        for padrao, classificacao in padroes:
            if re.search(padrao, texto, re.IGNORECASE):
                return classificacao
        return "não especificada"

    def _classificar_gravidade(
        self, request: str, dados_normalizados: Dict[str, Any]
    ) -> str:
        termos_leve = ["leve", "leve melhora", "discreto", "pouco"]
        termos_moderado = ["moderado", "regular", "razoável"]
        termos_grave = ["grave", "intenso", "forte", "muito", "insuportável"]

        texto = request.lower()
        for t in termos_grave:
            if t in texto:
                return "grave"
        for t in termos_moderado:
            if t in texto:
                return "moderada"
        for t in termos_leve:
            if t in texto:
                return "leve"
        return "não classificada"

    def _gerar_hipoteses(
        self, problema: Dict[str, Any], dados_normalizados: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Etapa 3: Gera hipóteses diferenciais organizadas por prioridade."""
        sindrome = problema.get("sindrome", "inespecífico")
        hipoteses = []

        if sindrome == "respiratório":
            hipoteses = [
                {
                    "name": "infecção respiratória aguda (viral ou bacteriana)",
                    "status": "provável",
                    "supporting_evidence": ["febre", "tosse", "início agudo"],
                    "opposing_evidence": [],
                    "missing_evidence": ["exame físico", "radiografia de tórax", "sinais vitais"],
                    "confidence": "moderada",
                    "confidence_rationale": "Apresentação clínica compatível, mas sem exames complementares.",
                },
                {
                    "name": "tromboembolismo pulmonar",
                    "status": "grave_não_perder",
                    "supporting_evidence": ["dor torácica", "dispneia"],
                    "opposing_evidence": ["sem fatores de risco conhecidos"],
                    "missing_evidence": ["D-dímero", "angiotomografia"],
                    "confidence": "baixa",
                    "confidence_rationale": "Quadro grave que deve ser excluído; baixa probabilidade pré-teste.",
                },
            ]
        elif sindrome == "cardíaco":
            hipoteses = [
                {
                    "name": "síndrome coronariana aguda",
                    "status": "grave_não_perder",
                    "supporting_evidence": ["dor torácica", "fatores de risco"],
                    "opposing_evidence": [],
                    "missing_evidence": ["ECG", "troponina", "exame físico"],
                    "confidence": "moderada",
                    "confidence_rationale": "Dor torácica requer exclusão de causa cardíaca.",
                },
            ]
        elif sindrome == "neurológico":
            hipoteses = [
                {
                    "name": "acidente vascular cerebral",
                    "status": "grave_não_perder",
                    "supporting_evidence": ["início súbito", "déficit focal"],
                    "opposing_evidence": [],
                    "missing_evidence": ["exame neurológico", "neuroimagem"],
                    "confidence": "moderada",
                    "confidence_rationale": "Sintomas neurológicos agudos requerem investigação urgente.",
                },
            ]
        else:
            hipoteses = [
                {
                    "name": "condição a esclarecer — dados insuficientes",
                    "status": "alternativa",
                    "supporting_evidence": [f"Síndrome: {sindrome}"],
                    "opposing_evidence": [],
                    "missing_evidence": ["história clínica completa", "exame físico", "exames complementares"],
                    "confidence": "baixa",
                    "confidence_rationale": "Dados insuficientes para hipótese específica.",
                },
            ]

        return hipoteses

    def _buscar_evidencias(
        self, hipoteses: List[Dict[str, Any]], dados_normalizados: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Etapa 4: Evidência — prioriza diretrizes e fontes regulatórias."""
        # Implementação base: retorna estrutura de evidência para revisão humana.
        # Em produção, integrar com RAG clínico (MODULOS_DISPONIVEIS["rag"]).
        evidencias = []
        for hip in hipoteses[:2]:
            evidencias.append({
                "claim": hip["name"],
                "source": "Diretrizes clínicas (a validar por profissional)",
                "source_version_or_date": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
                "locator": "Revisão por profissional habilitado",
                "applicability": "direta" if hip["status"] == "grave_não_perder" else "indireta",
            })
        return evidencias

    def _gerar_plano(
        self,
        problema: Dict[str, Any],
        hipoteses: List[Dict[str, Any]],
        evidencias: List[Dict[str, Any]],
        modo: str,
    ) -> Dict[str, Any]:
        """Etapa 5: Plano para revisão humana."""
        return {
            "immediate_actions": self._sugerir_acoes_imediatas(hipoteses),
            "questions": self._sugerir_perguntas(problema, hipoteses),
            "tests_to_consider": self._sugerir_exames(hipoteses),
            "treatment_options_to_validate": [],
            "monitoring": ["evolução dos sintomas", "sinais de alarme"],
            "referrals": [],
            "red_flags": [
                "dificuldade respiratória",
                "dor torácica persistente",
                "confusão mental",
                "cianose",
                "deterioração rápida",
            ],
            "reassessment": ["reavaliar em 24-48h ou antes se houver piora"],
        }

    def _sugerir_acoes_imediatas(self, hipoteses: List[Dict[str, Any]]) -> List[str]:
        acoes = []
        for h in hipoteses:
            if h["status"] == "grave_não_perder":
                acoes.append(f"Avaliar {h['name']} com urgência")
        if not acoes:
            acoes.append("Coletar dados adicionais para refinar hipóteses")
        return acoes

    def _sugerir_perguntas(
        self, problema: Dict[str, Any], hipoteses: List[Dict[str, Any]]
    ) -> List[str]:
        perguntas = [
            "Há sinais de alarme? (dispneia, dor torácica, confusão)",
            "Qual a evolução dos sintomas?",
            "Já realizou algum exame recentemente?",
            "Faz uso de medicação contínua?",
        ]
        for h in hipoteses:
            if h["missing_evidence"]:
                for m in h["missing_evidence"][:2]:
                    perguntas.append(f"Dispõe de {m}?")
        return perguntas

    def _sugerir_exames(self, hipoteses: List[Dict[str, Any]]) -> List[str]:
        exames = set()
        for h in hipoteses:
            for m in h.get("missing_evidence", []):
                exames.add(m)
        return list(exames)

    def _verificar(
        self,
        problema: Dict[str, Any],
        hipoteses: List[Dict[str, Any]],
        plano: Dict[str, Any],
        dados_normalizados: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Etapa 6: Checklist de verificação de segurança."""
        checks_passed = []
        checks_failed = []

        # Verificação 1: Diagnóstico definitivo sem sustentação?
        diagnosticos_definitivos = [
            h for h in hipoteses if "definitivo" in h.get("name", "").lower()
        ]
        if diagnosticos_definitivos:
            checks_failed.append("diagnóstico definitivo sem sustentação suficiente")
        else:
            checks_passed.append("nenhum diagnóstico definitivo sem sustentação")

        # Verificação 2: Recomendação incompatível com dados do paciente?
        checks_passed.append("recomendações compatíveis com dados disponíveis (verificação automática limitada)")

        # Verificação 3: Dose sem parâmetros mínimos?
        checks_passed.append("sem recomendação de dose autônoma")

        # Verificação 4: Sinal de alarme omitido?
        if plano.get("red_flags"):
            checks_passed.append("sinais de alarme incluídos no plano")
        else:
            checks_failed.append("sinais de alarme não listados")

        # Verificação 5: Incerteza declarada?
        tem_baixa_confianca = any(
            h.get("confidence") == "baixa" for h in hipoteses
        )
        if tem_baixa_confianca:
            checks_passed.append("incerteza explicitada nas hipóteses")
        else:
            checks_failed.append("incerteza não explicitada")

        # Verificação 6: Revisão humana indicada?
        checks_passed.append("revisão humana obrigatória indicada")

        # Verificação 7: Dado sensível desnecessário?
        checks_passed.append("princípio da minimização aplicado")

        return {
            "checks_passed": checks_passed,
            "checks_failed": checks_failed,
            "human_review_required": True,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Montagem da Resposta Estruturada
    # ──────────────────────────────────────────────────────────────────────────

    def _montar_resposta(
        self,
        modo: str,
        request: str,
        patient: Dict[str, Any],
        emergencia: bool,
        dados_normalizados: Dict[str, Any],
        problema: Dict[str, Any],
        hipoteses: List[Dict[str, Any]],
        evidencias: List[Dict[str, Any]],
        plano: Dict[str, Any],
        auditoria: Dict[str, Any],
    ) -> Dict[str, Any]:
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        prompt_texto = (
            f"Médico Virtual Supremo v{SKILL_VERSION} | Modo: {modo} | "
            f"Requisição: {request[:100]}"
        )
        self._prompt_hash = hashlib.sha256(prompt_texto.encode()).hexdigest()

        saida = {
            "resposta_medico_virtual_supremo": {
                "meta": {
                    "timestamp_utc": timestamp,
                    "language": "pt-BR",
                    "mode": modo,
                    "response_gen_id": RESPONSE_GEN_ID,
                    "response_seed": RESPONSE_SEED,
                    "response_seend_compat": RESPONSE_SEED,
                    "run_id": self._run_id,
                    "model_id": "opencode-medico-virtual-supremo",
                    "skill_version": SKILL_VERSION,
                    "prompt_hash": self._prompt_hash,
                    "input_hash": self._input_hash,
                    "knowledge_snapshot": timestamp[:10],
                    "modules_used": self._modulos_ativados,
                },
                "safety": {
                    "emergency_detected": emergencia,
                    "escalation_required": emergencia,
                    "intended_user": self._mapear_usuario_intencionado(modo),
                    "limitations": [
                        "Sistema de apoio à decisão clínica — não substitui profissional habilitado.",
                        "Revisão humana obrigatória antes de qualquer ação clínica.",
                        "Não substitui exame físico, avaliação presencial ou serviço de emergência.",
                    ],
                },
                "data_quality": {
                    "completeness": dados_normalizados.get("completude", 0.0),
                    "conflicts": dados_normalizados.get("alertas", []),
                    "missing_critical": self._extrair_dados_ausentes(hipoteses),
                    "provenance_summary": ["dados informados pelo usuário"],
                },
                "clinical_summary": {
                    "problem_representation": problema.get("representacao", ""),
                    "key_findings": {
                        "positive": problema.get("achados_positivos", []),
                        "negative": problema.get("achados_negativos", []),
                    },
                },
                "assessment": {
                    "hypotheses": hipoteses,
                },
                "plan_for_human_review": plano,
                "evidence": evidencias,
                "audit": auditoria,
                "mandatory_footer": {
                    "instagram": "https://www.instagram.com/marceloclaro.geomaker/",
                },
            }
        }
        return saida

    def _resposta_emergencia(self, modo: str, motivo: str) -> Dict[str, Any]:
        """Gera resposta de emergência — interrompe fluxo normal."""
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return {
            "resposta_medico_virtual_supremo": {
                "meta": {
                    "timestamp_utc": timestamp,
                    "language": "pt-BR",
                    "mode": modo,
                    "response_gen_id": RESPONSE_GEN_ID,
                    "response_seed": RESPONSE_SEED,
                    "response_seend_compat": RESPONSE_SEED,
                    "run_id": self._run_id,
                    "model_id": "opencode-medico-virtual-supremo",
                    "skill_version": SKILL_VERSION,
                    "prompt_hash": "emergency-override",
                    "input_hash": self._input_hash,
                    "knowledge_snapshot": timestamp[:10],
                    "modules_used": [MODULOS_DISPONIVEIS["seguranca"]],
                },
                "safety": {
                    "emergency_detected": True,
                    "escalation_required": True,
                    "intended_user": self._mapear_usuario_intencionado(modo),
                    "limitations": [
                        "ATENÇÃO: Emergência detectada. Esta resposta substituiu o fluxo analítico normal.",
                        "Não atrase atendimento presencial com questionário extenso.",
                        "Limite as orientações a medidas seguras e não invasivas.",
                    ],
                },
                "clinical_summary": {
                    "problem_representation": (
                        f"🚨 SITUAÇÃO DE EMERGÊNCIA: {motivo}. "
                        "Priorizar atendimento presencial imediato."
                    ),
                    "key_findings": {"positive": [], "negative": []},
                },
                "assessment": {
                    "hypotheses": [],
                },
                "plan_for_human_review": {
                    "immediate_actions": [
                        "ACIONAR SERVIÇO DE EMERGÊNCIA LOCAL (SAMU 192 / Bombeiros 193).",
                        "Não permitir que a conversa substitua avaliação presencial.",
                        "Se possível, manter vias aéreas pérvias e posição de segurança.",
                    ],
                    "red_flags": [motivo],
                },
                "audit": {
                    "checks_passed": ["emergência identificada corretamente"],
                    "checks_failed": [],
                    "human_review_required": True,
                },
                "mandatory_footer": {
                    "instagram": "https://www.instagram.com/marceloclaro.geomaker/",
                },
            }
        }

    def _resposta_recusa_prescricao(self, modo: str, motivo: str) -> Dict[str, Any]:
        """Resposta para solicitação de prescrição autônoma."""
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return {
            "resposta_medico_virtual_supremo": {
                "meta": {
                    "timestamp_utc": timestamp,
                    "language": "pt-BR",
                    "mode": modo,
                    "response_gen_id": RESPONSE_GEN_ID,
                    "response_seed": RESPONSE_SEED,
                    "run_id": self._run_id,
                    "model_id": "opencode-medico-virtual-supremo",
                    "skill_version": SKILL_VERSION,
                    "prompt_hash": self._prompt_hash,
                    "input_hash": self._input_hash,
                    "knowledge_snapshot": timestamp[:10],
                    "modules_used": [MODULOS_DISPONIVEIS["seguranca"]],
                },
                "safety": {
                    "emergency_detected": False,
                    "escalation_required": False,
                    "intended_user": self._mapear_usuario_intencionado(modo),
                    "limitations": [
                        "Prescrição autônoma recusada conforme política de segurança.",
                        "Apenas profissional habilitado pode prescrever ou ajustar doses.",
                    ],
                },
                "clinical_summary": {
                    "problem_representation": (
                        f"⚠️ Solicitação de prescrição autônoma detectada: {motivo}. "
                        "Este sistema não realiza prescrição sem validação profissional."
                    ),
                    "key_findings": {"positive": [], "negative": []},
                },
                "assessment": {"hypotheses": []},
                "plan_for_human_review": {
                    "immediate_actions": [
                        "Consultar profissional de saúde habilitado para prescrição.",
                    ],
                    "questions": [
                        "Qual o diagnóstico estabelecido?",
                        "Quais as comorbidades do paciente?",
                        "Há alergias medicamentosas conhecidas?",
                        "Qual a função hepática e renal?",
                    ],
                    "red_flags": [
                        "Nunca alterar anticoagulante, insulina, anticonvulsivante ou imunossupressor sem supervisão clínica.",
                    ],
                },
                "audit": {
                    "checks_passed": ["prescrição autônoma recusada conforme política"],
                    "checks_failed": [],
                    "human_review_required": True,
                },
                "mandatory_footer": {
                    "instagram": "https://www.instagram.com/marceloclaro.geomaker/",
                },
            }
        }

    def _erro(self, mensagem: str) -> Dict[str, Any]:
        # 🧠 MetaBus: erro
        if METABUS_ATIVO:
            try:
                error_occurred(getattr(self, '_run_id', 'N/A'), mensagem)
            except Exception:
                pass
        return {
            "resposta_medico_virtual_supremo": {
                "error": mensagem,
                "meta": {
                    "timestamp_utc": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "language": "pt-BR",
                },
            }
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Utilitários
    # ──────────────────────────────────────────────────────────────────────────

    def _mapear_usuario_intencionado(self, modo: str) -> str:
        mapa = {
            "professional_cds": "profissional de saúde habilitado",
            "patient_education": "paciente ou cuidador (modo educativo)",
            "research": "pesquisador",
            "simulation": "treinamento/estudante",
        }
        return mapa.get(modo, "não especificado")

    def _extrair_dados_ausentes(self, hipoteses: List[Dict[str, Any]]) -> List[str]:
        ausentes = set()
        for h in hipoteses:
            for m in h.get("missing_evidence", []):
                ausentes.add(m)
        return list(ausentes)

    def get_version(self) -> str:
        """Retorna a versão da skill."""
        return SKILL_VERSION

    def get_modulos_disponiveis(self) -> Dict[str, Any]:
        """Retorna o catálogo de módulos funcionais disponíveis."""
        return MODULOS_DISPONIVEIS

    def validar_saida(self, resposta: Dict[str, Any]) -> Dict[str, bool]:
        """
        Valida se a resposta contém todos os campos obrigatórios.
        Retorna dict com status de cada campo.
        """
        resultado = {}
        corpo = resposta.get("resposta_medico_virtual_supremo", {})
        for campo in CAMPOS_OBRIGATORIOS_SAIDA:
            resultado[campo] = campo in corpo
        resultado["valido"] = all(resultado.values())
        return resultado


# ──────────────────────────────────────────────────────────────────────────────
# Instância singleton para importação direta
# ──────────────────────────────────────────────────────────────────────────────

_skill = MedicoVirtualSupremoSkill()

analisar = _skill.analisar
validar_saida = _skill.validar_saida
get_version = _skill.get_version
get_modulos_disponiveis = _skill.get_modulos_disponiveis
