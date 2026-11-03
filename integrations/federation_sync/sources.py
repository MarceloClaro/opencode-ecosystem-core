# -*- coding: utf-8 -*-
"""R1012 — extratores somente-leitura dos quatro ecossistemas.

Cada função recebe raízes explícitas e devolve ``FederatedItem`` normalizados.
Não há rede, clone, instalação ou execução: o que não está no disco (ou no
manifesto versionado) simplesmente não existe para esta camada.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .gates import classify, license_from_text, normalize_license
from .model import FederatedItem, sha256_text, slugify

_LICENSE_FILES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "COPYING.md")
_SECRET_KEY = re.compile(r"(token|secret|password|passwd|api[_-]?key|apikey|auth|credential)", re.I)
_MAX_FILE = 400_000


# ----------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------
def _read_text(path: Path, *, limit: int = _MAX_FILE) -> str:
    try:
        if not path.is_file():
            return ""
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def _read_json(path: Path) -> Any:
    try:
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return None


def _sha256_file(path: Path) -> str:
    try:
        return sha256_text(path.read_bytes().decode("utf-8", "replace"))
    except OSError:
        return ""


def _frontmatter(text: str) -> Dict[str, str]:
    """Leitura mínima de frontmatter YAML: pares ``chave: valor`` de primeiro nível."""

    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end]
    data: Dict[str, str] = {}
    key = None
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1] in " \t" and key:
            data[key] = (data[key] + " " + line.strip()).strip()
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            data[key] = value.strip().strip("'\"")
    return data


def _license_in(directory: Path) -> str:
    for name in _LICENSE_FILES:
        found = license_from_text(_read_text(directory / name))
        if found:
            return found
    return ""


def _component_names(value: Any) -> List[str]:
    names = []
    for entry in value or ():
        if isinstance(entry, dict):
            name = entry.get("name") or entry.get("id")
        else:
            name = entry
        if name:
            names.append(str(name))
    return names


def _capabilities(*values: Any) -> Tuple[str, ...]:
    found: List[str] = []
    for value in values:
        text = str(value or "")
        for token in re.split(r"[^A-Za-z0-9]+", text):
            token = token.strip().lower()
            if len(token) >= 3 and token not in found:
                found.append(token)
    return tuple(found[:24])


def scrub_server(value: Any) -> Optional[Dict[str, Any]]:
    """
    Normaliza a definição de um servidor MCP sem reter segredo.

    ``env`` e ``headers`` perdem os valores; ficam apenas os nomes das chaves.
    Um servidor sem ``command`` nem ``url`` não é registrável e devolve ``None``.
    """

    if not isinstance(value, dict):
        return None
    server: Dict[str, Any] = {}
    existing_env_keys = value.get("env_keys")
    existing_header_keys = value.get("headers_keys")
    command = value.get("command")
    if isinstance(command, str):
        server["command"] = [command]
    elif isinstance(command, list) and all(isinstance(part, str) for part in command):
        server["command"] = list(command)
    args = value.get("args")
    if isinstance(args, list):
        server["args"] = [str(part) for part in args]
    url = value.get("url")
    if isinstance(url, str):
        server["url"] = url
    for key in ("env", "headers"):
        block = value.get(key)
        if isinstance(block, dict):
            server[f"{key}_keys"] = sorted(str(name) for name in block)
    if isinstance(existing_env_keys, list):
        server["env_keys"] = sorted(set(server.get("env_keys", [])) | {str(k) for k in existing_env_keys})
    if isinstance(existing_header_keys, list):
        server["headers_keys"] = sorted(set(server.get("headers_keys", [])) | {str(k) for k in existing_header_keys})
    if not server.get("command") and not server.get("url"):
        return None
    server["secrets_scrubbed"] = True
    return server


def _server_requires_auth(server: Optional[Dict[str, Any]]) -> bool:
    if not server:
        return False
    if server.get("url"):
        return True
    return any(_SECRET_KEY.search(name) for name in server.get("env_keys", []) + server.get("headers_keys", []))


def _mcp_from_directory(directory: Path) -> Dict[str, Dict[str, Any]]:
    """Coleta definições MCP de ``mcp.json``, ``.mcp.json`` e ``plugin.json``."""

    found: Dict[str, Dict[str, Any]] = {}
    for relative in ("mcp.json", ".mcp.json", "plugin.json", ".claude-plugin/plugin.json",
                     ".codex-plugin/plugin.json"):
        document = _read_json(directory / relative)
        if not isinstance(document, dict):
            continue
        block = document.get("mcpServers") or document.get("mcp_servers") or {}
        if isinstance(block, dict):
            for name, raw in block.items():
                server = scrub_server(raw)
                if server:
                    found[str(name)] = server
    return found


def _component_candidates(root: Path, kind: str, name: str) -> List[Path]:
    """Caminhos plausíveis do corpo de um componente dentro de um plugin."""

    if kind == "skill":
        return [root / "skills" / name / "SKILL.md",
                root / ".claude" / "skills" / name / "SKILL.md",
                root / "skills" / f"{name}.md"]
    if kind == "agent":
        return [root / "agents" / f"{name}.md", root / ".claude" / "agents" / f"{name}.md"]
    if kind == "command":
        return [root / "commands" / f"{name}.md", root / ".claude" / "commands" / f"{name}.md"]
    return []


def _component_body(roots: Iterable[Path], kind: str, name: str) -> str:
    for root in roots:
        for candidate in _component_candidates(root, kind, name):
            if candidate.is_file():
                return str(candidate)
    return ""


def _is_native_server(server: Optional[Dict[str, Any]], repo_root: Path) -> bool:
    """Servidor que aponta para o próprio Core não é artefato externo."""

    if not server:
        return False
    parts = list(server.get("command") or []) + list(server.get("args") or [])
    joined = " ".join(parts)
    markers = (str(repo_root), "opencode-ecosystem-core", "mci/mcp_server.py",
               "integrations/ecosystem_mcp.py", "integrations/antigravity/")
    return any(marker and marker in joined for marker in markers)


# ----------------------------------------------------------------------
# Claude
# ----------------------------------------------------------------------
def claude_items(home: Path, repo_root: Path) -> List[FederatedItem]:
    base = home / ".claude" / "plugins"
    catalog = _read_json(base / "plugin-catalog-cache.json")
    installed = _read_json(base / "installed_plugins.json") or {}
    install_index: Dict[str, str] = {}
    for key, records in (installed.get("plugins") or {}).items():
        for record in records or ():
            path = record.get("installPath")
            if path:
                install_index.setdefault(str(key).split("@", 1)[0], str(path))

    marketplace_licenses: Dict[str, str] = {}
    marketplace_dirs: Dict[str, Path] = {}
    marketplaces_root = base / "marketplaces"
    if marketplaces_root.is_dir():
        for directory in sorted(marketplaces_root.iterdir()):
            if directory.is_dir():
                marketplace_dirs[directory.name] = directory
                marketplace_licenses[directory.name] = _license_in(directory)

    items: List[FederatedItem] = []
    seen = set()

    def emit(item: FederatedItem) -> None:
        if item.item_id not in seen:
            seen.add(item.item_id)
            items.append(item)

    entries = ((catalog or {}).get("catalog") or {}).get("plugins") or {}
    for key, entry in entries.items():
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("plugin") or str(key).split("@", 1)[0])
        marketplace = str(key).split("@", 1)[1] if "@" in str(key) else ""
        meta = entry.get("marketplace_entry") or {}
        directory = marketplace_dirs.get(marketplace, Path()) / "plugins" / name
        plugin_present = directory.is_dir()
        plugin_license = _license_in(directory) if plugin_present else ""
        # O plugin pertence ao marketplace quando o próprio catálogo o declara
        # assim (``name@marketplace``) ou quando seus arquivos estão no repo.
        # Fora disso, licença desconhecida permanece desconhecida.
        belongs = plugin_present or str(entry.get("source") or "") == key
        inherited = marketplace_licenses.get(marketplace, "") if belongs else ""
        scope = "plugin" if plugin_license else ("marketplace" if inherited else "")
        license_value = plugin_license or inherited
        install_path = install_index.get(name)

        components = entry.get("components") or {}
        has_scripts = any((directory / part).is_dir() for part in ("scripts", "hooks", "bin"))
        source = entry.get("source")
        if isinstance(source, dict):
            source_uri = str(source.get("url") or source.get("repo") or "")
        else:
            source_uri = str(source or "")
        homepage = str(meta.get("homepage") or "")
        if homepage.startswith("http"):
            source_uri = homepage

        status, reasons, risk = classify(
            kind="plugin", license=license_value, install_mode="metadata",
            has_scripts=has_scripts,
        )
        emit(FederatedItem(
            ecosystem="claude", kind="plugin", name=name,
            description=str(meta.get("description") or ""),
            version=str(entry.get("version") or ""),
            license=license_value, license_scope=scope,
            source_uri=source_uri, source_path=str(directory) if directory.is_dir() else "",
            content_sha256=sha256_text(json.dumps(entry, ensure_ascii=False, sort_keys=True)),
            capabilities=_capabilities(name, meta.get("category"), meta.get("author")),
            tags=tuple(filter(None, [str(meta.get("category") or ""), marketplace])),
            install_mode="metadata", status=status, reasons=reasons, runtime_risk=risk,
            metadata={
                "marketplace": marketplace,
                "author": str((meta.get("author") or {}).get("name") or "") if isinstance(meta.get("author"), dict) else str(meta.get("author") or ""),
                "unique_installs": entry.get("unique_installs"),
                "component_counts": {kind: len(value or ()) for kind, value in components.items()},
                "installed": name in install_index,
                "install_path": install_index.get(name, ""),
            },
        ))

        for kind, component_key in (("skill", "skills"), ("agent", "agents"),
                                    ("command", "commands"), ("lsp", "lspServers")):
            for component in _component_names(components.get(component_key)):
                roots = []
                if install_path:
                    roots.append(Path(install_path))
                if plugin_present:
                    roots.append(directory)
                body = _component_body(roots, kind, component)
                mode = "materialize" if body and kind in {"skill", "agent"} else "metadata"
                c_status, c_reasons, c_risk = classify(
                    kind="lsp" if kind == "lsp" else kind, license=license_value,
                    install_mode=mode,
                )
                emit(FederatedItem(
                    ecosystem="claude", kind=kind, name=component, parent=name,
                    description="", license=license_value, license_scope=scope,
                    source_uri=source_uri, source_path=body,
                    content_sha256=_sha256_file(Path(body)) if body else sha256_text(f"{key}:{kind}:{component}"),
                    capabilities=_capabilities(component, name),
                    tags=(marketplace,) if marketplace else (),
                    install_mode=mode, status=c_status, reasons=c_reasons, runtime_risk=c_risk,
                    metadata={"marketplace": marketplace, "plugin": name},
                ))

        for hook in components.get("hooks") or ():
            hook_name = hook.get("name") if isinstance(hook, dict) else str(hook)
            emit(FederatedItem(
                ecosystem="claude", kind="hook", name=str(hook_name or "hook"), parent=name,
                description="Hook declarado por plugin de terceiro; nunca executado por esta camada.",
                license=license_value, license_scope=scope, content_sha256=sha256_text(str(hook)),
                capabilities=_capabilities("hook", hook_name), install_mode="metadata",
                status="blocked", reasons=("third_party_execution",), runtime_risk="exec",
                metadata={"marketplace": marketplace, "plugin": name},
            ))

        # Definições MCP reais: cache instalado primeiro, depois marketplace.
        server_defs: Dict[str, Dict[str, Any]] = {}
        if install_path:
            server_defs.update(_mcp_from_directory(Path(install_path)))
        if directory.is_dir():
            server_defs.update(_mcp_from_directory(directory))
        for server_name in _component_names(components.get("mcpServers")):
            server = scrub_server(server_defs.get(server_name)) or server_defs.get(server_name)
            if _is_native_server(server, repo_root):
                continue
            auth = _server_requires_auth(server)
            m_status, m_reasons, m_risk = classify(
                kind="mcp", license=license_value,
                install_mode="register_disabled" if server else "metadata",
                auth_required=auth,
            )
            emit(FederatedItem(
                ecosystem="claude", kind="mcp", name=server_name, parent=name,
                description=f"Servidor MCP declarado pelo plugin {name}.",
                license=license_value, license_scope=scope, source_uri=source_uri,
                content_sha256=sha256_text(json.dumps(server or server_name, sort_keys=True)),
                capabilities=_capabilities("mcp", server_name, name),
                tags=("mcp", marketplace) if marketplace else ("mcp",),
                install_mode="register_disabled" if server else "metadata",
                status=m_status, reasons=m_reasons, runtime_risk=m_risk,
                metadata={"server": server, "plugin": name, "marketplace": marketplace},
            ))

    # Plugins presentes no marketplace e ausentes do cache do catálogo.
    for marketplace, directory in marketplace_dirs.items():
        for sub in ("plugins", "external_plugins"):
            parent = directory / sub
            if not parent.is_dir():
                continue
            for plugin_dir in sorted(parent.iterdir()):
                if not plugin_dir.is_dir():
                    continue
                name = plugin_dir.name
                if any(item.kind == "plugin" and item.name == name and item.ecosystem == "claude" for item in items):
                    continue
                manifest = _read_json(plugin_dir / ".claude-plugin" / "plugin.json") or {}
                license_value = _license_in(plugin_dir) or marketplace_licenses.get(marketplace, "")
                has_scripts = any((plugin_dir / part).is_dir() for part in ("scripts", "hooks", "bin"))
                status, reasons, risk = classify(
                    kind="plugin", license=license_value, install_mode="metadata",
                    has_scripts=has_scripts,
                )
                emit(FederatedItem(
                    ecosystem="claude", kind="plugin", name=name,
                    description=str(manifest.get("description") or ""),
                    version=str(manifest.get("version") or ""),
                    license=license_value, license_scope="plugin" if _license_in(plugin_dir) else "marketplace",
                    source_uri=str(manifest.get("homepage") or ""),
                    source_path=str(plugin_dir), content_sha256=_sha256_file(plugin_dir / ".claude-plugin" / "plugin.json"),
                    capabilities=_capabilities(name, manifest.get("description")),
                    tags=(marketplace,), install_mode="metadata", status=status,
                    reasons=reasons, runtime_risk=risk,
                    metadata={"marketplace": marketplace, "external": sub == "external_plugins"},
                ))
    return items


# ----------------------------------------------------------------------
# Antigravity
# ----------------------------------------------------------------------
def antigravity_items(home: Path, repo_root: Path) -> List[FederatedItem]:
    items: List[FederatedItem] = []
    seen = set()

    def emit(item: FederatedItem) -> None:
        if item.item_id not in seen:
            seen.add(item.item_id)
            items.append(item)

    roots = [
        home / ".gemini" / "antigravity-cli" / "builtin" / "skills",
        home / ".gemini" / "antigravity-cli" / "implicit",
        repo_root / ".antigravity" / "skills",
    ]
    for root in roots:
        if not root.is_dir():
            continue
        for skill_file in sorted(root.glob("*/SKILL.md")):
            text = _read_text(skill_file)
            front = _frontmatter(text)
            name = str(front.get("name") or skill_file.parent.name)
            license_value = _license_in(skill_file.parent)
            status, reasons, risk = classify(
                kind="skill", license=license_value, install_mode="materialize",
            )
            emit(FederatedItem(
                ecosystem="antigravity", kind="skill", name=name,
                description=str(front.get("description") or ""),
                license=license_value, license_scope="skill" if license_value else "",
                source_path=str(skill_file), source_root=str(root),
                content_sha256=sha256_text(text),
                capabilities=_capabilities(name, front.get("description")),
                tags=("skill", "antigravity"), install_mode="materialize",
                status=status, reasons=reasons, runtime_risk=risk,
                metadata={"frontmatter": front},
            ))

    settings = _read_json(home / ".gemini" / "antigravity-cli" / "settings.json") or {}
    for name, raw in (settings.get("mcpServers") or {}).items():
        server = scrub_server(raw)
        if _is_native_server(server, repo_root):
            continue
        auth = _server_requires_auth(server)
        status, reasons, risk = classify(
            kind="mcp", license="", install_mode="register_disabled" if server else "metadata",
            auth_required=auth,
        )
        emit(FederatedItem(
            ecosystem="antigravity", kind="mcp", name=str(name),
            description="Servidor MCP declarado nas preferências do Antigravity CLI.",
            source_path=str(home / ".gemini" / "antigravity-cli" / "settings.json"),
            content_sha256=sha256_text(json.dumps(server or {}, sort_keys=True)),
            capabilities=_capabilities("mcp", name), tags=("mcp", "antigravity"),
            install_mode="register_disabled" if server else "metadata",
            status=status, reasons=reasons, runtime_risk=risk,
            metadata={"server": server, "origin": "antigravity-settings"},
        ))
    return items


# ----------------------------------------------------------------------
# ChatGPT / Codex
# ----------------------------------------------------------------------
def chatgpt_items(home: Path, repo_root: Path) -> List[FederatedItem]:
    items: List[FederatedItem] = []
    seen = set()

    def emit(item: FederatedItem) -> None:
        if item.item_id not in seen:
            seen.add(item.item_id)
            items.append(item)

    codex_root = home / ".codex"
    if codex_root.is_dir():
        for manifest_path in sorted(codex_root.glob("**/.codex-plugin/plugin.json")):
            manifest = _read_json(manifest_path) or {}
            name = str(manifest.get("name") or manifest_path.parents[1].name)
            license_value = normalize_license(str(manifest.get("license") or "")) or _license_in(manifest_path.parents[1])
            has_scripts = any((manifest_path.parents[1] / part).is_dir() for part in ("scripts", "hooks", "bin"))
            status, reasons, risk = classify(
                kind="plugin", license=license_value, install_mode="metadata", has_scripts=has_scripts,
            )
            emit(FederatedItem(
                ecosystem="chatgpt", kind="plugin", name=name,
                description=str(manifest.get("description") or ""),
                version=str(manifest.get("version") or ""),
                license=license_value, license_scope="plugin" if license_value else "",
                source_path=str(manifest_path), content_sha256=_sha256_file(manifest_path),
                capabilities=_capabilities(name, manifest.get("description")),
                tags=("codex",), install_mode="metadata", status=status,
                reasons=reasons, runtime_risk=risk, metadata={"manifest": manifest},
            ))

        for skill_file in sorted(codex_root.glob("**/skills/*/SKILL.md")):
            text = _read_text(skill_file)
            front = _frontmatter(text)
            name = str(front.get("name") or skill_file.parent.name)
            license_value = _license_in(skill_file.parent)
            status, reasons, risk = classify(kind="skill", license=license_value, install_mode="materialize")
            emit(FederatedItem(
                ecosystem="chatgpt", kind="skill", name=name,
                description=str(front.get("description") or ""), license=license_value,
                source_path=str(skill_file), content_sha256=sha256_text(text),
                capabilities=_capabilities(name, front.get("description")),
                tags=("codex", "skill"), install_mode="materialize",
                status=status, reasons=reasons, runtime_risk=risk, metadata={"frontmatter": front},
            ))

    manifest = _read_json(repo_root / "federation" / "chatgpt_sources.json") or {}
    for entry in manifest.get("connectors") or ():
        if not isinstance(entry, dict) or not entry.get("name"):
            continue
        name = str(entry["name"])
        status, reasons, _ = classify(
            kind="plugin", license="", install_mode="external",
            hosted_connector=True, auth_required=True,
        )
        emit(FederatedItem(
            ecosystem="chatgpt", kind="plugin", name=name,
            description=str(entry.get("description") or ""),
            license="Proprietary", license_scope="hosted",
            source_uri=str(entry.get("url") or ""), content_sha256=sha256_text(json.dumps(entry, sort_keys=True)),
            capabilities=_capabilities(name, entry.get("description"), entry.get("category")),
            tags=("chatgpt", "connector", "hosted"), install_mode="external",
            status=status, reasons=reasons, runtime_risk="network",
            metadata={"hosted_connector": True, "vendor": entry.get("vendor"),
                      "notes": entry.get("notes", "")},
        ))
    return items


# ----------------------------------------------------------------------
# GitHub (manifesto curado, sem clone)
# ----------------------------------------------------------------------
def github_items(repo_root: Path) -> List[FederatedItem]:
    manifest = _read_json(repo_root / "federation" / "github_sources.json") or {}
    items: List[FederatedItem] = []
    seen = set()

    def emit(item: FederatedItem) -> None:
        if item.item_id not in seen:
            seen.add(item.item_id)
            items.append(item)

    for entry in manifest.get("repositories") or ():
        if not isinstance(entry, dict) or not entry.get("repo"):
            continue
        repo = str(entry["repo"])
        license_value = normalize_license(str(entry.get("license") or ""))
        owner_repo = repo.replace("/", "-")
        description = str(entry.get("description") or "")
        servers = [s for s in (entry.get("servers") or ()) if isinstance(s, dict) and s.get("name")]
        if servers:
            for server in servers:
                command = server.get("command")
                command_list = [command] if isinstance(command, str) else list(command or [])
                spec = scrub_server({"command": command_list, "args": server.get("args"),
                                     "env": {k: "" for k in server.get("env_keys") or []}})
                installable = bool(spec and entry.get("installable", True) and server.get("installable", True))
                status, reasons, risk = classify(
                    kind="mcp", license=license_value,
                    install_mode="register_disabled" if installable else "metadata",
                    auth_required=bool(server.get("auth_required")),
                )
                emit(FederatedItem(
                    ecosystem="github", kind="mcp", name=str(server["name"]), parent=owner_repo,
                    description=str(server.get("description") or description),
                    license=license_value, license_scope="repository",
                    source_uri=f"https://github.com/{repo}",
                    content_sha256=sha256_text(json.dumps(server, sort_keys=True)),
                    capabilities=_capabilities("mcp", server["name"], description, server.get("tags")),
                    tags=tuple(["mcp", "github"] + [str(t) for t in server.get("tags") or ()]),
                    install_mode="register_disabled" if installable else "metadata",
                    status=status, reasons=reasons, runtime_risk=risk,
                    metadata={"server": spec, "repository": repo,
                              "package": server.get("package", ""),
                              "notes": server.get("notes", "")},
                ))
        else:
            status, reasons, risk = classify(
                kind="plugin", license=license_value, install_mode="metadata",
            )
            emit(FederatedItem(
                ecosystem="github", kind=str(entry.get("kind") or "plugin"), name=str(entry.get("name") or owner_repo),
                description=description, license=license_value, license_scope="repository",
                source_uri=f"https://github.com/{repo}", content_sha256=sha256_text(json.dumps(entry, sort_keys=True)),
                capabilities=_capabilities(entry.get("name"), description, entry.get("tags")),
                tags=tuple(["github"] + [str(t) for t in entry.get("tags") or ()]),
                install_mode="metadata", status=status, reasons=reasons, runtime_risk=risk,
                metadata={"repository": repo, "notes": entry.get("notes", "")},
            ))
    return items


# ----------------------------------------------------------------------
# Orquestração da coleta
# ----------------------------------------------------------------------
def collect(repo_root: Path, *, home: Optional[Path] = None) -> List[FederatedItem]:
    """Coleta todas as fontes e devolve a lista ordenada por identificador."""

    home = Path(home or os.path.expanduser("~")).resolve()
    repo_root = Path(repo_root).resolve()
    items: List[FederatedItem] = []
    for extractor in (
        lambda: claude_items(home, repo_root),
        lambda: antigravity_items(home, repo_root),
        lambda: chatgpt_items(home, repo_root),
        lambda: github_items(repo_root),
    ):
        try:
            items.extend(extractor())
        except (OSError, ValueError) as exc:  # fonte corrompida não derruba as demais
            items.append(FederatedItem(
                ecosystem="github", kind="plugin", name=f"erro-de-fonte-{slugify(str(exc))[:40]}",
                description=f"Fonte ignorada por erro: {type(exc).__name__}",
                license="", status="degraded", reasons=("source_error",),
                metadata={"error": str(exc)[:300]},
            ))
    # Deduplicação final: o primeiro item de cada id vence.
    unique: Dict[str, FederatedItem] = {}
    for item in items:
        unique.setdefault(item.item_id, item)
    return [unique[key] for key in sorted(unique)]
