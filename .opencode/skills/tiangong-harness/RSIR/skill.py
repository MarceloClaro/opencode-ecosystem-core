"""Skill Tiangong RSIR — delega ao MCP local `integrations.tiangong_mcp`.

`validate` e `features` são locais e determinísticos. `analyze` e `classify`
retornam `unavailable` porque o modelo ViT/QViT não foi observado; nenhum
rótulo ou probabilidade é fabricado.
"""

from __future__ import annotations

from integrations.tiangong_mcp import BASE_LIMITATIONS, APP_LIMITATIONS, rsir_handler


def validate_input(input_data: dict) -> dict:
    """Valida e executa a ação RSIR conforme o contrato do MCP local."""
    if not isinstance(input_data, dict):
        return {
            "status": "error",
            "technique": None,
            "result": {"code": "invalid_input", "message": "entrada deve ser objeto"},
            "evidence": {},
            "limitations": ["entrada deve ser objeto JSON"],
        }
    return rsir_handler(
        action=input_data.get("action"),
        features=input_data.get("features"),
        expected_dim=input_data.get("expected_dim", 768),
        metadata=input_data.get("metadata"),
    )


def execute_harness(input_data: dict) -> dict:
    """Alias explícito: a skill executa o mesmo contrato validado do MCP."""
    return validate_input(input_data)


def get_limitations() -> list[str]:
    """Limitações observadas e declaradas para RSIR."""
    return list(BASE_LIMITATIONS) + list(APP_LIMITATIONS["RSIR"])
