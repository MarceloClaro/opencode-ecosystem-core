# -*- coding: utf-8 -*-
"""SPEC-935-R1002: catálogo quântico como fonte de consulta local do Core.

Fonte preservada: `outputs/pesquisa-inovacao-enfoque/quantica-repositorios.json`.
Base consultável: `data/quantum_catalog/catalog.sqlite3` (SQLite, schema v1).

Regras centrais:
- Importação é explícita, transacional e idempotente. Consulta nunca importa.
- Consultas são somente leitura (SQLite mode=ro/query_only), parametrizadas e
  sem interpretar operadores da entrada (busca literal por tokens normalizados).
- TRL, licença, status, relevância e justificativa são alegações da fonte, nunca
  fatos verificados. Organização isolada não é repositório.
- Nenhum repositório, modelo, URL ou comando é executado.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import sqlite3
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

# --- Limites e caminhos (module-level para isolamento em teste) ------------
MAX_BYTES = 4 * 1024 * 1024
MAX_DB_BYTES = 64 * 1024 * 1024
MAX_TEXT = 8000
MAX_RECORDS = 5000
MAX_QUERY = 500
MAX_LIMIT = 20
SCHEMA_VERSION = 1

SOURCE_REL = "outputs/pesquisa-inovacao-enfoque/quantica-repositorios.json"
DATABASE_REL = "data/quantum_catalog/catalog.sqlite3"
PANEL_REL = "outputs/pesquisa-inovacao-enfoque/index_quantica.html"

_SEGMENT_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Campos pesquisáveis e suas descrições (sem validação externa).
SEARCH_FIELDS = [
    "id", "org_repo", "canonical_name", "tipo", "foco", "secao", "stacks",
    "justificativa_pesquisa", "aplicacao_pesquisa", "uso_sugerido",
    "relevancia_inovacao", "licenca",
]

CLAIM_FIELDS = [
    "tipo", "foco", "secao", "trl_estimado", "relevancia_inovacao",
    "uso_sugerido", "licenca", "status", "justificativa_pesquisa",
    "aplicacao_pesquisa",
]

VERIFICATION_STATUS = "unverified_catalog_claims"

_SCHEMA = (
    "CREATE TABLE IF NOT EXISTS imports ("
    "id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "source_sha256 TEXT NOT NULL,"
    "source_bytes BLOB NOT NULL,"
    "raw_records INTEGER NOT NULL,"
    "unique_entries INTEGER NOT NULL,"
    "repositories INTEGER NOT NULL,"
    "organizations INTEGER NOT NULL,"
    "duplicates_collapsed INTEGER NOT NULL,"
    "quarantined INTEGER NOT NULL,"
    "historical_entries INTEGER NOT NULL,"
    "imported_at TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS entries ("
    "import_id INTEGER NOT NULL,"
    "canonical_key TEXT NOT NULL,"
    "kind TEXT NOT NULL,"
    "canonical_name TEXT NOT NULL,"
    "historical INTEGER NOT NULL,"
    "search_tokens TEXT NOT NULL,"
    "aliases TEXT NOT NULL,"
    "stacks_norm TEXT NOT NULL,"
    "category_norm TEXT NOT NULL,"
    "summary TEXT NOT NULL,"
    "conflicting TEXT NOT NULL,"
    "PRIMARY KEY (import_id, canonical_key))",
    "CREATE TABLE IF NOT EXISTS source_records ("
    "import_id INTEGER NOT NULL,"
    "json_pointer TEXT NOT NULL,"
    "canonical_key TEXT,"
    "record_sha256 TEXT NOT NULL,"
    "claims TEXT NOT NULL,"
    "PRIMARY KEY (import_id, json_pointer))",
)

_PANEL_JS = (
    "(function(){function apply(){"
    "var q=document.querySelector('#catalog-query');"
    "var cat=document.querySelector('#catalog-category');"
    "var hist=document.querySelector('#catalog-history');"
    "var count=document.querySelector('#catalog-count');"
    "var raw=(q.value||'').trim().toLowerCase();"
    "var tokens=raw?raw.split(/\\s+/):[];"
    "var category=cat.value||'';"
    "var include=hist.checked;"
    "var cards=document.querySelectorAll('.repo-card');"
    "var visible=0;"
    "for(var i=0;i<cards.length;i++){var c=cards[i];"
    "var search=c.dataset.search||'';"
    "var catv=c.dataset.category||'';"
    "var histv=c.dataset.historical==='true';"
    "var match=true;"
    "for(var j=0;j<tokens.length;j++){"
    "if((' '+search+' ').indexOf(' '+tokens[j]+' ')<0){match=false;break;}}"
    "if(category&&catv!==category){match=false;}"
    "if(histv&&!include){match=false;}"
    "c.hidden=!match;if(match){visible++;}}"
    "count.textContent=String(visible);}"
    "var q=document.querySelector('#catalog-query');"
    "var cat=document.querySelector('#catalog-category');"
    "var hist=document.querySelector('#catalog-history');"
    "q.addEventListener('input',apply);"
    "cat.addEventListener('input',apply);"
    "hist.addEventListener('change',apply);"
    "apply();})();"
)


class QuantumCatalog:
    """Consulta local do catálogo quântico preservando proveniência."""

    def __init__(self, root: str | Path | None = None):
        self._root = Path(root).resolve() if root is not None else Path(__file__).resolve().parents[1]
        self._source_error = "unknown"

    # -- caminhos protegidos -------------------------------------------------
    @property
    def _source_path(self) -> Path:
        return self._root / SOURCE_REL

    @property
    def _db_path(self) -> Path:
        return self._root / DATABASE_REL

    def _safe(self, rel: str) -> Path | None:
        """Resolve um caminho relativo rejeitando componentes que sejam symlinks."""
        current = self._root
        for part in Path(rel).parts:
            current = current / part
            if current.is_symlink():
                return None
        return current

    # -- normalização e parsing ---------------------------------------------
    @staticmethod
    def _norm(text: Any) -> str:
        nfkd = unicodedata.normalize("NFKD", str(text)).casefold()
        return "".join(ch for ch in nfkd if not unicodedata.combining(ch))

    @staticmethod
    def _tokens(text: Any) -> set[str]:
        return set(_TOKEN_RE.findall(QuantumCatalog._norm(text)))

    @staticmethod
    def _token_list(text: str) -> list[str]:
        return _TOKEN_RE.findall(QuantumCatalog._norm(text))

    @staticmethod
    def _canonical(org_repo: str) -> str:
        value = org_repo.strip().rstrip("/")
        value = re.sub(r"\s+", " ", value)
        return QuantumCatalog._norm(value)

    @staticmethod
    def _valid_segment(segment: str) -> bool:
        if not segment or segment in (".", ".."):
            return False
        return bool(_SEGMENT_RE.fullmatch(segment))

    @staticmethod
    def _reject_constant(value: str) -> Any:
        raise ValueError(f"non-finite JSON number: {value}")

    @staticmethod
    def _reject_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    # -- conexões ------------------------------------------------------------
    def _connect(self, readonly: bool = True) -> sqlite3.Connection:
        db = self._db_path
        if readonly:
            connection = sqlite3.connect("file:" + str(db) + "?mode=ro", uri=True, timeout=5)
            connection.execute("PRAGMA query_only=ON")
        else:
            connection = sqlite3.connect(str(db), timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _readonly(self) -> sqlite3.Connection | None:
        db = self._db_path
        if db.is_symlink() or not db.is_file() or db.stat().st_size > MAX_DB_BYTES:
            return None
        try:
            with sqlite3.connect("file:" + str(db) + "?mode=ro", uri=True) as probe:
                if probe.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
                    return None
        except sqlite3.Error:
            return None
        try:
            return self._connect(readonly=True)
        except sqlite3.Error:
            return None

    def _db_writable_ok(self) -> bool:
        db = self._db_path
        if not db.exists():
            return True
        if db.is_symlink() or db.stat().st_size > MAX_DB_BYTES:
            self._source_error = "db_unsafe"
            return False
        try:
            with sqlite3.connect("file:" + str(db) + "?mode=ro", uri=True) as probe:
                if probe.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
                    self._source_error = "db_schema_version"
                    return False
        except sqlite3.Error:
            self._source_error = "db_corrupt"
            return False
        return True

    def _schema(self, connection: sqlite3.Connection) -> None:
        connection.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
        for statement in _SCHEMA:
            connection.execute(statement)

    # -- leitura da fonte ----------------------------------------------------
    def _read_source(self):
        path = self._safe(SOURCE_REL)
        if path is None:
            self._source_error = "source_symlink"
            return None
        if not path.is_file():
            self._source_error = "source_missing"
            return None
        raw = path.read_bytes()
        if len(raw) > MAX_BYTES:
            self._source_error = "source_too_large"
            return None
        digest = hashlib.sha256(raw).hexdigest()
        try:
            records = json.loads(
                raw.decode("utf-8-sig"),
                parse_constant=self._reject_constant,
                object_pairs_hook=self._reject_duplicates,
            )
        except (ValueError, UnicodeDecodeError) as exc:
            self._source_error = "source_invalid_json:" + type(exc).__name__
            return None
        if not isinstance(records, list):
            self._source_error = "source_not_list"
            return None
        if len(records) > MAX_RECORDS:
            self._source_error = "source_too_many_records"
            return None
        return raw, digest, records

    def _stale(self, imported_sha: str) -> dict[str, Any]:
        path = self._safe(SOURCE_REL)
        if path is None or not path.is_file():
            return {"source_stale": None, "current_source_state": "unavailable"}
        raw = path.read_bytes()
        if len(raw) > MAX_BYTES:
            return {"source_stale": None, "current_source_state": "invalid"}
        current = hashlib.sha256(raw).hexdigest()
        return {"source_stale": current != imported_sha, "current_source_state": "available"}

    @staticmethod
    def _unavailable(code: str = "database_unavailable") -> dict[str, Any]:
        return {"status": "unavailable", "abstained": True, "results": [], "error_code": code}

    # -- importação ----------------------------------------------------------
    def import_source(self) -> dict[str, Any]:
        source = self._read_source()
        if source is None:
            return self._unavailable(self._source_error)
        raw, digest, records = source
        if not self._db_writable_ok():
            return self._unavailable(self._source_error)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            connection = self._connect(readonly=False)
        except sqlite3.Error:
            return self._unavailable("db_open_failed")
        outcome = self._unavailable("import_failed")
        try:
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                self._schema(connection)
                latest = connection.execute(
                    "SELECT source_sha256 FROM imports ORDER BY id DESC LIMIT 1"
                ).fetchone()
                if latest is not None and latest["source_sha256"] == digest:
                    outcome = {"status": "unchanged", "source_sha256": digest,
                               "reason": "same_source_bytes"}
                else:
                    self._insert_snapshot(connection, raw, digest, records)
                    outcome = {"status": "imported", "source_sha256": digest,
                               "counts": self._counts(connection)}
        except sqlite3.Error as exc:
            return self._unavailable("import_failed:" + type(exc).__name__)
        finally:
            connection.close()
        return outcome

    @staticmethod
    def _counts(connection: sqlite3.Connection) -> dict[str, Any]:
        row = connection.execute(
            "SELECT raw_records, unique_entries, repositories, organizations, "
            "duplicates_collapsed, quarantined, historical_entries "
            "FROM imports ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return {
            "raw_records": row["raw_records"],
            "unique_entries": row["unique_entries"],
            "repositories": row["repositories"],
            "organizations": row["organizations"],
            "duplicates_collapsed": row["duplicates_collapsed"],
            "quarantined": row["quarantined"],
            "historical_entries": row["historical_entries"],
        }

    def _fields_ok(self, rec: dict) -> bool:
        for key, value in rec.items():
            if isinstance(value, str) and len(value) > MAX_TEXT:
                return False
            if key == "stacks":
                if not isinstance(value, list):
                    return False
                for item in value:
                    if not isinstance(item, str) or len(item) > MAX_TEXT:
                        return False
        return True

    def _classify(self, rec: dict):
        org_repo = rec.get("org_repo")
        if not isinstance(org_repo, str) or not org_repo.strip() or len(org_repo) > MAX_TEXT:
            return None
        if not self._fields_ok(rec):
            return None
        parts = org_repo.split("/")
        if len(parts) == 2 and all(self._valid_segment(p) for p in parts):
            kind = "repository"
            name = parts[1]
        elif len(parts) == 1 and self._valid_segment(parts[0]):
            kind = "organization"
            name = parts[0]
        else:
            return None
        canonical = self._canonical(org_repo)
        historical = (self._norm(str(rec.get("status", ""))) == "abandonado") or (
            self._norm(str(rec.get("secao", ""))) == "abandoned projects"
        )
        secao = rec.get("secao") if isinstance(rec.get("secao"), str) else ""
        foco = rec.get("foco") if isinstance(rec.get("foco"), str) else ""
        return {
            "canonical": canonical, "kind": kind, "name": name,
            "historical": historical, "secao": secao, "foco": foco,
        }

    def _search_tokens(self, canonical: str, name: str, recs: list[dict]) -> str:
        tokens: set[str] = set()
        tokens.update(self._tokens(canonical))
        tokens.update(self._tokens(name))
        for rec in recs:
            for field in SEARCH_FIELDS:
                value = rec["claims"].get(field)
                if isinstance(value, str):
                    tokens.update(self._tokens(value))
            stacks = rec["claims"].get("stacks")
            if isinstance(stacks, list):
                for item in stacks:
                    if isinstance(item, str):
                        tokens.update(self._tokens(item))
        return " ".join(sorted(tokens))

    @staticmethod
    def _stacks_norm(recs: list[dict]) -> list[str]:
        out: set[str] = set()
        for rec in recs:
            stacks = rec["claims"].get("stacks")
            if isinstance(stacks, list):
                for item in stacks:
                    if isinstance(item, str):
                        out.add(QuantumCatalog._norm(item))
        return sorted(out)

    @staticmethod
    def _conflicting(recs: list[dict]) -> list[str]:
        out = []
        for field in CLAIM_FIELDS:
            values = {json.dumps(rec["claims"].get(field), sort_keys=True, ensure_ascii=False)
                      for rec in recs}
            if len(values) > 1:
                out.append(field)
        return out

    def _insert_snapshot(self, connection: sqlite3.Connection,
                          raw: bytes, digest: str, records: list) -> None:
        groups: dict[str, dict] = {}
        records_out: list[tuple[str | None, str, str, str]] = []
        quarantined = 0
        for index, rec in enumerate(records):
            json_pointer = "/" + str(index)
            rbytes = json.dumps(rec, ensure_ascii=False, sort_keys=True,
                                separators=(",", ":")).encode("utf-8")
            rsha = hashlib.sha256(rbytes).hexdigest()
            claims_json = json.dumps(rec, ensure_ascii=False)
            if not isinstance(rec, dict):
                quarantined += 1
                records_out.append((None, json_pointer, rsha, claims_json))
                continue
            info = self._classify(rec)
            if info is None:
                quarantined += 1
                records_out.append((None, json_pointer, rsha, claims_json))
                continue
            canonical = info["canonical"]
            group = groups.setdefault(canonical, {
                "records": [], "kind": info["kind"], "name": info["name"],
                "historical": info["historical"], "secao": info["secao"],
                "foco": info["foco"],
            })
            group["records"].append({
                "json_pointer": json_pointer, "record_sha256": rsha,
                "claims": rec,
            })
            records_out.append((canonical, json_pointer, rsha, claims_json))

        repositories = sum(1 for g in groups.values() if g["kind"] == "repository")
        organizations = len(groups) - repositories
        duplicates = sum(1 for g in groups.values() if len(g["records"]) > 1)
        historical = sum(1 for g in groups.values() if g["historical"])
        import_id = connection.execute(
            "INSERT INTO imports (source_sha256, source_bytes, raw_records, "
            "unique_entries, repositories, organizations, duplicates_collapsed, "
            "quarantined, historical_entries, imported_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (digest, sqlite3.Binary(raw), len(records), len(groups), repositories,
             organizations, duplicates, quarantined, historical,
             datetime.now(timezone.utc).isoformat()),
        ).lastrowid

        for canonical, json_pointer, rsha, claims_json in records_out:
            connection.execute(
                "INSERT INTO source_records (import_id, json_pointer, canonical_key, "
                "record_sha256, claims) VALUES (?,?,?,?,?)",
                (import_id, json_pointer, canonical, rsha, claims_json),
            )

        for canonical, group in groups.items():
            recs = group["records"]
            aliases = sorted({
                self._norm(str(r["claims"].get("id")))
                for r in recs
                if r["claims"].get("id") is not None and str(r["claims"].get("id")).strip()
            })
            search_tokens = self._search_tokens(canonical, group["name"], recs)
            stacks_norm = json.dumps(self._stacks_norm(recs))
            category_norm = self._norm(group["secao"])
            summary = group["foco"]
            conflicting = json.dumps(self._conflicting(recs))
            connection.execute(
                "INSERT INTO entries (import_id, canonical_key, kind, canonical_name, "
                "historical, search_tokens, aliases, stacks_norm, category_norm, "
                "summary, conflicting) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (import_id, canonical, group["kind"], group["name"],
                 1 if group["historical"] else 0, search_tokens,
                 json.dumps(aliases), stacks_norm, category_norm, summary, conflicting),
            )

    # -- consultas -----------------------------------------------------------
    def _latest_import_id(self, connection: sqlite3.Connection):
        row = connection.execute("SELECT id, source_sha256 FROM imports ORDER BY id DESC LIMIT 1").fetchone()
        return row

    def _entries(self, connection: sqlite3.Connection, import_id: int) -> list[dict]:
        rows = connection.execute(
            "SELECT * FROM entries WHERE import_id = ? ORDER BY canonical_key", (import_id,)
        ).fetchall()
        return [dict(row) for row in rows]

    def execute(self, config: dict[str, Any]) -> dict[str, Any]:
        self._validate_config(config)
        op = config["operation"]
        connection = self._readonly()
        if connection is None:
            return self._unavailable("database_unavailable")
        try:
            if op == "status":
                return self._status(connection)
            if op == "history":
                return self._history(connection, config)
            if op == "list":
                return self._list(connection, config)
            if op == "search":
                return self._search(connection, config)
            return self._get(connection, config)
        finally:
            connection.close()

    def _validate_config(self, config: dict[str, Any]) -> None:
        if not isinstance(config, dict):
            raise ValueError("config deve ser um objeto")
        op = config.get("operation")
        allowed = {"operation"}
        if op == "status":
            pass
        elif op == "history":
            allowed |= {"limit", "offset"}
        elif op == "list":
            allowed |= {"limit", "offset", "kind", "include_historical"}
        elif op == "search":
            allowed |= {"query", "limit", "offset", "kind", "stack", "category", "include_historical"}
        elif op == "get":
            allowed |= {"identifier"}
        else:
            raise ValueError("operacao desconhecida")
        extra = set(config) - allowed
        if extra:
            raise ValueError("campo nao esperado: " + sorted(extra)[0])
        if "limit" in config:
            limit = config["limit"]
            if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_LIMIT:
                raise ValueError("limit deve ser inteiro entre 1 e %d" % MAX_LIMIT)
        if "offset" in config:
            offset = config["offset"]
            if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
                raise ValueError("offset deve ser inteiro nao negativo")
        if "include_historical" in config and not isinstance(config["include_historical"], bool):
            raise ValueError("include_historical deve ser booleano")
        if "kind" in config and config["kind"] not in {"repository", "organization"}:
            raise ValueError("kind invalido")
        if "stack" in config and not isinstance(config["stack"], str):
            raise ValueError("stack deve ser texto")
        if "category" in config and not isinstance(config["category"], str):
            raise ValueError("category deve ser texto")
        if op == "search":
            self._validate_query(config["query"])
        if op == "get":
            self._validate_identifier(config["identifier"])

    @staticmethod
    def _validate_query(query: Any) -> None:
        if not isinstance(query, str):
            raise ValueError("query deve ser texto")
        value = query.strip()
        if not value or len(value) > MAX_QUERY:
            raise ValueError("query deve ter entre 1 e %d caracteres" % MAX_QUERY)
        if not QuantumCatalog._token_list(value):
            raise ValueError("query nao possui tokens pesquisaveis")

    @staticmethod
    def _validate_identifier(identifier: Any) -> None:
        if not isinstance(identifier, str) or not identifier.strip() or len(identifier) > MAX_QUERY:
            raise ValueError("identifier deve ser texto entre 1 e %d caracteres" % MAX_QUERY)
        value = identifier.strip()
        if any(ord(ch) < 32 for ch in value) or ".." in value:
            raise ValueError("identifier invalido")
        if "://" in value:
            parsed = urlparse(value)
            if parsed.scheme not in ("http", "https") or parsed.netloc.lower() != "github.com":
                raise ValueError("identifier deve ser repositorio github")

    def _resolve_identifier(self, identifier: str) -> str:
        value = identifier.strip()
        if "://" in value:
            match = re.search(r"github\.com/([^/?#]+)/([^/?#]+)", value, re.I)
            if match is None:
                raise ValueError("identifier github sem owner/repo")
            return self._canonical(f"{match.group(1)}/{match.group(2)}")
        return self._canonical(value)

    def _status(self, connection: sqlite3.Connection) -> dict[str, Any]:
        row = connection.execute("SELECT * FROM imports ORDER BY id DESC LIMIT 1").fetchone()
        if row is None:
            return self._unavailable("no_import")
        stale = self._stale(row["source_sha256"])
        return {
            "status": "ok",
            "counts": self._counts(connection),
            "source": {"sha256": row["source_sha256"], "path": str(self._source_path),
                       "state": "imported"},
            "policy": {"external_validation": False, "instruction_authority": "none"},
            **stale,
        }

    def _history(self, connection: sqlite3.Connection, config: dict[str, Any]) -> dict[str, Any]:
        rows = connection.execute(
            "SELECT id, source_sha256, raw_records, unique_entries, imported_at "
            "FROM imports ORDER BY id DESC"
        ).fetchall()
        result = [dict(row) for row in rows]
        page = self._page(config, result)
        row = connection.execute("SELECT source_sha256 FROM imports ORDER BY id DESC LIMIT 1").fetchone()
        return {"status": "ok", "abstained": False, **page,
                **self._stale(row["source_sha256"] if row else "")}

    def _summary(self, entry: dict, source_sha256: str) -> dict[str, Any]:
        return {
            "canonical_key": entry["canonical_key"],
            "canonical_name": entry["canonical_name"],
            "kind": entry["kind"],
            "historical": bool(entry["historical"]),
            "verification_status": VERIFICATION_STATUS,
            "source_sha256": source_sha256,
        }

    def _list(self, connection: sqlite3.Connection, config: dict[str, Any]) -> dict[str, Any]:
        row = self._latest_import_id(connection)
        if row is None:
            return self._unavailable("no_import")
        import_id, sha = row["id"], row["source_sha256"]
        entries = self._entries(connection, import_id)
        kind = config.get("kind")
        include = config.get("include_historical", False)
        matched = [self._summary(e, sha) for e in entries
                   if (kind is None or e["kind"] == kind)
                   and (include or not e["historical"])]
        return {"status": "ok", "abstained": False, **self._page(config, matched),
                **self._stale(sha)}

    def _search(self, connection: sqlite3.Connection, config: dict[str, Any]) -> dict[str, Any]:
        row = self._latest_import_id(connection)
        if row is None:
            return self._unavailable("no_import")
        import_id, sha = row["id"], row["source_sha256"]
        tokens = self._token_list(config["query"])
        entries = self._entries(connection, import_id)
        kind = config.get("kind")
        include = config.get("include_historical", False)
        stack = self._norm(config["stack"]) if config.get("stack") else None
        category = self._norm(config["category"]) if config.get("category") else None
        matched = []
        for entry in entries:
            if kind and entry["kind"] != kind:
                continue
            if entry["historical"] and not include:
                continue
            entry_tokens = set(entry["search_tokens"].split())
            if not set(tokens).issubset(entry_tokens):
                continue
            if stack and stack not in json.loads(entry["stacks_norm"]):
                continue
            if category and entry["category_norm"] != category:
                continue
            matched.append(self._summary(entry, sha))
        if not matched:
            return {"status": "no_matches", "abstained": True, "results": [],
                    "total_matches": 0, "has_more": False,
                    "searched_fields": SEARCH_FIELDS, **self._stale(sha)}
        return {"status": "ok", "abstained": False, "searched_fields": SEARCH_FIELDS,
                **self._page(config, matched), **self._stale(sha)}

    def _get(self, connection: sqlite3.Connection, config: dict[str, Any]) -> dict[str, Any]:
        row = self._latest_import_id(connection)
        if row is None:
            return self._unavailable("no_import")
        import_id, sha = row["id"], row["source_sha256"]
        identifier = self._resolve_identifier(config["identifier"])
        entries = self._entries(connection, import_id)
        alias_map: dict[str, str] = {}
        for entry in entries:
            for alias in json.loads(entry["aliases"]):
                alias_map.setdefault(alias, entry["canonical_key"])
        canonical = alias_map.get(identifier, identifier)
        entry = next((e for e in entries if e["canonical_key"] == canonical), None)
        if entry is None:
            return {"status": "no_matches", "abstained": True, "results": [],
                    "total_matches": 0, "has_more": False, **self._stale(sha)}
        records = connection.execute(
            "SELECT json_pointer, record_sha256, claims FROM source_records "
            "WHERE import_id = ? AND canonical_key = ? ORDER BY json_pointer",
            (import_id, canonical),
        ).fetchall()
        item = {
            "canonical_key": entry["canonical_key"],
            "canonical_name": entry["canonical_name"],
            "kind": entry["kind"],
            "aliases": json.loads(entry["aliases"]),
            "verification_status": VERIFICATION_STATUS,
            "records": [{"json_pointer": r["json_pointer"],
                         "record_sha256": r["record_sha256"],
                         "claims": json.loads(r["claims"])} for r in records],
            "conflicting_fields": json.loads(entry["conflicting"]),
            "source_sha256": sha,
            "historical_in_source": bool(entry["historical"]),
            "historical": bool(entry["historical"]),
        }
        return {"status": "ok", "abstained": False, "results": [item],
                "total_matches": 1, "has_more": False, **self._stale(sha)}

    @staticmethod
    def _page(config: dict[str, Any], matched: list) -> dict[str, Any]:
        limit = config.get("limit", MAX_LIMIT)
        offset = config.get("offset", 0)
        page = matched[offset:offset + limit]
        return {
            "results": page,
            "total_matches": len(matched),
            "has_more": offset + limit < len(matched),
        }

    # -- painel --------------------------------------------------------------
    def export_panel(self) -> dict[str, Any]:
        connection = self._readonly()
        if connection is None:
            return self._unavailable("database_unavailable")
        try:
            row = self._latest_import_id(connection)
            if row is None:
                return self._unavailable("no_import")
            import_id, sha = row["id"], row["source_sha256"]
            entries = self._entries(connection, import_id)
        finally:
            connection.close()
        panel_path = self._safe(PANEL_REL)
        if panel_path is None:
            return self._unavailable("panel_path_unsafe")
        if panel_path.is_symlink() or (panel_path.exists() and not panel_path.is_file()):
            return self._unavailable("panel_path_unsafe")
        cards = []
        categories: set[str] = set()
        for entry in entries:
            category = entry["category_norm"]
            if category:
                categories.add(category)
            cards.append({
                "search": entry["search_tokens"],
                "category": category,
                "historical": "true" if entry["historical"] else "false",
                "name": entry["canonical_name"],
                "kind": entry["kind"],
                "summary": entry["summary"],
            })
        html_text = self._render_panel(sha, sorted(categories), cards)
        panel_path.write_text(html_text, encoding="utf-8")
        return {"status": "ok", "path": str(panel_path), "cards": len(cards)}

    @staticmethod
    def _render_panel(sha: str, categories: list[str], cards: list[dict]) -> str:
        parts = [
            '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">',
            f'<meta name="source-sha256" content="{sha}">',
            '<title>Catálogo Quântico — Fonte de Consulta do Core</title>',
            '<style>body{font-family:system-ui;background:#0b1020;color:#e8ecf5;'
            'padding:20px}.repo-card{border:1px solid #2b3564;border-radius:8px;'
            'padding:10px;margin:8px 0;background:#121830}.note{color:#a5b0d0;'
            'font-size:12px}</style></head><body>',
            '<h1>Catálogo Quântico</h1>',
            '<p class="note">Status, TRL, licença e atividade: não verificado '
            '— dados de curadoria, não validação externa.</p>',
            '<input id="catalog-query" placeholder="Buscar...">',
            '<select id="catalog-category"><option value="">Todas as categorias</option>',
            ''.join(f'<option value="{html.escape(c)}">{html.escape(c)}</option>'
                    for c in categories),
            '</select>',
            '<label><input type="checkbox" id="catalog-history"> Incluir históricos</label>',
            '<span id="catalog-count"></span>',
        ]
        for card in cards:
            parts.append(
                f'<div class="repo-card" data-search="{html.escape(card["search"])}" '
                f'data-category="{html.escape(card["category"])}" '
                f'data-historical="{card["historical"]}">'
                f'<strong>{html.escape(card["name"])}</strong> '
                f'<span class="note">({html.escape(card["kind"])})</span>'
                f'<p>{html.escape(card["summary"])}</p></div>'
            )
        parts.append("<script>" + _PANEL_JS + "</script></body></html>")
        return "".join(parts)
