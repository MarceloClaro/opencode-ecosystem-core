"""R921/R922: evidência local e extração instrucional seletiva, sem ativação.

Não há descoberta de HOME, acesso à rede, execução de código de plugins ou
registro alternativo. Licenças são reconhecidas conservadoramente por texto;
isso não constitui parecer jurídico. R921 permanece estrito em POSIX. Somente
o escopo pinned R922 projeta bits de dados em montagem 9p/DrvFS sem metadata,
observada efetivamente; fingerprints de origem nunca são projetados.

A transação protege contra falhas normais de I/O e deriva observada da origem.
Não é um journal de recuperação de energia nem um lock entre escritores não
cooperativos. O primário continua responsável por autorizar a operação real.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import tempfile
from typing import Any, Iterator


MAX_PACKAGES = 64
MAX_FILES_PER_PACKAGE = 256
MAX_FILE_BYTES = 1_048_576
MAX_TOTAL_BYTES = 16_777_216

_NAMESPACES = (
    "claude-cowork", "created-by-me-remote", "openai-bundled", "openai-curated-remote",
)
_MANIFESTS = (".codex-plugin/plugin.json", ".claude-plugin/plugin.json", "plugin.json")
_ID = re.compile(r"[A-Za-z0-9_-]{1,100}\Z")
_COMPONENT = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.+-]{0,199}\Z")
_TEXT_SUFFIXES = {".md", ".txt", ".rst"}
_PERMISSIVE = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause"}
_DOCUMENT_SKILLS = {"docx", "pdf", "pptx", "xlsx"}
_EXCLUDED_PARTS = {
    "scripts", "hooks", "bin", "node_modules", ".git", ".hg", ".svn", "__pycache__",
}
_SENSITIVE = {
    "auth.json", "credentials", "credentials.json", "token.json", "tokens.json",
    "cookies", "cookies.json", "cookies.sqlite", "cookies.sqlite3", "cookies.txt",
    "history", "history.json", "history.jsonl", "history.sqlite", "history.sqlite3",
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", ".netrc", ".npmrc", ".pypirc",
    ".ssh", ".aws", ".azure", ".gnupg", ".bash_history", ".zsh_history",
}
_RESTRICTED_TEXT = re.compile(
    r"proprietary|no (?:copying|extraction|redistribution)|"
    r"(?:copying|extraction|redistribution) (?:is )?(?:not permitted|prohibited)|"
    r"(?:may|must|shall) not (?:copy|extract|redistribute|distribute|use)|"
    r"(?:copying|extraction|redistribution|commercial use) (?:is )?forbidden|"
    r"notwithstanding the foregoing|additional (?:restrictions|limitations)|"
    r"non[- ]?commercial (?:use|purposes)|(?:research|internal use) only|"
    r"all advertising materials mentioning|"
    r"all rights reserved[.;]?\s*(?:no |except as)", re.IGNORECASE,
)
_SECRET_VALUE = re.compile(
    r"\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|secret|token)"
    r"[\"']?\s*[:=]\s*(?:\"(?:\\.|[^\"\\\r\n]){8,}\"|"
    r"'(?:\\.|[^'\\\r\n]){8,}'|[A-Za-z0-9_+/.-]{8,})|"
    r"\bauthorization[\"']?\s*[:=]\s*[\"']?(?:bearer|basic)\s+\S+|"
    r"-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----|"
    r"\bsk-[A-Za-z0-9_-]{24,}", re.IGNORECASE,
)
_REGISTRY_LIMIT = 8 * 1024 * 1024
_MAX_DEPTH = 16


def _limits() -> dict[str, int]:
    return {
        "max_packages": MAX_PACKAGES, "max_files_per_package": MAX_FILES_PER_PACKAGE,
        "max_file_bytes": MAX_FILE_BYTES, "max_total_bytes": MAX_TOTAL_BYTES,
    }


def _no_execution() -> dict[str, Any]:
    return {
        "executed": False, "credentials_copied": False, "hooks_executed": False,
        "transport_imported": False, "host_authentication": "not_verified",
        "external_validation": False,
    }


def _sensitive(name: str) -> bool:
    name = name.casefold()
    return name in _SENSITIVE or name == ".env" or name.startswith(".env.")


def _safe_relative(value: Any, *, dot_prefix: bool = False) -> str:
    if (not isinstance(value, str) or not 1 <= len(value) <= 4096
            or "\\" in value or ":" in value or any(ord(c) < 32 for c in value)):
        raise ValueError("unsafe_path")
    if dot_prefix and value.startswith("./"):
        value = value[2:]
    path = PurePosixPath(value)
    if (path.is_absolute() or value != path.as_posix()
            or any(part in {".", ".."} for part in path.parts)):
        raise ValueError("unsafe_path")
    return value


def _absolute(value: str | Path, *, code: str = "unsafe_path") -> Path:
    try:
        path = Path(value)
    except (TypeError, ValueError):
        raise ValueError(code) from None
    if (".." in path.parts or "\\" in str(path) or ":" in str(path)
            or any(ord(c) < 32 for c in str(path))):
        raise ValueError("unsafe_path")
    return Path(os.path.abspath(path))


def _fingerprint(info: os.stat_result) -> tuple[int, ...]:
    # atime não integra a identidade: uma leitura não deve alterar a evidência.
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns, info.st_nlink)


def _existing_chain(path: Path) -> None:
    """lstat em componentes: nunca resolver um symlink e perder sua origem."""
    for part in (*reversed(path.parents), path):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode):
            raise ValueError("unsafe_path")
        if part != path and not stat.S_ISDIR(info.st_mode):
            raise ValueError("unsafe_path")


def _cache_path(value: str | Path) -> Path:
    root = _absolute(value, code="invalid_cache")
    _existing_chain(root)
    try:
        info = root.lstat()
    except FileNotFoundError:
        raise ValueError("invalid_cache") from None
    if not stat.S_ISDIR(info.st_mode):
        raise ValueError("invalid_cache")
    return root


def _destination_path(value: str | Path) -> Path:
    root = _absolute(value)
    _existing_chain(root)
    if root.exists() and not root.is_dir():
        raise ValueError("unsafe_path")
    return root


@contextmanager
def _regular_stream(path: Path) -> Iterator[Any]:
    """Abre componentes com dir_fd/O_NOFOLLOW, sem seguir links intermediários.

    O_NONBLOCK impede bloquear em FIFO trocado após o preflight. Somente um
    descritor confirmado regular é exposto para leitura. Não abre corpos por
    glob/extensão sem que o chamador já tenha aprovado sua licença e finalidade.
    """
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    directory = os.open(path.anchor, flags | os.O_DIRECTORY)
    descriptor = None
    try:
        for part in path.parts[1:-1]:
            child = os.open(part, flags | os.O_DIRECTORY, dir_fd=directory)
            os.close(directory)
            directory = child
        descriptor = os.open(path.name, flags, dir_fd=directory)
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError("unsafe_path")
        # readline do frontmatter não pode antecipar um corpo ainda não licenciado.
        with os.fdopen(descriptor, "rb", buffering=0) as stream:
            descriptor = None
            yield stream
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)


def _read(path: Path, expected: tuple[int, ...], *, ceiling: int = MAX_FILE_BYTES) -> bytes:
    if expected[3] > ceiling:
        raise ValueError("limit_exceeded")
    with _regular_stream(path) as stream:
        if _fingerprint(os.fstat(stream.fileno())) != expected:
            raise ValueError("source_changed")
        raw = stream.read(ceiling + 1)
        if (len(raw) != expected[3] or len(raw) > ceiling
                or _fingerprint(os.fstat(stream.fileno())) != expected):
            raise ValueError("source_changed")
    return raw


def _text(raw: bytes) -> str:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError:
        raise ValueError("unsafe_instruction") from None
    if "\x00" in text:
        raise ValueError("unsafe_instruction")
    if _SECRET_VALUE.search(text):
        raise ValueError("secret_material")
    return text


def _json_document(raw: bytes, code: str) -> Any:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(code)
            result[key] = value
        return result

    def nonfinite(_value):
        raise ValueError(code)

    try:
        value = json.loads(raw, object_pairs_hook=unique, parse_constant=nonfinite)
    except (ValueError, UnicodeError, RecursionError):
        raise ValueError(code) from None

    def bounded(item, depth=0):
        if depth > 12:
            raise ValueError(code)
        if isinstance(item, dict):
            for child in item.values():
                bounded(child, depth + 1)
        elif isinstance(item, list):
            for child in item:
                bounded(child, depth + 1)

    bounded(value)
    return value


@dataclass
class _Package:
    root: Path
    nodes: dict[str, tuple[int, ...]]
    project_data_modes: bool = False
    id: str = ""
    version: str = ""
    declared_license: str | None = None
    skill_layout: bool = True
    manifests: dict[str, str] = field(default_factory=dict)
    read_hashes: dict[str, str] = field(default_factory=dict)
    contents: dict[str, bytes] = field(default_factory=dict)
    report: dict[str, Any] = field(default_factory=dict)

    def read(self, relative: str) -> bytes:
        raw = _read(self.root / relative, self.nodes[relative], ceiling=MAX_FILE_BYTES)
        self.read_hashes[relative] = hashlib.sha256(raw).hexdigest()
        return raw


def _walk_metadata(root: Path, *, source: bool, total: list[int],
                   instructional_bytes_only: bool = False) -> dict[str, tuple[int, ...]]:
    """Preflight sem abrir arquivos; limites incluem arquivos excluídos."""
    nodes: dict[str, tuple[int, ...]] = {}
    file_count = 0
    # O destino pode conservar pacotes legados maiores que o teto novo.
    node_limit = MAX_FILES_PER_PACKAGE * 4 if source else 250_000

    def walk(path: Path, depth: int):
        nonlocal file_count
        if depth > _MAX_DEPTH or len(nodes) >= node_limit:
            raise ValueError("limit_exceeded")
        relative = path.relative_to(root).as_posix()
        if relative != ".":
            _safe_relative(relative)
        if _sensitive(path.name):
            raise ValueError("sensitive_file")
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            raise ValueError("unsafe_path")
        if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
            raise ValueError("unsafe_path")
        if stat.S_ISREG(info.st_mode):
            if info.st_nlink != 1:
                raise ValueError("unsafe_path")
            file_count += 1
            measured = (not instructional_bytes_only or relative in _MANIFESTS
                        or _instruction_path(relative))
            if measured:
                total[0] += info.st_size
            if source and (file_count > MAX_FILES_PER_PACKAGE or
                           measured and (info.st_size > MAX_FILE_BYTES or total[0] > MAX_TOTAL_BYTES)):
                raise ValueError("limit_exceeded")
        nodes[relative] = _fingerprint(info)
        if stat.S_ISDIR(info.st_mode):
            # Limite durante a enumeração também: não materializar glob sem teto.
            children = []
            for child in path.iterdir():
                if len(children) + len(nodes) >= node_limit:
                    raise ValueError("limit_exceeded")
                children.append(child)
            for child in sorted(children):
                walk(child, depth + 1)

    walk(root, 0)
    return nodes


def _scan(cache: Path) -> list[_Package]:
    total = [0]
    packages = []
    enumerated = 0
    for namespace in _NAMESPACES:
        folder = cache / namespace
        if not folder.exists() and not folder.is_symlink():
            continue
        if not stat.S_ISDIR(folder.lstat().st_mode):
            raise ValueError("unsafe_path")
        for plugin_dir in folder.iterdir():
            enumerated += 1
            if enumerated > MAX_PACKAGES * 4:
                raise ValueError("limit_exceeded")
            if _sensitive(plugin_dir.name):
                raise ValueError("sensitive_file")
            if not _COMPONENT.fullmatch(plugin_dir.name):
                raise ValueError("unsafe_path")
            if not stat.S_ISDIR(plugin_dir.lstat().st_mode):
                raise ValueError("unsafe_path")
            for version_dir in plugin_dir.iterdir():
                enumerated += 1
                if len(packages) >= MAX_PACKAGES or enumerated > MAX_PACKAGES * 4:
                    raise ValueError("limit_exceeded")
                if (not _COMPONENT.fullmatch(version_dir.name)
                        or not stat.S_ISDIR(version_dir.lstat().st_mode)):
                    raise ValueError("unsafe_path")
                nodes = _walk_metadata(version_dir, source=True, total=total)
                packages.append(_Package(version_dir, nodes))
    return sorted(packages, key=lambda item: str(item.root))


def _drvfs_synthetic_modes(root: Path) -> bool:
    """Comprova o mount mais específico, não um prefixo de caminho WSL.

    Montagens empatadas/ocultas, dispositivo discordante, metadata e qualquer
    falha de leitura/parsing mantêm a política POSIX. Nenhum override público.
    """
    try:
        root = _absolute(root)
        device = root.lstat().st_dev
        with Path("/proc/self/mountinfo").open("rb") as stream:
            raw = stream.read(4 * 1024 * 1024 + 1)
        if len(raw) > 4 * 1024 * 1024:
            return False

        def unescape(value):
            # Escapes definidos pelo formato mountinfo, sem interpretar escapes
            # de shell/Python ou aceitar um caminho com escape desconhecido.
            escapes = {"040": " ", "011": "\t", "012": "\n", "134": "\\"}
            if re.search(r"\\(?!040|011|012|134)", value):
                raise ValueError("invalid_mountinfo")
            return re.sub(r"\\(040|011|012|134)", lambda m: escapes[m[1]], value)

        matches = []
        for line in raw.decode("utf-8").splitlines():
            fields = line.split()
            separator = fields.index("-")
            if separator < 6 or len(fields) != separator + 4:
                return False
            mountpoint = Path(unescape(fields[4]))
            if not mountpoint.is_absolute() or ".." in mountpoint.parts:
                return False
            if root != mountpoint and not root.is_relative_to(mountpoint):
                continue
            major, minor = map(int, fields[2].split(":"))
            # Opções não são mountpoints: caminhos Windows podem ter barras
            # literais (path=C:\...), sem escapes octais de mountinfo.
            options = re.split(r"[,;]", fields[5] + "," + fields[separator + 3])
            matches.append((len(mountpoint.parts), (major, minor), fields[separator + 1], options))
        if not matches:
            return False
        depth = max(item[0] for item in matches)
        effective = [item for item in matches if item[0] == depth]
        if len(effective) != 1:
            return False
        _, mount_device, filesystem, options = effective[0]
        return (mount_device == (os.major(device), os.minor(device))
                and filesystem == "9p" and "aname=drvfs" in options
                and not any(option.split("=", 1)[0] == "metadata" for option in options))
    except (OSError, ValueError, UnicodeError, AttributeError, IndexError):
        return False


def _scan_selected(cache: Path, ids: tuple[str, ...]) -> list[_Package]:
    """Somente raízes do catálogo; nem enumerar namespaces/pacotes irmãos."""
    from integrations.scientific_plugins import PLUGINS

    _selection(list(ids), PLUGINS)
    total = [0]
    packages = []
    for pid in ids:
        _, origin, version = PLUGINS[pid]
        relative = PurePosixPath(_safe_relative(origin))
        if (len(relative.parts) != 2 or relative.parts[0] not in _NAMESPACES
                or not _COMPONENT.fullmatch(version)):
            raise ValueError("source_mismatch")
        root = cache.joinpath(*relative.parts, version)
        _existing_chain(root)
        if not root.exists():
            raise ValueError("unknown_plugin")
        if not stat.S_ISDIR(root.lstat().st_mode):
            raise ValueError("unsafe_path")
        nodes = _walk_metadata(root, source=True, total=total, instructional_bytes_only=True)
        packages.append(_Package(root, nodes, project_data_modes=_drvfs_synthetic_modes(root)))
    return packages


def _scan_scope(cache: Path, selected_ids: tuple[str, ...] | None) -> list[_Package]:
    return _scan(cache) if selected_ids is None else _scan_selected(cache, selected_ids)


def _data_mode_eligible(package: _Package, relative: str, info: tuple[int, ...]) -> bool:
    if not stat.S_ISREG(info[2]):
        return False
    if not info[2] & 0o111:
        return True
    return package.project_data_modes and (relative in _MANIFESTS or _instruction_path(relative))


def _identities(packages: list[_Package], catalog: dict) -> None:
    seen = set()
    for package in packages:
        projections = []
        for relative in _MANIFESTS:
            info = package.nodes.get(relative)
            if info is None:
                continue
            if not stat.S_ISREG(info[2]):
                raise ValueError("unsafe_path")
            if not _data_mode_eligible(package, relative, info):
                continue
            raw = package.read(relative)
            _text(raw)
            meta = _json_document(raw, "duplicate_manifest")
            if not isinstance(meta, dict):
                raise ValueError("invalid_manifest")
            pid, version = meta.get("name"), meta.get("version")
            if not isinstance(pid, str) or not _ID.fullmatch(pid):
                raise ValueError("unsafe_path")
            if not isinstance(version, str) or not _COMPONENT.fullmatch(version):
                raise ValueError("unsafe_path")
            skills = meta.get("skills", "./skills")
            layout = isinstance(skills, str)
            if layout:
                # Campo de diretório dos manifests publicados usa ./skills/.
                # Não normalizar traversal ou caminhos de arquivos em geral.
                pointer = skills[:-1] if skills.endswith('/') else skills
                layout = _safe_relative(pointer, dot_prefix=True) == "skills"
            license_id = meta.get("license")
            if license_id is not None and (not isinstance(license_id, str) or len(license_id) > 200):
                raise ValueError("invalid_manifest")
            projections.append((pid, version, license_id, layout))
            package.manifests[relative] = hashlib.sha256(raw).hexdigest()
        if projections:
            if any(item != projections[0] for item in projections):
                raise ValueError("duplicate_manifest")
            package.id, package.version, package.declared_license, package.skill_layout = projections[0]
        else:
            # Ausência de manifesto nunca habilita cópia; apenas referência local.
            relative_origin = "/".join(package.root.parts[-3:-1])
            package.id = next((pid for pid, (_, origin, _) in catalog.items()
                               if origin == relative_origin), package.root.parent.name)
            package.version = package.root.name
        if package.id in seen:
            raise ValueError("duplicate_plugin_id")
        seen.add(package.id)
    # Primeiro detectar duplicidade; jamais escolher pela ordem/versão mais alta.
    for package in packages:
        if package.id in catalog:
            _, origin, version = catalog[package.id]
            if ("/".join(package.root.parts[-3:-1]) != origin
                    or package.root.name != version or package.version != version):
                raise ValueError("source_mismatch")


def _license_file(name: str) -> bool:
    lowered = name.lower()
    return (lowered.startswith(("license", "licence"))
            and Path(name).suffix.lower() in {"", ".txt", ".md", ".rst", ".0"})


def _license_text(text: str) -> tuple[str | None, str | None]:
    normalized = " ".join(text.lower().split())
    if _RESTRICTED_TEXT.search(normalized):
        return None, "license_restricted"
    matches = []
    if all(marker in normalized for marker in (
        "permission is hereby granted, free of charge", "to deal in the software without restriction",
        "the above copyright notice", 'software is provided "as is"',
        "without warranty of any kind", "in no event",
    )):
        matches.append("MIT")
    if all(marker in normalized for marker in (
        "apache license", "version 2.0, january 2004", "grant of copyright license",
        "grant of patent license", "redistribution", "royalty-free", "disclaimer of warranty",
        "limitation of liability", "end of terms and conditions",
    )):
        matches.append("Apache-2.0")
    if all(marker in normalized for marker in (
        "redistribution and use in source and binary forms", "redistributions of source code",
        "redistributions in binary form", "this list of conditions", 'contributors "as is"',
        "implied warranties of merchantability", "in no event",
    )):
        matches.append("BSD-3-Clause" if "neither the name" in normalized else "BSD-2-Clause")
    if len(matches) == 1:
        return matches[0], None
    return None, "license_conflict" if matches else "license_text_unverified"


def _instruction_path(relative: str) -> bool:
    path = PurePosixPath(relative)
    parts = path.parts
    if any(part.lower() in _EXCLUDED_PARTS for part in parts):
        return False
    if _license_file(path.name) or path.name.lower().startswith("notice"):
        # Não interpretar código com nome NOTICE.py como texto de licença.
        return path.suffix.lower() in {"", ".txt", ".md", ".rst", ".0"}
    if relative == "README.md":
        return True
    if parts[0] == "docs" and len(parts) >= 2:
        return path.suffix.lower() in _TEXT_SUFFIXES
    if len(parts) < 3 or parts[0] != "skills" or not _ID.fullmatch(parts[1]):
        return False
    return (len(parts) == 3 and parts[2] == "SKILL.md"
            or parts[2] == "references" and len(parts) >= 4 and path.suffix.lower() in _TEXT_SUFFIXES
             or len(parts) == 4 and parts[2:] == ("agents", "openai.yaml"))


def _yaml_document(text: str) -> Any:
    """YAML seguro não pode fazer last-key-wins em licença/permissões."""
    import yaml

    class UniqueLoader(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            if not isinstance(node, yaml.MappingNode):
                raise ValueError("unsafe_instruction")
            result = {}
            for key_node, value_node in node.value:
                if key_node.tag == 'tag:yaml.org,2002:merge':
                    raise ValueError("unsafe_instruction")
                key = self.construct_object(key_node, deep=deep)
                if not isinstance(key, str) or key in result:
                    raise ValueError("unsafe_instruction")
                result[key] = self.construct_object(value_node, deep=deep)
            return result

    try:
        return yaml.load(text, Loader=UniqueLoader)
    except (yaml.YAMLError, RecursionError):
        raise ValueError("unsafe_instruction") from None


def _skill_text(package: _Package, relative: str) -> tuple[bytes | None, str | None]:
    """Inspecionar frontmatter antes do corpo; licença restritiva não é carregada."""
    info = package.nodes[relative]
    with _regular_stream(package.root / relative) as stream:
        if _fingerprint(os.fstat(stream.fileno())) != info:
            raise ValueError("source_changed")
        prefix = stream.readline(min(MAX_FILE_BYTES, 16_384) + 1)
        if prefix.decode("utf-8-sig", errors="replace").rstrip("\r\n") == "---":
            while True:
                line = stream.readline(min(MAX_FILE_BYTES, 16_384) + 1)
                prefix += line
                if len(prefix) > min(MAX_FILE_BYTES, 16_384) or not line:
                    raise ValueError("unsafe_instruction")
                if line.rstrip(b"\r\n") == b"---":
                    break
            # Só linhas delimitadoras completas são removidas. Duplicatas e
            # merge keys também são recusadas antes de ler o corpo da skill.
            header = "".join(_text(prefix).splitlines(keepends=True)[1:-1])
            front = _yaml_document(header) or {}
            if not isinstance(front, dict):
                raise ValueError("unsafe_instruction")
            declared = front.get("license")
            if declared is not None:
                if not isinstance(declared, str) or declared not in _PERMISSIVE:
                    return None, "license_restricted"
                if package.declared_license and declared != package.declared_license:
                    return None, "license_conflict"
        raw = prefix + stream.read(MAX_FILE_BYTES + 1)
        if (len(raw) != info[3] or len(raw) > MAX_FILE_BYTES
                or _fingerprint(os.fstat(stream.fileno())) != info):
            raise ValueError("source_changed")
    _text(raw)
    package.read_hashes[relative] = hashlib.sha256(raw).hexdigest()
    return raw, None


def _analyze(package: _Package, catalog: dict) -> dict[str, Any]:
    reasons: set[str] = set()
    evidence = []
    root = package.root
    first_manifest = next(iter(package.manifests), "")
    report = {
        "id": package.id, "namespace": root.parts[-3], "version": package.version,
        "source_root": str(root), "manifest_path": first_manifest,
        "manifest_sha256": package.manifests.get(first_manifest, ""),
        "disposition": "reference_only", "reason_codes": [], "files": {},
        "license_evidence": evidence,
        "permission_projection": ("drvfs_synthetic_bits_data_only" if package.project_data_modes
                                  else "posix_mode_bits"),
    }
    package.report = report
    if package.id not in catalog:
        reasons.add("not_catalogued")
    if not first_manifest:
        reasons.add("manifest_missing_or_executable")
    if not package.skill_layout:
        reasons.add("unsupported_skill_layout")
    skills = {PurePosixPath(p).parts[1] for p, info in package.nodes.items()
              if len(PurePosixPath(p).parts) == 3 and p.startswith("skills/")
              and p.endswith("/SKILL.md") and stat.S_ISREG(info[2])
              and _data_mode_eligible(package, p, info) and _ID.fullmatch(PurePosixPath(p).parts[1])}
    if not skills:
        reasons.add("no_local_skills")
    if reasons:
        report["reason_codes"] = sorted(reasons)
        return report

    # Herança fail-closed: filho não revoga bloqueio de ancestral.
    allowed_dirs: dict[str, bool] = {}
    declared = package.declared_license
    directories = sorted((p for p, info in package.nodes.items() if stat.S_ISDIR(info[2])),
                         key=lambda p: (len(PurePosixPath(p).parts), p))
    for directory in directories:
        parts = PurePosixPath(directory).parts
        parent = PurePosixPath(directory).parent.as_posix()
        inherited = True if directory == "." else allowed_dirs.get(parent, False)
        known_private = (package.id == "anthropic-skills" and len(parts) >= 2
                         and parts[0] == "skills" and parts[1].lower() in _DOCUMENT_SKILLS)
        if known_private:
            reasons.add("license_restricted")
        if not inherited or known_private:
            allowed_dirs[directory] = False
            continue
        licenses = [(p, info) for p, info in package.nodes.items()
                    if stat.S_ISREG(info[2]) and PurePosixPath(p).parent.as_posix() == directory
                    and _license_file(PurePosixPath(p).name)]
        recognized = []
        failure = None
        for relative, info in sorted(licenses):
            if not _data_mode_eligible(package, relative, info):
                failure = "license_text_unverified"
                continue
            raw = package.read(relative)
            spdx, reason = _license_text(_text(raw))
            if spdx:
                evidence.append({"path": relative, "spdx": spdx,
                                 "sha256": hashlib.sha256(raw).hexdigest()})
                recognized.append(spdx)
            else:
                failure = reason
        if directory == ".":
            if not licenses:
                failure = "license_missing"
            if declared is not None and declared not in _PERMISSIVE:
                failure = "license_restricted"
        if recognized and (len(set(recognized)) != 1
                           or declared is not None and any(item != declared for item in recognized)):
            failure = "license_conflict"
        if failure:
            reasons.add(failure)
        allowed_dirs[directory] = failure is None and (bool(recognized) or directory != ".")

    # Ler SKILL antes das referências: frontmatter proprietário bloqueia o ramo.
    for skill in sorted(skills):
        relative = f"skills/{skill}/SKILL.md"
        if not allowed_dirs.get(f"skills/{skill}", False):
            continue
        raw, reason = _skill_text(package, relative)
        if reason:
            reasons.add(reason)
            prefix = f"skills/{skill}"
            for directory in allowed_dirs:
                if directory == prefix or directory.startswith(prefix + "/"):
                    allowed_dirs[directory] = False
        else:
            package.contents[relative] = raw

    for relative, info in sorted(package.nodes.items()):
        if (not _data_mode_eligible(package, relative, info) or not _instruction_path(relative)
                or not allowed_dirs.get(PurePosixPath(relative).parent.as_posix(), False)):
            continue
        # Não carregar referências/política de skill sem corpo instrucional aprovado.
        parts = PurePosixPath(relative).parts
        if (len(parts) >= 2 and parts[0] == "skills"
                and f"skills/{parts[1]}/SKILL.md" not in package.contents):
            continue
        if relative not in package.contents:
            raw = package.read(relative)
            text = _text(raw)
            if parts[-2:] == ("agents", "openai.yaml"):
                _check_policy(text)
            package.contents[relative] = raw
    installed_skills = [p for p in package.contents if p.endswith("/SKILL.md")]
    if installed_skills:
        report["disposition"] = "eligible"
        report["files"] = {p: hashlib.sha256(raw).hexdigest()
                           for p, raw in sorted(package.contents.items())}
    else:
        package.contents.clear()
        if not reasons:
            reasons.add("no_local_skills")
    report["reason_codes"] = sorted(reasons)
    return report


def _check_policy(text: str) -> None:
    policy = _yaml_document(text)
    if not isinstance(policy, dict) or set(policy) - {"policy", "interface"}:
        raise ValueError("unsafe_instruction")
    invocation = policy.get("policy", {})
    if (not isinstance(invocation, dict) or set(invocation) - {"allow_implicit_invocation"}
            or "allow_implicit_invocation" in invocation
            and type(invocation["allow_implicit_invocation"]) is not bool):
        raise ValueError("unsafe_instruction")
    interface = policy.get("interface", {})
    if not isinstance(interface, dict) or any(not isinstance(v, str) for v in interface.values()):
        raise ValueError("unsafe_instruction")


def inventory_local_plugins(cache_root: str | Path) -> dict[str, Any]:
    """Relatório de evidência, nunca uma autorização/registry de execução."""
    from integrations.scientific_plugins import PLUGINS

    cache = _cache_path(cache_root)
    packages = _scan(cache)
    _identities(packages, PLUGINS)
    reports = [_analyze(package, PLUGINS) for package in packages]
    _revalidate(cache, packages)
    return {
        "schema_version": 1, "kind": "local_plugin_evidence", "authoritative": False,
        "cache_root": str(cache), "plugins": sorted(reports, key=lambda p: (
            p["id"], p["source_root"], p["version"])), "limits": _limits(), **_no_execution(),
    }


def inventory_selected_plugins(cache_root: str | Path, plugin_ids: list[str]) -> dict[str, Any]:
    """R922: evidência restrita aos IDs canônicos, sem inspecionar seus irmãos."""
    from integrations.scientific_plugins import PLUGINS

    ids = tuple(_selection(plugin_ids, PLUGINS))
    cache = _cache_path(cache_root)
    packages = _scan_selected(cache, ids)
    _identities(packages, PLUGINS)
    if {package.id for package in packages} != set(ids):
        raise ValueError("source_mismatch")
    reports = [_analyze(package, PLUGINS) for package in packages]
    _revalidate(cache, packages, selected_ids=ids)
    return {
        "status": "catalogued", "schema_version": 1, "kind": "local_plugin_evidence",
        "authoritative": False, "cache_root": str(cache), "scope": "explicit_catalogued_packages",
        "plugin_ids": list(ids), "plugins": sorted(reports, key=lambda p: p["id"]),
        "limits": _limits(), **_no_execution(),
    }


def extract_local_plugins(
    cache_root: str | Path, destination_root: str | Path, plugin_ids: list[str],
) -> dict[str, Any]:
    """Usa o serviço canônico; destination_root é raiz de repositório, não cache."""
    from integrations.scientific_plugins import ScientificPluginService

    # O construtor histórico resolve a raiz: detectar links antes de instanciá-lo.
    root = _destination_path(destination_root)
    return ScientificPluginService(root).extract_eligible(cache_root=cache_root, plugin_ids=plugin_ids)


def _revalidate(
    cache: Path, packages: list[_Package], *, selected_ids: tuple[str, ...] | None = None,
) -> None:
    try:
        fresh = _scan_scope(_cache_path(cache), selected_ids)
        if ({str(p.root): (p.nodes, p.project_data_modes) for p in fresh}
                != {str(p.root): (p.nodes, p.project_data_modes) for p in packages}):
            raise ValueError("source_changed")
        # Metadados/licenças são comparados antes de reabrir qualquer corpo.
        for package in packages:
            for relative, expected in package.read_hashes.items():
                raw = _read(package.root / relative, package.nodes[relative], ceiling=MAX_FILE_BYTES)
                if hashlib.sha256(raw).hexdigest() != expected:
                    raise ValueError("source_changed")
    except (ValueError, OSError):
        raise ValueError("source_changed") from None


def _selection(plugin_ids: Any, catalog: dict) -> list[str]:
    if (not isinstance(plugin_ids, list) or not plugin_ids
            or any(not isinstance(pid, str) for pid in plugin_ids)):
        raise ValueError("invalid_selection")
    if any(not _ID.fullmatch(pid) for pid in plugin_ids):
        raise ValueError("unsafe_path")
    if len(set(plugin_ids)) != len(plugin_ids):
        raise ValueError("invalid_selection")
    if len(plugin_ids) > MAX_PACKAGES:
        raise ValueError("limit_exceeded")
    if any(pid not in catalog for pid in plugin_ids):
        raise ValueError("unknown_plugin")
    return list(plugin_ids)


def _destination_structure(root: Path, storage: Path, *, scan_retained: bool = True) -> None:
    _existing_chain(storage)
    if storage.exists():
        if not storage.is_dir():
            raise ValueError("unsafe_path")
        if scan_retained:
            _walk_metadata(storage, source=False, total=[0])
    if not storage.is_relative_to(root):
        raise ValueError("unsafe_path")


def _registry(service: Any) -> tuple[dict, bytes | None]:
    from integrations.scientific_plugins import PLUGINS, _manifest_json

    path = service.storage / "registry.json"
    if not path.exists():
        return {}, None
    try:
        info = _fingerprint(path.lstat())
        raw = _read(path, info, ceiling=_REGISTRY_LIMIT)
        registry = _json_document(raw, "invalid_registry")
        _manifest_json(registry)
        for pid, entry in registry.items():
            version = entry["version"]
            # Versão histórica íntegra não autoriza uso da atual, mas também
            # não deve impedir importar outro plugin. status() já a sinaliza
            # version_mismatch; preservar seus bytes/metadados sem migrar.
            if not _COMPONENT.fullmatch(version):
                raise ValueError("invalid_registry")
            expected = service.storage / "packages" / pid / version
            if entry["package_root"] != str(expected):
                raise ValueError("invalid_registry")
            # Origem retida é metadado; nunca abrir o cache histórico dela.
            if not Path(entry["source_root"]).is_absolute():
                raise ValueError("invalid_registry")
        return registry, raw
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError):
        raise ValueError("invalid_registry") from None


def _target_matches(target: Path, files: dict[str, str]) -> None:
    if not target.is_dir() or target.is_symlink():
        raise ValueError("destination_conflict")
    nodes = _walk_metadata(target, source=False, total=[0])
    actual = {p for p, info in nodes.items() if stat.S_ISREG(info[2])}
    if actual != set(files):
        raise ValueError("destination_conflict")
    if any(stat.S_IMODE(nodes[p][2]) not in {0o600, 0o644} for p in actual):
        raise ValueError("destination_conflict")
    # Licenças primeiro: uma licença adulterada não autoriza ler os corpos.
    for relative in sorted(files, key=lambda p: (not _license_file(PurePosixPath(p).name), p)):
        raw = _read(target / relative, nodes[relative], ceiling=MAX_FILE_BYTES)
        if hashlib.sha256(raw).hexdigest() != files[relative]:
            raise ValueError("destination_conflict")


def _mkdir(path: Path, created: list[Path]) -> None:
    if path.exists() or path.is_symlink():
        _existing_chain(path)
        if not path.is_dir():
            raise ValueError("unsafe_path")
        return
    _mkdir(path.parent, created)
    path.mkdir()
    created.append(path)


def _extract_eligible(
    service: Any, *, cache_root: str | Path, plugin_ids: list[str], selected_scope: bool = False,
) -> dict[str, Any]:
    """Worker privado do ScientificPluginService; não chama sync nem runtimes."""
    from integrations.scientific_plugins import PLUGINS, _manifest_json

    ids = _selection(plugin_ids, PLUGINS)
    scope_ids = tuple(ids) if selected_scope else None
    cache = _cache_path(cache_root)
    root = _destination_path(service._lexical_root)
    if root != service.root:
        raise ValueError("unsafe_path")
    if cache.is_relative_to(root) or root.is_relative_to(cache):
        raise ValueError("source_destination_overlap")
    storage = root / ".opencode/scientific-plugins"
    if Path(service.storage) != storage:
        raise ValueError("unsafe_path")
    _destination_structure(root, storage, scan_retained=not selected_scope)
    packages = _scan_scope(cache, scope_ids)
    _identities(packages, PLUGINS)
    by_id = {package.id: package for package in packages}
    if any(pid not in by_id for pid in ids):
        raise ValueError("unknown_plugin")
    selected = [by_id[pid] for pid in ids]
    for package in selected:
        _analyze(package, PLUGINS)
    eligible = [p for p in selected if p.report["disposition"] == "eligible"]
    result = {
        "status": "completed", "plugins": [],
        "reference_only": [p.report for p in selected if p not in eligible],
        "evidence": [p.report for p in selected], "limits": _limits(), **_no_execution(),
    }
    if selected_scope:
        result.update(scope="explicit_catalogued_packages", plugin_ids=ids)
    if not eligible:
        _revalidate(cache, packages, selected_ids=scope_ids)
        return result

    registry, original_registry = _registry(service)
    updated = dict(registry)
    prepared = []
    for package in eligible:
        target = storage / "packages" / package.id / package.version
        _existing_chain(target)
        files = package.report["files"]
        entry = {
            "id": package.id, "name": PLUGINS[package.id][0], "version": package.version,
            "source_root": str(package.root), "package_root": str(target), "files": files,
            "skills": sorted(PurePosixPath(p).parts[1] for p in files
                             if len(PurePosixPath(p).parts) == 3 and p.endswith("/SKILL.md")),
            "origin": "third_party_or_user",
        }
        exists = target.exists()
        if exists:
            _target_matches(target, files)
        if package.id in registry and (not exists or registry[package.id]["files"] != files):
            raise ValueError("destination_conflict")
        updated[package.id] = entry
        result["plugins"].append(entry)
        prepared.append((package, target, exists))
    _manifest_json(updated)
    _revalidate(cache, packages, selected_ids=scope_ids)
    if updated == registry and all(exists for _, _, exists in prepared):
        return result

    created: list[Path] = []
    stages: list[Path] = []
    published: list[tuple[Path, int]] = []
    committed = False
    try:
        staged = []
        for package, target, exists in prepared:
            if exists:
                continue
            _mkdir(target.parent, created)
            stage = Path(tempfile.mkdtemp(dir=target.parent, prefix=".extract-"))
            stages.append(stage)
            for relative, raw in sorted(package.contents.items()):
                output = stage / relative
                output.parent.mkdir(parents=True, exist_ok=True)
                descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                with os.fdopen(descriptor, "wb") as stream:
                    os.fchmod(stream.fileno(), 0o600)
                    stream.write(raw)
                    stream.flush()
                    os.fsync(stream.fileno())
            _target_matches(stage, package.report["files"])
            staged.append((stage, target))
        _revalidate(cache, packages, selected_ids=scope_ids)
        for stage, target in staged:
            if target.exists() or target.is_symlink():
                raise ValueError("destination_conflict")
            # O inode permite remover só diretórios promovidos por esta operação.
            published.append((target, stage.lstat().st_ino))
            os.rename(stage, target)
        _destination_structure(root, storage, scan_retained=not selected_scope)
        for package, target, _ in prepared:
            _target_matches(target, package.report["files"])
        _revalidate(cache, packages, selected_ids=scope_ids)
        _, current_registry = _registry(service)
        if current_registry != original_registry:
            raise ValueError("invalid_registry")
        service._write(storage / "registry.json", updated, manifest=True)
        committed = True
        return result
    finally:
        if not committed:
            for target, inode in reversed(published):
                if target.exists() and not target.is_symlink() and target.lstat().st_ino == inode:
                    shutil.rmtree(target)
        for stage in reversed(stages):
            if stage.exists():
                shutil.rmtree(stage)
        if not committed:
            for directory in reversed(created):
                try:
                    directory.rmdir()
                except FileNotFoundError:
                    pass
                except OSError:
                    # Nunca remover trabalho externo/retido só para limpar pais.
                    if directory.exists() and not any(directory.iterdir()):
                        raise
