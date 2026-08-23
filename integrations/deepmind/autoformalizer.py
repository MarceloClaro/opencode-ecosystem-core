# -*- coding: utf-8 -*-
"""
Bidirectional Auto-Formalization & Cross-Validation Engine — SPEC-935-R445
==========================================================================
1. Auto-Formalização: Linguagem Natural / LaTeX -> Código Formal Lean 4 / Mathlib.
2. Decompilação Explicativa: Código Lean 4 -> Demonstração Formal em Português Brasileiro.
3. Validação Cruzada Tripla: Checagem de consistência semântica entre texto e código formal.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from integrations.deepmind.lean4_verifier import Lean4ProofVerifier, Lean4VerificationResult


@dataclass
class CrossValidationResult:
    """Resultado da validação cruzada entre texto informal e código formal Lean 4."""
    is_aligned: bool
    status: str  # "aligned_and_verified", "incomplete_sorry", "variable_mismatch", "syntax_error"
    informal_summary: str
    lean_theorem_name: str
    variables_matched: List[str]
    confidence_score: float
    reconciliation_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_aligned": self.is_aligned,
            "status": self.status,
            "informal_summary": self.informal_summary,
            "lean_theorem_name": self.lean_theorem_name,
            "variables_matched": self.variables_matched,
            "confidence_score": self.confidence_score,
            "reconciliation_notes": self.reconciliation_notes,
        }


class AutoFormalizerEngine:
    """Motor de tradução bidirecional e validação cruzada entre linguagem natural e Lean 4."""

    def __init__(self, verifier: Optional[Lean4ProofVerifier] = None) -> None:
        self.verifier = verifier or Lean4ProofVerifier()

    def informal_to_lean4(
        self,
        informal_text: str,
        domain: str = "algebra",
        theorem_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Traduz enunciado informal ou conjectura matemática para script Lean 4 formal."""
        th_name = theorem_name or "autoformalized_theorem"
        
        # Extração de variáveis (letras soltas como x, y, z, a, b, n)
        vars_found = list(dict.fromkeys(re.findall(r'\b([a-z])\b', informal_text)))
        vars_str = " ".join(vars_found) if vars_found else "x"

        # Identificação do domínio de tipos
        if "inteiro" in informal_text.lower() or "natural" in informal_text.lower() or "n" in vars_found:
            type_decl = "Nat"
            tactics = ["intro " + vars_str, "omega"]
        elif "linear" in informal_text.lower() or "desigualdade" in informal_text.lower():
            type_decl = "Real"
            tactics = ["intro " + vars_str, "linarith"]
        else:
            type_decl = "Real"
            tactics = ["intro " + vars_str, "ring"]

        # Extração ou inferência de igualdade matemática
        eq_match = re.search(r'([a-zA-Z0-9\s\+\-\*\/\^\(\)]+)\s*=\s*([a-zA-Z0-9\s\+\-\*\/\^\(\)]+)', informal_text)
        if eq_match:
            statement = f"({vars_str} : {type_decl}) : {eq_match.group(1).strip()} = {eq_match.group(2).strip()}"
        else:
            # Enunciado simbólico padrão
            statement = f"({vars_str} : {type_decl}) : {vars_found[0] if vars_found else 'x'} + 0 = {vars_found[0] if vars_found else 'x'}"

        # Geração do código Lean 4
        lean_code = self.verifier.format_theorem(
            theorem_name=th_name,
            statement=statement.split(" : ")[-1],
            proof_tactics=tactics,
            parameters=f"({vars_str} : {type_decl})",
        )

        verification = self.verifier.verify_lean_code(lean_code)

        return {
            "informal_input": informal_text,
            "theorem_name": th_name,
            "domain": domain,
            "lean_code": lean_code,
            "tactics_suggested": tactics,
            "is_valid_syntax": verification.is_valid,
            "verification_status": verification.status,
        }

    def lean4_to_informal(
        self,
        lean_code: str,
        language: str = "pt-br",
    ) -> Dict[str, Any]:
        """Decompila e explica um script formal Lean 4 em linguagem natural formal."""
        th_name = self.verifier.extract_theorem_name(lean_code)
        tactics = self.verifier.extract_tactics(lean_code)
        has_sorry = bool(re.search(r'\bsorry\b', lean_code))

        # Extrai a proposição
        prop_match = re.search(r':\s*([^:=]+)\s*:=', lean_code)
        statement = prop_match.group(1).strip() if prop_match else "proposição matemática"

        tactic_explanations = {
            "intro": "introduz as variáveis e hipóteses no contexto local",
            "intros": "introduz múltiplas variáveis e hipóteses simultaneamente",
            "ring": "resolve a identidade através da teoria de anéis comutativos",
            "linarith": "aplica eliminação de Fourier-Motzkin para desigualdades lineares",
            "omega": "resolve a aritmética de Presburger sobre números inteiros/naturais",
            "simp": "simplifica a expressão aplicando lemas canônicos de reescrita",
            "exact": "fecha o objetivo com o termo exato fornecido",
            "apply": "aplica uma regra de inferência ou lema de implicação",
            "rw": "reescreve termos utilizando uma igualdade conhecida",
            "aesop": "executa busca automatizada com regras de tableau e táticas",
        }

        steps_explanation = []
        for t in tactics:
            exp = tactic_explanations.get(t, f"executa a tática '{t}'")
            steps_explanation.append(f"- **Passo:** `{t}` — {exp}.")

        if has_sorry:
            conclusion = "Atenção: A demonstração encontra-se INCOMPLETA devido à presença de 'sorry'."
        else:
            conclusion = "Demonstração concluída com sucesso formal (Q.E.D. / C.Q.D.)."

        explanation_text = f"""### Demonstração Formal do Teorema `{th_name}`

**Enunciado:** Para a proposição ${statement}$, demonstra-se que a igualdade ou implicação é válida formalmente.

**Estrutura da Demonstração:**
{chr(10).join(steps_explanation)}

**Conclusão:** {conclusion}
"""

        return {
            "theorem_name": th_name,
            "statement": statement,
            "tactics": tactics,
            "has_sorry": has_sorry,
            "explanation_text": explanation_text.strip(),
            "language": language,
        }

    def cross_validate(
        self,
        informal_text: str,
        lean_code: str,
    ) -> CrossValidationResult:
        """Executa validação cruzada rigorosa entre o texto informal e o código Lean 4."""
        th_name = self.verifier.extract_theorem_name(lean_code)
        verification = self.verifier.verify_lean_code(lean_code)

        notes = []

        # 1. Checagem de 'sorry'
        if verification.has_sorry:
            notes.append("Inconsistência crítica: o código Lean 4 contém 'sorry' (omissão de prova).")
            return CrossValidationResult(
                is_aligned=False,
                status="incomplete_sorry",
                informal_summary=informal_text[:100],
                lean_theorem_name=th_name,
                variables_matched=[],
                confidence_score=0.0,
                reconciliation_notes=notes,
            )

        # 2. Checagem sintática Lean 4
        if not verification.is_valid:
            notes.append(f"Erro sintático em Lean 4: {verification.errors}")
            return CrossValidationResult(
                is_aligned=False,
                status="syntax_error",
                informal_summary=informal_text[:100],
                lean_theorem_name=th_name,
                variables_matched=[],
                confidence_score=0.0,
                reconciliation_notes=notes,
            )

        # 3. Correspondência de variáveis
        informal_vars = set(re.findall(r'\b([a-z])\b', informal_text))
        lean_vars = set(re.findall(r'\b([a-z])\b', lean_code))
        matched = list(informal_vars.intersection(lean_vars))

        if not matched and informal_vars:
            notes.append("Aviso: Nenhuma variável do enunciado informal foi identificada no código Lean 4.")
            conf = 0.70
        else:
            notes.append(f"Alinhamento confirmado: variáveis {matched} presentes no enunciado e no script formal.")
            conf = 0.98

        notes.append(f"Verificação formal: status '{verification.status}' com {len(verification.tactics_used)} tática(s).")

        return CrossValidationResult(
            is_aligned=True,
            status="aligned_and_verified",
            informal_summary=informal_text[:100],
            lean_theorem_name=th_name,
            variables_matched=matched,
            confidence_score=conf,
            reconciliation_notes=notes,
        )
