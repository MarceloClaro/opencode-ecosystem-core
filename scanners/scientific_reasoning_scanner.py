# -*- coding: utf-8 -*-
"""Triagem lexical científica PT/EN (R223, corrigida em R815).

Os scores e rótulos legados são indicadores de vocabulário, sem validação de
qualidade científica, testabilidade real, risco de viés ou validade clínica.
"""
from __future__ import annotations

import re
import unicodedata
from bisect import bisect_left, bisect_right
from typing import Any, Dict


class _TextContext:
    """Indexa uma vez e consulta no máximo oito palavras antes/sete depois."""

    def __init__(self, text: str, clause_boundary: re.Pattern, additive: re.Pattern):
        self.text = text
        boundaries = list(clause_boundary.finditer(text))
        self.clause_starts = [match.start() for match in boundaries]
        self.clause_ends = [match.end() for match in boundaries]
        # Manter posições permite excluir 'não apenas/not only' dos tokens sem
        # deslocar os offsets dos aliases nem varrer a frase em cada ocorrência.
        masked = additive.sub(lambda match: " " * len(match.group()), text)
        words = list(re.finditer(r"\w+", masked))
        self.word_starts = [match.start() for match in words]
        self.word_ends = [match.end() for match in words]
        self.words = [match.group() for match in words]
        self.commas = [match.start() for match in re.finditer(",", text)]
        self.newlines = [match.start() for match in re.finditer("\n", text)]
        self.line_starts = [0, *(offset + 1 for offset in self.newlines)]
        self.headings = []
        for start, end in zip(self.line_starts, [*self.newlines, len(text)]):
            line = text[start:end]
            stripped = line.lstrip()
            first = start + len(line) - len(stripped)
            kind = "hash" if stripped.startswith("#") else "bold" if stripped.startswith("**") else "body"
            closing = text.find("**", first + 2) if kind == "bold" else -1
            self.headings.append((first, kind, closing))

    def is_heading(self, match: re.Match) -> bool:
        line_index = bisect_right(self.newlines, match.start() - 1)
        first, kind, closing = self.headings[line_index]
        if kind == "hash":
            return True
        end_index = bisect_left(self.newlines, match.end())
        line_end = self.newlines[end_index] if end_index < len(self.newlines) else len(self.text)
        return kind == "bold" and first < match.start() and closing >= match.end() and closing + 2 <= line_end

    def prefix(self, match: re.Match) -> str:
        boundary_index = bisect_right(self.clause_ends, match.start())
        clause_start = self.clause_ends[boundary_index - 1] if boundary_index else 0
        end = bisect_right(self.word_ends, match.start())
        start = max(end - 8, bisect_left(self.word_starts, clause_start))
        return " ".join(self.words[start:end])

    def suffix(self, match: re.Match) -> str:
        boundary_index = bisect_left(self.clause_starts, match.end())
        clause_end = self.clause_starts[boundary_index] if boundary_index < len(self.clause_starts) else len(self.text)
        comma_index = bisect_left(self.commas, match.end())
        if comma_index < len(self.commas):
            clause_end = min(clause_end, self.commas[comma_index])
        start = bisect_left(self.word_starts, match.end())
        end = min(start + 7, bisect_right(self.word_ends, clause_end))
        return " ".join(self.words[start:end])


class ScientificReasoningScanner:
    """Detecta conceitos e gatilhos textuais para orientar revisão humana."""

    FALSIFIABILITY_GROUPS = {
        "hypothesis": ("hipótese", "hipóteses", "hypothesis", "hypotheses"),
        "condition": ("se", "caso", "quando", "dado que", "if", "when", "provided that"),
        "prediction": ("então", "resulta", "impacta", "aumenta", "reduz", "then", "results", "increases", "reduces", "decreases"),
        "falsification": ("falsificável", "falsificabilidade", "invalidação", "refutação", "falsifiable", "falsifiability", "invalidation", "refutation"),
        "empirical_test": ("teste", "testes", "testável", "testáveis", "experimento", "experimentos", "test", "tests", "testing", "testable", "experiment", "experiments"),
        "measurement": ("métrica", "métricas", "mensurável", "mensuração", "metric", "metrics", "measurable", "measurement"),
    }
    METHODOLOGY_GROUPS = {
        "design": ("grupo de controle", "grupo controle", "grupos de controle", "control group", "control groups", "cego", "duplo-cego", "mascaramento", "blinded", "double-blind", "masking", "randomização", "randomisation", "randomization"),
        "sampling": ("amostragem", "sampling"),
        "uncertainty": ("p-valor", "p-value", "p value", "intervalo de confiança", "intervalos de confiança", "confidence interval", "confidence intervals"),
        "variables": ("variável independente", "variável dependente", "independent variable", "dependent variable", "preditor", "preditores", "predictor", "predictors", "desfecho", "desfechos", "outcome", "outcomes"),
        "baseline": ("baseline", "linha de base", "modelo de prevalência", "prevalence model"),
        "reproducibility": ("reprodutibilidade", "reproducibility", "reproduzido", "reproduced"),
    }
    # Atributos públicos legados: agora aliases PT/EN, sem contar aliases duplicados.
    FALSIFIABILITY_KEYWORDS = [
        alias for aliases in FALSIFIABILITY_GROUPS.values() for alias in aliases
    ]
    METHODOLOGY_KEYWORDS = [
        alias for aliases in METHODOLOGY_GROUPS.values() for alias in aliases
    ]
    FALLACY_TRIGGERS = [
        (r"\bprova que\b", "Afirmação categórica de prova absoluta sem margem de incerteza estatística"),
        (r"\bcorrelação implica\b", "Inclusão indevida de correlação como se fosse causalidade direta"),
        (r"\bsempre funciona\b", "Viés de generalização precipitada sem escopo restrito"),
        (r"\bobviamente\b", "Assunção não justificada sem citação empírica"),
    ]
    _FALLACY_PATTERNS = (
        r"\b(?:prova que|proves that|prove that)\b",
        r"\b(?:correlacao implica|correlation implies)\b",
        r"\b(?:sempre funciona|always works)\b",
        r"\b(?:obviamente|obviously)\b",
    )
    _CLAUSE_BOUNDARY = re.compile(
        r"[.!?;\n]|\b(?:mas|porem|contudo|but|however|yet)\b"
    )
    _NEGATION_BEFORE = re.compile(
        r"\b(?:nao|nenhum|nenhuma|nenhuns|nenhumas|sem|nem|no|not|without|never|neither|nor)\b"
    )
    _ADDITIVE = re.compile(r"\b(?:nao (?:apenas|somente|so)|not (?:only|just))\b")
    _NEGATION_AFTER = re.compile(
        r"^(?:(?:\w+\s+){0,4})?(?:nao|nem|not|never|neither|nor)\b|"
        r"^(?:ausente|inexistente|indisponivel|absent|unavailable|undocumented)\b"
    )
    LIMITATIONS = [
        "Scores e status são faixas de uma heurística lexical; não medem qualidade científica nem validade clínica.",
        "Negação local, aliases e gatilhos não interpretam todo o contexto, citações, desenhos de estudo ou evidências.",
        "A ausência de gatilhos não demonstra ausência de falácias; a presença de termos não demonstra execução dos métodos.",
        "Esta triagem não realiza PROBAST+AI e não substitui avaliação estruturada de risco de viés e revisão humana.",
    ]

    @staticmethod
    def _normalize(text: str) -> str:
        if not isinstance(text, str):
            raise ValueError("O texto deve ser uma string.")
        folded = unicodedata.normalize("NFKD", text.casefold())
        folded = "".join(char for char in folded if not unicodedata.combining(char))
        return folded.translate(str.maketrans({"–": "-", "—": "-", "−": "-", "‑": "-"}))

    @classmethod
    def _alias_pattern(cls, aliases: tuple[str, ...]) -> re.Pattern:
        choices = sorted(
            (re.escape(cls._normalize(alias)).replace(r"\ ", r"\s+") for alias in aliases),
            key=len, reverse=True,
        )
        return re.compile(r"(?<!\w)(?:" + "|".join(choices) + r")(?!\w)")

    @classmethod
    def _is_heading(cls, text: str, match: re.Match, context: _TextContext | None = None) -> bool:
        context = context or _TextContext(text, cls._CLAUSE_BOUNDARY, cls._ADDITIVE)
        return context.is_heading(match)

    @classmethod
    def _negated(cls, text: str, match: re.Match, *, check_suffix: bool = True,
                 context: _TextContext | None = None) -> bool:
        context = context or _TextContext(text, cls._CLAUSE_BOUNDARY, cls._ADDITIVE)
        if cls._NEGATION_BEFORE.search(context.prefix(match)):
            return True
        if check_suffix:
            return bool(cls._NEGATION_AFTER.search(context.suffix(match)))
        return False

    @classmethod
    def _concepts(cls, text: str, groups: dict,
                  context: _TextContext | None = None) -> tuple[list[str], list[str]]:
        context = context or _TextContext(text, cls._CLAUSE_BOUNDARY, cls._ADDITIVE)
        affirmative, negated = [], []
        for concept, aliases in groups.items():
            has_positive = has_negative = False
            for match in cls._alias_pattern(aliases).finditer(text):
                if cls._is_heading(text, match, context):
                    continue
                # Condição/previsão representam estrutura textual: uma premissa
                # negativa continua podendo formar uma previsão condicional.
                if concept not in {"condition", "prediction"} and cls._negated(text, match, context=context):
                    has_negative = True
                else:
                    has_positive = True
            if has_positive:
                affirmative.append(concept)
            if has_negative:
                negated.append(concept)
        return affirmative, negated

    def scan_text(self, text: str) -> Dict[str, Any]:
        """Retorna cobertura lexical normalizada, gatilhos e limites explícitos."""
        normalized = self._normalize(text)
        context = _TextContext(normalized, self._CLAUSE_BOUNDARY, self._ADDITIVE)
        falsifiability, false_negated = self._concepts(normalized, self.FALSIFIABILITY_GROUPS, context)
        methodology, method_negated = self._concepts(normalized, self.METHODOLOGY_GROUPS, context)
        falsifiability_norm = round(100 * len(falsifiability) / len(self.FALSIFIABILITY_GROUPS), 2)
        methodology_norm = round(100 * len(methodology) / len(self.METHODOLOGY_GROUPS), 2)

        detected_fallacies = []
        for (legacy_pattern, description), pattern in zip(self.FALLACY_TRIGGERS, self._FALLACY_PATTERNS):
            if any(
                not self._negated(normalized, match, check_suffix=False, context=context)
                and not self._is_heading(normalized, match, context)
                for match in re.finditer(pattern, normalized)
            ):
                detected_fallacies.append({"pattern": legacy_pattern, "description": description})

        raw_sri = falsifiability_norm * 0.4 + methodology_norm * 0.6 - len(detected_fallacies) * 15
        sri = round(max(0.0, min(100.0, raw_sri)), 2)
        recommendations = []
        if falsifiability_norm < 50:
            recommendations.append("Explicite hipótese, previsão mensurável e critérios de refutação quando pertinentes ao objetivo.")
        if methodology_norm < 50:
            recommendations.append("Descreva os métodos e suas limitações conforme o desenho do estudo; controle e amostragem dependem desse desenho.")
        if detected_fallacies:
            recommendations.append("Revise os gatilhos categóricos no contexto e fundamente as alegações com evidências e incertezas.")
        recommendations.append("Confirme a execução e a adequação dos métodos por revisão humana; a cobertura lexical não atesta rigor.")
        return {
            "sri_score": sri,
            "falsifiability_score": falsifiability_norm,
            "methodology_score": methodology_norm,
            "detected_fallacies": detected_fallacies,
            "recommendations": recommendations,
            "status": "high_rigor" if sri >= 70 else ("moderate_rigor" if sri >= 40 else "low_rigor"),
            "score_kind": "lexical_heuristic",
            "score_version": "R815",
            "scientific_quality_assessed": False,
            "risk_of_bias_assessed": False,
            "matched_concepts": {"falsifiability": falsifiability, "methodology": methodology},
            "negated_concepts": {"falsifiability": false_negated, "methodology": method_negated},
            "limitations": list(self.LIMITATIONS),
        }

    def evaluate_hypothesis(self, hypothesis: str) -> Dict[str, Any]:
        """O campo legado is_testable indica somente condição e previsão textuais."""
        scan = self.scan_text(hypothesis)
        concepts = scan["matched_concepts"]["falsifiability"]
        is_testable = "condition" in concepts and "prediction" in concepts
        return {
            "hypothesis": hypothesis,
            "is_testable": is_testable,
            "rigor_score": scan["sri_score"],
            "status": "valid_hypothesis" if is_testable else "needs_refinement",
            "score_kind": "lexical_heuristic",
            "scientific_quality_assessed": False,
            "limitations": list(self.LIMITATIONS),
        }


scientific_reasoning_scanner = ScientificReasoningScanner()
