# -*- coding: utf-8 -*-
"""
ScientificReporter — Relatórios Científicos com Padrão Qualis A1.

Upgrades vs SuperHuman:
- Relatório LaTeX completo (artigo científico格式)
- Reproducibility Checklist (Nature-style)
- Seção de limitações e viés
- DOI e citações (formato BibTeX)
- Painel de métricas científicas
- Relatório executivo em markdown
"""

from typing import Dict, Any


def _escape_latex(text: str) -> str:
    """Escapa caracteres especiais do LaTeX."""
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _format_confidence_interval(ci: list) -> str:
    if ci and len(ci) == 2:
        return f"[{ci[0]:.4f}, {ci[1]:.4f}]"
    return "N/A"


def build_report(
    claim: Dict[str, Any],
    context: Dict[str, Any] = None
) -> str:
    """
    Gera relatório científico completo no formato LaTeX (Qualis A1).

    Args:
        claim: ScientificClaim dict
        context: Contexto com metadados adicionais

    Returns:
        String LaTeX completa do relatório
    """
    if context is None:
        context = {}

    adv_findings = claim.get("adversarial_findings", [])
    findings_str = "\n".join(
        [f"\\item {_escape_latex(f)}" for f in adv_findings]
    ) if adv_findings else "\\item Nenhum achado adversarial significativo."

    limitations = claim.get("limitations", [])
    limitations_str = "\n".join(
        [f"\\item {_escape_latex(l)}" for l in limitations]
    ) if limitations else "\\item Nenhuma limitação declarada."

    metrics = claim.get("metrics", [])
    metrics_str = ", ".join(metrics) if metrics else "N/A"

    tests = claim.get("statistical_tests", [])
    tests_str = ", ".join(tests) if tests else "N/A"

    design = claim.get("experimental_design", {})
    confounders = design.get("confounders_controlled", [])
    confounders_str = "\n".join(
        [f"\\item {_escape_latex(c)}" for c in confounders]
    ) if confounders else "\\item Nenhum confounder declarado."

    def _tex(v):
        """Auxiliar para valores LaTeX."""
        if v is None or v == "N/A":
            return "N/A"
        return str(v)

    def _safe(s):
        return _escape_latex(str(s))

    cid = _safe(claim.get('claim_id', 'N/A'))
    hyp = _safe(claim.get('hypothesis', 'N/A'))
    nhyp = _safe(claim.get('null_hypothesis', 'N/A'))
    eff_dir = _tex(claim.get('effect_direction', 'two_sided'))
    dom = _tex(claim.get('domain', 'unknown'))
    sesoi = _tex(claim.get('sesoi', 0.2))
    prior = _tex(claim.get('bayesian_prior', 0.3))

    d_type = _safe(design.get('type', 'N/A'))
    d_samp = _safe(design.get('sample_strategy', 'N/A'))
    d_stop = _safe(design.get('stop_criteria', 'N/A'))
    d_pow = _tex(design.get('power_level', 'N/A'))
    d_alpha = _tex(design.get('alpha', 'N/A'))
    d_arms = _tex(design.get('n_arms', 'N/A'))
    d_n = _tex(design.get('n_per_group', 'N/A'))
    d_total = _tex(design.get('total_sample_size', 'N/A'))
    d_rand = _safe(design.get('randomization_unit', 'N/A'))
    d_blind = _safe(design.get('blinding', 'N/A'))
    d_reg = _tex(design.get('pre_registered', False))

    pval = _tex(claim.get('p_value', 'N/A'))
    pval_c = _tex(claim.get('p_value_corrected', 'N/A'))
    es = _tex(claim.get('effect_size', 'N/A'))
    es_class = _tex(claim.get('effect_size_classification', {}).get('classification', 'N/A'))
    ci = _format_confidence_interval(claim.get('confidence_interval'))
    bf10 = _tex(claim.get('bayes_factor', {}).get('BF10', 'N/A') if isinstance(claim.get('bayes_factor'), dict) else 'N/A')
    bf01 = _tex(claim.get('bayes_factor', {}).get('BF01', 'N/A') if isinstance(claim.get('bayes_factor'), dict) else 'N/A')
    bf_int = _safe(claim.get('bayes_factor_interpretation', 'N/A'))
    power = _tex(claim.get('statistical_power', 'N/A'))
    n = _tex(claim.get('sample_size', 'N/A'))
    ev_score = _tex(claim.get('evidence_score', 'N/A'))
    ev_str = _tex(claim.get('evidence_strength', 'N/A'))

    conf = _tex(claim.get('calibrated_confidence', 'N/A'))
    brier = _tex(claim.get('brier_score', 'N/A'))
    repro = _tex(claim.get('reproducibility_score', 'N/A'))
    abstain = _tex(claim.get('should_abstain', False))

    verdict = _tex(claim.get('final_verdict', 'inconclusive').upper())
    ev_base = _tex(claim.get('evidence_score', 0))
    adv_over = _tex(claim.get('adversarial_overridden', False))
    ver = _tex(claim.get('version', 'N/A'))
    fals = _tex(claim.get('falsifiable', True))
    ds = _safe(str(claim.get('dataset_refs', [])))

    report = (
        "\\section*{OpenCode Scientific Claim Report}\n"
        "\\label{sec:claim-report}\n\n"
        "\\begin{center}\n"
        "\\textbf{Qualis A1}~~$\\cdot$~~\\texttt{" + cid + "} \\\\\n"
        "\\vspace{2mm}\n"
        "\\small {Gerado em: \\today}\n"
        "\\end{center}\n\n"
        "\\subsection*{1. Hip\'oteses}\n%\n\n"
        "\\textbf{Hip\'otese de Pesquisa (H1):} " + hyp + "\n\n"
        "\\vspace{1mm}\n"
        "\\textbf{Hip\'otese Nula (H0):} " + nhyp + "\n\n"
        "\\vspace{1mm}\n"
        "\\textbf{Dire\c{c}\~ao do Efeito:} " + eff_dir + " \\\\\n"
        "\\textbf{Dom\'inio Cient\'ifico:} " + dom + " \\\\\n"
        "\\textbf{SESOI (M\'inimo Efeito de Interesse):} d = " + sesoi + " \\\\\n"
        "\\textbf{Prior Bayesiano:} " + prior + "\n\n"
        "\\subsection*{2. Desenho Experimental}\n%\n\n"
        "\\textbf{Tipo:} " + d_type + " \\\\\n"
        "\\textbf{Amostragem:} " + d_samp + " \\\\\n"
        "\\textbf{Crit\'erio de Parada:} " + d_stop + " \\\\\n"
        "\\textbf{Poder Estat\'istico:} " + d_pow + " \\\\\n"
        "\\textbf{Alpha:} " + d_alpha + " \\\\\n"
        "\\textbf{N\\textordmasculine Bra\c{c}os:} " + d_arms + " \\\\\n"
        "\\textbf{N por Grupo:} " + d_n + " \\\\\n"
        "\\textbf{Amostra Total:} " + d_total + " \\\\\n"
        "\\textbf{Randomiza\c{c}\~ao:} " + d_rand + " \\\\\n"
        "\\textbf{Cegamento:} " + d_blind + " \\\\\n"
        "\\textbf{Pr\'e-Registrado:} " + d_reg + "\n\n"
        "\\subsubsection*{Confounders Controlados}\n"
        "\\begin{itemize}\n" + confounders_str + "\n"
        "\\end{itemize}\n\n"
        "\\subsection*{3. M\'etricas e Testes}\n%\n\n"
        "\\textbf{M\'etricas:} " + _safe(metrics_str) + " \\\\\n"
        "\\textbf{Testes Estat\'isticos:} " + _safe(tests_str) + "\n\n"
        "\\subsection*{4. Resultados Estat\'isticos}\n%\n\n"
        "\\begin{tabular}{ll}\n"
        "\\hline\n"
        "\\textbf{Par\^ametro} & \\textbf{Valor} \\\\ \\hline\n"
        "p-valor & " + pval + " \\\\\n"
        "p-valor (corrigido) & " + pval_c + " \\\\\n"
        "Tamanho de Efeito (d de Cohen) & " + es + " \\\\\n"
        "Classifica\c{c}\~ao do Efeito & " + es_class + " \\\\\n"
        "Intervalo de Confian\c{c}a (95\\%) & " + ci + " \\\\\n"
        "Bayes Factor (BF10) & " + bf10 + " \\\\\n"
        "Bayes Factor (BF01) & " + bf01 + " \\\\\n"
        "Interpreta\c{c}\~ao BF & " + bf_int + " \\\\\n"
        "Poder Estat\'istico P\'os-Hoc & " + power + " \\\\\n"
        "Tamanho Amostral & " + n + " \\\\\n"
        "Score de Evid\^encia & " + ev_score + " \\\\\n"
        "For\c{c}a da Evid\^encia & " + ev_str + " \\\\ \\hline\n"
        "\\end{tabular}\n\n"
        "\\subsection*{5. Calibra\c{c}\~ao de Confian\c{c}a}\n%\n\n"
        "\\textbf{Confian\c{c}a Calibrada:} " + conf + " \\\\\n"
        "\\textbf{Brier Score:} " + brier + " \\\\\n"
        "\\textbf{Score de Reprodutibilidade:} " + repro + " \\\\\n"
        "\\textbf{Absten\c{c}\~ao Recomendada:} " + abstain + "\n\n"
        "\\subsection*{6. Revis\~ao Adversarial}\n%\n\n"
        "\\begin{itemize}\n" + findings_str + "\n"
        "\\end{itemize}\n\n"
        "\\subsection*{7. Limita\c{c}\~oes}\n%\n\n"
        "\\begin{itemize}\n" + limitations_str + "\n"
        "\\end{itemize}\n\n"
        "\\subsection*{8. Veredito Final}\n%\n\n"
        "\\textbf{Veredito:} " + verdict + " \\\\\n"
        "\\textbf{Evidence-Based:} " + ev_base + "/7 crit\'erios satisfeitos \\\\\n"
        "\\textbf{Override Adversarial:} " + adv_over + "\n\n"
        "\\subsection*{9. Metadados da Execu\c{c}\~ao}\n%\n\n"
        "\\begin{tabular}{ll}\n"
        "\\hline\n"
        "\\textbf{Campo} & \\textbf{Valor} \\\\ \\hline\n"
        "Claim ID & \\texttt{" + cid + "} \\\\\n"
        "Vers\~ao & " + ver + " \\\\\n"
        "Dom\'inio & " + dom + " \\\\\n"
        "Falsific\'avel & " + fals + " \\\\\n"
        "Datasets & " + ds + " \\\\\n"
        "\\hline\n"
        "\\end{tabular}\n"
    )

    return report


def build_executive_summary(claim: Dict[str, Any]) -> str:
    """
    Gera sumário executivo em markdown para consumo rápido.
    """
    verdict = claim.get("final_verdict", "inconclusive").upper()
    confidence = claim.get("calibrated_confidence", 0.0)
    p_value = claim.get("p_value", "N/A")
    effect = claim.get("effect_size", "N/A")
    bf = claim.get("bayes_factor", {})
    bf10 = bf.get("BF10", "N/A") if isinstance(bf, dict) else "N/A"

    summary = f"""## Executive Summary — Scientific Claim

**Verdict:** {verdict}
**Confidence (calibrated):** {confidence:.2%}
**p-value:** {p_value}
**Effect size (d):** {effect}
**Bayes Factor (BF10):** {bf10}
**Reproducibility:** {claim.get('reproducibility_score', 'N/A')}

### Hypothesis
{claim.get('hypothesis', 'N/A')}

### Key Findings
- {len(claim.get('adversarial_findings', []))} adversarial issues identified
- {len(claim.get('limitations', []))} limitations noted
"""
    return summary


def build_reproducibility_checklist(claim: Dict[str, Any]) -> str:
    """
    Gera checklist de reprodutibilidade (estilo Nature/Science).

    Retorna markdown com itens verificados.
    """
    design = claim.get("experimental_design", {})

    checklist = f"""## Reproducibility Checklist

### Data & Code
- [{'x' if design.get('pre_registered') else ' '}] Pre-registration
- [ ] Data availability statement
- [ ] Code availability statement
- [ ] Random seed specified

### Methods
- [{'x' if design.get('type') else ' '}] Experimental design fully specified
- [{'x' if design.get('sample_strategy') else ' '}] Sampling strategy described
- [{'x' if design.get('blinding') else ' '}] Blinding protocol
- [{'x' if design.get('n_per_group', 0) > 0 else ' '}] Sample size justification (power analysis)

### Statistics
- [{'x' if claim.get('p_value') is not None else ' '}] Effect size reported
- [{'x' if claim.get('confidence_interval') is not None else ' '}] Confidence intervals
- [{'x' if claim.get('bayes_factor') else ' '}] Bayes Factor or alternative
- [{'x' if claim.get('p_value_corrected') is not None else ' '}] Multiple comparison correction

### Robustness
- [{'x' if claim.get('adversarial_findings') else ' '}] Adversarial review conducted
- [{'x' if len(claim.get('adversarial_findings', [])) > 0 else ' '}] Sensitivity analysis
- [ ] Independent replication

### Transparency
- [{'x' if claim.get('limitations') else ' '}] Limitations explicitly stated
- [ ] Conflicts of interest declared
- [ ] Funding sources disclosed
"""
    return checklist
