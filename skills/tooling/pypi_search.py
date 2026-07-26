#!/usr/bin/env python3
"""
PyPI Search Engine v3.0
========================
Motor de busca e recomendação de bibliotecas Python no PyPI para o ecossistema
OpenCode. Estratégias em cascata:

1. **Simple API (JSON)** — índice local de nomes de pacotes (cache semanal)
2. **JSON API** — detalhes e metadados de cada pacote
3. **Per-package Simple API** — verificação de existência e versões

Uso:
    python skills/tooling/pypi_search.py "termo de busca" --limit 10
    python skills/tooling/pypi_search.py "async http" --limit 5 --no-enrich
    python skills/tooling/pypi_search.py "requests" --exact
    python skills/tooling/pypi_search.py "scihub paper download" --category academic

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import argparse
import gzip
import json
import logging
import re
import sys
import time
import xmlrpc.client
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

import requests

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PyPISearch] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("pypi-search")

# ============================================================
# Constantes
# ============================================================

PYPI_JSON_API = "https://pypi.org/pypi/{package}/json"
PYPI_SIMPLE_API = "https://pypi.org/simple/"
PYPI_SIMPLE_API_JSON = "https://pypi.org/simple/?format=json"

CACHE_DIR = Path(__file__).parent / ".cache"
PACKAGE_INDEX_CACHE = CACHE_DIR / "pypi_simple_index_v3.json.gz"
INDEX_TTL_SECONDS = 7 * 86400  # 7 dias
JSON_CACHE_TTL = 3600  # 1 hora para cache de JSON de pacotes

# Limites
MAX_SEARCH_RESULTS = 25
MAX_ENRICH_WORKERS = 5

# Pesos dos critérios de avaliação (alinhados com o agent card)
CRITERIA_WEIGHTS = {
    "saude": 0.25,
    "popularidade": 0.20,
    "qualidade_tecnica": 0.25,
    "compatibilidade": 0.20,
    "afinidade_ecossistema": 0.10,
}

# Categorias de busca para refino semântico
CATEGORY_KEYWORDS = {
    "academic": ["paper", "pdf", "doi", "scihub", "research", "citation", "bibliography",
                 "scholar", "journal", "article", "reference", "thesis", "dissertation",
                 "preprint", "arxiv", "pubmed", "crossref"],
    "web": ["http", "async", "requests", "scraping", "crawler", "html", "rest", "api",
            "webhook", "graphql", "grpc"],
    "data": ["pandas", "numpy", "dataframe", "dataset", "csv", "sql", "database",
             "etl", "pipeline", "parquet", "feather"],
    "ml": ["tensorflow", "pytorch", "sklearn", "neural", "deep learning", "nlp",
           "transformer", "llm", "embedding", "vector"],
    "cli": ["click", "typer", "argparse", "terminal", "console", "rich", "prompt",
            "shell", "command"],
    "pdf": ["pdf", "reportlab", "weasyprint", "pypdf", "pdfminer", "pdfplumber",
            "camelot", "tabula"],
}


# ============================================================
# Modelos de Dados
# ============================================================

@dataclass
class PackageInfo:
    """Informações completas de um pacote PyPI."""

    name: str
    version: str = ""
    summary: str = ""
    description: str = ""
    author: str = ""
    author_email: str = ""
    license: str = ""
    home_page: str = ""
    project_urls: Dict[str, str] = field(default_factory=dict)
    requires_python: str = ""
    requires_dist: List[str] = field(default_factory=list)
    classifiers: List[str] = field(default_factory=list)
    keywords: str = ""
    release_url: str = ""
    last_upload: str = ""
    downloads_last_month: int = 0
    score: float = 0.0
    scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Resultado consolidado de uma busca."""

    query: str
    total_found: int
    packages: List[PackageInfo]
    elapsed_ms: int
    source: str
    error: Optional[str] = None


# ============================================================
# Gerenciamento de Cache
# ============================================================

def _cache_get(key: str, ttl: int = JSON_CACHE_TTL) -> Optional[Any]:
    """Recupera valor do cache."""
    safe_key = re.sub(r"[^a-zA-Z0-9._-]", "_", key)[:120]
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{safe_key}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        age = time.time() - data.get("_ts", 0)
        if age < ttl:
            return data.get("value")
    except (json.JSONDecodeError, OSError):
        pass
    return None


def _cache_set(key: str, value: Any) -> None:
    """Armazena valor no cache."""
    safe_key = re.sub(r"[^a-zA-Z0-9._-]", "_", key)[:120]
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{safe_key}.json"
    try:
        path.write_text(json.dumps({"value": value, "_ts": time.time()},
                                    ensure_ascii=False))
    except OSError as exc:
        logger.debug("Cache write error: %s", exc)


# ============================================================
# Estratégia 1: Índice Local de Pacotes (Simple API)
# ============================================================

def _build_local_index() -> Dict[str, int]:
    """
    Baixa e cacheia o índice completo de pacotes do PyPI Simple API (JSON).
    Retorna dict: nome_do_pacote -> _last-serial
    """
    # Verificar cache
    if PACKAGE_INDEX_CACHE.exists():
        try:
            mtime = PACKAGE_INDEX_CACHE.stat().st_mtime
            age = time.time() - mtime
            if age < INDEX_TTL_SECONDS:
                with gzip.open(PACKAGE_INDEX_CACHE, "rt", encoding="utf-8") as f:
                    return json.load(f)
            logger.info("Índice expirado (%.1f dias). Recarregando...", age / 86400)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Cache corrompido: %s", exc)

    # Baixar índice completo
    logger.info("Baixando índice PyPI Simple API (~40MB)...")
    start = time.time()
    try:
        resp = requests.get(
            PYPI_SIMPLE_API,
            timeout=120,
            headers={"Accept": "application/vnd.pypi.simple.v1+json"},
        )
        resp.raise_for_status()
        data = resp.json()
        projects = data.get("projects", [])
        index = {p["name"]: p.get("_last-serial", 0) for p in projects}

        # Salvar cache comprimido (leva ~5-10s)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with gzip.open(PACKAGE_INDEX_CACHE, "wt", encoding="utf-8") as f:
            json.dump(index, f, separators=(",", ":"))

        elapsed = time.time() - start
        logger.info("Índice carregado: %d pacotes em %.1fs", len(index), elapsed)
        return index

    except requests.RequestException as exc:
        logger.error("Falha ao baixar índice: %s", exc)
        # Tentar cache expirado como fallback
        if PACKAGE_INDEX_CACHE.exists():
            logger.warning("Usando cache expirado como fallback")
            with gzip.open(PACKAGE_INDEX_CACHE, "rt", encoding="utf-8") as f:
                return json.load(f)
        return {}


def _search_local(query: str, limit: int = 10) -> List[str]:
    """
    Busca no índice local de pacotes usando correspondência parcial.
    Retorna lista de nomes de pacotes.
    """
    query_lower = query.lower().strip()
    terms = query_lower.split()

    # Carregar índice (pode ser do cache)
    index = _build_local_index()
    if not index:
        logger.warning("Índice vazio, busca local indisponível")
        return []

    # Estratégia de matching:
    # 1. Correspondência exata (score mais alto)
    # 2. Prefixo corresponde exato
    # 3. Substring corresponde ao query inteiro
    # 4. Qualquer termo corresponde (OR) — para multi-word queries
    # 5. Quanto mais termos correspondem, maior o score
    scored: List[Tuple[str, float]] = []

    for pkg_name in index:
        pkg_lower = pkg_name.lower()
        score = 0.0

        # Exato
        if pkg_lower == query_lower:
            score = 100.0
        # Começa com o query
        elif pkg_lower.startswith(query_lower):
            score = 80.0
        # Termina com o query
        elif pkg_lower.endswith(query_lower):
            score = 60.0
        # Query completo como substring
        elif len(terms) > 1 and query_lower in pkg_lower:
            score = 45.0
        else:
            # Correspondência por termos individuais (OR)
            pkg_parts = pkg_lower.replace("-", " ").replace("_", " ").split()
            match_count = 0
            for term in terms:
                if len(term) < 2:
                    continue  # Ignorar termos muito curtos
                if term in pkg_lower:
                    match_count += 1
                elif any(term in part for part in pkg_parts):
                    match_count += 0.5

            if match_count == 0:
                continue

            # Score baseado na fração de termos correspondidos
            n_terms = max(len([t for t in terms if len(t) >= 2]), 1)
            ratio = match_count / n_terms
            if ratio >= 0.8:
                score = 35.0 + ratio * 20.0
            elif ratio >= 0.5:
                score = 20.0 + ratio * 15.0
            else:
                score = 10.0 + ratio * 10.0

            # Bônus: o primeiro termo está no início do nome?
            first_term = terms[0]
            if len(first_term) >= 2 and pkg_lower.startswith(first_term):
                score += 15.0
            # Bônus: o nome começa com uma letra que corresponde
            if pkg_lower[0] == first_term[0]:
                score += 2.0

        if score > 0:
            scored.append((pkg_name, score))

    # Ordenar por score decrescente
    scored.sort(key=lambda x: -x[1])
    return [name for name, _ in scored[:limit]]


# ============================================================
# Estratégia 2: XML-RPC browse (fallback para categorias)
# ============================================================

def _browse_xmlrpc(letter: str = "") -> List[str]:
    """
    Usa XML-RPC browse para listar pacotes por letra (não depende de search).
    Útil como fallback ou para pacotes recentes.
    """
    try:
        client = xmlrpc.client.ServerProxy("https://pypi.org/pypi")
        results = client.browse(
            ["Programming Language :: Python :: 3"],
        ) if not letter else client.browse([f"Framework :: {letter}"])
        return [r["name"] for r in results if isinstance(r, dict)]
    except Exception as exc:
        logger.debug("XML-RPC browse falhou: %s", exc)
        return []


# ============================================================
# Estratégia 3: JSON API (detalhes do pacote)
# ============================================================

def _fetch_package_json(package_name: str) -> Optional[dict]:
    """Obtém detalhes completos de um pacote via JSON API."""
    cache_key = f"json_{package_name}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    url = PYPI_JSON_API.format(package=package_name)
    try:
        resp = requests.get(url, timeout=15, headers={"Accept": "application/json"})
        resp.raise_for_status()
        data = resp.json()
        _cache_set(cache_key, data)
        return data
    except requests.RequestException as exc:
        logger.debug("JSON API falhou para %s: %s", package_name, exc)
        return None


# ============================================================
# Estratégia 4: Per-Package Simple API (fallback detalhes)
# ============================================================

def _fetch_simple_package(package_name: str) -> Optional[dict]:
    """
    Obtém metadados básicos via Simple API per-package.
    Retorna dict com name, versions, e links.
    """
    url = f"{PYPI_SIMPLE_API}{package_name}/"
    try:
        resp = requests.get(
            url,
            timeout=10,
            headers={"Accept": "application/vnd.pypi.simple.v1+json"},
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None


# ============================================================
# Parsing e Enriquecimento
# ============================================================

def _parse_json_to_info(package_name: str, data: dict) -> Optional[PackageInfo]:
    """Converte resposta da JSON API em PackageInfo."""
    try:
        info = data.get("info", {})
        releases = data.get("releases", {})

        # Última upload
        last_upload = ""
        all_uploads = []
        for ver, files in releases.items():
            for f in files:
                if f.get("upload_time"):
                    all_uploads.append(f["upload_time"])
        if all_uploads:
            all_uploads.sort(reverse=True)
            last_upload = all_uploads[0]

        # URL do release
        version = info.get("version", "")
        release_url = f"https://pypi.org/project/{package_name}/{version}/" if version else f"https://pypi.org/project/{package_name}/"

        return PackageInfo(
            name=package_name,
            version=version,
            summary=info.get("summary", ""),
            description=(info.get("description") or "")[:500],
            author=info.get("author", ""),
            author_email=info.get("author_email", ""),
            license=info.get("license", ""),
            home_page=info.get("home_page", ""),
            project_urls=info.get("project_urls") or {},
            requires_python=info.get("requires_python", ""),
            requires_dist=info.get("requires_dist") or [],
            classifiers=info.get("classifiers") or [],
            keywords=info.get("keywords", ""),
            release_url=release_url,
            last_upload=last_upload,
        )
    except Exception as exc:
        logger.debug("Erro parseando %s: %s", package_name, exc)
        return None


# ============================================================
# Scoring
# ============================================================

def _calculate_scores(pkg: PackageInfo) -> Dict[str, float]:
    """
    Calcula scores nos 5 critérios (0-10 cada) conforme agent card.
    """
    scores: Dict[str, float] = {}

    # 1. Saúde do Projeto (25%)
    saude = 5.0
    if pkg.last_upload:
        try:
            uploaded_str = pkg.last_upload.replace("Z", "+00:00")
            uploaded = datetime.fromisoformat(uploaded_str)
            # Normalizar para timezone-aware
            if uploaded.tzinfo is None:
                uploaded = uploaded.replace(tzinfo=timezone.utc)
            days_since = (datetime.now(timezone.utc) - uploaded).days
            if days_since < 30:
                saude = 9.0
            elif days_since < 180:
                saude = 7.5
            elif days_since < 365:
                saude = 5.0
            else:
                saude = 3.0
        except ValueError:
            saude = 5.0
    if pkg.license and pkg.license not in ("UNKNOWN", ""):
        saude += 1.0
    if pkg.author:
        saude += 0.5
    scores["saude"] = min(saude, 10.0)

    # 2. Popularidade e Adoção (20%)
    pop = 5.0
    # Inferir popularidade pelo número de classifiers e descrição
    n_classifiers = len(pkg.classifiers)
    if n_classifiers > 20:
        pop = 8.5
    elif n_classifiers > 10:
        pop = 7.0
    elif n_classifiers > 5:
        pop = 6.0
    # Ter muitas versões lançadas indica longevidade
    scores["popularidade"] = min(pop, 10.0)

    # 3. Qualidade Técnica (25%)
    qual = 5.0
    if len(pkg.summary) > 100:
        qual += 1.0
    if len(pkg.description) > 300:
        qual += 0.5
    if pkg.home_page:
        qual += 0.5
    if len(pkg.project_urls) > 2:
        qual += 1.0
    if pkg.requires_dist:
        qual += 0.5  # Declara dependências
    if any("typed" in c.lower() or "typing" in c.lower() for c in pkg.classifiers):
        qual += 1.0
    scores["qualidade_tecnica"] = min(qual, 10.0)

    # 4. Compatibilidade (20%)
    compat = 7.0
    if pkg.requires_python:
        match = re.search(r">=(\d+\.\d+)", pkg.requires_python)
        if match:
            min_py = float(match.group(1))
            if min_py <= 3.9:
                compat = 9.0
            elif min_py <= 3.11:
                compat = 7.5
            else:
                compat = 5.0
        elif "3" in pkg.requires_python:
            compat = 8.0
    n_deps = len(pkg.requires_dist)
    if n_deps > 20:
        compat -= 1.5
    elif n_deps > 10:
        compat -= 0.5
    scores["compatibilidade"] = max(compat, 1.0)

    # 5. Afinidade com Ecossistema (10%)
    afin = 5.0
    eco_kws = [
        "asyncio", "async", "mcp", "cli", "api", "http", "json", "yaml",
        "pdf", "csv", "data", "ml", "ai", "llm", "token", "search", "rest",
    ]
    text = f"{pkg.summary} {pkg.keywords} {' '.join(pkg.classifiers)}".lower()
    matches = sum(1 for kw in eco_kws if kw in text)
    afin += matches * 0.5
    scores["afinidade_ecossistema"] = min(afin, 10.0)

    return scores


# ============================================================
# Motor de Busca Principal
# ============================================================

def search(
    query: str,
    limit: int = 10,
    enrich: bool = True,
    use_cache: bool = True,
    exact: bool = False,
    category: str = "",
) -> SearchResult:
    """
    Executa busca no PyPI usando o índice local (Simple API).

    Args:
        query: Termo de busca
        limit: Máximo de resultados (padrão 10, máx 25)
        enrich: Se deve enriquecer com JSON API (default True)
        use_cache: Se deve usar cache (default True)
        exact: Busca exata por nome (default False)
        category: Categoria para refinar busca (ex: "academic", "pdf", "web")

    Returns:
        SearchResult
    """
    start = time.time()
    query_clean = query.strip().lower()
    limit = min(limit, MAX_SEARCH_RESULTS)
    logger.info("Buscando: '%s' (limit=%d, enrich=%s)", query_clean, limit, enrich)

    # A categoria influencia apenas o re-ranqueamento, não a query de matching
    # (evita falsos negativos por exigir muitas keywords)
    search_query = query_clean
    category_kws = []
    if category and category in CATEGORY_KEYWORDS:
        category_kws = CATEGORY_KEYWORDS[category][:5]
        logger.info("Categoria '%s' aplicada para re-ranqueamento", category)

    # Verificar cache
    cache_key = f"search_{search_query}_{limit}_{exact}_{category}"
    if use_cache:
        cached = _cache_get(cache_key, ttl=1800)  # 30 min cache de busca
        if cached:
            pkgs_data = cached.get("packages", [])
            packages = [PackageInfo(**p) for p in pkgs_data]
            elapsed = int((time.time() - start) * 1000)
            source = cached.get("source", "cache")
            logger.info("Cache hit: %d pacotes", len(packages))
            return SearchResult(
                query=query_clean, total_found=len(packages),
                packages=packages, elapsed_ms=elapsed, source=f"cache/{source}",
            )

    # Busca exata?
    if exact:
        detail = _fetch_package_json(query_clean)
        if detail:
            pkg = _parse_json_to_info(query_clean, detail)
            if pkg:
                pkg.scores = _calculate_scores(pkg)
                pkg.score = sum(
                    pkg.scores[k] * CRITERIA_WEIGHTS[k]
                    for k in CRITERIA_WEIGHTS if k in pkg.scores
                )
                elapsed = int((time.time() - start) * 1000)
                return SearchResult(
                    query=query_clean, total_found=1, packages=[pkg],
                    elapsed_ms=elapsed, source="json_api",
                )
        elapsed = int((time.time() - start) * 1000)
        return SearchResult(
            query=query_clean, total_found=0, packages=[],
            elapsed_ms=elapsed, source="none",
            error=f"Pacote '{query_clean}' não encontrado",
        )

    # Busca no índice local
    package_names = _search_local(search_query, limit=limit * 3)

    if not package_names:
        elapsed = int((time.time() - start) * 1000)
        return SearchResult(
            query=query_clean, total_found=0, packages=[],
            elapsed_ms=elapsed, source="local_index",
            error="Nenhum pacote encontrado no índice local",
        )

    # Enriquecer com detalhes
    packages: List[PackageInfo] = []
    if enrich:
        selected = package_names[:limit]
        with ThreadPoolExecutor(max_workers=MAX_ENRICH_WORKERS) as pool:
            futures = {pool.submit(_fetch_package_json, n): n for n in selected}
            for future in as_completed(futures):
                name = futures[future]
                try:
                    data = future.result()
                    if data:
                        pkg = _parse_json_to_info(name, data)
                        if pkg:
                            pkg.scores = _calculate_scores(pkg)

                            # Bônus de categoria (re-ranqueamento)
                            cat_bonus = 0.0
                            if category_kws and pkg.summary:
                                text_lower = (
                                    f"{pkg.summary} {pkg.keywords} "
                                    f"{' '.join(pkg.classifiers)}"
                                ).lower()
                                cat_matches = sum(
                                    1 for kw in category_kws if kw in text_lower
                                )
                                cat_bonus = cat_matches * 2.0  # até 10 pts extras

                            pkg.score = sum(
                                pkg.scores[k] * CRITERIA_WEIGHTS[k]
                                for k in CRITERIA_WEIGHTS if k in pkg.scores
                            ) + cat_bonus
                            packages.append(pkg)
                            continue
                except Exception as exc:
                    logger.debug("Erro enriquecendo %s: %s", name, exc)

        # Preencher com dados básicos os que falharam
        enriched_names = {p.name for p in packages}
        for name in selected:
            if name not in enriched_names:
                packages.append(PackageInfo(name=name))
    else:
        packages = [PackageInfo(name=n) for n in package_names[:limit]]

    # Ordenar por score decrescente
    packages.sort(key=lambda p: -p.score)

    source = "local_index+json_api" if enrich else "local_index"
    elapsed = int((time.time() - start) * 1000)

    # Salvar cache
    if use_cache and packages:
        try:
            _cache_set(cache_key, {
                "packages": [asdict(p) for p in packages],
                "source": source,
            })
        except Exception as exc:
            logger.debug("Cache save error: %s", exc)

    logger.info("Busca: %d pacotes em %dms (fonte: %s)", len(packages), elapsed, source)
    return SearchResult(
        query=query_clean, total_found=len(package_names),
        packages=packages, elapsed_ms=elapsed, source=source,
    )


# ============================================================
# Utilitário: Recomendar bibliotecas para tarefas específicas
# ============================================================

TASK_LIBRARIES = {
    "download_papers": [
        ("scihub", "Biblioteca para acesso a papers acadêmicos via Sci-Hub", "scihub"),
        ("arxiv", "cliente da API do arXiv para busca de preprints", "arxiv"),
        ("crossrefapi", "acesso à API CrossRef para metadados de artigos", "crossrefapi"),
        ("pubmed-lxml", "acesso ao PubMed/MEDLINE", "pubmed-lxml"),
        ("habanero", "cliente CrossRef oficial", "habanero"),
        ("pypdf", "leitura e extração de texto de PDFs", "pypdf"),
        ("pdfminer.six", "mineração de PDFs acadêmicos", "pdfminer.six"),
    ],
    "web_scraping": [
        ("requests", "HTTP requests", "requests"),
        ("httpx", "HTTP async com tipagem", "httpx"),
        ("beautifulsoup4", "Parser HTML/XML", "beautifulsoup4"),
        ("selenium", "Automação de navegador", "selenium"),
        ("playwright", "Automação headless moderna", "playwright"),
    ],
    "data_analysis": [
        ("polars", "DataFrame rápido em Rust", "polars"),
        ("pandas", "DataFrame clássico", "pandas"),
        ("numpy", "Computação numérica", "numpy"),
        ("scipy", "Computação científica", "scipy"),
    ],
    "cli_tools": [
        ("typer", "CLI com tipagem", "typer"),
        ("click", "CLI clássico", "click"),
        ("rich", "Terminal estilizado", "rich"),
        ("prompt_toolkit", "Interface interativa", "prompt-toolkit"),
    ],
    "pdf_generation": [
        ("reportlab", "Geração de PDF programática", "reportlab"),
        ("weasyprint", "HTML+CSS → PDF", "weasyprint"),
        ("fpdf2", "PDF leve sem dependências", "fpdf2"),
    ],
}


def recommend_for_task(task_type: str) -> Dict[str, Any]:
    """
    Retorna bibliotecas recomendadas para um tipo de tarefa.

    Args:
        task_type: Tipo de tarefa (download_papers, web_scraping, data_analysis, etc.)

    Returns:
        Dict com recomendações
    """
    libs = TASK_LIBRARIES.get(task_type, [])
    if not libs:
        return {
            "task_type": task_type,
            "found": False,
            "message": f"Tipo de tarefa '{task_type}' não reconhecido. Opções: {list(TASK_LIBRARIES.keys())}",
        }

    results = []
    for lib_name, description, pypi_name in libs:
        data = _fetch_package_json(pypi_name)
        if data:
            info = _parse_json_to_info(pypi_name, data)
            if info:
                info.scores = _calculate_scores(info)
                info.score = sum(
                    info.scores[k] * CRITERIA_WEIGHTS[k]
                    for k in CRITERIA_WEIGHTS if k in info.scores
                )
                results.append(info)
            else:
                results.append(PackageInfo(name=pypi_name, summary=description))
        else:
            results.append(PackageInfo(name=pypi_name, summary=description))

    results.sort(key=lambda p: -p.score)
    return {
        "task_type": task_type,
        "found": True,
        "description": f"Bibliotecas recomendadas para {task_type}",
        "recommendations": [
            {
                "name": p.name,
                "version": p.version,
                "summary": p.summary[:150] if p.summary else "",
                "score": round(p.score, 2),
                "install": f"pip install {p.name}",
                "url": f"https://pypi.org/project/{p.name}/",
            }
            for p in results
        ],
    }


# ============================================================
# Formatação de Saída
# ============================================================

def format_output(result: SearchResult, json_output: bool = False) -> str:
    """Formata o resultado da busca."""
    if json_output:
        return json.dumps({
            "query": result.query,
            "total_found": result.total_found,
            "elapsed_ms": result.elapsed_ms,
            "source": result.source,
            "error": result.error,
            "packages": [
                {
                    "name": p.name,
                    "version": p.version,
                    "summary": p.summary[:200] if p.summary else "",
                    "score": round(p.score, 2),
                    "scores": {k: round(v, 1) for k, v in p.scores.items()},
                    "license": p.license,
                    "requires_python": p.requires_python,
                    "last_upload": p.last_upload,
                    "release_url": p.release_url,
                }
                for p in result.packages
            ],
        }, ensure_ascii=False, indent=2)

    lines = [f"🔍 PyPI Search: '{result.query}'"]
    lines.append(f"   {result.total_found} encontrados, {len(result.packages)} exibidos")
    lines.append(f"   Fonte: {result.source} | {result.elapsed_ms}ms")
    if result.error:
        lines.append(f"   ⚠️  {result.error}")
    lines.append("")

    if result.packages:
        lines.append(f"{'Pacote':<30} {'Versão':<14} {'Score':<8} {'Saúde':<8} {'Qualif.':<8}")
        lines.append("-" * 68)
        for pkg in result.packages:
            scores = pkg.scores
            saude = f"{scores.get('saude', 0):.1f}"
            qual = f"{scores.get('qualidade_tecnica', 0):.1f}"
            lines.append(f"{pkg.name:<30} {pkg.version:<14} {pkg.score:<8.2f} {saude:<8} {qual:<8}")

        lines.append("")
        best = result.packages[0]
        lines.append("🎯 Melhor candidato:")
        lines.append(f"   {best.name} v{best.version} — score {best.score:.2f}/10")
        lines.append(f"   {best.summary[:200]}")
        if best.license:
            lines.append(f"   📜 Licença: {best.license}")
        if best.requires_python:
            lines.append(f"   🐍 Python: {best.requires_python}")
        lines.append(f"   🔗 {best.release_url}")
        lines.append("")

    return "\n".join(lines)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="PyPI Search Engine v3.0 — OpenCode Ecosystem",
    )
    parser.add_argument("query", type=str, nargs="?", default="",
                        help="Termo de busca")
    parser.add_argument("--limit", type=int, default=10,
                        help=f"Máximo de resultados (padrão: 10, máx: {MAX_SEARCH_RESULTS})")
    parser.add_argument("--no-enrich", action="store_true",
                        help="Desativa enriquecimento via JSON API")
    parser.add_argument("--no-cache", action="store_true",
                        help="Ignora cache")
    parser.add_argument("--exact", action="store_true",
                        help="Busca exata por nome do pacote")
    parser.add_argument("--category", type=str, default="",
                        choices=list(CATEGORY_KEYWORDS.keys()) + [""],
                        help="Categoria para refinar busca (academic, web, data, ml, cli, pdf)")
    parser.add_argument("--recommend", type=str, default="",
                        choices=list(TASK_LIBRARIES.keys()),
                        help="Recomenda bibliotecas para um tipo de tarefa")
    parser.add_argument("--build-index", action="store_true",
                        help="Força reconstrução do índice local")
    parser.add_argument("--json", action="store_true",
                        help="Saída em JSON")

    args = parser.parse_args()

    # Comando: reconstruir índice
    if args.build_index:
        logger.info("Forçando reconstrução do índice...")
        # Remover cache
        if PACKAGE_INDEX_CACHE.exists():
            PACKAGE_INDEX_CACHE.unlink()
        index = _build_local_index()
        print(json.dumps({
            "status": "ok",
            "total_packages": len(index),
            "cache_file": str(PACKAGE_INDEX_CACHE),
        }, ensure_ascii=False, indent=2))
        return 0

    # Comando: recomendar para tarefa
    if args.recommend:
        recs = recommend_for_task(args.recommend)
        if args.json:
            print(json.dumps(recs, ensure_ascii=False, indent=2))
        else:
            print(f"\n📦 Bibliotecas recomendadas para: {args.recommend}\n")
            for r in recs.get("recommendations", []):
                print(f"  • {r['name']} v{r.get('version', '?')} — score {r['score']}/10")
                print(f"    {r.get('summary', '')}")
                print(f"    Instalação: {r['install']}")
                print()
        return 0

    # Comando: busca
    if not args.query:
        parser.print_help()
        return 1

    result = search(
        query=args.query,
        limit=args.limit,
        enrich=not args.no_enrich,
        use_cache=not args.no_cache,
        exact=args.exact,
        category=args.category,
    )

    output = format_output(result, json_output=args.json)
    print(output)

    return 0 if not result.error else 1


if __name__ == "__main__":
    sys.exit(main())
