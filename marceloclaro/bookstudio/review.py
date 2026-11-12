"""Gate literário R1111: regras nativas PT-BR + LanguageTool local.

Nenhum achado aqui aprova o texto. O relatório sempre exige revisão humana e
declara que regras heurísticas produzem falsos positivos.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
import json
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


class ReviewError(ValueError):
    """Erro de leitura ou de relatório de revisão."""


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    message: str
    excerpt: str
    start: int
    end: int
    confidence: float
    source: str = "native"
    suggestions: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["suggestions"] = list(self.suggestions)
        return data


MULETAS = (
    "basicamente", "literalmente", "realmente", "simplesmente", "obviamente",
    "claramente", "extremamente", "absolutamente", "definitivamente",
    "particularmente", "especialmente", "praticamente", "virtualmente",
    "efetivamente", "certamente", "possivelmente", "provavelmente",
    "na verdade", "de certa forma", "de alguma forma", "por assim dizer",
    "no final do dia", "tipo assim", "meio que", "sem dúvida", "com certeza",
    "cada vez mais", "de certo modo", "de algum modo",
)

CLICHES = (
    "coração disparou", "lágrimas rolaram", "frio na barriga",
    "nó na garganta", "mundo desabou", "tempo parou",
    "silêncio ensurdecedor", "suspiro profundo", "olhar penetrante",
    "sorriso amarelo", "arrepio na espinha", "sangue gelou",
    "queria que a terra se abrisse", "respirou fundo",
)

STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da",
    "dos", "das", "em", "no", "na", "nos", "nas", "por", "para", "com",
    "sem", "que", "e", "ou", "mas", "se", "ao", "aos", "à", "às", "é",
    "foi", "era", "ser", "são", "como", "mais", "menos", "muito", "muita",
    "muitos", "muitas", "seu", "sua", "seus", "suas", "ele", "ela", "eles",
    "elas", "eu", "tu", "você", "nós", "vós", "lhe", "lhes", "me", "te",
    "nos", "vos", "já", "não", "sim", "também", "só", "quando", "onde",
    "porque", "então", "assim", "depois", "antes", "entre", "sobre",
}

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:['’-][A-Za-zÀ-ÖØ-öø-ÿ]+)*")


def _excerpt(text: str, start: int, end: int, width: int = 50) -> str:
    left = max(0, start - width)
    right = min(len(text), end + width)
    snippet = re.sub(r"\s+", " ", text[left:right]).strip()
    return snippet[:180]


def _finding(text: str, rule: str, severity: str, message: str,
             start: int, end: int, confidence: float,
             suggestions: Sequence[str] = ()) -> Finding:
    return Finding(rule=rule, severity=severity, message=message,
                   excerpt=_excerpt(text, start, end), start=start, end=end,
                   confidence=confidence, suggestions=tuple(suggestions))


def _iter_matches(pattern: re.Pattern[str], text: str) -> Iterable[re.Match[str]]:
    return pattern.finditer(text)


def native_review(text: str) -> List[Finding]:
    """Regras determinísticas PT-BR. Não julga mérito literário."""
    if not isinstance(text, str):
        raise ReviewError("texto deve ser string")
    findings: List[Finding] = []

    for match in _iter_matches(re.compile(r'"'), text):
        findings.append(_finding(text, "aspas_retas", "warning",
                                 "Aspas retas em prosa; usar aspas tipográficas “ ”.",
                                 match.start(), match.end(), 0.95, ("“", "”")))
    for match in _iter_matches(re.compile(r"\.\.\."), text):
        findings.append(_finding(text, "reticencias", "warning",
                                 "Reticências como três pontos; usar o caractere …",
                                 match.start(), match.end(), 0.9, ("…",)))
    for match in _iter_matches(re.compile(r"(?m)^\s*(?:--?|—)\s+"), text):
        findings.append(_finding(text, "travessao_dialogo", "info",
                                 "Diálogo com travessão; confirmar o padrão — e o espaço.",
                                 match.start(), match.end(), 0.5, ("— ",)))
    for match in _iter_matches(re.compile(r"--"), text):
        findings.append(_finding(text, "travessao_duplo", "warning",
                                 "Dois hífens no lugar de travessão —.",
                                 match.start(), match.end(), 0.8, ("—",)))
    for match in _iter_matches(re.compile(r"\s+[,.;:!?]"), text):
        findings.append(_finding(text, "espaco_antes_pontuacao", "warning",
                                 "Espaço antes de pontuação.",
                                 match.start(), match.end(), 0.95))
    for match in _iter_matches(re.compile(r"\S {2,}\S"), text):
        findings.append(_finding(text, "duplo_espaco", "info",
                                 "Espaço duplo no meio da frase.",
                                 match.start(), match.end(), 0.8))
    for match in _iter_matches(re.compile(r"(?m)^\s*—[A-ZÀ-Ý]"), text):
        findings.append(_finding(text, "travessao_sem_espaco", "info",
                                 "Travessão de diálogo sem espaço depois.",
                                 match.start(), match.end(), 0.6, ("— ",)))

    lowered = text.casefold()
    for phrase in MULETAS:
        for match in re.finditer(re.escape(phrase), lowered):
            findings.append(_finding(text, "muleta", "info",
                                     f"Muleta de estilo: “{phrase}”.",
                                     match.start(), match.end(), 0.6))
    for phrase in CLICHES:
        for match in re.finditer(re.escape(phrase), lowered):
            findings.append(_finding(text, "cliche", "warning",
                                     f"Clichê: “{phrase}”.",
                                     match.start(), match.end(), 0.7))

    sentences = [s.strip() for s in SENTENCE_SPLIT.split(text) if s.strip()]
    for sentence in sentences:
        words = WORD_RE.findall(sentence)
        if len(words) > 45:
            start = text.find(sentence)
            findings.append(_finding(text, "frase_longa", "warning",
                                     f"Frase com {len(words)} palavras; considerar dividir.",
                                     max(0, start), max(0, start) + len(sentence), 0.6))
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    for paragraph in paragraphs:
        words = WORD_RE.findall(paragraph)
        if len(words) > 180:
            start = text.find(paragraph)
            findings.append(_finding(text, "paragrafo_longo", "info",
                                     f"Parágrafo com {len(words)} palavras.",
                                     max(0, start), max(0, start) + len(paragraph), 0.5))

    tokens = [(m.group(0).casefold(), m.start(), m.end())
              for m in WORD_RE.finditer(text)]
    recent: Dict[str, int] = {}
    for index, (word, start, end) in enumerate(tokens):
        if len(word) < 4 or word in STOPWORDS:
            continue
        previous = recent.get(word)
        if previous is not None and index - previous <= 12:
            findings.append(_finding(text, "repeticao_proxima", "info",
                                     f"“{word}” repetido em até 12 palavras.",
                                     start, end, 0.45))
        recent[word] = index

    adverbs = [m for m in WORD_RE.finditer(text) if m.group(0).casefold().endswith("mente")]
    if len(adverbs) > max(8, len(tokens) // 40):
        findings.append(_finding(text, "excesso_adverbios", "info",
                                 f"{len(adverbs)} advérbios em -mente; revisar densidade.",
                                 0, 0, 0.5))

    open_quotes = text.count("“")
    close_quotes = text.count("”")
    if open_quotes != close_quotes:
        findings.append(_finding(text, "aspas_desbalanceadas", "warning",
                                 f"Aspas tipográficas desbalanceadas: {open_quotes} “ e {close_quotes} ”.",
                                 0, 0, 0.9))
    return findings


def _lt_severity(issue_type: str) -> str:
    issue = (issue_type or "").casefold()
    if issue in {"misspelling", "grammar", "typography"}:
        return "error" if issue in {"misspelling", "grammar"} else "warning"
    if issue in {"style", "locale-violation", "register"}:
        return "info"
    return "info"


def check_languagetool(text: str, *, endpoint: str = "http://127.0.0.1:8081/v2/check",
                       language: str = "pt-BR", timeout: float = 20.0,
                       max_findings: int = 200) -> Dict[str, Any]:
    """Consulta um servidor LanguageTool local. Indisponibilidade é declarada."""
    if not isinstance(text, str):
        raise ReviewError("texto deve ser string")
    if not endpoint.startswith(("http://127.0.0.1", "http://localhost", "https://")):
        raise ReviewError("endpoint LanguageTool deve ser local ou HTTPS")
    payload = urllib.parse.urlencode({"language": language, "text": text}).encode("utf-8")
    request = urllib.request.Request(
        endpoint, data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        return {"available": False, "error": type(exc).__name__,
                "detail": str(exc)[:200], "findings": []}
    findings: List[Finding] = []
    for match in data.get("matches", [])[:max_findings]:
        offset = int(match.get("offset", 0))
        length = int(match.get("length", 0))
        rule = match.get("rule") or {}
        message = match.get("message") or "Achado LanguageTool"
        issue_type = rule.get("issueType", "style")
        replacements = [r.get("value", "") for r in match.get("replacements", [])[:5]]
        findings.append(Finding(
            rule=f"languagetool:{rule.get('id', '?')}",
            severity=_lt_severity(issue_type),
            message=message[:300],
            excerpt=_excerpt(text, offset, offset + length),
            start=offset, end=offset + length, confidence=0.9,
            source="languagetool", suggestions=tuple(str(r) for r in replacements)))
    language_info = data.get("language") or {}
    return {"available": True, "language": language_info.get("name"),
            "version": data.get("software", {}).get("version"),
            "findings": findings}


def _metrics(text: str) -> Dict[str, Any]:
    words = WORD_RE.findall(text)
    sentences = [s for s in SENTENCE_SPLIT.split(text) if s.strip()]
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    unique = {w.casefold() for w in words}
    return {
        "chars": len(text), "words": len(words), "sentences": len(sentences),
        "paragraphs": len(paragraphs),
        "avg_sentence_words": round(len(words) / len(sentences), 2) if sentences else 0,
        "avg_word_chars": round(sum(len(w) for w in words) / len(words), 2) if words else 0,
        "lexical_diversity": round(len(unique) / len(words), 3) if words else 0,
    }


def review_text(text: str, *, use_languagetool: bool = False,
                endpoint: str = "http://127.0.0.1:8081/v2/check",
                language: str = "pt-BR") -> Dict[str, Any]:
    """Relatório completo; nunca aprova, sempre pede revisão humana."""
    if not isinstance(text, str) or not text.strip():
        raise ReviewError("texto vazio")
    native = native_review(text)
    lt: Dict[str, Any] = {"available": False, "error": "not_requested", "findings": []}
    if use_languagetool:
        lt = check_languagetool(text, endpoint=endpoint, language=language)
    all_findings = [f.to_dict() for f in native] + [f.to_dict() for f in lt["findings"]]
    severity_order = {"error": 0, "warning": 1, "info": 2}
    all_findings.sort(key=lambda item: (severity_order.get(item["severity"], 3),
                                        item.get("start", 0)))
    counts = {level: sum(1 for f in all_findings if f["severity"] == level)
              for level in ("error", "warning", "info")}
    return {
        "status": "completed",
        "human_review_required": True,
        "external_validation": False,
        "metrics": _metrics(text),
        "counts": counts,
        "findings": all_findings[:400],
        "languagetool": {
            "requested": use_languagetool,
            "available": lt.get("available", False),
            "version": lt.get("version"),
            "error": lt.get("error"),
        },
        "limitations": [
            "Regras heurísticas produzem falsos positivos e falsos negativos.",
            "O gate não avalia voz, ritmo, verossimilhança ou mérito literário.",
            "LanguageTool é externo e pode não estar disponível.",
            "Nenhum resultado constitui aprovação editorial ou revisão humana.",
        ],
    }


def review_file(path: str | Path, *, use_languagetool: bool = False,
                endpoint: str = "http://127.0.0.1:8081/v2/check",
                language: str = "pt-BR") -> Dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_file():
        raise ReviewError(f"texto ausente: {file_path}")
    text = file_path.read_text(encoding="utf-8", errors="replace")
    report = review_text(text, use_languagetool=use_languagetool,
                         endpoint=endpoint, language=language)
    report["file"] = str(file_path)
    return report
