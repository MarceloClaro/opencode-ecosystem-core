"""SPEC-935-R841: registro coordenado das camadas de provedor do REA.

A prontidão é uma sonda local sobre variáveis de ambiente, diretórios e
comandos declarados pelo próprio REA (docs/architecture.mermaid, subgrafo
"Provider Layers"). Ela **não** abre alvos, **não** inicia o REA, **não**
executa aplicações e **não** promove confiança. Os nomes de ferramenta são os
anunciados pelo catálogo MCP do REA 6.4.0 e não são inventados aqui.

Camadas "bundled" têm o motor embarcado no REA; camadas "engine" dependem de um
motor externo resolvido por variável de ambiente, cujo nome é documentado pelo
próprio REA (docs/*.md).
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


NATIVE_ROOT = Path.home() / ".local" / "share" / "opencode-core" / "native-rea"
PLAYWRIGHT_HOME = Path(os.environ.get("CORE_BROWSER_HOME")
                       or Path.home() / ".local" / "share" / "opencode-core" / "playwright-mcp")

# Caminhos padrão do launcher Hopper documentados pelo REA (docs/installation.md#hopper);
# substituível em teste para isolamento do host.
HOPPER_DEFAULT_LAUNCHERS: tuple[Path, ...] = (
    Path("/opt/hopper/bin/Hopper"),
    Path.home() / ".local" / "share" / "rea" / "hopper" / "bin" / "Hopper",
    Path("/Applications/Hopper Disassembler.app/Contents/MacOS/hopper"),
)


# Ferramentas de inspeção estática por caminho, com o campo de caminho exigido
# pelo schema real e valores fixos aceitos pela ferramenta.
LAYERS: tuple[dict[str, Any], ...] = (
    {
        "id": "javascript",
        "title": "JavaScript / Electron / sourcemaps",
        "kind": "bundled",
        "engine": "Analisador JavaScript embarcado no REA",
        "env": (),
        "inspection": {"tool": "analyze_javascript_application", "path_field": "input_path",
                       "fixed": {"detail": "complete", "format": "auto", "integrity_policy": "fail"}},
        "tools": ("analyze_javascript_application", "recover_javascript_sources",
                  "compare_source_to_bundle", "trace_javascript_semantics", "export_web_scripts"),
        "reference": "docs/architecture.mermaid#inspector",
    },
    {
        "id": "native_ghidra",
        "title": "Binário nativo (Ghidra)",
        "kind": "engine",
        "engine": "Ghidra 12.x + JDK 21",
        "env": (
            {"name": "GHIDRA_INSTALL_DIR", "kind": "dir", "default": NATIVE_ROOT / "ghidra_12.1.4_PUBLIC"},
            {"name": "JAVA_HOME", "kind": "dir", "default": NATIVE_ROOT / "jdk-21.0.12.1+1"},
        ),
        "inspection": None,
        "tools": ("open_binary", "analyze_function", "binary_session", "close_binary",
                  "batch_decompile", "list_procedures", "xrefs"),
        "reference": "docs/architecture.mermaid#ghidra-ida-hopper; SPEC-935-R823",
    },
    {
        "id": "native_ida",
        "title": "Binário nativo (IDA)",
        "kind": "engine",
        "engine": "IDA MCP registrado no REA",
        "env": ({"name": "REA_IDA_MCP_CONFIG", "kind": "path", "format": "ida_mcp_config"},),
        "inspection": None,
        "tools": ("open_binary", "analyze_function"),
        "reference": "docs/installation.md#ida",
    },
    {
        "id": "native_hopper",
        "title": "Binário nativo (Hopper)",
        "kind": "engine",
        "engine": "Hopper (launcher; demo/licença do operador)",
        "env": ({"name": "HOPPER_LAUNCHER_PATH", "kind": "command"},),
        "inspection": None,
        "tools": ("open_binary",),
        "reference": "docs/installation.md#hopper",
    },
    {
        "id": "apple",
        "title": "Apple (Mach-O / plist / Objective-C / Swift)",
        "kind": "bundled",
        "engine": "Leitores Mach-O/plist embarcados no REA",
        "env": (),
        "inspection": {"tool": "inspect_plist", "path_field": "path", "fixed": {}},
        "tools": ("inspect_macho", "inspect_plist", "analyze_swift_types",
                  "get_objc_classes", "get_objc_protocols", "project_apple_application_graph"),
        "reference": "docs/architecture.mermaid#apple",
    },
    {
        "id": "android_jadx",
        "title": "Android (JADX headless)",
        "kind": "engine",
        "engine": "jadx-headless-mcp 0.7.1",
        "env": ({"name": "REA_JADX_MCP_JAR", "kind": "path"},),
        "inspection": {"tool": "inspect_android_package", "path_field": "path", "fixed": {}},
        "tools": ("inspect_android_package", "inspect_android_class", "inspect_android_method",
                  "search_android_classes", "trace_android_references", "project_android_application_graph"),
        "reference": "docs/android-analysis.md",
    },
    {
        "id": "android_apktool",
        "title": "Android (recursos via apktool)",
        "kind": "engine",
        "engine": "apktool",
        "env": ({"name": "REA_APKTOOL_COMMAND", "kind": "command"},),
        "inspection": {"tool": "decode_android_resources", "path_field": "path", "fixed": {}},
        "tools": ("decode_android_resources", "inspect_apktool_client"),
        "reference": "docs/apktool-resource-analysis.md",
    },
    {
        "id": "android_adb",
        "title": "Android (runtime em dispositivo via adb)",
        "kind": "engine",
        "engine": "Android Platform Tools (adb)",
        "env": ({"name": "REA_ADB_PATH", "kind": "command"},),
        "inspection": None,
        "tools": ("inspect_adb_client", "inspect_adb_device", "list_adb_devices",
                  "capture_adb_screen", "collect_adb_bugreport", "read_adb_logcat"),
        "reference": "docs/android-analysis.md#adb",
    },
    {
        "id": "firmware",
        "title": "Firmware (binwalk + unblob)",
        "kind": "engine",
        "engine": "Unblob 26.6.x e Binwalk 3.1.x",
        "env": (
            {"name": "REA_UNBLOB_COMMAND", "kind": "command"},
            {"name": "REA_BINWALK_COMMAND", "kind": "command"},
        ),
        "inspection": {"tool": "inspect_firmware_regions", "path_field": "path", "fixed": {}},
        "tools": ("inspect_firmware_regions", "extract_firmware"),
        "reference": "docs/firmware-analysis.md",
    },
    {
        "id": "native_offline_elf",
        "title": "ELF/core offline (pwntools)",
        "kind": "engine",
        "engine": "pwntools 4.15.0 + pyelftools + Unicorn",
        "env": ({"name": "REA_PWNTOOLS_PYTHON", "kind": "command"},),
        "inspection": {"tool": "inspect_binary_layout", "path_field": "path", "fixed": {}},
        "tools": ("inspect_binary_layout",),
        "reference": "docs/binary-diagnostics.md",
    },
    {
        "id": "native_core_crash",
        "title": "Crash/core gravado (pwntools + pwndbg)",
        "kind": "engine",
        "engine": "pwntools 4.15.0 + pwndbg + gdb",
        "env": (
            {"name": "REA_PWNTOOLS_PYTHON", "kind": "command"},
            {"name": "REA_PWNDBG_GDB", "kind": "command"},
            {"name": "REA_PWNDBG_GDBINIT", "kind": "path"},
            {"name": "REA_PWNDBG_VENV_PATH", "kind": "dir"},
        ),
        "inspection": {"tool": "inspect_recorded_crash", "path_field": "path", "fixed": {}},
        "tools": ("inspect_recorded_crash",),
        "reference": "docs/recorded-crashes.md",
    },
    {
        "id": "managed_dotnet",
        "title": "Gerenciado (.NET / PE managed)",
        "kind": "bundled",
        "engine": "Leitor de metadados .NET embarcado no REA",
        "env": ({"name": "REA_ILSPY_CMD_PATH", "kind": "command", "optional": True},),
        "inspection": {"tool": "inspect_managed_artifact", "path_field": "path", "fixed": {}},
        "tools": ("inspect_managed_artifact", "inspect_managed_members",
                  "project_managed_application_graph"),
        "reference": "docs/architecture.mermaid#dotnet",
    },
    {
        "id": "pe_resources",
        "title": "Recursos PE",
        "kind": "bundled",
        "engine": "Leitor PE embarcado no REA",
        "env": (),
        "inspection": {"tool": "inspect_pe_resources", "path_field": "path", "fixed": {}},
        "tools": ("inspect_pe_resources",),
        "reference": "docs/architecture.mermaid#pe",
    },
    {
        "id": "evm",
        "title": "EVM / bytecode (evmole)",
        "kind": "bundled",
        "engine": "evmole embarcado no REA",
        "env": ({"name": "REA_EVM_PRLIMIT_COMMAND", "kind": "command", "optional": True},),
        "inspection": {"tool": "inspect_evm_interface", "path_field": "path", "fixed": {},
                       "encoding": True},
        "tools": ("inspect_evm_interface",),
        "reference": "docs/architecture.mermaid#evm",
    },
    {
        "id": "browser",
        "title": "Navegador / web runtime",
        "kind": "engine",
        "engine": "Chromium coordenado (SPEC-935-R824)",
        "env": ({"name": "REA_BROWSER_EXECUTABLE", "kind": "path"},),
        "inspection": None,
        "tools": ("capture_browser_scenario", "capture_web_screenshot", "inspect_web_page",
                  "observe_web_session", "export_web_scripts"),
        "reference": "SPEC-935-R824",
    },
    {
        "id": "jeb",
        "title": "Android (JEB)",
        "kind": "engine",
        "engine": "JEB MCP",
        "env": ({"name": "REA_JEB_MCP_URL", "kind": "url", "format": "local_mcp_url",
                 "require_explicit": True},),
        "inspection": None,
        "tools": ("inspect_jeb_client", "list_jeb_units", "decompile_jeb_item"),
        "reference": "docs/architecture.mermaid#android",
    },
    {
        "id": "artifact",
        "title": "Artefatos e pacotes Evidence",
        "kind": "bundled",
        "engine": "Leitor de artefatos embarcado no REA",
        "env": (),
        "inspection": {"tool": "inspect_keyed_archive", "path_field": "path", "fixed": {}},
        "tools": ("inspect_artifact", "inspect_keyed_archive", "extract_artifact",
                  "compare_artifacts", "export_evidence_bundle", "import_evidence_bundle"),
        "reference": "docs/architecture.mermaid#reference",
    },
    {
        "id": "reference",
        "title": "Referência e bundles de Evidence",
        "kind": "bundled",
        "engine": "Leitor de referência embarcado no REA",
        "env": (),
        "inspection": None,
        "tools": ("get_evidence_bundle", "import_evidence_bundle", "export_evidence_bundle"),
        "reference": "docs/architecture.mermaid#reference",
    },
)

_BY_ID = {layer["id"]: layer for layer in LAYERS}
LAYER_IDS = frozenset(_BY_ID)

# Superfícies que o próprio REA declara no catálogo MCP (campo `surface`). Servem
# apenas de âncora de auditoria: toda ferramenta listada em uma camada deve
# pertencer a uma destas superfícies, e o schema ainda é conferido no handshake.
SURFACES: dict[str, tuple[str, ...]] = {
    "javascript": ("electron-provider", "application"),
    "native_ghidra": ("official-proxy", "enhanced", "session"),
    "native_ida": ("session", "enhanced", "official-proxy"),
    "native_hopper": ("session",),
    "apple": ("native-provider", "enhanced", "application"),
    "android_jadx": ("android-provider", "application"),
    "android_apktool": ("apktool-provider",),
    "android_adb": ("adb-provider",),
    "firmware": ("firmware-provider",),
    "native_offline_elf": ("native-provider",),
    "native_core_crash": ("native-provider",),
    "managed_dotnet": ("managed-provider", "application"),
    "pe_resources": ("native-provider",),
    "evm": ("artifact-provider",),
    "browser": ("browser-provider", "application"),
    "jeb": ("jeb-provider",),
    "artifact": ("artifact-provider", "session"),
    "reference": ("session", "artifact-provider"),
}


def layer_surfaces(layer_id: str) -> tuple[str, ...]:
    return SURFACES.get(layer_id, ())


ENCODINGS = frozenset({"raw", "hex"})

# Requisitos de versão declarados pelo REA (docs/*.md); informativos, não provados aqui.
REQUIREMENTS = {
    "native_ghidra": "Ghidra 12.x e JDK 21 (caminhos absolutos completos)",
    "native_ida": "IDA MCP registrado em REA_IDA_MCP_CONFIG (licença comercial do operador)",
    "native_hopper": "Hopper launcher (HOPPER_LAUNCHER_PATH ou instalação padrão; demo/licença comercial do operador)",
    "android_jadx": "jadx-headless-mcp 0.7.1 (fat jar)",
    "android_apktool": "apktool 2.7.0 ou mais recente + runtime Java",
    "android_adb": "Android Platform Tools (adb) em PATH ou REA_ADB_PATH",
    "firmware": "Unblob 26.6.x e Binwalk 3.1.x + prlimit",
    "native_offline_elf": "Python 3.12 com pwntools, pyelftools 0.33 e Unicorn 2.1.2",
    "native_core_crash": "pwntools + pwndbg (gdbinit.py) e gdb",
    "browser": "Chromium Playwright (R824) via REA_BROWSER_EXECUTABLE",
    "jeb": "JEB MCP em URL local explícita (REA_JEB_MCP_URL; serviço comercial do operador)",
}

_DISCOVERED: dict[str, str] | None = None


def _discovered() -> dict[str, str]:
    # A instalação/configuração pode mudar após o setup no mesmo processo.
    return engine_environment()


def layer(layer_id: str) -> dict[str, Any] | None:
    return _BY_ID.get(layer_id)


def layer_inspection(layer_id: str) -> dict[str, Any] | None:
    entry = _BY_ID.get(layer_id)
    return dict(entry["inspection"]) if entry and entry.get("inspection") else None


def _validate_ida_mcp_config(candidate: Path) -> tuple[bool, str]:
    """Fail-closed: aceita somente os formatos documentados de REA_IDA_MCP_CONFIG
    (docs/ida-provider.md do REA 6.4.0): registro stdio com command+args,
    supervisor headless com mode/url, ou objeto mcpServers com entrada ida-pro-mcp."""
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return False, f"JSON inválido: {exc.__class__.__name__}"
    if not isinstance(payload, dict):
        return False, "registro deve ser um objeto JSON"

    def _registration_ok(reg: object) -> bool:
        if not isinstance(reg, dict):
            return False
        has_stdio = isinstance(reg.get("command"), str) and reg.get("command") and \
            isinstance(reg.get("args"), list) and all(isinstance(a, str) for a in reg["args"])
        has_url = isinstance(reg.get("url"), str) and _validate_local_mcp_url(reg["url"])[0]
        if "url" in reg and not has_url:
            return False
        if not (has_stdio or has_url):
            return False
        mode = reg.get("mode")
        if mode is not None and mode != "headless":
            return False
        for key, expected in (("env", dict), ("timeoutMs", int), ("workspaceRoot", str)):
            if key in reg and not isinstance(reg[key], expected):
                return False
        return True

    if _registration_ok(payload):
        return True, "registro stdio/headless válido"
    servers = payload.get("mcpServers")
    if isinstance(servers, dict) and isinstance(servers.get("ida-pro-mcp"), dict) \
            and _registration_ok(servers["ida-pro-mcp"]):
        return True, "mcpServers com entrada ida-pro-mcp válida"
    return False, "registro não corresponde a command+args, url/mode ou mcpServers:ida-pro-mcp"


def _validate_local_mcp_url(value: str) -> tuple[bool, str]:
    """Fail-closed, espelha o REA (docs/jeb-analysis.md): http/https absoluto,
    host literal 127.0.0.1 ou [::1]; rejeita credenciais, query e fragmento."""
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        return False, f"URL inválida: {exc.__class__.__name__}"
    if parsed.scheme not in ("http", "https"):
        return False, "esquema deve ser http ou https"
    if parsed.hostname not in ("127.0.0.1", "::1"):
        return False, "host deve ser literal 127.0.0.1 ou [::1]"
    if port == 0 or parsed.netloc.endswith(":"):
        return False, "porta deve estar entre 1 e 65535"
    if parsed.username is not None or parsed.password is not None:
        return False, "URL não pode conter credenciais"
    if parsed.query or parsed.fragment:
        return False, "URL não pode conter query ou fragmento"
    return True, "URL MCP local válida"


def _env_state(entry: dict[str, Any]) -> dict[str, Any]:
    name = entry["name"]
    kind = entry.get("kind", "path")
    optional = bool(entry.get("optional"))
    fmt = entry.get("format")
    require_explicit = bool(entry.get("require_explicit"))
    value = os.environ.get(name, "")
    source = "environment"
    if not value:
        discovered = _discovered().get(name)
        if discovered:
            value = discovered
            source = "isolated_engine"
    state = {"name": name, "kind": kind, "optional": optional, "set": bool(value),
             "value": value or None, "resolved": None, "ok": False, "source": source if value else None,
             "reason": None}
    if not value:
        default = entry.get("default")
        if default is not None and Path(default).exists() and not require_explicit:
            state.update(resolved=str(default), ok=True, source="default")
        elif optional:
            state["source"] = "optional_absent"
        else:
            state["reason"] = f"{name} não configurado"
        return state
    if kind == "url":
        if fmt == "local_mcp_url":
            ok, reason = _validate_local_mcp_url(value)
            state.update(resolved=value, ok=ok, reason=None if ok else reason)
            return state
        state.update(resolved=value, ok=True)
        return state
    if fmt == "ida_mcp_config":
        ok, reason = _validate_ida_mcp_config(Path(value).expanduser())
        state.update(resolved=str(Path(value).expanduser().resolve()),
                     ok=ok and Path(value).expanduser().is_file(),
                     reason=None if (ok and Path(value).expanduser().is_file()) else
                     (reason if Path(value).expanduser().is_file() else f"{name} não é arquivo"))
        return state
    candidate = Path(value).expanduser()
    if kind == "command":
        found = str(candidate.resolve()) if candidate.is_file() and os.access(candidate, os.X_OK) \
            else shutil.which(value)
        state.update(resolved=found, ok=bool(found),
                     reason=None if found else f"{name}: executável não encontrado")
        return state
    resolved = str(candidate.resolve())
    ok = candidate.is_dir() if kind == "dir" else candidate.is_file()
    state.update(resolved=resolved, ok=ok,
                 reason=None if ok else f"{name}: caminho ausente")
    return state


def probe_layer(layer_id: str) -> dict[str, Any]:
    entry = _BY_ID[layer_id]
    env = [_env_state(item) for item in entry["env"]]
    required = [state for state in env if not state["optional"]]
    if entry["kind"] == "bundled":
        ready = True
        reason = "Motor embarcado no REA; sem dependência externa obrigatória."
    else:
        missing = [state["name"] for state in required if not state["ok"]]
        ready = bool(required) and not missing
        reason = ("Motores externos resolvidos." if ready
                  else "Motores externos pendentes: " + ", ".join(missing) + ".")
    inspection = entry.get("inspection")
    return {
        "id": entry["id"], "title": entry["title"], "kind": entry["kind"],
        "engine": entry["engine"], "ready": ready, "env": env,
        "requirement": REQUIREMENTS.get(entry["id"]),
        "inspection_tool": (inspection or {}).get("tool"),
        "surfaces": list(SURFACES.get(entry["id"], ())),
        "tools": list(entry["tools"]), "reference": entry["reference"], "reason": reason,
    }


def layers_status() -> dict[str, Any]:
    """Mapa de prontidão das camadas; nunca abre alvo nem inicia o REA."""
    rows = [probe_layer(layer_id) for layer_id in _BY_ID]
    ready = [row for row in rows if row["ready"]]
    return {
        "operation": "layers", "status": "completed", "success": True,
        "verification": "local_readiness_probe",
        "layers": rows,
        "summary": {
            "total": len(rows), "ready": len(ready), "pending": len(rows) - len(ready),
            "inspectable": sum(1 for row in rows if row["inspection_tool"]),
        },
        "limitations": [
            "A prontidão é sonda de configuração local; não prova execução da camada.",
            "Camadas empacotadas ainda dependem do runtime REA (operation=status/session).",
            "Nenhum alvo é aberto nem executado por esta operação.",
        ],
    }


def engine_environment() -> dict[str, str]:
    """Exporta comandos de motores já presentes; nunca inventa caminhos."""
    discovered: dict[str, str] = {}
    wrappers = {
        "REA_UNBLOB_COMMAND": NATIVE_ROOT / "bin" / "unblob",
        "REA_APKTOOL_COMMAND": NATIVE_ROOT / "bin" / "apktool",
        "REA_BINWALK_COMMAND": NATIVE_ROOT / "bin" / "binwalk",
    }
    for name, path in wrappers.items():
        if name not in os.environ and path.is_file() and os.access(path, os.X_OK):
            discovered[name] = str(path)
    jar = NATIVE_ROOT / "jadx-headless-mcp-0.7.1-all.jar"
    if "REA_JADX_MCP_JAR" not in os.environ and jar.is_file():
        discovered["REA_JADX_MCP_JAR"] = str(jar)
    pwntools_python = NATIVE_ROOT / "py-pwntools" / "bin" / "python"
    pwndbg_init = NATIVE_ROOT / "pwndbg" / "gdbinit.py"
    pwndbg_venv = NATIVE_ROOT / "pwndbg" / ".venv"
    browsers = sorted(PLAYWRIGHT_HOME.glob("browsers/chromium-*/chrome-linux*/chrome"))
    browser = next((path for path in browsers if path.is_file() and os.access(path, os.X_OK)), None)
    hopper_candidates = HOPPER_DEFAULT_LAUNCHERS
    hopper = next((path for path in hopper_candidates
                   if path.is_file() and os.access(path, os.X_OK)), None)
    computed = {
        "REA_ADB_PATH": shutil.which("adb"),
        "REA_BROWSER_EXECUTABLE": str(browser) if browser is not None else None,
        "REA_PWNTOOLS_PYTHON": str(pwntools_python) if os.access(pwntools_python, os.X_OK) else None,
        "REA_PWNDBG_GDB": shutil.which("gdb"),
        "REA_PWNDBG_GDBINIT": str(pwndbg_init) if pwndbg_init.is_file() else None,
        "REA_PWNDBG_VENV_PATH": str(pwndbg_venv) if pwndbg_venv.is_dir() else None,
        "HOPPER_LAUNCHER_PATH": str(hopper) if hopper is not None else None,
    }
    for name, value in computed.items():
        if name not in os.environ and value:
            discovered[name] = value
    return discovered
