"""Integracao Academica — SPEC-935 R86.

Integracoes com fontes externas:
1. arXiv API: busca de papers reais
2. Semantic Scholar API: metricas de citacao e influencia
3. Sci-Hub: verificacao de disponibilidade de acesso aberto
"""

from __future__ import annotations
import json
import logging
import time
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# =========================================================================
# Constantes
# =========================================================================

ARXIV_API_URL = "http://export.arxiv.org/api/query"
SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
SCI_HUB_DOMAINS = ["sci-hub.se", "sci-hub.ru", "sci-hub.st", "sci-hub.ee"]
USER_AGENT = "OpenCodeEcosystem/1.0 (Academic Integration; +https://github.com/MarceloClaro/opencode-ecosystem-core)"


# =========================================================================
# 1. arXiv API
# =========================================================================

def search_arxiv(query: str, max_results: int = 10) -> List[Dict]:
    """Busca papers no arXiv.
    
    Args:
        query: Termo de busca
        max_results: Maximo de resultados (padrao 10, max 100)
    
    Returns:
        Lista de dicts com id, title, summary, authors, category
    """
    try:
        # Formatar query
        encoded = urllib.parse.quote(query.replace(' ', '+'))
        url = f"{ARXIV_API_URL}?search_query=all:{encoded}&max_results={max_results}&sortBy=relevance"
        
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read().decode()
        
        return _parse_arxiv_xml(xml_data)
    
    except Exception as e:
        logger.warning(f"arXiv search failed for '{query}': {e}")
        return []


def _parse_arxiv_xml(xml_data: str) -> List[Dict]:
    """Parseia XML de resposta do arXiv."""
    results = []
    
    try:
        root = ET.fromstring(xml_data)
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom',
        }
        
        for entry in root.findall('atom:entry', ns):
            paper = {
                'id': entry.findtext('atom:id', '', ns).strip(),
                'title': ' '.join(entry.findtext('atom:title', '', ns).strip().split()),
                'summary': ' '.join(entry.findtext('atom:summary', '', ns).strip().split())[:500],
                'authors': [],
                'category': '',
                'published': entry.findtext('atom:published', '', ns).strip()[:10],
            }
            
            # Autores
            for author in entry.findall('atom:author', ns):
                name = author.findtext('atom:name', '', ns).strip()
                if name:
                    paper['authors'].append(name)
            
            # Categoria primaria
            primary = entry.find('arxiv:primary_category', ns)
            if primary is not None:
                paper['category'] = primary.get('term', '')
            
            results.append(paper)
    
    except ET.ParseError as e:
        logger.warning(f"Failed to parse arXiv XML: {e}")
    
    return results


# =========================================================================
# 2. Semantic Scholar API
# =========================================================================

def search_semantic_scholar(query: str, limit: int = 5) -> List[Dict]:
    """Busca papers no Semantic Scholar.
    
    Args:
        query: Termo de busca
        limit: Maximo de resultados
    
    Returns:
        Lista de dicts com paperId, title, citationCount, venue, year, doi
    """
    try:
        params = urllib.parse.urlencode({
            'query': query,
            'limit': min(limit, 10),
            'fields': 'title,citationCount,venue,year,externalIds',
        })
        url = f"{SEMANTIC_SCHOLAR_URL}?{params}"
        
        headers = {"User-Agent": USER_AGENT}
        api_key = os.environ.get("S2_API_KEY", "")
        if api_key:
            headers["x-api-key"] = api_key
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        
        results = []
        for paper in data.get('data', []):
            ext_ids = paper.get('externalIds', {}) or {}
            results.append({
                'paperId': paper.get('paperId', ''),
                'title': paper.get('title', ''),
                'citationCount': paper.get('citationCount', 0),
                'venue': paper.get('venue', ''),
                'year': paper.get('year', 0),
                'doi': ext_ids.get('DOI', ''),
            })
        
        return results
    
    except Exception as e:
        logger.warning(f"Semantic Scholar search failed for '{query}': {e}")
        return []


# =========================================================================
# 3. Sci-Hub — Verificacao de Disponibilidade
# =========================================================================

def check_sci_hub(doi: str) -> Dict:
    """Verifica se um paper esta disponivel via Sci-Hub.
    
    Tenta multiplos dominios do Sci-Hub em sequencia.
    
    Args:
        doi: DOI do paper
    
    Returns:
        Dict com available (bool), doi, domain (se encontrado)
    """
    for domain in SCI_HUB_DOMAINS:
        try:
            url = f"https://{domain}/{doi}"
            req = urllib.request.Request(url, headers={
                "User-Agent": USER_AGENT,
            })
            
            with urllib.request.urlopen(req, timeout=5) as resp:
                # Se retorna conteudo, esta disponivel
                content = resp.read()
                if resp.status == 200 and len(content) > 1000:
                    logger.info(f"Sci-Hub: {doi} disponivel via {domain}")
                    return {
                        'available': True,
                        'doi': doi,
                        'domain': domain,
                        'status': resp.status,
                    }
        
        except Exception:
            continue
    
    logger.info(f"Sci-Hub: {doi} nao encontrado em nenhum dominio")
    return {
        'available': False,
        'doi': doi,
        'domain': None,
        'status': None,
    }


# =========================================================================
# 4. LiteratureBacking — Score de Suporte Bibliografico
# =========================================================================

@dataclass
class LiteratureBacking:
    """Score de suporte bibliografico para uma query/tese.
    
    Combina resultados de arXiv, Semantic Scholar e Sci-Hub
    em um score unificado de 0 a 1.
    """
    query: str
    arxiv_results: List[Dict] = field(default_factory=list)
    semantic_results: List[Dict] = field(default_factory=list)
    sci_hub_results: List[Dict] = field(default_factory=list)
    
    def calculate_score(self) -> float:
        """Calcula score de suporte bibliografico.
        
        Fatores:
        - Presenca de papers no arXiv (0.3)
        - Citacoes no Semantic Scholar (0.4)
        - Disponibilidade via Sci-Hub (0.3)
        """
        score = 0.0
        
        # arXiv: quanto mais papers, melhor
        n_arxiv = len(self.arxiv_results)
        arxiv_score = min(1.0, n_arxiv / 5.0) * 0.3
        score += arxiv_score
        
        # Semantic Scholar: citacoes
        if self.semantic_results:
            total_citations = sum(
                p.get('citationCount', 0) for p in self.semantic_results
            )
            citations_score = min(1.0, total_citations / 200.0) * 0.4
            score += citations_score
        else:
            score += 0.0  # sem resultados = sem score
        
        # Sci-Hub: proporcao de papers disponiveis
        if self.sci_hub_results:
            available = sum(1 for r in self.sci_hub_results if r.get('available'))
            sh_score = (available / len(self.sci_hub_results)) * 0.3
            score += sh_score
        else:
            score += 0.15  # score conservador se nao testamos
        
        return min(1.0, max(0.0, score))


# =========================================================================
# 5. AcademicIntegrator — Orquestrador Principal
# =========================================================================

class AcademicIntegrator:
    """Orquestrador das integracoes academicas.
    
    Para uma query/conceito, busca em todas as fontes e retorna
    um resultado consolidado com backing score.
    """
    
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
    
    def search(self, query: str, offline: bool = False) -> Dict:
        """Busca papers em todas as fontes para uma query.
        
        Args:
            query: Termo de busca
            offline: Se True, nao faz chamadas de rede (retorna score medio)
        
        Returns:
            Dict com backing_score, papers, sources
        """
        # Cache
        cache_key = query.lower().strip()
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        if offline:
            result = {
                'query': query,
                'backing_score': 0.5,
                'papers': [],
                'arxiv_count': 0,
                'semantic_count': 0,
                'sci_hub_available': 0,
                'offline': True,
                'timestamp': time.time(),
            }
            self._cache[cache_key] = result
            return result
        
        # Busca em paralelo (simplificada — sequencial)
        arxiv_results = search_arxiv(query, max_results=5)
        semantic_results = search_semantic_scholar(query, limit=5)
        
        # Sci-Hub: verificar DOIs encontrados
        sci_hub_results = []
        for paper in semantic_results[:3]:
            doi = paper.get('doi', '')
            if doi:
                sh = check_sci_hub(doi)
                sci_hub_results.append(sh)
        
        # Calcular backing score
        lb = LiteratureBacking(
            query=query,
            arxiv_results=arxiv_results,
            semantic_results=semantic_results,
            sci_hub_results=sci_hub_results,
        )
        backing_score = lb.calculate_score()
        
        # Consolidar papers
        all_papers = []
        seen_ids = set()
        
        for p in arxiv_results:
            pid = p.get('id', '')
            if pid not in seen_ids:
                seen_ids.add(pid)
                all_papers.append({
                    'source': 'arxiv',
                    'id': pid,
                    'title': p.get('title', ''),
                    'authors': p.get('authors', []),
                    'category': p.get('category', ''),
                })
        
        for p in semantic_results:
            pid = p.get('paperId', '')
            if pid not in seen_ids and pid:
                seen_ids.add(pid)
                all_papers.append({
                    'source': 'semantic_scholar',
                    'id': pid,
                    'title': p.get('title', ''),
                    'citationCount': p.get('citationCount', 0),
                    'venue': p.get('venue', ''),
                    'doi': p.get('doi', ''),
                })
        
        result = {
            'query': query,
            'backing_score': round(backing_score, 4),
            'papers': all_papers,
            'arxiv_count': len(arxiv_results),
            'semantic_count': len(semantic_results),
            'sci_hub_available': sum(1 for r in sci_hub_results if r.get('available')),
            'offline': False,
            'timestamp': time.time(),
        }
        
        self._cache[cache_key] = result
        return result
    
    def search_thesis(self, thesis_title: str, thesis_concepts: List[str]) -> Dict:
        """Busca papers para uma tese completa.
        
        Combina o titulo com os conceitos para uma busca mais abrangente.
        """
        # Query combinada
        query = f"{thesis_title} {' '.join(thesis_concepts[:3])}"
        return self.search(query)
    
    def clear_cache(self):
        """Limpa o cache de resultados."""
        self._cache.clear()
