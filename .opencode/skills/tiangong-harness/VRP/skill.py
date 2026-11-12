"""Skill Tiangong VRP — delega ao MCP local `integrations.tiangong_mcp`.

`solve` usa heurística clássica determinística (vizinho mais próximo + 2-opt),
sem alegar QAOA, vantagem quântica ou otimalidade. `upload` é indisponível.
"""

from __future__ import annotations

from integrations.tiangong_mcp import BASE_LIMITATIONS, APP_LIMITATIONS, vrp_handler


def validate_input(input_data: dict) -> dict:
    """Valida e executa a ação VRP conforme o contrato do MCP local."""
    if not isinstance(input_data, dict):
        return {
            "status": "error",
            "technique": None,
            "result": {"code": "invalid_input", "message": "entrada deve ser objeto"},
            "evidence": {},
            "limitations": ["entrada deve ser objeto JSON"],
        }
    return vrp_handler(
        action=input_data.get("action"),
        nodes=input_data.get("nodes"),
        vehicles=input_data.get("vehicles"),
        depot=input_data.get("depot"),
        n_vehicles=input_data.get("n_vehicles"),
        capacity=input_data.get("capacity", input_data.get("vehicle_capacity")),
        metadata=input_data.get("metadata"),
    )


def execute_harness(input_data: dict) -> dict:
    """Alias explícito: a skill executa o mesmo contrato validado do MCP."""
    return validate_input(input_data)


def get_limitations() -> list[str]:
    """Limitações observadas e declaradas para VRP."""
    return list(BASE_LIMITATIONS) + list(APP_LIMITATIONS["VRP"])
