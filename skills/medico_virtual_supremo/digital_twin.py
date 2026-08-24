# -*- coding: utf-8 -*-
"""Gêmeo digital para simulações clínicas fictícias.

Este módulo NÃO modela pacientes reais, não prevê prognóstico individual e não
prescreve tratamento. Ele cria trajetórias contrafactuais para ensino, pesquisa
metodológica e teste de hipóteses, sempre com revisão humana obrigatória.
"""
from __future__ import annotations

import hashlib
import json
import math
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Protocol


class SwarmProtocol(Protocol):
    def predict(self, question: str, signal: float = 0.5, noise: float = 0.12) -> Dict[str, Any]: ...


@dataclass(frozen=True)
class TwinState:
    step: int
    label: str
    physiological_state: Dict[str, float]
    intervention: str
    outcome_score: float
    uncertainty: float
    assumptions: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class DigitalTwinResult:
    twin_id: str
    run_id: str
    created_at_utc: str
    simulation_only: bool
    source_hash: str
    model_contract: str
    trajectories: List[TwinState]
    mirofish: Dict[str, Any]
    reversa_review: Dict[str, Any]
    safety: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["trajectories"] = [asdict(t) for t in self.trajectories]
        return data


class ReversaMedicalReviewer:
    """Revisor adversarial determinístico inspirado no agente Reversa.

    Procura causalidade indevida, extrapolação, baixa completude e confiança
    excessiva. Não gera conduta clínica.
    """

    def review(self, *, case: Dict[str, Any], trajectories: List[TwinState], swarm: Dict[str, Any]) -> Dict[str, Any]:
        findings: List[Dict[str, str]] = []
        completeness = float(case.get("data_completeness", 0.0) or 0.0)
        consensus = float(swarm.get("consensus", 0.0) or 0.0)

        if completeness < 0.6:
            findings.append({"severity": "high", "code": "REV-DATA-001", "message": "Dados simulados incompletos; trajetórias não devem ser interpretadas como prognóstico."})
        if consensus > 0.9:
            findings.append({"severity": "medium", "code": "REV-CONS-001", "message": "Consenso elevado não equivale a validade clínica externa."})
        if any(t.uncertainty < 0.1 for t in trajectories):
            findings.append({"severity": "high", "code": "REV-UNC-001", "message": "Incerteza artificialmente baixa em pelo menos uma trajetória."})
        if not findings:
            findings.append({"severity": "info", "code": "REV-OK-001", "message": "Nenhum desvio estrutural crítico detectado; revisão profissional continua obrigatória."})

        return {
            "reviewer": "reversa-medical-adversarial",
            "decision": "block_clinical_use" if any(f["severity"] == "high" for f in findings) else "simulation_only",
            "findings": findings,
            "counterfactual_questions": [
                "Quais premissas, se invertidas, mudariam a trajetória?",
                "Há variável omitida que explique o mesmo desfecho?",
                "A direção causal foi confundida com correlação?",
            ],
        }


class MedicalDigitalTwinEngine:
    """Cria um gêmeo digital por execução em modo ``simulation``.

    O motor é determinístico quando recebe o mesmo ``seed`` e o mesmo swarm.
    O swarm pode ser o ``mirofish.MiroFishSwarm`` existente ou um fake em testes.
    """

    CONTRACT_VERSION = "medical-digital-twin/1.0"

    def __init__(
        self,
        swarm: Optional[SwarmProtocol] = None,
        reversa: Optional[ReversaMedicalReviewer] = None,
        seed: int = 42,
    ) -> None:
        self.seed = seed
        self.swarm = swarm or self._build_default_swarm(seed)
        self.reversa = reversa or ReversaMedicalReviewer()

    @staticmethod
    def _build_default_swarm(seed: int) -> SwarmProtocol:
        from mirofish.swarm import MiroFishSwarm
        return MiroFishSwarm(n_agents=15, seed=seed)

    def build(
        self,
        *,
        run_id: str,
        request: str,
        patient: Dict[str, Any],
        clinical_data: Dict[str, Any],
        hypotheses: List[Dict[str, Any]],
        interventions: Optional[List[str]] = None,
        horizon_steps: int = 4,
    ) -> DigitalTwinResult:
        if horizon_steps < 2 or horizon_steps > 12:
            raise ValueError("horizon_steps deve estar entre 2 e 12")

        interventions = interventions or ["observação simulada", "coleta adicional de dados"]
        canonical = {
            "request": request,
            "patient": patient,
            "clinical_data": clinical_data,
            "hypotheses": hypotheses,
            "interventions": interventions,
            "horizon_steps": horizon_steps,
        }
        source_hash = hashlib.sha256(json.dumps(canonical, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        completeness = self._completeness(patient, clinical_data)
        base_signal = self._base_signal(hypotheses, completeness)

        swarm_result = self.swarm.predict(
            question=f"Trajetória simulada do caso {source_hash[:12]} permanecerá estável?",
            signal=base_signal,
            noise=0.08,
        )
        aggregate = float(swarm_result.get("aggregate", base_signal))
        consensus = float(swarm_result.get("consensus", 0.0))

        trajectories: List[TwinState] = []
        for step in range(horizon_steps):
            intervention = interventions[min(step, len(interventions) - 1)]
            drift = (step / max(horizon_steps - 1, 1)) * (aggregate - 0.5) * 0.35
            outcome = max(0.0, min(1.0, base_signal + drift))
            uncertainty = max(0.12, min(0.95, 1.0 - completeness * 0.55 - consensus * 0.25 + step * 0.03))
            trajectories.append(TwinState(
                step=step,
                label=f"T{step}",
                physiological_state={
                    "stability_index": round(outcome, 4),
                    "data_completeness": round(completeness, 4),
                    "swarm_consensus": round(consensus, 4),
                },
                intervention=intervention,
                outcome_score=round(outcome, 4),
                uncertainty=round(uncertainty, 4),
                assumptions=[
                    "caso inteiramente fictício",
                    "sem calibração clínica externa",
                    "sem efeito causal atribuído à intervenção",
                ],
            ))

        case = {"data_completeness": completeness, **canonical}
        reversa_review = self.reversa.review(case=case, trajectories=trajectories, swarm=swarm_result)
        return DigitalTwinResult(
            twin_id=f"mdt-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            simulation_only=True,
            source_hash=source_hash,
            model_contract=self.CONTRACT_VERSION,
            trajectories=trajectories,
            mirofish={
                "engine": "MiroFishSwarm",
                "prediction_id": swarm_result.get("prediction_id"),
                "aggregate": round(aggregate, 4),
                "consensus": round(consensus, 4),
                "n_agents": swarm_result.get("n_agents"),
                "interpretation": "dispersão de cenários simulados; não é probabilidade clínica",
            },
            reversa_review=reversa_review,
            safety={
                "clinical_use_allowed": False,
                "prescription_allowed": False,
                "diagnostic_claim_allowed": False,
                "human_review_required": True,
                "warning": "Gêmeo digital educacional e experimental. Não usar para decisões sobre pacientes reais.",
            },
        )

    @staticmethod
    def _completeness(patient: Dict[str, Any], clinical_data: Dict[str, Any]) -> float:
        required = [patient.get("age_years"), patient.get("sex_at_birth"), clinical_data.get("history"), clinical_data.get("vital_signs"), clinical_data.get("lab_results")]
        return round(sum(value not in (None, "", [], {}) for value in required) / len(required), 4)

    @staticmethod
    def _base_signal(hypotheses: List[Dict[str, Any]], completeness: float) -> float:
        severe = sum(h.get("status") == "grave_não_perder" for h in hypotheses)
        signal = 0.55 + completeness * 0.15 - min(severe, 2) * 0.12
        return max(0.05, min(0.95, signal))


def attach_digital_twin_to_simulation(
    result: Dict[str, Any],
    *,
    request: str,
    patient: Dict[str, Any],
    clinical_data: Dict[str, Any],
    engine: Optional[MedicalDigitalTwinEngine] = None,
) -> Dict[str, Any]:
    """Anexa automaticamente um gêmeo digital a uma resposta de simulação."""
    body = result.get("resposta_medico_virtual_supremo", result)
    mode = body.get("meta", {}).get("mode")
    if mode != "simulation":
        return result

    hypotheses = body.get("assessment", {}).get("hypotheses", [])
    run_id = body.get("meta", {}).get("run_id") or body.get("meta", {}).get("analysis_id") or uuid.uuid4().hex
    twin = (engine or MedicalDigitalTwinEngine()).build(
        run_id=run_id,
        request=request,
        patient=patient,
        clinical_data=clinical_data,
        hypotheses=hypotheses,
    )
    body["digital_twin"] = twin.to_dict()
    return result
