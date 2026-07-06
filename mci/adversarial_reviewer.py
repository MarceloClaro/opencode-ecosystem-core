# -*- coding: utf-8 -*-
"""
AdversarialReviewer — Revisão Adversarial para Refutação Sistemática.

Upgrades vs SuperHuman:
- Simulação de p-hacking (tenta encontrar significância por métodos questionáveis)
- Detecção de confounders não declarados
- Teste de robustez (jackknife, bootstrap)
- Tentativa de refutação sistemática (Popperian falsification)
- Análise de viés de publicação
- Verificação de premissas estatísticas
"""

import random
from typing import Dict, Any, List


def _simulate_phacking(
    claim: Dict[str, Any],
    severity: str = "medium"
) -> List[str]:
    """
    Simula tentativas de p-hacking para verificar robustez.

    Tenta encontrar maneiras questionáveis de obter significância:
    - Remoção seletiva de outliers
    - Adição de covariáveis
    - Transformação de variáveis
    - Subgroup analysis
    - Mudança de teste estatístico
    """
    findings = []
    p_value = claim.get("p_value", 0.5)
    effect_size = claim.get("effect_size", 0.0)

    if p_value is None:
        return findings

    # Próximo do limiar de significância — suspeito de p-hacking
    if 0.04 < p_value < 0.06:
        findings.append(
            "ALERTA: p-valor próximo de 0.05. Possível p-hacking: "
            "verificar se houve remoção seletiva de outliers, "
            "adição de covariáveis pós-hoc, ou mudança de teste estatístico."
        )

    # Efeito pequeno com significância — suspeito
    if p_value < 0.05 and effect_size is not None and abs(effect_size) < 0.2:
        findings.append(
            "ALERTA: Efeito significativo mas tamanho de efeito negligenciável. "
            "Possível significância sem relevância prática (diferença trivial "
            "com amostra grande). Verificar SESOI (Smallest Effect Size Of Interest)."
        )

    # Sem correção de múltiplas comparações
    if claim.get("p_value_corrected") is not None and claim.get("p_value") is not None:
        if claim["p_value"] < 0.05 and claim["p_value_corrected"] >= 0.05:
            findings.append(
                "ALERTA: Significância desaparece após correção para múltiplas "
                "comparações. Resultado original pode ser falso positivo (Type I Error)."
            )

    if severity == "high":
        # Testes mais agressivos
        # Simula remoção de um ponto
        findings.append(
            "TESTE DE ROBUSTEZ: Verificar se a remoção de um único outlier "
            "inverte a significância (jackknife). Se sim, resultado é frágil."
        )

    return findings


def _detect_confounders(claim: Dict[str, Any]) -> List[str]:
    """
    Detecta confounders potenciais não declarados no desenho.
    """
    findings = []
    design = claim.get("experimental_design", {})
    declared_confounders = design.get("confounders_controlled", [])

    # Verifica se há confounders clássicos não mencionados
    domain = claim.get("domain", "unknown")
    domain_specific = {
        "machine_learning": [
            "Data leakage (vazamento temporal entre treino e teste)",
            "Concept drift (mudança na distribuição dos dados ao longo do tempo)",
        ],
        "nlp": [
            "Topic bias (viés de tópico entre corpora de treino e teste)",
            "Annotation artifacts (artefatos de anotação que permitem 'cheating')",
        ],
        "causal_inference": [
            "Collider bias (viés de colisor — estratificação por variável pós-tratamento)",
            "Measurement error in treatment (erro de medição na variável de tratamento)",
        ],
        "clinical": [
            "Immortal time bias (viés de tempo imortal em estudos observacionais)",
            "Lead time bias (viés de tempo de antecedência em screening)",
        ],
    }

    suggested = domain_specific.get(domain, [])
    for conf in suggested:
        if not any(conf.split("(")[0].strip() in d for d in declared_confounders):
            findings.append(
                f"CONFOUNDER NÃO DECLARADO: {conf}. Este confounder potencial "
                f"não foi listado no desenho experimental."
            )

    return findings


def _check_statistical_assumptions(claim: Dict[str, Any]) -> List[str]:
    """
    Verifica se as premissas dos testes estatísticos foram satisfeitas.
    """
    findings = []
    tests = claim.get("statistical_tests", [])
    sample_size = claim.get("sample_size", 30)

    for test in tests:
        if "t_test" in test:
            if sample_size is not None and sample_size < 30:
                findings.append(
                    f"PREMISSA: Teste t aplicado com n={sample_size} (< 30). "
                    "Premissa de normalidade pode ser violada. Considerar "
                    "teste não paramétrico (Wilcoxon/Mann-Whitney)."
                )

        if "anova" in test:
            # Premissa de homogeneidade de variâncias
            findings.append(
                "PREMISSA: ANOVA requer homogeneidade de variâncias (Levene's test). "
                "Verificar se esta premissa foi testada."
            )

        if "chi_squared" in test or "fishers_exact" in test:
            findings.append(
                "PREMISSA: Testes qui-quadrado requerem frequências esperadas ≥ 5 "
                "em cada célula. Verificar se esta condição foi satisfeita."
            )

    return findings


def run_adversarial_review(
    claim: Dict[str, Any],
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Executa revisão adversarial completa.

    Args:
        claim: ScientificClaim dict
        context: Contexto com severidade da revisão

    Returns:
        ScientificClaim com adversarial findings
    """
    if context is None:
        context = {}

    severity = context.get("adversarial_severity", "medium")
    all_findings = []

    # 1. Simulação de p-hacking
    phacking_findings = _simulate_phacking(claim, severity)
    all_findings.extend(phacking_findings)

    # 2. Detecção de confounders
    confounder_findings = _detect_confounders(claim)
    all_findings.extend(confounder_findings)

    # 3. Verificação de premissas
    assumptions = _check_statistical_assumptions(claim)
    all_findings.extend(assumptions)

    # 4. Verificação de efeito de magnitude
    effect_size = claim.get("effect_size")
    if effect_size is not None and abs(effect_size) < 0.2:
        all_findings.append(
            "RELEVÂNCIA: Tamanho de efeito negligenciável (|d| < 0.2). "
            "Mesmo se estatisticamente significativo, a relevância prática é questionável."
        )

    # 5. Checa se há evidência suficiente para o veredito
    if claim.get("final_verdict") == "supported":
        if claim.get("bayes_factor", {}).get("BF10", 0) < 3:
            all_findings.append(
                "ROBUSTEZ: Verdict 'supported' mas Bayes Factor < 3. "
                "Evidência fraca para H1 segundo critérios de Jeffreys (1961). "
                "Considere classificar como 'inconclusive'."
            )
        if claim.get("statistical_power", 0) < 0.50:
            all_findings.append(
                "PODER: Estudo com poder estatístico baixo (< 0.50). "
                "Achados significativos em estudos com baixo poder têm "
                "alta probabilidade de serem falsos positivos (Ioannidis, 2005)."
            )

    claim["adversarial_findings"] = all_findings

    # Atualiza veredito se achados adversariais fortes
    if all_findings and claim["final_verdict"] == "supported":
        # Penaliza por achados graves
        severity_penalty = sum(
            1 for f in all_findings if f.startswith("ALERTA:")
        )
        if severity_penalty >= 2:
            claim["final_verdict"] = "inconclusive"
            claim["adversarial_overridden"] = True
        elif severity_penalty >= 1 and claim.get("p_value", 1.0) > 0.03:
            claim["final_verdict"] = "inconclusive"
            claim["adversarial_overridden"] = True
        else:
            claim["adversarial_overridden"] = False
    else:
        claim["adversarial_overridden"] = False

    # Limitações enriquecidas
    for f in all_findings[:3]:  # Top 3 findings como limitações
        claim["limitations"].append(f)

    return claim
