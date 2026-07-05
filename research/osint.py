# -*- coding: utf-8 -*-
"""
OSINT LinkTree — Mapeamento de referências acadêmicas obscuras
==============================================================
Inspirado no módulo linktree.py do TorBot: constrói uma árvore de links
(LinkTree) a partir de referências bibliográficas, mapeando a "Dark Web"
acadêmica (artigos não indexados, preprints obscuros, repositórios) e
extraindo metadados ocultos.
"""
from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class LinkNode:
    url: str
    depth: int
    title: str = ""
    is_academic: bool = False
    is_darkweb: bool = False
    children: List["LinkNode"] = field(default_factory=list)


class OsintLinkTree:
    """
    Construtor de árvores de links para OSINT acadêmico.
    Simula a extração de links de referências e a classificação de domínios.
    """

    ACADEMIC_TLDS = {".edu", ".ac.uk", ".edu.br", ".gov"}
    ACADEMIC_DOMAINS = {"arxiv.org", "doi.org", "researchgate.net", "scielo.br"}
    DARKWEB_TLDS = {".onion", ".i2p"}

    def __init__(self, max_depth: int = 2):
        self.max_depth = max_depth
        self.visited: Set[str] = set()

    def _classify_url(self, url: str) -> tuple[bool, bool]:
        """Retorna (is_academic, is_darkweb)."""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            if not domain:
                return False, False
            
            is_dark = any(domain.endswith(tld) for tld in self.DARKWEB_TLDS)
            is_acad = (
                any(domain.endswith(tld) for tld in self.ACADEMIC_TLDS) or
                any(d in domain for d in self.ACADEMIC_DOMAINS)
            )
            return is_acad, is_dark
        except Exception:
            return False, False

    def _extract_links(self, text: str) -> List[str]:
        """Extrai URLs de um texto bruto (simulação de scraping)."""
        # Regex simplificada para URLs
        pattern = r"https?://[^\s<>\"']+|[a-zA-Z0-9.-]+\.onion[^\s<>\"']*"
        return list(set(re.findall(pattern, text)))

    def build_tree(self, root_url: str, content: str, current_depth: int = 0) -> LinkNode:
        """Constrói a árvore recursivamente a partir do conteúdo."""
        is_acad, is_dark = self._classify_url(root_url)
        node = LinkNode(
            url=root_url,
            depth=current_depth,
            is_academic=is_acad,
            is_darkweb=is_dark
        )
        self.visited.add(root_url)

        if current_depth < self.max_depth:
            links = self._extract_links(content)
            for link in links:
                if link not in self.visited:
                    # Em um cenário real, faríamos um GET no link aqui.
                    # Como é simulação OSINT, criamos nós folha vazios.
                    child_acad, child_dark = self._classify_url(link)
                    child = LinkNode(
                        url=link,
                        depth=current_depth + 1,
                        is_academic=child_acad,
                        is_darkweb=child_dark
                    )
                    self.visited.add(link)
                    node.children.append(child)

        return node

    def analyze_references(self, references_text: str) -> Dict[str, Any]:
        """
        Analisa um bloco de referências bibliográficas e retorna estatísticas
        da "Dark Web" acadêmica encontrada.
        """
        links = self._extract_links(references_text)
        trees = []
        stats = {"total_links": len(links), "academic": 0, "darkweb": 0, "obscure": 0}

        for link in links:
            is_acad, is_dark = self._classify_url(link)
            if is_acad: stats["academic"] += 1
            if is_dark: stats["darkweb"] += 1
            if not is_acad and not is_dark: stats["obscure"] += 1
            
            # Constrói árvore de profundidade 1 para cada link raiz
            trees.append(self.build_tree(link, "", current_depth=0))

        return {
            "stats": stats,
            "trees_built": len(trees),
            "recommendation": (
                "Atenção: Fontes obscuras detectadas. Recomenda-se validação cruzada."
                if stats["obscure"] > stats["academic"] else
                "Fontes predominantemente acadêmicas e rastreáveis."
            )
        }
