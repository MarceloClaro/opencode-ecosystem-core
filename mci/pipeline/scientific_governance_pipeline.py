# -*- coding: utf-8 -*-
from typing import Dict, Any, Callable
from mci.oqs import run_oqs_scanner
from mci.orchestration import run_scientific_cycle
from mci.vsee import run_vsee_router
from mci.egs import run_egs_scanner

def run_scientific_governance_pipeline(problem_text: str, executor_fn: Callable, context: Dict[str, Any] = None) -> Dict[str, Any]:
    if context is None:
        context = {}
        
    # 1. OQS Stage
    oqs_res = run_oqs_scanner(problem_text, context)
    selected_question = oqs_res["selected_question"]
    
    # 2. MCI Scientific Core Stage
    scientific_res = run_scientific_cycle(selected_question, context)
    claim = scientific_res.claim
    report_tex = scientific_res.report_tex
    
    # 3. VSEE Stage
    vsee_res = run_vsee_router(executor_fn, context)
    
    # 4. EGS Stage
    check_content = f"{claim.get('hypothesis', '')} {vsee_res.get('result_data', {}).get('data', '')}"
    egs_res = run_egs_scanner(check_content, context)
    
    pipeline_success = oqs_res["pass"] and egs_res["decision"] != "block"
    
    return {
        "problem_id": oqs_res["problem_id"],
        "oqs": oqs_res,
        "scientific_claim": claim,
        "report_tex": report_tex,
        "vsee": vsee_res,
        "egs": egs_res,
        "pipeline_success": pipeline_success,
        "status": "blocked" if egs_res["decision"] == "block" else "success" if pipeline_success else "failed",
        "version": "1.0.0"
    }
