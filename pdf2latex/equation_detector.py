"""
Detecção de equações matemáticas em texto extraído de PDF.
Converte notações para math mode LaTeX.
"""

import re
from typing import List, Tuple


class EquationDetector:
    """Detecta e converte equações matemáticas para LaTeX."""

    # Padrões para detecção de equações
    EQUATION_PATTERNS = [
        # $$ ... $$
        (re.compile(r'\$\$(.+?)\$\$', re.DOTALL), 'display'),
        # \[ ... \]
        (re.compile(r'\\\[(.+?)\\\]', re.DOTALL), 'display'),
        # \( ... \)
        (re.compile(r'\\\((.+?)\\\)', re.DOTALL), 'inline'),
        # $...$ (cuidado para não capturar cifrões)
        (re.compile(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', re.DOTALL), 'inline'),
        # \begin{equation} ... \end{equation}
        (re.compile(r'\\begin\{equation\}(.+?)\\end\{equation\}', re.DOTALL), 'numbered'),
        # \begin{align} ... \end{align}
        (re.compile(r'\\begin\{align\}(.+?)\\end\{align\}', re.DOTALL), 'numbered'),
        # \begin{eqnarray} ... \end{eqnarray}
        (re.compile(r'\\begin\{eqnarray\}(.+?)\\end\{eqnarray\}', re.DOTALL), 'numbered'),
    ]

    # Padrões heurísticos para detectar equações em texto não-LaTeX
    HEURISTIC_PATTERNS = [
        re.compile(r'^[α-ωΑ-Ωa-zA-Z\s]+\s*=\s*[α-ωΑ-Ωa-zA-Z0-9\s+\-*/^_(){}\[\]]+$'),
        re.compile(r'^\s*[\\∫∑∏√∂∆∞∅∈⊂⊃∪∩∧∨¬⇒⇔∀∃]'),
        re.compile(r'\b\d+\s*[+\-*/×÷]\s*\d+\s*=\s*\d+'),
        re.compile(r'[a-zA-Z]\s*\^\s*\{\d+\}'),
        re.compile(r'\\frac\{[^}]*\}\{[^}]*\}'),
        re.compile(r'\\sqrt\{[^}]*\}'),
        re.compile(r'\\sum_\{[^}]*\}\^\{[^}]*\}'),
        re.compile(r'\\int_\{[^}]*\}\^\{[^}]*\}'),
    ]

    def __init__(self, text: str):
        self.text = text

    def detect(self) -> List[Tuple[str, int]]:
        """
        Detecta equações no texto.
        Retorna: [(codigo_latex_equation, numero_estimado_pagina), ...]
        """
        equations = []

        # 1. Extrair equações LaTeX explícitas
        for pattern, style in self.EQUATION_PATTERNS:
            for match in pattern.finditer(self.text):
                eq_content = match.group(1).strip()
                if len(eq_content) > 5:  # Ignorar falsos positivos muito curtos
                    if style == 'display':
                        latex_eq = f"\\begin{{equation}}\n{eq_content}\n\\end{{equation}}"
                    elif style == 'inline':
                        latex_eq = f"${eq_content}$"
                    elif style == 'numbered':
                        latex_eq = match.group(0)
                    else:
                        latex_eq = match.group(0)
                    equations.append((latex_eq, 0))

        # 2. Detectar equações por heurística (texto não-LaTeX)
        lines = self.text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            for heuristic in self.HEURISTIC_PATTERNS:
                if heuristic.search(line) and len(line) > 10:
                    # Estimar página (cada ~40 linhas = 1 página)
                    pagina = i // 40 + 1
                    latex_eq = self._convert_to_latex(line)
                    if latex_eq not in [e[0] for e in equations]:
                        equations.append((latex_eq, pagina))
                    break

        # 3. Normalizar: remover duplicatas próximas
        unique_eqs = []
        seen = set()
        for eq, page in equations:
            # Usar hash do conteúdo normalizado
            normalized = re.sub(r'\s+', ' ', eq)[:100]
            if normalized not in seen:
                seen.add(normalized)
                unique_eqs.append((eq, page))

        return unique_eqs

    def _convert_to_latex(self, text: str) -> str:
        """Converte expressão matemática textual para LaTeX."""
        # Se já parece LaTeX, retornar como display
        if '\\' in text or '{' in text:
            return f"\\begin{{equation}}\n{text}\n\\end{{equation}}"

        # Caso contrário, tentar converter símbolos comuns
        replacements = {
            'α': r'\\alpha', 'β': r'\\beta', 'γ': r'\\gamma',
            'δ': r'\\delta', 'ε': r'\\epsilon', 'θ': r'\\theta',
            'λ': r'\\lambda', 'μ': r'\\mu', 'π': r'\\pi',
            'σ': r'\\sigma', 'τ': r'\\tau', 'ω': r'\\omega',
            '∑': r'\\sum', '∫': r'\\int', '√': r'\\sqrt',
            '∞': r'\\infty', '∂': r'\\partial', '∆': r'\\Delta',
            '→': r'\\rightarrow', '⇒': r'\\Rightarrow',
            '∈': r'\\in', '⊂': r'\\subset', '∪': r'\\cup',
            '∩': r'\\cap', '∀': r'\\forall', '∃': r'\\exists',
            '×': r'\\times', '÷': r'\\div',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)

        return f"\\begin{{equation}}\n{text}\n\\end{{equation}}"
