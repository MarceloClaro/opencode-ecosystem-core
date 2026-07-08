"""
Visual Abstract Generator — Gera figuras academicas para teses via Antigravity Image.

Pipeline:
  1. Seleciona top N teses por composite_score
  2. Para cada tese, gera descricao visual concisa
  3. Tenta Antigravity Image Generator
  4. Fallback: diagrama SVG conceitual
  5. Cache por hash do conteudo
  6. Indice JSON com metadados

SPEC-935-R90 — R90 do OpenCode Ecosystem Core.
"""

import hashlib
import json
import logging
import os
import time
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class VisualAbstractGenerator:
    """Gerador de abstracts visuais para teses academicas.

    Args:
        output_dir: Diretorio para salvar as imagens.
        cache_dir: Diretorio para cache de metadados.
        style: Estilo visual ('professional', 'diagram', 'academic').
        lang: Idioma ('pt' ou 'en').
    """

    def __init__(
        self,
        output_dir: str = "academic/visual_abstracts",
        cache_dir: str = "cache/visual_abstracts",
        style: str = "academic",
        lang: str = "pt",
    ):
        self.output_dir = output_dir
        self.cache_dir = cache_dir
        self.style = style
        self.lang = lang
        self._cache: dict = {}
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(cache_dir, exist_ok=True)

    def generate(self, thesis: dict) -> dict:
        """Gera visual abstract para uma tese.

        Args:
            thesis: Dict com 'thesis_id', 'title', 'hypothesis', etc.

        Returns:
            Dict com resultado da geracao.
        """
        content_hash = self._content_hash(thesis)

        # Verifica cache
        cached = self._cache.get(content_hash)
        if cached:
            logger.debug("R90 Cache hit: %s", thesis.get("thesis_id"))
            return cached

        thesis_id = thesis.get("thesis_id", "unknown")
        title = thesis.get("title", "Untitled")

        # Tenta gerar imagem via Antigravity
        try:
            result = self._generate_image(thesis)
            if result and result.get("success"):
                result["generated_at"] = datetime.now().isoformat()
                self._cache[content_hash] = result
                return result
        except Exception as e:
            logger.warning("R90 Antigravity Image falhou para %s: %s", thesis_id, e)

        # Fallback: diagrama SVG
        result = self._generate_svg_fallback(thesis)
        result["generated_at"] = datetime.now().isoformat()
        self._cache[content_hash] = result
        return result

    def generate_all(self, theses: list, top_n: int = 5) -> list:
        """Gera visuals para as top N teses."""
        selected = self._select_top(theses, top_n)
        return [self.generate(t) for t in selected]

    def write_index(self, results: list) -> str:
        """Escreve arquivo de indice JSON com metadados das imagens."""
        index = {
            "generated_at": datetime.now().isoformat(),
            "total": len(results),
            "style": self.style,
            "visual_abstracts": results,
        }
        index_path = os.path.join(self.output_dir, "index.json")
        with open(index_path, "w") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        logger.info("R90 Indice escrito em %s", index_path)
        return index_path

    def _generate_image(self, thesis: dict) -> dict:
        """Tenta gerar imagem via Antigravity Image Generator.

        Tenta enviar solicitacao ao Antigravity Bridge.
        Se nao for possivel (sem acesso a ferramenta), retorna None
        para ativar o fallback SVG.

        Returns dict com sucesso ou None/lanca excecao para fallback.
        """
        thesis_id = thesis.get("thesis_id", "unknown")
        description = self._build_description(thesis)
        filename = f"{thesis_id}_{self._content_hash(thesis)[:8]}.svg"
        output_path = os.path.join(self.output_dir, filename)

        # Se o arquivo SVG ja existe, retorna sucesso
        if os.path.exists(output_path):
            logger.info("R90 Imagem ja existe: %s", output_path)
            return {
                "thesis_id": thesis_id,
                "image_path": output_path,
                "description": description,
                "source": "cache",
                "success": True,
                "file_format": "svg",
            }

        # Nao temos acesso a API de image generation do Python,
        # entao ativamos fallback SVG que gera arquivos reais.
        # A geracao via Antigravity e feita pelo orquestrador (AI assistant).
        logger.info(
            "R90 Usando fallback SVG para %s (antigravity_image via orquestrador)",
            thesis_id,
        )
        return None

    def _generate_svg_fallback(self, thesis: dict) -> dict:
        """Gera diagrama SVG conceitual como fallback.

        Cria um SVG simples representando a estrutura da tese.
        """
        thesis_id = thesis.get("thesis_id", "unknown")
        title = thesis.get("title", "Untitled")
        hypothesis = thesis.get("hypothesis", "")
        score = thesis.get("composite_score", 0)
        faculties = thesis.get("faculties_involved", [])

        filename = f"{thesis_id}_fallback.svg"
        output_path = os.path.join(self.output_dir, filename)

        # Cria SVG com diagrama conceitual
        faculties_str = ", ".join(faculties) if faculties else "General"
        svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 400" width="500" height="400">
  <rect width="500" height="400" fill="#0f172a" rx="8"/>
  <text x="250" y="40" text-anchor="middle" fill="#38bdf8" font-family="sans-serif" font-size="16" font-weight="bold">
    Visual Abstract
  </text>
  <text x="250" y="70" text-anchor="middle" fill="#e2e8f0" font-family="sans-serif" font-size="12">
    {self._xml_escape(title[:60])}
  </text>
  <line x1="50" y1="85" x2="450" y2="85" stroke="#334155" stroke-width="1"/>
  <text x="30" y="115" fill="#94a3b8" font-family="sans-serif" font-size="11">
    Score: {score:.2f}
  </text>
  <text x="30" y="140" fill="#94a3b8" font-family="sans-serif" font-size="11">
    Faculdades: {self._xml_escape(faculties_str)}
  </text>
  <text x="30" y="170" fill="#38bdf8" font-family="sans-serif" font-size="12" font-weight="bold">
    Hipotese:
  </text>
  <text x="30" y="195" fill="#cbd5e1" font-family="sans-serif" font-size="11">
    {self._xml_escape(hypothesis[:100])}
  </text>
  <line x1="50" y1="215" x2="450" y2="215" stroke="#334155" stroke-width="1"/>
  <rect x="50" y="235" width="180" height="100" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="140" y="260" text-anchor="middle" fill="#38bdf8" font-family="sans-serif" font-size="10" font-weight="bold">
    Conceitos
  </text>
  <text x="140" y="285" text-anchor="middle" fill="#94a3b8" font-family="sans-serif" font-size="9">
    {self._xml_escape(self._extract_keywords(title))}
  </text>
  <rect x="270" y="235" width="180" height="100" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="360" y="260" text-anchor="middle" fill="#38bdf8" font-family="sans-serif" font-size="10" font-weight="bold">
    Metodologia
  </text>
  <text x="360" y="285" text-anchor="middle" fill="#94a3b8" font-family="sans-serif" font-size="9">
    {self._xml_escape(self._detect_methodology(hypothesis))}
  </text>
  <text x="250" y="380" text-anchor="middle" fill="#475569" font-family="sans-serif" font-size="8">
    Generated by OpenCode Synthetic University | {datetime.now().strftime('%Y-%m-%d')}
  </text>
</svg>"""

        with open(output_path, "w") as f:
            f.write(svg_content)

        logger.info("R90 SVG fallback gerado: %s", filename)

        return {
            "thesis_id": thesis_id,
            "image_path": output_path,
            "description": f"SVG diagram for {title}",
            "source": "svg_fallback",
            "success": True,
            "file_format": "svg",
        }

    def _build_description(self, thesis: dict) -> str:
        """Constroi descricao para geracao de imagem academica."""
        title = thesis.get("title", "")
        hypothesis = thesis.get("hypothesis", "")
        score = thesis.get("composite_score", 0)

        if self.lang == "pt":
            return (
                f"Figura academica conceitual representando a tese: '{title}'. "
                f"Hipotese: {hypothesis}. "
                f"Score composto: {score:.2f}. "
                f"Estilo: diagrama academico com cores profissionais, "
                f"mostrando conceitos-chave, metodologia e resultados esperados."
            )
        else:
            return (
                f"Conceptual academic figure representing the thesis: '{title}'. "
                f"Hypothesis: {hypothesis}. "
                f"Composite score: {score:.2f}. "
                f"Style: academic diagram with professional colors, "
                f"showing key concepts, methodology, and expected results."
            )

    @staticmethod
    def _content_hash(thesis: dict) -> str:
        """Gera hash SHA-256 do conteudo da tese."""
        content = json.dumps(thesis, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content.encode()).hexdigest()

    @staticmethod
    def _select_top(theses: list, n: int = 5) -> list:
        """Seleciona top N teses por composite_score."""
        sorted_theses = sorted(
            theses,
            key=lambda t: t.get("composite_score", 0),
            reverse=True,
        )
        return sorted_theses[:n]

    @staticmethod
    def _xml_escape(text: str) -> str:
        """Escapa caracteres especiais para XML."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    @staticmethod
    def _extract_keywords(title: str) -> str:
        """Extrai palavras-chave do titulo."""
        stopwords = {"a", "o", "e", "da", "do", "em", "para", "com", "de", "um", "uma"}
        words = title.split()
        keywords = [w for w in words if w.lower() not in stopwords and len(w) > 2]
        return ", ".join(keywords[:5]) if keywords else title

    @staticmethod
    def _detect_methodology(hypothesis: str) -> str:
        """Detecta metodologia a partir da hipotese."""
        hypothesis_lower = hypothesis.lower()
        if any(w in hypothesis_lower for w in ["rede", "neural", "deep", "cnn", "lstm"]):
            return "Deep Learning"
        if any(w in hypothesis_lower for w in ["quantum", "qubit"]):
            return "Computacao Quantica"
        if any(w in hypothesis_lower for w in ["algorithm", "algoritmo"]):
            return "Analise Algoritmica"
        if any(w in hypothesis_lower for w in ["formal", "verificacao", "verification"]):
            return "Metodos Formais"
        if any(w in hypothesis_lower for w in ["survey", "revisao", "review"]):
            return "Revisao Sistematica"
        return "Metodologia Cientifica"
