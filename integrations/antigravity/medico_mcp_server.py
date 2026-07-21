# -*- coding: utf-8 -*-
"""
MCP Server — Médico Virtual Supremo para Antigravity CLI
===========================================================
Implementa ferramentas MCP que o Antigravity CLI (e qualquer cliente MCP)
pode chamar para realizar análises clínicas.

Ferramentas MCP expostas:
  - medico_analisar      → Análise clínica completa
  - medico_urgencia      → Triagem de emergência
  - medico_especialistas → Roteamento para especialista via transformer
  - medico_validar       → Validação cruzada multi-especialista

Uso (standalone):
    python3 medico_mcp_server.py

Uso (Antigravity Bridge):
    from integrations.antigravity.medico_mcp_server import MedicoMCPToolset
"""

import json
import sys
import os
from typing import Any, Dict, List, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


class MedicoMCPToolset:
    """
    Conjunto de ferramentas MCP para o Médico Virtual Supremo.
    Cada método corresponde a uma tool MCP exposta para o Antigravity CLI.
    """

    def __init__(self):
        self._skill = None
        self._pipeline = None
        self._cross_validator = None

    @property
    def skill(self):
        if self._skill is None:
            from skills.medico_virtual_supremo.skill import MedicoVirtualSupremoSkill
            self._skill = MedicoVirtualSupremoSkill()
        return self._skill

    @property
    def pipeline(self):
        if self._pipeline is None:
            from skills.medico_virtual_supremo.orchestration.transformer_pipeline import (
                criar_pipeline_padrao
            )
            self._pipeline = criar_pipeline_padrao()
        return self._pipeline

    @property
    def cross_validator(self):
        if self._cross_validator is None:
            from skills.medico_virtual_supremo.plugins.cross_validation import (
                CrossValidationPlugin,
            )
            v = CrossValidationPlugin()
            v.registrar_especialista("cardiologia", ["ecg", "ecocardiograma"])
            v.registrar_especialista("neurologia", ["eeg", "neuroimagem"])
            v.registrar_especialista("infectologia", ["microbiologia", "antibioticoterapia"])
            self._cross_validator = v
        return self._cross_validator

    # ──────────────────────────────────────────────────────────────────────────
    # Tools MCP
    # ──────────────────────────────────────────────────────────────────────────

    def analisar(
        self,
        modo: str,
        request: str,
        patient: Optional[Dict[str, Any]] = None,
        clinical_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Tool MCP: Realiza análise clínica completa.

        Args:
            modo: professional_cds | patient_education | research | simulation
            request: Descrição do caso clínico
            patient: Dados demográficos opcionais
            clinical_data: Dados clínicos opcionais

        Returns:
            Dict com resultado completo no formato resposta_medico_virtual_supremo
        """
        resultado = self.skill.analisar(
            modo=modo,
            request=request,
            patient=patient or {},
            clinical_data=clinical_data or {},
        )
        return resultado

    def urgencia(self, request: str) -> Dict[str, Any]:
        """
        Tool MCP: Triagem rápida de urgência/emergência.

        Args:
            request: Descrição dos sintomas

        Returns:
            Dict com avaliação de urgência
        """
        emergencia, motivo = self.skill._detectar_emergencia(request, {})
        return {
            "emergencia_detectada": emergencia,
            "motivo": motivo,
            "orientacao": (
                "ACIONAR SAMU 192 IMEDIATAMENTE" if emergencia
                else "Buscar avaliação médica para diagnóstico completo"
            ),
        }

    def especialistas(self, caso: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tool MCP: Roteia caso para especialistas via transformer pipeline.

        Args:
            caso: Dicionário com dados do caso clínico

        Returns:
            Dict com ranking de especialistas
        """
        resultado = self.pipeline.processar(caso)
        return {
            "caso_id": resultado.caso_id,
            "score_urgencia": resultado.score_urgencia,
            "especialista_principal": {
                "nome": resultado.especialista_principal.nome,
                "especialidade": resultado.especialista_principal.especialidade,
            } if resultado.especialista_principal else None,
            "especialistas_ranqueados": [
                {
                    "nome": e.nome,
                    "especialidade": e.especialidade,
                    "peso_atencao": round(p, 3),
                }
                for e, p in resultado.especialistas_ranqueados
            ],
            "justificativa": resultado.justificativa,
        }

    def validar_cruzado(self, caso: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tool MCP: Validação cruzada multi-especialista.

        Args:
            caso: Dicionário com hipóteses e evidências

        Returns:
            Dict com relatório de validação cruzada
        """
        report = self.cross_validator.validar(caso)
        return {
            "caso_id": report.caso_id,
            "consenso": report.consenso_geral,
            "num_especialistas": report.num_especialistas_consultados,
            "score_confianca": round(report.score_confianca_geral, 3),
            "conflitos": report.conflitos[:5],
            "summary": report.summary,
        }

    def raciocinar(
        self,
        prob_pre_teste: float,
        teste: str,
        resultado_teste: bool,
        hipotese: str = "",
    ) -> Dict[str, Any]:
        """
        Tool MCP: Raciocínio bayesiano para diagnóstico.

        Args:
            prob_pre_teste: Probabilidade pré-teste (0-1)
            teste: Nome do teste (ecg_para_iam, troponina_para_iam, etc.)
            resultado_teste: True se positivo, False se negativo
            hipotese: Nome da hipótese diagnóstica

        Returns:
            Dict com probabilidade pós-teste e interpretação
        """
        from skills.medico_virtual_supremo.reasoning.diagnostic_reasoning import (
            criar_raciocinio_padrao,
        )
        motor = criar_raciocinio_padrao()
        try:
            bayes = motor.avaliar_teste(teste, prob_pre_teste, resultado_teste, hipotese)
            return {
                "hipotese": bayes.hipotese,
                "probabilidade_pre_teste": bayes.prob_pre_teste,
                "probabilidade_pos_teste": bayes.prob_pos_teste,
                "lr_aplicado": bayes.lr_aplicado,
                "variacao": bayes.variacao,
                "interpretacao": bayes.interpretacao,
            }
        except ValueError as e:
            return {"erro": str(e)}

    def listar_ferramentas(self) -> List[Dict[str, Any]]:
        """
        Retorna o catálogo de ferramentas MCP disponíveis.
        """
        return [
            {
                "name": "medico_analisar",
                "description": "Análise clínica completa com pipeline de 7 etapas",
                "parameters": ["modo", "request", "patient?", "clinical_data?"],
            },
            {
                "name": "medico_urgencia",
                "description": "Triagem rápida de urgência/emergência",
                "parameters": ["request"],
            },
            {
                "name": "medico_especialistas",
                "description": "Roteia caso para especialista via transformer pipeline",
                "parameters": ["caso"],
            },
            {
                "name": "medico_validar_cruzado",
                "description": "Validação cruzada multi-especialista",
                "parameters": ["caso"],
            },
            {
                "name": "medico_raciocinar",
                "description": "Raciocínio bayesiano para diagnóstico",
                "parameters": ["prob_pre_teste", "teste", "resultado_teste", "hipotese?"],
            },
        ]


# ──────────────────────────────────────────────────────────────────────────────
# MCP Server (protocolo stdio)
# ──────────────────────────────────────────────────────────────────────────────

def serve_stdio():
    """
    Inicia servidor MCP no modo stdio (linha a linha JSON).
    Compatível com o formato MCP padrão do Antigravity CLI.
    """
    toolset = MedicoMCPToolset()
    router = {
        "analisar": toolset.analisar,
        "urgencia": toolset.urgencia,
        "especialistas": toolset.especialistas,
        "validar_cruzado": toolset.validar_cruzado,
        "raciocinar": toolset.raciocinar,
        "listar_ferramentas": toolset.listar_ferramentas,
    }

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            method = req.get("method", "")
            params = req.get("params", {})
            req_id = req.get("id", 0)

            if method in router:
                result = router[method](**params)
                response = {"id": req_id, "result": result}
            elif method == "listar_ferramentas":
                response = {"id": req_id, "result": toolset.listar_ferramentas()}
            else:
                response = {
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Método não encontrado: {method}"},
                }
        except Exception as e:
            response = {"error": {"code": -32603, "message": str(e)}}

        print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    serve_stdio()
