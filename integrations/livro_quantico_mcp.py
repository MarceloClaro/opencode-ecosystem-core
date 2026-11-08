"""MCP local, somente leitura, da fábrica do livro quântico.

Expõe o estado da obra, o catálogo E01–E18, a auditoria de counts, o status do
Lean 4, o resumo de repetições e o checklist de publicação. Não escreve no
repositório, não executa backend e não promove confiança.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from academic.bohm_feynman_panel import panel as reviewer_panel_data, questions as panel_questions_data
from scanners.bohm_scanner import bohm_scanner

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "educacao_quantica_bohm"
LIVRO = BOOK / "livro_pixel"
PDF = LIVRO / "LIVRO_3000_LAUDAS.pdf"
LEAN = ROOT / "livro-core" / "lean" / "QuantumTrails.lean"
REPETICOES = LIVRO / "RELATORIO_REPETICOES.md"
DADOS = BOOK / "dados_experimentos"


def _json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def audit_counts(counts: Any, shots: int | None = None) -> dict[str, Any]:
    """Valida counts e calcula probabilidades, EP e alertas. Puro, sem escrita."""
    blocos = counts if isinstance(counts, list) else [counts]
    resultados = []
    for i, bloco in enumerate(blocos):
        if not isinstance(bloco, dict):
            raise ValueError("cada bloco de counts deve ser um objeto {resultado: inteiro}")
        limpo: dict[str, int] = {}
        for chave, valor in bloco.items():
            if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
                raise ValueError("counts devem ser inteiros não negativos")
            limpo[str(chave)] = valor
        total = sum(limpo.values())
        esperado = shots if shots is not None else total
        probs = {k: v / total for k, v in limpo.items()} if total else {}
        ep = {k: (p * (1 - p) / total) ** 0.5 if total else 0.0 for k, p in probs.items()}
        alertas = []
        if total != esperado:
            alertas.append(f"bloco {i}: soma {total} != shots {esperado}")
        if total == 0:
            alertas.append(f"bloco {i}: counts vazios")
        resultados.append({
            "bloco": i,
            "total": total,
            "shots_esperados": esperado,
            "probabilidades": {k: round(v, 6) for k, v in probs.items()},
            "erro_padrao": {k: round(v, 6) for k, v in ep.items()},
            "alertas": alertas,
        })
    return {"ok": all(not r["alertas"] for r in resultados), "blocos": resultados}


def create_server() -> FastMCP:
    server = FastMCP("livro-quantico")
    readonly = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)

    @server.tool(name="book_status", annotations=readonly)
    def book_status() -> dict:
        """Retorna páginas, tamanho e metadados do PDF; não compila nem executa."""
        if not PDF.is_file():
            return {"status": "missing", "path": str(PDF)}
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(PDF))
            meta = reader.metadata or {}
            return {
                "status": "present",
                "path": str(PDF),
                "pages": len(reader.pages),
                "bytes": PDF.stat().st_size,
                "title": str(meta.get("/Title", "")),
                "author": str(meta.get("/Author", "")),
                "subject": str(meta.get("/Subject", "")),
            }
        except Exception as exc:  # noqa: BLE001 - diagnóstico local
            return {"status": "unreadable", "error": type(exc).__name__, "path": str(PDF)}

    @server.tool(name="list_experiments", annotations=readonly)
    def list_experiments() -> dict:
        """Lista os 18 experimentos e a última leitura simulada/real disponível."""
        itens = []
        for path in sorted(DADOS.glob("E[0-9][0-9].json")):
            d = _json(path)
            itens.append({
                "id": d.get("id", path.stem),
                "nome": d.get("nome", ""),
                "descricao": d.get("descricao", ""),
                "simulado": (d.get("simulado") or {}).get("leitura", ""),
                "real": (d.get("real") or {}).get("leitura", ""),
                "backend": (d.get("real") or {}).get("backend", ""),
                "task_ids": (d.get("real") or {}).get("task_ids", []),
            })
        return {"total": len(itens), "experimentos": itens}

    @server.tool(name="experiment_card", annotations=readonly)
    def experiment_card(exp_id: str) -> dict:
        """Retorna o JSON de um experimento E01–E18, se existir."""
        if not re.fullmatch(r"E(?:0[1-9]|1[0-8])", exp_id):
            raise ValueError("exp_id deve ser E01–E18")
        d = _json(DADOS / f"{exp_id}.json")
        return d or {"status": "missing", "id": exp_id}

    @server.tool(name="audit_counts", annotations=readonly)
    def audit_counts_tool(counts: Any, shots: int | None = None) -> dict:
        """Valida soma, probabilidades e erro padrão; não mede fidelidade de estado."""
        return audit_counts(counts, shots)

    @server.tool(name="lean_status", annotations=readonly)
    def lean_status() -> dict:
        """Inspeciona o arquivo Lean; não executa o compilador."""
        if not LEAN.is_file():
            return {"status": "missing", "path": str(LEAN)}
        texto = LEAN.read_text(encoding="utf-8")
        teoremas = re.findall(r"^theorem\s+([A-Za-z0-9_]+)", texto, re.M)
        return {
            "status": "present",
            "path": str(LEAN),
            "bytes": LEAN.stat().st_size,
            "theorems": teoremas,
            "theorem_count": len(teoremas),
            "has_sorry": bool(re.search(r"\bsorry\b", texto)),
            "has_admit": bool(re.search(r"\badmit\b", texto)),
            "command": "cd livro-core/lean && lake env lean QuantumTrails.lean",
            "executed": False,
        }

    @server.tool(name="repetition_summary", annotations=readonly)
    def repetition_summary() -> dict:
        """Lê o relatório de repetições e devolve os números principais."""
        if not REPETICOES.is_file():
            return {"status": "missing", "path": str(REPETICOES)}
        texto = REPETICOES.read_text(encoding="utf-8")
        def numero(padrao: str) -> int | None:
            m = re.search(padrao, texto)
            return int(m.group(1).replace(".", "")) if m else None
        return {
            "status": "present",
            "laudas": numero(r"Laudas analisadas: \*\*([\d.]+)\*\*"),
            "palavras": numero(r"Palavras \(texto limpo\): \*\*([\d.]+)\*\*"),
            "paragrafos_repetidos": numero(r"Parágrafos repetidos[^\n]*\*\*([\d.]+)\*\*"),
        }

    @server.tool(name="bohm_scan", annotations=readonly)
    def bohm_scan(text: str) -> dict:
        """Triagem lexical de temas bohmianos; não mede verdade ou mérito."""
        return bohm_scanner.scan_text(text)

    @server.tool(name="reviewer_panel", annotations=readonly)
    def reviewer_panel() -> dict:
        """Lista os 13 revisores, incluindo as personas Bohm e Feynman."""
        return reviewer_panel_data()

    @server.tool(name="panel_questions", annotations=readonly)
    def panel_questions(claim: str, rounds: int = 2) -> dict:
        """Gera perguntas dos 13 revisores; não gera respostas nem parecer."""
        return panel_questions_data(claim, rounds)

    @server.tool(name="publication_checklist", annotations=readonly)
    def publication_checklist() -> dict:
        """Verifica presença dos artefatos de publicação; não aprova a obra."""
        itens = {
            "licenca": (LIVRO / "LICENCA.md").is_file(),
            "eficacia": (LIVRO / "AVALIACAO_EFICACIA.md").is_file(),
            "piloto": (LIVRO / "PILOTO_SINTETICO.md").is_file(),
            "peer_review": (LIVRO / "PACOTE_PEER_REVIEW.md").is_file(),
            "ledger": (LIVRO / "LEDGER_AFIRMACOES.md").is_file(),
            "lean": LEAN.is_file(),
            "pdf": PDF.is_file(),
        }
        return {
            "itens": itens,
            "pronto_para_digital": all(itens.values()),
            "peer_review_externo": False,
            "eficacia_medida": False,
            "nota": "Presença de artefato não é aprovação; peer review e eficácia seguem pendentes.",
        }

    return server


if __name__ == "__main__":
    create_server().run(transport="stdio")
