"""R1025 — guarda operacional para projetos Remotion.

O módulo é local e somente leitura: não instala, não renderiza, não abre
navegador, não executa Node/Remotion e não acessa a rede. Ele resume a licença,
inspeciona arquivos do projeto, pré-checa um plano R1024 e decide se um comando
de shell exige aprovação explícita.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

LICENSE_COMMIT = "1e55bdc62fb2a9e828060b9728a767f27816f762"
LICENSE_URL = (
    "https://github.com/remotion-dev/remotion/blob/"
    f"{LICENSE_COMMIT}/LICENSE.md"
)
LICENSE_NAME = "Remotion License (não OSI)"

MAX_FILES = 2000
MAX_BYTES = 20 * 1024 * 1024
MAX_FILE_BYTES = 1024 * 1024
SKIP_DIRS = {
    ".git", "node_modules", "out", "build", "dist", ".next", ".cache",
    "coverage", "vendor", "__pycache__",
}
EXACT_VERSION = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
COMPOSITION = re.compile(r"<Composition\b([^>]*)>", re.S)
ATTRIBUTE = re.compile(
    r"\b(id|durationInFrames|fps|width|height)\s*=\s*"
    r"(?:\"([^\"]*)\"|'([^']*)'|\{([^}]*)\})"
)
RENDER_COMMAND = re.compile(r"\bremotion\s+(?:render|still|bundle)\b", re.I)
STUDIO_COMMAND = re.compile(r"\bremotion\s+studio\b", re.I)
UPGRADE_COMMAND = re.compile(r"\bremotion\s+upgrade\b", re.I)
INSTALL_COMMAND = re.compile(
    r"\b(?:npm|pnpm|yarn|bun)\s+(?:install|i|add)\b[^;&|]*"
    r"\b(?:remotion|@remotion/)",
    re.I,
)
REMOTION_COMMAND = re.compile(r"\bremotion\b", re.I)

ENTITY_TYPES = {"individual", "nonprofit", "for_profit"}
LICENSE_FILES = {"license", "license.md", "license.txt", "copying", "copying.md"}
CONFIG_NAMES = {
    "remotion.config.ts", "remotion.config.js", "remotion.config.mjs",
    "remotion.config.cjs",
}
ENTRY_NAMES = {"root.tsx", "root.jsx", "index.ts", "index.tsx", "video.tsx"}


class RemotionError(ValueError):
    """Falha de inspeção local, com código estável."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def _license_result(status: str, reasons: list[str], notes: list[str]) -> dict:
    return {
        "status": status,
        "reasons": reasons,
        "license": LICENSE_NAME,
        "license_commit": LICENSE_COMMIT,
        "license_url": LICENSE_URL,
        "legal_advice": False,
        "warranty": False,
        "notes": notes,
    }


def license_scope(entity_type, employees=None, commercial_use=True,
                  resell=False) -> dict:
    """Resume a elegibilidade da Remotion License; não é parecer jurídico."""
    if resell is True:
        return _license_result(
            "blocked", ["resale_forbidden"],
            ["A licença não permite vender, alugar ou relicenciar derivado do Remotion."],
        )
    kind = entity_type.strip().lower() if isinstance(entity_type, str) else ""
    if kind not in ENTITY_TYPES:
        return _license_result(
            "blocked", ["entity_unknown"],
            ["Informe individual, nonprofit ou for_profit; não presuma elegibilidade."],
        )
    if kind in {"individual", "nonprofit"}:
        return _license_result(
            "eligible_free", [],
            ["Uso gratuito conforme o resumo da licença; confirme o texto oficial."],
        )
    if employees is None:
        return _license_result(
            "blocked", ["employees_required"],
            ["Para for_profit, o número de funcionários decide a elegibilidade."],
        )
    if isinstance(employees, bool) or not isinstance(employees, int) or employees < 0:
        return _license_result(
            "blocked", ["employees_invalid"],
            ["employees deve ser inteiro não negativo."],
        )
    if employees <= 3:
        return _license_result(
            "eligible_free", [],
            ["Empresa for_profit com até 3 funcionários no resumo da licença."],
        )
    return _license_result(
        "company_license_required", [],
        ["Empresa for_profit acima de 3 funcionários exige licença comercial."],
    )


def _read(path: Path, limit: int = MAX_FILE_BYTES) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def _collect_files(root: Path):
    files = []
    total = 0
    truncated = False
    oversized = []
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(
            name for name in dirnames
            if name not in SKIP_DIRS and not name.startswith(".")
        )
        for name in sorted(filenames):
            path = Path(directory) / name
            if path.is_symlink():
                continue
            try:
                size = path.stat().st_size
            except OSError:
                continue
            relative = path.relative_to(root).as_posix()
            if size > MAX_FILE_BYTES:
                oversized.append(relative)
                continue
            if len(files) >= MAX_FILES or total + size > MAX_BYTES:
                truncated = True
                break
            files.append((path, relative, size))
            total += size
        if truncated:
            break
    return files, total, truncated, oversized


def _package(files, warnings):
    path = next((item[0] for item in files if item[1] == "package.json"), None)
    if path is None:
        warnings.append("package_json_missing")
        return {}
    try:
        document = json.loads(_read(path, 1024 * 1024))
    except (ValueError, TypeError):
        warnings.append("package_json_invalid")
        return {}
    if not isinstance(document, dict):
        warnings.append("package_json_invalid")
        return {}
    dependencies = {}
    for block in ("dependencies", "devDependencies", "peerDependencies",
                  "optionalDependencies"):
        value = document.get(block)
        if isinstance(value, dict):
            dependencies.update(value)
    remotion = {
        name: str(version) for name, version in sorted(dependencies.items())
        if name == "remotion" or name.startswith("@remotion/")
    }
    pinned = {
        name: bool(EXACT_VERSION.fullmatch(version))
        for name, version in remotion.items()
    }
    scripts = document.get("scripts") if isinstance(document.get("scripts"), dict) else {}
    return {
        "name": document.get("name") if isinstance(document.get("name"), str) else "",
        "version": document.get("version") if isinstance(document.get("version"), str) else "",
        "scripts": {str(k): str(v) for k, v in sorted(scripts.items())},
        "remotion_dependencies": remotion,
        "pinned": pinned,
    }


def _license(files, warnings):
    found = []
    detected = False
    for path, relative, _size in files:
        if "/" in relative or path.name.lower() not in LICENSE_FILES:
            continue
        found.append(path.name)
        if "remotion license" in _read(path, 200 * 1024).lower():
            detected = True
    if not found:
        warnings.append("license_file_missing")
    elif not detected:
        warnings.append("remotion_license_not_found")
    return {"files": sorted(found), "remotion_license_detected": detected}


def _compositions(files):
    found = []
    for path, relative, _size in files:
        if path.suffix.lower() not in {".tsx", ".jsx", ".ts", ".js"}:
            continue
        text = _read(path)
        for match in COMPOSITION.finditer(text):
            attributes = {}
            for attribute in ATTRIBUTE.finditer(match.group(1)):
                key = attribute.group(1)
                value = next(
                    (part for part in attribute.groups()[1:] if part is not None),
                    "",
                ).strip()
                attributes[key] = value
            identifier = attributes.get("id", "")
            if not identifier:
                continue
            item = {
                "id": identifier,
                "file": relative,
                "line": text.count("\n", 0, match.start()) + 1,
            }
            for key, output in (
                ("durationInFrames", "duration_in_frames"),
                ("fps", "fps"),
                ("width", "width"),
                ("height", "height"),
            ):
                raw = attributes.get(key)
                item[output] = int(raw) if raw and raw.isdigit() else None
            found.append(item)
    return sorted(found, key=lambda item: (item["file"], item["line"], item["id"]))


def scan_project(path) -> dict:
    """Inspeciona um projeto Remotion local sem executá-lo."""
    target = Path(path).expanduser()
    if target.is_symlink():
        raise RemotionError("unsafe_path", "projeto não pode ser symlink")
    root = target.resolve()
    if not root.is_dir():
        raise RemotionError("path_not_directory", "caminho deve ser diretório")
    files, total, truncated, oversized = _collect_files(root)
    warnings = []
    if truncated:
        warnings.append("scan_truncated")
    if oversized:
        warnings.append("file_skipped_oversized")
    package = _package(files, warnings)
    license_info = _license(files, warnings)
    config_files = sorted(
        relative for _path, relative, _size in files
        if relative in CONFIG_NAMES
        or (
            relative.startswith("src/")
            and Path(relative).name.lower() in ENTRY_NAMES
        )
    )
    compositions = _compositions(files)
    if not compositions:
        warnings.append("no_compositions_found")
    return {
        "root": str(root),
        "status": "scanned" if package else "partial",
        "package": package,
        "license": license_info,
        "config_files": config_files,
        "compositions": compositions,
        "warnings": sorted(set(warnings)),
        "files_scanned": len(files),
        "bytes_scanned": total,
        "limits": {
            "max_files": MAX_FILES,
            "max_bytes": MAX_BYTES,
            "max_file_bytes": MAX_FILE_BYTES,
        },
        "executed": False,
        "network": False,
    }


def render_preflight(plan, composition_id=None, output_path=None,
                     project_path=None) -> dict:
    """Valida o plano R1024 e confere composição/saída; não renderiza."""
    from integrations.video_edit_plan import validate_plan

    checked = validate_plan(plan)
    reasons = []
    warnings = []
    if checked["status"] != "valid":
        reasons.append({
            "code": "plan_invalid", "path": "$",
            "message": "plano precisa ser válido antes do render",
        })
    else:
        expected = checked["summary"]["output"]["path"]
        if output_path is not None and output_path != expected:
            reasons.append({
                "code": "output_path_mismatch", "path": "output_path",
                "message": f"esperado {expected}",
            })
        if project_path is not None:
            scanned = scan_project(project_path)
            if composition_id:
                identifiers = {item["id"] for item in scanned["compositions"]}
                if composition_id not in identifiers:
                    reasons.append({
                        "code": "composition_not_found", "path": "composition_id",
                        "message": f"composição {composition_id} não encontrada",
                    })
            else:
                warnings.append("composition_not_specified")
        elif composition_id is None:
            warnings.append("composition_not_specified")
    return {
        "status": "ready" if not reasons else "blocked",
        "plan_status": checked["status"],
        "reasons": reasons,
        "warnings": warnings,
        "composition_id": composition_id,
        "render_executed": False,
        "visual_quality_verified": False,
    }


def command_policy(command, render_approved=False, license_ack=False) -> dict:
    """Decide se um comando de shell precisa de aprovação; não executa nada."""
    if not isinstance(command, str) or not command.strip():
        return {
            "decision": "block", "code": "invalid_command",
            "reason": "comando vazio ou inválido", "command": command,
            "executed": False,
        }
    normalized = " ".join(command.split())
    if INSTALL_COMMAND.search(normalized):
        if license_ack is True:
            return {
                "decision": "allow", "code": "install_license_acknowledged",
                "reason": "ciência da licença registrada pelo operador",
                "command": normalized, "executed": False,
            }
        return {
            "decision": "block", "code": "license_ack_required",
            "reason": "instalação de Remotion exige REMOTION_LICENSE_ACK=1",
            "command": normalized, "executed": False,
        }
    if RENDER_COMMAND.search(normalized):
        if render_approved is True:
            return {
                "decision": "allow", "code": "render_approved",
                "reason": "render autorizado explicitamente pelo operador",
                "command": normalized, "executed": False,
            }
        return {
            "decision": "block", "code": "render_requires_approval",
            "reason": "render/still/bundle exige REMOTION_RENDER_APPROVED=1",
            "command": normalized, "executed": False,
        }
    if STUDIO_COMMAND.search(normalized):
        return {
            "decision": "allow", "code": "preview_allowed",
            "reason": "prévia interativa não renderiza o vídeo",
            "command": normalized, "executed": False,
        }
    if UPGRADE_COMMAND.search(normalized):
        return {
            "decision": "block", "code": "upgrade_requires_review",
            "reason": "upgrade altera dependências; revise antes",
            "command": normalized, "executed": False,
        }
    if REMOTION_COMMAND.search(normalized):
        return {
            "decision": "allow", "code": "remotion_readonly",
            "reason": "comando Remotion sem render nem instalação",
            "command": normalized, "executed": False,
        }
    return {
        "decision": "allow", "code": "unrelated",
        "reason": "comando não pertence ao fluxo Remotion",
        "command": normalized, "executed": False,
    }
