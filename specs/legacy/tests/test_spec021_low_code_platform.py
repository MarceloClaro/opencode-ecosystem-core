"""
SPEC-021: Low-Code Agent Platform — 6 CTs (TDD)
Gartner Hype Cycle 2026: Low-Code Application Platforms
"""
import pytest
from dataclasses import dataclass, field
from typing import Any, Optional


# ============================================================
# Exceções
# ============================================================

class SchemaValidationError(Exception):
    """Schema declarativo inválido."""
    pass


class DeployError(Exception):
    """Falha no deploy do pipeline."""
    pass


# ============================================================
# Implementação sob teste
# ============================================================

@dataclass
class AgentNode:
    id: str
    type: str
    params: dict = field(default_factory=dict)


@dataclass
class Connection:
    source: str  # "agent_id.output"
    target: str  # "agent_id.input"


@dataclass
class Pipeline:
    version: str
    agents: list[AgentNode] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)

    def validate(self) -> bool:
        if not self.version:
            return False
        if not self.agents:
            return False
        # Verificar que todas as conexões referenciam agentes existentes
        agent_ids = {a.id for a in self.agents}
        for conn in self.connections:
            src_agent = conn.source.split(".")[0]
            tgt_agent = conn.target.split(".")[0]
            if src_agent not in agent_ids or tgt_agent not in agent_ids:
                return False
        return True


@dataclass
class Deployment:
    pipeline: Pipeline
    status: str = "pending"
    endpoint: Optional[str] = None


@dataclass
class AgentType:
    id: str
    description: str
    inputs: list[dict] = field(default_factory=list)
    outputs: list[dict] = field(default_factory=list)


class LowCodePlatform:
    """Plataforma low-code para composição declarativa de agentes."""

    def __init__(self):
        self.pipelines: list[Pipeline] = []
        self.deployments: list[Deployment] = []
        self.agent_catalog: dict[str, AgentType] = {}

    # --- Schema loading ---
    def load_schema(self, schema: dict) -> Pipeline:
        self._validate_schema(schema)
        pipeline = Pipeline(version=schema.get("version", "1.0"))
        for a in schema.get("agents", []):
            pipeline.agents.append(
                AgentNode(id=a["id"], type=a["type"],
                          params=a.get("params", {}))
            )
        for c in schema.get("connections", []):
            pipeline.connections.append(
                Connection(source=c["from"], target=c["to"])
            )
        self.pipelines.append(pipeline)
        return pipeline

    def _validate_schema(self, schema: dict) -> None:
        if "version" not in schema:
            raise SchemaValidationError("version field is required")
        if "agents" not in schema or not schema["agents"]:
            raise SchemaValidationError(
                "agents field must contain at least one agent"
            )
        for a in schema["agents"]:
            if "id" not in a:
                raise SchemaValidationError("each agent must have an id")
            if "type" not in a:
                raise SchemaValidationError(f"agent '{a.get('id', '?')}' "
                                            f"must have a type")

        # Validar conexões
        agent_ids = {a["id"] for a in schema.get("agents", [])}
        for c in schema.get("connections", []):
            src = c.get("from", "").split(".")[0]
            tgt = c.get("to", "").split(".")[0]
            if src not in agent_ids:
                raise SchemaValidationError(
                    f"connection source '{src}' not found in agents"
                )
            if tgt not in agent_ids:
                raise SchemaValidationError(
                    f"connection target '{tgt}' not found in agents"
                )

    # --- Exportação ---
    def export(self, language: str = "python") -> str:
        if not self.pipelines:
            return ""
        pipeline = self.pipelines[-1]

        if language == "python":
            code = "def pipeline():\n"
            code += "    \"\"\"Pipeline gerado pelo Low-Code Agent Platform.\"\"\"\n"
            code += "    results = {}\n"
            for agent in pipeline.agents:
                params_repr = ", ".join(
                    f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"
                    for k, v in agent.params.items()
                )
                code += f"    results['{agent.id}'] = Agent('{agent.type}'"
                if params_repr:
                    code += f", {params_repr}"
                code += ")\n"
            code += "    return results\n"
            return code
        return ""

    # --- Versioning ---
    def get_history(self, limit: int = 10) -> list[Pipeline]:
        return list(reversed(self.pipelines))[:limit]

    # --- Deploy ---
    def deploy(self, pipeline: Pipeline) -> Deployment:
        if not pipeline.validate():
            raise DeployError("Pipeline validation failed")
        deployment = Deployment(
            pipeline=pipeline,
            status="running",
            endpoint=f"/api/v1/pipelines/{pipeline.version}/{id(pipeline)}"
        )
        self.deployments.append(deployment)
        return deployment

    # --- Discovery ---
    def register_agent_type(self, agent_id: str,
                            config: dict) -> None:
        self.agent_catalog[agent_id] = AgentType(
            id=agent_id,
            description=config.get("description", ""),
            inputs=config.get("inputs", []),
            outputs=config.get("outputs", [])
        )

    def discover_agents(self, filter: str = "") -> list[AgentType]:
        results = []
        for agent in self.agent_catalog.values():
            if not filter:
                results.append(agent)
            elif filter.lower() in agent.description.lower():
                results.append(agent)
        return results


# Schema válido compartilhado entre testes
VALID_SCHEMA = {
    "version": "1.0",
    "agents": [
        {"id": "extractor", "type": "seeker",
         "params": {"query": "AI papers"}},
        {"id": "summarizer", "type": "writer",
         "params": {"style": "academic"}}
    ],
    "connections": [
        {"from": "extractor.output", "to": "summarizer.input"}
    ]
}


# ============================================================
# Testes (CT-001 a CT-006)
# ============================================================

class TestDeclarativePipeline:
    """CT-001: Schema Declarativo — Definição de Pipeline"""

    def test_declarative_pipeline(self):
        lc = LowCodePlatform()
        pipeline = lc.load_schema(VALID_SCHEMA)
        assert len(pipeline.agents) == 2
        assert len(pipeline.connections) == 1
        assert pipeline.validate() is True


class TestInvalidSchema:
    """CT-002: Validação — Schema Inválido"""

    def test_invalid_schema(self):
        lc = LowCodePlatform()
        schema = {"agents": []}  # sem versão
        with pytest.raises(SchemaValidationError):
            lc.load_schema(schema)


class TestCodeExport:
    """CT-003: Exportação — Geração de Código Python"""

    def test_code_export(self):
        lc = LowCodePlatform()
        lc.load_schema(VALID_SCHEMA)
        code = lc.export("python")
        assert "def pipeline():" in code
        assert "extractor" in code
        assert "summarizer" in code
        # Verificar que o código gerado é parseável
        compile(code, "<string>", "exec")


class TestVersioning:
    """CT-004: Versioning — Histórico de Versões"""

    def test_pipeline_versioning(self):
        lc = LowCodePlatform()
        v1_schema = VALID_SCHEMA.copy()
        v1 = lc.load_schema(v1_schema)

        v2_schema = VALID_SCHEMA.copy()
        v2_schema["agents"].append(
            {"id": "reviewer", "type": "critic",
             "params": {"strict": True}}
        )
        v2 = lc.load_schema(v2_schema)

        assert v1.version == "1.0"
        assert v2.version == "1.0"
        history = lc.get_history(limit=2)
        assert len(history) == 2


class TestDeploy:
    """CT-005: Deploy — Pipeline Executável"""

    def test_pipeline_deploy(self):
        lc = LowCodePlatform()
        pipeline = lc.load_schema(VALID_SCHEMA)
        deployment = lc.deploy(pipeline)
        assert deployment.status == "running"
        assert deployment.endpoint is not None


class TestDiscovery:
    """CT-006: Discovery — Catálogo de Agentes"""

    def test_agent_discovery(self):
        lc = LowCodePlatform()
        lc.register_agent_type("seeker", {
            "description": "Academic researcher for scholarly search",
            "inputs": [{"name": "query", "type": "string"}],
            "outputs": [{"name": "papers", "type": "list"}]
        })
        catalog = lc.discover_agents(filter="Academic")
        assert len(catalog) >= 1
        assert catalog[0].id == "seeker"
