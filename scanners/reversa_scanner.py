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

        # 0. Delegação universal quando corpus é path existente (SPEC-935-R437)
        #    Permite Reversa em artigos, repos, códigos e scripts via filesystem
        corpus_stripped = corpus.strip()
        # Heurística: path curto (<500 chars) sem quebras excessivas e que existe no FS
        if corpus_stripped and len(corpus_stripped) < 600 and "\n" not in corpus_stripped[:300]:
            import os as _os
            from pathlib import Path as _Path
            _p = _Path(corpus_stripped)
            # Tenta resolver relativo ao repo root se não absoluto
            if not _p.is_absolute():
                _root = _Path(__file__).resolve().parents[1]
                _cand = _root / corpus_stripped
                if _cand.exists():
                    _p = _cand
            if _p.exists():
                try:
                    from reversa_universal.engine import ReversaUniversalEngine
                    _eng = ReversaUniversalEngine()
                    _analysis = _eng.analyze(str(_p))
                    _gaps = _analysis.get("gaps", {}).get("gaps", [])
                    _inv = _analysis.get("inventory", {})
                    _mods = _analysis.get("modules", [])
                    if _inv.get("total_files", 0) > 0 or _mods:
                        # Enriquece findings com análise universal
                        findings.append(
                            f"Reversa Universal analisou `{_p}`: "
                            f"{len(_mods)} módulos, {_inv.get('total_files',0)} arquivos, "
                            f"{_inv.get('total_loc',0)} LOC, linguagens {', '.join(_inv.get('languages',[])[:3]) or '—'}."
                        )
                        if _gaps:
                            findings.append(
                                f"Gaps estruturais Reversa: {', '.join(g['type'] for g in _gaps[:3])} "
                                f"({len(_gaps)} total) — correlações e soluções disponíveis."
                            )
                            for g in _gaps[:2]:
                                recommendations.append(f"[{g['severity']}] {g['type']}: {g['description']}")
                        for corr in _analysis.get("gaps", {}).get("correlations", [])[:1]:
                            findings.append(f"Correlação Reversa: {corr}")
                        for sol in _analysis.get("gaps", {}).get("solutions", [])[:2]:
                            recommendations.append(sol)
                        for inn in _analysis.get("gaps", {}).get("innovations", [])[:1]:
                            recommendations.append(f"Inovação: {inn}")
                        # Score universal: base 5 + gaps*0.5 + módulos*0.3 clamp 10
                        _score = 5.0 + min(len(_gaps), 6) * 0.6 + min(len(_mods), 8) * 0.3
                        _score = min(10.0, max(5.5, _score))
                        # Para path, retorna sempre o score universal quando análise produziu inventário
                        return DiagnosticResult(
                            scanner_name=self.name,
                            score=round(_score, 2),
                            findings=findings,
                            recommendations=recommendations or [
                                "Gerar TSPECs para cada módulo via Reversa Universal antes de refatorar."
                            ],
                        )
                except Exception:
                    pass  # fallback para detecção textual

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
