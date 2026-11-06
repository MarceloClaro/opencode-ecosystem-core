"""Centro de Produção Global do MarceloClaro.

O orquestrador deixa de apenas rotear uma tarefa e passa a decidir, por
atenção executiva, qual é o próximo passo de uma produção: especificar,
rotear, executar, verificar, refletir, entregar, pedir consentimento ou parar.

A camada é determinística e auditável. Ela não executa código de terceiro por
conta própria: prepara o plano, aplica gates e devolve o recibo. A execução
externa continua sob autorização do operador.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Callable, Dict, List, Optional
import uuid

from transformer.executive import ExecutiveAttention

STAGES = ("intake", "spec", "route", "execute", "verify", "reflect", "deliver",
          "complete", "blocked", "awaiting_consent")


@dataclass
class ProductionState:
    production_id: str
    goal: str
    stage: str = "intake"
    status: str = "active"
    risk_level: str = "low"
    budget: float = 8.0
    cost_spent: float = 0.0
    consent: bool = False
    spec_id: Optional[str] = None
    selected_adapter: Optional[str] = None
    execution_plan: Optional[Dict[str, Any]] = None
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "production_id": self.production_id,
            "goal": self.goal,
            "stage": self.stage,
            "status": self.status,
            "risk_level": self.risk_level,
            "budget": round(self.budget, 4),
            "cost_spent": round(self.cost_spent, 4),
            "consent": self.consent,
            "spec_id": self.spec_id,
            "selected_adapter": self.selected_adapter,
            "execution_plan": self.execution_plan,
            "evidence_count": len(self.evidence),
            "limitations": list(self.limitations),
            "history": list(self.history),
        }

    def attention_state(self) -> Dict[str, Any]:
        return {
            "stage": self.stage,
            "budget": self.budget,
            "consent": self.consent,
            "evidence_count": len(self.evidence),
            "risk_level": self.risk_level,
        }


STORE_DIR = Path.home() / ".local/share/opencode-core/productions"
PRODUCTION_ID_RE = re.compile(r"prod-[a-f0-9]{12}\Z")
STORE_MAX_BYTES = 2 * 1024 * 1024


def _state_from_dict(data: Dict[str, Any]) -> ProductionState:
    if not isinstance(data, dict):
        raise ValueError("estado da produção deve ser objeto")
    production_id = data.get("production_id")
    if not isinstance(production_id, str) or not PRODUCTION_ID_RE.fullmatch(production_id):
        raise ValueError("production_id inválido")
    goal = data.get("goal")
    if not isinstance(goal, str) or not goal.strip():
        raise ValueError("goal inválido")
    stage = data.get("stage", "intake")
    if stage not in STAGES:
        raise ValueError("stage inválido")
    status = data.get("status", "active")
    if status not in {"active", "completed", "blocked", "awaiting_consent", "budget_exhausted"}:
        raise ValueError("status inválido")
    risk = data.get("risk_level", "low")
    if risk not in {"low", "medium", "high"}:
        raise ValueError("risk_level inválido")
    budget = data.get("budget", 0.0)
    cost = data.get("cost_spent", 0.0)
    if (isinstance(budget, bool) or not isinstance(budget, (int, float))
            or not math.isfinite(budget) or budget < 0):
        raise ValueError("budget inválido")
    if (isinstance(cost, bool) or not isinstance(cost, (int, float))
            or not math.isfinite(cost) or cost < 0):
        raise ValueError("cost_spent inválido")
    for name in ("evidence", "limitations", "history"):
        if not isinstance(data.get(name, []), list):
            raise ValueError(f"{name} inválido")
    plan = data.get("execution_plan")
    if plan is not None and not isinstance(plan, dict):
        raise ValueError("execution_plan inválido")
    return ProductionState(
        production_id=production_id,
        goal=goal.strip(),
        stage=stage,
        status=status,
        risk_level=risk,
        budget=float(budget),
        cost_spent=float(cost),
        consent=data.get("consent") is True,
        spec_id=data.get("spec_id") if isinstance(data.get("spec_id"), str) else None,
        selected_adapter=(data.get("selected_adapter")
                          if isinstance(data.get("selected_adapter"), str) else None),
        execution_plan=plan,
        evidence=list(data.get("evidence", [])),
        limitations=[str(item) for item in data.get("limitations", [])],
        history=list(data.get("history", [])),
    )


class ProductionStore:
    """Persistência local e atômica de produções, fora do repositório."""

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root).expanduser() if root is not None else STORE_DIR
        self.root.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(self.root, 0o700)
        except OSError:
            pass

    def _path(self, production_id: str) -> Path:
        if not isinstance(production_id, str) or not PRODUCTION_ID_RE.fullmatch(production_id):
            raise ValueError("production_id inválido")
        return self.root / f"{production_id}.json"

    def path_for(self, production_id: str) -> str:
        return str(self._path(production_id))

    def save(self, state: ProductionState) -> str:
        if not isinstance(state, ProductionState):
            raise ValueError("estado inválido")
        target = self._path(state.production_id)
        payload = {"schema_version": 1,
                   "saved_at": datetime.now(timezone.utc).isoformat(),
                   "state": state.to_dict()}
        temp = target.with_suffix(".tmp")
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        try:
            os.chmod(temp, 0o600)
        except OSError:
            pass
        temp.replace(target)
        return str(target)

    def load(self, production_id: str) -> ProductionState:
        target = self._path(production_id)
        if not target.is_file():
            raise ValueError("produção não encontrada")
        if target.stat().st_size > STORE_MAX_BYTES:
            raise ValueError("estado da produção excessivo")
        try:
            payload = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ValueError("estado da produção ilegível") from exc
        if not isinstance(payload, dict) or payload.get("schema_version") != 1:
            raise ValueError("schema de produção inválido")
        return _state_from_dict(payload.get("state") or {})

    def list(self) -> List[Dict[str, Any]]:
        rows = []
        for target in sorted(self.root.glob("prod-*.json")):
            try:
                if target.stat().st_size > STORE_MAX_BYTES:
                    continue
                payload = json.loads(target.read_text(encoding="utf-8"))
                state = _state_from_dict(payload.get("state") or {})
            except (OSError, ValueError, TypeError):
                continue
            rows.append({"production_id": state.production_id,
                         "goal": state.goal[:300], "stage": state.stage,
                         "status": state.status,
                         "saved_at": payload.get("saved_at"),
                         "path": str(target)})
        return rows


class ProductionCenter:
    """Decide o próximo passo de uma produção e preserva evidência/limites."""

    def __init__(self, registry=None, attention: ExecutiveAttention | None = None,
                 bus=None, max_steps: int = 8, store: ProductionStore | None = None):
        if type(max_steps) is not int or not 1 <= max_steps <= 32:
            raise ValueError("max_steps deve estar entre 1 e 32")
        self._registry = registry
        self.attention = attention or ExecutiveAttention()
        self.bus = bus
        self.max_steps = max_steps
        self._store = store

    @property
    def registry(self):
        if self._registry is None:
            from integrations.external_skills import load_registry
            self._registry = load_registry()
        return self._registry

    @property
    def store(self) -> ProductionStore:
        if self._store is None:
            self._store = ProductionStore()
        return self._store

    def status(self) -> Dict[str, Any]:
        from integrations.external_skills import status as registry_status
        return {
            "status": "ready",
            "center": "marceloclaro.production",
            "stages": list(STAGES),
            "attention": {"heads": list(self.attention.weights),
                          "weights": dict(self.attention.weights),
                          "policy": "atenção executiva determinística; não é rede neural treinada"},
            "adapters": registry_status(registry=self.registry).get("adapters", []),
            "bounded": {"max_steps": self.max_steps},
            "execution_scope": "planejamento e gates; execução externa exige autorização",
        }

    @staticmethod
    def _adapter_capabilities(adapter: Dict[str, Any]) -> List[str]:
        return ["external_skill", str(adapter.get("kind", "unknown"))]

    def _adapter_candidates(self, state: ProductionState) -> List[Dict[str, Any]]:
        from integrations.external_skills import status as registry_status
        rows = registry_status(registry=self.registry).get("adapters", [])
        candidates: List[Dict[str, Any]] = []
        for adapter in rows:
            if not adapter.get("ready"):
                continue
            skill_id = str(adapter["skill_id"])
            requires = adapter.get("consent_required") is True
            available = (state.spec_id is not None
                         and state.execution_plan is None
                         and (state.selected_adapter in (None, skill_id)))
            keywords = " ".join(str(item) for item in adapter.get("keywords", []) or [])
            candidates.append({
                "action_id": f"execute:{skill_id}",
                "kind": "execute",
                "description": (f"executar adaptador {skill_id} "
                                f"({adapter.get('kind', 'unknown')}): {keywords}; "
                                f"{adapter.get('notes', '')}"),
                "stage": "execute",
                "risk": (0.65 if requires and not state.consent
                         else 0.30 if requires else 0.25),
                "cost": 1.0,
                "evidence_gain": 0.75,
                "confidence": 0.6,
                "available": available,
                "requires_consent": requires,
                "capabilities": self._adapter_capabilities(adapter),
                "keywords": list(adapter.get("keywords", []) or []),
            })
            if requires and not state.consent and available:
                candidates.append({
                    "action_id": f"consent:{skill_id}",
                    "kind": "consent",
                    "description": f"pedir consentimento explícito para {skill_id}",
                    "stage": "execute",
                    "risk": 0.05,
                    "cost": 0.2,
                    "evidence_gain": 0.1,
                    "confidence": 0.9,
                    "available": True,
                    "requires_consent": False,
                    "capabilities": ["consent"],
                })
        return candidates

    def candidates(self, state: ProductionState) -> List[Dict[str, Any]]:
        verified = any(
            entry.get("kind") == "verify"
            and (entry.get("result") or {}).get("verified") is True
            for entry in state.evidence
        )
        reflected = any(entry.get("kind") == "reflect" for entry in state.evidence)
        delivered = any(entry.get("kind") == "deliver" for entry in state.evidence)
        rows = [
            {"action_id": "specify", "kind": "specify",
             "description": "especificar escopo, critérios de aceitação e riscos da produção",
             "stage": "intake", "risk": 0.0, "cost": 0.5, "evidence_gain": 0.6,
             "confidence": 0.8, "available": state.spec_id is None,
             "requires_consent": False, "capabilities": ["spec"]},
            # A ação é aplicável no estágio em que o centro está; o handler
            # avança o estado para o próximo estágio.
            {"action_id": "route", "kind": "route",
             "description": "rotear a produção para o adaptador ou agente mais adequado",
             "stage": "spec", "risk": 0.1, "cost": 0.5, "evidence_gain": 0.4,
             "confidence": 0.7,
             "available": state.spec_id is not None and state.selected_adapter is None,
             "requires_consent": False, "capabilities": ["routing"]},
            {"action_id": "verify", "kind": "verify",
             "description": "verificar evidência, dependências, testes e limites",
             "stage": "verify", "risk": 0.0, "cost": 0.5, "evidence_gain": 0.9,
             "confidence": 0.8,
             "available": state.execution_plan is not None and not verified,
             "requires_consent": False, "capabilities": ["verification"]},
            {"action_id": "reflect", "kind": "reflect",
             "description": "refletir sobre o resultado e registrar lição no MetaBus",
             "stage": "reflect", "risk": 0.0, "cost": 0.3, "evidence_gain": 0.3,
             "confidence": 0.7, "available": verified and not reflected,
             "requires_consent": False, "capabilities": ["reflection"]},
            {"action_id": "deliver", "kind": "deliver",
             "description": "entregar o recibo com evidência, limitações e próximo passo",
             "stage": "deliver", "risk": 0.15, "cost": 0.3, "evidence_gain": 0.2,
             "confidence": 0.8, "available": reflected and not delivered,
             "requires_consent": False, "capabilities": ["delivery"]},
            {"action_id": "stop", "kind": "stop",
             "description": "parar e devolver bloqueio sem executar terceiros",
             "stage": state.stage, "risk": 0.0, "cost": 0.1, "evidence_gain": 0.0,
             "confidence": 0.2, "available": True, "requires_consent": False,
             "capabilities": ["stop"]},
        ]
        rows.extend(self._adapter_candidates(state))
        return rows

    def plan(self, goal: str, *, risk_level: str = "low", budget: float = 8.0,
             consent: bool = False) -> Dict[str, Any]:
        """Dry-run auditável: ranqueia ações, não executa nenhuma."""
        state = self._new_state(goal, risk_level=risk_level, budget=budget,
                                consent=consent)
        decision = self.attention.evaluate(goal, state.attention_state(),
                                           self.candidates(state))
        return {"status": "planned", "state": state.to_dict(), "decision": decision,
                "executed": False}

    def _new_state(self, goal: str, *, risk_level: str, budget: float,
                   consent: bool) -> ProductionState:
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("o objetivo da produção deve conter texto")
        if risk_level not in {"low", "medium", "high"}:
            raise ValueError("risk_level deve ser low, medium ou high")
        if isinstance(budget, bool) or not isinstance(budget, (int, float)) or budget <= 0:
            raise ValueError("budget deve ser um número positivo")
        return ProductionState(
            production_id="prod-" + uuid.uuid4().hex[:12],
            goal=goal.strip(), risk_level=risk_level, budget=float(budget),
            consent=consent is True,
        )

    def _select_adapter(self, state: ProductionState) -> Optional[Dict[str, Any]]:
        candidates = [c for c in self._adapter_candidates(state) if c["kind"] == "execute"]
        if not candidates:
            return None
        # O roteamento pode escolher um adaptador que exigirá consentimento na
        # execução; o gate de consentimento continua no passo `execute`.
        selection_state = state.attention_state()
        selection_state["consent"] = True
        # O roteamento não executa o adaptador; ele pode escolher mesmo quando
        # o orçamento restante já não paga a execução seguinte.
        selection_state["budget"] = max(1.0, float(state.budget))
        decision = self.attention.evaluate(state.goal, selection_state, candidates)
        if not state.consent:
            # Prefira pedir consentimento ao adaptador mais aderente em vez de
            # substituí-lo silenciosamente por outro que não exige aprovação.
            tags = (decision.get("heads") or {}).get("tags") or {}
            gated = [c for c in candidates if c.get("requires_consent")]
            free = [c for c in candidates if not c.get("requires_consent")]
            if gated and free:
                best_gated = max(gated, key=lambda c: tags.get(c["action_id"], 0.0))
                best_free = max(free, key=lambda c: tags.get(c["action_id"], 0.0))
                # Só peça consentimento quando o adaptador gated for
                # materialmente mais aderente; empate favorece o livre.
                if tags.get(best_gated["action_id"], 0.0) > tags.get(
                        best_free["action_id"], 0.0) + 0.05:
                    return best_gated
        selected = decision.get("selected")
        return next((c for c in candidates if c["action_id"] == selected), None)

    @staticmethod
    def _safe_check(plan: Dict[str, Any], timeout: int = 60) -> Optional[Dict[str, Any]]:
        """Executa somente o argv read-only declarado pelo adaptador."""
        argv = plan.get("safe_argv")
        if not isinstance(argv, list) or not argv or not all(
                isinstance(part, str) and part for part in argv):
            return None
        if any("\x00" in part for part in argv):
            return {"returncode": None, "error": "argv_invalid", "executed": False}
        try:
            result = subprocess.run(
                argv, cwd=plan.get("cwd") or None, capture_output=True,
                text=True, timeout=timeout, shell=False,
            )
        except subprocess.TimeoutExpired:
            return {"returncode": None, "error": "timeout", "executed": False}
        except OSError as exc:
            return {"returncode": None, "error": type(exc).__name__, "executed": False}
        return {
            "returncode": result.returncode,
            "stdout": (result.stdout or "")[-4000:],
            "stderr": (result.stderr or "")[-2000:],
            "argv": argv,
            "read_only": True,
            "executed": True,
        }

    def _default_handler(self, action: Dict[str, Any], state: ProductionState,
                         allow_safe_checks: bool = False) -> Dict[str, Any]:
        kind = action["kind"]
        if kind == "specify":
            spec_id = "spec-" + hashlib.sha256(state.goal.encode()).hexdigest()[:12]
            state.spec_id = spec_id
            state.stage = "spec"
            return {"status": "completed", "spec_id": spec_id,
                    "criteria": ["licença verificada", "dependências explícitas",
                                 "evidência antes da entrega", "sem execução não autorizada"]}
        if kind == "route":
            adapter = self._select_adapter(state)
            if adapter is None:
                state.status = "blocked"
                state.limitations.append("nenhum adaptador pronto para o objetivo")
                return {"status": "blocked", "reason": "no_adapter"}
            state.selected_adapter = adapter["action_id"].split(":", 1)[1]
            state.stage = "execute"
            return {"status": "completed", "adapter": state.selected_adapter}
        if kind == "execute":
            if not state.selected_adapter:
                state.status = "blocked"
                state.limitations.append("execução sem adaptador roteado")
                return {"status": "blocked", "reason": "no_selected_adapter"}
            from integrations.external_skills import plan as adapter_plan
            plan = adapter_plan(state.selected_adapter, state.goal,
                                consent=state.consent, registry=self.registry)
            if allow_safe_checks:
                safe = self._safe_check(plan)
                if safe is not None:
                    plan["safe_check"] = safe
            state.execution_plan = plan
            if plan.get("status") == "consent_required":
                state.status = "awaiting_consent"
                state.stage = "awaiting_consent"
                state.limitations.append(plan.get("reason", "consentimento necessário"))
                return plan
            if plan.get("status") != "planned":
                state.status = "blocked"
                state.limitations.extend(plan.get("missing", []) or [plan.get("reason", "plano bloqueado")])
                return plan
            state.stage = "verify"
            return plan
        if kind == "verify":
            plan = state.execution_plan or {}
            safe = plan.get("safe_check")
            safe_ok = True if not isinstance(safe, dict) else safe.get("returncode") == 0
            verified = (plan.get("status") == "planned"
                        and bool(plan.get("argv") or plan.get("mode"))
                        and safe_ok)
            if not verified:
                state.status = "blocked"
                state.stage = "blocked"
                state.limitations.append(
                    "verificação falhou; corrija o plano/check antes de retomar")
                return {"status": "blocked", "verified": False,
                        "gates": plan.get("gates", []),
                        "safe_returncode": (safe or {}).get("returncode")
                        if isinstance(safe, dict) else None}
            state.stage = "reflect"
            return {"status": "completed", "verified": True,
                    "gates": plan.get("gates", [])}
        if kind == "reflect":
            lesson = (f"Produção {state.production_id}: adaptador "
                      f"{state.selected_adapter or 'nenhum'}; "
                      f"plano {'presente' if state.execution_plan else 'ausente'}; "
                      f"evidência {len(state.evidence)}.")
            state.stage = "deliver"
            return {"status": "completed", "lesson": lesson}
        if kind == "deliver":
            state.status = "completed"
            state.stage = "complete"
            return {"status": "completed", "receipt": True}
        if kind == "consent":
            state.status = "awaiting_consent"
            state.stage = "awaiting_consent"
            return {"status": "awaiting_consent",
                    "reason": "consentimento explícito necessário para o adaptador"}
        state.status = "blocked"
        return {"status": "blocked", "reason": "ação de parada"}

    def step(self, state: ProductionState,
             handler: Callable[[Dict[str, Any], ProductionState], Dict[str, Any]] | None = None,
             allow_safe_checks: bool = False) -> Dict[str, Any]:
        if state.status not in {"active"}:
            return {"status": state.status, "state": state.to_dict(),
                    "executed": False, "reason": "produção não está ativa"}
        if state.budget <= 0 or len(state.history) >= self.max_steps:
            state.status = "budget_exhausted"
            state.limitations.append("orçamento de passos esgotado")
            return {"status": "budget_exhausted", "state": state.to_dict(),
                    "executed": False}
        candidates = self.candidates(state)
        decision = self.attention.evaluate(state.goal, state.attention_state(), candidates)
        selected = decision.get("selected")
        if selected is None:
            state.status = "blocked"
            state.limitations.append("nenhuma ação elegível")
            return {"status": "blocked", "state": state.to_dict(),
                    "decision": decision, "executed": False}
        action = next((c for c in candidates if c["action_id"] == selected), None)
        if action is None:
            state.status = "blocked"
            return {"status": "blocked", "state": state.to_dict(),
                    "decision": decision, "executed": False}
        state.budget = max(0.0, state.budget - float(action.get("cost", 0.0)))
        state.cost_spent += float(action.get("cost", 0.0))
        stage_before = state.stage
        if handler is None:
            result = self._default_handler(action, state, allow_safe_checks)
        else:
            result = handler(action, state)
        state.evidence.append({"step": len(state.history) + 1,
                               "action": selected, "kind": action["kind"],
                               "result": result})
        state.history.append({
            "step": len(state.history) + 1,
            "action": selected,
            "kind": action["kind"],
            "stage_before": stage_before,
            "attention": {"selected": selected, "weights": dict(decision.get("weights", {}))},
            "result_status": result.get("status"),
        })
        self._record(state, selected, result)
        if state.budget <= 0 and state.status == "active":
            state.status = "budget_exhausted"
            state.limitations.append("orçamento de passos esgotado")
        return {"status": result.get("status", "completed"),
                "state": state.to_dict(), "decision": decision,
                "action": action, "result": result, "executed": False}

    def _run_state(self, state: ProductionState, *,
                   handler: Callable[[Dict[str, Any], ProductionState], Dict[str, Any]] | None,
                   max_steps: int | None, allow_safe_checks: bool,
                   persist: bool) -> Dict[str, Any]:
        limit = self.max_steps if max_steps is None else max_steps
        if type(limit) is not int or not 1 <= limit <= 32:
            raise ValueError("max_steps deve estar entre 1 e 32")
        steps = []
        for _ in range(limit):
            if state.status != "active":
                break
            outcome = self.step(state, handler=handler,
                                allow_safe_checks=allow_safe_checks)
            if persist:
                self.store.save(state)
            steps.append({"status": outcome.get("status"),
                          "action": (outcome.get("action") or {}).get("action_id")
                          if isinstance(outcome.get("action"), dict) else None})
            if outcome.get("status") in {"blocked", "awaiting_consent"}:
                break
        if persist:
            self.store.save(state)
        receipt = self.receipt(state, steps=steps)
        if persist:
            receipt["state_path"] = self.store.path_for(state.production_id)
            receipt["persisted"] = True
        return receipt

    def run(self, goal: str, *, risk_level: str = "low", budget: float = 8.0,
            consent: bool = False,
            handler: Callable[[Dict[str, Any], ProductionState], Dict[str, Any]] | None = None,
            max_steps: int | None = None,
            allow_safe_checks: bool = False,
            persist: bool = False) -> Dict[str, Any]:
        """Executa o ciclo de planejamento/gates; não executa terceiros.

        ``allow_safe_checks`` permite apenas o ``safe_argv`` read-only
        declarado pelo adaptador; render, OAuth e coletores continuam fora.
        ``persist`` grava o estado fora do repositório para retomada.
        """
        state = self._new_state(goal, risk_level=risk_level, budget=budget, consent=consent)
        return self._run_state(state, handler=handler, max_steps=max_steps,
                               allow_safe_checks=allow_safe_checks, persist=persist)

    def resume(self, production_id: str, *, consent: bool | None = None,
               budget: float | None = None,
               handler: Callable[[Dict[str, Any], ProductionState], Dict[str, Any]] | None = None,
               max_steps: int | None = None,
               allow_safe_checks: bool = False,
               persist: bool = True) -> Dict[str, Any]:
        """Retoma uma produção persistida; não recria o histórico."""
        state = self.store.load(production_id)
        if consent is True:
            state.consent = True
            if state.status == "awaiting_consent":
                state.status = "active"
                state.stage = "execute"
        if budget is not None:
            if (isinstance(budget, bool) or not isinstance(budget, (int, float))
                    or not math.isfinite(budget) or budget <= 0):
                raise ValueError("budget de retomada deve ser positivo")
            state.budget += float(budget)
            if state.status == "budget_exhausted":
                state.status = "active"
        if state.status != "active":
            receipt = self.receipt(state)
            receipt["state_path"] = self.store.path_for(production_id)
            receipt["persisted"] = True
            return receipt
        return self._run_state(state, handler=handler, max_steps=max_steps,
                               allow_safe_checks=allow_safe_checks, persist=persist)

    def list(self) -> List[Dict[str, Any]]:
        """Lista produções persistidas, sem carregar payloads no contexto."""
        return self.store.list()

    def receipt(self, state: ProductionState, *, steps: List[Dict[str, Any]] | None = None
                ) -> Dict[str, Any]:
        return {
            "status": state.status,
            "production_id": state.production_id,
            "goal": state.goal,
            "stage": state.stage,
            "risk_level": state.risk_level,
            "budget": round(state.budget, 4),
            "cost_spent": round(state.cost_spent, 4),
            "selected_adapter": state.selected_adapter,
            "execution_plan": state.execution_plan,
            "evidence": list(state.evidence),
            "limitations": list(state.limitations),
            "history": list(state.history),
            "steps": steps or [],
            "confidence_promoted": False,
            "external_validation": False,
            "human_review_required": True,
            "policy": "atenção executiva determinística; execução externa exige autorização",
        }

    def _record(self, state: ProductionState, action: str, result: Dict[str, Any]) -> None:
        if self.bus is None:
            return
        payload = {"production_id": state.production_id, "action": action,
                   "stage": state.stage, "status": result.get("status"),
                   "evidence_count": len(state.evidence),
                   "confidence_promoted": False}
        try:
            if hasattr(self.bus, "publish"):
                self.bus.publish("production.step", payload, source_agent="marceloclaro.production")
            memory = getattr(self.bus, "memory", None)
            if memory is not None and hasattr(memory, "record_observation"):
                memory.record_observation("marceloclaro.production", state.goal[:2000], payload)
        except (OSError, RuntimeError, ValueError, TypeError):
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="production-center", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("adapters")
    sub.add_parser("list")
    plan_cmd = sub.add_parser("plan")
    plan_cmd.add_argument("goal")
    plan_cmd.add_argument("--risk", choices=("low", "medium", "high"), default="low")
    plan_cmd.add_argument("--budget", type=float, default=8.0)
    plan_cmd.add_argument("--consent", action="store_true")
    run_cmd = sub.add_parser("run")
    run_cmd.add_argument("goal")
    run_cmd.add_argument("--risk", choices=("low", "medium", "high"), default="low")
    run_cmd.add_argument("--budget", type=float, default=8.0)
    run_cmd.add_argument("--consent", action="store_true")
    run_cmd.add_argument("--safe-checks", action="store_true",
                         help="executa apenas checagens read-only declaradas")
    run_cmd.add_argument("--persist", action="store_true",
                         help="grava o estado para retomada")
    resume_cmd = sub.add_parser("resume")
    resume_cmd.add_argument("production_id")
    resume_cmd.add_argument("--consent", action="store_true")
    resume_cmd.add_argument("--budget", type=float)
    resume_cmd.add_argument("--safe-checks", action="store_true")
    resume_cmd.add_argument("--max-steps", type=int)
    args = parser.parse_args(argv)
    center = ProductionCenter()
    try:
        if args.command == "status":
            payload = center.status()
        elif args.command == "adapters":
            payload = center.status()
        elif args.command == "list":
            payload = {"status": "completed", "productions": center.list()}
        elif args.command == "plan":
            payload = center.plan(args.goal, risk_level=args.risk,
                                  budget=args.budget, consent=args.consent)
        elif args.command == "resume":
            payload = center.resume(
                args.production_id,
                consent=True if args.consent else None,
                budget=args.budget,
                allow_safe_checks=args.safe_checks,
                max_steps=args.max_steps,
            )
        else:
            payload = center.run(args.goal, risk_level=args.risk,
                                 budget=args.budget, consent=args.consent,
                                 allow_safe_checks=args.safe_checks,
                                 persist=args.persist)
    except (ValueError, OSError) as exc:
        payload = {"status": "blocked", "error": str(exc), "executed": False}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") in {"ready", "planned", "completed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
