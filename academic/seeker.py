# -*- coding: utf-8 -*-
"""
SEEKER-DatasetSearch v1.0 — Busca de Datasets Abertos
OpenCode Ecosystem v4.2.2

Pipeline de descoberta de dados com 4 fontes integradas:
  1. Catálogo curado local (public_datasets_catalog.csv)
  2. data.gov CKAN API (portão oficial do governo dos EUA)
  3. Kaggle API (se token disponível)
  4. Hugging Face Datasets Hub API

Funcionalidades:
  - Busca full-text no catálogo local
  - Filtro por categoria, cloud, vintage, palavra-chave
  - Busca dinâmica em data.gov via CKAN REST API
  - Exportação em JSON estruturado para o pipeline SEEKER
  - Log de observabilidade em .evolve/
  - Formatação de resultado para citação acadêmica
"""

import csv
import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import urllib3

urllib3.disable_warnings()

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(
    format='[%(asctime)s][%(levelname)s][DatasetSearch] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('DatasetSearch')
logger.setLevel(logging.INFO)

# ─────────────────────────────────────────────
# Paths e constantes
# ─────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
DATA_DIR    = BASE_DIR.parent / 'data'
CATALOG_CSV = DATA_DIR / 'public_datasets_catalog.csv'
EVOLVE_DIR  = Path('.evolve')

# APIs externas
DATAGOV_API    = 'https://catalog.data.gov/api/3/action/package_search'
HF_DATASETS_API = 'https://huggingface.co/api/datasets'
KAGGLE_API     = 'https://www.kaggle.com/api/v1/datasets/list'

HEADERS = {
    'User-Agent': 'OpenCode-Ecosystem/4.2.2 (academic research; contact=opencode@ecosystem.br)'
}

CATEGORIES_MAP = {
    'biology': ['Biology', 'Healthcare', 'Agriculture'],
    'nlp': ['Natural Language', 'Social Networks', 'Social Sciences'],
    'geo': ['GIS', 'Transportation', 'Climate/Weather'],
    'ml': ['Machine Learning', 'Data Challenges', 'Computer Networks'],
    'social': ['Social Networks', 'Social Sciences', 'Museums'],
    'gov': ['Government', 'Social Sciences', 'Energy'],
    'transport': ['Transportation'],
    'energy': ['Energy'],
}


# ─────────────────────────────────────────────
# Carregamento do catálogo local
# ─────────────────────────────────────────────

def load_catalog(csv_path: Path = CATALOG_CSV) -> list[dict]:
    """Carrega o catálogo curado de datasets do CSV local."""
    datasets = []
    if not csv_path.exists():
        logger.warning(f"Catálogo não encontrado: {csv_path}")
        return datasets
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            datasets.append({
                'name':     row.get('datasetName', '').strip(),
                'about':    row.get('about', '').strip(),
                'link':     row.get('link', '').strip(),
                'category': row.get('categoryName', '').strip(),
                'cloud':    row.get('cloud', '').strip(),
                'vintage':  row.get('vintage', '').strip(),
                'source':   'catalog_local',
            })
    logger.info(f"Catálogo local: {len(datasets)} datasets carregados")
    return datasets


# ─────────────────────────────────────────────
# Busca local no catálogo
# ─────────────────────────────────────────────

def search_local(
    datasets: list[dict],
    query: str = '',
    category: str = '',
    cloud: str = '',
    vintage_from: int = 0,
    vintage_to: int = 9999,
    limit: int = 20,
) -> list[dict]:
    """
    Busca full-text e filtra o catálogo local.

    Args:
        query:        palavras-chave (busca em name + about)
        category:     filtro exato de categoria (ex: 'Transportation')
        cloud:        filtro de cloud (GitHub, Amazon, etc.)
        vintage_from: ano mínimo
        vintage_to:   ano máximo
        limit:        máximo de resultados
    """
    query_lower = query.lower()
    results = []
    for d in datasets:
        # Filtro de texto
        if query and query_lower not in d['name'].lower() and query_lower not in d['about'].lower():
            continue
        # Filtro de categoria (flexível)
        if category and category.lower() not in d['category'].lower():
            continue
        # Filtro de cloud
        if cloud and cloud.lower() not in d['cloud'].lower():
            continue
        # Filtro de vintage
        if d['vintage'] and d['vintage'] != 'NA':
            try:
                yr = int(d['vintage'])
                if yr < vintage_from or yr > vintage_to:
                    continue
            except ValueError:
                pass
        results.append(d)
        if len(results) >= limit:
            break
    return results


def search_by_theme(datasets: list[dict], theme: str, limit: int = 10) -> list[dict]:
    """
    Busca por tema semântico usando o mapa de categorias.
    Ex: theme='nlp' retorna datasets de Natural Language, Social Networks, etc.
    """
    cats = CATEGORIES_MAP.get(theme.lower(), [theme])
    results = []
    for d in datasets:
        if any(c.lower() in d['category'].lower() for c in cats):
            results.append(d)
        if len(results) >= limit:
            break
    return results


# ─────────────────────────────────────────────
# data.gov — CKAN API
# ─────────────────────────────────────────────

def search_datagov(query: str, limit: int = 10) -> list[dict]:
    """
    Busca no catálogo oficial data.gov via CKAN REST API.
    Gratuito, sem autenticação.
    Documentação: https://catalog.data.gov/api/3
    """
    try:
        params = {
            'q': query,
            'rows': limit,
            'sort': 'score desc, metadata_modified desc',
        }
        r = requests.get(DATAGOV_API, params=params, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            logger.warning(f"data.gov: status {r.status_code}")
            return []
        results_raw = r.json().get('result', {}).get('results', [])
        results = []
        for pkg in results_raw:
            # Extrair recurso de download principal
            resources = pkg.get('resources', [])
            download_url = ''
            for res in resources:
                if res.get('url') and res.get('format', '').upper() in ('CSV', 'JSON', 'XLS', 'XLSX', 'ZIP'):
                    download_url = res['url']
                    break
            if not download_url and resources:
                download_url = resources[0].get('url', '')

            results.append({
                'name':     pkg.get('title', ''),
                'about':    (pkg.get('notes') or '')[:200].replace('\n', ' '),
                'link':     f"https://catalog.data.gov/dataset/{pkg.get('name','')}",
                'download': download_url,
                'category': ', '.join(g.get('display_name','') for g in pkg.get('groups', [])),
                'cloud':    'data.gov',
                'vintage':  str(pkg.get('metadata_created','')[:4]) if pkg.get('metadata_created') else 'NA',
                'org':      (pkg.get('organization') or {}).get('title',''),
                'license':  pkg.get('license_title',''),
                'source':   'data.gov',
            })
        logger.info(f"data.gov: {len(results)} resultados para '{query}'")
        return results
    except Exception as e:
        logger.error(f"data.gov error: {e}")
        return []


# ─────────────────────────────────────────────
# Hugging Face Datasets Hub
# ─────────────────────────────────────────────

def search_huggingface(query: str, limit: int = 10) -> list[dict]:
    """
    Busca datasets no Hugging Face Hub.
    Gratuito, sem autenticação para buscas básicas.
    """
    try:
        params = {'search': query, 'limit': limit, 'full': 'false'}
        r = requests.get(HF_DATASETS_API, params=params, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            logger.warning(f"HuggingFace: status {r.status_code}")
            return []
        raw = r.json() if isinstance(r.json(), list) else r.json().get('datasets', [])
        results = []
        for ds in raw[:limit]:
            ds_id = ds.get('id', ds.get('modelId', ''))
            results.append({
                'name':     ds_id,
                'about':    ds.get('description','')[:200] if ds.get('description') else '',
                'link':     f"https://huggingface.co/datasets/{ds_id}",
                'download': f"https://huggingface.co/datasets/{ds_id}",
                'category': ', '.join(ds.get('task_categories', [])),
                'cloud':    'HuggingFace',
                'vintage':  str(ds.get('lastModified','')[:4]) if ds.get('lastModified') else 'NA',
                'license':  ds.get('license',''),
                'source':   'HuggingFace',
            })
        logger.info(f"HuggingFace: {len(results)} resultados para '{query}'")
        return results
    except Exception as e:
        logger.warning(f"HuggingFace error: {e}")
        return []


# ─────────────────────────────────────────────
# Pipeline unificado de busca
# ─────────────────────────────────────────────

def search_all(
    query: str,
    category: str = '',
    include_datagov: bool = True,
    include_hf: bool = True,
    limit_local: int = 10,
    limit_remote: int = 10,
    parallel: bool = True,
) -> dict:
    """
    Busca unificada em todas as fontes disponíveis.

    Retorna:
      {
        'query': str,
        'total': int,
        'results': {
          'local':     [dict, ...],  # catálogo curado
          'datagov':   [dict, ...],  # data.gov CKAN
          'huggingface': [dict, ...],
        },
        'audit': [str, ...],  # trilha para PhD Auditor L5
        'timestamp': str,
      }
    """
    report = {
        'query':     query,
        'category':  category,
        'total':     0,
        'results':   {'local': [], 'datagov': [], 'huggingface': []},
        'audit':     [],
        'timestamp': datetime.now().isoformat(),
    }

    # 1 — Catálogo local
    catalog = load_catalog()
    local_res = search_local(catalog, query=query, category=category, limit=limit_local)
    report['results']['local'] = local_res
    report['audit'].append(f"Catálogo local: {len(local_res)} resultados")

    if parallel and (include_datagov or include_hf):
        tasks = {}
        with ThreadPoolExecutor(max_workers=2) as executor:
            if include_datagov:
                tasks['datagov'] = executor.submit(search_datagov, query, limit_remote)
            if include_hf:
                tasks['huggingface'] = executor.submit(search_huggingface, query, limit_remote)
            for key, future in tasks.items():
                try:
                    res = future.result(timeout=20)
                    report['results'][key] = res
                    report['audit'].append(f"{key}: {len(res)} resultados")
                except Exception as e:
                    report['audit'].append(f"{key}: erro — {e}")
    else:
        if include_datagov:
            res = search_datagov(query, limit_remote)
            report['results']['datagov'] = res
            report['audit'].append(f"data.gov: {len(res)} resultados")
        if include_hf:
            res = search_huggingface(query, limit_remote)
            report['results']['huggingface'] = res
            report['audit'].append(f"HuggingFace: {len(res)} resultados")

    report['total'] = sum(len(v) for v in report['results'].values())
    _log_evolve(report)
    return report


# ─────────────────────────────────────────────
# Formatação de resultados
# ─────────────────────────────────────────────

def format_results_table(report: dict) -> str:
    """Gera tabela Markdown com todos os resultados para uso em artigos."""
    lines = [
        f"## Datasets encontrados: '{report['query']}'",
        f"> Busca realizada em: {report['timestamp']} | Total: {report['total']} datasets\n",
        "| # | Nome | Categoria | Cloud | Vintage | Link |",
        "|:---:|---|---|:---:|:---:|---|",
    ]
    i = 1
    for source, datasets in report['results'].items():
        for d in datasets:
            name    = d.get('name','')[:40]
            cat     = d.get('category','')[:20]
            cloud   = d.get('cloud','')[:12]
            vintage = d.get('vintage','NA')
            link    = d.get('link','')
            lines.append(f"| {i} | {name} | {cat} | {cloud} | {vintage} | [link]({link}) |")
            i += 1
    return '\n'.join(lines)


def format_citation_abnt(dataset: dict) -> str:
    """Gera citação ABNT NBR 6023:2025 para dataset (dado como fonte de dados)."""
    name    = dataset.get('name', '[s.n.]')
    about   = dataset.get('about', '')
    link    = dataset.get('link', '')
    vintage = dataset.get('vintage', 'NA')
    cloud   = dataset.get('cloud', '')
    year    = vintage if vintage and vintage != 'NA' else datetime.now().year

    cloud_str = f" Disponível em: {cloud}." if cloud else ''
    return (
        f"{name.upper()}. {about}. "
        f"[Dataset]. {year}.{cloud_str} "
        f"Acesso em: <{link}>."
    )


def export_json(report: dict, output_path: str = '') -> str:
    """Exporta relatório de busca em JSON para integração com SEEKER."""
    if not output_path:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = str(EVOLVE_DIR / f'dataset-search-{ts}.json')
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info(f"Exportado: {output_path}")
    return output_path


# ─────────────────────────────────────────────
# Estatísticas do catálogo
# ─────────────────────────────────────────────

def catalog_stats(datasets: list[dict]) -> dict:
    """Gera estatísticas descritivas do catálogo."""
    from collections import Counter
    cats    = Counter(d['category'] for d in datasets)
    clouds  = Counter(d['cloud'] for d in datasets if d['cloud'])
    decades = Counter(
        str(int(d['vintage'])//10*10)+'s'
        for d in datasets
        if d['vintage'] and d['vintage'] != 'NA' and d['vintage'].isdigit()
    )
    return {
        'total':       len(datasets),
        'categories':  dict(cats.most_common()),
        'clouds':      dict(clouds.most_common()),
        'by_decade':   dict(decades.most_common()),
        'with_github': sum(1 for d in datasets if 'GitHub' in d.get('cloud','')),
        'with_amazon': sum(1 for d in datasets if 'Amazon' in d.get('cloud','')),
        'with_vintage': sum(1 for d in datasets if d.get('vintage','NA') != 'NA' and d['vintage']),
    }


# ─────────────────────────────────────────────
# Observabilidade
# ─────────────────────────────────────────────

def _log_evolve(report: dict) -> None:
    log_path = EVOLVE_DIR / 'dataset-search-observability.jsonl'
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        'timestamp': report['timestamp'],
        'query':     report['query'],
        'total':     report['total'],
        'by_source': {k: len(v) for k, v in report['results'].items()},
    }
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='SEEKER DatasetSearch v1.0 — OpenCode Ecosystem'
    )
    parser.add_argument('-q', '--query',    metavar='TEXTO',  default='', help='Palavras-chave de busca')
    parser.add_argument('-c', '--category', metavar='CAT',    default='', help='Filtro de categoria')
    parser.add_argument('-t', '--theme',    metavar='TEMA',   default='', help='Tema semântico: nlp, geo, ml, social, gov, transport, energy, biology')
    parser.add_argument('--no-datagov',  action='store_true', help='Desativar busca no data.gov')
    parser.add_argument('--no-hf',       action='store_true', help='Desativar busca no HuggingFace')
    parser.add_argument('-l', '--limit',  metavar='N', type=int, default=10)
    parser.add_argument('--stats',        action='store_true', help='Exibir estatísticas do catálogo local')
    parser.add_argument('--export',       metavar='FILE',     default='', help='Exportar resultados em JSON')
    parser.add_argument('--markdown',     action='store_true', help='Exibir tabela Markdown')
    args = parser.parse_args()

    catalog = load_catalog()

    if args.stats:
        stats = catalog_stats(catalog)
        print(f"\n{'='*50}")
        print(f"  Catálogo: {stats['total']} datasets")
        print(f"{'='*50}")
        print("\n  Por categoria:")
        for cat, n in stats['categories'].items():
            print(f"    {cat:<25} {n:>3}")
        print("\n  Por cloud:")
        for cloud, n in stats['cloud'].items() if hasattr(stats,'cloud') else stats['clouds'].items():
            print(f"    {cloud:<15} {n:>3}")
        print(f"\n  Com vintage: {stats['with_vintage']}")
        print(f"  GitHub: {stats['with_github']} | Amazon: {stats['with_amazon']}")
        return

    if args.theme and not args.query:
        results = search_by_theme(catalog, args.theme, args.limit)
        print(f"\n[Theme: {args.theme}] {len(results)} datasets encontrados:\n")
        for i, d in enumerate(results, 1):
            print(f"  {i:>2}. [{d['category']}] {d['name']}")
            print(f"       {d['about'][:80]}")
            print(f"       {d['link']}")
            if d.get('cloud'): print(f"       Cloud: {d['cloud']}")
            if d.get('vintage') and d['vintage'] != 'NA': print(f"       Vintage: {d['vintage']}")
        return

    # Busca unificada
    report = search_all(
        query=args.query or args.theme,
        category=args.category,
        include_datagov=not args.no_datagov,
        include_hf=not args.no_hf,
        limit_local=args.limit,
        limit_remote=args.limit,
    )

    print(f"\n{'='*60}")
    print(f"  Busca: '{args.query}' | Total: {report['total']} datasets")
    print(f"{'='*60}")

    for source, datasets in report['results'].items():
        if not datasets: continue
        print(f"\n  [{source.upper()}] — {len(datasets)} resultados")
        for i, d in enumerate(datasets, 1):
            print(f"    {i:>2}. {d['name'][:50]}")
            if d.get('about'): print(f"        {d['about'][:80]}")
            print(f"        {d.get('link','')[:80]}")

    print(f"\n  Auditoria:")
    for step in report.get('audit', []):
        print(f"    → {step}")

    if args.markdown:
        print('\n' + format_results_table(report))

    if args.export:
        path = export_json(report, args.export)
        print(f"\n  JSON exportado: {path}")
    elif report['total'] > 0:
        path = export_json(report)
        print(f"\n  JSON exportado automaticamente: {path}")


if __name__ == '__main__':
    main()
