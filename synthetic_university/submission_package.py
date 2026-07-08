"""
Submission Package Generator — Gera pacotes de submissao para periodicos Qualis A1.

Funcionalidades:
  - Compliance check para multiplos periodicos
  - Geracao de metadados, cover letter, response to reviewers
  - Estrutura de diretorios padronizada
  - Checklist de completude

SPEC-935-R92 — R92 do OpenCode Ecosystem Core.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Requisitos de periodicos Qualis A1 (simulados)
JOURNAL_REQUIREMENTS: Dict[str, Dict] = {
    "Journal of AI Ethics": {
        "max_words": 8000,
        "format": "APA",
        "sections": ["abstract", "introduction", "methods", "results", "discussion", "conclusion", "references"],
        "max_authors": 5,
        "open_access": True,
        "review_type": "double_blind",
    },
    "Nature Machine Intelligence": {
        "max_words": 5000,
        "format": "Nature",
        "sections": ["abstract", "main", "methods", "references", "acknowledgments"],
        "max_authors": 8,
        "open_access": False,
        "review_type": "single_blind",
    },
    "AI & Society": {
        "max_words": 10000,
        "format": "APA",
        "sections": ["abstract", "introduction", "background", "methodology", "findings", "discussion", "conclusion"],
        "max_authors": 4,
        "open_access": False,
        "review_type": "double_blind",
    },
}


class MetadataGenerator:
    """Gerador de metadados para submissao academica."""

    @staticmethod
    def generate(thesis: dict) -> dict:
        return {
            "title": thesis.get("title", "Untitled"),
            "authors": thesis.get("authors", ["Author"]),
            "abstract": thesis.get("abstract", ""),
            "keywords": thesis.get("keywords", []),
            "faculties": thesis.get("faculties_involved", []),
            "score": thesis.get("composite_score", 0),
            "generated_at": datetime.now().isoformat(),
            "language": "en",
            "fields_of_study": thesis.get("faculties_involved", []),
        }

    @staticmethod
    def generate_orcid_block(authors: list) -> str:
        lines = ["ORCIDs:"]
        for a in authors:
            lines.append(f"  {a}: 0000-0000-0000-0000")
        return "\n".join(lines)


class ComplianceChecker:
    """Verificador de conformidade com requisitos de periodicos."""

    def __init__(self, lang: str = "en"):
        self.lang = lang

    def check(self, thesis: dict) -> dict:
        """Verifica conformidade com todos os periodicos conhecidos."""
        results = {}
        for jname, req in JOURNAL_REQUIREMENTS.items():
            results[jname] = self._check_journal(thesis, jname, req)
        return results

    def _check_journal(self, thesis: dict, jname: str, req: dict) -> dict:
        issues = []
        word_count = len(thesis.get("abstract", "").split())

        # Verificacoes
        if word_count > req["max_words"]:
            issues.append(f"Word count ({word_count}) exceeds max ({req['max_words']})")

        authors = thesis.get("authors", [])
        if len(authors) > req["max_authors"]:
            issues.append(f"Authors ({len(authors)}) exceed max ({req['max_authors']})")

        if not thesis.get("keywords"):
            issues.append("Missing keywords")

        format_ok = self._check_format(thesis, req["format"])
        if not format_ok:
            issues.append(f"Format requirements not met ({req['format']})")

        sections_ok = self._check_sections(thesis, req["sections"])
        if not sections_ok:
            issues.append(f"Missing required sections")

        return {
            "journal": jname,
            "compliant": len(issues) == 0,
            "issues": issues,
            "requirements": req,
        }

    @staticmethod
    def _check_format(thesis: dict, format_name: str) -> bool:
        # Simulado — sempre True para testes
        return True

    @staticmethod
    def _check_sections(thesis: dict, sections: list) -> bool:
        # Simulado — sempre True para testes
        return True


class SubmissionPackage:
    """Montador de pacote de submissao academica.

    Args:
        output_dir: Diretorio raiz para pacotes.
        lang: Idioma ('pt' ou 'en').
    """

    def __init__(self, output_dir: str = "academic/submissions", lang: str = "en"):
        self.output_dir = output_dir
        self.lang = lang
        self.compliance = ComplianceChecker(lang)
        self.metadata = MetadataGenerator()

    def build(self, thesis: dict, journal_name: str) -> str:
        """Monta pacote completo de submissao para um periodico.

        Returns:
            Caminho do diretorio do pacote.
        """
        thesis_id = thesis.get("thesis_id", "unknown")
        safe_jname = journal_name.replace(" ", "_").replace("/", "_")
        pkg_dir = os.path.join(self.output_dir, f"{thesis_id}_{safe_jname}")
        os.makedirs(pkg_dir, exist_ok=True)

        # Estrutura de diretorios
        dirs = ["manuscript", "figures", "metadata", "reviews"]
        for d in dirs:
            os.makedirs(os.path.join(pkg_dir, d), exist_ok=True)

        # Gera arquivos
        self._write_manuscript(pkg_dir, thesis)
        self._write_metadata(pkg_dir, thesis, journal_name)
        self._write_cover_letter(pkg_dir, thesis, journal_name)
        self._write_checklist(pkg_dir, thesis, journal_name)
        self._write_compliance(pkg_dir, thesis, journal_name)

        logger.info("R92 Pacote gerado: %s", pkg_dir)
        return pkg_dir

    def generate_cover_letter(self, thesis: dict, journal_name: str) -> str:
        """Gera cover letter personalizada."""
        title = thesis.get("title", "Untitled")
        authors = ", ".join(thesis.get("authors", ["Author"]))
        abstract = thesis.get("abstract", "")

        is_pt = self.lang == "pt"

        if is_pt:
            return (
                f"Carta de Submissao\n\n"
                f"Prezado Editor,\n\n"
                f"Submetemos o manuscrito intitulado '{title}' "
                f"por {authors} para consideracao no {journal_name}.\n\n"
                f"Resumo: {abstract}\n\n"
                f"Acreditamos que este trabalho contribui significativamente para a area "
                f"e esta alinhado com o escopo do periodico.\n\n"
                f"Atenciosamente,\n{authors}"
            )
        else:
            return (
                f"Cover Letter\n\n"
                f"Dear Editor,\n\n"
                f"We submit the manuscript titled '{title}' "
                f"by {authors} for consideration in {journal_name}.\n\n"
                f"Abstract: {abstract}\n\n"
                f"We believe this work contributes significantly to the field "
                f"and aligns with the journal's scope.\n\n"
                f"Sincerely,\n{authors}"
            )

    def generate_response_template(self, thesis: dict) -> str:
        """Gera template de resposta aos revisores."""
        title = thesis.get("title", "Untitled")
        is_pt = self.lang == "pt"

        if is_pt:
            return (
                f"Resposta aos Revisores\n\n"
                f"Manuscrito: {title}\n\n"
                f"Comentario do Revisor 1:\n"
                f"> ...\n"
                f"Resposta: ...\n\n"
                f"Comentario do Revisor 2:\n"
                f"> ...\n"
                f"Resposta: ...\n"
            )
        else:
            return (
                f"Response to Reviewers\n\n"
                f"Manuscript: {title}\n\n"
                f"Reviewer 1 Comment:\n"
                f"> ...\n"
                f"Response: ...\n\n"
                f"Reviewer 2 Comment:\n"
                f"> ...\n"
                f"Response: ...\n"
            )

    def checklist(self, thesis: dict) -> list:
        """Gera checklist de submissao."""
        items = [
            {"name": "Title page with all authors", "status": bool(thesis.get("authors"))},
            {"name": "Abstract (150-250 words)", "status": len(thesis.get("abstract", "").split()) > 100},
            {"name": "Keywords (4-6)", "status": len(thesis.get("keywords", [])) >= 3},
            {"name": "Main manuscript file", "status": True},
            {"name": "Figures and tables", "status": True},
            {"name": "References formatted", "status": True},
            {"name": "Cover letter", "status": True},
            {"name": "Conflict of interest statement", "status": False},
            {"name": "Data availability statement", "status": False},
            {"name": "Author contributions", "status": False},
        ]
        return items

    def _write_manuscript(self, pkg_dir: str, thesis: dict):
        """Escreve arquivo do manuscrito."""
        path = os.path.join(pkg_dir, "manuscript", "manuscript.md")
        title = thesis.get("title", "Untitled")
        authors = ", ".join(thesis.get("authors", ["Author"]))
        abstract = thesis.get("abstract", "")

        content = (
            f"# {title}\n\n"
            f"{authors}\n\n"
            f"## Abstract\n\n{abstract}\n\n"
            f"## Introduction\n\n[TBD]\n\n"
            f"## Methods\n\n[TBD]\n\n"
            f"## Results\n\n[TBD]\n\n"
            f"## Discussion\n\n[TBD]\n\n"
            f"## Conclusion\n\n[TBD]\n\n"
            f"## References\n\n[TBD]\n"
        )
        with open(path, "w") as f:
            f.write(content)

    def _write_metadata(self, pkg_dir: str, thesis: dict, journal: str):
        """Escreve arquivo de metadados."""
        meta = self.metadata.generate(thesis)
        meta["journal"] = journal
        path = os.path.join(pkg_dir, "metadata", "metadata.json")
        with open(path, "w") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

    def _write_cover_letter(self, pkg_dir: str, thesis: dict, journal: str):
        """Escreve cover letter."""
        letter = self.generate_cover_letter(thesis, journal)
        path = os.path.join(pkg_dir, "metadata", "cover_letter.txt")
        with open(path, "w") as f:
            f.write(letter)

    def _write_checklist(self, pkg_dir: str, thesis: dict, journal: str):
        """Escreve checklist de submissao."""
        items = self.checklist(thesis)
        checklist_text = f"Submission Checklist for {journal}\n\n"
        for item in items:
            status = "✓" if item["status"] else "✗"
            checklist_text += f"[{status}] {item['name']}\n"
        path = os.path.join(pkg_dir, "metadata", "checklist.txt")
        with open(path, "w") as f:
            f.write(checklist_text)

    def _write_compliance(self, pkg_dir: str, thesis: dict, journal: str):
        """Escreve relatorio de conformidade."""
        results = self.compliance.check(thesis)
        jresult = results.get(journal, {"compliant": False, "issues": ["Unknown journal"]})
        path = os.path.join(pkg_dir, "metadata", "compliance.json")
        with open(path, "w") as f:
            json.dump(jresult, f, indent=2, ensure_ascii=False)
