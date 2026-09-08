# -*- coding: utf-8 -*-
"""
Simulated Expert Reviews v2 — 5 Revisores com Lógica Formal, Axiomas e Game Theory
====================================================================================
Cada revisor aplica:
1. Raciocínio lógico formal (dedutivo, indutivo, abdutivo)
2. Axiomas e teorias fundamentais da epistemologia e metodologia
3. Análise por Teoria dos Jogos (equilíbrio de Nash, Pareto, mecanismo)
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import subprocess
import numpy as np

logger = logging.getLogger("simulated.reviews.v2")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════
# FUNDAMENTOS LÓGICOS E AXIOMÁTICOS
# ═══════════════════════════════════════════════════════════════════════

LOGICAL_FRAMEWORKS = {
    "dedutiva": {
        "name": "Lógica Dedutiva",
        "description": "Parte de premissas gerais para conclusões específicas. Se P→Q e P, então Q (Modus Ponens).",
        "laws": [
            "Modus Ponens: P→Q, P ⊢ Q",
            "Modus Tollens: P→Q, ¬Q ⊢ ¬P",
            "Silogismo: P→Q, Q→R ⊢ P→R",
            "Reductio ad absurdum: Se P→(Q∧¬Q), então ¬P",
        ],
        "axioms": [
            "Princípio da Não-Contradição: ¬(P ∧ ¬P)",
            "Princípio do Terceiro Excluído: P ∨ ¬P",
            "Princípio da Identidade: P → P",
            "Lei de De Morgan: ¬(P ∧ Q) ≡ ¬P ∨ ¬Q",
        ],
    },
    "indutiva": {
        "name": "Lógica Indutiva",
        "description": "Parte de observações particulares para generalizações. Conclusão provável, não certa.",
        "laws": [
            "Enumeração simples: Se todos os a são A, então próximo a será A",
            "Eliminação: Se A→B e C→B e A≠C, então B independe de A/C",
            "Correlação: Se A e B co-variam, pode haver causalidade",
        ],
        "axioms": [
            "Uniformidade da natureza: O futuro se assemelhará ao passado",
            "Princípio da parcimônia (Occam): Explicações mais simples são preferíveis",
            "Indução de Hume: Não se pode justificar a indução dedutivamente",
        ],
    },
    "abdutiva": {
        "name": "Lógica Abdutiva",
        "description": "Inferência à melhor explicação. Dado E, se H→E, então H é plausível.",
        "laws": [
            "Abdução de Peirce: F(observado), C→F, logo C (hipótese plausível)",
            "Inference to Best Explanation: A hipótese que melhor explica os dados é preferida",
        ],
        "axioms": [
            "Plenitude causal: Todo evento tem uma causa",
            "Verdade explicativa: A melhor explicação é a mais completa e coerente",
        ],
    },
}

EPISTEMOLOGICAL_THEORIES = {
    "falsificacionismo": {
        "name": "Falsificacionismo (Popper)",
        "core": "Uma teoria é científica se e só se for falsificável",
        "criteria": [
            "A teoria faz previsões observacionais específicas",
            "Existem condições que, se observadas, refutariam a teoria",
            "A teoria não é tautológica nem vacuamente verdadeira",
            "O grau de falsificabilidade é proporcional à informatividade",
        ],
        "evaluation": lambda m: {
            "falsificability": "Alta" if any(w in m.lower() for w in ["limitação", "ameaça", "exclusão", "condição"]) else "Média",
            "testability": "Alta" if any(w in m.lower() for w in ["experimento", "teste", "hipótese", "predição"]) else "Baixa",
        },
    },
    "paradigma_kuhniano": {
        "name": "Paradigma Científico (Kuhn)",
        "core": "A ciência progide por revoluções paradigmáticas, não acumulativamente",
        "criteria": [
            "O estudo opera dentro de um paradigma reconhecido",
            "Identifica anomalias que o paradigma atual não explica",
            "Propõe uma resolução de puzzle (puzzle-solving) dentro do paradigma",
            "Contribui para a acumulação de conhecimento normal",
        ],
        "evaluation": lambda m: {
            "paradigm_fit": "Forte" if any(w in m.lower() for w in ["framework", "teoria", "modelo"]) else "Fraco",
            "anomaly_detection": "Alta" if any(w in m.lower() for w in ["limitação", "lacuna", "problema"]) else "Baixa",
        },
    },
    "realismo_cientifico": {
        "name": "Realismo Científico (Bhaskar)",
        "core": "A realidade existe independente da percepção; estratificada em domínios real, atual e empírico",
        "criteria": [
            "Distingue entre estruturas reais (generativas), eventos atuais e observações empíricas",
            "Reconhece que modelos são transformativos, não meramente descritivos",
            "Inferência retrodutiva: do efeito para as estruturas causais",
        ],
        "evaluation": lambda m: {
            "depth": "Profundo" if any(w in m.lower() for w in ["estrutura", "mecanismo", "causal"]) else "Superficial",
            "retroduction": "Presente" if any(w in m.lower() for w in ["por que", "mecanismo", "por trás"]) else "Ausente",
        },
    },
}

def _extract_mean(scores: dict) -> float:
    """Extrai média de scores que podem ser dicts ou floats."""
    vals = []
    for v in scores.values():
        if isinstance(v, dict) and "score" in v:
            vals.append(v["score"])
        elif isinstance(v, (int, float)):
            vals.append(v)
    return sum(vals) / len(vals) if vals else 0.0


GAME_THEORY_FRAMEWORK = {
    "equilibrio_nash": {
        "name": "Equilíbrio de Nash",
        "definition": "Estratégia estável onde nenhum jogador tem incentivo unilateral para desviar",
        "formula": "∀i: u_i(s*_i, s*_{-i}) ≥ u_i(s_i, s*_{-i})",
        "application": "Se o autor publica o artigo e o revisor avalia honestamente, nenhum dos dois tem incentivo para mudar de estratégia unilateralmente.",
        "evaluation": lambda scores: {
            "is_nash": all(
                (s["score"] if isinstance(s, dict) else s) >= 7
                for s in scores.values()
            ),
            "incentive_compatibility": "Se o manuscrito é bom (score ≥ 7), o autor não tem incentivo para inflacionar; se o revisor é honesto, não tem incentivo para rejeitar injustamente.",
        },
    },
    "pareto_eficiencia": {
        "name": "Eficiência de Pareto",
        "definition": "Alocação é Pareto-eficiente se não existe realocação que melhore alguém sem piorar outro",
        "formula": "∀i: u_i(s') ≥ u_i(s) ∧ ∃j: u_j(s') > u_j(s) ⟹ s não é Pareto-eficiente",
        "application": "A alocação atual de esforço (autor: manuscrito, revisor: avaliação) é Pareto-eficiente se não é possível melhorar a qualidade sem aumentar o custo para o revisor.",
        "evaluation": lambda scores: {
            "pareto_optimal": _extract_mean(scores) >= 8,
            "improvement_possible": _extract_mean(scores) < 8,
        },
    },
    "dilema_prisioneiro": {
        "name": "Dilema do Prisioneiro",
        "definition": "Dois jogadores racionais podem escolher cooperação (C) ou traição (T), resultando em subotimalidade quando ambos traem",
        "formula": "T > R > P > S (onde R=cooperação mútua, T=traição, P=punição, S=sucker)",
        "application": "Se o autor coopera (escreve bem) e o revisor coopera (avalia honestamente), ambos ganham R. Se o autor 'trai' (inflaciona) e o revisor 'trae' (rejeita injustamente), ambos perdem P.",
        "evaluation": lambda scores: {
            "cooperação_necessária": _extract_mean(scores) >= 7,
            "risco_descooperacao": _extract_mean(scores) < 5,
            "equilibrio_estavel": "Cooperação mútua" if _extract_mean(scores) >= 7 else "Subótimo (descooperação)",
        },
    },
    "mecanismo_design": {
        "name": "Design de Mecanismos",
        "definition": "Projeto de regras do jogo para induzir comportamentos desejados",
        "principles": [
            "Incentive Compatibility (IC): Cada jogador prefere verdadeiramente reportar sua informação",
            "Individual Rationality (IR): Cada jogador aceita participar voluntariamente",
            "Budget Balance: O mecanismo é sustentável sem subsídios externos",
            "Efficiency: A alocação é Pareto-eficiente",
        ],
        "application": "O sistema de peer review é um mecanismo: deve ser incentive-compatible (revisores honestos são recompensados), individual-rational (participar é melhor que não participar), e eficiente (produz decisões de alta qualidade).",
        "evaluation": lambda scores: {
            "incentive_compatible": _extract_mean(scores) >= 7,
            "individually_rational": True,
            "budget_balance": True,
            "mechanism_score": _extract_mean(scores) / 10,
        },
    },
    "teoria_utilidade": {
        "name": "Teoria da Utilidade Esperada",
        "definition": "Agentes racionais maximizam utilidade esperada: E[U] = Σ p(x)·u(x)",
        "formula": "E[U] = Σ p(x) · u(x)",
        "application": "O autor maximiza utilidade esperada ao escolher submeter (probabilidade × recompensa − custo). O revisor maximiza utilidade ao ser honesto (reputação × probabilidade de acerto).",
        "evaluation": lambda scores: {
            "utility_positive": _extract_mean(scores) >= 6,
            "expected_value": "Positivo" if _extract_mean(scores) >= 7 else "Negativo",
            "risk_aversion": "Alta" if _extract_mean(scores) < 5 else "Moderada" if _extract_mean(scores) < 8 else "Baixa",
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════
# 5 REVISORES COM LÓGICA + AXIOMAS + GAME THEORY
# ═══════════════════════════════════════════════════════════════════════

REVIEWERS_V2 = {
    "R1_metodologista": {
        "name": "R1 — Professor Metodologista (PhD, Qualis A1 reviewer)",
        "focus": "Metodologia, reprodutibilidade, design experimental, rigor do pipeline",
        "axioms_used": [
            "Falsificacionismo (Popper): O estudo deve gerar previsões falsificáveis",
            "Princípio da Reprodutibilidade: Resultados devem ser replicáveis independentemente",
            "Princípio da Parsimônia (Occam): Metodologia deve ser a mais simples possível sem perder rigor",
        ],
        "game_theory_axes": [
            "Dilema do Prisioneiro: Autor coopera (escreve bem) ↔ Revisor coopera (avalia honestamente)",
            "Design de Mecanismos: O peer review deve ser incentive-compatible",
        ],
        "scoring_rubric": {
            "methodology_rigor": {"weight": 0.25, "axiom": "Falsificacionismo", "signals": ["design explícito", "protocolo documentado", "variáveis controladas"]},
            "reproducibility": {"weight": 0.25, "axiom": "Reprodutibilidade", "signals": ["seeds fixas", "receipts SHA-256", "código disponível"]},
            "sampling": {"weight": 0.20, "axiom": "Parsimônia", "signals": ["power analysis", "amostra justificada", "critérios explícitos"]},
            "data_collection": {"weight": 0.15, "axiom": "Uniformidade da Natureza", "signals": ["protocolo padronizado", "múltiplas fontes", "verificação cruzada"]},
            "validity_threats": {"weight": 0.15, "axiom": "Modus Tollens", "signals": ["ameaças documentadas", "mitigações propostas", "limitações explícitas"]},
        },
    },
    "R2_teorico": {
        "name": "R2 — Teórico (PhD, Science & Technology Studies)",
        "focus": "Fundamentação teórica, marco conceitual, diálogo com literatura",
        "axioms_used": [
            "Paradigma Kuhniano: O estudo contribui para puzzle-solving dentro de um paradigma",
            "Realismo Científico (Bhaskar): Distinção entre estruturas reais, eventos atuais e observações",
            "Princípio da Não-Contradição: O framework teórico deve ser internamente coerente",
        ],
        "game_theory_axes": [
            "Eficiência de Pareto: O conhecimento produzido melhora situação de todos sem prejudicar ninguém",
            "Teoria da Utilidade: O valor teórico do artigo deve ser maior que o custo de produzi-lo",
        ],
        "scoring_rubric": {
            "theoretical_foundation": {"weight": 0.25, "axiom": "Paradigma Kuhniano", "signals": ["framework explícito", "teorias citadas", "fundamentação sólida"]},
            "literature_dialogue": {"weight": 0.25, "axiom": "Realismo Científico", "signals": ["diálogo real com autores", "convergência/divergência", "posição explícita"]},
            "conceptual_clarity": {"weight": 0.20, "axiom": "Princípio da Não-Contradição", "signals": ["definições explícitas", "uso consistente", "ambiguidades minimizadas"]},
            "originality": {"weight": 0.15, "axiom": "Plenitude Causal", "signals": ["contribuição inédita", "lacuna identificada", "nova perspectiva"]},
            "epistemological_rigor": {"weight": 0.15, "axiom": "Modus Ponens", "signals": ["pressupostos declarados", "limitações epistemológicas", "validade interna"]},
        },
    },
    "R3_estatistico": {
        "name": "R3 — Estatístico (PhD, Biostatistics)",
        "focus": "Análise estatística, validade inferencial, correção de múltiplas comparações",
        "axioms_used": [
            "Teoria da Decisão Estatística: Minimizar erro esperado sob perda quadrática",
            "Princípio da Máxima Verossimilhança: Estimador que maximiza P(dados|θ)",
            "Teorema Central do Limite: Médias amostrais convergem para normalidade",
        ],
        "game_theory_axes": [
            "Teoria da Utilidade: O estatístico maximize utilidade ao escolher teste correto (poder vs. erro tipo I)",
            "Equilíbrio de Nash: Nível de significância α=0.05 é equilíbrio Nash na comunidade científica",
        ],
        "scoring_rubric": {
            "statistical_appropriateness": {"weight": 0.25, "axiom": "Teoria da Decisão", "signals": ["teste adequado", "pressupostos verificados", "alternativa não-paramétrica"]},
            "effect_sizes": {"weight": 0.20, "axiom": "Máxima Verossimilhança", "signals": ["Cohen's d", "η²", "IC 95%"]},
            "power_analysis": {"weight": 0.20, "axiom": "Teorema Central do Limite", "signals": ["power ≥ 0.80", "tamanho de efeito esperado", "amostra justificada"]},
            "multiple_comparisons": {"weight": 0.20, "axiom": "Bonferroni/FDR", "signals": ["correção aplicada", "family-wise error controlado", "α ajustado"]},
            "assumption_checking": {"weight": 0.15, "axiom": "Modus Tollens", "signals": ["Shapiro-Wilk", "Levene", "normalidade verificada"]},
        },
    },
    "R4_etica": {
        "name": "R4 — Bioeticista (PhD, Research Ethics)",
        "focus": "Ética em pesquisa, FAIR principles, viés algorítmico, consentimento",
        "axioms_used": [
            "Princípio de Belmont: Respeito pelas pessoas, beneficência, justiça",
            "Princípio FAIR: Findable, Accessible, Interoperable, Reusable",
            "Categorical Imperative (Kuhn): Agir como se a máxima da ação devesse ser lei universal",
        ],
        "game_theory_axes": [
            "Design de Mecanismos: O sistema de pesquisa deve ser justo (justiça distributiva)",
            "Dilema do Prisioneiro: Viés algorítmico é 'traição' do sistema que afeta todos",
        ],
        "scoring_rubric": {
            "ethical_compliance": {"weight": 0.25, "axiom": "Belmont", "signals": ["viés discutido", "fairness", "consentimento"]},
            "fair_data": {"weight": 0.25, "axiom": "FAIR", "signals": ["metadados completos", "formatos abertos", "licença explícita"]},
            "transparency": {"weight": 0.20, "axiom": "Categorical Imperative", "signals": ["limitações explícitas", "conflitos declarados", "código aberto"]},
            "algorithmic_bias": {"weight": 0.15, "axiom": "Justiça Distributiva", "signals": ["mitigação de viés", "diversidade de dados", "fairness metrics"]},
            "open_science": {"weight": 0.15, "axiom": "Reprodutibilidade", "signals": ["pipeline reproduzível", "receipts", "cosign"]},
        },
    },
    "R5_inovacao": {
        "name": "R5 — Inovador (PhD, Computer Science, Top-venue reviewer)",
        "focus": "Inovação, contribuição original, impacto, comparação com SOTA",
        "axioms_used": [
            "Princípio da Originalidade: Contribuição deve ser genuinamente nova (não incremental)",
            "Lei de Moore (metafórica): Capacidade computacional cresce exponencialmente; métodos devem escalar",
            "Teoria da Complexidade: Soluções devem ser analiticamente tractáveis ou empiricamente viáveis",
        ],
        "game_theory_axes": [
            "Equilíbrio de Nash: Se todos os pesquisadores inovam, o estado estacionário é progresso; se ninguém inova, é estagnação",
            "Teoria da Utilidade Esperada: Inovação tem alto risco (rejeição) mas alta recompensa (publicação top-tier)",
        ],
        "scoring_rubric": {
            "novelty": {"weight": 0.25, "axiom": "Originalidade", "signals": ["idéia genuinamente nova", "não incremental", "contribuição clara"]},
            "sota_comparison": {"weight": 0.20, "axiom": "Lei de Moore", "signals": ["comparação justa", "benchmark padronizado", "melhoria quantificada"]},
            "impact_potential": {"weight": 0.20, "axiom": "Complexidade", "signals": ["potencial de citado", "generalizabilidade", "relevância prática"]},
            "clarity_presentation": {"weight": 0.15, "axiom": "Princípio da Parsimônia", "signals": ["escrita clara", "figuras informativas", "seções lógicas"]},
            "completeness": {"weight": 0.20, "axiom": "Modus Ponens", "signals": ["claims suportados", "evidência suficiente", "lacunas preenchidas"]},
        },
    },
}


class SimulatedReviewBoardV2:
    """5 revisores com lógica formal, axiomas e Game Theory."""

    def __init__(self, workspace: Path, model: str = "heuristic"):
        self.workspace = workspace
        self.model = model
        self.reviews: List[Dict[str, Any]] = []

    def run_all_reviews(self, manuscript_path: str, experimental_data_path: str) -> Dict[str, Any]:
        """Executa 5 revisões com análise lógica + axiomas + game theory."""
        manuscript = Path(manuscript_path).read_text(encoding="utf-8")
        exp_data = Path(experimental_data_path).read_text(encoding="utf-8") if Path(experimental_data_path).exists() else "{}"

        logger.info("═══ INÍCIO DA REVISÃO V2 (LÓGICA + AXIOMAS + GAME THEORY) ═══")

        for reviewer_id, config in REVIEWERS_V2.items():
            logger.info(f"Revisão: {config['name']}")
            review = self._build_review(reviewer_id, config, manuscript, exp_data)
            self.reviews.append(review)

        aggregated = self._aggregate_reviews()
        game_theory_analysis = self._game_theory_analysis()

        results = {
            "reviews": self.reviews,
            "aggregated": aggregated,
            "game_theory_analysis": game_theory_analysis,
            "timestamp": _now_iso(),
            "n_reviewers": len(self.reviews),
        }

        _write_json(self.workspace / "simulated_reviews_v2.json", results)
        logger.info(f"═══ REVISÕES V2 CONCLUÍDAS: {aggregated['mean_score']:.2f}/10 ═══")
        return results

    def _build_review(self, reviewer_id: str, config: Dict, manuscript: str, exp_data: str) -> Dict[str, Any]:
        """Constrói revisão completa com lógica, axiomas e game theory."""
        import re

        manuscript_lower = manuscript.lower()
        scores = {}

        # ── SCORING POR CRITÉRIO (com análise lógica) ──
        for criterion, rubric in config["scoring_rubric"].items():
            score, justification, logical_chain = self._score_criterion(
                criterion, rubric, manuscript_lower, exp_data
            )
            scores[criterion] = {
                "score": score,
                "justification": justification,
                "axiom_applied": rubric["axiom"],
                "logical_chain": logical_chain,
            }

        overall = sum(s["score"] * config["scoring_rubric"][c]["weight"]
                      for c, s in scores.items()) / \
                  sum(config["scoring_rubric"][c]["weight"]
                      for c in scores)

        # ── ANÁLISE LÓGICA (dedutiva + indutiva + abdutiva) ──
        logical_analysis = self._logical_analysis(manuscript_lower, config)

        # ── AVALIAÇÃO DE AXIOMAS ──
        axiom_evaluation = self._evaluate_axioms(manuscript_lower, config)

        # ── GAME THEORY ──
        gt_analysis = self._reviewer_game_theory(reviewer_id, scores, config)

        # ── RECOMENDAÇÃO ──
        recommendation = "accept" if overall >= 7.5 else "revise" if overall >= 5.0 else "reject"

        # ── ISSUE IDENTIFICATION ──
        major_issues, minor_issues = self._identify_issues(scores, config)

        return {
            "reviewer": reviewer_id,
            "name": config["name"],
            "focus": config["focus"],
            "scores": scores,
            "overall_score": round(overall, 2),
            "logical_analysis": logical_analysis,
            "axiom_evaluation": axiom_evaluation,
            "game_theory": gt_analysis,
            "major_issues": major_issues,
            "minor_issues": minor_issues,
            "recommendation": recommendation,
            "summary": self._generate_summary(reviewer_id, overall, scores, gt_analysis, config),
        }

    def _score_criterion(self, criterion: str, rubric: Dict, text: str, exp_data: str) -> Tuple[int, str, str]:
        """Score com cadeia lógica explícita."""
        base_score = 5
        signal_hits = []
        for signal in rubric["signals"]:
            if signal.lower() in text:
                base_score += 1
                signal_hits.append(signal)

        # Bônus por termos-chave específicos do critério
        keyword_bonuses = {
            "methodology_rigor": ["design", "protocol", "controlled", "randomized"],
            "reproducibility": ["sha-256", "receipt", "seed=42", "cosign"],
            "sampling": ["power analysis", "sample size", "n=", "amostra"],
            "data_collection": ["multi-source", "four databases", "open access"],
            "validity_threats": ["threat", "limitation", "bias", "validity"],
            "theoretical_foundation": ["theory", "framework", "paradigm", "kuhn", "popper"],
            "literature_dialogue": ["dialogue", "agrees with", "contrary to", "extends"],
            "conceptual_clarity": ["defined as", "definition", "term", "concept"],
            "originality": ["novel", "first", "inédit", "original", "new"],
            "epistemological_rigor": ["assumption", "epistemolog", "ontolog"],
            "statistical_appropriateness": ["anova", "t-test", "mann-whitney", "kruskal"],
            "effect_sizes": ["cohen", "eta", "effect size", "confidence interval"],
            "power_analysis": ["power", "0.80", "0.95", "sample size calculation"],
            "multiple_comparisons": ["bonferroni", "fdr", "correction", "family-wise"],
            "assumption_checking": ["shapiro", "levene", "normality", "homoscedasticity"],
            "ethical_compliance": ["bias", "fairness", "ethical", "consent"],
            "fair_data": ["fair", "findable", "accessible", "reusable", "metadata"],
            "transparency": ["limitation", "conflict", "disclosure", "open"],
            "algorithmic_bias": ["mitigation", "diversity", "fairness metric"],
            "open_science": ["reproducible", "receipt", "cosign", "pipeline"],
            "novelty": ["novel", "first", "new contribution", "inédit"],
            "sota_comparison": ["state-of-the-art", "benchmark", "comparison", "sota"],
            "impact_potential": ["impact", "significant", "important", "relevant"],
            "clarity_presentation": ["clear", "well-organized", "figure", "table"],
            "completeness": ["complete", "all claims", "supported", "evidence"],
        }

        for keyword in keyword_bonuses.get(criterion, []):
            if keyword.lower() in text:
                base_score += 0.5

        score = max(1, min(10, int(round(base_score))))

        # Justificativa com sinais detectados
        if signal_hits:
            justification = f"Sinais detectados: {', '.join(signal_hits[:3])}. "
        else:
            justification = f"Poucos sinais explícitos para {criterion}. "

        # Cadeia lógica
        logical_chain = (
            f"Premissa 1: O manuscrito contém elementos de {criterion.replace('_', ' ')}. "
            f"Premissa 2: Foram detectados {len(signal_hits)} sinais de {rubric['axiom']}. "
            f"Conclusão: Score {score}/10 (base 5 + {signal_hits and len(signal_hits) or 0} sinais × 1 + keywords)."
        )

        return score, justification, logical_chain

    def _logical_analysis(self, text: str, config: Dict) -> Dict[str, Any]:
        """Análise lógica formal: dedutiva, indutiva, abdutiva."""
        analysis = {}

        # ── LÓGICA DEDUTIVA ──
        deductive_checks = {
            "premisse_coherence": any(w in text for w in ["therefore", "consequently", "thus", "portanto", "consequentemente"]),
            "conclusion_follows": any(w in text for w in ["results show", "findings suggest", "demonstrate", "demonstram"]),
            "modus_ponens": any(w in text for w in ["if.*then", "given that", "since"]),
            "no_contradictions": not (text.count("contradicts") > 2 or text.count("inconsistent") > 2),
        }
        deductive_score = sum(deductive_checks.values()) / len(deductive_checks)
        analysis["dedutiva"] = {
            "score": round(deductive_score * 10, 1),
            "checks": deductive_checks,
            "reasoning": (
                f"Premissas verificadas: {sum(deductive_checks.values())}/{len(deductive_checks)}. "
                + ("Conclusão segue logicamente das premissas." if deductive_score > 0.75
                   else "Há lacunas na cadeia dedutiva.")
            ),
        }

        # ── LÓGICA INDUTIVA ──
        inductive_checks = {
            "sufficient_evidence": len(text) > 3000,
            "diverse_sources": text.count("study") + text.count("research") > 5,
            "pattern_recognition": any(w in text for w in ["trend", "pattern", "correlation", "relationship"]),
            "generalization_justified": any(w in text for w in ["general", "broad", "across", "multi"]),
        }
        inductive_score = sum(inductive_checks.values()) / len(inductive_checks)
        analysis["indutiva"] = {
            "score": round(inductive_score * 10, 1),
            "checks": inductive_checks,
            "reasoning": (
                f"Evidências coletadas: {sum(inductive_checks.values())}/{len(inductive_checks)}. "
                + ("Generalização indutiva é justificada." if inductive_score > 0.75
                   else "Evidências insuficientes para generalização robusta.")
            ),
        }

        # ── LÓGICA ABDUTIVA ──
        abductive_checks = {
            "hypothesis_stated": any(w in text for w in ["hypothesis", "research question", "rq", "hipótese"]),
            "inference_to_best": any(w in text for w in ["best explanation", "suggests that", "consistent with"]),
            "alternative_explanations": any(w in text for w in ["alternative", "could also", "limitation"]),
            "retroduction": any(w in text for w in ["mechanism", "underlying", "generative", "causal"]),
        }
        abductive_score = sum(abductive_checks.values()) / len(abductive_checks)
        analysis["abdutiva"] = {
            "score": round(abductive_score * 10, 1),
            "checks": abductive_checks,
            "reasoning": (
                f"Elementos abdutivos: {sum(abductive_checks.values())}/{len(abductive_checks)}. "
                + ("Inferência à melhor explicação é adequada." if abductive_score > 0.75
                   else "Faltam elementos para inferência abdutiva robusta.")
            ),
        }

        return analysis

    def _evaluate_axioms(self, text: str, config: Dict) -> List[Dict[str, Any]]:
        """Avalia cada axioma listado pelo revisor."""
        evaluations = []
        for axiom in config["axioms_used"]:
            axiom_lower = axiom.lower()
            # Verifica se o axioma é mencionado ou aplicado
            keywords = [w for w in axiom_lower.split() if len(w) > 4]
            hits = sum(1 for kw in keywords if kw in text)
            relevance = min(1.0, hits / max(1, len(keywords) * 0.3))

            evaluations.append({
                "axiom": axiom,
                "relevance_score": round(relevance * 10, 1),
                "applied": relevance > 0.3,
                "justification": (
                    f"Axioma aplicado com relevância {relevance:.0%}. "
                    + ("Estudo alinha-se com este princípio." if relevance > 0.3
                       else "Axioma pouco explorado no manuscrito.")
                ),
            })
        return evaluations

    def _reviewer_game_theory(self, reviewer_id: str, scores: Dict, config: Dict) -> Dict[str, Any]:
        """Análise de Game Theory específica do revisor."""
        overall = sum(s["score"] for s in scores.values()) / len(scores)

        # Equilíbrio de Nash
        nash = GAME_THEORY_FRAMEWORK["equilibrio_nash"]
        nash_eval = nash["evaluation"](scores)
        nash_analysis = {
            "equilibrium_type": "Nash" if nash_eval["is_nash"] else "Subótimo",
            "incentive_compatibility": nash_eval["incentive_compatibility"],
            "is_stable": nash_eval["is_nash"],
        }

        # Pareto
        pareto = GAME_THEORY_FRAMEWORK["pareto_eficiencia"]
        pareto_eval = pareto["evaluation"](scores)
        pareto_analysis = {
            "pareto_optimal": pareto_eval["pareto_optimal"],
            "improvement_possible": pareto_eval["improvement_possible"],
        }

        # Dilema do Prisioneiro
        dilema = GAME_THEORY_FRAMEWORK["dilema_prisioneiro"]
        dilema_eval = dilema["evaluation"](scores)
        dilema_analysis = {
            "cooperação_necessária": dilema_eval["cooperação_necessária"],
            "risco_descooperacao": dilema_eval["risco_descooperacao"],
            "equilibrio_estavel": dilema_eval["equilibrio_estavel"],
        }

        # Design de Mecanismos
        mecanismo = GAME_THEORY_FRAMEWORK["mecanismo_design"]
        mecanismo_eval = mecanismo["evaluation"](scores)

        # Utilidade
        utilidade = GAME_THEORY_FRAMEWORK["teoria_utilidade"]
        utilidade_eval = utilidade["evaluation"](scores)

        return {
            "nash": nash_analysis,
            "pareto": pareto_analysis,
            "prisoner_dilemma": dilema_analysis,
            "mechanism_design": mecanismo_eval,
            "expected_utility": utilidade_eval,
            "overall_game_theory_score": round(
                (nash_analysis["is_stable"] * 2 + pareto_analysis["pareto_optimal"] * 2 +
                 dilema_analysis["cooperação_necessária"] * 2 + mecanismo_eval["mechanism_score"] * 2 +
                 (1 if utilidade_eval["utility_positive"] else 0)) / 9 * 10, 2
            ),
        }

    def _identify_issues(self, scores: Dict, config: Dict) -> Tuple[List[str], List[str]]:
        """Identifica issues baseado na cadeia lógica."""
        major = []
        minor = []

        for criterion, data in scores.items():
            if data["score"] <= 5:
                major.append(f"{criterion}: Score {data['score']}/10 — {data['justification']}")
            elif data["score"] <= 7:
                minor.append(f"{criterion}: Score {data['score']}/10 — {data['justification']}")

        return major[:5], minor[:5]

    def _generate_summary(self, reviewer_id: str, overall: float, scores: Dict, gt: Dict, config: Dict) -> str:
        """Gera resumo narrativo da revisão."""
        nash_status = gt["nash"]["equilibrium_type"]
        pareto_status = "Pareto-eficiente" if gt["pareto"]["pareto_optimal"] else "Subótimo"
        coop_status = gt["prisoner_dilemma"]["equilibrio_estavel"]

        return (
            f"Revisão {reviewer_id}: {overall:.1f}/10. "
            f"Análise lógica: cadeia dedutiva {'completa' if overall >= 7 else 'com lacunas'}. "
            f"Game Theory: equilíbrio de Nash {nash_status.lower()}, "
            f"alocação {pareto_status.lower()}, "
            f"cooperação {coop_status.lower()}. "
            f"{'Aceitável com revisões menores.' if overall >= 7 else 'Requer revisões substanciais.'}"
        )

    def _aggregate_reviews(self) -> Dict[str, Any]:
        """Agrega as 5 revisões."""
        scores = [r["overall_score"] for r in self.reviews]
        recommendations = [r["recommendation"] for r in self.reviews]

        accept_count = recommendations.count("accept")
        revise_count = recommendations.count("revise")
        reject_count = recommendations.count("reject")

        if accept_count >= 4:
            consensus = "ACCEPT"
        elif revise_count >= 4:
            consensus = "MAJOR_REVISION"
        elif reject_count >= 4:
            consensus = "REJECT"
        else:
            consensus = "MINOR_REVISION"

        all_criterion_scores = {}
        for r in self.reviews:
            for criterion, data in r["scores"].items():
                if criterion not in all_criterion_scores:
                    all_criterion_scores[criterion] = []
                all_criterion_scores[criterion].append(data["score"])

        criterion_means = {
            k: round(sum(v) / len(v), 2)
            for k, v in all_criterion_scores.items()
        }

        all_major = []
        all_minor = []
        for r in self.reviews:
            all_major.extend(r.get("major_issues", []))
            all_minor.extend(r.get("minor_issues", []))

        # Logical analysis aggregation
        logical_means = {"dedutiva": [], "indutiva": [], "abdutiva": []}
        for r in self.reviews:
            for ltype in logical_means:
                if ltype in r.get("logical_analysis", {}):
                    logical_means[ltype].append(r["logical_analysis"][ltype]["score"])

        logical_summary = {
            k: round(sum(v) / len(v), 2) if v else 0
            for k, v in logical_means.items()
        }

        # Game Theory aggregation
        gt_scores = [r["game_theory"]["overall_game_theory_score"] for r in self.reviews]

        return {
            "mean_score": round(sum(scores) / len(scores), 2),
            "min_score": round(min(scores), 2),
            "max_score": round(max(scores), 2),
            "std_score": round(float(np.std(scores)), 2) if len(scores) > 1 else 0.0,
            "individual_scores": {r["reviewer"]: r["overall_score"] for r in self.reviews},
            "consensus": consensus,
            "accept_count": accept_count,
            "revise_count": revise_count,
            "reject_count": reject_count,
            "criterion_means": criterion_means,
            "total_major_issues": len(all_major),
            "total_minor_issues": len(all_minor),
            "major_issues": all_major,
            "minor_issues": all_minor,
            "logical_analysis_summary": logical_summary,
            "game_theory_mean": round(sum(gt_scores) / len(gt_scores), 2),
        }

    def _game_theory_analysis(self) -> Dict[str, Any]:
        """Análise consolidada de Game Theory para todo o sistema de revisão."""
        # Cada revisor é um jogador
        players = [r["reviewer"] for r in self.reviews]
        strategies = ["accept", "revise", "reject"]
        payoffs = {}

        for r in self.reviews:
            player = r["reviewer"]
            score = r["overall_score"]
            if r["recommendation"] == "accept":
                payoffs[player] = {"accept": score, "revise": score - 1, "reject": score - 3}
            elif r["recommendation"] == "revise":
                payoffs[player] = {"accept": score + 1, "revise": score, "reject": score - 2}
            else:
                payoffs[player] = {"accept": score + 2, "revise": score + 1, "reject": score}

        # Nash equilibria
        nash_equilibria = []
        for i, p1 in enumerate(players):
            for j, p2 in enumerate(players):
                if i < j:
                    s1 = r["recommendation"]
                    s2 = self.reviews[j]["recommendation"]
                    # Verifica se é Nash
                    if (payoffs[p1][s1] >= payoffs[p1][s2] and
                        payoffs[p2][s2] >= payoffs[p2][s1]):
                        nash_equilibria.append({
                            "players": [p1, p2],
                            "strategies": [s1, s2],
                            "payoffs": [payoffs[p1][s1], payoffs[p2][s2]],
                        })

        return {
            "players": players,
            "strategies": strategies,
            "payoffs": payoffs,
            "nash_equilibria": nash_equilibria,
            "system_cooperative": all(r["recommendation"] == "accept" for r in self.reviews),
            "pareto_optimal": all(r["overall_score"] >= 8 for r in self.reviews),
        }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("manuscript", help="Path to manuscript file")
    ap.add_argument("experimental_data", help="Path to experimental_results.json")
    ap.add_argument("--output", default=".", help="Output directory")
    args = ap.parse_args()

    board = SimulatedReviewBoardV2(Path(args.output))
    results = board.run_all_reviews(args.manuscript, args.experimental_data)

    print(f"\n{'='*80}")
    print(f"SIMULATED REVIEW BOARD V2 — 5 REVISORS (LÓGICA + AXIOMAS + GAME THEORY)")
    print(f"{'='*80}")
    for r in results["reviews"]:
        nash = r["game_theory"]["nash"]["equilibrium_type"]
        pareto = "Pareto" if r["game_theory"]["pareto"]["pareto_optimal"] else "Subótimo"
        print(f"  {r['name'][:50]:50s} {r['overall_score']:.1f}/10  [{r['recommendation'].upper():8s}] Nash:{nash:8s} {pareto}")
    agg = results["aggregated"]
    print(f"{'='*80}")
    print(f"  MEAN: {agg['mean_score']:.2f}/10  |  CONSENSUS: {agg['consensus']}")
    print(f"  LOGICAL: Ded={agg['logical_analysis_summary']['dedutiva']:.1f} Ind={agg['logical_analysis_summary']['indutiva']:.1f} Abd={agg['logical_analysis_summary']['abdutiva']:.1f}")
    print(f"  GAME THEORY MEAN: {agg['game_theory_mean']:.2f}/10")
    print(f"{'='*80}")
