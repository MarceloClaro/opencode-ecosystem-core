"""R1082: configuração local do perfil literário, sem OpenCode Go."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "opencode.json"
PROFILE = "romance-psicologico-molambudos"
LOCAL_PREFIXES = ("ollama-local/", "litert-lm/")


def test_profile_model_is_local_and_has_no_go_fallback():
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    entry = data["agent"][PROFILE]
    assert entry["model"].startswith(LOCAL_PREFIXES), entry["model"]
    fallbacks = entry.get("options", {}).get("model_fallbacks", [])
    assert len(fallbacks) >= 2
    assert all(item.startswith(LOCAL_PREFIXES) for item in fallbacks), fallbacks
    assert "opencode-go" not in json.dumps(entry, ensure_ascii=False).lower()
    assert entry["options"]["model_economy"]["head"] == entry["model"]


def test_profile_still_validates_after_local_override():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)
    result = orchestrator.agent_profile_action(
        {"operation": "validate", "agent_id": PROFILE}
    )
    assert result["definition_validated"] is True
    assert result["agent_id"] == PROFILE
