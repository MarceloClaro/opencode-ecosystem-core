"""Plano validado para PortSwigger Burp MCP em Ubuntu/WSL2 (R1249).

Somente lê manifesto do Core. Não baixa, instala, inicia Burp ou conecta ao MCP.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MANIFEST = "federation/burp-wsl2-adaptation-r1249.json"
SOURCE_COMMIT = "291034081160bc944b6df3eccd60c6fc99b477e1"
ENDPOINT = "http://127.0.0.1:9876/mcp"


def load_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Validate and return the selected direct Streamable HTTP path."""
    root = Path(repo_root or Path(__file__).resolve().parents[1]).resolve()
    path = root / MANIFEST
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 256 * 1024:
        raise ValueError("manifesto R1249 ausente, inseguro ou excessivo")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("manifesto R1249 ilegível") from exc
    if not isinstance(manifest, dict):
        raise ValueError("manifesto R1249 deve ser objeto JSON")
    if manifest.get("schema_version") != "r1249.v1" or manifest.get("spec_id") != "SPEC-935-R1249":
        raise ValueError("schema/spec R1249 divergente")
    source = manifest.get("source")
    runtime = manifest.get("burp_runtime")
    wsl = manifest.get("wsl2_observation")
    safety = manifest.get("safety")
    if not all(isinstance(value, dict) for value in (source, runtime, wsl, safety)):
        raise ValueError("seções obrigatórias ausentes no manifesto R1249")
    if source.get("repository") != "PortSwigger/mcp-server" or source.get("commit") != SOURCE_COMMIT:
        raise ValueError("proveniência PortSwigger divergente")
    if source.get("commit_signature_status") != "unsigned":
        raise ValueError("estado de assinatura do commit não corresponde à observação")
    if source.get("bapp_version") != "1.4.0" or source.get("supported_products") != ["Pro", "Community"]:
        raise ValueError("versão/produtos do BApp divergentes")
    if "streamable_http" not in source.get("transports", []):
        raise ValueError("transporte Streamable HTTP não documentado no manifesto")
    if manifest.get("selected_transport") != "remote_streamable_http" or manifest.get("endpoint") != ENDPOINT:
        raise ValueError("transporte ou endpoint selecionado diverge")
    if manifest.get("requires_java") is not False or manifest.get("requires_proxy_jar") is not False:
        raise ValueError("rota HTTP direta não pode exigir Java ou proxy JAR")
    if manifest.get("status") != "blocked_missing_bapp":
        raise ValueError("status deve permanecer bloqueado enquanto faltar o BApp")
    if type(runtime.get("burp_community_installed")) is not bool:
        raise ValueError("estado observado de instalação do Burp deve ser booleano")
    if runtime.get("official_bapp_installed") is not False:
        raise ValueError("plano atual não deve promover BApp ausente a instalado")
    if runtime.get("default_host") != "127.0.0.1" or runtime.get("default_port") != 9876:
        raise ValueError("bind/porta padrão PortSwigger divergente")
    if runtime.get("enabled_default_on_extension_load") is not True:
        raise ValueError("alerta de inicialização automática da extensão ausente")
    if runtime.get("config_editing_tooling_default") is not False or runtime.get("http_request_approval_default") is not True:
        raise ValueError("defaults de segurança PortSwigger divergentes")
    if wsl.get("kernel_identifies_wsl2") is not True or wsl.get("wslg_environment_present") is not True:
        raise ValueError("observação WSL2/WSLg divergente")
    if wsl.get("agent_desktop_binary_found") is not False:
        raise ValueError("estado do backend agent-desktop divergente")
    if wsl.get("atspi_typelib_package") != "gir1.2-atspi-2.0":
        raise ValueError("pacote AT-SPI selecionado divergente")
    if safety != {
        "bind_host": "127.0.0.1",
        "burp_started": False,
        "extension_installed": False,
        "opencode_server_configured": False,
        "mcp_connected": False,
        "http_requests_sent": False,
        "target_testing_authorized": False,
        "burp_config_edited": False,
    }:
        raise ValueError("estado de segurança R1249 não está fail-closed")
    result = dict(manifest)
    result["transport"] = result["selected_transport"]
    return result


__all__ = ["load_plan"]
