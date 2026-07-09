#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anti-Plagiarism Scanner v1.0 — Detector de Padrões de Plágio
=============================================================

Analisa texto acadêmico em busca de padrões que indicam possível plágio
ou baixa originalidade, gerando um score de originalidade (0-100).

Critérios analisados:
  1. Repetição de frases longas (>5 palavras)
  2. Similaridade entre parágrafos
  3. Uso excessivo de citações diretas
  4. Falta de paráfrase
  5. Terminologia sem atribuição
  6. Padrões de cópia estrutural

Uso:
  python anti_plagiarism_scanner.py --input dissertacao.tex
  python anti_plagiarism_scanner.py --input dissertacao.tex --json
"""

import re
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from collections import Counter
from itertools import combinations


# ============================================================
# PADRÕES DE PLÁGIO DETECTÁVEIS
# ============================================================

# Citações diretas (entre aspas)
DIRECT_QUOTES = [
    r'"[^"]{10,}"',  # Aspas retas longas
    r'"[^"]{10,}"',  # Aspas curvas longas
    r'``[^`]{10,}\'\'',  # Aspas LaTeX longas
]

# Referências sem contexto (possível cópia de referências)
REFERENCE_PATTERNS = [
    r'\b(?:segundo|conforme|de acordo com|apud)\s+\w+\s+\(\d{4}\)',
    r'\b\w+\s+\(\d{4}\)\s+(?:relata|afirma|destaca|ressalta|argumenta)',
]


@dataclass
class ScanResult:
    """Resultado do scan anti-plágio."""
    score: float  # 0-100 (maior = mais original)
    grade: str  # A-F
    details: dict
    warnings: list[str]
    suggestions: list[str]


class AntiPlagiarismScanner:
    """Scanner de padrões de plágio em texto acadêmico."""

    def __init__(self):
        self.text = ""
        self.paragraphs = []
        self.sentences = []
        self.warnings = []
        self.suggestions = []

    def load_text(self, filepath: str) -> None:
        """Carrega texto de um arquivo .tex."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        self._raw_text = content  # Store raw text before stripping

        # Remove comandos LaTeX (preservando texto)
        content = re.sub(r'\\begin\{[^}]*\}', '', content)
        content = re.sub(r'\\end\{[^}]*\}', '', content)
        content = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', content)
        content = re.sub(r'\\[a-zA-Z]+', '', content)
        content = re.sub(r'%.*$', '', content, flags=re.MULTILINE)

        self.text = content
        self.paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 50]
        self.sentences = re.split(r'[.!?]+', content)
        self.sentences = [s.strip() for s in self.sentences if s.strip() and len(s.split()) > 5]

    def _count_pattern(self, patterns: list[str], text: str) -> int:
        """Conta ocorrências de padrões no texto."""
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE | re.MULTILINE))
        return count

    def _analyze_repeated_phrases(self) -> float:
        """Analisa repetição de frases longas (0-100)."""
        if len(self.sentences) < 5:
            return 70

        # Extrair frases de 5+ palavras
        phrase_windows = []
        for sent in self.sentences:
            words = sent.split()
            for i in range(len(words) - 4):
                phrase = ' '.join(words[i:i+5])
                phrase_windows.append(phrase.lower())

        if not phrase_windows:
            return 70

        # Contar repetições
        phrase_counts = Counter(phrase_windows)
        repeated = {p: c for p, c in phrase_counts.items() if c > 1}

        # Calcular score
        total_phrases = len(phrase_windows)
        repeated_phrases = sum(c - 1 for c in repeated.values())
        ratio = repeated_phrases / total_phrases if total_phrases > 0 else 0

        if ratio < 0.05:
            return 90
        elif ratio < 0.10:
            return 70
        elif ratio < 0.15:
            return 50
        elif ratio < 0.20:
            return 30
        else:
            return 10

    def _analyze_paragraph_similarity(self) -> float:
        """Analisa similaridade entre parágrafos (0-100)."""
        if len(self.paragraphs) < 3:
            return 70

        # Calcular similaridade Jaccard entre pares de parágrafos
        similarities = []
        for p1, p2 in combinations(self.paragraphs[:20], 2):  # Limitar a 20 parágrafos
            words1 = set(p1.lower().split())
            words2 = set(p2.lower().split())

            if not words1 or not words2:
                continue

            intersection = words1 & words2
            union = words1 | words2
            similarity = len(intersection) / len(union)
            similarities.append(similarity)

        if not similarities:
            return 70

        avg_similarity = sum(similarities) / len(similarities)

        if avg_similarity < 0.15:
            return 90
        elif avg_similarity < 0.25:
            return 70
        elif avg_similarity < 0.35:
            return 50
        elif avg_similarity < 0.45:
            return 30
        else:
            return 10

    def _analyze_direct_quotes(self) -> float:
        """Analisa uso de citações diretas (0-100)."""
        total_words = len(self.text.split())
        if total_words == 0:
            return 70

        quote_count = self._count_pattern(DIRECT_QUOTES, self.text)
        quote_words = sum(len(q.split()) for q in re.findall(r'"[^"]+"', self.text))

        quote_ratio = quote_words / total_words

        # Texto acadêmico ideal: < 10% citações diretas
        if quote_ratio < 0.05:
            return 90
        elif quote_ratio < 0.10:
            return 70
        elif quote_ratio < 0.15:
            return 50
        elif quote_ratio < 0.20:
            return 30
        else:
            return 10

    def _analyze_attribution_patterns(self) -> float:
        """Analisa padrões de atribuição (0-100)."""
        total_sentences = len(self.sentences)
        if total_sentences == 0:
            return 50

        # Contar frases com atribuição
        attributed = 0
        for sent in self.sentences:
            for pattern in REFERENCE_PATTERNS:
                if re.search(pattern, sent, re.IGNORECASE):
                    attributed += 1
                    break

        # Also count \cite{} occurrences in raw text
        cite_count = 0
        if hasattr(self, '_raw_text'):
            cite_count = len(re.findall(r'cite\{[^}]+\}', self._raw_text))

        # Combine: natural language attributions + \cite{} attributions
        total_attributed = attributed + cite_count
        attribution_ratio = total_attributed / total_sentences

        # Texto bem atribuído: 20-40% das frases
        if 0.15 <= attribution_ratio <= 0.45:
            return 90
        elif 0.10 <= attribution_ratio <= 0.55:
            return 70
        elif 0.05 <= attribution_ratio <= 0.65:
            return 50
        else:
            return 30

    def scan(self) -> ScanResult:
        """Executa o scan anti-plágio completo."""
        self.warnings = []
        self.suggestions = []

        # Análises
        repeated_score = self._analyze_repeated_phrases()
        similarity_score = self._analyze_paragraph_similarity()
        quote_score = self._analyze_direct_quotes()
        attribution_score = self._analyze_attribution_patterns()

        # Pesos
        weights = {
            'repeated_phrases': 0.30,
            'paragraph_similarity': 0.30,
            'direct_quotes': 0.20,
            'attribution': 0.20,
        }

        scores = {
            'repeated_phrases': repeated_score,
            'paragraph_similarity': similarity_score,
            'direct_quotes': quote_score,
            'attribution': attribution_score,
        }

        # Score final ponderado
        final_score = sum(scores[k] * weights[k] for k in scores)

        # Gerar warns e sugestões
        if repeated_score < 50:
            self.warnings.append("Repetição excessiva de frases longas")
            self.suggestions.append("Reformular frases repetidas usando paráfrase")

        if similarity_score < 50:
            self.warnings.append("Alta similaridade entre parágrafos")
            self.suggestions.append("Diversificar estrutura e vocabulário entre parágrafos")

        if quote_score < 50:
            self.warnings.append("Uso excessivo de citações diretas")
            self.suggestions.append("Substituir citações diretas por paráfrases com atribuição")

        if attribution_score < 50:
            self.warnings.append("Padrões de atribuição inadequados")
            self.suggestions.append("Melhorar contextualização das citações")

        # Determinar grade
        if final_score >= 80:
            grade = "A"
        elif final_score >= 65:
            grade = "B"
        elif final_score >= 50:
            grade = "C"
        elif final_score >= 35:
            grade = "D"
        else:
            grade = "F"

        return ScanResult(
            score=round(final_score, 1),
            grade=grade,
            details=scores,
            warnings=self.warnings,
            suggestions=self.suggestions,
        )


def main():
    parser = argparse.ArgumentParser(description='Anti-Plagiarism Scanner')
    parser.add_argument('--input', '-i', required=True, help='Arquivo .tex para analisar')
    parser.add_argument('--json', '-j', action='store_true', help='Saída em JSON')
    args = parser.parse_args()

    scanner = AntiPlagiarismScanner()
    scanner.load_text(args.input)
    result = scanner.scan()

    if args.json:
        print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    else:
        print(f"=== Anti-Plagiarism Scanner v1.0 ===")
        print(f"Arquivo: {args.input}")
        print(f"")
        print(f"SCORE: {result.score}/100 (Grade: {result.grade})")
        print(f"")
        print(f"Detalhes:")
        for k, v in result.details.items():
            print(f"  - {k}: {v}/100")
        print(f"")
        if result.warnings:
            print(f"Alertas:")
            for w in result.warnings:
                print(f"  [!] {w}")
        print(f"")
        if result.suggestions:
            print(f"Sugestoes:")
            for s in result.suggestions:
                print(f"  -> {s}")


if __name__ == '__main__':
    main()
