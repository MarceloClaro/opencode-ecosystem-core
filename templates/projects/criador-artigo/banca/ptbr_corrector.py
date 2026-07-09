# -*- coding: utf-8 -*-
"""
PT-BR Output Corrector — Corretor Ortografico, Gramatical e Linguistico

Detecta e remove contaminacao de caracteres chineses em saidas PT-BR.
Integrado ao ecossistema OpenCode com contexto em chines + saida PT-BR.

Uso:
  python ptbr_corrector.py --input texto.md
  python ptbr_corrector.py --input texto.md --output texto_corrigido.md
  python ptbr_corrector.py --input texto.md --fix --output texto_corrigido.md
  python ptbr_corrector.py --input texto.md --json
  python ptbr_corrector.py --directory documentos/armadilha-renda-media/ --recursive --fix

Autor: Ecossistema OpenCode v3.4
Modelo: big-pickle (OpenCode Zen)
"""

import re
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime


# ============================================================
# Unicode Ranges — Caracteres CJK (Chines/Japones/Coreano)
# ============================================================

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


@dataclass
class ContaminationIssue:
    """Representa um unico problema de contaminacao detectado."""
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
    """Relatorio completo de correcao."""
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


def is_cjk(char: str) -> tuple[bool, str]:
    """
    Verifica se um caractere pertence a algum bloco CJK.
    Retorna (is_cjk, category).
    """
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
    """Remove todos os caracteres CJK de um texto, caractere por caractere."""
    result = []
    for char in text:
        is_c, _ = is_cjk(char)
        if not is_c:
            result.append(char)
        elif char == '\u3000':
            # Espaco CJK → espaco normal
            result.append(' ')
    return ''.join(result)


# ============================================================
# Corretor Ortografico/Gramatical PT-BR
# ============================================================

# Correcoes de acentuacao para palavras comuns sem acento
PTBR_ACCENT_FIXES = {
    "voce": "você",
    "nao": "não",
    "ate": "até",
    "tambem": "também",
    "alem": "além",
    "possivel": "possível",
    "facil": "fácil",
    "dificil": "difícil",
    "logica": "lógica",
    "matematica": "matemática",
    "automatico": "automático",
    "numero": "número",
    "periodo": "período",
    "inicio": "início",
    "serie": "série",
    "historico": "histórico",
    "economico": "econômico",
    "tecnico": "técnico",
    "cientifico": "científico",
    "estatistico": "estatístico",
    "metodo": "método",
    "analise": "análise",
    "conclusao": "conclusão",
    "pesquisa": "pesquisa",
    "relevancia": "relevância",
    "eficiencia": "eficiência",
    "experiencia": "experiência",
    "essencia": "essência",
    "diferenca": "diferença",
    "existencia": "existência",
    "importancia": "importância",
    "abreviacao": "abreviação",
    "automacao": "automação",
    "comunicacao": "comunicação",
    "distribuicao": "distribuição",
    "educacao": "educação",
    "formacao": "formação",
    "informacao": "informação",
    "operacao": "operação",
    "producao": "produção",
    "situacao": "situação",
    "solucao": "solução",
    "transformacao": "transformação",
    "utilizacao": "utilização",
    "validacao": "validação",
    "variacao": "variação",
    "avaliacao": "avaliação",
    "correcao": "correção",
    "descricao": "descrição",
    "explicacao": "explicação",
    "geracao": "geração",
    "implementacao": "implementação",
    "integracao": "integração",
    "otimizacao": "otimização",
    "selecao": "seleção",
    "simulacao": "simulação",
    "verificacao": "verificação",
    # Palavras com acento no primeiro e
    "e": None,  # IGNORAR — conjuncao "e" nao leva acento
    "excecao": "exceção",
    "projecao": "projeção",
    "refeicao": "refeição",
    "sancao": "sanção",
}

# Palavras que NAO devem ser acentuadas (falsos positivos)
PTBR_NO_ACCENT = {"e", "ou", "se", "mas", "que", "de", "do", "da", "dos", "das",
                  "um", "uma", "uns", "umas", "no", "na", "nos", "nas",
                  "por", "para", "com", "sem", "sob", "sobre", "entre"}

# Padroes gramaticais
GRAMMAR_FIXES = [
    (re.compile(r"\bfazem\s+(\d+)\s+anos\b", re.IGNORECASE), r"faz \1 anos"),
    (re.compile(r"\bhaviam\s+(\d+)\b", re.IGNORECASE), r"havia \1"),
    (re.compile(r"\bexistem\s+(.+?)\s+problema\b", re.IGNORECASE), r"existem \1 problemas"),
]


def apply_ptbr_corrections(text: str) -> tuple[str, list[dict]]:
    """
    Aplica correcoes ortograficas e gramaticais basicas em PT-BR.
    Retorna (texto_corrigido, lista_de_correcoes).
    """
    corrections = []
    result = text

    # 1. Normalizar espacos
    result = re.sub(r" {2,}", " ", result)
    result = re.sub(r" +([.,;:!?\)])", r"\1", result)
    result = re.sub(r"([(\[])\s+", r"\1", result)

    # 2. Correcoes de acentuacao
    for wrong, correct in PTBR_ACCENT_FIXES.items():
        if correct is None:
            continue
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

    # 3. Correcoes gramaticais
    for pattern, replacement in GRAMMAR_FIXES:
        for match in pattern.finditer(result):
            corrections.append({
                "type": "gramatica",
                "original": match.group(),
                "correction": pattern.sub(replacement, match.group()),
                "position": match.start(),
            })
        result = pattern.sub(replacement, result)

    # 4. Normalizar aspas
    result = result.replace('\u201c', '"').replace('\u201d', '"')
    result = result.replace('\u2018', "'").replace('\u2019', "'")

    return result, corrections


# ============================================================
# Pipeline Completo
# ============================================================

class PTBRCorrector:
    """Corretor de contaminacao linguistica para saidas PT-BR."""

    def __init__(self):
        pass

    def scan_text(self, text: str) -> list[ContaminationIssue]:
        """Escaneia texto em busca de contaminacao CJK."""
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
                        full_line=line, suggestion=f"Remover caractere {category}: '{char}'"
                    ))
        return issues

    def clean_text(self, text: str) -> tuple[str, list[ContaminationIssue]]:
        """Remove todos os caracteres CJK do texto."""
        issues = self.scan_text(text)
        cleaned = remove_cjk_chars(text)
        # Normalizar espacos resultantes
        cleaned = re.sub(r" {2,}", " ", cleaned)
        cleaned = re.sub(r"\n\s+", "\n", cleaned)
        return cleaned, issues


def correct_file(input_path: str, output_path: Optional[str] = None,
                fix: bool = True, json_output: bool = False) -> CorrectionReport:
    """Pipeline completo de correcao para um arquivo."""
    input_p = Path(input_path)
    if not input_p.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {input_path}")

    text = input_p.read_text(encoding="utf-8")
    corrector = PTBRCorrector()

    # Fase 1: Deteccao e remocao de CJK
    cleaned, cjk_issues = corrector.clean_text(text)

    # Fase 2: Correcao ortografica/gramatical PT-BR
    final_text, ptbr_corrections = apply_ptbr_corrections(cleaned)

    # Gerar relatorio
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
    report.summary = (f"Texto limpo: nenhum CJK detectado." if report.is_clean
                      else f"Contaminacao: {len(cjk_issues)} caractere(s) CJK removido(s), "
                           f"{len(ptbr_corrections)} correcao(oes) PT-BR.")

    # Salvar arquivo corrigido
    if fix and output_path:
        output_p = Path(output_path)
        output_p.parent.mkdir(parents=True, exist_ok=True)
        output_p.write_text(final_text, encoding="utf-8")

    if json_output:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(report.summary)
        if cjk_issues:
            print(f"\nDetalhes CJK:")
            for issue in cjk_issues[:20]:
                print(f"  Linha {issue.line_number}, Col {issue.column}: "
                      f"'{issue.character}' ({issue.category}) [{issue.unicode_hex}]")
        if ptbr_corrections:
            print(f"\nCorrecoes PT-BR ({len(ptbr_corrections)}):")
            for corr in ptbr_corrections[:20]:
                print(f"  '{corr['original']}' → '{corr['correction']}' ({corr['type']})")

    return report


def correct_directory(directory: str, recursive: bool = False, fix: bool = True) -> dict:
    """Corrige todos os arquivos de texto em um diretorio."""
    dir_p = Path(directory)
    if not dir_p.exists():
        raise FileNotFoundError(f"Diretorio nao encontrado: {directory}")

    glob_pattern = "**/*" if recursive else "*"
    files = [f for f in dir_p.glob(glob_pattern)
             if f.is_file() and f.suffix in (".md", ".txt", ".py", ".ts", ".json")]

    results = {}
    total_issues = 0

    for f in files:
        output_path = str(f).replace(f"{f.suffix}", f"_corrigido{f.suffix}")
        try:
            report = correct_file(str(f), output_path, fix=fix)
            results[str(f)] = {"issues": report.total_issues, "is_clean": report.is_clean}
            total_issues += report.total_issues
        except Exception as e:
            results[str(f)] = {"error": str(e)}

    return {"directory": directory, "total_files": len(files),
            "total_issues": total_issues, "files": results}


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="PT-BR Output Corrector — Corretor de contaminacao CJK em saidas PT-BR"
    )
    parser.add_argument("--input", "-i", help="Arquivo de entrada")
    parser.add_argument("--output", "-o", help="Arquivo de saida (corrigido)")
    parser.add_argument("--directory", "-d", help="Diretorio para correcao em massa")
    parser.add_argument("--recursive", "-r", action="store_true")
    parser.add_argument("--fix", action="store_true", help="Aplicar correcoes")
    parser.add_argument("--json", action="store_true", help="Saida em JSON")
    parser.add_argument("--scan-only", action="store_true", help="Apenas escanear")

    args = parser.parse_args()

    if args.directory:
        result = correct_directory(args.directory, args.recursive, fix=args.fix)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\nDiretorio: {args.directory}")
            print(f"Arquivos: {result['total_files']}")
            print(f"Issues totais: {result['total_issues']}")
    elif args.input:
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
            print(f"# {len(issues)} CJK chars removed, {len(ptbr)} PT-BR corrections",
                  file=sys.stderr)
        else:
            issues = corrector.scan_text(text)
            if args.json:
                print(json.dumps([asdict(i) for i in issues], ensure_ascii=False, indent=2))
            else:
                print(f"Scan: {len(issues)} CJK characters found")


if __name__ == "__main__":
    main()
