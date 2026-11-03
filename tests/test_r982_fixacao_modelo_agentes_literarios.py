"""RED/GREEN — SPEC-982: fixação de modelo da cabeça não pode reintroduzir
o modo de falha de retorno vazio dos agentes literários (SPEC-935-R276).

A governança de custo (SPEC-981) fixa o modelo da cabeça em todo agente sem
modelo declarado. Os agentes literários, porém, foram deliberadamente
removidos de `model:` explícito no R276 porque a fixação explícita fazia o
runtime devolver `task_result` vazio (R271/R277). A cadeia de fallback
continua sendo publicada em `options.model_fallbacks`; apenas a fixação é
suprimida, por categoria e por prefixo declarados na política.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

AGENTES_LITERARIOS = (
    "literary-orchestrator-phd",
    "literary-narratology-architect-phd",
    "literary-style-voice-phd",
    "literary-character-psychology-phd",
    "literary-symbolic-imagery-phd",
    "literary-ethics-trauma-phd",
    "literary-innovation-editorial-phd",
    "literary-research-scholar-phd",
    "literary-smoke-minimal",
    "literary-image-sepia",
    "literary-neurolinguistic-engineering-phd",
)


def test_agentes_literarios_sem_modelo_explicito_no_config():
    """Nenhum agente literário pode receber `model` fixado."""
    from integrations.opencode_cli import build_config

    config = build_config()
    agentes = config["agent"]
    for agent_id in AGENTES_LITERARIOS:
        agent = agentes.get(agent_id)
        assert agent is not None, f"agente literário ausente do config: {agent_id}"
        assert "model" not in agent, (
            f"{agent_id} recebeu model fixado; o runtime literário usa fallback"
        )


def test_cadeia_de_fallback_preservada_para_agentes_literarios():
    """Suprimir a fixação não pode remover a cadeia de fallback."""
    from integrations.opencode_cli import build_config

    config = build_config()
    for agent_id in AGENTES_LITERARIOS:
        opcoes = config["agent"][agent_id].get("options") or {}
        assert opcoes.get("model_fallbacks"), (
            f"{agent_id} ficou sem cadeia de fallback declarada"
        )


def test_agentes_nao_literarios_continuam_com_modelo_fixado():
    """A supressão é delimitada: agentes comuns seguem com cabeça fixada."""
    from integrations.opencode_cli import build_config

    config = build_config()
    assert config["agent"]["coder"].get("model"), "coder ficou sem modelo fixado"
    assert config["agent"]["auditor"].get("model"), "auditor ficou sem modelo fixado"


def test_politica_declara_exclusao_auditavel():
    """A exclusão é declarada no registro, com justificativa, não implícita."""
    from integrations import cost_governance

    registro = cost_governance.load_registry()
    politica = registro.get("policy", {}) or {}
    assert "literary" in (politica.get("no_fix_model_categories") or [])
    assert "literary-" in (politica.get("no_fix_model_prefixes") or [])
    notas = " ".join(politica.get("notes") or []).lower()
    assert "r276" in notas, "a política deve referenciar o contrato R276"


def test_regeneracao_do_opencode_json_mantem_agentes_literarios_sem_modelo():
    """O artefato gerado (opencode.json) é consistente com o construtor."""
    caminho = ROOT / "opencode.json"
    if not caminho.exists():
        return
    config = json.loads(caminho.read_text(encoding="utf-8"))
    for agent_id in AGENTES_LITERARIOS:
        agent = config.get("agent", {}).get(agent_id)
        assert agent is not None, f"{agent_id} ausente do opencode.json"
        assert "model" not in agent, (
            f"{agent_id} consta com model fixado no opencode.json publicado"
        )


def test_modelo_declarado_no_cartao_permanece_autoritativo():
    """Supressão por política não descarta `model` declarado no cartão."""
    from integrations.opencode_cli import build_config

    config = build_config()
    assert config["agent"]["kdp-orchestrator-phd"]["model"] == "opencode/deepseek-v4-pro"


def test_primario_recebe_cadeia_ollama_cloud_openai_opencode_go():
    """R1019: decisão do operador para o primário.

    A regra anterior preservava o modelo global no primário; R1019 a substitui
    por uma cadeia explícita Ollama Cloud → OpenAI → OpenCode Go. Os agentes
    literários continuam sem fixação de modelo, que é o objeto deste arquivo.
    """
    from integrations.opencode_cli import build_config

    config = build_config()
    primary = config["agent"]["marceloclaro"]
    assert primary["model"] == "ollama-cloud/deepseek-v4.1-flash"
    assert primary["options"]["model_fallbacks"][:2] == [
        "openai/gpt-6.1-sol",
        "opencode-go/deepseek-v4.1-flash",
    ]
    assert config["model"] == "ollama-local/llama3.2"
