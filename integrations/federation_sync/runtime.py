# -*- coding: utf-8 -*-
"""R1014 — runtime federado: instalação isolada, prova e ativação com recibo.

Fluxo obrigatório por servidor:

1. **instalar** em diretório isolado do Core, com versão fixada e
   ``--ignore-scripts`` (nenhum postinstall de terceiro executa);
2. **provar** o protocolo MCP (``initialize`` + ``tools/list``);
3. **ativar** apenas o que provou, gravando ``federation/activated.json``;
4. **regenerar** o ``opencode.json`` a partir desse arquivo.

Sem prova, não há ativação. Sem ativação, não há entrada no config.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.parser import Parser
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .model import sha256_text
from .probe import call_tool, probe
from .store import federation_root

INSTALL_ROOT = Path(".opencode") / "mcp" / "federated"
ACTIVATED_SCHEMA = "federation-activated-mcp/v2"
PROBE_SCHEMA = "federation-mcp-probe/v2"
SMOKE_SCHEMA = "federation-mcp-smoke/v2"
MAX_RECEIPT_AGE_SECONDS = 24 * 60 * 60
# Os opcionais continuam instalados, inspecionáveis e reativáveis com --ids.
OPTIONAL_SERVERS = frozenset({"mcp-everything", "executeautomation-playwright"})
DEFAULT_SERVERS = ("mcp-time", "mcp-memory", "context7", "chroma", "qdrant", "playwright")


@dataclass(frozen=True)
class ServerSpec:
    name: str
    package: str
    version: str
    ecosystem: str
    license: str
    source: str
    command: Tuple[str, ...]
    env: Mapping[str, str] = field(default_factory=dict)
    limitations: Tuple[str, ...] = ()
    notes: str = ""


def _bin(repo_root: Path, relative: str) -> str:
    return str(Path(repo_root) / INSTALL_ROOT / relative)


def server_specs(repo_root: Path) -> Dict[str, ServerSpec]:
    """Os oito servidores autorizados, com comando absoluto e versão fixada."""

    root = Path(repo_root).resolve()
    npm = "node/node_modules/.bin"
    return {
        "mcp-time": ServerSpec(
            name="mcp-time", package="mcp-server-time", version="2026.10.28",
            ecosystem="python", license="MIT",
            source="https://pypi.org/project/mcp-server-time/",
            command=(_bin(root, "py-time/bin/mcp-server-time"),),
        ),
        "mcp-memory": ServerSpec(
            name="mcp-memory", package="@modelcontextprotocol/server-memory", version="2.0.1",
            ecosystem="node", license="MIT",
            source="https://github.com/modelcontextprotocol/servers",
            command=(_bin(root, f"{npm}/mcp-server-memory"),),
            limitations=("Grafo de conhecimento em memória do processo; persistência exige MEMORY_FILE_PATH.",),
        ),
        "mcp-everything": ServerSpec(
            name="mcp-everything", package="@modelcontextprotocol/server-everything", version="2.1.0",
            ecosystem="node", license="MIT",
            source="https://github.com/modelcontextprotocol/servers",
            command=(_bin(root, f"{npm}/mcp-server-everything"), "stdio"),
            limitations=("Servidor de demonstração; não usar como ferramenta de produção.",),
        ),
        "context7": ServerSpec(
            name="context7", package="@upstash/context7-mcp", version="4.4.4",
            ecosystem="node", license="MIT",
            source="https://github.com/upstash/context7",
            command=(_bin(root, f"{npm}/context7-mcp"), "--transport", "stdio"),
            limitations=("Sem CONTEXT7_API_KEY a cota anônima é limitada; a chave é do operador.",),
        ),
        "chroma": ServerSpec(
            name="chroma", package="chroma-mcp", version="0.2.6",
            ecosystem="python", license="Apache-2.0",
            source="https://pypi.org/project/chroma-mcp/",
            command=(
                _bin(root, "py-chroma/bin/chroma-mcp"),
                "--client-type", "persistent",
                "--data-dir", str(root / INSTALL_ROOT / "data" / "chroma"),
            ),
            limitations=("Cliente persistente local; dados ficam em .opencode/mcp/federated/data/chroma.",),
        ),
        "qdrant": ServerSpec(
            name="qdrant", package="mcp-server-qdrant", version="0.8.1",
            ecosystem="python", license="Apache-2.0",
            source="https://pypi.org/project/mcp-server-qdrant/",
            command=(_bin(root, "py-qdrant/bin/mcp-server-qdrant"), "--transport", "stdio"),
            # R1020: servidor Qdrant único em Podman, em vez de cliente local
            # embarcado. O modo local usa lock exclusivo e falha quando duas
            # sessões do OpenCode tentam abrir o mesmo diretório.
            env={"QDRANT_URL": "http://127.0.0.1:6333"},
            limitations=(
                "Servidor Qdrant local em 127.0.0.1:6333, container rootless "
                "`qdrant-core`; requer o container ativo. A primeira inicialização "
                "baixa o modelo FastEmbed do Hugging Face; o handshake não prova "
                "geração de embeddings.",
            ),
        ),
        "playwright": ServerSpec(
            name="playwright", package="@playwright/mcp", version="0.0.84",
            ecosystem="node", license="Apache-2.0",
            source="https://github.com/microsoft/playwright-mcp",
            command=(_bin(root, f"{npm}/playwright-mcp"), "--browser", "chromium", "--headless", "--isolated"),
            limitations=(
                "Navegador headless com perfil isolado em memória (--isolated); "
                "este pacote exige Chrome for Testing compatível; instalar explicitamente "
                "com 'playwright-mcp install-browser chrome-for-testing'.",
            ),
        ),
        "executeautomation-playwright": ServerSpec(
            name="executeautomation-playwright",
            package="@executeautomation/playwright-mcp-server", version="1.0.12",
            ecosystem="node", license="MIT",
            source="https://github.com/executeautomation/mcp-playwright",
            command=(_bin(root, f"{npm}/playwright-mcp-server"),),
            limitations=("Opcional; requer seu próprio navegador compatível e novo smoke real antes da reativação.",),
        ),
    }


INSTALL_COMMANDS = {
    "node": [
        "npm", "install", "--prefix", str(INSTALL_ROOT / "node"),
        "--no-audit", "--no-fund", "--ignore-scripts", "--save-exact",
        "@modelcontextprotocol/server-memory@2.0.1",
        "@modelcontextprotocol/server-everything@2.1.0",
        "@upstash/context7-mcp@4.4.4",
        "@playwright/mcp@0.0.84",
        "@executeautomation/playwright-mcp-server@1.0.12",
    ],
    "python": [
        ["uv", "venv", str(INSTALL_ROOT / "py-chroma"), "--python", "3.12"],
        ["uv", "pip", "install", "--python", str(INSTALL_ROOT / "py-chroma/bin/python"), "chroma-mcp==0.2.6", "pydantic<2.12"],
        ["uv", "venv", str(INSTALL_ROOT / "py-time"), "--python", "3.12"],
        ["uv", "pip", "install", "--python", str(INSTALL_ROOT / "py-time/bin/python"), "mcp-server-time==2026.10.28"],
        ["uv", "venv", str(INSTALL_ROOT / "py-qdrant"), "--python", "3.12"],
        ["uv", "pip", "install", "--python", str(INSTALL_ROOT / "py-qdrant/bin/python"), "mcp-server-qdrant==0.8.1"],
    ],
}


def _within(path: Path, directory: Path) -> bool:
    try:
        return path.resolve(strict=True).is_relative_to(directory.resolve(strict=True))
    except (OSError, ValueError, RuntimeError):
        return False


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalized_package(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def installation_identity(repo_root: Path, spec: ServerSpec) -> Dict[str, Any]:
    """Lê bytes do launcher e versão do manifesto instalado sem executar pacote.

    Limite: não autentica a cadeia de suprimentos nem as dependências transitivas.
    """

    root = Path(repo_root).resolve()
    install_root = root / INSTALL_ROOT
    binary = Path(spec.command[0])
    if not binary.is_file() or not _within(binary, install_root):
        raise ValueError("binário ausente ou symlink externo ao runtime isolado")
    if not os.access(binary, os.X_OK):
        raise ValueError("binário sem permissão de execução")
    if spec.ecosystem == "node":
        manifest = install_root / "node/node_modules" / spec.package / "package.json"
        if not manifest.is_file() or not _within(manifest, install_root):
            raise ValueError("manifesto Node ausente ou externo")
        package = json.loads(manifest.read_text(encoding="utf-8"))
        installed_name = str(package.get("name") or "")
        installed_version = str(package.get("version") or "")
    elif spec.ecosystem == "python":
        venv_name = "py-time" if spec.name == "mcp-time" else f"py-{spec.name}"
        site_packages = install_root / venv_name / "lib/python3.12/site-packages"
        manifests = []
        for candidate in sorted(site_packages.glob("*.dist-info/METADATA")):
            if not _within(candidate, install_root):
                continue
            headers = Parser().parsestr(candidate.read_text(encoding="utf-8"), headersonly=True)
            if _normalized_package(headers.get("Name", "")) == _normalized_package(spec.package):
                manifests.append((candidate, headers))
        if len(manifests) != 1:
            raise ValueError("manifesto Python ausente ou ambíguo")
        manifest, headers = manifests[0]
        installed_name = str(headers.get("Name") or "")
        installed_version = str(headers.get("Version") or "")
    else:
        raise ValueError("ecossistema não suportado")
    if _normalized_package(installed_name) != _normalized_package(spec.package):
        raise ValueError("pacote instalado divergente")
    if installed_version != spec.version:
        raise ValueError("versão instalada divergente")
    return {
        "command": list(spec.command), "env": dict(spec.env),
        "package": spec.package, "installed_version": installed_version,
        "binary_path": str(binary.resolve(strict=True)),
        "binary_sha256": _sha256(binary), "manifest_sha256": _sha256(manifest),
    }


def _receipt_age_issue(receipt: Mapping[str, Any]) -> str:
    stamp = receipt.get("checked_at")
    if not isinstance(stamp, str) or not stamp:
        return "timestamp ausente"
    try:
        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
            return "timestamp sem UTC"
        age = time.time() - parsed.timestamp()
    except (ValueError, OverflowError):
        return "timestamp inválido"
    if age < 0:
        return "timestamp futuro"
    if age > MAX_RECEIPT_AGE_SECONDS:
        return "recibo expirado"
    return ""


def _receipt_issue(name: str, spec: ServerSpec, identity: Mapping[str, Any],
                   receipt: Any, *, smoke_check: bool = False,
                   probe_receipt: Optional[Mapping[str, Any]] = None) -> str:
    if not isinstance(receipt, dict):
        return "recibo ausente ou inválido"
    if receipt.get("schema") != (SMOKE_SCHEMA if smoke_check else PROBE_SCHEMA):
        return "schema de recibo ausente ou legado"
    if receipt.get("name") != name:
        return "servidor divergente"
    if receipt.get("ok") is not True or receipt.get("error"):
        return "prova ausente ou falha"
    if (age_issue := _receipt_age_issue(receipt)):
        return age_issue
    if receipt.get("identity") != identity:
        return "identidade do comando/binário/manifesto divergente"
    if smoke_check:
        if receipt.get("result_is_error") is not False:
            return "resultado da ferramenta não comprovado ou retornou isError"
        tool, arguments = SMOKE_CALLS[name]
        if receipt.get("tool") != tool or receipt.get("arguments") != arguments:
            return "ferramenta ou argumentos de smoke divergentes"
        if probe_receipt is None or tool not in (probe_receipt.get("tools") or []):
            return "ferramenta não constava no catálogo provado"
    elif (not isinstance(receipt.get("tools"), list) or
          not receipt["tools"] or receipt.get("tools_count") != len(receipt["tools"]) or
          not receipt.get("protocol_version")):
        return "catálogo ou protocolo não provado"
    return ""


def _read_smoke(repo_root: Path, name: str) -> Dict[str, Any]:
    path = federation_root(repo_root) / "probes" / f"{name}.smoke.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def _gate_issues(repo_root: Path, name: str, spec: ServerSpec,
                 probe_receipt: Any, smoke_receipt: Any) -> List[Dict[str, str]]:
    try:
        identity = installation_identity(repo_root, spec)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [{"server": name, "code": "installation_invalid", "detail": str(exc)}]
    probe_error = _receipt_issue(name, spec, identity, probe_receipt)
    smoke_error = _receipt_issue(name, spec, identity, smoke_receipt,
                                 smoke_check=True, probe_receipt=probe_receipt)
    issues = []
    if probe_error:
        issues.append({"server": name, "code": "probe_invalid", "detail": probe_error})
    if smoke_error:
        issues.append({"server": name, "code": "smoke_invalid", "detail": smoke_error})
    return issues


# ----------------------------------------------------------------------
# Probe e recibos
# ----------------------------------------------------------------------
def probe_all(repo_root: Path, *, names: Optional[Iterable[str]] = None,
              timeout: int = 60) -> Dict[str, Any]:
    root = Path(repo_root).resolve()
    specs = server_specs(root)
    selected = list(names) if names else list(specs)
    receipts: Dict[str, Any] = {}
    for name in selected:
        spec = specs.get(name)
        if spec is None:
            receipts[name] = {"ok": False, "error": "servidor não registrado"}
            continue
        try:
            identity = installation_identity(root, spec)
            (root / INSTALL_ROOT / "data" / "chroma").mkdir(parents=True, exist_ok=True)
            (root / INSTALL_ROOT / "data" / "qdrant").mkdir(parents=True, exist_ok=True)
            result = probe(spec.command, cwd=root, env=dict(spec.env), timeout=timeout)
            if installation_identity(root, spec) != identity:
                result.update(ok=False, error="instalação mudou durante o probe")
        except (OSError, ValueError, TypeError, KeyError) as exc:
            identity = {}
            result = {"ok": False, "error": f"instalação: {exc}", "tools": [], "tools_count": 0}
        receipt = {
            "schema": PROBE_SCHEMA,
            "name": name,
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "identity": identity,
            "package": spec.package,
            "version": spec.version,
            "license": spec.license,
            "source": spec.source,
            "command": list(spec.command),
            "limitations": list(spec.limitations),
            "notes": spec.notes,
            **result,
        }
        receipts[name] = receipt
        directory = federation_root(root) / "probes"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"{name}.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipts


def load_probes(repo_root: Path) -> Dict[str, Any]:
    directory = federation_root(Path(repo_root).resolve()) / "probes"
    found: Dict[str, Any] = {}
    if not directory.is_dir():
        return found
    for path in sorted(directory.glob("*.json")):
        if path.name.endswith(".smoke.json"):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                found[path.stem] = data
        except (OSError, ValueError):
            continue
    return found


# Ferramenta de fumaça por servidor: leitura ou operação inofensiva.
SMOKE_CALLS: Dict[str, Tuple[str, Dict[str, Any]]] = {
    "mcp-time": ("get_current_time", {"timezone": "America/Fortaleza"}),
    "mcp-memory": ("search_nodes", {"query": "__core_federation_smoke_nonexistent__"}),
    "mcp-everything": ("echo", {"message": "ok"}),
    "context7": ("resolve-library-id", {"libraryName": "React", "query": "react useState"}),
    "chroma": ("chroma_list_collections", {}),
    # Escrita confinada a uma coleção local técnica; valida a cadeia de embeddings.
    "qdrant": ("qdrant-store", {"collection_name": "core_federation_smoke",
                               "information": "Core MCP smoke — conteúdo técnico sem dados do usuário"}),
    "playwright": ("browser_navigate", {"url": "about:blank"}),
    "executeautomation-playwright": ("playwright_navigate", {"url": "about:blank"}),
}


def smoke(repo_root: Path, *, names: Optional[Iterable[str]] = None,
          timeout: int = 150) -> Dict[str, Any]:
    """Chama uma ferramenta real de cada servidor e grava o recibo."""

    root = Path(repo_root).resolve()
    specs = server_specs(root)
    selected = list(names) if names else list(specs)
    receipts: Dict[str, Any] = {}
    for name in selected:
        spec = specs.get(name)
        call = SMOKE_CALLS.get(name)
        if spec is None or call is None:
            receipts[name] = {"ok": False, "error": "sem chamada de fumaça declarada"}
            continue
        tool, arguments = call
        try:
            identity = installation_identity(root, spec)
            scratch_root = Path("/tmp/opencode")
            with tempfile.TemporaryDirectory(
                prefix="mcp-smoke-", dir=str(scratch_root) if scratch_root.is_dir() else None,
            ) as scratch:
                result = call_tool(spec.command, tool, arguments, cwd=Path(scratch),
                                   env=dict(spec.env), timeout=timeout)
            if installation_identity(root, spec) != identity:
                result.update(ok=False, error="instalação mudou durante o smoke")
        except (OSError, ValueError, TypeError, KeyError) as exc:
            identity = {}
            result = {"ok": False, "error": f"instalação: {exc}", "result": None}
        payload = result.get("result")
        excerpt = ("[conteúdo potencialmente privado omitido]" if name == "mcp-memory" else
                   json.dumps(payload, ensure_ascii=False, default=str)[:1200])
        receipt = {
            "schema": SMOKE_SCHEMA,
            "name": name,
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "identity": identity,
            "tool": tool,
            "arguments": arguments,
            "result_is_error": (payload.get("isError") is True if isinstance(payload, dict) else None),
            "ok": bool(result.get("ok")),
            "duration_ms": result.get("duration_ms"),
            "error": result.get("error") or "",
            "result_excerpt": excerpt,
            "stderr_tail": result.get("stderr_tail") or "",
        }
        receipts[name] = receipt
        directory = federation_root(root) / "probes"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"{name}.smoke.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_activation_report(root)
    return receipts


def _entry(spec: ServerSpec) -> Dict[str, Any]:
    entry = {"type": "local", "command": list(spec.command), "enabled": True, "timeout": 120000}
    if spec.env:
        entry["environment"] = dict(spec.env)
    return entry


def _activation_digest(servers: Dict[str, Any], provenance: Dict[str, Any], schema: str) -> str:
    # v1 cobria só as entradas; v2 fecha também a proveniência associada.
    payload = (servers if schema == "federation-activated-mcp/v1" else
               {"servers": servers, "provenance": provenance})
    return sha256_text(json.dumps(payload, sort_keys=True))


def _document_issue(document: Dict[str, Any]) -> str:
    if not document:
        return ""
    servers = document.get("servers")
    if document.get("schema") not in {ACTIVATED_SCHEMA, "federation-activated-mcp/v1"}:
        return "schema de ativação inválido"
    if not isinstance(servers, dict) or not isinstance(document.get("provenance"), dict):
        return "mapa de servidores/proveniência inválido"
    if document.get("digest") != _activation_digest(servers, document["provenance"], document["schema"]):
        return "digest da ativação divergente"
    return ""


def _write_active(root: Path, document: Dict[str, Any]) -> Path:
    """Troca o documento em uma única operação; não trunca o registro anterior."""

    path = federation_root(root) / "activated.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name("activated.json.tmp")
    pending.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending.replace(path)
    return path


# ----------------------------------------------------------------------
# Ativação
# ----------------------------------------------------------------------
def activate(
    repo_root: Path,
    *,
    names: Optional[Iterable[str]] = None,
    probes: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    root = Path(repo_root).resolve()
    specs = server_specs(root)
    probes = probes if probes is not None else load_probes(root)
    requested = list(names) if names is not None else list(DEFAULT_SERVERS)
    previous = load_activated(root)
    if (issue := _document_issue(previous)):
        return {"status": "degraded", "activated": [], "blocked": {"document": issue}}
    activated: Dict[str, Any] = dict(previous.get("servers") or {})
    provenance: Dict[str, Any] = dict(previous.get("provenance") or {})
    blocked: Dict[str, str] = {}
    for name in requested:
        spec = specs.get(name)
        if spec is None:
            blocked[name] = "servidor não registrado"
            continue
        receipt = probes.get(name) or {}
        errors = _gate_issues(root, name, spec, receipt, _read_smoke(root, name))
        if errors:
            blocked[name] = "; ".join(f"{i['code']}: {i['detail']}" for i in errors)
            activated.pop(name, None)
            provenance.pop(name, None)
            continue
        activated[name] = _entry(spec)
        provenance[name] = {
            "item_id": f"github:mcp:{name}",
            "package": spec.package,
            "version": spec.version,
            "license": spec.license,
            "source": spec.source,
            "tools_count": receipt.get("tools_count"),
            "protocol_version": receipt.get("protocol_version"),
            "probed_at": receipt.get("checked_at"),
            "binary_sha256": receipt["identity"]["binary_sha256"],
            "manifest_sha256": receipt["identity"]["manifest_sha256"],
            "limits": list(spec.limitations),
        }

    document = {
        "schema": ACTIVATED_SCHEMA,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "servers": activated,
        "provenance": provenance,
        "digest": _activation_digest(activated, provenance, ACTIVATED_SCHEMA),
        "rule": "Probe e smoke recentes, vinculados à instalação, são necessários; saúde contínua não é garantida.",
    }
    path = _write_active(root, document)
    write_activation_report(root)
    return {
        "status": "ok" if not blocked else "degraded",
        "activated": sorted(activated),
        "blocked": blocked,
        "file": str(path),
        "digest": document["digest"],
    }


def deactivate(repo_root: Path, *, names: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    root = Path(repo_root).resolve()
    path = federation_root(root) / "activated.json"
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "missing", "activated": []}
    if (issue := _document_issue(document)):
        return {"status": "degraded", "error": issue, "removed": []}
    servers = dict(document.get("servers") or {})
    provenance = dict(document.get("provenance") or {})
    removed = []
    for name in (list(names) if names else list(servers)):
        if name in servers:
            servers.pop(name, None)
            provenance.pop(name, None)
            removed.append(name)
    document.update(servers=servers, provenance=provenance,
                    schema=ACTIVATED_SCHEMA,
                    updated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    digest=_activation_digest(servers, provenance, ACTIVATED_SCHEMA))
    _write_active(root, document)
    write_activation_report(root)
    return {"status": "ok", "removed": sorted(removed), "remaining": sorted(servers)}


def load_activated(repo_root: Path) -> Dict[str, Any]:
    path = federation_root(Path(repo_root).resolve()) / "activated.json"
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return document if isinstance(document, dict) else {}


def activated_servers(repo_root: Path) -> Dict[str, Dict[str, Any]]:
    """Somente entradas comprovadas entram no config; recibo velho falha fechado."""

    root = Path(repo_root).resolve()
    document = load_activated(root)
    if _document_issue(document) or document.get("schema") == "federation-activated-mcp/v1":
        return {}
    servers = document.get("servers") or {}
    specs = server_specs(root)
    probes = load_probes(root)
    return {name: entry for name, entry in servers.items()
            if name in specs and entry == _entry(specs[name]) and
            not _gate_issues(root, name, specs[name], probes.get(name), _read_smoke(root, name))}


def write_activation_report(repo_root: Path) -> Optional[Path]:
    """Relatório humano da ativação com o MESMO gate do diagnóstico."""

    root = Path(repo_root).resolve()
    document = load_activated(root)
    servers = document.get("servers") or {}
    probes = load_probes(root)
    specs = server_specs(root)
    provenance = document.get("provenance") or {}
    lines = [
        "# MCPs federados ativados — R1015",
        "",
        f"Gerado em `{document.get('updated_at', '')}`. Fonte: `federation/activated.json`.",
        "",
        "> Ativação exige instalação íntegra, probe e smoke com vínculo idêntico e idade até 24 h.",
        "> Instalação e recibo não provam disponibilidade futura. Opcionais instalados: "
        "`mcp-everything`, `executeautomation-playwright`; reativação via `--ids` "
        "somente com probe e smoke realmente válidos.",
        "",
        "| Servidor | Pacote | Versão | Licença | Ferramentas | Probe | Smoke |",
        "|---|---|---|---|---:|---|---|",
    ]
    for name in sorted(servers):
        info = provenance.get(name) or {}
        probe = probes.get(name) or {}
        spec = specs.get(name)
        gate = (_gate_issues(root, name, spec, probe, _read_smoke(root, name))
                if spec is not None else [{"code": "unknown_server"}])
        lines.append(
            f"| `{name}` | `{info.get('package', '')}` | {info.get('version', '')} | "
            f"{info.get('license', '')} | {probe.get('tools_count', '')} | "
            f"{'válido' if not any(i['code'] in ('installation_invalid', 'probe_invalid') for i in gate) else 'falhou'} | "
            f"{'válido' if not gate else 'falhou'} |"
        )
    lines += ["", "## Limites declarados", ""]
    for name in sorted(servers):
        limits = (provenance.get(name) or {}).get("limits") or []
        if limits:
            lines.append(f"- **{name}**: " + " ".join(str(item) for item in limits))
    lines += [
        "",
        "## Comandos",
        "",
        "```bash",
        "python3 -m marceloclaro.cli federacao probe",
        "python3 -m marceloclaro.cli federacao activate",
        "python3 -m marceloclaro.cli federacao smoke",
        "python3 -m marceloclaro.cli federacao doctor",
        "```",
        "",
    ]
    path = federation_root(root) / "activation.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ----------------------------------------------------------------------
# Doctor
# ----------------------------------------------------------------------
def doctor(repo_root: Path) -> Dict[str, Any]:
    root = Path(repo_root).resolve()
    document = load_activated(root)
    probes = load_probes(root)
    specs = server_specs(root)
    servers = document.get("servers") or {}
    document_error = _document_issue(document)
    issues = ([{"server": "document", "code": "activation_document_invalid",
                "detail": document_error}] if document_error else [])
    if document.get("schema") == "federation-activated-mcp/v1":
        issues.append({"server": "document", "code": "legacy_document_requires_migration",
                       "detail": "execute activate após probe/smoke recentes"})
    if not isinstance(servers, dict):
        servers = {}
    checked = []
    for name, entry in sorted(servers.items()):
        spec = specs.get(name)
        if spec is None:
            issues.append({"server": name, "code": "unknown_server", "detail": "não está no catálogo"})
            continue
        if entry != _entry(spec):
            issues.append({"server": name, "code": "activation_entry_invalid",
                           "detail": "comando/ambiente/configuração divergente"})
        receipt = probes.get(name) or {}
        smoke_receipt = _read_smoke(root, name)
        gate = _gate_issues(root, name, spec, receipt, smoke_receipt)
        issues.extend(gate)
        checked.append({
            "server": name,
            "installation": not any(issue["code"] == "installation_invalid" for issue in gate),
            "probe": not any(issue["code"] == "probe_invalid" for issue in gate) and not gate,
            "smoke": not gate and not document_error and entry == _entry(spec),
            "tools_count": receipt.get("tools_count"),
            "probed_at": receipt.get("checked_at"),
            "smoked_at": smoke_receipt.get("checked_at"),
        })
    # Uma configuração ainda não regenerada pode manter entradas que o gate já
    # recusou; não confundir activated.json íntegro com estado efetivo do host.
    config_path = root / "opencode.json"
    if config_path.is_file():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            configured = config.get("mcp") or {}
            if not isinstance(configured, dict):
                raise ValueError("mcp não é objeto")
            verified_names = set(activated_servers(root))
            for name in sorted(set(specs) & (set(configured) - verified_names)):
                issues.append({"server": name, "code": "config_stale_or_unverified",
                               "detail": "presente no opencode.json sem recibos válidos; regenere o config"})
        except (OSError, ValueError, AttributeError) as exc:
            issues.append({"server": "config", "code": "config_invalid", "detail": str(exc)})
    return {
        "status": "ok" if not issues else "degraded",
        "activated": len(servers),
        "checked": checked,
        "issues": issues,
    }
