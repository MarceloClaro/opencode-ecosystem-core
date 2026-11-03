"""R1019 — cadeia do agente primário: Ollama Cloud → OpenAI → OpenCode Go."""

from __future__ import annotations

import json
from pathlib import Path

from integrations.opencode_cli import build_config


ROOT = Path(__file__).resolve().parents[1]
PRIMARY_MODEL = "ollama-cloud/deepseek-v4.1-flash"
EXPECTED_FALLBACKS = [
    "openai/gpt-6.1-sol",
    "opencode-go/deepseek-v4.1-flash",
    "opencode-go/deepseek-v4-pro",
]


def primary(config: dict) -> dict:
    return config["agent"]["marceloclaro"]


def test_primary_agent_uses_ollama_cloud_head() -> None:
    config = build_config()
    agent = primary(config)
    assert agent.get("model") == "ollama-cloud/deepseek-v4.1-flash"
    assert PRIMARY_MODEL == agent.get("model")
    assert agent.get("options", {}).get("model_economy", {}).get("head") == PRIMARY_MODEL


def test_primary_fallbacks_prefer_openai_then_opencode_go() -> None:
    fallbacks = primary(build_config()).get("options", {}).get("model_fallbacks", [])
    assert fallbacks[:2] == [
        "openai/gpt-6.1-sol",
        "opencode-go/deepseek-v4.1-flash",
    ]
    assert EXPECTED_FALLBACKS == fallbacks


def test_global_model_and_other_agents_are_unchanged() -> None:
    config = build_config()
    assert config["model"] == "ollama-local/llama3.2"
    assert sum(
        1 for agent in config["agent"].values()
        if agent.get("model") == PRIMARY_MODEL
    ) == 1


def test_openai_provider_declares_fallback_model() -> None:
    config = build_config()
    models = config["provider"]["openai"]["models"]
    assert "gpt-6.1-sol" in models
    assert models["gpt-6.1-sol"]["name"] == "GPT-6.1 Sol"


def test_config_is_reproducible_and_uses_env_placeholders() -> None:
    config = build_config()
    current = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    assert current == config
    assert config["provider"]["openai"]["options"]["apiKey"] == "{env:OPENAI_API_KEY}"
    assert config["provider"]["opencode-go"]["options"]["apiKey"] == "{env:OPENCODE_API_KEY}"
