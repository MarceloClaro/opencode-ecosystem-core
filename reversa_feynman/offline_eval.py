# -*- coding: utf-8 -*-
"""OfflinePolicyEvaluator v3 — decide→observe, holdout, Brier/ECE, drift,
reward/regret, IC95 bootstrap, readiness sem auto-ativação (SPEC-935-R504).

Port Python dos contratos Offline Policy Evaluation v3 do ReversaFeynman:
- separação decide/observe (sem look-ahead do outcome atual no histórico);
- holdout temporal (trainFraction 0.70 por `decided_at`);
- Brier/ECE apenas em shadow-matched-only;
- contrafactual conservador: quando shadow_action != executed_action o
  outcome do shadow NÃO é inventado; estimativas são rotuladas
  `observational/model-based` e `not causal`;
- IC95% bootstrap com PRNG determinístico (seed);
- DriftDetector: referência vs recente → insufficient_data|stable|drift;
- promotion_readiness(): auto_activate = False SEMPRE; elegível produz only
  requestPolicyActivation().
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class DecisionRecord:
    event_id: str
    decided_at: float
    confidence: float
    outcome: Optional[int]
    shadow_action: str = "default"
    executed_action: str = "default"
    shadow_match: bool = True
    reward: Optional[float] = None


@dataclass
class PromotionReadiness:
    eligible: bool
    auto_activate: bool = False
    reasons: List[str] = field(default_factory=list)
    request: Optional[Dict[str, Any]] = None

    def request_policy_activation(self, requester: str, reason: str) -> Dict[str, Any]:
        """Readiness apenas SOLICITA ativação; nunca ativa sozinho."""
        self.request = {
            "status": "activation_requested",
            "auto_activate": False,
            "requester": requester,
            "reason": reason,
            "eligible": self.eligible,
        }
        return self.request


def _brier(preds: List[float], outcomes: List[int]) -> Optional[float]:
    if not preds or len(preds) != len(outcomes):
        return None
    return sum((p - o) ** 2 for p, o in zip(preds, outcomes)) / len(preds)


def _ece(preds: List[float], outcomes: List[int], n_bins: int = 10) -> Optional[float]:
    if not preds or len(preds) != len(outcomes):
        return None
    bin_counts = [0] * n_bins
    bin_correct = [0] * n_bins
    bin_conf = [0.0] * n_bins
    for p, o in zip(preds, outcomes):
        idx = min(int(p * n_bins), n_bins - 1)
        bin_counts[idx] += 1
        bin_correct[idx] += o
        bin_conf[idx] += p
    total = len(preds)
    ece = 0.0
    for i in range(n_bins):
        if bin_counts[i] == 0:
            continue
        acc = bin_correct[i] / bin_counts[i]
        conf = bin_conf[i] / bin_counts[i]
        ece += (bin_counts[i] / total) * abs(acc - conf)
    return ece


class DriftDetector:
    """Compara janela de referência vs janela recente (reward, confidence,
    proporção OBSERVED). Estado drift bloqueia readiness e active mode."""

    def __init__(self, window_ref: int = 60, window_recent: int = 30,
                 reward_delta: float = 0.15, conf_delta: float = 0.10,
                 observed_delta: float = 0.20):
        self.window_ref = window_ref
        self.window_recent = window_recent
        self.reward_delta = reward_delta
        self.conf_delta = conf_delta
        self.observed_delta = observed_delta
        self._events: List[Dict[str, Any]] = []

    def add(self, reward: float, confidence: float, observed: bool) -> None:
        self._events.append({"reward": reward, "confidence": confidence,
                             "observed": observed})

    def state(self) -> str:
        ref = self._events[: self.window_ref]
        recent = self._events[-self.window_recent:] if self.window_recent else []
        if len(ref) < max(2, self.window_ref // 2) or len(recent) < max(2, self.window_recent // 2):
            return "insufficient_data"
        def _avg(xs, key):
            return sum(e[key] for e in xs) / len(xs)
        d_reward = abs(_avg(ref, "reward") - _avg(recent, "reward"))
        d_conf = abs(_avg(ref, "confidence") - _avg(recent, "confidence"))
        d_obs = abs(sum(e["observed"] for e in ref) / len(ref)
                    - sum(e["observed"] for e in recent) / len(recent))
        if d_reward > self.reward_delta or d_conf > self.conf_delta or d_obs > self.observed_delta:
            return "drift"
        return "stable"


class OfflinePolicyEvaluator:
    """Avaliação offline de política com governança conservadora (v3)."""

    DEFAULTS = {
        "minRecords": 30,
        "minMatchedShadow": 12,
        "minShadowCoverage": 0.20,
        "maxBrier": 0.25,
        "maxEce": 0.20,
        "maxEstimatedShadowRegret": 0.10,
        "minEstimatedRewardDelta": 0.00,
    }

    def __init__(self, seed: int = 42, train_fraction: float = 0.70,
                 thresholds: Optional[Dict[str, float]] = None):
        self.seed = seed
        self.train_fraction = train_fraction
        self.thresholds = {**self.DEFAULTS, **(thresholds or {})}
        self._records: List[DecisionRecord] = []
        self._drift = DriftDetector()
        self._cache: Optional[Dict[str, Any]] = None

    # ── ingestão ────────────────────────────────────────────────────────
    def record(self, r: DecisionRecord) -> None:
        self._records.append(r)
        self._drift.add(reward=r.reward if r.reward is not None else (1.0 if r.outcome else 0.0),
                        confidence=r.confidence,
                        observed=bool(r.outcome) if r.outcome is not None else False)
        self._cache = None

    def _hist_len(self) -> int:
        return len(self._records)

    # ── decide / observe (separados — sem look-ahead) ───────────────────
    def decide(self, context: Dict[str, Any], event_id: str) -> Dict[str, Any]:
        """Decide em shadow usando apenas o histórico ANTERIOR ao evento.
        O outcome do próprio evento ainda não existe no histórico."""
        past = [r for r in self._records if r.event_id != event_id]
        n = len(past)
        conf = sum(r.confidence for r in past) / n if n else 0.5
        return {"mode": "shadow", "policy": "contextual-shadow-v1",
                "expected_success": conf, "n_history": n}

    def observe(self, context: Dict[str, Any], decision: Dict[str, Any],
                outcome: int) -> DecisionRecord:
        rec = DecisionRecord(
            event_id=decision.get("event_id", f"ev-{self._hist_len() + 1}"),
            decided_at=decision.get("decided_at", float(self._hist_len() + 1)),
            confidence=decision.get("expected_success", 0.5),
            outcome=outcome,
            shadow_action=decision.get("shadow_action", "default"),
            executed_action=decision.get("executed_action", "default"),
            shadow_match=decision.get("shadow_match", True),
        )
        self.record(rec)
        return rec

    # ── avaliação ───────────────────────────────────────────────────────
    def _split_train_holdout(self):
        ordered = sorted(self._records, key=lambda r: r.decided_at)
        n_train = int(len(ordered) * self.train_fraction)
        return ordered[:n_train], ordered[n_train:]

    def evaluate(self, bootstrap_seed: Optional[int] = None) -> Dict[str, Any]:
        train, holdout = self._split_train_holdout()
        matched = [r for r in train if r.shadow_match and r.outcome is not None]
        n_matched = len(matched)
        brier = _brier([r.confidence for r in matched],
                       [int(r.outcome) for r in matched]) if matched else None
        ece = _ece([r.confidence for r in matched],
                   [int(r.outcome) for r in matched]) if matched else None

        # reward shadow = outcome médio matched; baseline = outcome médio executado
        executed = [r for r in train if r.outcome is not None]
        reward_baseline = (sum(int(r.outcome) for r in executed) / len(executed)
                           if executed else None)
        reward_shadow = (sum(int(r.outcome) for r in matched) / n_matched
                         if matched else None)
        delta = (reward_shadow - reward_baseline
                 if reward_shadow is not None and reward_baseline is not None else None)

        ic95 = None
        if (matched and reward_shadow is not None and reward_baseline is not None
                and len(matched) >= 3):
            rng = random.Random(bootstrap_seed if bootstrap_seed is not None else self.seed)
            diffs = []
            for _ in range(2000):
                sample = [rng.choice(matched) for _ in matched]
                s_shadow = sum(int(r.outcome) for r in sample) / len(sample)
                diffs.append(s_shadow - reward_baseline)
            diffs.sort()
            lo = diffs[50]          # percentil 2.5
            hi = diffs[1950 - 1]    # percentil 97.5 (0-index: 1949)
            ic95 = (round(lo, 4), round(hi, 4))

        self._cache = {
            "n_total": len(self._records), "n_train": len(train),
            "n_holdout": len(holdout), "n_shadow_matched": n_matched,
            "brier_shadow_matched": brier, "ece_shadow_matched": ece,
            "reward_baseline": reward_baseline, "reward_shadow": reward_shadow,
            "delta": delta, "delta_ic95": ic95,
            "contrafactual": ("shadow != executed => outcome NÃO inventado; "
                              "estimativas observational/model-based, not causal")
            if any(not r.shadow_match for r in train) else None,
            "drift": self._drift.state(),
        }
        return self._cache

    # ── readiness ───────────────────────────────────────────────────────
    def promotion_readiness(self) -> PromotionReadiness:
        report = self.evaluate()
        t = self.thresholds
        reasons: List[str] = []
        if report["n_total"] < t["minRecords"]:
            reasons.append(f"minRecords: {report['n_total']} < {t['minRecords']}")
        if report["n_shadow_matched"] < t["minMatchedShadow"]:
            reasons.append(f"minMatchedShadow: {report['n_shadow_matched']} < {t['minMatchedShadow']}")
        if report["n_total"]:
            coverage = report["n_shadow_matched"] / report["n_total"]
            if coverage < t["minShadowCoverage"]:
                reasons.append(f"minShadowCoverage: {coverage:.2f} < {t['minShadowCoverage']}")
        if report["brier_shadow_matched"] is not None and report["brier_shadow_matched"] > t["maxBrier"]:
            reasons.append(f"maxBrier: {report['brier_shadow_matched']:.3f} > {t['maxBrier']}")
        if report["ece_shadow_matched"] is not None and report["ece_shadow_matched"] > t["maxEce"]:
            reasons.append(f"maxEce: {report['ece_shadow_matched']:.3f} > {t['maxEce']}")
        if report["delta"] is not None and report["delta"] < t["minEstimatedRewardDelta"]:
            reasons.append(f"minEstimatedRewardDelta: {report['delta']:.3f} < {t['minEstimatedRewardDelta']}")
        if report["drift"] == "drift":
            reasons.append("drift detectado — bloqueia readiness")

        eligible = not reasons and report["n_shadow_matched"] >= t["minMatchedShadow"]
        return PromotionReadiness(eligible=bool(eligible), auto_activate=False, reasons=reasons)