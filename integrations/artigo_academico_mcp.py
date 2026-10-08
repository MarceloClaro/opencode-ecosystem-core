# -*- coding: utf-8 -*-
"""
Artigo Acadêmico MCP Server — Pipeline de artigo científico ABNT
================================================================
Expõe as ferramentas do pipeline de artigo acadêmico (LaTeX modular,
BibTeX auditado, DOCX ABNT, deck MIRA) via MCP, para a orquestração do Core.

Ferramentas:
  - auditar_referencia:  Verifica DOI na fonte primária (Crossref) antes de citar
  - verificar_citacoes:  Cruza chaves \\cite do LaTeX com entradas do .bib (undefined/unused)
  - pipeline_status:     Inventaria artefatos do artigo (existência + SHA-256)
  - validar_deck:        Valida deck HTML (estrutura + smoke test de JS se node existir)

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import os
import sys
import re
import json
import glob
import asyncio
import hashlib
import logging
import secrets
import urllib.request
import urllib.parse
import subprocess
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any, Mapping, Dict

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Adiciona a raiz do projeto ao sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Imports locais após o bootstrap permitem executar este arquivo standalone.
from integrations.mcp_validation import validate_arguments  # noqa: E402

try:
    from mcp.types import CallToolResult
except ImportError:
    class CallToolResult(list[TextContent]):
        def __init__(
            self, *, content: list[TextContent], isError: bool = False, **extra_data: Any,
        ) -> None:
            super().__init__(content)
            self.content = list(content)
            self.isError = isError
            for key, value in extra_data.items():
                setattr(self, key, value)

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("artigo-academico-mcp")


def _text_content(text: str) -> list[TextContent]:
    return [TextContent(type="text", text=text)]


def _call_tool_result(payload: Dict[str, Any]) -> CallToolResult | list[TextContent]:
    return _text_content(json.dumps(payload, ensure_ascii=False, indent=2))


def _mcp_error(message: str) -> CallToolResult | list[TextContent]:
    return _text_content(json.dumps({"ok": False, "error": message}, ensure_ascii=False))


app = Server("artigo-academico-mcp")

TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "auditar_referencia": {
        "type": "object",
        "properties": {
            "doi": {"type": "string", "description": "DOI a verificar (com ou sem prefixo https://doi.org/)"},
        },
        "required": ["doi"],
    },
    "verificar_citacoes": {
        "type": "object",
        "properties": {
            "diretorio": {"type": "string", "description": "Diretório do artigo com .tex e .bib"},
        },
        "required": ["diretorio"],
    },
    "pipeline_status": {
        "type": "object",
        "properties": {
            "diretorio": {"type": "string", "description": "Diretório do artigo a inventariar"},
        },
        "required": ["diretorio"],
    },
    "validar_deck": {
        "type": "object",
        "properties": {
            "caminho_html": {"type": "string", "description": "Caminho do deck HTML MIRA"},
        },
        "required": ["caminho_html"],
    },
    "registrar_triagem": {
        "type": "object",
        "properties": {
            "diretorio": {"type": "string", "description": "Diretório do artigo (recebe triagem.jsonl)"},
            "titulo": {"type": "string", "description": "Título do estudo triado"},
            "fonte": {"type": "string", "description": "Base de origem (ex.: SciELO, PubMed)"},
            "decisao": {"type": "string", "description": "incluir, excluir ou duvida"},
            "motivo": {"type": "string", "description": "Justificativa da decisão em 1 frase"},
            "doi": {"type": "string", "description": "DOI do estudo, quando existir"},
            "etapa": {"type": "string", "description": "title_abstract (padrão) ou full_text"},
            "protocolo": {"type": "string", "description": "ID do protocolo de revisão"},
        },
        "required": ["diretorio", "titulo", "fonte", "decisao", "motivo"],
    },
    "emitir_manifesto": {
        "type": "object",
        "properties": {
            "diretorio": {"type": "string", "description": "Diretório do artigo a empacotar"},
            "versao": {"type": "string", "description": "Versão do release (padrão 1.0)"},
        },
        "required": ["diretorio"],
    },
    "auditar_forca_alegacao": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Texto do manuscrito a triar (Contrato de Força de Alegação)"},
        },
        "required": ["text"],
    },
    "estimar_did": {
        "type": "object",
        "properties": {
            "csv_texto": {"type": "string", "description": "Conteúdo CSV (painel longo, teto de 50000 linhas)"},
            "coluna_y": {"type": "string", "description": "Coluna do desfecho numérico"},
            "coluna_tempo": {"type": "string", "description": "Coluna do período (0/1)"},
            "coluna_tratado": {"type": "string", "description": "Coluna do tratamento (0/1)"},
            "n_perm": {"type": "integer", "description": "Permutações para o p-valor (padrão 199)"},
        },
        "required": ["csv_texto", "coluna_y", "coluna_tempo", "coluna_tratado"],
    },
    "estimar_iv": {
        "type": "object",
        "properties": {
            "csv_texto": {"type": "string", "description": "Conteúdo CSV (teto de 50000 linhas)"},
            "coluna_y": {"type": "string", "description": "Coluna do desfecho"},
            "coluna_x": {"type": "string", "description": "Coluna da exposição endógena"},
            "coluna_z": {"type": "string", "description": "Coluna do instrumento"},
        },
        "required": ["csv_texto", "coluna_y", "coluna_x", "coluna_z"],
    },
    "atualizar_bayes": {
        "type": "object",
        "properties": {
            "csv_texto": {"type": "string", "description": "Conteúdo CSV com a coluna de medida"},
            "coluna": {"type": "string", "description": "Coluna da medida"},
            "mu0": {"type": "number", "description": "Média do prior"},
            "tau0": {"type": "number", "description": "Desvio-padrão do prior (positivo)"},
        },
        "required": ["csv_texto", "coluna", "mu0", "tau0"],
    },
    "icc_cluster": {
        "type": "object",
        "properties": {
            "csv_texto": {"type": "string", "description": "Conteúdo CSV (teto de 50000 linhas)"},
            "coluna_y": {"type": "string", "description": "Coluna da medida"},
            "coluna_grupo": {"type": "string", "description": "Coluna do grupo/cluster"},
        },
        "required": ["csv_texto", "coluna_y", "coluna_grupo"],
    },
}

TOOL_DESCRIPTIONS = {
    "auditar_referencia": "Verifica um DOI na fonte primária (Crossref) e retorna título, autores, periódico e ano — antes de citar. DOI sem metadados confirmáveis deve ser marcado [NÃO VERIFICADA].",
    "verificar_citacoes": "Cruza chaves \\cite/\\citeonline dos .tex com entradas @ do .bib: lista citações indefinidas (sem entrada) e entradas não citadas. Exige undefined=0 para submissão.",
    "pipeline_status": "Inventaria os artefatos do pipeline (main.tex, módulos, .bib, .pdf, .docx, deck, roteiro) com existência e SHA-256 — cadeia de custódia da entrega.",
    "validar_deck": "Valida deck HTML MIRA: conta slides, verifica navegação e roda o smoke test de JS (classe R580) quando node existir.",
    "registrar_triagem": "Registra decisão de triagem por estudo em triagem.jsonl, conforme o contrato screening-decision v4.1 (etapa title_abstract/full_text; decisão incluir/excluir/duvida) — triagem PRISMA auditável.",
    "emitir_manifesto": "Emite MANIFESTO.json do artigo (artefatos + hashes + referências), conforme o contrato release-manifest v4.1 — pacote replicável da entrega.",
    "auditar_forca_alegacao": "Triagem heurística de overclaim pelo Contrato de Força de Alegação (research/claim_strength): sinaliza causação/efeito/eficácia e absolutos sem mitigador próximo. Não prova ausência de overclaim; decisão final é humana.",
    "estimar_did": "Dupla diferença com p por permutação sobre CSV inline. Suposição de tendências paralelas declarada, não testada.",
    "estimar_iv": "IV-2SLS manual sobre CSV inline com F do primeiro estágio; F<10 = instrumento fraco, sem alegação causal.",
    "atualizar_bayes": "Posterior Normal-Normal conjugada com prior explícito registrado e IC crível; crença atualizada, não prova.",
    "icc_cluster": "ICC por ANOVA de efeitos aleatórios sobre CSV inline; hierarquia importa se ICC>=0.1.",
}


def _tool_auditar_referencia(doi: str) -> Dict[str, Any]:
    doi = doi.strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    if not re.match(r"^10\.\d{4,}/", doi):
        return {"ok": False, "error": "DOI com formato inválido (esperado 10.xxxx/...)."}
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    req = urllib.request.Request(url, headers={"User-Agent": "opencode-ecosystem-core/artigo-academico-mcp", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8", "ignore"))
    except Exception as exc:
        logger.debug("Falha Crossref: %s", exc)
        return {"ok": False, "error": f"Crossref inacessível ou DOI não resolvido: {type(exc).__name__}."}
    msg = data.get("message", {})
    autores = [f"{a.get('family', '')}, {a.get('given', '')}".strip(", ") for a in msg.get("author", [])]
    return {
        "ok": True,
        "doi": msg.get("DOI", doi),
        "titulo": (msg.get("title") or [""])[0],
        "autores": autores,
        "periodico": (msg.get("container-title") or [""])[0],
        "volume": msg.get("volume", ""),
        "edicao": msg.get("issue", ""),
        "paginas": msg.get("page", ""),
        "ano": ((msg.get("published-print") or msg.get("published-online") or {}).get("date-parts") or [[None]])[0][0],
        "veredito": "VERIFICADA em fonte primária (Crossref).",
    }


def _tool_verificar_citacoes(diretorio: str) -> Dict[str, Any]:
    if not os.path.isdir(diretorio):
        return {"ok": False, "error": f"Diretório inexistente: {diretorio}."}
    citados: set[str] = set()
    for path in glob.glob(os.path.join(diretorio, "**", "*.tex"), recursive=True):
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                texto = fh.read()
        except OSError:
            continue
        for m in re.findall(r"\\cite(?:online|alp|alt|author|year)?\{([^}]*)\}", texto):
            citados.update(k.strip() for k in m.split(",") if k.strip())
    entradas: set[str] = set()
    for path in glob.glob(os.path.join(diretorio, "**", "*.bib"), recursive=True):
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                texto = fh.read()
        except OSError:
            continue
        entradas.update(re.findall(r"@\w+\{([^,\s]+)\s*,", texto))
    indefinidas = sorted(citados - entradas)
    nao_citadas = sorted(entradas - citados)
    return {
        "ok": True,
        "citacoes_encontradas": len(citados),
        "entradas_bib": len(entradas),
        "indefinidas": indefinidas,
        "nao_citadas": nao_citadas,
        "pronto_para_submissao": not indefinidas,
    }


def _sha256_corto(path: str) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for bloco in iter(lambda: fh.read(65536), b""):
                h.update(bloco)
    except OSError:
        return ""
    return h.hexdigest()[:16]


def _tool_pipeline_status(diretorio: str) -> Dict[str, Any]:
    if not os.path.isdir(diretorio):
        return {"ok": False, "error": f"Diretório inexistente: {diretorio}."}
    padroes = ["main.tex", "referencias.bib", "modulos/*.tex", "*.pdf", "*.docx",
               "mira_deck/*.html", "mira_deck/*.md", "gerar_*.py"]
    artefatos = []
    for pad in padroes:
        achados = sorted(glob.glob(os.path.join(diretorio, pad)))
        for a in achados:
            artefatos.append({
                "arquivo": os.path.relpath(a, diretorio),
                "bytes": os.path.getsize(a),
                "sha256": _sha256_corto(a),
            })
    return {"ok": True, "diretorio": diretorio, "artefatos": artefatos, "total": len(artefatos)}


def _tool_registrar_triagem(diretorio: str, titulo: str, fonte: str, decisao: str,
                            motivo: str, doi: str = "", etapa: str = "title_abstract",
                            protocolo: str = "artigo-gap") -> Dict[str, Any]:
    if not os.path.isdir(diretorio):
        return {"ok": False, "error": f"Diretório inexistente: {diretorio}."}
    mapa = {"incluir": "include", "excluir": "exclude", "duvida": "uncertain",
            "include": "include", "exclude": "exclude", "uncertain": "uncertain"}
    dec = mapa.get((decisao or "").strip().lower(), "")
    if not dec:
        return {"ok": False, "error": "decisao deve ser incluir, excluir ou duvida."}
    if etapa not in ("title_abstract", "full_text"):
        return {"ok": False, "error": "etapa deve ser title_abstract ou full_text."}
    if doi.strip():
        study_id = "DOI:" + re.sub(r"^https?://(dx\.)?doi\.org/", "", doi.strip())
    else:
        study_id = "TIT:" + hashlib.sha1(titulo.encode("utf-8")).hexdigest()[:12].upper()
    registro = {
        "schema_version": "1.0",
        "decision_id": "SCR-" + secrets.token_hex(6).upper(),
        "protocol_id": protocolo,
        "study_id": study_id,
        "stage": etapa,
        "reviewer": "marceloclaro",
        "decision": dec,
        "reason": motivo,
        "decided_at": datetime.now(timezone.utc).isoformat(),
        "human_decision": True,
    }
    caminho = os.path.join(diretorio, "triagem.jsonl")
    try:
        with open(caminho, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(registro, ensure_ascii=False) + "\n")
    except OSError as exc:
        return {"ok": False, "error": f"Falha ao gravar triagem.jsonl: {exc}."}
    return {"ok": True, "registro": registro, "arquivo": caminho}


def _tool_emitir_manifesto(diretorio: str, versao: str = "1.0") -> Dict[str, Any]:
    if not os.path.isdir(diretorio):
        return {"ok": False, "error": f"Diretório inexistente: {diretorio}."}
    base = _tool_pipeline_status(diretorio)
    if not base.get("ok"):
        return base
    chaves_bib: list[str] = []
    for path in glob.glob(os.path.join(diretorio, "**", "*.bib"), recursive=True):
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                chaves_bib.extend(re.findall(r"@\w+\{([^,\s]+)\s*,", fh.read()))
        except OSError:
            continue
    commit = ""
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, timeout=10, cwd=diretorio)
        if proc.returncode == 0:
            commit = proc.stdout.strip()
    except Exception:
        commit = ""
    manifesto = {
        "schema_version": "1.0",
        "release_id": "REL-" + datetime.now(timezone.utc).strftime("%Y%m%d") + "-"
                        + hashlib.sha1(diretorio.encode()).hexdigest()[:6].upper(),
        "version": versao,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "core_reference_commit": commit,
        "artifacts": base["artefatos"],
        "sbom": {},
        "tests": {},
        "claims": [],
    }
    manifesto["referencias_bib"] = sorted(set(chaves_bib))
    caminho = os.path.join(diretorio, "MANIFESTO.json")
    try:
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump(manifesto, fh, ensure_ascii=False, indent=2)
    except OSError as exc:
        return {"ok": False, "error": f"Falha ao gravar MANIFESTO.json: {exc}."}
    return {"ok": True, "arquivo": caminho,
            "artefatos": len(base["artefatos"]), "referencias": len(manifesto["referencias_bib"])}


class _DeckParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.slides = 0
        self.scripts = 0
        self.in_script = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "section":
            self.slides += 1
        if tag == "script":
            self.scripts += 1
            self.in_script = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.in_script = False


def _tool_validar_deck(caminho_html: str) -> Dict[str, Any]:
    if not os.path.isfile(caminho_html):
        return {"ok": False, "error": f"Arquivo inexistente: {caminho_html}."}
    with open(caminho_html, encoding="utf-8", errors="ignore") as fh:
        html = fh.read()
    parser = _DeckParser()
    try:
        parser.feed(html)
    except Exception as exc:
        return {"ok": False, "error": f"HTML malformado: {type(exc).__name__}."}
    resultado: Dict[str, Any] = {
        "ok": True, "slides": parser.slides, "scripts_inline": parser.scripts,
        "tem_navegacao": "navegar" in html and "keydown" in html,
        "tem_progresso": 'id="barra"' in html or 'id="fill"' in html,
        "smoke": "nao_executado",
    }
    repo = REPO_ROOT
    stub = os.path.join(repo, ".opencode", "hooks", "smoke_dom_stub.js")
    node_ok = False
    try:
        node_ok = subprocess.run(["node", "--version"], capture_output=True, timeout=10).returncode == 0
    except Exception:
        node_ok = False
    if node_ok and os.path.isfile(stub):
        try:
            proc = subprocess.run(["node", stub, caminho_html], capture_output=True,
                                  text=True, timeout=60, cwd=repo)
            saida = (proc.stdout + proc.stderr)[-500:]
            resultado["smoke"] = "SMOKE_OK" if "SMOKE_OK" in saida else f"SMOKE_FAIL: {saida.strip()[:200]}"
        except Exception as exc:
            resultado["smoke"] = f"nao_executado: {type(exc).__name__}"
    return resultado


@app.list_tools()
async def list_tools() -> list[Tool]:
    ferramentas = []
    for nome, esquema in TOOL_SCHEMAS.items():
        ferramentas.append(Tool(name=nome, description=TOOL_DESCRIPTIONS[nome], inputSchema=esquema))
    return ferramentas


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult | list[TextContent]:
    supported_tools = {"auditar_referencia", "verificar_citacoes", "pipeline_status", "validar_deck",
                         "registrar_triagem", "emitir_manifesto", "auditar_forca_alegacao",
                         "estimar_did", "estimar_iv", "atualizar_bayes", "icc_cluster"}
    if not isinstance(name, str) or name not in supported_tools:
        return _mcp_error(f"Ferramenta desconhecida: {name}")
    if not isinstance(arguments, Mapping):
        return _mcp_error("Payload inválido: argumentos devem ser um objeto.")
    validation = validate_arguments(name, dict(arguments), TOOL_SCHEMAS[name])
    if not validation["valid"]:
        return _mcp_error("Payload inválido: " + "; ".join(validation["errors"]))

    try:
        if name == "auditar_referencia":
            doi = arguments.get("doi", "")
            if not isinstance(doi, str) or not doi.strip():
                return _mcp_error("Payload inválido: 'doi' deve ser uma string não vazia.")
            return _call_tool_result(_tool_auditar_referencia(doi))
        if name == "verificar_citacoes":
            diretorio = arguments.get("diretorio", "")
            if not isinstance(diretorio, str) or not diretorio.strip():
                return _mcp_error("Payload inválido: 'diretorio' deve ser uma string não vazia.")
            return _call_tool_result(_tool_verificar_citacoes(diretorio))
        if name == "pipeline_status":
            diretorio = arguments.get("diretorio", "")
            if not isinstance(diretorio, str) or not diretorio.strip():
                return _mcp_error("Payload inválido: 'diretorio' deve ser uma string não vazia.")
            return _call_tool_result(_tool_pipeline_status(diretorio))
        if name == "validar_deck":
            caminho = arguments.get("caminho_html", "")
            if not isinstance(caminho, str) or not caminho.strip():
                return _mcp_error("Payload inválido: 'caminho_html' deve ser uma string não vazia.")
            return _call_tool_result(_tool_validar_deck(caminho))
        if name == "registrar_triagem":
            req = ["diretorio", "titulo", "fonte", "decisao", "motivo"]
            if any(not isinstance(arguments.get(k, ""), str) or not arguments.get(k, "").strip() for k in req):
                return _mcp_error("Payload inválido: diretorio/titulo/fonte/decisao/motivo devem ser strings não vazias.")
            return _call_tool_result(_tool_registrar_triagem(
                arguments["diretorio"], arguments["titulo"], arguments["fonte"],
                arguments["decisao"], arguments["motivo"],
                arguments.get("doi", "") if isinstance(arguments.get("doi", ""), str) else "",
                arguments.get("etapa", "title_abstract") if isinstance(arguments.get("etapa", ""), str) else "title_abstract",
                arguments.get("protocolo", "artigo-gap") if isinstance(arguments.get("protocolo", ""), str) else "artigo-gap"))
        if name == "emitir_manifesto":
            diretorio = arguments.get("diretorio", "")
            if not isinstance(diretorio, str) or not diretorio.strip():
                return _mcp_error("Payload inválido: 'diretorio' deve ser uma string não vazia.")
            versao = arguments.get("versao", "1.0")
            if not isinstance(versao, str):
                return _mcp_error("Payload inválido: 'versao' deve ser uma string.")
            return _call_tool_result(_tool_emitir_manifesto(diretorio, versao))
        if name == "auditar_forca_alegacao":
            texto = arguments.get("text", "")
            if not isinstance(texto, str) or not texto.strip():
                return _mcp_error("Payload inválido: 'text' deve ser uma string não vazia.")
            try:
                from research.claim_strength.guard import auditar
            except Exception as exc:
                return _mcp_error(f"Guarda indisponível: {type(exc).__name__}.")
            try:
                return _call_tool_result(auditar(texto))
            except Exception as exc:
                logger.debug("Falha em auditar_forca_alegacao: %s", exc, exc_info=True)
                return _mcp_error(f"Falha na triagem: {type(exc).__name__}.")
        if name in ("estimar_did", "estimar_iv", "atualizar_bayes", "icc_cluster"):
            return _call_tool_result(_tool_quantitativo(name, arguments))
    except Exception as exc:
        logger.debug("Falha em %s: %s", name, exc, exc_info=True)
        return _mcp_error(f"Falha na execução: {type(exc).__name__}.")
    return _mcp_error("Ferramenta desconhecida.")


_LINHAS_MAX_CSV = 50000


def _csv_para_df(csv_texto: str):
    """Parseia CSV inline com teto de linhas (fail-closed)."""
    if not isinstance(csv_texto, str) or not csv_texto.strip():
        raise ValueError("csv_texto deve ser uma string CSV não vazia.")
    linhas = csv_texto.strip().splitlines()
    if len(linhas) > _LINHAS_MAX_CSV + 1:
        raise ValueError(f"CSV excede o teto de {_LINHAS_MAX_CSV} linhas.")
    try:
        import pandas as pd
        from io import StringIO
    except ImportError as exc:
        raise ValueError("pandas indisponível no servidor MCP.") from exc
    try:
        df = pd.read_csv(StringIO(csv_texto))
    except Exception as exc:
        raise ValueError(f"CSV inválido: {type(exc).__name__}.")
    if df.empty:
        raise ValueError("CSV sem linhas de dados.")
    return df


def _tool_quantitativo(name: str, arguments: dict) -> dict:
    """Despacho das 4 ferramentas quantitativas sobre CSV inline."""
    from research.discovery import causal, bayes, mistos
    try:
        if name == "estimar_did":
            req = ["csv_texto", "coluna_y", "coluna_tempo", "coluna_tratado"]
            if any(not isinstance(arguments.get(k, ""), str) or not arguments.get(k, "").strip() for k in req):
                return {"ok": False, "error": "Payload inválido: colunas devem ser strings não vazias."}
            n_perm = arguments.get("n_perm", 199)
            if not isinstance(n_perm, int) or n_perm < 19:
                return {"ok": False, "error": "n_perm deve ser inteiro >= 19."}
            df = _csv_para_df(arguments["csv_texto"])
            return causal.did(df, arguments["coluna_y"], arguments["coluna_tempo"],
                              arguments["coluna_tratado"], n_perm=n_perm)
        if name == "estimar_iv":
            req = ["csv_texto", "coluna_y", "coluna_x", "coluna_z"]
            if any(not isinstance(arguments.get(k, ""), str) or not arguments.get(k, "").strip() for k in req):
                return {"ok": False, "error": "Payload inválido: colunas devem ser strings não vazias."}
            df = _csv_para_df(arguments["csv_texto"])
            return causal.iv_2sls(df, arguments["coluna_y"], arguments["coluna_x"], arguments["coluna_z"])
        if name == "atualizar_bayes":
            if (not isinstance(arguments.get("csv_texto", ""), str) or not arguments.get("csv_texto", "").strip()
                    or not isinstance(arguments.get("coluna", ""), str) or not arguments.get("coluna", "").strip()):
                return {"ok": False, "error": "Payload inválido: csv_texto/coluna devem ser strings não vazias."}
            for k in ("mu0", "tau0"):
                if not isinstance(arguments.get(k), (int, float)):
                    return {"ok": False, "error": f"Payload inválido: {k} deve ser número."}
            df = _csv_para_df(arguments["csv_texto"])
            alt = arguments.get("prior_alternativo")
            alt_t = tuple(alt) if isinstance(alt, list) and len(alt) == 2 else None
            return bayes.atualizar(df, arguments["coluna"], float(arguments["mu0"]),
                                   float(arguments["tau0"]), prior_alternativo=alt_t)
        if name == "icc_cluster":
            req = ["csv_texto", "coluna_y", "coluna_grupo"]
            if any(not isinstance(arguments.get(k, ""), str) or not arguments.get(k, "").strip() for k in req):
                return {"ok": False, "error": "Payload inválido: colunas devem ser strings não vazias."}
            df = _csv_para_df(arguments["csv_texto"])
            return mistos.icc(df, arguments["coluna_y"], arguments["coluna_grupo"])
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": False, "error": "Ferramenta desconhecida."}


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
