# -*- coding: utf-8 -*-
"""
HypothesisEngine — Geração de Hipóteses Científicas Falsificáveis.

Upgrades vs SuperHuman:
- Hipóteses falsificáveis (Popper)
- Prior Bayesiano configurável
- Previsão de direção e magnitude do efeito
- Hipótese nula explícita com justificativa
- Domínio científico detectado automaticamente
"""

import uuid
from typing import Dict, Any, List, Optional


# Domínios científicos com métricas e testes padrão
SCIENTIFIC_DOMAINS = {
    "machine_learning": {
        "metrics": ["Accuracy", "F1-score", "AUROC", "Precision", "Recall"],
        "statistical_tests": ["paired_t_test", "wilcoxon", "mcnemar"],
        "effect_size_convention": "cohens_d",
        "default_alpha": 0.05,
    },
    "nlp": {
        "metrics": ["BLEU", "ROUGE-L", "Perplexity", "BERTScore"],
        "statistical_tests": ["paired_t_test", "bootstrap_test"],
        "effect_size_convention": "cohens_d",
        "default_alpha": 0.05,
    },
    "causal_inference": {
        "metrics": ["ATE", "ATT", "CATE", "ATE_confidence"],
        "statistical_tests": ["t_test", "wald_test", "bootstrap_ci"],
        "effect_size_convention": "cohens_d",
        "default_alpha": 0.05,
    },
    "clinical": {
        "metrics": ["AUC-ROC", "Sensitivity", "Specificity", "PPV", "NPV"],
        "statistical_tests": ["chi_squared", "fishers_exact", "logistic_regression"],
        "effect_size_convention": "odds_ratio",
        "default_alpha": 0.05,
    },
    "social_science": {
        "metrics": ["Cohen_d", "eta_squared", "R2", "RMSE"],
        "statistical_tests": ["anova", "t_test", "mann_whitney"],
        "effect_size_convention": "cohens_d",
        "default_alpha": 0.05,
    },
    "engineering": {
        "metrics": ["Latency", "Throughput", "Error_rate", "Resource_usage"],
        "statistical_tests": ["paired_t_test", "bootstrap"],
        "effect_size_convention": "cohens_d",
        "default_alpha": 0.05,
    },
}


def _detect_domain(question: str, context: Dict[str, Any]) -> str:
    """Detecta o domínio científico da pergunta."""
    domain = context.get("domain", "")
    if domain and domain in SCIENTIFIC_DOMAINS:
        return domain

    q = question.lower()
    # Heurísticas de detecção
    if any(w in q for w in ["machine learning", "classificação", "predição", "accuracy", "f1", "modelo"]):
        return "machine_learning"
    if any(w in q for w in ["nlp", "linguagem", "texto", "tradução", "sumarização"]):
        return "nlp"
    if any(w in q for w in ["causal", "causa efeito", "inferência causal", "ate estimativa", "viés de seleção"]):
        return "causal_inference"
    if any(w in q for w in ["clínico", "paciente", "diagnóstico", "doença", "tratamento clínico", "tratamento médico", "sobrevida", "tratamento", "medicamento"]):
        return "clinical"
    if any(w in q for w in ["social", "comportamento", "educação", "psicológico", "survey"]):
        return "social_science"
    if any(w in q for w in ["latência", "throughput", "performance", "engenharia", "sistema"]):
        return "engineering"

    return "machine_learning"  # default


def _parse_effect_direction(question: str) -> str:
    """Determina a direção esperada do efeito."""
    q = question.lower()
    if any(w in q for w in ["aumenta", "melhora", "acelera", "aumento", "positivo", "mais"]):
        return "positive"
    if any(w in q for w in ["reduz", "diminui", "menos", "negativo", "piora", "diminuição"]):
        return "negative"
    return "two_sided"


def generate_hypothesis(
    question: str,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Gera hipóteses científicas falsificáveis a partir de uma pergunta.

    Args:
        question: Pergunta de pesquisa (ex: "A intervenção X reduz erro?")
        context: Contexto com domínio, métricas, priors, etc.

    Returns:
        Dict com ScientificClaim completo (hipóteses + design + metadados)
    """
    if context is None:
        context = {}

    clean_q = question.strip()
    if clean_q.endswith("?"):
        clean_q = clean_q[:-1]

    domain = _detect_domain(question, context)
    domain_config = SCIENTIFIC_DOMAINS.get(domain, SCIENTIFIC_DOMAINS["machine_learning"])
    effect_direction = _parse_effect_direction(question)

    # Constrói hipóteses com direção explícita
    if effect_direction == "positive":
        h1 = f"H1: {clean_q} produz um aumento estatisticamente significativo e positivo."
        h0 = f"H0: {clean_q} não produz alteração ou produz efeito nulo."
    elif effect_direction == "negative":
        h1 = f"H1: {clean_q} produz uma redução estatisticamente significativa."
        h0 = f"H0: {clean_q} não produz redução estatisticamente significativa."
    else:
        h1 = f"H1: {clean_q} produz um efeito estatisticamente significativo (bidirecional)."
        h0 = f"H0: {clean_q} não possui efeito estatisticamente significativo (efeito nulo)."

    # Prior Bayesiano (default: levemente cético)
    bayesian_prior = context.get("bayesian_prior", 0.3)

    # Tamanho de efeito mínimo detectável (SESOI — Smallest Effect Size Of Interest)
    sesoi = context.get("sesoi", 0.2)

    return {
        "claim_id": f"clm-{uuid.uuid4().hex[:8]}",
        "hypothesis": h1,
        "null_hypothesis": h0,
        "effect_direction": effect_direction,
        "domain": domain,
        "bayesian_prior": bayesian_prior,
        "sesoi": sesoi,
        "falsifiable": True,
        "experimental_design": {
            "type": context.get("design_type", "randomized_control_trial"),
            "sample_strategy": context.get("sample_strategy", "stratified_random_sampling"),
            "stop_criteria": context.get("stop_criteria", "minimum_sample_size_and_power_0.8"),
            "power_level": context.get("power_level", 0.80),
            "alpha": context.get("alpha", domain_config["default_alpha"]),
            "effect_size_convention": domain_config["effect_size_convention"],
        },
        "dataset_refs": context.get("dataset_refs", ["dataset_default_v1"]),
        "metrics": context.get("metrics", domain_config["metrics"]),
        "statistical_tests": context.get("statistical_tests", domain_config["statistical_tests"]),
        "effect_size": None,
        "confidence_interval": None,
        "p_value": None,
        "bayes_factor": None,
        "limitations": [
            "Os dados experimentais estão sujeitos a ruído de medição.",
            "A inferência causal depende da validade das premissas de identificação.",
            "Generalização limitada pela população amostrada.",
        ],
        "reproducibility_score": 0.0,
        "calibrated_confidence": 0.0,
        "adversarial_findings": [],
        "final_verdict": "inconclusive",
        "version": "2.0.0",
    }
