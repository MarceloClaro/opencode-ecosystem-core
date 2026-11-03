"""MCP local, somente leitura, para matrizes públicas CAEd/SPAECE.

O servidor abre apenas dois bancos allowlisted de descritores. Não acessa os
diretórios de resultados estudantis, não recebe SQL/caminhos do chamador e não
executa os scripts do pacote Airam Veras.
"""
from __future__ import annotations

from contextlib import closing
from pathlib import Path
import os
import sqlite3
from typing import Any, Literal
from urllib.parse import quote

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations


CORE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AIRAM_ROOT = CORE_ROOT / "PROJETO 1" / "Airam veras"
MATRIX_DATABASES = {
    "CAEd": Path("caed-dados/dados/caed.sqlite"),
    "SPAECE": Path("spaece-dados/dados/spaece.sqlite"),
}
DESCRIPTOR_COLUMNS = {
    "CAEd": (
        "matriz_id", "documento_id", "ano_edicao", "componente", "etapa", "ano_serie",
        "tipo_instrumento", "codigo", "eixo_topico_extraido", "pagina_pdf",
        "fonte_arquivo", "fonte_url", "fonte_sha256", "descricao",
        "codigo_relacionado_publicado", "descricao_relacionada_publicada",
    ),
    "SPAECE": (
        "matriz_id", "sistema", "componente", "etapa", "ano_serie", "codigo",
        "eixo_topico_extraido", "subeixo", "fonte_url", "fonte_arquivo", "pagina_pdf",
        "fonte_sha256", "vigencia_2026", "descricao",
    ),
}
MAX_LIMIT = 100
MAX_QUERY_CHARS = 120
MAX_SEARCH_SCAN = 50_000


class MatrixSourceUnavailable(RuntimeError):
    """A fonte local allowlisted não está presente ou não tem o schema esperado."""


def _checked_integer(value: int, name: str, *, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{name} deve estar entre {minimum} e {maximum}.")
    return value


class MatrixCorpus:
    """Fachada de leitura sobre os dois bancos documentais autorizados."""

    def __init__(self, root: str | Path | None = None) -> None:
        configured = root or os.environ.get("AIRAM_VERAS_ROOT") or DEFAULT_AIRAM_ROOT
        self.root = Path(configured).expanduser().resolve()

    def _database_path(self, system: str) -> Path:
        try:
            relative = MATRIX_DATABASES[system]
        except KeyError as exc:
            raise ValueError("Sistema deve ser CAEd ou SPAECE.") from exc
        candidate = self.root / relative
        current = candidate
        while current != self.root:
            if current.is_symlink():
                raise ValueError("Symlink não permitido em fonte de matriz.")
            current = current.parent
        path = candidate.resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("A fonte está fora do corpus allowlisted.")
        if not path.is_file():
            raise MatrixSourceUnavailable(f"Banco local indisponível para {system}.")
        return path

    def _connect(self, system: str) -> sqlite3.Connection:
        path = self._database_path(system)
        uri = f"file:{quote(str(path))}?mode=ro"
        connection = sqlite3.connect(uri, uri=True, timeout=2.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only=ON")
        return connection

    @staticmethod
    def _row(row: sqlite3.Row) -> dict[str, Any]:
        return {key: row[key] for key in row.keys()}

    def source_status(self) -> dict[str, Any]:
        systems = {}
        for system, relative in MATRIX_DATABASES.items():
            candidate = self.root / relative
            path = candidate.resolve()
            systems[system] = {
                "available": (
                    not candidate.is_symlink()
                    and path.is_relative_to(self.root)
                    and path.is_file()
                ),
                "database": relative.as_posix(),
                "read_only": True,
            }
        available = [name for name, value in systems.items() if value["available"]]
        return {
            "status": "available" if len(available) == len(systems) else "partial",
            "root": self.root.as_posix(),
            "systems": systems,
            "restricted_results_accessed": False,
            "scripts_executed": False,
        }

    def list_matrices(
        self,
        *,
        system: Literal["CAEd", "SPAECE", "all"] = "all",
        edition_year: int | None = None,
        stage: str | None = None,
        component: str | None = None,
        grade: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        limit = _checked_integer(limit, "limit", minimum=1, maximum=MAX_LIMIT)
        offset = _checked_integer(offset, "offset", minimum=0, maximum=100_000)
        if edition_year is not None:
            edition_year = _checked_integer(edition_year, "edition_year", minimum=1900, maximum=2200)
        if grade is not None:
            grade = _checked_integer(grade, "grade", minimum=1, maximum=20)
        if system not in {"CAEd", "SPAECE", "all"}:
            raise ValueError("Sistema deve ser CAEd, SPAECE ou all.")

        systems = list(MATRIX_DATABASES) if system == "all" else [system]
        matrices: list[dict[str, Any]] = []
        unavailable: list[str] = []
        for selected in systems:
            try:
                with closing(self._connect(selected)) as connection:
                    if selected == "CAEd":
                        sql = """SELECT matriz_id, ano_edicao AS edition_year, etapa AS stage,
                                        ano_serie AS grade, componente AS component,
                                        tipo_instrumento AS instrument_type,
                                        COUNT(*) AS descritor_count,
                                        MIN(fonte_arquivo) AS source_file,
                                        MIN(fonte_url) AS source_url
                                 FROM descritores WHERE 1=1"""
                        parameters: list[Any] = []
                        if edition_year is not None:
                            sql += " AND ano_edicao = ?"
                            parameters.append(edition_year)
                        if stage:
                            sql += " AND etapa = ?"
                            parameters.append(stage)
                        if component:
                            sql += " AND componente = ?"
                            parameters.append(component)
                        if grade is not None:
                            sql += " AND ano_serie = ?"
                            parameters.append(grade)
                        sql += " GROUP BY matriz_id, ano_edicao, etapa, ano_serie, componente, tipo_instrumento"
                        sql += " ORDER BY ano_edicao, matriz_id LIMIT ? OFFSET ?"
                        parameters.extend([limit + 1, offset])
                    else:
                        sql = """SELECT matriz_id, NULL AS edition_year, etapa AS stage,
                                        ano_serie AS grade, componente AS component,
                                        NULL AS instrument_type, COUNT(*) AS descritor_count,
                                        MIN(fonte_arquivo) AS source_file,
                                        MIN(fonte_url) AS source_url
                                 FROM descritores WHERE 1=1"""
                        parameters = []
                        # O banco SPAECE antigo não registra ano da edição; filtro
                        # temporal nele não pode ser inferido a partir da série.
                        if edition_year is not None:
                            sql += " AND 1=0"
                        if stage:
                            sql += " AND etapa = ?"
                            parameters.append(stage)
                        if component:
                            sql += " AND componente = ?"
                            parameters.append(component)
                        if grade is not None:
                            sql += " AND ano_serie = ?"
                            parameters.append(grade)
                        sql += " GROUP BY matriz_id, etapa, ano_serie, componente"
                        sql += " ORDER BY matriz_id LIMIT ? OFFSET ?"
                        parameters.extend([limit + 1, offset])
                    rows = [self._row(row) for row in connection.execute(sql, parameters)]
                    if len(rows) > limit:
                        rows = rows[:limit]
                        more = True
                    else:
                        more = False
                    matrices.extend({"system": selected, **row} for row in rows)
                    if more:
                        unavailable.append(f"{selected}:additional_page")
            except MatrixSourceUnavailable:
                unavailable.append(selected)

        matrices.sort(key=lambda item: (item.get("edition_year") or 0, item["system"], item["matriz_id"]))
        return {
            "status": "partial" if unavailable else "ok",
            "matrices": matrices,
            "limit": limit,
            "offset": offset,
            "coverage_notes": unavailable,
            "edition_year_missing_is_not_inferred": True,
        }

    def get_matrix(
        self,
        matrix_id: str,
        *,
        system: Literal["CAEd", "SPAECE"],
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        if not isinstance(matrix_id, str) or not 1 <= len(matrix_id) <= 160:
            raise ValueError("matrix_id deve conter de 1 a 160 caracteres.")
        limit = _checked_integer(limit, "limit", minimum=1, maximum=MAX_LIMIT)
        offset = _checked_integer(offset, "offset", minimum=0, maximum=100_000)
        with closing(self._connect(system)) as connection:
            where = "matriz_id = ?"
            if system == "CAEd":
                summary_sql = """SELECT matriz_id, ano_edicao AS edition_year, etapa AS stage,
                                        ano_serie AS year_serie, componente AS component,
                                        tipo_instrumento AS instrument_type,
                                        COUNT(*) AS descriptor_count,
                                        MIN(fonte_arquivo) AS source_file,
                                        MIN(fonte_url) AS source_url
                                 FROM descritores WHERE matriz_id = ?
                                 GROUP BY matriz_id, ano_edicao, etapa, ano_serie, componente,
                                          tipo_instrumento"""
            else:
                summary_sql = """SELECT matriz_id, NULL AS edition_year, etapa AS stage,
                                        ano_serie AS year_serie, componente AS component,
                                        NULL AS instrument_type, COUNT(*) AS descriptor_count,
                                        MIN(fonte_arquivo) AS source_file,
                                        MIN(fonte_url) AS source_url
                                 FROM descritores WHERE matriz_id = ?
                                 GROUP BY matriz_id, etapa, ano_serie, componente"""
            summary_row = connection.execute(summary_sql, (matrix_id,)).fetchone()
            count = connection.execute(
                f"SELECT COUNT(*) FROM descritores WHERE {where}", (matrix_id,)
            ).fetchone()[0]
            columns = ", ".join(DESCRIPTOR_COLUMNS[system])
            rows = connection.execute(
                f"SELECT {columns} FROM descritores WHERE {where} ORDER BY codigo LIMIT ? OFFSET ?",
                (matrix_id, limit + 1, offset),
            ).fetchall()
        more = len(rows) > limit
        records = [self._row(row) for row in rows[:limit]]
        return {
            "status": "ok" if count else "not_found",
            "system": system,
            "matrix_id": matrix_id,
            "matrix": self._row(summary_row) if summary_row is not None else None,
            "total_descriptors": count,
            "descriptors": records,
            "limit": limit,
            "offset": offset,
            "more_available": more,
            "source_scope": "public matrix metadata only",
        }

    def search_descriptors(
        self,
        query: str,
        *,
        system: Literal["CAEd", "SPAECE", "all"] = "all",
        edition_year: int | None = None,
        component: str | None = None,
        grade: int | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        if not isinstance(query, str) or not 2 <= len(query.strip()) <= MAX_QUERY_CHARS:
            raise ValueError(f"query deve conter de 2 a {MAX_QUERY_CHARS} caracteres.")
        limit = _checked_integer(limit, "limit", minimum=1, maximum=MAX_LIMIT)
        if edition_year is not None:
            edition_year = _checked_integer(edition_year, "edition_year", minimum=1900, maximum=2200)
        if grade is not None:
            grade = _checked_integer(grade, "grade", minimum=1, maximum=20)
        if system not in {"CAEd", "SPAECE", "all"}:
            raise ValueError("Sistema deve ser CAEd, SPAECE ou all.")

        needle = query.strip().casefold()
        selected_systems = list(MATRIX_DATABASES) if system == "all" else [system]
        results: list[dict[str, Any]] = []
        missing: list[str] = []
        scan_limited = False
        for selected in selected_systems:
            try:
                with closing(self._connect(selected)) as connection:
                    columns = ", ".join(DESCRIPTOR_COLUMNS[selected])
                    sql = f"SELECT {columns} FROM descritores WHERE 1=1"
                    parameters: list[Any] = []
                    if selected == "CAEd":
                        if edition_year is not None:
                            sql += " AND ano_edicao = ?"
                            parameters.append(edition_year)
                    else:
                        if edition_year is not None:
                            sql += " AND 1=0"
                    if component:
                        sql += " AND componente = ?"
                        parameters.append(component)
                    if grade is not None:
                        sql += " AND ano_serie = ?"
                        parameters.append(grade)
                    sql += " ORDER BY matriz_id, codigo LIMIT ?"
                    parameters.append(MAX_SEARCH_SCAN + 1)
                    rows = connection.execute(sql, parameters).fetchall()
                    if len(rows) > MAX_SEARCH_SCAN:
                        rows = rows[:MAX_SEARCH_SCAN]
                        scan_limited = True
                    for row in rows:
                        item = self._row(row)
                        description = item.get("descricao") or item.get("descricao_extraida") or ""
                        if needle in str(description).casefold():
                            results.append({"system": selected, **item})
            except MatrixSourceUnavailable:
                missing.append(selected)

        results.sort(key=lambda item: (item["system"], item.get("matriz_id", ""), item.get("codigo", "")))
        more = len(results) > limit or scan_limited
        return {
            "status": "partial" if missing or scan_limited else "ok",
            "matches": results[:limit],
            "limit": limit,
            "more_available": more,
            "missing_sources": missing,
            "scan_limited": scan_limited,
            "edition_year_missing_is_not_inferred": True,
        }


def create_server(corpus: MatrixCorpus | None = None, adapter=None) -> FastMCP:
    corpus = corpus or MatrixCorpus()
    if adapter is None:
        from integrations.airamveras_adapter import AiramVerasAdapter
        adapter = AiramVerasAdapter(corpus)
    server = FastMCP("caed-spaece-data")
    readonly = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)

    @server.tool(name="source_status", annotations=readonly)
    def source_status() -> dict:
        """Verifica somente a presença dos dois bancos públicos allowlisted."""
        return corpus.source_status()

    @server.tool(name="list_matrices", annotations=readonly)
    def list_matrices(
        system: Literal["CAEd", "SPAECE", "all"] = "all",
        edition_year: int | None = None,
        stage: str | None = None,
        component: str | None = None,
        grade: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """Lista matriz/edição/etapa/série/componente; não presume vigência."""
        return corpus.list_matrices(system=system, edition_year=edition_year, stage=stage,
                                    component=component, grade=grade, limit=limit, offset=offset)

    @server.tool(name="get_matrix", annotations=readonly)
    def get_matrix(
        matrix_id: str,
        system: Literal["CAEd", "SPAECE"],
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """Recupera descritores de uma matriz identificada por seu ID composto."""
        return corpus.get_matrix(matrix_id, system=system, limit=limit, offset=offset)

    @server.tool(name="search_descriptors", annotations=readonly)
    def search_descriptors(
        query: str,
        system: Literal["CAEd", "SPAECE", "all"] = "all",
        edition_year: int | None = None,
        component: str | None = None,
        grade: int | None = None,
        limit: int = 50,
    ) -> dict:
        """Busca texto de descritores sem SQL fornecido pelo chamador."""
        return corpus.search_descriptors(query, system=system, edition_year=edition_year,
                                         component=component, grade=grade, limit=limit)

    @server.tool(name="export_matrix_bundle", annotations=readonly)
    def export_matrix_bundle(
        matrix_id: str,
        system: Literal["CAEd", "SPAECE"],
        format: Literal["records", "json", "jsonl", "csv"] = "records",
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """Emite um bundle versionado em records/JSON/JSONL/CSV, sem escrever arquivos."""
        return adapter.export_matrix_bundle(matrix_id, system=system, format=format,
                                             limit=limit, offset=offset)

    return server


if __name__ == "__main__":
    create_server().run(transport="stdio")
