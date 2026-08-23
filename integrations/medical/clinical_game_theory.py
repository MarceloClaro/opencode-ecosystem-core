# -*- coding: utf-8 -*-
"""
Motor de Teoria dos Jogos e Grafos de Decisão Diagnóstica
=========================================================
Implementa:
1. Grafos de Decisão Bayesiana e Atualização por Razão de Verossimilhança (LR+/LR-).
2. Seleção de Exames por Redução de Entropia de Shannon (Information Gain).
3. Matrizes de Payoff e Critério Minimax Regret (Médico vs. Natureza).
4. Gerador de Anamnese Guiada por Grafos e Fatores de Risco.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class DiagnosticHypothesis:
    """Representa uma hipótese diagnóstica com probabilidades e pesos de risco."""
    name: str
    prior_probability: float  # 0.0 a 1.0
    severity_level: str       # "baixa", "moderada", "alta", "critica"
    critical_miss_penalty: float  # 0.0 a 10.0 (penalidade se não diagnosticada)
    status: str = "provavel"  # "provavel", "grave_nao_perder", "alternativa", "iatrogenica"
    supporting_findings: List[str] = field(default_factory=list)
    opposing_findings: List[str] = field(default_factory=list)
    missing_evidence: List[str] = field(default_factory=list)
    posterior_probability: float = 0.0
    confidence_rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "prior_probability": round(self.prior_probability, 4),
            "posterior_probability": round(self.posterior_probability if self.posterior_probability > 0 else self.prior_probability, 4),
            "severity_level": self.severity_level,
            "critical_miss_penalty": self.critical_miss_penalty,
            "status": self.status,
            "supporting_findings": self.supporting_findings,
            "opposing_findings": self.opposing_findings,
            "missing_evidence": self.missing_evidence,
            "confidence_rationale": self.confidence_rationale,
        }


@dataclass
class DiagnosticTest:
    """Representa um exame ou teste propedêutico discriminatório."""
    name: str
    target_condition: str
    sensitivity: float        # 0.0 a 1.0
    specificity: float        # 0.0 a 1.0
    cost_score: float         # 1.0 a 10.0 (custo financeiro/tempo)
    invasiveness_score: float # 0.0 a 10.0 (risco de complicações)
    turnaround_hours: float   # tempo para resultado
    contraindications: List[str] = field(default_factory=list)

    @property
    def lr_positive(self) -> float:
        """Razão de Verossimilhança Positiva (LR+ = Sens / (1 - Espec))."""
        denom = max(1.0 - self.specificity, 0.001)
        return self.sensitivity / denom

    @property
    def lr_negative(self) -> float:
        """Razão de Verossimilhança Negativa (LR- = (1 - Sens) / Espec)."""
        denom = max(self.specificity, 0.001)
        return (1.0 - self.sensitivity) / denom

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "target_condition": self.target_condition,
            "sensitivity": self.sensitivity,
            "specificity": self.specificity,
            "lr_positive": round(self.lr_positive, 2),
            "lr_negative": round(self.lr_negative, 3),
            "cost_score": self.cost_score,
            "invasiveness_score": self.invasiveness_score,
            "turnaround_hours": self.turnaround_hours,
            "contraindications": self.contraindications,
        }


class DiagnosticDecisionGraph:
    """Grafo Bayesiano de Decisão Clínica com Atualização Propedêutica."""

    def __init__(self, hypotheses: List[DiagnosticHypothesis]) -> None:
        self.hypotheses = hypotheses
        self._normalize_priors()

    def _normalize_priors(self) -> None:
        """Garante que as probabilidades a priori somem 1.0."""
        total = sum(h.prior_probability for h in self.hypotheses)
        if total > 0:
            for h in self.hypotheses:
                h.prior_probability /= total
                h.posterior_probability = h.prior_probability

    def update_with_test_result(self, test: DiagnosticTest, outcome_positive: bool) -> Dict[str, float]:
        """Aplica o Teorema de Bayes para atualizar probabilidades com base no resultado do exame."""
        updated = {}
        for h in self.hypotheses:
            if h.name.lower() == test.target_condition.lower() or test.target_condition.lower() in h.name.lower():
                lr = test.lr_positive if outcome_positive else test.lr_negative
            else:
                # Para outras condições, o teste atua como discriminante inverso
                lr = (1.0 / test.lr_positive) if outcome_positive else (1.0 / max(test.lr_negative, 0.001))

            # Odds pré-teste
            prior = max(min(h.posterior_probability, 0.999), 0.001)
            prior_odds = prior / (1.0 - prior)
            post_odds = prior_odds * lr
            post_prob = post_odds / (1.0 + post_odds)
            h.posterior_probability = post_prob
            updated[h.name] = post_prob

        # Re-normalização global
        total_post = sum(h.posterior_probability for h in self.hypotheses)
        if total_post > 0:
            for h in self.hypotheses:
                h.posterior_probability /= total_post
                updated[h.name] = h.posterior_probability

        return updated


class ShannonEntropyEngine:
    """Calculador de Entropia de Shannon e Ganho de Informação Propedêutico."""

    @staticmethod
    def calculate_entropy(probabilities: List[float]) -> float:
        """Calcula H(D) = - sum(p * log2(p))."""
        entropy = 0.0
        for p in probabilities:
            if p > 0.0001:
                entropy -= p * math.log2(p)
        return max(entropy, 0.0)

    @classmethod
    def calculate_information_gain(cls, hypotheses: List[DiagnosticHypothesis], test: DiagnosticTest) -> float:
        """Calcula o Ganho de Informação esperado IG(T) para um teste clínico."""
        priors = [h.posterior_probability if h.posterior_probability > 0 else h.prior_probability for h in hypotheses]
        h_initial = cls.calculate_entropy(priors)

        # Probabilidade esperada de teste positivo
        p_target = 0.0
        for h in hypotheses:
            if h.name.lower() == test.target_condition.lower() or test.target_condition.lower() in h.name.lower():
                p_target = h.posterior_probability if h.posterior_probability > 0 else h.prior_probability
                break

        p_pos = (p_target * test.sensitivity) + ((1.0 - p_target) * (1.0 - test.specificity))
        p_neg = 1.0 - p_pos

        # Simula pós-teste positivo
        sim_pos = []
        for h in hypotheses:
            is_target = h.name.lower() == test.target_condition.lower() or test.target_condition.lower() in h.name.lower()
            lr = test.lr_positive if is_target else (1.0 / max(test.lr_positive, 0.01))
            p = h.posterior_probability if h.posterior_probability > 0 else h.prior_probability
            odds = (p / max(1.0 - p, 0.001)) * lr
            sim_pos.append(odds / (1.0 + odds))
        tot_pos = sum(sim_pos) or 1.0
        sim_pos = [x / tot_pos for x in sim_pos]

        # Simula pós-teste negativo
        sim_neg = []
        for h in hypotheses:
            is_target = h.name.lower() == test.target_condition.lower() or test.target_condition.lower() in h.name.lower()
            lr = test.lr_negative if is_target else (1.0 / max(test.lr_negative, 0.01))
            p = h.posterior_probability if h.posterior_probability > 0 else h.prior_probability
            odds = (p / max(1.0 - p, 0.001)) * lr
            sim_neg.append(odds / (1.0 + odds))
        tot_neg = sum(sim_neg) or 1.0
        sim_neg = [x / tot_neg for x in sim_neg]

        h_pos = cls.calculate_entropy(sim_pos)
        h_neg = cls.calculate_entropy(sim_neg)

        expected_h = (p_pos * h_pos) + (p_neg * h_neg)
        ig = h_initial - expected_h
        return max(ig, 0.0)


class ClinicalGameTheoryEngine:
    """Motor de Teoria dos Jogos e Minimax Regret para Decisão Médica sob Incerteza."""

    def __init__(self, hypotheses: List[DiagnosticHypothesis], available_tests: List[DiagnosticTest]) -> None:
        self.hypotheses = hypotheses
        self.tests = available_tests

    def build_payoff_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Constrói a matriz de utilidade U(Estado, Ação).
        Estados: Cada hipótese diagnóstica real d_i
        Ações: Cada teste propedêutico t_j
        """
        payoffs: Dict[str, Dict[str, float]] = {}
        for h in self.hypotheses:
            payoffs[h.name] = {}
            for t in self.tests:
                is_match = (h.name.lower() == t.target_condition.lower() or t.target_condition.lower() in h.name.lower())
                if is_match:
                    # Teste correto para a doença: ganho proporcional à sensibilidade e severidade
                    utility = 100.0 * t.sensitivity - (t.cost_score * 2.0) - (t.invasiveness_score * 3.0)
                else:
                    # Teste desnecessário para essa doença: custo + risco de falso positivo
                    utility = 0.0 - (t.cost_score * 2.0) - (t.invasiveness_score * 3.0)
                    # Se a doença não testada for grave, penalidade pelo atraso diagnóstico
                    utility -= (h.critical_miss_penalty * 8.0)
                payoffs[h.name][t.name] = utility
        return payoffs

    def compute_minimax_regret(self) -> Dict[str, Any]:
        """
        Aplica o critério de Minimax Regret (Savage, 1951):
        Calcula o Arrependimento R(s, a) = max_a' U(s, a') - U(s, a).
        A melhor ação é a que minimiza o arrependimento máximo: a* = argmin_a max_s R(s, a).
        """
        payoffs = self.build_payoff_matrix()
        if not payoffs:
            return {"recommended_action": None, "max_regrets": {}, "optimal_path": []}

        # 1. Encontra a utilidade máxima para cada estado
        max_utility_per_state = {}
        for h_name, actions in payoffs.items():
            max_utility_per_state[h_name] = max(actions.values()) if actions else 0.0

        # 2. Constrói a matriz de arrependimento
        regret_matrix: Dict[str, Dict[str, float]] = {}
        for h_name, actions in payoffs.items():
            regret_matrix[h_name] = {}
            for t_name, val in actions.items():
                regret_matrix[h_name][t_name] = max_utility_per_state[h_name] - val

        # 3. Calcula o arrependimento máximo para cada ação
        max_regret_per_action = {}
        for t in self.tests:
            max_r = max(regret_matrix[h.name].get(t.name, 0.0) for h in self.hypotheses)
            max_regret_per_action[t.name] = round(max_r, 2)

        # 4. Ação ótima é a que minimiza o arrependimento máximo
        best_test_name = min(max_regret_per_action, key=max_regret_per_action.get)
        best_test = next((t for t in self.tests if t.name == best_test_name), None)

        # Ranqueia todas as ações
        ranked_actions = sorted(max_regret_per_action.items(), key=lambda x: x[1])

        return {
            "recommended_action": best_test_name,
            "best_test_details": best_test.to_dict() if best_test else None,
            "max_regrets": max_regret_per_action,
            "ranked_strategy": ranked_actions,
            "game_type": "Physician vs. Nature (Savage Minimax Regret)",
            "safety_rationale": "Garante que hipóteses com risco de dano irreversível não sejam negligenciadas."
        }


class ClinicalAnamnesisGenerator:
    """Gerador e estruturador de Anamnese Guiada por Redução de Incerteza."""

    @staticmethod
    def generate_problem_representation(patient_profile: Dict[str, Any], chief_complaint: str, duration: str, severity: str) -> str:
        """Gera a frase clínica compacta padronizada."""
        age = patient_profile.get("age", "Idade não informada")
        sex = patient_profile.get("sex", "Sexo não informado")
        comorbidities = patient_profile.get("comorbidities", [])
        comorb_str = f"com histórico de {', '.join(comorbidities)}" if comorbidities else "sem comorbidades prévias relatadas"

        return (
            f"Paciente {sex}, {age} anos, {comorb_str}, apresentando {chief_complaint} "
            f"com início há {duration}. Gravidade aparente: {severity}."
        )

    @staticmethod
    def prioritize_clinical_questions(hypotheses: List[DiagnosticHypothesis], questions_catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ordena as perguntas de anamnese pelo poder de esclarecimento de hipóteses graves."""
        scored_questions = []
        for q in questions_catalog:
            target = q.get("target_condition", "").lower()
            # Peso base + severidade da hipótese associada
            associated_hyp = next((h for h in hypotheses if target in h.name.lower()), None)
            weight = (associated_hyp.critical_miss_penalty * 1.5) if associated_hyp else 3.0
            scored_questions.append({
                "question": q["text"],
                "target_condition": q.get("target_condition", "Geral"),
                "clinical_utility_score": round(weight, 1),
                "rationale": f"Esclarece critérios para {q.get('target_condition', 'hipótese clínica')}."
            })

        return sorted(scored_questions, key=lambda x: x["clinical_utility_score"], reverse=True)
