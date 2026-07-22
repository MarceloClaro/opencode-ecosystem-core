"""
Preset: Assistente Pessoal
===========================
Configura um assistente pessoal prestativo com ferramentas úteis.

Uso:
    litert-lm chat gemma-4-E2B-it --preset skills/litert_lm/presets/assistant.py
"""

system_instruction = (
    "Você é um assistente pessoal prestativo, amigável e preciso. "
    "Responda em português brasileiro de forma clara e concisa. "
    "Quando apropriado, use as ferramentas disponíveis para ajudar o usuário."
)


def get_current_time(timezone: str = "America/Sao_Paulo") -> str:
    """Obtém a hora atual em um fuso horário específico.

    Args:
        timezone: Fuso horário (ex.: "America/Sao_Paulo", "UTC", "America/New_York").

    Returns:
        String com a data e hora atual no fuso horário solicitado.
    """
    from datetime import datetime
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(timezone)
        now = datetime.now(tz)
        return now.strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return f"Fuso horário '{timezone}' não reconhecido."


# Lista de ferramentas exportada para o LiteRT-LM
tools = [get_current_time]
