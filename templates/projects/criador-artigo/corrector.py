#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PT-BR Output Corrector v2.0 — Refatorado com DI
=================================================
Corretor Ortografico, Gramatical e Linguistico com deteccao CJK.
Injecao de Dependencia via state_manager (opcional, fallback = Container).

Pipeline:
  1. Scan/Remove CJK characters (Chinese/Japanese/Korean)
  2. PT-BR ortografia/gramatica corrections
  3. Report generation
"""

from __future__ import annotations
import re
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime

try:
    from core.interfaces import IStateManager, IEventBus
except ImportError:
    import sys as _sys
    _recon = Path(__file__).resolve().parent.parent / "reconstruction"
    if _recon.exists():
        _sys.path.insert(0, str(_recon))
    from core_interfaces import IStateManager, IEventBus

try:
    from core.container import Container
except ImportError:
    class Container:
        _instance = None
        @classmethod
        def instance(cls):
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
        def __init__(self):
            self._services = {}
        def register(self, name, instance):
            self._services[name] = instance
        def resolve(self, name):
            return self._services.get(name)

# ============================================================================
# CJK Detection
# ============================================================================

CJK_RANGES = [
    (0x4E00, 0x9FFF,   "CJK Unified Ideographs"),
    (0x3400, 0x4DBF,   "CJK Unified Ideographs Extension A"),
    (0x20000, 0x2A6DF, "CJK Unified Ideographs Extension B"),
    (0x2A700, 0x2B73F, "CJK Unified Ideographs Extension C"),
    (0x2B740, 0x2B81F, "CJK Unified Ideographs Extension D"),
    (0x2B820, 0x2CEAF, "CJK Unified Ideographs Extension E"),
    (0xF900, 0xFAFF,   "CJK Compatibility Ideographs"),
    (0x2F800, 0x2FA1F, "CJK Compatibility Ideographs Supplement"),
    (0x3000, 0x303F,   "CJK Symbols and Punctuation"),
    (0x3040, 0x309F,   "Hiragana"),
    (0x30A0, 0x30FF,   "Katakana"),
    (0xAC00, 0xD7AF,   "Hangul Syllables"),
    (0x1100, 0x11FF,   "Hangul Jamo"),
    (0x3130, 0x318F,   "Hangul Compatibility Jamo"),
    (0x3200, 0x32FF,   "Enclosed CJK Letters and Months"),
    (0xFF00, 0xFFEF,   "Halfwidth and Fullwidth Forms"),
]

# ============================================================================
# Data classes
# ============================================================================

@dataclass
class ContaminationIssue:
    line_number: int
    column: int
    character: str
    unicode_hex: str
    category: str
    context_before: str
    context_after: str
    full_line: str
    suggestion: str = ""

@dataclass
class CorrectionReport:
    timestamp: str = ""
    input_file: str = ""
    output_file: str = ""
    total_lines: int = 0
    total_chars: int = 0
    total_issues: int = 0
    issues_by_category: dict = field(default_factory=dict)
    issues: list = field(default_factory=list)
    corrected_text: str = ""
    is_clean: bool = True
    summary: str = ""

# ============================================================================
# PT-BR Corrections Map
# ============================================================================

PTBR_ACCENT_FIXES = {
    "voce": "você", "nao": "não", "ate": "até",
    "tambem": "também", "alem": "além",
    "possivel": "possível", "facil": "fácil", "dificil": "difícil",
    "logica": "lógica", "matematica": "matemática",
    "automatico": "automático", "numero": "número",
    "periodo": "período", "inicio": "início",
    "serie": "série", "historico": "histórico",
    "economico": "econômico", "tecnico": "técnico",
    "cientifico": "científico", "estatistico": "estatístico",
    "metodo": "método", "analise": "análise",
    "conclusao": "conclusão", "pesquisa": "pesquisa",
    "relevancia": "relevância", "eficiencia": "eficiência",
    "experiencia": "experiência", "essencia": "essência",
    "diferenca": "diferença", "existencia": "existência",
    "importancia": "importância", "abreviacao": "abreviação",
    "automacao": "automação", "comunicacao": "comunicação",
    "distribuicao": "distribuição", "educacao": "educação",
    "formacao": "formação", "informacao": "informação",
    "operacao": "operação", "producao": "produção",
    "situacao": "situação", "solucao": "solução",
    "transformacao": "transformação", "utilizacao": "utilização",
    "validacao": "validação", "variacao": "variação",
    "avaliacao": "avaliação", "correcao": "correção",
    "descricao": "descrição", "explicacao": "explicação",
    "geracao": "geração", "implementacao": "implementação",
    "integracao": "integração", "otimizacao": "otimização",
    "selecao": "seleção", "simulacao": "simulação",
    "verificacao": "verificação",
}

PTBR_NO_ACCENT = {"e", "ou", "se", "mas", "que", "de", "do", "da", "dos", "das",
                  "um", "uma", "uns", "umas", "no", "na", "nos", "nas",
                  "por", "para", "com", "sem", "sob", "sobre", "entre"}

GRAMMAR_FIXES = [
    (re.compile(r"\bfazem\s+(\d+)\s+anos\b", re.IGNORECASE), r"faz \1 anos"),
    (re.compile(r"\bhaviam\s+(\d+)\b", re.IGNORECASE), r"havia \1"),
    (re.compile(r"\bexistem\s+(.+?)\s+problema\b", re.IGNORECASE), r"existem \1 problemas"),
]

# ============================================================================
# Core Functions
# ============================================================================

def is_cjk(char: str) -> tuple[bool, str]:
    code = ord(char)
    for start, end, name in CJK_RANGES:
        if start <= code <= end:
            if "Hiragana" in name or "Katakana" in name:
                return True, "japanese"
            if "Hangul" in name:
                return True, "korean"
            if "Punctuation" in name or "Symbols" in name:
                return True, "cjk_punctuation"
            return True, "chinese"
    return False, ""

def remove_cjk_chars(text: str) -> str:
    result = []
    for char in text:
        is_c, _ = is_cjk(char)
        if not is_c:
            result.append(char)
        elif char == '\u3000':
            result.append(' ')
    return ''.join(result)

def apply_ptbr_corrections(text: str) -> tuple[str, list[dict]]:
    corrections = []
    result = text
    result = re.sub(r" {2,}", " ", result)
    result = re.sub(r" +([.,;:!?\)])", r"\1", result)
    result = re.sub(r"([(\[])\s+", r"\1", result)

    for wrong, correct in PTBR_ACCENT_FIXES.items():
        if wrong in PTBR_NO_ACCENT:
            continue
        pattern = re.compile(rf"(?<![a-zA-Z]){re.escape(wrong)}(?![a-zA-Z])", re.IGNORECASE)
        for match in pattern.finditer(result):
            corrections.append({
                "type": "ortografia",
                "original": match.group(),
                "correction": correct,
                "position": match.start(),
            })
        result = pattern.sub(correct, result)

    for pattern, replacement in GRAMMAR_FIXES:
        for match in pattern.finditer(result):
            corrections.append({
                "type": "gramatica",
                "original": match.group(),
                "correction": pattern.sub(replacement, match.group()),
                "position": match.start(),
            })
        result = pattern.sub(replacement, result)

    result = result.replace('\u201c', '"').replace('\u201d', '"')
    result = result.replace('\u2018', "'").replace('\u2019', "'")
    return result, corrections


class PTBRCorrector:
    """Corretor linguistico com DI."""

    def __init__(self, state_manager: Optional[IStateManager] = None):
        self.state_manager = state_manager or Container.instance().resolve("state_manager")

    def scan_text(self, text: str) -> list[ContaminationIssue]:
        issues = []
        lines = text.split("\n")
        for line_num, line in enumerate(lines, 1):
            for col, char in enumerate(line, 1):
                is_c, category = is_cjk(char)
                if is_c:
                    context_before = line[max(0, col-1-30):col-1]
                    context_after = line[col:min(len(line), col+30)]
                    issues.append(ContaminationIssue(
                        line_number=line_num, column=col, character=char,
                        unicode_hex=f"U+{ord(char):04X}", category=category,
                        context_before=context_before, context_after=context_after,
                        full_line=line,
                        suggestion=f"Remover caractere {category}: '{char}'"
                    ))
        return issues

    def clean_text(self, text: str) -> tuple[str, list[ContaminationIssue]]:
        issues = self.scan_text(text)
        cleaned = remove_cjk_chars(text)
        cleaned = re.sub(r" {2,}", " ", cleaned)
        cleaned = re.sub(r"\n\s+", "\n", cleaned)
        return cleaned, issues


def correct_file(input_path: str, output_path: Optional[str] = None,
                fix: bool = True, json_output: bool = False,
                state_manager: Optional[IStateManager] = None) -> CorrectionReport:
    """Pipeline completo de correcao."""
    sm = state_manager or Container.instance().resolve("state_manager")
    input_p = Path(input_path)
    text = input_p.read_text(encoding="utf-8")
    corrector = PTBRCorrector(sm)

    cleaned, cjk_issues = corrector.clean_text(text)
    final_text, ptbr_corrections = apply_ptbr_corrections(cleaned)

    report = CorrectionReport(
        timestamp=datetime.now().isoformat(),
        input_file=input_path,
        output_file=output_path or "",
        total_lines=text.count("\n") + 1,
        total_chars=len(text),
        total_issues=len(cjk_issues) + len(ptbr_corrections),
        issues_by_category={"cjk": len(cjk_issues), "ptbr_ortografia": len(ptbr_corrections)},
        issues=[asdict(i) for i in cjk_issues[:50]],
        corrected_text=final_text if fix else "",
        is_clean=len(cjk_issues) == 0,
    )
    report.summary = (
        "Texto limpo: nenhum CJK detectado." if report.is_clean
        else f"Contaminacao: {len(cjk_issues)} CJK removido(s), "
             f"{len(ptbr_corrections)} correcao(oes) PT-BR."
    )

    if fix and output_path:
        output_p = Path(output_path)
        output_p.parent.mkdir(parents=True, exist_ok=True)
        output_p.write_text(final_text, encoding="utf-8")

    if json_output:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(report.summary)
        if cjk_issues:
            print(f"\nCJK ({len(cjk_issues)}):")
            for issue in cjk_issues[:20]:
                print(f"  L{issue.line_number}:{issue.column} '{issue.character}' ({issue.category})")
        if ptbr_corrections:
            print(f"\nPT-BR ({len(ptbr_corrections)}):")
            for c in ptbr_corrections[:20]:
                print(f"  '{c['original']}' -> '{c['correction']}'")

    return report


def main():
    parser = argparse.ArgumentParser(description="PT-BR Output Corrector v2.0 - Refatorado DI")
    parser.add_argument("--input", "-i", help="Arquivo de entrada")
    parser.add_argument("--output", "-o", help="Arquivo de saida")
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--scan-only", action="store_true")
    args = parser.parse_args()

    if args.input:
        output = args.output
        if not output and args.fix:
            output = str(Path(args.input).with_stem(Path(args.input).stem + "_corrigido"))
        correct_file(args.input, output, fix=args.fix, json_output=args.json)
    else:
        text = sys.stdin.read()
        corrector = PTBRCorrector()
        if args.fix:
            cleaned, issues = corrector.clean_text(text)
            final, ptbr = apply_ptbr_corrections(cleaned)
            print(final)
        else:
            issues = corrector.scan_text(text)
            print(f"Scan: {len(issues)} CJK characters found")


if __name__ == "__main__":
    main()
