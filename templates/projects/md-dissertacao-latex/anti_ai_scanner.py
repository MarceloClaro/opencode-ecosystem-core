#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anti-AI Scanner v1.0 — Detector de Padrões de IA Generativa
===========================================================

Analisa texto acadêmico em busca de padrões típicos de geração por IA,
gerando um score de "voz autoral" (0-100).

Padrões detectados:
  1. Conectivos genéricos repetitivos
  2. Frases de comprimento uniforme
  3. Ausência de primeira pessoa do pesquisador
  4. Falta de exemplos concretos
  5. Terminologia excessivamente formal/genérica
  6. Transições mecânicas
  7. Ausência de autocrítica/limitações

Uso:
  python anti_ai_scanner.py --input dissertacao.tex
  python anti_ai_scanner.py --input dissertacao.tex --json
"""

import re
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from collections import Counter


# ============================================================
# PADRÕES DE IA DETECTÁVEIS
# ============================================================

# Conectivos genéricos típicos de IA
GENERIC_CONNECTIVES = [
    r'\bÉ importante destacar\b',
    r'\bVale ressaltar\b',
    r'\bNão é possível ignorar\b',
    r'\bCabe ressaltar\b',
    r'\bAdemais\b',
    r'\bPortanto\b',
    r'\bDessa forma\b',
    r'\bNesse sentido\b',
    r'\bSobretudo\b',
    r'\bAlem disso\b',
    r'\bCom efeito\b',
    r'\bEm suma\b',
    r'\bEm consonância\b',
    r'\bNessa perspectiva\b',
    r'\bA esse respeito\b',
    r'\bPor conseguinte\b',
    r'\bTodavia\b',
    r'\bEntretanto\b',
    r'\bImporta salientar\b',
    r'\bRessalta-se\b',
    r'\bDestaca-se\b',
    r'\bSalienta-se\b',
]

# Transições mecânicas
MECHANICAL_TRANSITIONS = [
    r'\bA seguir\b',
    r'\bPor fim\b',
    r'\bEm seguida\b',
    r'\bPrimeiramente\b',
    r'\bSegundamente\b',
    r'\bTerceiramente\b',
    r'\bEm primeiro lugar\b',
    r'\bEm segundo lugar\b',
    r'\bEm terceiro lugar\b',
]

# Padrões de voz passiva excessiva
PASSIVE_VOICE = [
    r'\bfoi (?:realizado|conduzido|elaborado|apresentado|desenvolvido|proposto)\b',
    r'\b(?:são|foi) (?:apresentados?|descritos?|analisados?|discutidos?)\b',
    r'\bforam (?:utilizados?|adotados?|empregados?|selecionados?)\b',
]

# Padrões de frase genérica (início de frase)
GENERIC_OPENERS = [
    r'^(?:A|O|As|Os|Esta|Este|Esta|Estes|Essa|Esse|Essas|Esses) \w+ \w+ (?:de|do|da|dos|das|em|no|na|nos|nas)',
    r'^(?:Neste|Nessa|Nesse|Nestas|Nesses|Naquele|Naquela) (?:capítulo|seção|contexto|sentido|caso)',
]

# Palavras/tipos que indicam presença humana
HUMAN_INDICATORS = [
    r'\b[Ee]u\b',
    r'\b[Mm]inha\b',
    r'\b[Mm]eu\b',
    r'\b[Cc]onsidero\b',
    r'\b[Pp]enso\b',
    r'\b[Aa]credito\b',
    r'\b[Oo]bs[er]vo\b',
    r'\b[Rr]ecalco\b',
    r'\b[Dd]evo admitir\b',
    r'\b[Nn]ão ignoro\b',
    r'\b[Mm]inha experiência\b',
    r'\b[Tt]estemunhei\b',
    r'\b[Oo] que me parece\b',
    r'\b[Uu]ma ressalva\b',
    r'\b[Ss]e eu pudesse\b',
    r'\b[Mm]inha expectativa\b',
]

# Exemplos concretos (indicadores)
CONCRETE_EXAMPLES = [
    r'\b(?:por exemplo|como exemplo|ilustra|exemplifica)\b',
    r'\b\d{4}\b',  # Anos (referências temporais)
    r'\bn\s*=\s*\d+',  # Tamanhos de amostra
    r'\bp\s*[<>≤≥]\s*[\d.]+',  # Valores p
    r'\bd\s*=\s*[\d.]+',  # Tamanho de efeito
]


@dataclass
class ScanResult:
    """Resultado do scan anti-AI."""
    score: float  # 0-100 (maior = mais autoral)
    grade: str  # A-F
    details: dict
    warnings: list[str]
    suggestions: list[str]


class AntiAIScanner:
    """Scanner de padrões de IA generativa em texto acadêmico."""

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

        # Remove comandos LaTeX
        content = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', content)
        content = re.sub(r'\\[a-zA-Z]+', '', content)
        content = re.sub(r'%.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'\{[^}]*\}', '', content)

        self.text = content
        self.paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        self.sentences = re.split(r'[.!?]+', content)
        self.sentences = [s.strip() for s in self.sentences if s.strip()]

    def _count_pattern(self, patterns: list[str], text: str) -> int:
        """Conta ocorrências de padrões no texto."""
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE | re.MULTILINE))
        return count

    def _analyze_sentence_uniformity(self) -> float:
        """Analisa uniformidade do comprimento das frases (0-100)."""
        if not self.sentences:
            return 50

        lengths = [len(s.split()) for s in self.sentences if len(s.split()) > 3]
        if not lengths:
            return 50

        avg = sum(lengths) / len(lengths)
        variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
        std_dev = variance ** 0.5

        # Coeficiente de variação (menor = mais uniforme = mais IA)
        cv = std_dev / avg if avg > 0 else 0

        # CV típico de texto humano: 0.4-0.7
        # CV típico de IA: 0.2-0.4
        if cv < 0.25:
            return 30  # Muito uniforme (IA)
        elif cv < 0.35:
            return 50  # Moderadamente uniforme
        elif cv < 0.45:
            return 70  # Variação natural
        elif cv < 0.55:
            return 85  # Boa variação
        else:
            return 100  # Alta variação (humano)

    def _analyze_connectives(self) -> float:
        """Analisa uso de conectivos genéricos (0-100)."""
        total_words = len(self.text.split())
        if total_words == 0:
            return 50

        generic_count = self._count_pattern(GENERIC_CONNECTIVES, self.text)
        mechanical_count = self._count_pattern(MECHANICAL_TRANSITIONS, self.text)

        total_bad = generic_count + mechanical_count
        ratio = total_bad / (total_words / 1000)  # por 1000 palavras

        # Ratio ideal: < 3 por 1000 palavras
        if ratio < 1:
            return 100
        elif ratio < 2:
            return 85
        elif ratio < 4:
            return 70
        elif ratio < 6:
            return 50
        elif ratio < 8:
            return 30
        else:
            return 10

    def _analyze_voice(self) -> float:
        """Analisa presença de voz autoral (0-100)."""
        human_count = self._count_pattern(HUMAN_INDICATORS, self.text)
        passive_count = self._count_pattern(PASSIVE_VOICE, self.text)

        total = human_count + passive_count
        if total == 0:
            return 30  # Sem indicadores humanos

        human_ratio = human_count / total
        return min(100, human_ratio * 100 + 20)

    def _analyze_examples(self) -> float:
        """Analisa presença de exemplos concretos (0-100)."""
        total_words = len(self.text.split())
        if total_words == 0:
            return 50

        example_count = self._count_pattern(CONCRETE_EXAMPLES, self.text)
        ratio = example_count / (total_words / 1000)

        if ratio > 7:
            return 100
        elif ratio > 5:
            return 85
        elif ratio > 3:
            return 70
        elif ratio > 1:
            return 50
        else:
            return 30

    def _analyze_paragraph_variation(self) -> float:
        """Analisa variação de comprimento dos parágrafos (0-100)."""
        if not self.paragraphs:
            return 50

        lengths = [len(p.split()) for p in self.paragraphs if len(p.split()) > 10]
        if len(lengths) < 3:
            return 50

        avg = sum(lengths) / len(lengths)
        std_dev = (sum((l - avg) ** 2 for l in lengths) / len(lengths)) ** 0.5
        cv = std_dev / avg if avg > 0 else 0

        if cv < 0.3:
            return 30
        elif cv < 0.4:
            return 50
        elif cv < 0.55:
            return 70
        elif cv < 0.7:
            return 85
        else:
            return 100

    def scan(self) -> ScanResult:
        """Executa o scan anti-AI completo."""
        self.warnings = []
        self.suggestions = []

        # Análises
        sentence_score = self._analyze_sentence_uniformity()
        connective_score = self._analyze_connectives()
        voice_score = self._analyze_voice()
        example_score = self._analyze_examples()
        paragraph_score = self._analyze_paragraph_variation()

        # Pesos
        weights = {
            'sentence_uniformity': 0.20,
            'connectives': 0.25,
            'voice': 0.25,
            'examples': 0.15,
            'paragraph_variation': 0.15,
        }

        scores = {
            'sentence_uniformity': sentence_score,
            'connectives': connective_score,
            'voice': voice_score,
            'examples': example_score,
            'paragraph_variation': paragraph_score,
        }

        # Score final ponderado
        final_score = sum(scores[k] * weights[k] for k in scores)

        # Gerar warns e sugestões
        if sentence_score < 50:
            self.warnings.append("Comprimento de frases excessivamente uniforme")
            self.suggestions.append("Variar estrutura sintática: misturar frases curtas e longas")

        if connective_score < 50:
            self.warnings.append("Uso excessivo de conectivos genéricos")
            self.suggestions.append("Substituir conectivos genéricos por linguagem mais específica")

        if voice_score < 50:
            self.warnings.append("Baixa presença de voz autoral")
            self.suggestions.append("Inserir posicionamento pessoal do pesquisador")

        if example_score < 50:
            self.warnings.append("Poucos exemplos concretos")
            self.suggestions.append("Adicionar exemplos específicos do contexto brasileiro")

        if paragraph_score < 50:
            self.warnings.append("Parágrafos de comprimento muito uniforme")
            self.suggestions.append("Variar tamanho dos parágrafos")

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
    parser = argparse.ArgumentParser(description='Anti-AI Scanner')
    parser.add_argument('--input', '-i', required=True, help='Arquivo .tex para analisar')
    parser.add_argument('--json', '-j', action='store_true', help='Saída em JSON')
    args = parser.parse_args()

    scanner = AntiAIScanner()
    scanner.load_text(args.input)
    result = scanner.scan()

    if args.json:
        print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    else:
        print(f"=== Anti-AI Scanner v1.0 ===")
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
