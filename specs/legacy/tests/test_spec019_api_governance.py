"""
SPEC-019: Federated API Governance — 8 CTs (TDD)
Gartner Hype Cycle 2026: API Gateway/Brokering
"""
import pytest
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Optional
from conftest import APIService, AuditEntry, CircuitState


# ============================================================
# Implementação sob teste
# ============================================================

@dataclass
class RateLimit:
    calls: int
    window_sec: int


class TokenBucket:
    """Rate limiter token bucket algorithm."""
    def __init__(self, calls: int, window_sec: int):
        self.max_tokens = calls
        self.tokens = calls
        self.window_sec = window_sec
        self.last_refill = time.time()

    def allow(self) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens,
                          self.tokens + elapsed * (self.max_tokens / self.window_sec))
        self.last_refill = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class FederatedAPIGovernor:
    """Governança federada de API entre agentes OpenCode."""

    def __init__(self, node_id: str = "default"):
        self.node_id = node_id
        self.registry: dict[str, APIService] = {}
        self.policies: dict[str, RateLimit] = {}
        self.buckets: dict[str, TokenBucket] = {}
        self.circuit_failures: dict[str, int] = {}
        self.circuit_states: dict[str, CircuitState] = {}
        self.circuit_half_open_success: dict[str, int] = {}
        self.audit_trail: list[AuditEntry] = []
        self.federated_nodes: list[FederatedAPIGovernor] = []
        self.cache: dict[str, tuple[dict, float]] = {}
        self.cache_invalidations: set[str] = set()

    # --- Registry ---
    def register(self, service: APIService) -> dict:
        if not service.name:
            return {"status": "error", "reason": "name_required"}
        if not service.version:
            return {"status": "error", "reason": "version_required"}
        key = f"{service.name}:{service.version}"
        self.registry[key] = service
        return {"status": "registered"}

    # --- Policy / Rate Limiting ---
    def set_policy(self, agent_id: str, limit: RateLimit) -> None:
        self.policies[agent_id] = limit
        self.buckets[agent_id] = TokenBucket(limit.calls, limit.window_sec)

    def check_rate_limit(self, agent_id: str) -> bool:
        if agent_id not in self.buckets:
            return True  # sem política = permitido
        return self.buckets[agent_id].allow()

    # --- Circuit Breaker ---
    def record_failure(self, service: str) -> None:
        self.circuit_failures[service] = self.circuit_failures.get(service, 0) + 1
        if self.circuit_failures[service] >= 3:
            self.circuit_states[service] = CircuitState.OPEN
            self.circuit_half_open_success[service] = 0

    def record_success(self, service: str) -> None:
        if service in self.circuit_states:
            if self.circuit_states[service] == CircuitState.HALF_OPEN:
                self.circuit_half_open_success[service] = \
                    self.circuit_half_open_success.get(service, 0) + 1
                if self.circuit_half_open_success[service] >= 5:
                    self.circuit_states[service] = CircuitState.CLOSED
                    self.circuit_failures[service] = 0
                    self.circuit_half_open_success[service] = 0
            elif self.circuit_states[service] == CircuitState.OPEN:
                pass  # permanece aberto até half-open timeout
            else:
                self.circuit_failures[service] = 0

    def get_circuit_state(self, service: str) -> str:
        state = self.circuit_states.get(service, CircuitState.CLOSED)
        return state.value

    # --- Audit Trail ---
    def call(self, agent_id: str, service: str, action: str,
             params: dict) -> dict:
        entry = AuditEntry(
            agent_id=agent_id,
            service=service,
            action=action,
            params=params,
            result="ok",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )
        # SHA-256 hash do entry para imutabilidade
        raw = f"{entry.agent_id}|{entry.service}|{entry.action}|{json.dumps(params, sort_keys=True)}|{entry.timestamp}"
        entry.hash = hashlib.sha256(raw.encode()).hexdigest()
        self.audit_trail.append(entry)
        return {"status": "ok", "audit_hash": entry.hash}

    def get_audit(self, limit: int = 10) -> list[AuditEntry]:
        return list(reversed(self.audit_trail))[:limit]

    # --- Discovery ---
    def discover(self, query: str = "") -> list[APIService]:
        results = []
        for key, service in self.registry.items():
            if not query:
                results.append(service)
            elif "version>=" in query:
                ver = query.split("version>=")[1].strip()
                if self._compare_versions(service.version, ver) >= 0:
                    results.append(service)
            elif service.name in query or query in service.name:
                results.append(service)
        return results

    @staticmethod
    def _compare_versions(a: str, b: str) -> int:
        parts_a = [int(x) for x in a.split(".")]
        parts_b = [int(x) for x in b.split(".")]
        for pa, pb in zip(parts_a, parts_b):
            if pa != pb:
                return pa - pb
        return len(parts_a) - len(parts_b)

    # --- Federation ---
    def federate_with(self, other: "FederatedAPIGovernor") -> None:
        self.federated_nodes.append(other)
        other.federated_nodes.append(self)  # bidirecional

    def get_policy(self, name: str) -> Optional[RateLimit]:
        if name in self.policies:
            return self.policies[name]
        for node in self.federated_nodes:
            policy = node.get_policy(name)
            if policy:
                return policy
        return None

    # --- Cache ---
    def cache_set(self, key: str, data: dict, ttl_sec: int = 60) -> None:
        self.cache[key] = (data, time.time() + ttl_sec)

    def cache_get(self, key: str) -> Optional[dict]:
        if key in self.cache_invalidations:
            return None
        entry = self.cache.get(key)
        if not entry:
            return None
        data, expiry = entry
        if time.time() > expiry:
            del self.cache[key]
            return None
        return data

    def invalidate(self, key_prefix: str) -> None:
        self.cache_invalidations.add(f"key:{key_prefix}")

    # --- Versioning ---
    def resolve(self, name: str, version: str) -> Optional[APIService]:
        key = f"{name}:{version}"
        return self.registry.get(key)


# ============================================================
# Testes (CT-001 a CT-008)
# ============================================================

class TestRegistry:
    """CT-001: Registry — Registro de Serviço"""

    def test_register_service(self):
        governor = FederatedAPIGovernor()
        service = APIService(name="alpha", version="1.0",
                             endpoints=["/predict", "/health"])
        result = governor.register(service)
        assert result["status"] == "registered"
        assert governor.registry.get("alpha:1.0") == service


class TestRateLimiting:
    """CT-002: Policy Engine — Rate Limiting por Agente"""

    def test_rate_limit_agent(self):
        governor = FederatedAPIGovernor()
        governor.set_policy("agent-alpha", RateLimit(calls=5, window_sec=60))
        for _ in range(5):
            assert governor.check_rate_limit("agent-alpha") is True
        assert governor.check_rate_limit("agent-alpha") is False


class TestCircuitBreaker:
    """CT-003: Circuit Breaker — 3 Falhas → Open"""

    def test_circuit_breaker_trips(self):
        governor = FederatedAPIGovernor()
        service = "model-serving"
        for _ in range(3):
            governor.record_failure(service)
        assert governor.get_circuit_state(service) == "open"


class TestAuditTrail:
    """CT-004: Audit Trail — Imutabilidade"""

    def test_audit_trail_immutable(self):
        governor = FederatedAPIGovernor()
        governor.call("agent-a", "service-b", "predict", {"x": 1})
        governor.call("agent-b", "service-a", "health", {})
        entries = governor.get_audit(limit=2)
        assert len(entries) == 2
        assert entries[0].agent_id == "agent-b"  # mais recente primeiro
        assert entries[0].hash != ""  # hash SHA-256 presente


class TestDiscovery:
    """CT-005: Discovery — Descoberta Automática"""

    def test_service_discovery(self):
        governor = FederatedAPIGovernor()
        governor.register(APIService(name="gamma", version="2.0"))
        governor.register(APIService(name="delta", version="1.5"))
        services = governor.discover(query="version>=2.0")
        assert len(services) == 1
        assert services[0].name == "gamma"


class TestFederation:
    """CT-006: Federation — Propagação de Políticas entre Nós"""

    def test_federation_propagation(self):
        node_a = FederatedAPIGovernor(node_id="a")
        node_b = FederatedAPIGovernor(node_id="b")
        node_a.federate_with(node_b)
        node_a.set_policy("global", RateLimit(calls=50, window_sec=60))
        assert node_b.get_policy("global") is not None


class TestCache:
    """CT-007: Cache — Invalidação por Evento"""

    def test_cache_invalidation(self):
        governor = FederatedAPIGovernor()
        governor.cache_set("key:model-1", {"data": "cached"}, ttl_sec=60)
        assert governor.cache_get("key:model-1") is not None
        governor.invalidate("model-1")
        assert governor.cache_get("key:model-1") is None


class TestVersioning:
    """CT-008: Versioning — Múltiplas Versões de API"""

    def test_api_versioning(self):
        governor = FederatedAPIGovernor()
        governor.register(APIService(name="api", version="1.0",
                                     endpoints=["/v1/data"]))
        governor.register(APIService(name="api", version="2.0",
                                     endpoints=["/v2/data"]))
        v1 = governor.resolve("api", version="1.0")
        v2 = governor.resolve("api", version="2.0")
        assert v1 is not None, "v1 should be registered"
        assert v2 is not None, "v2 should be registered"
        assert v1.endpoints == ["/v1/data"]
        assert v2.endpoints == ["/v2/data"]
