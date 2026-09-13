#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PolymathicConvergence v1.0 — Convergência Polimática (R486)

Progressão do usuário:
    ERRO → AUSÊNCIA → OPORTUNIDADE → REVERSO (R483) → TRAJETÓRIAS (R485)
    → **CONVERGÊNCIA POLIMÁTICA** (este módulo)

Para cada lacuna do gap evolutivo Δ (R483), pergunta: **"quem, fora do domínio
atual, já resolveu parte disso?"** — cruzando a lacuna com a paisagem externa
curada no R482 (`landscape/manifest.json`, 20 agentes MIT auto-contidos) por
sobreposição léxica ponderada.

Modelo formal:

    tokens(t)  = palavras alfanuméricas de t (lowercase)
    score(a,g) = Σ_campo peso(campo) · I(∃ tok ∈ tokens(g): tok ∈ campo_do_agente)
                 ───────────────────────────────────────────────────────────────
                 Σ_campo peso(campo)

Campos e pesos: title=2.0, industry=2.0, framework=1.5, dependencies=1.0,
swift=1.0 (descrição PT-BR). overlap_terms = tokens de g presentes em campos.

Por lacuna g, `top_k` agentes ordenados por score desc, desempate agent_id asc.
Manifest ausente → fail-soft (warning + relatório vazio). 100% stdlib, hermético.
Nenhum código externo é baixado ou executado: a saída referencia `reference_url`.
"""

from __future__ import annotations

import json
import re
import pathlib
from dataclasses import dataclass, field
from typing import Any

from scanners.reverse_scanner import ReverseScanner

WEIGHTED_FIELDS: list[tuple[str, float]] = [
    ("title", 2.0),
    ("industry", 2.0),
    ("framework", 1.5),
    ("dependencies", 1.0),
    ("swift", 1.0),
]
ACADEMIC_FIELDS: list[tuple[str, float]] = [
    ("title", 2.0),
    ("description", 2.0),
    ("tags", 1.5),
]
DEFAULT_TOP_K = 3

_TOKEN_RE = re.compile(r"[a-zà-ÿ0-9]+", re.IGNORECASE)


@dataclass
class PolymathicMatch:
    """Agente externo que cobre parcialmente uma lacuna do gap."""
    capability: str
    agent_id: str
    agent_title: str
    source: str
    score: float
    overlap_terms: list[str]


@dataclass
class ConvergenceReport:
    """Relatório de convergência polimática por lacuna."""
    target_state: list[str]
    evolution_gap: list[str]
    matches: list["PolymathicMatch"]
    by_capability: dict[str, list["PolymathicMatch"]]
    params: dict[str, Any]
    warnings: list[str] = field(default_factory=list)


class PolymathicConvergence:
    """Cruzador de lacunas evolutivas com a paisagem externa (R482)."""

    def __init__(self, manifest_path: str | pathlib.Path | None = None):
        if manifest_path is None:
            manifest_path = (
                pathlib.Path(__file__).resolve().parent.parent
                / "landscape" / "manifest.json"
            )
        self.manifest_path = pathlib.Path(manifest_path)
        self.agents: list[dict[str, Any]] = []
        self.academic_sources: list[dict[str, Any]] = []
        self.warnings: list[str] = []
        if self.manifest_path.exists():
            try:
                data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
                self.agents = data.get("agents", [])
                self.academic_sources = data.get("academic", [])
            except (json.JSONDecodeError, OSError) as exc:
                self.warnings.append(f"manifest ilegível: {exc}")
        else:
            self.warnings.append(
                f"manifest não encontrado em {self.manifest_path} — convergência vazia"
            )

    # ─── TOKENS (CA1) ─────────────────────────────────────────────────────

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return set(_TOKEN_RE.findall(text.lower()))

    # ─── SCORE (CA2) ──────────────────────────────────────────────────────

    def _score_agent(self, capability_tokens: set[str], agent: dict[str, Any],
                     fields: list[tuple[str, float]] | None = None) -> tuple[float, list[str]]:
        matched_weight = 0.0
        total_weight = 0.0
        overlap: set[str] = set()
        fields = fields or WEIGHTED_FIELDS
        for field_name, weight in fields:
            total_weight += weight
            value = agent.get(field_name, "")
            if isinstance(value, list):
                value = " ".join(str(v) for v in value)
            field_tokens = self._tokens(str(value))
            hit_tokens = capability_tokens & field_tokens
            if hit_tokens:
                matched_weight += weight
                overlap.update(hit_tokens)
        if total_weight <= 0:
            return 0.0, []
        return round(matched_weight / total_weight, 4), sorted(overlap)

    def _all_sources(self) -> list[tuple[str, dict[str, Any], list[tuple[str, float]]]]:
        """Fontes de convergência: agentes (manifest) + acadêmicas (R489)."""
        items: list[tuple[str, dict[str, Any], list[tuple[str, float]]]] = [
            ("manifest", a, WEIGHTED_FIELDS) for a in self.agents
        ]
        items += [
            ("academic", a, ACADEMIC_FIELDS) for a in self.academic_sources
        ]
        return items

    # ─── MATCH POR LACUNA (CA1-CA3) ───────────────────────────────────────

    def match_capability(self, capability: str, top_k: int = DEFAULT_TOP_K) -> list[PolymathicMatch]:
        """Top_k fontes (agents + academic) que cobrem `capability`, por score."""
        cap_tokens = self._tokens(capability)
        scored: list[tuple[float, str, dict[str, Any], list[str]]] = []
        for kind, agent, fields in self._all_sources():
            if not cap_tokens:
                break
            score, overlap = self._score_agent(cap_tokens, agent, fields)
            if score > 0.0:
                scored.append((score, str(agent.get("id", "")), agent, overlap))
        scored.sort(key=lambda item: (-item[0], item[1]))  # desempate agent_id asc
        matches: list[PolymathicMatch] = []
        for score, agent_id, agent, overlap in scored[:top_k]:
            kind = "academic" if agent_id in {a.get("id") for a in self.academic_sources} else "manifest"
            matches.append(
                PolymathicMatch(
                    capability=capability,
                    agent_id=agent_id,
                    agent_title=str(agent.get("title", "")),
                    source=f"{kind}:{agent_id}",
                    score=score,
                    overlap_terms=overlap,
                )
            )
        return matches

    # ─── SCAN ORQUESTRADO (CA4-CA9) ───────────────────────────────────────

    def scan(
        self,
        noological_scan: dict[str, Any],
        target_state: list[str],
        observed: list[str] | None = None,
        corpus_terms: list[str] | None = None,
        exemplars: list[list[str]] | None = None,
        top_k: int = DEFAULT_TOP_K,
    ) -> ConvergenceReport:
        """Convergência por lacuna: Δ do R483 × manifest externo."""
        rs = ReverseScanner()
        base = rs.scan(
            noological_scan,
            target_state=target_state,
            observed=observed,
            corpus_terms=corpus_terms,
            exemplars=exemplars,
        )

        matches: list[PolymathicMatch] = []
        by_capability: dict[str, list[PolymathicMatch]] = {}
        for gap in base.evolution_gap:
            per_gap = self.match_capability(gap, top_k=top_k)
            by_capability[gap] = per_gap
            matches.extend(per_gap)

        return ConvergenceReport(
            target_state=list(base.target_state),
            evolution_gap=list(base.evolution_gap),
            matches=matches,
            by_capability=by_capability,
            params={
                "top_k": top_k,
                "source": str(self.manifest_path),
                "agents_indexed": len(self.agents) + len(self.academic_sources),
            },
            warnings=list(base.warnings) + list(self.warnings),
        )