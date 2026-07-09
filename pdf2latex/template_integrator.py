"""
Integrador de templates LaTeX.
Aplica um template do catálogo do ecossistema a um projeto LaTeX gerado.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Optional

# Mapa de aliases para templates
TEMPLATE_ALIASES = {
    "abnt": "abntex2",
    "abnt2025": "abnt2025",
    "acm": "acm",
    "ieee": "ieee",
    "elsevier": "elsevier",
    "nature": "nature",
    "springer": "springer",
    "tandf": "tandf",
    "mdpi": "mdpi",
    "sbc": "sbc",
    "icmc": "icmc",
    "usp": "usp",
    "unb": "unb-monografia",
    "ipleiria": "ipleiria",
    "capes": "capes",
    "livro": "victoria-regia",
    "victoria": "victoria-regia",
    "livro-simples": "book-simple",
    "cv": "latexcv",
    "curriculo": "latexcv",
    "quali": "artigo-qualis-a1",
    "qualis": "artigo-qualis-a1",
}

# Mapa de templates → documentclass
TEMPLATE_CLASS = {
    "abntex2": r"\documentclass[12pt,a4paper]{abntex2}",
    "abnt2025": r"\documentclass[12pt,a4paper]{abnt2025}",
    "acm": r"\documentclass[sigconf]{acmart}",
    "ieee": r"\documentclass[conference]{IEEEtran}",
    "elsevier": r"\documentclass{elsarticle}",
    "nature": r"\documentclass{sn-jnl}",
    "springer": r"\documentclass{sn-jnl}",
    "tandf": r"\documentclass{interact}",
    "mdpi": r"\documentclass{mdpi}",
    "sbc": r"\documentclass{article}",
    "icmc": r"\documentclass{icmc}",
    "unb-monografia": r"\documentclass{UnB-CIC}",
    "usp": r"\documentclass[12pt,a4paper]{article}",
    "ipleiria": r"\documentclass{IPLeiriaThesis}",
    "capes": r"\documentclass[12pt,a4paper]{article}",
    "victoria-regia": r"\documentclass[12pt,a4paper]{book}",
    "book-simple": r"\documentclass[12pt,a4paper]{book}",
    "artigo-qualis-a1": r"\documentclass[12pt,a4paper]{article}",
}


class TemplateIntegrator:
    """Aplica um template LaTeX a um projeto gerado."""

    def __init__(self, project_dir: Path, template_name: str):
        self.project_dir = Path(project_dir)
        self.template_name = self._resolve_alias(template_name)
        self.templates_dir = self._find_templates_dir()

    def _resolve_alias(self, name: str) -> str:
        """Resolve alias para nome de template real."""
        name_lower = name.lower().strip()
        return TEMPLATE_ALIASES.get(name_lower, name_lower)

    def _find_templates_dir(self) -> Optional[Path]:
        """Localiza o diretório de templates do ecossistema."""
        # Caminhos possíveis
        candidates = [
            Path("/home/marceloclaro/opencode-ecosystem-core/templates"),
            Path.cwd() / "templates",
            Path.cwd().parent / "templates",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def apply(self) -> bool:
        """Aplica o template ao projeto LaTeX."""
        if not self.templates_dir:
            return False

        # Localizar template
        template_path = self._locate_template()
        if not template_path:
            return False

        # Copiar arquivos do template
        self._copy_template_files(template_path)

        # Adaptar main.tex
        self._adapt_main_tex()

        # Adaptar Makefile
        self._adapt_makefile()

        return True

    def _locate_template(self) -> Optional[Path]:
        """Localiza o diretório do template no catálogo."""
        # Buscar em todas as categorias
        for category in ["academic-br", "international", "books", "cv"]:
            candidate = self.templates_dir / category / self.template_name
            if candidate.exists():
                return candidate

        # Templates na raiz
        candidate = self.templates_dir / self.template_name
        if candidate.exists():
            return candidate

        # Tentar encontrar por nome parcial
        for root, dirs, files in os.walk(self.templates_dir):
            for d in dirs:
                if self.template_name in d.lower():
                    return Path(root) / d

        return None

    def _copy_template_files(self, template_path: Path):
        """Copia arquivos relevantes do template."""
        # Copiar .cls e .sty
        for ext in ["*.cls", "*.sty", "*.bst", "*.bib"]:
            for f in template_path.glob(ext):
                shutil.copy2(f, self.project_dir / f.name)

        # Copiar subdiretórios relevantes
        for subdir in ["config", "images", "logos"]:
            src = template_path / subdir
            if src.exists() and src.is_dir():
                dst = self.project_dir / subdir
                if not dst.exists():
                    shutil.copytree(src, dst)

    def _adapt_main_tex(self):
        """Adapta o main.tex para usar a documentclass do template."""
        main_path = self.project_dir / "main.tex"
        if not main_path.exists():
            return

        content = main_path.read_text(encoding="utf-8")

        # Substituir documentclass
        doc_class = TEMPLATE_CLASS.get(self.template_name)
        if doc_class:
            # Usar lambda para evitar interpretação de escapes na replacement
            content = re.sub(
                r'\\documentclass\[.*?\]\{.*?\}',
                lambda m: doc_class,
                content
            )

        # Adicionar pacotes específicos do template
        extra_packages = self._get_extra_packages()
        if extra_packages:
            # Inserir após o último pacote carregado
            insert_point = content.rfind(r"\usepackage{")
            if insert_point >= 0:
                # Encontrar final da linha
                end_line = content.find("\n", insert_point)
                if end_line >= 0:
                    content = (
                        content[: end_line + 1]
                        + "\n"
                        + extra_packages
                        + "\n"
                        + content[end_line + 1 :]
                    )

        main_path.write_text(content, encoding="utf-8")

    def _get_extra_packages(self) -> str:
        """Retorna pacotes extras necessários para cada template."""
        packages = {
            "abntex2": r"\usepackage[alf]{abntex2cite}",
            "abnt2025": "",
            "acm": r"\citestyle{acmauthoryear}",
            "ieee": "",
            "elsevier": r"\journal{Journal Name}",
            "nature": "",
            "springer": "",
        }
        return packages.get(self.template_name, "")

    def _adapt_makefile(self):
        """Adapta o Makefile para o template."""
        makefile_path = self.project_dir / "Makefile"
        if not makefile_path.exists():
            return

        content = makefile_path.read_text(encoding="utf-8")

        # Adicionar nota sobre o template
        note = f"\n# Template aplicado: {self.template_name}\n"
        if note not in content:
            content = content.replace(
                "# Gerado automaticamente",
                f"# Gerado automaticamente\n# Template aplicado: {self.template_name}",
            )

        makefile_path.write_text(content, encoding="utf-8")
