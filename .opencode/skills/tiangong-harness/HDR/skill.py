"""Skill Tiangong HDR — delega ao MCP local `integrations.tiangong_mcp`.

A skill não simula reconhecimento: `recognize` retorna `unavailable` enquanto o
backend QNN não for observado. A validação, o pré-processamento PNG/pixels e a
comparação de vetores são determinísticos e executados localmente.
"""

from __future__ import annotations

from typing import Any

from integrations.tiangong_mcp import BASE_LIMITATIONS, APP_LIMITATIONS, hdr_handler


def validate_input(input_data: dict) -> dict:
    """Valida e executa a ação HDR conforme o contrato do MCP local."""
    if not isinstance(input_data, dict):
        return {
            "status": "error",
            "technique": None,
            "result": {"code": "invalid_input", "message": "entrada deve ser objeto"},
            "evidence": {},
            "limitations": ["entrada deve ser objeto JSON"],
        }
    return hdr_handler(
        action=input_data.get("action"),
        image_base64=input_data.get("image_base64"),
        pixels=input_data.get("pixels"),
        image_path=input_data.get("image_path"),
        left=input_data.get("left"),
        right=input_data.get("right"),
        metadata=input_data.get("metadata"),
    )


def execute_harness(input_data: dict) -> dict:
    """Alias explícito: a skill executa o mesmo contrato validado do MCP."""
    return validate_input(input_data)


def get_limitations() -> list[str]:
    """Limitações observadas e declaradas para HDR."""
    return list(BASE_LIMITATIONS) + list(APP_LIMITATIONS["HDR"])
