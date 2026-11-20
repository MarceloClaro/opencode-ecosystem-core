"""MCP stdio server for the dependency-free quantum optimization harness.

Local tools never use the network. ``qaoa_optimize_gjq`` is an explicit
external-effect tool: its schema requires per-call confirmation and bounded
job/shot counts, while the underlying adapter still enforces the credential
and provider-reported hardware gates. This module uses only the Python
standard library so local inspection does not require installing an MCP SDK.
"""
from __future__ import annotations

import json
import sys
from typing import Any, Callable

from integrations import quantum_optimization as qo


SERVER_NAME = "quantum-optimization"
SERVER_VERSION = "0.1.0"
PROTOCOL_VERSION = "2024-11-05"
MAX_REQUEST_BYTES = 1_048_576


_QUBO_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "name", "num_variables", "constant", "linear", "quadratic"],
    "properties": {
        "schema_version": {"type": "integer", "const": 1},
        "name": {"type": "string", "minLength": 1, "maxLength": 120},
        "num_variables": {"type": "integer", "minimum": 1, "maximum": qo.MAX_QAOA_VARIABLES},
        "constant": {"type": "number"},
        "linear": {"type": "array", "items": {"type": "number"}},
        "quadratic": {
            "type": "array",
            "items": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "prefixItems": [
                    {"type": "integer", "minimum": 0},
                    {"type": "integer", "minimum": 0},
                    {"type": "number"},
                ],
            },
        },
    },
}


def _object_schema(properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": required,
    }


_TOOLS: list[dict[str, Any]] = [
    {
        "name": "quantum_catalog",
        "description": "Catálogo estático de frameworks/fontes; não consulta rede, credenciais ou hardware.",
        "inputSchema": _object_schema({}, []),
        "annotations": {"readOnlyHint": True, "destructiveHint": False,
                         "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "qubo_inspect",
        "description": "Valida QUBO v1 e retorna hash, Ising e baseline clássico exato quando n<=16; local e sem rede.",
        "inputSchema": _object_schema(
            {"problem": _QUBO_SCHEMA,
             "assignment": {"type": "array", "items": {"type": "integer", "enum": [0, 1]} }},
            ["problem"],
        ),
        "annotations": {"readOnlyHint": True, "destructiveHint": False,
                         "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "qaoa_prepare",
        "description": "Prepara QUBO→Ising, IR QAOA e limites de shots/jobs; não executa circuito nem acessa rede.",
        "inputSchema": _object_schema(
            {"problem": _QUBO_SCHEMA,
             "depth": {"type": "integer", "minimum": 1, "maximum": qo.MAX_QAOA_DEPTH},
             "shots": {"type": "integer", "minimum": 1, "maximum": qo.MAX_REMOTE_SHOTS},
             "max_evaluations": {"type": "integer", "minimum": 1, "maximum": qo.MAX_REMOTE_EVALUATIONS}},
            ["problem"],
        ),
        "annotations": {"readOnlyHint": True, "destructiveHint": False,
                         "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "qaoa_optimize_gjq",
        "description": (
            "EFEITO EXTERNO: submete avaliações QAOA ao GJQ. Exige confirm_remote=true nesta chamada, "
            "backend exato, limites explícitos, GJQ_API_KEY e backend identificado pelo provedor como hardware. "
            "Jobs/shots não limitam custo monetário; falhas podem deixar submissão incerta."
        ),
        "inputSchema": _object_schema(
            {"problem": _QUBO_SCHEMA,
             "backend_name": {"type": "string", "minLength": 1, "maxLength": 120},
             "shots": {"type": "integer", "minimum": 1, "maximum": qo.MAX_REMOTE_SHOTS},
             "max_evaluations": {"type": "integer", "minimum": 1, "maximum": qo.MAX_REMOTE_EVALUATIONS},
             "max_total_shots": {"type": "integer", "minimum": 1, "maximum": qo.MAX_REMOTE_TOTAL_SHOTS},
             "confirm_remote": {"type": "boolean"},
             "depth": {"type": "integer", "minimum": 1, "maximum": qo.MAX_QAOA_DEPTH},
             "seed": {"type": "integer"}},
            ["problem", "backend_name", "shots", "max_evaluations", "max_total_shots", "confirm_remote"],
        ),
        "annotations": {"readOnlyHint": False, "destructiveHint": False,
                         "idempotentHint": False, "openWorldHint": True},
    },
]


def _inspect(arguments: dict[str, Any]) -> dict[str, Any]:
    qubo = qo.parse_qubo(arguments["problem"])
    baseline = (qo.exact_classical_baseline(qubo)
                if qubo.num_variables <= qo.MAX_EXACT_VARIABLES else None)
    result: dict[str, Any] = {
        "problem_sha256": qubo.problem_sha256,
        "name": qubo.name,
        "num_variables": qubo.num_variables,
        "num_quadratic_terms": len(qubo.quadratic),
        "ising": qo.qubo_to_ising(qubo),
        "classical_baseline": baseline,
        "network": False,
    }
    if "assignment" in arguments:
        result["assignment_energy"] = qubo.energy(arguments["assignment"])
    return {
        "status": "success",
        "app": "quantum-optimization",
        "technique": "local-QUBO-inspection",
        "result": result,
        "evidence": {"method": "local-deterministic-inspection", "network": False},
        "limitations": [
            "Baseline exato é clássico e só é calculado até 16 variáveis.",
            "Nenhuma execução de circuito ou hardware ocorreu.",
        ],
    }


def _prepare(arguments: dict[str, Any]) -> dict[str, Any]:
    return qo.qaoa_plan(
        arguments["problem"],
        depth=arguments.get("depth", 1),
        shots=arguments.get("shots", 1024),
        max_evaluations=arguments.get("max_evaluations", qo.MAX_REMOTE_EVALUATIONS),
    )


def _optimize(arguments: dict[str, Any]) -> dict[str, Any]:
    return qo.run_gjq_qaoa(
        arguments["problem"],
        backend_name=arguments["backend_name"],
        shots=arguments["shots"],
        max_evaluations=arguments["max_evaluations"],
        max_total_shots=arguments["max_total_shots"],
        confirm_remote=arguments["confirm_remote"],
        depth=arguments.get("depth", 1),
        seed=arguments.get("seed", 42),
    )


_HANDLERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "quantum_catalog": lambda _arguments: qo.quantum_catalog(),
    "qubo_inspect": _inspect,
    "qaoa_prepare": _prepare,
    "qaoa_optimize_gjq": _optimize,
}


class QuantumOptimizationMCPServer:
    """Small newline-delimited JSON-RPC transport with bounded input."""

    def __init__(self) -> None:
        self._initialized = False

    @staticmethod
    def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id,
                "error": {"code": code, "message": message}}

    @staticmethod
    def _success(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def handle(self, message: Any) -> dict[str, Any] | None:
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            return self._error(None, -32600, "Invalid Request")

        method = message.get("method")
        if not isinstance(method, str) or not method:
            return self._error(message.get("id"), -32600, "Invalid Request")
        request_id = message.get("id")
        is_notification = "id" not in message
        if is_notification:
            if method == "notifications/initialized":
                self._initialized = True
            # Notifications, including unknown notifications, never receive a response.
            return None
        if isinstance(request_id, bool) or not isinstance(request_id, (str, int, float, type(None))):
            return self._error(None, -32600, "Invalid Request")

        params = message.get("params", {})
        if not isinstance(params, dict):
            return self._error(request_id, -32602, "params must be an object")

        if method == "initialize":
            requested = params.get("protocolVersion", PROTOCOL_VERSION)
            if not isinstance(requested, str):
                return self._error(request_id, -32602, "protocolVersion must be text")
            # Return the version supported by this server. MCP clients negotiate
            # against the version in the initialize result.
            return self._success(request_id, {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            })
        if method == "ping":
            return self._success(request_id, {})
        if method == "tools/list":
            return self._success(request_id, {"tools": _TOOLS})
        if method == "tools/call":
            name, arguments = params.get("name"), params.get("arguments", {})
            if not isinstance(name, str) or name not in _HANDLERS:
                return self._error(request_id, -32602, "Unknown tool")
            if not isinstance(arguments, dict):
                return self._error(request_id, -32602, "Tool arguments must be an object")
            schema = next(tool["inputSchema"] for tool in _TOOLS if tool["name"] == name)
            allowed = set(schema["properties"])
            required = set(schema.get("required", []))
            if set(arguments) - allowed or not required.issubset(arguments):
                return self._error(request_id, -32602, "Tool arguments do not match inputSchema")
            try:
                payload = _HANDLERS[name](arguments)
                encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
                return self._success(request_id, {
                    "content": [{"type": "text", "text": encoded}],
                    "structuredContent": payload,
                    "isError": payload.get("status") in {"blocked", "error", "unavailable", "partial"},
                })
            except qo.QuantumContractError as exc:
                payload = {"status": "error", "app": "quantum-optimization",
                           "result": {"code": "invalid_request", "message": str(exc)},
                           "evidence": {"network": False},
                           "limitations": ["A requisição foi rejeitada antes de qualquer execução."]}
                return self._success(request_id, {
                    "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
                    "structuredContent": payload,
                    "isError": True,
                })
            except Exception:
                # Do not emit tracebacks, provider messages, environment values,
                # or account state over the MCP channel.
                payload = {"status": "error", "app": "quantum-optimization",
                           "result": {"code": "internal_error", "message": "falha interna sem detalhes sensíveis."},
                           "evidence": {"network": False},
                           "limitations": ["Consulte o log local protegido; nenhuma credencial é retornada."]}
                return self._success(request_id, {
                    "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
                    "structuredContent": payload,
                    "isError": True,
                })
        return self._error(request_id, -32601, "Method not found")

    def run(self, stdin=None, stdout=None) -> int:
        input_stream = stdin or sys.stdin
        output_stream = stdout or sys.stdout
        while True:
            line = input_stream.readline(MAX_REQUEST_BYTES + 2)
            if not line:
                return 0
            if len(line.encode("utf-8", errors="replace")) > MAX_REQUEST_BYTES or (
                    not line.endswith("\n") and len(line) >= MAX_REQUEST_BYTES + 2):
                while line and not line.endswith("\n"):
                    line = input_stream.readline(MAX_REQUEST_BYTES + 2)
                response = self._error(None, -32700, "Request too large")
            else:
                try:
                    message = json.loads(line)
                    response = self.handle(message)
                except (json.JSONDecodeError, UnicodeError):
                    response = self._error(None, -32700, "Parse error")
            if response is not None:
                output_stream.write(json.dumps(response, ensure_ascii=False, allow_nan=False,
                                               separators=(",", ":")) + "\n")
                output_stream.flush()


def create_server() -> QuantumOptimizationMCPServer:
    """Construct without reading credentials, importing optional SDKs, or I/O."""
    return QuantumOptimizationMCPServer()


def main() -> int:
    return create_server().run()


if __name__ == "__main__":
    raise SystemExit(main())
