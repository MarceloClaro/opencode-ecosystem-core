# -*- coding: utf-8 -*-
"""
MCP Lean Proof Server — SPEC-935-R747
Envolve motores existentes (R444/R445) com contrato fail-closed e anti-overclaim.
Sem rede. Reutiliza lean4_verifier, autoformalizer e egraph quando disponível.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Optional

from integrations.deepmind.lean4_verifier import Lean4ProofVerifier
from integrations.deepmind.autoformalizer import AutoFormalizerEngine

_VERIFIER = Lean4ProofVerifier()
_FORMALIZER = AutoFormalizerEngine(verifier=_VERIFIER)

_SORRY_RE = re.compile(r"\bsorry\b")
_ADMIT_RE = re.compile(r"\badmit\b")
_AXIOM_RE = re.compile(r"^\s*axiom\b", re.MULTILINE)


def _provenance() -> Dict[str, Any]:
    return {
        "has_compiler": bool(_VERIFIER.has_compiler),
        "lean_binary": _VERIFIER.lean_binary,
        "mathlib_version_hint": "Mathlib 4 (imports declarados no código)",
        "engine": "lean4_verifier R444 + autoformalizer R445 via R747",
    }


def lean_verify(code: str, project_dir: Optional[str] = None) -> Dict[str, Any]:
    """Verifica código Lean com fail-closed para sorry/admit/axiom não declarado. R754: project_dir usa lake-env."""
    if _SORRY_RE.search(code) or _ADMIT_RE.search(code):
        th = _VERIFIER.extract_theorem_name(code)
        tactics = _VERIFIER.extract_tactics(code)
        return {
            "is_valid": False,
            "status": "incomplete_sorry",
            "theorem_name": th,
            "tactics_used": tactics,
            "has_sorry": True,
            "errors": ["Bloqueio fail-closed: 'sorry' ou 'admit' detectado. Prova incompleta."],
            "output_log": "bloqueado_sorry_admit",
            "lean_source": code,
            "provenance": {**_provenance(), "project_dir": project_dir, "via": "lake-env" if project_dir else "bare-lean"},
        }
    if _AXIOM_RE.search(code):
        th = _VERIFIER.extract_theorem_name(code)
        tactics = _VERIFIER.extract_tactics(code)
        return {
            "is_valid": False,
            "status": "axiom_nao_declarado",
            "theorem_name": th,
            "tactics_used": tactics,
            "has_sorry": False,
            "errors": ["Bloqueio fail-closed: 'axiom' exige declaração explícita e auditoria."],
            "output_log": "bloqueado_axiom",
            "lean_source": code,
            "provenance": {**_provenance(), "project_dir": project_dir, "via": "lake-env" if project_dir else "bare-lean"},
        }
    res = _VERIFIER.verify_lean_code(code, project_dir=project_dir)
    d = res.to_dict()
    # Anti-overclaim: sem compilador real, nunca machine_checked.
    if not _VERIFIER.has_compiler and d.get("status") == "machine_checked":
        d["status"] = "syntax_verified"
        d["is_valid"] = True
        d["output_log"] = (d.get("output_log", "") + "\n[anti-overclaim R747: sem compilador, rebaixado para syntax_verified]").strip()
    d["provenance"] = {**_provenance(), "project_dir": project_dir, "via": "lake-env" if project_dir else "bare-lean"}
    return d


def lean_export(
    theorem_name: str,
    statement: str,
    tactics: List[str],
    imports: Optional[List[str]] = None,
    parameters: str = "",
) -> Dict[str, Any]:
    """Exporta teorema em Lean 4 com hash SHA-256 para custódia."""
    imports = imports or ["Mathlib.Tactic", "Mathlib.Data.Real.Basic"]
    src = _VERIFIER.format_theorem(
        theorem_name=theorem_name,
        statement=statement,
        proof_tactics=tactics,
        imports=imports,
        parameters=parameters,
    )
    return {
        "theorem_name": theorem_name,
        "lean_source": src,
        "sha256": hashlib.sha256(src.encode("utf-8")).hexdigest(),
        "imports": imports,
        "provenance": _provenance(),
    }


def lean_autoformalize(informal_text: str, domain: str = "algebra") -> Dict[str, Any]:
    """Autoformaliza texto informal para Lean 4 (R445) com chave lean_source."""
    out = _FORMALIZER.informal_to_lean4(informal_text=informal_text, domain=domain)
    lean_src = out.get("lean_code", "")
    out["lean_source"] = lean_src
    out["provenance"] = _provenance()
    return out


def lean_saturate(expr: str, rules: Optional[List[str]] = None) -> Dict[str, Any]:
    """Saturação E-Graph quando disponível; senão indisponível explícito."""
    try:
        from integrations.deepmind.egraph_rewriter import EqualitySaturationEngine
        eng = EqualitySaturationEngine()
        # API mínima: tenta simplificar se método existir, senão ecoa.
        simplify = getattr(eng, "simplify", None) or getattr(eng, "saturate", None)
        if callable(simplify):
            try:
                result = simplify(expr, rules or [])
            except TypeError:
                result = simplify(expr)
            return {"expr": expr, "result": str(result), "status": "saturado", "provenance": _provenance()}
        return {"expr": expr, "result": expr, "status": "motor_presente_sem_simplify", "provenance": _provenance()}
    except Exception as exc:  # fail-closed explícito
        return {"expr": expr, "result": expr, "status": "indisponivel", "error": str(exc), "provenance": _provenance()}
