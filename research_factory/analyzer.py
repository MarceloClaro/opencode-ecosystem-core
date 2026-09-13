# -*- coding: utf-8 -*-
"""ReviewStyleAnalyzer — aprende preferências de revisão a partir de feedback.

Inspirado no entrypoint Analyzer do open-swe (langchain-ai/open-swe):
converte feedback histórico em regras reutilizáveis e determinísticas
(sem LLM): seções obrigatórias observadas e piso de tamanho. Regras e
exemplos persistem em JSON sob o diretório raiz do analisador.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


CANONICAL_SECTIONS = [
    "Introdução",
    "Método",
    "Resultados",
    "Discussão",
    "Conclusão",
    "Referências",
]


class ReviewStyleAnalyzer:
    """Analisador de estilo de revisão com regras derivadas de feedback."""

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._examples = self._load_examples()
        self._rules = self._load_rules()

    # ---- persistência ----

    def _examples_path(self) -> Path:
        return self.root / "examples.json"

    def _rules_path(self) -> Path:
        return self.root / "rules.json"

    def _load_examples(self) -> List[Dict[str, Any]]:
        path = self._examples_path()
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return []

    def _load_rules(self) -> List[Dict[str, Any]]:
        path = self._rules_path()
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return []

    def _save_examples(self) -> None:
        self._examples_path().write_text(
            json.dumps(self._examples, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _save_rules(self) -> None:
        self._rules_path().write_text(
            json.dumps(self._rules, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ---- aprendizado ----

    def add_example(self, manuscript: str, feedback: Dict[str, Any],
                    accepted: Optional[str] = None) -> Dict[str, Any]:
        example = {
            "manuscript": manuscript,
            "feedback": feedback,
            "accepted": accepted,
            "timestamp_utc": time.time(),
        }
        self._examples.append(example)
        self._save_examples()
        derived = self._derive_rules(manuscript, feedback)
        self._merge_rules(derived)
        self._save_rules()
        return example

    @staticmethod
    def _extract_section(text: str) -> Optional[str]:
        for section in CANONICAL_SECTIONS:
            if section.lower() in text.lower():
                return section
        return None

    def _derive_rules(self, manuscript: str,
                      feedback: Dict[str, Any]) -> List[Dict[str, Any]]:
        rules: List[Dict[str, Any]] = []
        decision = (feedback or {}).get("decision", "")
        comments = (feedback or {}).get("comments", []) or []
        for comment in comments:
            severity = comment.get("severity", "")
            text = comment.get("text", "") or ""
            if severity == "blocker" and decision == "reject":
                section = self._extract_section(text)
                if section and section not in manuscript:
                    rules.append({
                        "kind": "required_section",
                        "section": section,
                        "rationale": text,
                    })
        if decision == "reject" and len(manuscript) < 200:
            rules.append({
                "kind": "length_floor",
                "floor": 200,
                "rationale": "manuscrito abaixo do piso observado",
            })
        return rules

    def _merge_rules(self, derived: List[Dict[str, Any]]) -> None:
        for rule in derived:
            if rule["kind"] == "required_section":
                existing = next(
                    (r for r in self._rules
                     if r["kind"] == "required_section"
                     and r["section"] == rule["section"]),
                    None,
                )
                if existing:
                    existing["rationale"] = rule["rationale"]
                else:
                    self._rules.append(rule)
            elif rule["kind"] == "length_floor":
                existing = next(
                    (r for r in self._rules if r["kind"] == "length_floor"),
                    None,
                )
                if existing:
                    existing["floor"] = max(existing["floor"], rule["floor"])
                else:
                    self._rules.append(rule)

    # ---- consulta ----

    def rules(self) -> List[Dict[str, Any]]:
        return list(self._rules)

    def flag(self, manuscript: str) -> List[Dict[str, Any]]:
        flagged: List[Dict[str, Any]] = []
        for rule in self._rules:
            if (rule["kind"] == "required_section"
                    and rule["section"] not in manuscript):
                flagged.append(rule)
            elif (rule["kind"] == "length_floor"
                  and len(manuscript) < rule["floor"]):
                flagged.append(rule)
        return flagged