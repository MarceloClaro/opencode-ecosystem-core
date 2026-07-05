# -*- coding: utf-8 -*-
from typing import Dict, Any

def build_report(claim: Dict[str, Any], context: Dict[str, Any]) -> str:
    adv_findings = claim.get("adversarial_findings", [])
    findings_str = "\n".join([f"- {x}" for x in adv_findings]) if adv_findings else "- none"
    
    return rf"""
\section*{{Scientific Claim Report}}
\textbf{{Claim ID}}: {claim["claim_id"]}

\subsection*{{Hypotheses}}
H1: {claim["hypothesis"]}

H0: {claim["null_hypothesis"]}

\subsection*{{Design}}
Type: {claim["experimental_design"]["type"]}

Sampling: {claim["experimental_design"]["sample_strategy"]}

Stop criteria: {claim["experimental_design"]["stop_criteria"]}

\subsection*{{Results}}
p-value: {claim.get("p_value")}

Effect size: {claim.get("effect_size")}

Confidence interval: {claim.get("confidence_interval")}

Calibrated confidence: {claim.get("calibrated_confidence")}

Reproducibility score: {claim.get("reproducibility_score")}

\subsection*{{Adversarial Findings}}
{findings_str}

\subsection*{{Verdict}}
{claim["final_verdict"]}
"""
