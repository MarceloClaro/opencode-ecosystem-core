# -*- coding: utf-8 -*-
"""Andaimes de raciocínio produtivo científico-literário — SPEC-935-R369.

Ponte contratual entre os motores de raciocínio (SPEC-917 / ARCHE) e a
produção de artigos, teses, dissertações e obras literárias:

- andaime científico: movimentos de raciocínio obrigatórios auditáveis;
- auditoria de novidade: alegações de ineditismo exigem ancoradouro de
  comparação/citação na mesma frase — novidade se argumenta, não se decreta;
- plano literário contratual: voz, conflito, símbolos e estranhamento
  explícitos antes da escrita;
- relatório de distintividade literária: números descritivos, nunca
  veredito de qualidade ou "disrupção".

Limite epistêmico: nenhuma função deste módulo atesta relevância
científica nem valor literário; elas verificam estrutura argumentativa
observável e medem características textuais. Decisões finais são humanas.
"""

from __future__ import annotations

import copy
import re
import statistics
import unicodedata
from typing import Any, Dict, List, Mapping, Optional


class ContractError(ValueError):
    """Entrada fora do contrato — falha fechada."""


# ═══════════════════════════════════════════════════════════════════════
# Andaime científico
# ═══════════════════════════════════════════════════════════════════════

SCIENTIFIC_MOVES: Dict[str, Dict[str, Any]] = {
    "problema": {
        "severity_if_missing": "medium",
        "engine_hints": ["critical"],
        "markers": [
            "problema", "problem", "questao de pesquisa", "research question",
        ],
    },
    "lacuna": {
        "severity_if_missing": "medium",
        "engine_hints": ["abducao", "critical"],
        "markers": [
            "lacuna", "gap", "nao ha estudos", "pouco explorado",
            "understudied", "remains open",
        ],
    },
    "hipotese": {
        "severity_if_missing": "medium",
        "engine_hints": ["abducao", "bayesian"],
        "markers": ["hipotese", "hypothesis", "h1", "h2", "conjectura", "conjecture"],
    },
    "metodo": {
        "severity_if_missing": "high",
        "engine_hints": ["deducao", "causal"],
        "markers": [
            "metodo", "metodologia", "method", "methodology", "procedimento",
            "procedure", "amostra", "sample", "protocolo", "protocol",
        ],
    },
    "evidencia": {
        "severity_if_missing": "high",
        "engine_hints": ["inducao", "bayesian"],
        "markers": [
            "resultados", "results", "evidencia", "evidence", "tabela",
            "table", "p <", "p<", "intervalo de confianca", "confidence interval",
        ],
    },
    "contra_argumento": {
        "severity_if_missing": "medium",
        "engine_hints": ["contrafactual", "critical"],
        "markers": [
            "contra-argumento", "counterargument", "entretanto", "however",
            "alternativa", "alternative", "por outro lado", "on the other hand",
        ],
    },
    "limitacao": {
        "severity_if_missing": "high",
        "engine_hints": ["critical"],
        "markers": [
            "limitacao", "limitacoes", "limitation", "limitations",
            "ameacas a validade", "threats to validity",
        ],
    },
    "contribuicao": {
        "severity_if_missing": "medium",
        "engine_hints": ["analogia"],
        "markers": [
            "contribuicao", "contribution", "implicacoes", "implications",
        ],
    },
}

_NOVELTY_TERMS = (
    "inedito", "inedita", "inovador", "inovadora", "pioneiro", "pioneira",
    "primeiro", "primeira", "novel", "unprecedented", "state-of-the-art",
    "disruptivo", "disruptiva",
)

_ANCHOR_PATTERNS = (
    re.compile(r"\\cite\{[^}]+\}"),
    re.compile(r"\[\d+\]"),
    re.compile(r"\([A-ZÀ-Ü][A-Za-zÀ-ü&\-. ]+,\s*\d{4}\)"),
)
_ANCHOR_PHRASES = (
    "em comparacao", "comparado com", "comparada com", "diferente de",
    "ao contrario de", "compared to", "compared with", "unlike",
    "in contrast to", "em contraste com",
)

DISCLAIMER_CIENTIFICO = (
    "A presença dos movimentos de raciocínio não atesta relevância, rigor "
    "nem novidade científica: atesta apenas estrutura argumentativa "
    "observável. Mérito é julgamento humano e de pares."
)


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _finding(code: str, severity: str, detail: str, move: Optional[str] = None) -> Dict[str, Any]:
    item = {
        "code": code,
        "severity": severity,
        "detail": detail,
        "requires_human_review": True,
    }
    if move is not None:
        item["move"] = move
    return item


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?…])\s+", text.strip())
    return [p for p in parts if p.strip()]


def audit_scientific_manuscript(sections: Mapping[str, str]) -> Dict[str, Any]:
    """Audita movimentos de raciocínio e alegações de novidade. Determinístico."""
    if not isinstance(sections, Mapping) or not sections:
        raise ContractError("sections deve ser mapeamento não vazio {secao: texto}.")
    for name, text in sections.items():
        if not isinstance(text, str):
            raise ContractError(f"seção {name!r} deve conter texto.")

    full_norm = _normalize(" \n ".join(sections.values()))
    findings: List[Dict[str, Any]] = []
    moves_presentes: List[str] = []

    for move, spec in SCIENTIFIC_MOVES.items():
        present = any(marker in full_norm for marker in spec["markers"])
        if present:
            moves_presentes.append(move)
        else:
            findings.append(_finding(
                "MISSING_MOVE", spec["severity_if_missing"],
                f"nenhum marcador do movimento {move!r} encontrado",
                move=move,
            ))

    # auditoria de novidade: frase a frase
    for name, text in sections.items():
        for sentence in _split_sentences(text):
            norm = _normalize(sentence)
            claimed = [t for t in _NOVELTY_TERMS if t in norm]
            if not claimed:
                continue
            anchored = (
                any(p.search(sentence) for p in _ANCHOR_PATTERNS)
                or any(phrase in norm for phrase in _ANCHOR_PHRASES)
            )
            if not anchored:
                findings.append(_finding(
                    "UNSUPPORTED_NOVELTY_CLAIM", "high",
                    f"seção {name!r}: alegação de novidade "
                    f"({', '.join(claimed)}) sem citação ou comparação na "
                    f"mesma frase: {sentence.strip()[:120]!r}",
                ))

    high = any(f["severity"] == "high" for f in findings)
    return {
        "schema_version": "1.0.0",
        "scaffold": "scientific",
        "moves_presentes": moves_presentes,
        "findings": findings,
        "human_gate": "required" if high else "recommended",
        "disclaimer": DISCLAIMER_CIENTIFICO,
    }


# ═══════════════════════════════════════════════════════════════════════
# Andaime literário
# ═══════════════════════════════════════════════════════════════════════

LITERARY_PLAN_FIELDS = (
    "voz", "conflito_central", "simbolos",
    "estrategia_estranhamento", "cliches_a_evitar",
)


def validate_literary_plan(plan: Mapping[str, Any]) -> Dict[str, Any]:
    """Plano de obra contratual: raciocínio literário explícito antes da escrita."""
    if not isinstance(plan, Mapping):
        raise ContractError("plano deve ser um mapeamento.")
    validated = copy.deepcopy(dict(plan))
    missing = [f for f in LITERARY_PLAN_FIELDS if f not in validated]
    if missing:
        raise ContractError(f"plano sem: {', '.join(missing)}.")
    for field in ("voz", "conflito_central", "estrategia_estranhamento"):
        value = validated[field]
        if not isinstance(value, str) or not value.strip():
            raise ContractError(f"{field} deve ser texto não vazio.")
        validated[field] = value.strip()
    simbolos = validated["simbolos"]
    if not isinstance(simbolos, list) or not simbolos:
        raise ContractError("simbolos deve ser lista não vazia.")
    if not isinstance(validated["cliches_a_evitar"], list):
        raise ContractError("cliches_a_evitar deve ser lista.")
    return validated


# Léxico curado de clichês pt (expressões desgastadas; lista aberta)
CLICHE_LEXICON = (
    "frio na espinha", "silencio ensurdecedor", "lagrimas amargas",
    "coracao partido", "olhos marejados", "sorriso maroto",
    "mar de lagrimas", "no fundo do coracao", "suor frio",
    "noite escura", "medo palpavel", "silencio mortal",
    "olhar penetrante", "beleza estonteante", "dor lancinante",
    "grito preso na garganta", "sangue gelou", "mundo desabou",
    "vazio no peito", "no de dor na garganta", "chorar copiosamente",
    "tremer como vara verde",
)

_STOPWORDS = frozenset(
    "a o e de da do das dos em na no nas nos um uma que se com por para "
    "as os ao aos sua seu suas seus ela ele elas eles isso isto aquilo "
    "the of and to in a an it is was were".split()
)

DISCLAIMER_LITERARIO = (
    "Números descritivos do texto medido: distintividade lexical e rítmica "
    "NÃO é veredito de qualidade nem de disrupção literária. Originalidade "
    "é julgamento humano de leitores, editores e crítica."
)


def literary_distinctiveness_report(text: str) -> Dict[str, Any]:
    """Mede características textuais observáveis. Descritivo e determinístico."""
    if not isinstance(text, str) or not text.strip():
        raise ContractError("texto não pode ser vazio.")

    norm = _normalize(text)
    tokens = re.findall(r"[a-zà-ü0-9]+", norm)
    sentences = _split_sentences(text)
    sentence_lengths = [len(re.findall(r"\w+", s)) for s in sentences]

    cliche_hits = []
    for expressao_norm, expressao in (
        (c, c) for c in CLICHE_LEXICON
    ):
        count = norm.count(expressao_norm)
        if count:
            # devolve a forma acentuada convencional quando conhecida
            display = {
                "silencio ensurdecedor": "silêncio ensurdecedor",
                "lagrimas amargas": "lágrimas amargas",
                "coracao partido": "coração partido",
                "no fundo do coracao": "no fundo do coração",
            }.get(expressao, expressao)
            cliche_hits.append({"expressao": display, "ocorrencias": count})

    content_tokens = [t for t in tokens if t not in _STOPWORDS and len(t) > 2]
    freq: Dict[str, int] = {}
    for t in content_tokens:
        freq[t] = freq.get(t, 0) + 1
    recorrentes = sorted(
        ((t, c) for t, c in freq.items() if c >= 2),
        key=lambda item: (-item[1], item[0]),
    )[:10]

    return {
        "schema_version": "1.0.0",
        "measured": True,
        "claim": "internal-descriptive-measurement",
        "token_count": len(tokens),
        "type_token_ratio": (len(set(tokens)) / len(tokens)) if tokens else 0.0,
        "sentence_count": len(sentences),
        "sentence_length_mean": (
            statistics.mean(sentence_lengths) if sentence_lengths else 0.0
        ),
        "sentence_length_stdev": (
            statistics.pstdev(sentence_lengths) if len(sentence_lengths) > 1 else 0.0
        ),
        "ritmo": {
            "interrogacoes": len(re.findall(r"[?？]", text)),
            "exclamacoes": len(re.findall(r"[!！]", text)),
            "reticencias": len(re.findall(r"\.\.\.|…+", text)),
            "travessoes": len(re.findall(r"—|–", text)),
        },
        "cliche_hits": cliche_hits,
        "simbolos_recorrentes": [
            {"token": t, "ocorrencias": c} for t, c in recorrentes
        ],
        "disclaimer": DISCLAIMER_LITERARIO,
    }


# ═══════════════════════════════════════════════════════════════════════
# Seleção de andaime via camada epistêmica (R363/R368)
# ═══════════════════════════════════════════════════════════════════════

_SCIENTIFIC_REGIMES = frozenset({"empirico_analitico", "formal_dedutivo"})


def select_scaffold(task_description: str) -> str:
    """Escolhe o andaime pela episteme da tarefa; sem sinais → indeterminate."""
    try:
        from transformer.episteme import infer_task_episteme
        profile = infer_task_episteme(task_description)
    except Exception:
        profile = None
    if profile is None:
        return "indeterminate"
    if profile.episteme in _SCIENTIFIC_REGIMES:
        return "scientific"
    if profile.episteme == "hermeneutico_interpretativo":
        return "literary"
    return "indeterminate"
