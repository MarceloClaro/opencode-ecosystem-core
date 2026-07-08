"""
Thesis Enricher — Enriquece teses com pesquisa web real via Antigravity Bridge.

Pipeline:
  1. Para cada conceito da tese, busca web via Antigravity
  2. Extrai abstracts de URLs encontradas
  3. Cache persistente em disco para evitar re-busca
  4. Fallback com dados simulados quando offline

SPEC-935-R89 — R89 do OpenCode Ecosystem Core.
"""

import hashlib
import json
import logging
import os
import time
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Dados simulados de fallback para cada conceito
FALLBACK_DATA = {
    "quantum": {
        "title": "Advances in Quantum Computing",
        "url": "https://arxiv.org/abs/quant-ph/2024",
        "snippet": "Recent advances in quantum computing algorithms and applications.",
    },
    "ethics": {
        "title": "Machine Ethics: Foundations and Applications",
        "url": "https://arxiv.org/abs/cs.AI/2024",
        "snippet": "A comprehensive survey of machine ethics frameworks.",
    },
    "ai": {
        "title": "Responsible Artificial Intelligence",
        "url": "https://arxiv.org/abs/cs.AI/2023",
        "snippet": "Principles and practices for responsible AI development.",
    },
    "algorithm": {
        "title": "Algorithmic Fairness: A Survey",
        "url": "https://arxiv.org/abs/cs.LG/2024",
        "snippet": "Survey of algorithmic fairness definitions and methods.",
    },
    "learning": {
        "title": "Deep Learning: State of the Art",
        "url": "https://arxiv.org/abs/cs.LG/2024",
        "snippet": "Overview of deep learning techniques and architectures.",
    },
    "data": {
        "title": "Big Data Analytics in Research",
        "url": "https://arxiv.org/abs/cs.DB/2024",
        "snippet": "Methods for large-scale data analysis in academic research.",
    },
    "health": {
        "title": "AI in Healthcare: A Systematic Review",
        "url": "https://arxiv.org/abs/cs.AI/2024",
        "snippet": "Systematic review of artificial intelligence applications in healthcare.",
    },
    "system": {
        "title": "Complex Systems: Theory and Applications",
        "url": "https://arxiv.org/abs/nlin.AO/2024",
        "snippet": "Theory and applications of complex adaptive systems.",
    },
    "network": {
        "title": "Neural Network Architectures: A Taxonomy",
        "url": "https://arxiv.org/abs/cs.NE/2024",
        "snippet": "Taxonomy and comparison of neural network architectures.",
    },
    "model": {
        "title": "Formal Methods in System Design",
        "url": "https://arxiv.org/abs/cs.SE/2024",
        "snippet": "Formal verification and modeling of computational systems.",
    },
}


def _concept_to_key(concept: str) -> str:
    """Normaliza conceito para nome de arquivo seguro."""
    safe = concept.lower().strip().replace(" ", "_")
    safe = "".join(c for c in safe if c.isalnum() or c in "_-")
    return safe or "concept"


class ThesisEnricher:
    """Enriquece teses com pesquisa web academica.

    Args:
        cache_dir: Diretorio para cache persistente.
        ttl_days: Dias antes de re-buscar um conceito.
        lang: Idioma das descricoes ('pt' ou 'en').
    """

    def __init__(
        self,
        cache_dir: str = "cache/enrich",
        ttl_days: int = 7,
        lang: str = "pt",
    ):
        self.cache_dir = cache_dir
        self.ttl_days = ttl_days
        self.lang = lang
        self._concept_cache: dict = {}
        os.makedirs(cache_dir, exist_ok=True)

    def enrich(self, thesis: dict) -> dict:
        """Enriquece uma unica tese com dados de pesquisa web.

        Args:
            thesis: Dict com 'thesis_id', 'title', 'concepts' (lista de str).

        Returns:
            Dict com dados enriquecidos.
        """
        thesis_id = thesis.get("thesis_id", "unknown")
        concepts = thesis.get("concepts", [])
        title = thesis.get("title", "")

        if not concepts:
            return {
                "thesis_id": thesis_id,
                "title": title,
                "concepts_enriched": [],
                "fallback_used": False,
                "enriched_at": datetime.now().isoformat(),
            }

        enriched_concepts = []
        fallback_used = False

        for concept in concepts:
            enriched = self._enrich_concept(concept)
            if enriched.get("source") == "fallback":
                fallback_used = True
            enriched_concepts.append(enriched)

        return {
            "thesis_id": thesis_id,
            "title": title,
            "concepts_enriched": enriched_concepts,
            "fallback_used": fallback_used,
            "enriched_at": datetime.now().isoformat(),
        }

    def batch_enrich(self, theses: list) -> list:
        """Enriquece multiplas teses."""
        return [self.enrich(t) for t in theses]

    def fetch_abstract(self, url: str) -> Optional[dict]:
        """Busca abstract de um paper via Antigravity.

        Returns:
            Dict com 'url', 'abstract', 'source' ou None.
        """
        try:
            return self._fetch_abstract(url)
        except Exception as e:
            logger.warning("R89 Erro ao buscar abstract de %s: %s", url, e)
            return None

    def _enrich_concept(self, concept: str) -> dict:
        """Enriquece um unico conceito."""
        # Tenta cache primeiro
        cached = self._load_from_cache(concept)
        if cached:
            logger.debug("R89 Cache hit para conceito: %s", concept)
            return cached

        # Tenta busca web
        try:
            result = self._search_concept(concept)
            if result and result.get("results"):
                self._save_to_cache(concept, result)
                return result
        except Exception as e:
            logger.warning("R89 Erro na busca de '%s': %s", concept, e)

        # Fallback
        fallback = self._fallback_for(concept)
        self._save_to_cache(concept, fallback)
        return fallback

    def _search_concept(self, concept: str) -> Optional[dict]:
        """Busca web por um conceito.

        Tenta o Antigravity Bridge via opencode run com pesquisa web.
        """
        # Constroi query de busca academica
        query = f"academic paper {concept} 2024 2025 site:arxiv.org OR site:scholar.google.com"
        prompt_pt = (
            f"Pesquise sobre o conceito academico '{concept}' e retorne "
            f"um JSON com resultados reais. "
            f"Formato: {{\"query\": \"{concept}\", \"results\": ["
            f"{{\"title\": \"...\", \"url\": \"...\", \"snippet\": \"...\", \"source\": \"web\"}}"
            f"], \"total_found\": N}}"
        )

        try:
            import subprocess
            cmd = [
                "opencode", "run",
                "--model", "opencode/north-mini-code-free",
                "--format", "json",
                prompt_pt,
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=45
            )
            if result.returncode == 0 and result.stdout.strip():
                # Tenta extrair JSON da resposta
                data = self._extract_json(result.stdout)
                if data and isinstance(data, dict) and data.get("results"):
                    data["source"] = "antigravity_web"
                    return data
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.debug("R89 OpenCode CLI: %s", e)

        # Se o OpenCode nao funcionou, retorna dados simulados com marcacao
        return self._fallback_for(concept)

    def _fetch_abstract(self, url: str) -> dict:
        """Busca abstract de uma URL via Antigravity.

        Tenta o comando 'opencode run' para extrair conteudo.
        """
        prompt = (
            f"Acesse a URL {url} e extraia o abstract/resumo do paper academico. "
            f"Retorne APENAS o texto do abstract, sem comentarios."
        )

        try:
            import subprocess
            cmd = [
                "opencode", "run",
                "--model", "opencode/north-mini-code-free",
                prompt,
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                abstract = result.stdout.strip()
                if abstract and len(abstract) > 20:
                    return {
                        "url": url,
                        "abstract": abstract,
                        "source": "antigravity_read_url",
                    }
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.debug("R89 Fetch abstract: %s", e)

        return {
            "url": url,
            "abstract": f"Abstract not available for {url}",
            "source": "fallback",
        }

    def _fallback_for(self, concept: str) -> dict:
        """Gera dados de fallback para um conceito."""
        concept_lower = concept.lower().strip()

        # Tenta match exato
        for key, data in FALLBACK_DATA.items():
            if key in concept_lower or concept_lower in key:
                return {
                    "query": concept,
                    "results": [
                        {
                            "title": data["title"],
                            "url": data["url"],
                            "snippet": data["snippet"],
                            "source": "fallback",
                        }
                    ],
                    "total_found": 1,
                    "source": "fallback",
                }

        # Fallback generico
        return {
            "query": concept,
            "results": [
                {
                    "title": f"Research on {concept.title()}",
                    "url": f"https://scholar.google.com/scholar?q={concept.replace(' ', '+')}",
                    "snippet": f"Academic research related to {concept}.",
                    "source": "fallback",
                }
            ],
            "total_found": 1,
            "source": "fallback",
        }

    def _load_from_cache(self, concept: str) -> Optional[dict]:
        """Carrega resultado do cache se ainda valido."""
        key = _concept_to_key(concept)
        cache_path = os.path.join(self.cache_dir, f"{key}.json")

        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, "r") as f:
                data = json.load(f)

            # Verifica TTL
            cached_at = data.get("cached_at", 0)
            if time.time() - cached_at > self.ttl_days * 86400:
                logger.debug("R89 Cache expirado para: %s", concept)
                return None

            data["source"] = "cache"
            return data
        except (json.JSONDecodeError, OSError) as e:
            logger.debug("R89 Erro ao ler cache: %s", e)
            return None

    def _save_to_cache(self, concept: str, data: dict):
        """Salva resultado no cache."""
        key = _concept_to_key(concept)
        cache_path = os.path.join(self.cache_dir, f"{key}.json")

        try:
            data["cached_at"] = time.time()
            with open(cache_path, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.warning("R89 Erro ao salvar cache: %s", e)

    @staticmethod
    def _extract_json(text: str) -> Optional[dict]:
        """Extrai JSON de texto com possivel ruido."""
        import re
        # Tenta encontrar { ... } com conteudo JSON
        match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # Tenta parse do texto completo
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
