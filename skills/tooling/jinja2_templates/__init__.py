#!/usr/bin/env python3
"""
Jinja2Templates — Geração de Documentos sem LLM (SPEC-964)
=============================================================
Motor de templates Jinja2 para substituir geração de documentos,
relatórios e notebooks via LLM ou f-strings hardcoded.

Uso:
    from skills.tooling.jinja2_templates import Jinja2Engine, TEMPLATE_DIR

    engine = Jinja2Engine()
    html = engine.render("fichamento.md.j2", {
        "titulo": "Paper X",
        "autores": ["João"],
        "ano": 2024,
        "resumo": "...",
        "palavras_chave": ["IA", "ML"],
    })
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import BaseLoader, Environment, FileSystemLoader, FunctionLoader, Template

from .filters import CUSTOM_FILTERS

# Diretório padrão de templates (dentro do pacote)
TEMPLATE_DIR = Path(__file__).parent / "templates"
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)


class Jinja2Engine:
    """
    Motor de renderização de templates Jinja2.

    Suporta:
    - Renderização de strings (render_string)
    - Renderização de arquivos .j2 (render)
    - Cache de templates compilados
    - Filtros customizados (markdown, table, etc.)
    - Múltiplos diretórios de templates
    """

    def __init__(
        self,
        template_dirs: Optional[List[str]] = None,
        autoescape: bool = False,
        cache_size: int = 100,
    ):
        self._template_dirs = template_dirs or [str(TEMPLATE_DIR)]
        self._env = Environment(
            loader=FileSystemLoader(self._template_dirs),
            autoescape=autoescape,
            cache_size=cache_size,
        )
        self._stats = {
            "render_calls": 0,
            "string_calls": 0,
            "template_hits": 0,
            "template_misses": 0,
            "total_ms": 0.0,
        }

        # Registrar filtros customizados
        for name, func in CUSTOM_FILTERS.items():
            self._env.filters[name] = func

    # ─── Renderização ────────────────────────────────────────

    def render(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Renderiza um template a partir de arquivo .j2.

        Args:
            template_name: nome do arquivo (ex: "fichamento.md.j2")
            data: dicionário com variáveis do template

        Returns:
            String renderizada
        """
        start = time.time()

        # Tenta carregar do cache
        try:
            template = self._env.get_template(template_name)
            self._stats["template_hits"] += 1
        except Exception:
            self._stats["template_misses"] += 1
            raise

        result = template.render(**data)
        self._stats["render_calls"] += 1
        self._stats["total_ms"] += (time.time() - start) * 1000
        return result

    def render_string(self, template_string: str, data: Dict[str, Any]) -> str:
        """
        Renderiza uma string de template diretamente.

        Args:
            template_string: string Jinja2 (ex: "Olá {{ nome }}!")
            data: dicionário com variáveis

        Returns:
            String renderizada
        """
        start = time.time()
        template = self._env.from_string(template_string)
        result = template.render(**data)
        self._stats["string_calls"] += 1
        self._stats["total_ms"] += (time.time() - start) * 1000
        return result

    # ─── Gerenciamento de Templates ──────────────────────────

    def list_templates(self) -> List[str]:
        """Lista todos os templates disponíveis nos diretórios registrados."""
        templates = []
        for dir_path in self._template_dirs:
            p = Path(dir_path)
            if p.exists():
                templates.extend(
                    sorted(str(f.relative_to(p)) for f in p.glob("**/*.j2"))
                )
        return templates

    def get_template_names(self) -> List[str]:
        """Retorna nomes de templates disponíveis (sem extensão)."""
        return sorted(
            t.replace(".j2", "") for t in self.list_templates()
        )

    def template_exists(self, template_name: str) -> bool:
        """Verifica se um template existe."""
        try:
            self._env.get_template(template_name)
            return True
        except Exception:
            return False

    def add_template_dir(self, directory: str):
        """Adiciona diretório adicional de templates."""
        if directory not in self._template_dirs:
            self._template_dirs.append(directory)
            self._env.loader.searchpath.append(directory)

    def register_filter(self, name: str, func):
        """Registra filtro customizado."""
        self._env.filters[name] = func

    # ─── Utilitários ─────────────────────────────────────────

    def render_to_file(
        self, template_name: str, data: Dict[str, Any], output_path: str
    ) -> str:
        """Renderiza e salva em arquivo."""
        result = self.render(template_name, data)
        Path(output_path).write_text(result, encoding="utf-8")
        return result

    def load_and_render(
        self, template_path: str, data: Dict[str, Any]
    ) -> str:
        """Carrega template de um path arbitrário e renderiza."""
        p = Path(template_path)
        if not p.exists():
            raise FileNotFoundError(f"Template não encontrado: {template_path}")
        template_str = p.read_text(encoding="utf-8")
        return self.render_string(template_str, data)

    # ─── Stats ───────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso."""
        total_calls = self._stats["render_calls"] + self._stats["string_calls"]
        return {
            **self._stats,
            "total_calls": total_calls,
            "avg_ms": round(
                self._stats["total_ms"] / total_calls, 2
            ) if total_calls > 0 else 0.0,
            "templates_available": len(self.list_templates()),
        }


# Singleton
_default_engine: Optional[Jinja2Engine] = None


def get_engine() -> Jinja2Engine:
    global _default_engine
    if _default_engine is None:
        _default_engine = Jinja2Engine()
    return _default_engine


# ─── Teste Rápido ───────────────────────────────────────────

if __name__ == "__main__":
    engine = get_engine()
    print("=== Jinja2Engine ===")
    print(f"Templates disponíveis: {engine.list_templates()}")

    # Teste render_string
    r = engine.render_string("Olá {{nome}}!", {"nome": "Mundo"})
    print(f"render_string: {r}")

    # Teste render (se existir template)
    templates = engine.list_templates()
    if templates:
        r = engine.render(templates[0], {"titulo": "Teste"})
        print(f"render({templates[0]}): {r[:100]}...")

    print(f"\nStats: {engine.get_stats()}")
