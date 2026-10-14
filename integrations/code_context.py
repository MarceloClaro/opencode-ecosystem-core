"""R887: context-link subordinado ao Core, com corpus privado e MCP confinado.

Somente setup usa rede. Indexação explícita; consultas não instalam nem atualizam.
O grafo é estático e seus resultados são dados de contexto, não evidência de execução.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import re
import shutil
import signal
import sqlite3
import subprocess
import tarfile
import tempfile
import time
import urllib.request
import uuid
from collections import Counter
from pathlib import Path, PurePosixPath

VERSION = "1.1.0"
SOURCE_COMMIT = "e5af49c11c5b2228c6b611dd3594d93014997306"
ARCHIVE_SHA256 = "cb61fe2618d1aa27724520c5c9205440d57802fc4e1bee9a0690c2c652927b1a"
ARCHIVE_BYTES = 20_852_723
ASSET_URL = f"https://github.com/context-link-mcp/context-link/releases/download/v{VERSION}/context-link_{VERSION}_linux_amd64.tar.gz"
TOOLS = ("ping", "semantic_search_symbols", "get_code_by_symbol", "get_file_skeleton", "get_symbol_usages", "get_call_tree", "get_blast_radius")
BLOCKED_TOOLS = ("get_symbol_usages", "get_call_tree", "get_blast_radius")
VALIDATED_TOOLS = tuple(tool for tool in TOOLS if tool not in BLOCKED_TOOLS)
SUFFIXES = {".py", ".js", ".mjs", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".c", ".h", ".cpp", ".hpp", ".cs", ".kt", ".swift"}
EXCLUDED = {"tests", "test", "docs", "examples", "templates", "template", "vendor", "node_modules", "third_party", "third-party", "archive", "archives", "archived", "history", "snapshots", "outputs", "artigos", "livro-core", "benchmarks", "fixtures", "generated", "dist", "build"}
MAX_FILE_BYTES = 512 * 1024
MAX_CORPUS_BYTES = 32 * 1024 * 1024
MAX_FILES = 2000
MAX_RESPONSE_BYTES = 64 * 1024
_SQLITE_COLUMNS = {
    "files": {"id": "INTEGER", "repo_name": "TEXT", "path": "TEXT", "content_hash": "TEXT", "last_indexed": "TIMESTAMP", "size_bytes": "INTEGER"},
    "symbols": {"id": "INTEGER", "repo_name": "TEXT", "name": "TEXT", "qualified_name": "TEXT", "kind": "TEXT", "file_path": "TEXT", "content_hash": "TEXT", "code_block": "TEXT", "start_line": "INTEGER", "end_line": "INTEGER", "language": "TEXT", "indexed_at": "TIMESTAMP"},
    "vec_symbols": {"symbol_id": "INTEGER", "repo_name": "TEXT", "embedding": "BLOB"},
    "fts_symbols": {key: "" for key in ("symbol_id", "repo_name", "name", "qualified_name", "kind", "signature", "extra_keywords")},
    "memories": {"id": "INTEGER", "symbol_id": "INTEGER", "note": "TEXT", "author": "TEXT", "is_stale": "BOOLEAN", "stale_reason": "TEXT", "last_known_symbol": "TEXT", "last_known_file": "TEXT", "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP"},
    "vec_meta": {"key": "TEXT", "value": "TEXT"},
}


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _no_symlinks(path: Path) -> None:
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("symlink recusado no caminho")


def _write_json(path: Path, value: dict) -> None:
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


class CodeContextProvider:
    """Adaptador local síncrono; o primário controla orçamento e invocação."""

    def __init__(self, repo_root=None, state_root=None):
        root = Path(repo_root or Path(__file__).resolve().parents[1]).absolute()
        state = Path(state_root or root / ".mci_state" / "code_context").absolute()
        _no_symlinks(root)
        _no_symlinks(state)
        if state == root or root.is_relative_to(state):
            raise ValueError("estado deve ser diretório privado próprio")
        self.repo_root = root.resolve()
        self.state_root = state.resolve()
        self.tool_root = self.state_root / "tool" / VERSION

    def run(self, config: dict) -> dict:
        base = {"provider": "context-link", "version": VERSION, "source_commit": SOURCE_COMMIT,
                "calibrated": False, "confidence_promoted": False, "source_read_only": True,
                "validated_tools": list(VALIDATED_TOOLS), "blocked_tools": list(BLOCKED_TOOLS),
                "limitations": ["Grafo estático; não comprova execução nem ausência de comportamento dinâmico.",
                                "Filtro de segredos é heurístico; não constitui auditoria DLP.",
                                "Índice/cache privado pode receber escrita; fontes originais não são montadas no provedor."]}
        try:
            self._validate_request(config)
            operation = config.get("operation", "status")
            result = {"status": self._status, "setup": self._setup, "index": self._index, "query": self._query}[operation](config)
            return {**base, **result, "success": bool(result.get("ok"))}
        except (ValueError, TypeError) as exc:
            return {**base, "ok": False, "success": False, "available": False, "index_ready": False, "status": "invalid_request", "error": str(exc)[:400]}
        except (TimeoutError, subprocess.TimeoutExpired) as exc:
            return {**base, "ok": False, "success": False, "available": False, "status": "timeout", "error": str(exc)[:400]}
        except Exception as exc:  # noqa: BLE001 -- Fronteira pública converte falhas do SDK MCP em estado explícito.
            nested = getattr(exc, "exceptions", ())
            if nested:
                pending = list(nested)
                while pending:
                    leaf = pending.pop()
                    if getattr(leaf, "exceptions", ()):
                        pending.extend(leaf.exceptions)
                    elif isinstance(leaf, TimeoutError):
                        return {**base, "ok": False, "success": False, "available": False, "status": "timeout", "error": "deadline MCP excedido"}
            return {**base, "ok": False, "success": False, "available": False, "status": "provider_error", "error": f"{type(exc).__name__}: {exc}"[:500]}

    def _validate_request(self, config):
        if not isinstance(config, dict) or set(config) - {"operation", "tool", "arguments", "timeout_seconds"}:
            raise ValueError("campos de operação inválidos")
        operation = config.get("operation", "status")
        if operation not in {"setup", "index", "status", "query"}:
            raise ValueError("operação inválida")
        timeout = config.get("timeout_seconds", 30)
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 1 <= timeout <= 120:
            raise ValueError("timeout_seconds deve estar entre 1 e 120")
        if operation != "query":
            if set(config) & {"tool", "arguments"}:
                raise ValueError("tool/arguments somente em query")
            return
        tool, args = config.get("tool"), config.get("arguments", {})
        if tool not in TOOLS or not isinstance(args, dict):
            raise ValueError("tool fora da allowlist ou arguments inválido")
        props = {"ping": set(), "semantic_search_symbols": {"query", "top_k", "kind", "file_path_prefix", "min_similarity"},
                 "get_file_skeleton": {"file_path"}, "get_code_by_symbol": {"symbol_name", "depth"},
                 "get_symbol_usages": {"symbol_name"}, "get_call_tree": {"symbol_name", "direction", "depth"},
                 "get_blast_radius": {"symbol_name", "depth"}}[tool]
        required = "query" if tool == "semantic_search_symbols" else "file_path" if tool == "get_file_skeleton" else "symbol_name" if tool != "ping" else None
        if set(args) - props or (required and required not in args):
            raise ValueError("schema da consulta inválido")
        for key, value in args.items():
            if key in {"depth", "top_k", "min_similarity"}:
                lower, upper = (1, 10) if key == "top_k" else (0, 1) if key == "min_similarity" else (1 if tool == "get_blast_radius" else 0, 3)
                if type(value) not in (int, float) or not math.isfinite(value) or not lower <= value <= upper or (key != "min_similarity" and int(value) != value):
                    raise ValueError(f"limite numérico inválido: {key}")
            else:
                if not isinstance(value, str) or not value.strip() or len(value) > 2000 or any(ord(c) < 32 for c in value):
                    raise ValueError(f"texto inválido: {key}")
                if key in {"file_path", "file_path_prefix"}:
                    path = PurePosixPath(value)
                    if path.is_absolute() or ".." in path.parts or "\\" in value or ":" in value or value.startswith("."):
                        raise ValueError("caminho relativo inválido")
                if key == "direction" and value not in {"callers", "callees"}:
                    raise ValueError("direction inválida")

    def _prepare_state(self):
        _no_symlinks(self.state_root)
        self.state_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.state_root.chmod(0o700)

    def _installation(self):
        receipt = self.tool_root / "installation.json"
        binary = self.tool_root / "context-link"
        _no_symlinks(binary)
        if not receipt.is_file() or not binary.is_file():
            return {"installed": False}
        info = json.loads(receipt.read_text())
        valid = info.get("archive_sha256") == ARCHIVE_SHA256 and info.get("binary_sha256") == _digest(binary.read_bytes())
        return {"installed": bool(valid), "binary_sha256": info.get("binary_sha256"), "provenance": info}

    def _setup(self, config):
        if os.uname().sysname != "Linux" or os.uname().machine != "x86_64":
            return {"ok": False, "status": "unsupported_platform", "installed": False, "available": False}
        self._prepare_state()
        if not self._installation()["installed"]:
            self.tool_root.mkdir(parents=True, exist_ok=True, mode=0o700)
            with tempfile.TemporaryDirectory(dir=self.state_root, prefix="download-") as temporary:
                archive = Path(temporary) / "asset.tar.gz"
                request = urllib.request.Request(ASSET_URL, headers={"User-Agent": "OpenCode-Core-R887"})
                with urllib.request.urlopen(request, timeout=config.get("timeout_seconds", 30)) as response, archive.open("wb") as target:
                    total = 0
                    while chunk := response.read(65536):
                        total += len(chunk)
                        if total > ARCHIVE_BYTES:
                            raise ValueError("asset excedeu tamanho fixado")
                        target.write(chunk)
                if total != ARCHIVE_BYTES or _digest(archive.read_bytes()) != ARCHIVE_SHA256:
                    raise ValueError("digest/tamanho do asset não corresponde ao pin")
                extracted = set()
                with tarfile.open(archive, "r:gz") as tar:
                    for member in tar.getmembers():
                        path = PurePosixPath(member.name)
                        if path.is_absolute() or ".." in path.parts or not member.isfile() or member.size > 100 * 1024 * 1024:
                            raise ValueError("membro de arquivo inseguro")
                        if path.name not in {"context-link", "LICENSE", "README.md"}:
                            continue
                        content = tar.extractfile(member)
                        if content is None:
                            raise ValueError("membro ilegível")
                        destination = self.tool_root / path.name
                        destination.write_bytes(content.read())
                        destination.chmod(0o700 if path.name == "context-link" else 0o600)
                        extracted.add(path.name)
                if not {"context-link", "LICENSE"}.issubset(extracted):
                    raise ValueError("binário/licença ausentes no asset")
                _write_json(self.tool_root / "installation.json", {"version": VERSION, "source_commit": SOURCE_COMMIT,
                    "asset_url": ASSET_URL, "archive_sha256": ARCHIVE_SHA256, "archive_bytes": ARCHIVE_BYTES,
                    "binary_sha256": _digest((self.tool_root / "context-link").read_bytes()), "license": "Apache-2.0",
                    "network_used_only_for_setup": True})
        return {"ok": True, "status": "installed", **self._installation(), "index_ready": False, "available": False,
                "network_isolation": self._network_probe()}

    def _git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo_root), *args], timeout=10, stderr=subprocess.DEVNULL)

    def _source_files(self):
        files, excluded, total = {}, Counter(), 0
        for raw in self._git("ls-files", "-z").split(b"\0"):
            if not raw:
                continue
            rel = raw.decode("utf-8", errors="strict")
            path = PurePosixPath(rel)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("caminho Git inválido")
            if any(part.startswith(".") or part.lower() in EXCLUDED for part in path.parts) or path.suffix.lower() not in SUFFIXES or path.name.startswith("test_") or path.stem.lower() in {"secret", "secrets", "credential", "credentials", "settings_local", "settingslocal", "local_settings"}:
                excluded["policy"] += 1
                continue
            source = self.repo_root.joinpath(*path.parts)
            try:
                _no_symlinks(source)
            except ValueError:
                excluded["symlink"] += 1
                continue
            if not source.is_file():
                excluded["missing"] += 1
                continue
            if source.stat().st_size > MAX_FILE_BYTES:
                excluded["oversized"] += 1
                continue
            # No-follow on the final component also closes a common link race.
            fd = os.open(source, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(fd, "rb") as stream:
                data = stream.read(MAX_FILE_BYTES + 1)
            if len(data) > MAX_FILE_BYTES:
                raise ValueError("fonte mudou para tamanho fora do limite")
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                excluded["encoding"] += 1
                continue
            if b"\x00" in data or re.search(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(?:ghp_|sk-proj-)[A-Za-z0-9_-]{20,}|(?i:\b(?:api[_-]?key|access[_-]?token|password|client[_-]?secret)\s*[:=]\s*['\"][A-Za-z0-9_+/=.-]{16,}['\"])", data):
                excluded["secret_marker"] += 1
                continue
            total += len(data)
            if len(files) >= MAX_FILES or total > MAX_CORPUS_BYTES:
                raise ValueError("corpus excedeu orçamento; nenhuma geração parcial será promovida")
            files[rel] = {"sha256": _digest(data), "bytes": len(data), "_data": data}
        return files, dict(excluded), total

    def _export_corpus(self, corpus):
        corpus = Path(corpus)
        _no_symlinks(corpus)
        corpus.mkdir(parents=True, exist_ok=False, mode=0o700)
        sources, excluded, total = self._source_files()
        for rel, info in sources.items():
            destination = corpus / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(info.pop("_data"))
            destination.chmod(0o400)
        return {"head": self._git("rev-parse", "HEAD").decode().strip(), "files": sources,
                "excluded": excluded, "bytes": total, "file_count": len(sources), "scope": "tracked_production_sources"}

    def _manifest_current(self, manifest, corpus=None):
        try:
            files, _, _ = self._source_files()
            for value in files.values():
                value.pop("_data")
            if manifest.get("files") != files:
                return False
            if corpus is not None:
                corpus = Path(corpus)
                _no_symlinks(corpus)
                copied = set()
                for path in corpus.rglob("*"):
                    if path.is_symlink():
                        return False
                    if path.is_file():
                        rel = path.relative_to(corpus).as_posix()
                        if rel not in files or path.stat().st_size != files[rel]["bytes"] or _digest(path.read_bytes()) != files[rel]["sha256"]:
                            return False
                        copied.add(rel)
                if copied != set(files):
                    return False
            return True
        except (OSError, ValueError, subprocess.SubprocessError):
            return False

    @staticmethod
    def _env():
        return {"PATH": "/usr/bin:/bin", "HOME": "/tmp", "TMPDIR": "/tmp", "LANG": "C.UTF-8",
                "GOMAXPROCS": "2", "GOMEMLIMIT": "512MiB", "DO_NOT_TRACK": "1"}

    @staticmethod
    def _sandbox_prefix():
        if not shutil.which("bwrap") or not shutil.which("prlimit"):
            raise RuntimeError("bubblewrap/prlimit indisponível")
        command = ["/usr/bin/prlimit", "--as=4294967296", "--cpu=120", "--fsize=67108864", "--nofile=256", "--",
                   "/usr/bin/bwrap", "--unshare-user", "--unshare-net", "--uid", "0", "--gid", "0", "--die-with-parent", "--new-session"]
        for directory in ("/usr", "/lib", "/lib64"):
            if Path(directory).exists():
                command += ["--ro-bind", directory, directory]
        return command + ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp"]

    def _network_probe(self):
        try:
            command = self._sandbox_prefix() + ["--", "/usr/bin/python3", "-c",
                "import socket; s=socket.socket(); s.settimeout(1); print(s.connect_ex(('1.1.1.1',443)))"]
            out = subprocess.run(command, capture_output=True, text=True, env=self._env(), timeout=4, check=False)
            errno = int(out.stdout.strip()) if out.returncode == 0 else None
            # ENETUNREACH, not an ordinary connection refusal or DNS failure.
            return {"available": out.returncode == 0 and errno == 101, "mechanism": "bubblewrap_user_network_mount_namespace",
                    "probe": "TCP 1.1.1.1:443", "connect_errno": errno, "sources_mounted": False}
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
            return {"available": False, "reason": type(exc).__name__}

    def _command(self, generation, operation):
        work, corpus = generation / "work", generation / "corpus"
        for path in (self.tool_root, work, corpus):
            _no_symlinks(path)
        command = self._sandbox_prefix() + ["--ro-bind", str(self.tool_root), "/tool", "--ro-bind", str(corpus), "/corpus",
            "--bind", str(work), "/state", "--chdir", "/state", "--", "/tool/context-link", operation,
            "--project-root", "/corpus", "--db-path", "/state/index.db", "--config", "/state/config.yaml", "--log-level", "warn"]
        return command + (["--workers", "2"] if operation == "index" else ["--tools", ",".join(TOOLS)])

    def _current(self):
        path = self.state_root / "current.json"
        _no_symlinks(path)
        if not path.is_file():
            return None
        pointer = json.loads(path.read_text())
        name = pointer.get("generation", "")
        if not re.fullmatch(r"[a-f0-9]{32}", name):
            raise ValueError("geração inválida")
        generation = self.state_root / "generations" / name
        _no_symlinks(generation)
        manifest = json.loads((generation / "manifest.json").read_text())
        return generation, manifest

    def _audit_index(self, generation, manifest, log_path):
        """Confere os dados persistidos; code=0/ping não demonstram índice íntegro."""
        expected = manifest["files"]
        audit = {"schema_version": 1, "complete": False, "expected_files": len(expected),
                 "indexed_files": 0, "stats": {}, "log_name": Path(log_path).name}
        try:
            _no_symlinks(Path(log_path))
            text = Path(log_path).read_text(encoding="utf-8", errors="replace").rsplit("Indexing complete:", 1)[-1]
            labels = {"Files discovered": "discovered", "Files indexed": "indexed", "Files unchanged": "unchanged",
                      "Files deleted": "deleted", "Files skipped": "skipped", "Errors": "errors"}
            for label, key in labels.items():
                match = re.search(r"^\s*" + re.escape(label) + r":\s*(\d+)\s*$", text, flags=re.MULTILINE)
                if match:
                    audit["stats"][key] = int(match.group(1))
            db_path = generation / "work" / "index.db"
            _no_symlinks(db_path)
            connection = sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True, timeout=2)
            try:
                for table, required_columns in _SQLITE_COLUMNS.items():
                    columns = connection.execute(f"PRAGMA table_info({table})").fetchall()
                    if {column[1]: column[2].upper() for column in columns} != required_columns:
                        raise ValueError("schema SQLite incompatível com a revisão fixada")
                    if table in {"files", "symbols", "memories"} and not any(column[1] == "id" and column[5] == 1 for column in columns):
                        raise ValueError("chave primária SQLite incompatível")
                    table_sql = connection.execute("SELECT type,sql FROM sqlite_master WHERE name=?", (table,)).fetchone()
                    if not table_sql or table_sql[0] != "table" or (table == "fts_symbols" and "using fts5" not in table_sql[1].lower()):
                        raise ValueError("tipo SQLite incompatível")
                rows = connection.execute("SELECT repo_name,path,content_hash,size_bytes FROM files LIMIT ?", (MAX_FILES + 1,)).fetchall()
                audit["indexed_files"] = len(rows)
                indexed = {path: {"sha256": sha, "bytes": size} for repo, path, sha, size in rows if repo == "corpus"}
                mismatches = [path for path in sorted(set(expected) | set(indexed)) if expected.get(path) != indexed.get(path)]
                audit["missing_or_changed"] = mismatches[:20]
                audit["missing_or_changed_count"] = len(mismatches)
                stats = audit["stats"]
                stats_ok = set(stats) == set(labels.values()) and stats["discovered"] == len(expected) and stats["indexed"] + stats["unchanged"] == len(expected) and not any(stats[k] for k in ("deleted", "skipped", "errors"))
                files_ok = not mismatches and len(rows) == len(expected) and len(indexed) == len(rows)
                if files_ok and stats_ok:
                    counts = {name: connection.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
                              for name in ("symbols", "vec_symbols", "fts_symbols", "memories")}
                    audit["table_counts"] = counts
                    dimensions = connection.execute("SELECT value FROM vec_meta WHERE key='embedding_dim'").fetchall()
                    foreign_symbols = connection.execute("SELECT COUNT(*) FROM symbols s LEFT JOIN files f ON f.repo_name=s.repo_name AND f.path=s.file_path WHERE f.id IS NULL").fetchone()[0]
                    bad_vectors = connection.execute("SELECT COUNT(*) FROM vec_symbols v LEFT JOIN symbols s ON s.id=v.symbol_id AND s.repo_name=v.repo_name WHERE s.id IS NULL OR length(v.embedding)!=512").fetchone()[0]
                    bad_fts = connection.execute("SELECT COUNT(*) FROM fts_symbols f LEFT JOIN symbols s ON s.id=f.symbol_id AND s.repo_name=f.repo_name WHERE s.id IS NULL").fetchone()[0]
                    missing_vectors = connection.execute("SELECT COUNT(*) FROM symbols s LEFT JOIN vec_symbols v ON s.id=v.symbol_id AND s.repo_name=v.repo_name WHERE v.symbol_id IS NULL").fetchone()[0]
                    missing_fts = connection.execute("SELECT COUNT(*) FROM (SELECT id,repo_name FROM symbols EXCEPT SELECT symbol_id,repo_name FROM fts_symbols)").fetchone()[0]
                    audit["invalid_relationships"] = foreign_symbols + bad_vectors + bad_fts + missing_vectors + missing_fts
                    audit["complete"] = counts["symbols"] == counts["vec_symbols"] == counts["fts_symbols"] and counts["memories"] == 0 and dimensions == [("128",)] and audit["invalid_relationships"] == 0
                if not audit["complete"]:
                    audit["reason"] = "Resumo nativo ou arquivos/hashes/embeddings SQLite não correspondem integralmente ao corpus."
            finally:
                connection.close()
        except (OSError, ValueError, sqlite3.Error) as exc:
            audit["reason"] = f"Auditoria local indisponível: {type(exc).__name__}"
        return audit

    def _current_quality(self, generation, manifest):
        audit = manifest.get("index_audit", {})
        name = audit.get("log_name", "")
        if audit.get("schema_version") != 1 or not audit.get("complete") or not re.fullmatch(r"index(?:\.\d+)?\.stderr\.log", name):
            return {"schema_version": 1, "complete": False, "reason": "Geração sem auditoria integral R889; reindexação explícita necessária."}
        return self._audit_index(generation, manifest, generation / "work" / name)

    def _pending_candidate(self, binary_sha256):
        """Retoma somente cópias/arquivos/binário idênticos; nunca promove aqui."""
        pointer_path = self.state_root / "pending.json"
        _no_symlinks(pointer_path)
        if not pointer_path.is_file():
            return None
        pointer = json.loads(pointer_path.read_text())
        name = pointer.get("generation", "")
        if not re.fullmatch(r"[a-f0-9]{32}", name):
            raise ValueError("candidato pendente inválido")
        generation = self.state_root / "generations" / name
        draft = generation / "manifest-draft.json"
        _no_symlinks(draft)
        if not draft.is_file():
            return None
        manifest = json.loads(draft.read_text())
        if manifest.get("binary_sha256") != binary_sha256 or not self._manifest_current(manifest, generation / "corpus"):
            return None
        return generation, manifest

    def _revision_metadata(self, manifest):
        current_head = self._git("rev-parse", "HEAD").decode().strip()
        return {"source_head": manifest["head"], "current_head": current_head,
                "revision_relation": "same_commit" if current_head == manifest["head"] else "unchanged_selected_content"}

    def _status(self, config):
        installation = self._installation()
        current = self._current()
        quality = self._current_quality(*current) if current else None
        ready = bool(current and self._manifest_current(current[1], current[0] / "corpus"))
        isolation = self._network_probe() if installation["installed"] else {"available": False, "reason": "not_installed"}
        ready = bool(ready and installation["installed"] and isolation["available"] and quality and quality["complete"])
        return {"ok": True, "status": "ready" if ready else "not_installed" if not installation["installed"] else "index_failed_partial" if current and quality and not quality["complete"] else "stale" if current else "not_indexed",
                **installation, "index_ready": ready, "available": ready, "network_isolation": isolation,
                "index_audit": quality,
                "revision": self._revision_metadata(current[1]) if ready and current else None,
                "manifest": {k: v for k, v in current[1].items() if k != "files"} if current else None,
                "query_verified": bool(ready and current and current[1].get("mcp_smoke_verified")),
                "query_verification_scope": "ping initialize/tools-list/call; não valida toda semântica de consulta"}

    def _index(self, config):
        if not self._installation()["installed"]:
            return {"ok": False, "status": "not_installed", "index_ready": False, "available": False}
        import fcntl
        self._prepare_state()
        lock_path = self.state_root / "index.lock"
        _no_symlinks(lock_path)
        descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, "a+") as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return {"ok": False, "status": "index_busy", "index_ready": False, "available": False}
            return self._index_locked(config)

    def _index_locked(self, config):
        started = time.monotonic()
        deadline = started + config.get("timeout_seconds", 30)
        def remaining():
            budget = deadline - time.monotonic()
            if budget <= 0:
                raise TimeoutError("orçamento global de indexação excedido")
            return budget
        if not self._installation()["installed"]:
            return {"ok": False, "status": "not_installed", "index_ready": False, "available": False}
        isolation = self._network_probe()
        if not isolation["available"]:
            return {"ok": False, "status": "isolation_unavailable", "index_ready": False, "available": False, "network_isolation": isolation}
        self._prepare_state()
        generations = self.state_root / "generations"
        _no_symlinks(generations)
        generations.mkdir(exist_ok=True, mode=0o700)
        installation = self._installation()
        pending = self._pending_candidate(installation["binary_sha256"])
        if pending:
            generation, manifest = pending
        else:
            generation = generations / uuid.uuid4().hex
            generation.mkdir(mode=0o700)
            manifest = self._export_corpus(generation / "corpus")
            manifest["binary_sha256"] = installation["binary_sha256"]
            _write_json(generation / "manifest-draft.json", manifest)
            _write_json(self.state_root / "pending.json", {"generation": generation.name})
        work = generation / "work"
        _no_symlinks(work)
        work.mkdir(mode=0o700, exist_ok=True)
        (work / "config.yaml").write_text('model_path: ""\nvocab_path: ""\nort_lib_path: ""\nlog_level: warn\n', encoding="utf-8")
        if not manifest["files"]:
            return {"ok": False, "status": "empty_corpus", "index_ready": False, "available": False}
        history_path = generation / "index_attempts.json"
        _no_symlinks(history_path)
        history = json.loads(history_path.read_text()).get("attempts", []) if history_path.is_file() else []
        attempts = []
        previous_logs = [int(path.name.split(".")[1]) for path in work.glob("index.*.stderr.log") if path.name.split(".")[1].isdigit()]
        first_attempt = max(previous_logs, default=0) + 1
        for invocation_attempt in range(1, 7):
            attempt = first_attempt + invocation_attempt - 1
            stderr_path = work / f"index.{attempt}.stderr.log"
            with (work / f"index.{attempt}.stdout.log").open("wb") as stdout, stderr_path.open("wb") as stderr:
                process = subprocess.Popen(self._command(generation, "index"), stdout=stdout, stderr=stderr, env=self._env(), start_new_session=True)
                try:
                    code = process.wait(timeout=remaining())
                except (subprocess.TimeoutExpired, TimeoutError):
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    interrupted = {"attempt": attempt, "exit_code": None, "status": "timeout", "audit": self._audit_index(generation, manifest, stderr_path)}
                    attempts.append(interrupted)
                    _write_json(history_path, {"attempts": history + attempts, "status": "timeout", "active_attempt": attempt})
                    return {"ok": False, "status": "timeout", "index_ready": False, "available": False,
                            "attempts": attempts, "generation": generation.name, "resumable": True}
            audit = self._audit_index(generation, manifest, stderr_path)
            attempts.append({"attempt": attempt, "exit_code": code, "audit": audit})
            _write_json(history_path, {"attempts": history + attempts})
            remaining()
            if code:
                return {"ok": False, "status": "index_failed", "index_ready": False, "available": False,
                        "exit_code": code, "attempts": attempts, "error": stderr_path.read_text(errors="replace")[-1500:]}
            if audit["complete"]:
                break
            # A fresh process avoids reusing the failed upstream parser. Keep the
            # same complete corpus/DB: successful hashes are skipped incrementally.
            if invocation_attempt == 6 or (len(attempts) > 1 and audit["indexed_files"] <= attempts[-2]["audit"]["indexed_files"]):
                return {"ok": False, "status": "index_failed_partial", "index_ready": False, "available": False,
                        "index_audit": audit, "attempts": attempts, "generation": generation.name, "resumable": True}
        smoke = asyncio.run(self._mcp_call(generation, "ping", {}, remaining()))
        ping = smoke.get("result", {}).get("structuredContent", {})
        if smoke.get("isError") or smoke.get("result", {}).get("isError") or ping.get("status") != "ok" or ping.get("version") != VERSION:
            return {"ok": False, "status": "index_smoke_failed", "index_ready": False, "available": False,
                    "reason": "ping MCP não confirmou status/version da release fixada", "smoke": smoke}
        if not self._manifest_current(manifest, generation / "corpus"):
            return {"ok": False, "status": "sources_changed", "index_ready": False, "available": False}
        remaining()
        manifest.update({"index_seconds": round(time.monotonic() - started, 4), "mcp_smoke_verified": True,
                         "binary_sha256": self._installation()["binary_sha256"], "network_isolation": isolation,
                         "tools": smoke["tools"], "generation": generation.name, "index_audit": audit, "index_attempt_count": len(history) + len(attempts)})
        _write_json(generation / "manifest.json", manifest)
        _write_json(self.state_root / "current.json", {"generation": generation.name})
        (self.state_root / "pending.json").unlink(missing_ok=True)
        return {"ok": True, "status": "indexed", "installed": True, "index_ready": True, "available": True,
                "query_verified": True, "manifest": {k: v for k, v in manifest.items() if k != "files"}, "smoke": smoke,
                "attempts": attempts, "resumed": bool(pending), "revision": self._revision_metadata(manifest)}

    @staticmethod
    def _validate_tools(tools):
        names = {tool["name"] for tool in tools}
        if names != set(TOOLS):
            raise ValueError("schema do provedor diverge da allowlist")
        for tool in tools:
            schema = tool.get("inputSchema", {})
            if schema.get("type") != "object":
                raise ValueError("schema MCP não é objeto")
            required = {"semantic_search_symbols": "query", "get_file_skeleton": "file_path"}.get(tool["name"], "symbol_name" if tool["name"] != "ping" else None)
            if required and (required not in schema.get("required", []) or schema.get("properties", {}).get(required, {}).get("type") != "string"):
                raise ValueError("schema MCP obrigatório incompatível")

    async def _mcp_call(self, generation, tool, arguments, timeout):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        command = self._command(generation, "serve")
        params = StdioServerParameters(command=command[0], args=command[1:], env=self._env(), cwd=str(generation / "work"))
        with (generation / "work" / "serve.stderr.log").open("a", encoding="utf-8") as error_log:
            async with asyncio.timeout(timeout):
                async with stdio_client(params, errlog=error_log) as (read, write):
                    async with ClientSession(read, write) as session:
                        initialized = await session.initialize()
                        listed = await session.list_tools()
                        schemas = [entry.model_dump(by_alias=True, exclude_none=True) for entry in listed.tools]
                        self._validate_tools(schemas)
                        answer = await session.call_tool(tool, arguments=arguments)
                        result = answer.model_dump(by_alias=True, exclude_none=True)
                        raw = json.dumps(result, ensure_ascii=False).encode()
                        if len(raw) > MAX_RESPONSE_BYTES:
                            return {"isError": True, "status": "response_too_large", "response_bytes": len(raw), "limit_bytes": MAX_RESPONSE_BYTES,
                                    "tools": sorted(entry.name for entry in listed.tools), "schema_bytes": len(json.dumps(schemas).encode())}
                        return {"result": result, "tools": sorted(entry.name for entry in listed.tools), "schema_bytes": len(json.dumps(schemas).encode()),
                                "response_bytes": len(raw), "protocol_version": initialized.protocolVersion,
                                "tool_calls": 1, "negotiation_calls": 2}

    def _query(self, config):
        if config["tool"] in BLOCKED_TOOLS:
            return {"ok": False, "status": "blocked_semantic_validation", "available": False, "query_verified": False,
                    "tool": config["tool"], "reason": "Oracle Python mínimo falhou nesta revisão upstream; grafo não será apresentado como correto.",
                    "upstream_revision": SOURCE_COMMIT, "counterexample": {"source": "def add(a,b): return a+b; def calculate(): return add(2,3)",
                    "expected_caller": "calculate", "observed_usages_caller": "add", "observed_calculate_callees": [], "observed_blast_radius": 0}}
        if not self._installation()["installed"]:
            return {"ok": False, "status": "not_installed", "available": False}
        current = self._current()
        if not current:
            return {"ok": False, "status": "not_indexed", "available": False}
        generation, manifest = current
        quality = self._current_quality(generation, manifest)
        if not quality["complete"]:
            return {"ok": False, "status": "index_failed_partial", "index_ready": False, "available": False, "index_audit": quality}
        if not self._manifest_current(manifest, generation / "corpus"):
            return {"ok": False, "status": "stale", "index_ready": False, "available": False}
        isolation = self._network_probe()
        if not isolation["available"]:
            return {"ok": False, "status": "isolation_unavailable", "available": False, "network_isolation": isolation}
        arguments = config.get("arguments", {})
        for key in ("file_path", "file_path_prefix"):
            if key in arguments and not any(path == arguments[key] or path.startswith(arguments[key].rstrip("/") + "/") for path in manifest["files"]):
                return {"ok": False, "status": "path_not_in_corpus", "available": True}
        started = time.monotonic()
        out = asyncio.run(self._mcp_call(generation, config["tool"], arguments, config.get("timeout_seconds", 30)))
        if not self._manifest_current(manifest, generation / "corpus"):
            return {"ok": False, "status": "sources_changed", "available": False}
        # Corpus provenance is retained; claims in the tool text remain untrusted.
        source_paths = set()
        def collect_paths(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if key in {"file_path", "path", "file"} and isinstance(item, str) and item in manifest["files"]:
                        source_paths.add(item)
                    collect_paths(item)
            elif isinstance(value, list):
                for item in value:
                    collect_paths(item)
        structured = out.get("result", {}).get("structuredContent", {})
        collect_paths(structured)
        sources = [{"path": rel, "sha256": manifest["files"][rel]["sha256"], "bytes": manifest["files"][rel]["bytes"]}
                   for rel in sorted(source_paths)]
        error = bool(out.get("isError") or out.get("result", {}).get("isError") or structured.get("error_count", 0) or structured.get("error"))
        return {"ok": not error, "status": out.get("status", "query_failed" if error else "completed"), "available": True, "index_ready": True,
                "query_verified": not error, "query_verification_scope": "chamada MCP concluída; precisão geral não calibrada", "tool": config["tool"], **out, "response": out.get("result"), "sources": sources[:10], "source_head": manifest["head"],
                "provenance": {"provider": "context-link", "version": VERSION, **self._revision_metadata(manifest), "generation": generation.name,
                               "manifest_sha256": _digest((generation / "manifest.json").read_bytes()), "sources": sources[:10], "scope": manifest["scope"]},
                "generation": generation.name, "network_isolation": isolation, "duration_seconds": round(time.monotonic() - started, 4),
                "tokens_measured": False, "source_provenance_truncated": len(sources) > 10}
