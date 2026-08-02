# -*- coding: utf-8 -*-
"""TerminologyGraphAgent — grafo terminológico trilíngue versionado.

Consome os deltas `propose_upsert` do CulturalEpistemeAgent
(SPEC-935-R359) e mantém termos, símbolos e instituições com traduções
preferidas/proibidas. O grafo não decide equivalência cultural: propostas
só ganham autoridade com aprovação humana identificada, e o gate de
release permanece fechado enquanto houver conflito aberto ou termo de
alto risco sem decisão.

SPEC-935-R364 / OCB-TERMINOLOGY-GRAPH-001.
"""

from __future__ import annotations

import copy
import json
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

from translation.cultural_episteme import (
    ContractError,
    _validate_terminology_delta,
)

SCHEMA_VERSION = "1.0.0"

# entity_types cuja ativação sem decisão humana bloqueia o release
_HIGH_RISK_ENTITY_TYPES = frozenset({"symbol", "historical", "clinical"})

_HUMAN_FORBIDDEN_REVIEWERS = frozenset({"", "agent", "bot", "auto", "system"})


def _norm(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _contains_term(text: str, term: str) -> bool:
    """Presença de termo com fronteira de palavra para escrita latina;
    substring direta para termos CJK (sem espaços)."""
    norm_text, norm_term = _norm(text), _norm(term)
    if re.search(r"[a-z0-9]", norm_term):
        return re.search(
            rf"(?<![a-z0-9]){re.escape(norm_term)}(?![a-z0-9])", norm_text
        ) is not None
    return norm_term in norm_text


def _preferred_field(target_language: str) -> Optional[str]:
    lang = target_language.lower()
    if lang.startswith("en"):
        return "preferred_en"
    if lang.startswith("zh"):
        return "preferred_zh_cn"
    return None


class TerminologyGraph:
    """Grafo terminológico com revisão monotônica e gate fail-closed."""

    def __init__(self, graph_id: str):
        if not graph_id or not str(graph_id).strip():
            raise ContractError("graph_id não pode ser vazio.")
        self.graph_id = str(graph_id).strip()
        self.revision = 0
        self._terms: Dict[str, Dict[str, Any]] = {}
        self._applied_deltas: set = set()
        self._open_findings: List[Dict[str, Any]] = []

    # ── deltas ────────────────────────────────────────────────────────
    def apply_delta(self, delta: Any) -> Dict[str, Any]:
        item = _validate_terminology_delta(delta, "delta")
        if item["base_graph_id"] != self.graph_id:
            raise ContractError(
                f"delta para grafo {item['base_graph_id']!r}; "
                f"este grafo é {self.graph_id!r}."
            )
        if item["delta_id"] in self._applied_deltas:
            return {"applied": False, "reason": "delta_id já aplicado", "revision": self.revision}
        try:
            base_revision = int(item["base_revision"])
        except (TypeError, ValueError):
            raise ContractError("base_revision deve ser inteira.")
        if base_revision != self.revision:
            raise ContractError(
                f"base_revision obsoleta: delta baseado em {base_revision}, "
                f"grafo está em {self.revision}."
            )
        key = _norm(item["source_term"])
        self._terms[key] = {
            "source_term": item["source_term"],
            "entity_type": item["entity_type"],
            "preferred_en": item.get("preferred_en"),
            "preferred_zh_cn": item.get("preferred_zh_cn"),
            "preserve_portuguese": bool(item.get("preserve_portuguese", False)),
            "forbidden_translations": list(item.get("forbidden_translations", [])),
            "rationale": item["rationale"],
            "provenance": copy.deepcopy(item["provenance"]),
            "approval_state": "proposed",
            "decided_by": None,
            "delta_id": item["delta_id"],
        }
        self._applied_deltas.add(item["delta_id"])
        self.revision += 1
        return {"applied": True, "revision": self.revision}

    # ── decisão humana ────────────────────────────────────────────────
    def _decide(self, source_term: str, reviewer: str, state: str) -> None:
        if not isinstance(reviewer, str) or _norm(reviewer.strip()) in _HUMAN_FORBIDDEN_REVIEWERS:
            raise ContractError(
                "decisão exige revisor humano identificado (não vazio, não 'agent')."
            )
        key = _norm(source_term)
        entry = self._terms.get(key)
        if entry is None:
            raise ContractError(f"termo {source_term!r} não existe no grafo.")
        if entry["approval_state"] != "proposed":
            raise ContractError(
                f"termo {source_term!r} já decidido ({entry['approval_state']})."
            )
        entry["approval_state"] = state
        entry["decided_by"] = reviewer.strip()
        self.revision += 1

    def approve(self, source_term: str, reviewer: str) -> None:
        self._decide(source_term, reviewer, "approved")

    def reject(self, source_term: str, reviewer: str) -> None:
        self._decide(source_term, reviewer, "rejected")

    def get_term(self, source_term: str) -> Optional[Dict[str, Any]]:
        entry = self._terms.get(_norm(source_term))
        return copy.deepcopy(entry) if entry else None

    # ── verificação de segmentos ──────────────────────────────────────
    def check_segment(
        self, source_text: str, translated_text: str, target_language: str
    ) -> List[Dict[str, Any]]:
        """Achados observáveis por regra; termos 'proposed' não têm autoridade."""
        findings: List[Dict[str, Any]] = []
        pref_field = _preferred_field(target_language)
        for entry in self._terms.values():
            if entry["approval_state"] != "approved":
                continue
            if not _contains_term(source_text, entry["source_term"]):
                continue
            for forbidden in entry["forbidden_translations"]:
                if _contains_term(translated_text, forbidden):
                    findings.append(self._finding(
                        "TERM_CONFLICT", "high", entry,
                        f"tradução proibida {forbidden!r} presente no alvo",
                    ))
            if entry["preserve_portuguese"] and not _contains_term(
                translated_text, entry["source_term"]
            ):
                findings.append(self._finding(
                    "TERM_CONFLICT", "high", entry,
                    "termo com preserve_portuguese ausente do alvo",
                ))
            elif (
                entry["entity_type"] == "symbol"
                and pref_field
                and entry.get(pref_field)
                and not _contains_term(translated_text, entry[pref_field])
            ):
                findings.append(self._finding(
                    "SYMBOL_DRIFT", "medium", entry,
                    f"tradução preferida {entry[pref_field]!r} ausente do alvo",
                ))
        self._open_findings.extend(
            f for f in findings if f["code"] == "TERM_CONFLICT"
        )
        return findings

    @staticmethod
    def _finding(code: str, severity: str, entry: Dict[str, Any], detail: str) -> Dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "code": code,
            "severity": severity,
            "source_term": entry["source_term"],
            "entity_type": entry["entity_type"],
            "detail": detail,
            "requires_human_review": True,
        }

    def resolve_findings(self, reviewer: str) -> int:
        """Marca conflitos abertos como tratados por revisão humana."""
        if not isinstance(reviewer, str) or _norm(reviewer.strip()) in _HUMAN_FORBIDDEN_REVIEWERS:
            raise ContractError("resolução exige revisor humano identificado.")
        count = len(self._open_findings)
        self._open_findings = []
        return count

    # ── relatório medido ──────────────────────────────────────────────
    def consistency_report(
        self, pairs: List[Tuple[str, str, str]]
    ) -> Dict[str, Any]:
        """Números observados neste corpus; nunca metas anunciadas."""
        occurrences = 0
        consistent = 0
        by_code: Dict[str, int] = {}
        for source_text, translated_text, lang in pairs:
            seg_findings = []
            pref_field = _preferred_field(lang)
            for entry in self._terms.values():
                if entry["approval_state"] != "approved":
                    continue
                if not _contains_term(source_text, entry["source_term"]):
                    continue
                occurrences += 1
                term_findings = [
                    f for f in self.check_segment(source_text, translated_text, lang)
                    if _norm(f["source_term"]) == _norm(entry["source_term"])
                ]
                if term_findings:
                    seg_findings.extend(term_findings)
                else:
                    consistent += 1
            for f in seg_findings:
                by_code[f["code"]] = by_code.get(f["code"], 0) + 1
        ratio = (consistent / occurrences) if occurrences else None
        return {
            "schema_version": SCHEMA_VERSION,
            "measured": True,
            "claim": "internal-fixture-measurement",
            "pairs_checked": len(pairs),
            "term_occurrences": occurrences,
            "consistent_occurrences": consistent,
            "consistency_ratio": ratio,
            "findings_by_code": by_code,
        }

    # ── gate fail-closed ──────────────────────────────────────────────
    def release_gate(self) -> Dict[str, Any]:
        reasons: List[str] = []
        for f in self._open_findings:
            reasons.append(
                f"TERM_CONFLICT aberto para {f['source_term']!r}: {f['detail']}"
            )
        for entry in self._terms.values():
            if (
                entry["approval_state"] == "proposed"
                and entry["entity_type"] in _HIGH_RISK_ENTITY_TYPES
            ):
                reasons.append(
                    f"termo de alto risco {entry['source_term']!r} "
                    f"({entry['entity_type']}) sem decisão humana"
                )
        return {"blocked": bool(reasons), "reasons": reasons}

    # ── persistência ──────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "graph_id": self.graph_id,
            "revision": self.revision,
            "terms": copy.deepcopy(self._terms),
            "applied_deltas": sorted(self._applied_deltas),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TerminologyGraph":
        graph = cls(data["graph_id"])
        graph.revision = int(data["revision"])
        graph._terms = copy.deepcopy(dict(data.get("terms", {})))
        graph._applied_deltas = set(data.get("applied_deltas", []))
        return graph

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")

    @classmethod
    def load(cls, path: str) -> "TerminologyGraph":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))
