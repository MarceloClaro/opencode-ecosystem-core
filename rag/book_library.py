"""SPEC-935-R657: PDFs técnicos locais, páginas citáveis e busca offline.

O conteúdo dos PDFs é dado não confiável. Este módulo somente extrai e recupera
texto; não executa instruções, links, código, modelos ou chamadas de rede.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import unicodedata
from contextlib import closing
from pathlib import Path
from typing import Any


class LocalBookLibrary:
    """Índice SQLite explícito, com leitura somente de fontes ainda atuais."""

    SCHEMA_VERSION = 1
    MAX_SOURCE_BYTES = 200 * 1024 * 1024
    MAX_PAGES = 2000
    MAX_PAGE_CHARS = 100_000
    MAX_QUERY_CHARS = 2000
    MAX_QUERY_TERMS = 32
    MAX_CANDIDATES = 500
    CHUNK_CHARS = 1200
    REQUIRED_COLUMNS = {
        "metadata": {"key", "value"},
        "sources": {"file", "title", "book_id", "status", "error", "size", "mtime_ns"},
        "pages": {"book_id", "page", "text", "page_sha256"},
        "chunks": {"chunk_id", "book_id", "page", "position", "text"},
        "terms": {"term", "chunk_id"},
    }
    STOPWORDS = frozenset(
        "a o as os de da do das dos um uma e ou em no na nos nas para por com "
        "que se como qual quais sobre ao aos the of and or in on to for with "
        "is are was what how an this that".split()
    )

    def __init__(self, source_dir=None, index_path=None):
        root = Path(__file__).resolve().parents[1]
        self.source_dir = Path(source_dir if source_dir is not None else root / "biblioteca ai").resolve()
        self.index_path = Path(index_path if index_path is not None else root / ".mci_cache/book_library.sqlite3").resolve()

    @staticmethod
    def _pdf_reader():
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ImportError("pypdf ausente; instale pypdf para indexar PDFs.") from exc
        return PdfReader

    def _connect(self, *, readonly=False):
        if readonly:
            connection = sqlite3.connect(self.index_path.as_uri() + "?mode=ro", uri=True, timeout=10)
        else:
            connection = sqlite3.connect(self.index_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _sha_file(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    @classmethod
    def _tokens(cls, text: str) -> set[str]:
        normalized = unicodedata.normalize("NFKD", text).casefold()
        normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        return {word for word in re.findall(r"[a-z0-9]+", normalized)
                if len(word) >= 2 and word not in cls.STOPWORDS}

    def _files(self) -> list[Path]:
        if not self.source_dir.is_dir():
            return []
        return sorted((path for path in self.source_dir.iterdir()
                       if path.suffix.casefold() == ".pdf"), key=lambda path: path.name)

    def _inside(self, path: Path) -> bool:
        return path.resolve().is_relative_to(self.source_dir)

    @staticmethod
    def _excluded_report(path: Path) -> bool:
        # O nome visível do alias não pode reintroduzir um laudo excluído.
        return (path.name.casefold() == "laudo.pdf"
                or path.resolve().name.casefold() == "laudo.pdf")

    @classmethod
    def _schema(cls, connection):
        # execute() mantém todas as alterações na mesma transação; executescript
        # faria commit implícito e poderia deixar uma atualização incompleta.
        # Reparação acontece somente na indexação solicitada. A consulta não
        # altera tabelas ausentes ou incompletas nem declara o índice pronto.
        for table, required in cls.REQUIRED_COLUMNS.items():
            existing = {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}
            if existing and not required <= existing:
                connection.execute(f"DROP TABLE {table}")
        statements = (
            "CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS sources (file TEXT PRIMARY KEY, title TEXT NOT NULL, "
            "book_id TEXT, status TEXT NOT NULL, error TEXT, size INTEGER, mtime_ns INTEGER)",
            "CREATE TABLE IF NOT EXISTS pages (book_id TEXT NOT NULL, page INTEGER NOT NULL, "
            "text TEXT NOT NULL, page_sha256 TEXT NOT NULL, PRIMARY KEY(book_id,page))",
            "CREATE TABLE IF NOT EXISTS chunks (chunk_id TEXT PRIMARY KEY, book_id TEXT NOT NULL, "
            "page INTEGER NOT NULL, position INTEGER NOT NULL, text TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS terms (term TEXT NOT NULL, chunk_id TEXT NOT NULL, "
            "PRIMARY KEY(term,chunk_id))",
            "CREATE INDEX IF NOT EXISTS chunk_book ON chunks(book_id)",
        )
        for statement in statements:
            connection.execute(statement)

    @classmethod
    def _validate_schema(cls, connection):
        for table, required in cls.REQUIRED_COLUMNS.items():
            existing = {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}
            if not required <= existing:
                raise ValueError(f"Índice incompleto: tabela {table} ou colunas obrigatórias ausentes; execute indexar.")

    def _extract(self, path: Path):
        if path.stat().st_size > self.MAX_SOURCE_BYTES:
            raise ValueError("PDF excede o limite de 200 MiB.")
        before = self._sha_file(path)
        reader_class = self._pdf_reader()
        with path.open("rb") as stream:
            reader = reader_class(stream)
            if reader.is_encrypted:
                raise ValueError("PDF criptografado não participa do índice.")
            if len(reader.pages) > self.MAX_PAGES:
                raise ValueError("PDF excede o limite de 2000 páginas.")
            pages = []
            for number, page in enumerate(reader.pages, start=1):
                text = re.sub(r"\s+", " ", page.extract_text() or "").strip()
                if len(text) > self.MAX_PAGE_CHARS:
                    raise ValueError(f"Página {number} excede o limite de 100000 caracteres.")
                pages.append((number, text))
        if self._sha_file(path) != before:
            raise ValueError("Fonte mudou durante a extração; repita a indexação.")
        return before, pages

    @classmethod
    def _chunks(cls, text: str):
        start = 0
        while start < len(text):
            end = min(len(text), start + cls.CHUNK_CHARS)
            if end < len(text):
                boundary = text.rfind(" ", start, end)
                if boundary > start:
                    end = boundary
            fragment = text[start:end].strip()
            if fragment:
                yield fragment
            start = end
            while start < len(text) and text[start].isspace():
                start += 1

    def index(self) -> dict[str, Any]:
        """Reconstrói o índice em transação; erros de fonte ficam no inventário."""
        if not self.source_dir.is_dir():
            raise FileNotFoundError(f"Pasta da biblioteca não encontrada: {self.source_dir}")
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        connection = self._connect()
        try:
            # WAL permite consultas ao snapshot anterior enquanto PDFs são
            # extraídos e a nova versão ainda não foi confirmada.
            connection.execute("PRAGMA journal_mode=WAL")
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                self._schema(connection)
                for table in ("terms", "chunks", "pages", "sources"):
                    connection.execute(f"DELETE FROM {table}")
                indexed_ids = set()
                for path in self._files():
                    title = path.stem
                    book_id = None
                    pages = []
                    error = None
                    size = mtime_ns = None
                    try:
                        if not self._inside(path):
                            state, error = "excluded", "Symlink fora da pasta da biblioteca."
                        elif self._excluded_report(path):
                            state, error = "excluded", "Laudo ou alias para laudo.pdf excluído da biblioteca técnica por padrão."
                        elif not path.is_file():
                            state, error = "excluded", "A fonte não é um arquivo regular."
                        else:
                            stat = path.stat()
                            size, mtime_ns = stat.st_size, stat.st_mtime_ns
                            if size == 0:
                                state, error = "empty", "PDF vazio, sem conteúdo para extrair."
                            else:
                                book_id, pages = self._extract(path)
                                state = "indexed" if any(text for _, text in pages) else "no_text"
                                if state == "no_text":
                                    error = "PDF sem texto extraível; OCR não foi executado."
                    except Exception as exc:
                        state, error, book_id = "error", str(exc), None
                    connection.execute("INSERT INTO sources VALUES (?,?,?,?,?,?,?)",
                                       (path.name, title, book_id, state, error, size, mtime_ns))
                    if state != "indexed" or book_id in indexed_ids:
                        continue
                    indexed_ids.add(book_id)
                    for number, text in pages:
                        page_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
                        connection.execute("INSERT INTO pages VALUES (?,?,?,?)", (book_id, number, text, page_sha))
                        for position, fragment in enumerate(self._chunks(text), start=1):
                            chunk_id = f"{book_id}:p{number}:c{position}"
                            connection.execute("INSERT INTO chunks VALUES (?,?,?,?,?)",
                                               (chunk_id, book_id, number, position, fragment))
                            connection.executemany("INSERT INTO terms VALUES (?,?)",
                                                   ((term, chunk_id) for term in sorted(self._tokens(fragment))))
                connection.execute("INSERT OR REPLACE INTO metadata VALUES ('schema_version',?)",
                                   (str(self.SCHEMA_VERSION),))
                connection.execute("INSERT OR REPLACE INTO metadata VALUES ('source_dir',?)", (str(self.source_dir),))
        finally:
            connection.close()
        return self.status()

    def _snapshot(self):
        """Lê inventário e verifica hashes; nunca cria/atualiza o índice."""
        base = {"status": "missing", "indexed": False, "books": 0, "pages": 0, "chunks": 0,
                "inventory": [], "outdated": [], "source_dir": str(self.source_dir),
                "index_path": str(self.index_path), "offline": True,
                "source_kind": "local_technical_book", "clinical_evidence": False}
        if not self.index_path.is_file():
            return base, set()
        try:
            with closing(self._connect(readonly=True)) as connection:
                self._validate_schema(connection)
                metadata = dict(connection.execute("SELECT key,value FROM metadata"))
                if metadata.get("schema_version") != str(self.SCHEMA_VERSION):
                    raise ValueError("Versão do índice incompatível; execute indexar.")
                if metadata.get("source_dir") != str(self.source_dir):
                    raise ValueError("Índice pertence a outra pasta; execute indexar.")
                inventory = [dict(row) for row in connection.execute("SELECT * FROM sources ORDER BY file")]
                counts = {"books": connection.execute("SELECT COUNT(DISTINCT book_id) FROM sources WHERE status='indexed'").fetchone()[0],
                          "pages": connection.execute("SELECT COUNT(*) FROM pages").fetchone()[0],
                          "chunks": connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]}
        except (sqlite3.Error, ValueError) as exc:
            base.update(status="error", error=str(exc))
            return base, set()
        fresh = set()
        outdated = []
        known = {item["file"] for item in inventory}
        for item in inventory:
            path = self.source_dir / item["file"]
            current = False
            try:
                if item["status"] == "indexed":
                    current = (self._inside(path) and not self._excluded_report(path) and path.is_file()
                               and path.stat().st_size <= self.MAX_SOURCE_BYTES
                               and self._sha_file(path) == item["book_id"])
                    if current:
                        fresh.add(item["book_id"])
                elif item["status"] == "no_text" and item["book_id"]:
                    current = (self._inside(path) and not self._excluded_report(path) and path.is_file()
                               and path.stat().st_size <= self.MAX_SOURCE_BYTES
                               and self._sha_file(path) == item["book_id"])
                elif item["status"] == "excluded":
                    current = path.exists() or path.is_symlink()
                else:
                    stat = path.stat()
                    current = self._inside(path) and stat.st_size == item["size"] and stat.st_mtime_ns == item["mtime_ns"]
            except (OSError, ValueError):
                current = False
            item["current"] = current
            if not current:
                outdated.append(item["file"])
        outdated.extend(path.name for path in self._files() if path.name not in known)
        state = "outdated" if outdated else ("degraded" if any(item["status"] == "error" for item in inventory) else "ready")
        base.update(counts, status=state, indexed=True, inventory=inventory, outdated=outdated,
                    schema_version=self.SCHEMA_VERSION, current_books=len(fresh))
        return base, fresh

    def status(self) -> dict[str, Any]:
        return self._snapshot()[0]

    def _evidence(self, row, *, page_text=False):
        book_id, page = row["book_id"], row["page"]
        result = {"file": row["file"], "source": row["file"], "title": row["title"],
                  "page": page, "book_id": book_id, "source_sha256": book_id,
                  "page_sha256": row["page_sha256"], "text": row["text"],
                  "source_kind": "local_technical_book", "clinical_evidence": False,
                  "citation": f"{row['file']}, página PDF {page}, SHA-256 {book_id}",
                  "uri": f"ecosystem://books/{book_id}/pages/{page}"}
        if not page_text:
            result.update(chunk_id=row["chunk_id"], score=round(row["score"], 6))
        return result

    def query(self, query: str, top_k: int = 5) -> dict[str, Any]:
        if not isinstance(query, str) or len(query) > self.MAX_QUERY_CHARS:
            raise ValueError("Consulta deve ser texto com até 2000 caracteres.")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 10:
            raise ValueError("top_k deve ser inteiro entre 1 e 10.")
        # R677: índice pronto não transforma uma solicitação vazia em válida.
        # A guarda ocorre antes de ler inventário, hashes, PDFs ou SQLite.
        if not query.strip():
            return {"query": query, "status": "invalid_request", "reason_code": "empty_query",
                    "abstained": True, "evidence": [], "evidence_count": 0,
                    "source_kind": "local_technical_book", "clinical_evidence": False,
                    "method": "offline_lexical", "retrieval_executed": False,
                    "model_inference_executed": False, "training_executed": False,
                    "reason": "Consulta vazia; informe uma consulta não vazia para buscar suporte bibliográfico."}
        terms = sorted(self._tokens(query))
        if len(terms) > self.MAX_QUERY_TERMS:
            raise ValueError("Consulta excede o limite de 32 termos informativos.")
        status, fresh = self._snapshot()
        result = {"query": query, "abstained": True, "evidence": [], "evidence_count": 0,
                  "status": status["status"], "index_status": status,
                  "source_kind": "local_technical_book", "clinical_evidence": False,
                  "method": "offline_lexical", "reason": "Não há trechos atuais com suporte lexical à consulta."}
        if not fresh or not terms:
            return result
        term_marks = ",".join("?" for _ in terms)
        # Cada hash vem do inventário local validado, nunca de entrada SQL.
        fresh_marks = ",".join("?" for _ in fresh)
        fresh_files = [item["file"] for item in status["inventory"]
                       if item["current"] and item["status"] == "indexed"]
        file_marks = ",".join("?" for _ in fresh_files)
        sql = ("SELECT c.*,p.page_sha256,MIN(s.file) AS file,COUNT(DISTINCT t.term) AS matched "
               "FROM terms t JOIN chunks c ON c.chunk_id=t.chunk_id "
               "JOIN pages p ON p.book_id=c.book_id AND p.page=c.page "
               "JOIN sources s ON s.book_id=c.book_id AND s.status='indexed' "
               f"WHERE t.term IN ({term_marks}) AND c.book_id IN ({fresh_marks}) AND s.file IN ({file_marks}) "
               "GROUP BY c.chunk_id ORDER BY matched DESC,c.book_id,c.page,c.position LIMIT ?")
        try:
            with closing(self._connect(readonly=True)) as connection:
                candidates = [dict(row) for row in connection.execute(sql, (*terms, *sorted(fresh), *fresh_files, self.MAX_CANDIDATES))]
        except sqlite3.Error as exc:
            result.update(status="error", error=str(exc), reason="Índice indisponível; consulte status e execute indexar.")
            return result
        hits = []
        for row in candidates:
            row["title"] = Path(row["file"]).stem
            overlap = len(self._tokens(row["text"]) & set(terms))
            row["score"] = overlap / len(terms)
            # Um termo genérico compartilhado não sustenta uma pergunta com
            # vários termos: por exemplo, "estrela" pode ser apenas metáfora.
            required_overlap = min(2, len(terms))
            if overlap >= required_overlap and row["score"] >= 0.4:
                hits.append(row)
        hits.sort(key=lambda row: (-row["score"], row["book_id"], row["page"], row["position"]))
        evidence = [self._evidence(row) for row in hits[:top_k]]
        if evidence:
            result.update(abstained=False, evidence=evidence, evidence_count=len(evidence), reason=None)
        return result

    def read_page(self, book_id: str, page: int) -> dict[str, Any]:
        if not isinstance(book_id, str) or re.fullmatch(r"[a-f0-9]{64}", book_id) is None:
            raise ValueError("book_id deve ser um SHA-256 hexadecimal de 64 caracteres.")
        if isinstance(page, bool) or not isinstance(page, int) or not 1 <= page <= self.MAX_PAGES:
            raise ValueError("Página deve ser inteiro entre 1 e 2000.")
        status, fresh = self._snapshot()
        if book_id not in fresh:
            return {"status": status["status"] if status["status"] != "ready" else "not_found",
                    "book_id": book_id, "page": page, "error": "Livro ausente ou fonte desatualizada; indexe a biblioteca."}
        fresh_files = [item["file"] for item in status["inventory"]
                       if item["current"] and item["status"] == "indexed"]
        file_marks = ",".join("?" for _ in fresh_files)
        try:
            with closing(self._connect(readonly=True)) as connection:
                row = connection.execute(
                    "SELECT p.*,MIN(s.file) AS file FROM pages p JOIN sources s ON s.book_id=p.book_id "
                    f"WHERE p.book_id=? AND p.page=? AND s.status='indexed' AND s.file IN ({file_marks}) "
                    "GROUP BY p.book_id,p.page", (book_id, page, *fresh_files)).fetchone()
        except sqlite3.Error as exc:
            return {"status": "error", "book_id": book_id, "page": page, "error": str(exc)}
        if row is None:
            return {"status": "not_found", "book_id": book_id, "page": page, "error": "Página não encontrada."}
        row = dict(row)
        row["title"] = Path(row["file"]).stem
        return {"status": "ready", **self._evidence(row, page_text=True)}
