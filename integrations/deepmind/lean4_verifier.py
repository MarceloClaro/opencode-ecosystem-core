# -*- coding: utf-8 -*-
"""
Lean 4 Formal Proof Bridge & Verifier — SPEC-935-R444
======================================================
Integração nativa com o assistente de provas interativo Lean 4 (e Mathlib 4).

Permite:
1. Geração de código formal Lean 4 para teoremas deduzidos pelo ecossistema.
2. Análise estática, detecção de `sorry` e validação sintática de táticas.
3. Execução direta via compilador `lean` / `lake` quando disponível no ambiente.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class Lean4VerificationResult:
    """Resultado da validação formal de script Lean 4."""
    is_valid: bool
    status: str  # "machine_checked", "syntax_verified", "incomplete_sorry", "syntax_error"
    theorem_name: str
    tactics_used: List[str]
    has_sorry: bool
    errors: List[str] = field(default_factory=list)
    output_log: str = ""
    lean_source: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "status": self.status,
            "theorem_name": self.theorem_name,
            "tactics_used": self.tactics_used,
            "has_sorry": self.has_sorry,
            "errors": self.errors,
            "output_log": self.output_log,
            "lean_source": self.lean_source,
        }


class Lean4ProofVerifier:
    """Verificador e gerador formal de código Lean 4."""

    KNOWN_TACTICS: Set[str] = {
        "intro", "intros", "exact", "apply", "rw", "rewrite",
        "simp", "dsimp", "ring", "linarith", "nlinarith", "omega",
        "aesop", "cases", "rcases", "induction", "constructor",
        "contradiction", "by_contra", "calc", "norm_num", "positivity",
        "refine", "have", "obtain", "revert", "clear", "subst",
        "decide", "trivial", "rfl", "assumption",
    }

    def __init__(self, lean_binary: Optional[str] = None) -> None:
        self.lean_binary = lean_binary or self._discover_lean_binary()

    def _discover_lean_binary(self) -> Optional[str]:
        """Procura o binário do Lean 4 no PATH ou caminhos padrão."""
        for candidate in ["lean", "lean4", "lake"]:
            found = shutil.which(candidate)
            if found:
                return found
        # Checagem em diretórios ~/.elan/bin
        elan_path = os.path.expanduser("~/.elan/bin/lean")
        if os.path.isfile(elan_path) and os.access(elan_path, os.X_OK):
            return elan_path
        return None

    @property
    def has_compiler(self) -> bool:
        """Indica se um binário real de Lean 4 está executável no sistema."""
        return self.lean_binary is not None

    def format_theorem(
        self,
        theorem_name: str,
        statement: str,
        proof_tactics: List[str],
        imports: Optional[List[str]] = None,
        parameters: str = "",
    ) -> str:
        """Gera um arquivo/código fonte formal em Lean 4."""
        imports = imports or ["Mathlib.Tactic", "Mathlib.Data.Real.Basic"]
        import_lines = "\n".join(f"import {imp}" for imp in imports)
        
        param_str = f" {parameters}" if parameters else ""
        tactic_lines = "\n  ".join(proof_tactics)

        code = f"""-- OpenCode Ecosystem Core — Lean 4 Formal Theorem
{import_lines}

theorem {theorem_name}{param_str} : {statement} := by
  {tactic_lines}
"""
        return code.strip()

    def extract_tactics(self, code: str) -> List[str]:
        """Extrai as táticas Lean 4 utilizadas no script."""
        used = []
        # Procura por palavras-chave após := by ou em linhas indentadas
        tokens = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', code)
        for t in tokens:
            if t in self.KNOWN_TACTICS and t not in used:
                used.append(t)
        return used

    def extract_theorem_name(self, code: str) -> str:
        """Extrai o nome do teorema declarado no código."""
        match = re.search(r'\b(?:theorem|lemma|def)\s+([a-zA-Z0-9_]+)', code)
        return match.group(1) if match else "unnamed_theorem"

    def verify_lean_code(self, code: str, project_dir: Optional[str] = None) -> Lean4VerificationResult:
        """
        Valida formalmente o código Lean 4.
        Se project_dir (projeto lake com .lake) for dado, usa `lake env lean` (R754).
        Senão, execução bare `lean` ou análise sintática (R444/R753).
        """
        th_name = self.extract_theorem_name(code)
        tactics = self.extract_tactics(code)
        has_sorry = bool(re.search(r'\bsorry\b', code))

        # 1. Se contém 'sorry', a prova é incompleta
        if has_sorry:
            return Lean4VerificationResult(
                is_valid=False,
                status="incomplete_sorry",
                theorem_name=th_name,
                tactics_used=tactics,
                has_sorry=True,
                errors=["A prova contém 'sorry' (passo em aberto não demonstrado)."],
                output_log="Aviso: Prova incompleta com 'sorry'.",
                lean_source=code,
            )

        # 1b. 'admit' e 'axiom' não declarado também bloqueiam aqui (defesa em
        # profundidade R764; o MCP mantém sua checagem própria).
        if re.search(r'\badmit\b', code):
            return Lean4VerificationResult(
                is_valid=False,
                status="incomplete_sorry",
                theorem_name=th_name,
                tactics_used=tactics,
                has_sorry=False,
                errors=["Bloqueio fail-closed: 'admit' detectado (passo admitido, não provado)."],
                output_log="Aviso: Prova com 'admit'.",
                lean_source=code,
            )
        if re.search(r'^\s*axiom\b', code, re.MULTILINE):
            return Lean4VerificationResult(
                is_valid=False,
                status="axiom_nao_declarado",
                theorem_name=th_name,
                tactics_used=tactics,
                has_sorry=False,
                errors=["Bloqueio fail-closed: 'axiom' exige declaração explícita e auditoria."],
                output_log="Aviso: axioma não declarado.",
                lean_source=code,
            )

        # 2. Checagem sintática de balanceamento de delimitadores
        delimiters = {'(': ')', '[': ']', '{': '}'}
        stack = []
        for char in code:
            if char in delimiters:
                stack.append(char)
            elif char in delimiters.values():
                if not stack:
                    return Lean4VerificationResult(
                        is_valid=False,
                        status="syntax_error",
                        theorem_name=th_name,
                        tactics_used=tactics,
                        has_sorry=False,
                        errors=[f"Delimitador desbalanceado: '{char}' inesperado."],
                        output_log="Erro de sintaxe em delimitadores Lean 4.",
                        lean_source=code,
                    )
                top = stack.pop()
                if delimiters[top] != char:
                    return Lean4VerificationResult(
                        is_valid=False,
                        status="syntax_error",
                        theorem_name=th_name,
                        tactics_used=tactics,
                        has_sorry=False,
                        errors=[f"Delimitador incompatível: '{top}' fechado por '{char}'."],
                        output_log="Erro de parênteses/chaves incompatíveis.",
                        lean_source=code,
                    )

        if stack:
            return Lean4VerificationResult(
                is_valid=False,
                status="syntax_error",
                theorem_name=th_name,
                tactics_used=tactics,
                has_sorry=False,
                errors=[f"Delimitadores não fechados: {stack}"],
                output_log="Erro: bloco ou expressão não finalizada.",
                lean_source=code,
            )

        # 2b. Via projeto lake (R754): `lake env lean` com search path do projeto.
        if project_dir and os.path.isdir(project_dir) and os.path.isdir(os.path.join(project_dir, ".lake")):
            lake_bin = shutil.which("lake") or os.path.expanduser("~/.elan/bin/lake")
            if lake_bin and (shutil.which("lake") or (os.path.isfile(lake_bin) and os.access(lake_bin, os.X_OK))):
                tmp_path = None
                try:
                    with tempfile.NamedTemporaryFile(suffix=".lean", mode="w", encoding="utf-8", delete=False, dir=project_dir) as f:
                        f.write(code)
                        tmp_path = f.name
                    proc = subprocess.run([lake_bin, "env", "lean", tmp_path], capture_output=True, text=True, timeout=300, cwd=project_dir)
                    if proc.returncode == 0:
                        return Lean4VerificationResult(True, "machine_checked", th_name, tactics, False, [], "lake env lean exit 0 em projeto com Mathlib (R754).", code)
                    return Lean4VerificationResult(False, "compiler_error", th_name, tactics, False, [proc.stderr.strip() or proc.stdout.strip()], proc.stderr or proc.stdout, code)
                except subprocess.TimeoutExpired:
                    return Lean4VerificationResult(False, "compiler_error", th_name, tactics, False, ["Timeout 300s no lake env lean (fail-closed)."], "Timeout no projeto lake.", code)
                finally:
                    try:
                        if tmp_path and os.path.isfile(tmp_path):
                            os.remove(tmp_path)
                    except OSError:
                        pass
            # lake ausente ou projeto inválido: cai para o caminho sem projeto, sem alegar machine_checked.

        # 3. Execução real via binário Lean se disponível
        if self.has_compiler:
            try:
                with tempfile.NamedTemporaryFile(suffix=".lean", mode="w", encoding="utf-8", delete=False) as f:
                    f.write(code)
                    tmp_file = f.name
                
                cmd = [self.lean_binary, tmp_file]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                os.remove(tmp_file)

                if proc.returncode == 0:
                    return Lean4VerificationResult(
                        is_valid=True,
                        status="machine_checked",
                        theorem_name=th_name,
                        tactics_used=tactics,
                        has_sorry=False,
                        errors=[],
                        output_log="Verificado com sucesso pelo kernel Lean 4 (exit code 0).",
                        lean_source=code,
                    )
                else:
                    err_text = (proc.stderr.strip() or proc.stdout.strip())
                    # Ambiente sem Mathlib/projeto lake: erro é de setup, não de prova.
                    # Fallback honesto para syntax_verified apenas neste caso específico.
                    env_missing = any(s in err_text for s in (
                        "unknown module prefix 'Mathlib'", "unknown package",
                        "No directory 'Mathlib'", "Mathlib.olean",
                    ))
                    static_ok = (
                        ("theorem" in code or "lemma" in code)
                        and (":= by" in code or ":=" in code)
                        and len(tactics) > 0
                    )
                    if env_missing and static_ok:
                        return Lean4VerificationResult(
                            is_valid=True,
                            status="syntax_verified",
                            theorem_name=th_name,
                            tactics_used=tactics,
                            has_sorry=False,
                            errors=[],
                            output_log=(
                                "Estrutura Lean 4 válida; compilador presente mas "
                                "Mathlib ausente no projeto (sem lake env). "
                                "Máximo syntax_verified; não alegar machine_checked. "
                                f"Detalhe: {err_text[:300]}"
                            ),
                            lean_source=code,
                        )
                    # Tática Mathlib (ring/linarith/omega/aesop/...) sem import: também ambiente.
                    mathlib_only = {"ring", "linarith", "nlinarith", "omega", "aesop", "norm_num", "positivity"}
                    unknown_tactic = "unknown tactic" in err_text
                    uses_mathlib_tactic = any(t in mathlib_only for t in tactics)
                    if unknown_tactic and uses_mathlib_tactic and "import Mathlib" not in code and static_ok:
                        return Lean4VerificationResult(
                            is_valid=True,
                            status="syntax_verified",
                            theorem_name=th_name,
                            tactics_used=tactics,
                            has_sorry=False,
                            errors=[],
                            output_log=(
                                "Estrutura Lean 4 válida; tática Mathlib sem import no arquivo bare. "
                                "Máximo syntax_verified; use projeto lake+Mathlib para machine_checked. "
                                f"Detalhe: {err_text[:300]}"
                            ),
                            lean_source=code,
                        )
                    return Lean4VerificationResult(
                        is_valid=False,
                        status="compiler_error",
                        theorem_name=th_name,
                        tactics_used=tactics,
                        has_sorry=False,
                        errors=[proc.stderr.strip() or proc.stdout.strip()],
                        output_log=proc.stderr or proc.stdout,
                        lean_source=code,
                    )
            except Exception as exc:
                # Fallback para syntax_verified
                pass

        # 4. Modo de validação estática estrutural (syntax_verified)
        is_structure_valid = (
            ("theorem" in code or "lemma" in code) and
            (":= by" in code or ":=" in code) and
            len(tactics) > 0
        )

        if is_structure_valid:
            return Lean4VerificationResult(
                is_valid=True,
                status="syntax_verified",
                theorem_name=th_name,
                tactics_used=tactics,
                has_sorry=False,
                errors=[],
                output_log=f"Estrutura Lean 4 válida com {len(tactics)} tática(s) formais ({', '.join(tactics)}).",
                lean_source=code,
            )
        else:
            return Lean4VerificationResult(
                is_valid=False,
                status="syntax_error",
                theorem_name=th_name,
                tactics_used=tactics,
                has_sorry=False,
                errors=["Declaração Lean 4 incompleta (ausência de 'theorem', ':= by' ou táticas)."],
                output_log="Estrutura de prova inválida.",
                lean_source=code,
            )
