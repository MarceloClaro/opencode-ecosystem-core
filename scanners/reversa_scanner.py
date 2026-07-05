# -*- coding: utf-8 -*-
"""
ReversaScanner — Scanner de Engenharia Reversa
==============================================
Inspirado no repositório MarceloClaro/reversa: analisa código-fonte legado
(ou corpus textual contendo código) e extrai sinais para gerar especificações
executáveis (TSPECs) de engenharia reversa — o caminho código → spec → refatoração.

Sem dependências externas (stdlib puro) e sem imports circulares:
define suas próprias dataclasses de resultado.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class DiagnosticResult:
    scanner_name: str
    score: float
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


# Padrões de linguagens/construções reconhecidas no corpus
_CODE_PATTERNS = {
    "python_def": re.compile(r"\bdef\s+\w+\s*\("),
    "python_class": re.compile(r"\bclass\s+\w+"),
    "js_function": re.compile(r"\bfunction\s+\w+\s*\(|=>"),
    "java_like": re.compile(r"\b(public|private|protected)\s+\w+"),
    "sql": re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE)\b\s+", re.IGNORECASE),
    "imports": re.compile(r"^\s*(import|from|#include|require\()", re.MULTILINE),
}

_SMELL_PATTERNS = {
    "todo_fixme": re.compile(r"\b(TODO|FIXME|XXX|HACK)\b"),
    "magic_numbers": re.compile(r"[^\w.](\d{4,})[^\w.]"),
    "long_lines": re.compile(r"^.{160,}$", re.MULTILINE),
    "bare_except": re.compile(r"except\s*:\s*$", re.MULTILINE),
    "hardcoded_secret": re.compile(
        r"(password|api_key|secret|token)\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE),
}


class ReversaScanner:
    """
    Scanner de Engenharia Reversa (código legado → especificações executáveis).

    Estratégia:
    1. Detecta presença e densidade de código estruturado no corpus
    2. Identifica code smells que sinalizam necessidade de engenharia reversa
    3. Pontua a aplicabilidade da engenharia reversa (0–10)
    4. Recomenda a geração de TSPECs para as construções encontradas
    """

    name = "ReversaScanner"

    def scan(self, corpus: str) -> DiagnosticResult:
        corpus = corpus or ""
        findings: List[str] = []
        recommendations: List[str] = []

        # 1. Detecção de código
        detected = [k for k, p in _CODE_PATTERNS.items() if p.search(corpus)]
        has_code = bool(detected)

        # 2. Detecção de smells
        smells = [k for k, p in _SMELL_PATTERNS.items() if p.search(corpus)]

        # 3. Pontuação: base pela presença de código, ajuste por densidade e smells
        if has_code:
            density = min(len(detected) / len(_CODE_PATTERNS), 1.0)
            score = 5.0 + 3.0 * density + min(len(smells), 4) * 0.5
            score = min(score, 10.0)
            findings.append(
                f"Código estruturado detectado ({', '.join(detected)}). "
                "Engenharia reversa aplicável."
            )
            if smells:
                findings.append(
                    f"Code smells encontrados: {', '.join(smells)} — "
                    "candidatos prioritários à engenharia reversa."
                )
            recommendations.append(
                "Gerar TSPECs (specs executáveis) para cada módulo detectado "
                "antes de refatorar (código → spec → refatoração guiada)."
            )
            recommendations.append(
                "Extrair regras de negócio implícitas para SPEC-000 e vinculá-las "
                "ao SpecRegistry do motor SDD."
            )
            if "hardcoded_secret" in smells:
                recommendations.append(
                    "URGENTE: remover segredos hardcoded e migrar para variáveis "
                    "de ambiente antes de qualquer publicação."
                )
        else:
            score = 3.0
            findings.append(
                "Nenhum código estruturado detectado para engenharia reversa."
            )

        return DiagnosticResult(
            scanner_name=self.name,
            score=round(score, 2),
            findings=findings,
            recommendations=recommendations,
        )


# Singleton para uso no pipeline
reversa_scanner = ReversaScanner()
