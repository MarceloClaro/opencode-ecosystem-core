# -*- coding: utf-8 -*-
"""
Evolution Cycles — Registro de Ciclos Evolutivos (R1..R46+)
===========================================================
Porta a disciplina de ciclos evolutivos documentados do OpenCode_Ecosystem
(evolution/evo-*.md, com scores por round) para um registro programático.

Cada ciclo (round) registra: objetivo, mudanças, score de qualidade (0-10),
lições aprendidas. O registro persiste em evolution/cycles.json e alimenta a
memória metacognitiva do ecossistema (lições viram reflexões no MetaBus).
"""

from __future__ import annotations

import glob
import json
import os
import re
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

EVOLUTION_DIR = os.path.dirname(os.path.abspath(__file__))
# Isolamento de teste: respeita EVOLUTION_STATE_PATH se definida,
# senao usa o state_path real (evolution/cycles.json).
STATE_PATH = os.environ.get(
    "EVOLUTION_STATE_PATH",
    os.path.join(EVOLUTION_DIR, "cycles.json"),
)


@dataclass
class EvolutionCycle:
    round_id: str                 # ex.: "R47"
    objective: str
    changes: List[str] = field(default_factory=list)
    score: Optional[float] = None  # 0-10
    lessons: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    # --- Cadeia de custódia auditável (SPEC-935-R462) ---
    artifact_hashes: Dict[str, str] = field(default_factory=dict)  # sha256 por artefato
    external_verdict: Optional[Dict[str, Any]] = None  # quem auditou + passou/reprovou
    verifier_identity: str = ""  # identificador do auditor (≠ gerador)
    evidence_trail: List[str] = field(default_factory=list)  # specs/testes/scans
    audited: bool = False  # True se passou pelo gate externo
    legacy: bool = False  # True se ciclo pré-R462 sem auditoria formal


class EvolutionRegistry:
    """Registro persistente de ciclos evolutivos do ecossistema."""

    def __init__(self, state_path: str = STATE_PATH):
        self.state_path = state_path
        self.cycles: List[EvolutionCycle] = []
        self._total_score: float = 0.0
        self._scored_count: int = 0
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                allowed = {"round_id", "objective", "changes", "score", "lessons",
                           "timestamp", "artifact_hashes", "external_verdict",
                           "verifier_identity", "evidence_trail", "audited", "legacy"}
                self.cycles = [
                    EvolutionCycle(**{key: value for key, value in cycle.items() if key in allowed})
                    for cycle in data.get("cycles", [])
                    if isinstance(cycle, dict)
                ]
            except (json.JSONDecodeError, TypeError, ValueError):
                self.cycles = []
        self._recompute_stats()

    def _recompute_stats(self) -> None:
        scored = [c.score for c in self.cycles if c.score is not None]
        self._total_score = sum(scored)
        self._scored_count = len(scored)

    def save(self) -> None:
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump({"cycles": [asdict(c) for c in self.cycles]},
                      f, ensure_ascii=False, indent=2)

    def next_round_id(self) -> str:
        max_n = 46  # R1..R46 documentados no ecossistema original
        for c in self.cycles:
            m = re.match(r"R(\d+)", c.round_id)
            if m:
                max_n = max(max_n, int(m.group(1)))
        return f"R{max_n + 1}"

    def record(self, objective: str, changes: List[str],
               score: Optional[float] = None,
               lessons: Optional[List[str]] = None,
               round_id: Optional[str] = None) -> EvolutionCycle:
        cycle = EvolutionCycle(
            round_id=round_id or self.next_round_id(),
            objective=objective, changes=changes,
            score=score, lessons=lessons or [],
            legacy=True,  # sem auditoria externa formal => ciclo legado (R462)
        )
        self.cycles.append(cycle)
        if score is not None:
            self._total_score += score
            self._scored_count += 1
        self.save()
        return cycle

    def record_audited(self, objective: str, changes: List[str],
                       artifact_hashes: Dict[str, str],
                       external_verdict: Dict[str, Any],
                       verifier_identity: str,
                       generator_identity: str,
                       evidence_trail: Optional[List[str]] = None,
                       round_id: Optional[str] = None,
                       score: Optional[float] = None,
                       lessons: Optional[List[str]] = None) -> EvolutionCycle:
        """Registra um ciclo que JÁ passou pelo EvolutionAuditGate (auditado).

        Fail-closed: se o veredito externo não estiver aprovado (passed=True),
        ou se verificador == gerador, o registro é RECUSADO (PermissionError)
        e nada é persistido. (SPEC-935-R462 / A6, gate fail-closed)
        """
        passed = bool(external_verdict and external_verdict.get("passed") is True)
        verified_by_other = bool(verifier_identity
                                 and verifier_identity != generator_identity)
        if not passed or not verified_by_other:
            raise PermissionError(
                "Ciclo recusado: exige external_verdict.passed=True e "
                "verifier_identity distinto do gerador. (SPEC-935-R462 gate)"
            )

        cycle = EvolutionCycle(
            round_id=round_id or self.next_round_id(),
            objective=objective, changes=changes,
            score=score, lessons=lessons or [],
            artifact_hashes=dict(artifact_hashes),
            external_verdict=dict(external_verdict),
            verifier_identity=verifier_identity,
            evidence_trail=list(evidence_trail or []),
            audited=True,
            legacy=False,
        )
        self.cycles.append(cycle)
        if score is not None:
            self._total_score += score
            self._scored_count += 1
        self.save()
        return cycle

    def custody_metric(self) -> Dict[str, Any]:
        """Métrica de Custódia Auditável (SPEC-935-R462 / gate de aceitação).

        Custódia(%) = (ciclos com artifact_hashes ∧ external_verdict ∧
                       verifier_identity ≠ '') / total × 100.
        Baseline medido: 0,0%. Alvo pós-R462: ≥ 90%.
        """
        total = len(self.cycles)
        if total == 0:
            return {"audited": 0, "total": 0, "pct": 0.0, "rejected": 0,
                    "tampered": 0, "legacy": 0}
        audited = sum(1 for c in self.cycles
                      if c.audited
                      and c.artifact_hashes
                      and c.external_verdict
                      and c.verifier_identity
                      and c.external_verdict.get("passed") is True)
        legacy = sum(1 for c in self.cycles if c.legacy)
        tampered = sum(1 for c in self.cycles
                       if c.external_verdict
                       and c.external_verdict.get("tampered") is True)
        return {
            "audited": audited,
            "total": total,
            "pct": round(100.0 * audited / total, 1),
            "rejected": sum(1 for c in self.cycles
                            if c.external_verdict
                            and c.external_verdict.get("passed") is False),
            "tampered": tampered,
            "legacy": legacy,
        }

    def custody_recent(self, since_round: str = "R462") -> Dict[str, Any]:
        """Custódia sobre ciclos NOVOS (a partir de `since_round`). Mede a
        fração dos ciclos gerados sob o regime auditado que realmente passaram
        pelo gate externo. É a medida honesta da melhoria estrutural (R462)."""
        recent = [c for c in self.cycles
                  if self._round_num(c.round_id) >= self._round_num(since_round)]
        total = len(recent)
        if total == 0:
            return {"audited": 0, "total": 0, "pct": 0.0}
        audited = sum(1 for c in recent
                      if c.audited and c.artifact_hashes and c.external_verdict
                      and c.verifier_identity
                      and c.external_verdict.get("passed") is True)
        return {
            "audited": audited,
            "total": total,
            "pct": round(100.0 * audited / total, 1),
        }

    def _round_num(self, round_id: str) -> int:
        m = re.match(r"R(\d+)", round_id or "")
        return int(m.group(1)) if m else -1


    def history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return [asdict(c) for c in self.cycles[-limit:]]

    def average_score(self) -> Optional[float]:
        """Média móvel dos scores dos ciclos com score (G5 — R438).

        Esta média **não é gate de qualidade**. O gate real é
        `SpecVerifier` + `GradingHead` + `confidence_calibrator` (verificado
        por `SpecRegistry` e `loop_spec_registry`), não a média histórica.
        A média serve apenas como indicador de tendência evolutiva.
        """
        if self._scored_count > 0:
            return round(self._total_score / self._scored_count, 2)
        return None

    def load_documented_cycles(self) -> List[Dict[str, str]]:
        """Indexa os ciclos documentados em evolution/evo-*.md (portados do original)."""
        docs = []
        for path in sorted(glob.glob(os.path.join(EVOLUTION_DIR, "evo-*.md"))):
            name = os.path.basename(path)
            title = ""
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("#"):
                            title = line.lstrip("# ").strip()
                            break
            except OSError:
                pass
            docs.append({"file": name, "title": title})
        return docs


# Singleton
evolution_registry = EvolutionRegistry()
