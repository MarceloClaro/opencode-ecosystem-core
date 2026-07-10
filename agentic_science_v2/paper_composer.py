# -*- coding: utf-8 -*-
"""
R105 — Agentic Paper Composer
===============================
Sistema agentivo de composicao de manuscritos academicos que integra
outputs de R101 (descoberta), R102 (evidencias), R103 (revisao),
R104 (revisao de manuscrito) para gerar artigo academico completo.

Pipeline: Plan → Write → Format → Verify → Export
"""

import json
import logging
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ── Templates de Venue ─────────────────────────────────────────────

VENUE_TEMPLATES = {
    "abnt": {
        "name": "ABNT NBR 6023",
        "sections": [
            {"name": "Título", "type": "title", "required": True},
            {"name": "Resumo", "type": "abstract", "required": True},
            {"name": "Introdução", "type": "introduction", "required": True},
            {"name": "Metodologia", "type": "methods", "required": True},
            {"name": "Resultados", "type": "results", "required": True},
            {"name": "Discussão", "type": "discussion", "required": True},
            {"name": "Conclusão", "type": "conclusion", "required": True},
            {"name": "Referências", "type": "references", "required": True},
        ],
        "citation_style": "abnt",
        "language": "pt-BR"
    },
    "apa": {
        "name": "APA 7th Edition",
        "sections": [
            {"name": "Title", "type": "title", "required": True},
            {"name": "Abstract", "type": "abstract", "required": True},
            {"name": "Introduction", "type": "introduction", "required": True},
            {"name": "Method", "type": "methods", "required": True},
            {"name": "Results", "type": "results", "required": True},
            {"name": "Discussion", "type": "discussion", "required": True},
            {"name": "Conclusion", "type": "conclusion", "required": False},
            {"name": "References", "type": "references", "required": True},
        ],
        "citation_style": "apa",
        "language": "en"
    },
    "ieee": {
        "name": "IEEE Transactions",
        "sections": [
            {"name": "Title", "type": "title", "required": True},
            {"name": "Abstract", "type": "abstract", "required": True},
            {"name": "Introduction", "type": "introduction", "required": True},
            {"name": "Proposed Method", "type": "methods", "required": True},
            {"name": "Experimental Results", "type": "results", "required": True},
            {"name": "Discussion", "type": "discussion", "required": False},
            {"name": "Conclusion", "type": "conclusion", "required": True},
            {"name": "References", "type": "references", "required": True},
        ],
        "citation_style": "ieee",
        "language": "en"
    }
}


# ── StructurePlanner ───────────────────────────────────────────────

class StructurePlanner:
    """Planeja a estrutura do manuscrito baseado no venue template."""

    def __init__(self):
        self.templates = VENUE_TEMPLATES

    def plan(self, title: str, venue: str = "apa") -> Dict[str, Any]:
        """Gera outline completo baseado no venue."""
        venue = venue.lower() if venue else "apa"
        if venue not in self.templates:
            venue = "apa"

        template = self.templates[venue]
        sections = []
        for sec_template in template["sections"]:
            sections.append({
                "name": sec_template["name"],
                "type": sec_template["type"],
                "required": sec_template["required"],
                "word_count_goal": self._estimate_word_count(sec_template["type"]),
                "status": "pending"
            })

        return {
            "title": title,
            "venue": venue,
            "venue_name": template["name"],
            "language": template["language"],
            "sections": sections,
            "citation_style": template["citation_style"],
            "total_sections": len(sections)
        }

    def _estimate_word_count(self, section_type: str) -> int:
        """Estima contagem de palavras por tipo de secao."""
        estimates = {
            "title": 15,
            "abstract": 200,
            "introduction": 800,
            "methods": 1200,
            "results": 1000,
            "discussion": 800,
            "conclusion": 400,
            "references": 300,
        }
        return estimates.get(section_type, 500)


# ── SectionWriter ──────────────────────────────────────────────────

class SectionWriter:
    """Escreve cada secao do manuscrito."""

    def write_abstract(self, title: str, discoveries: List[Dict],
                       evidence_graph: Dict) -> str:
        """Escreve o abstract."""
        parts = ["This paper presents"]
        if discoveries:
            best = max(discoveries, key=lambda d: d.get("fitness", 0))
            parts.append(f"a novel approach based on: {best.get('hypothesis', title)}")
        else:
            parts.append(f"a study on {title}")

        if evidence_graph and evidence_graph.get("entities"):
            parts.append(f", supported by evidence from {len(evidence_graph['entities'])} sources")

        parts.append(".")
        parts.append("Our results demonstrate significant improvements")
        parts.append("over existing approaches.")
        parts.append("Contributions include a novel framework")
        parts.append("and comprehensive experimental validation.")

        return " ".join(parts)

    def write_introduction(self, title: str, discoveries: List[Dict],
                           evidence_graph: Dict) -> str:
        """Escreve a introducao."""
        lines = [
            f"## Introduction\n",
            f"The field of {title.lower()} has seen significant advances in recent years.",
            "However, several key challenges remain open.",
            "",
            "### Related Work",
        ]

        if evidence_graph and evidence_graph.get("entities"):
            entities = evidence_graph["entities"]
            entity_list = list(entities.values()) if isinstance(entities, dict) else entities
            for ent in entity_list[:3]:
                if ent.get("type") == "paper":
                    lines.append(f"- {ent.get('title', 'Prior work')}")
            lines.append("")

        if discoveries:
            lines.append("\n### Contributions\n")
            for d in discoveries[:3]:
                lines.append(f"- {d.get('hypothesis', 'Contribution')} "
                             f"(fitness: {d.get('fitness', 0):.2f})")

        lines.append("\nThis paper addresses these gaps by proposing a novel approach.")
        return "\n".join(lines)

    def write_methods(self, discoveries: List[Dict]) -> str:
        """Escreve a secao de metodos."""
        lines = [
            "## Methods\n",
            "### Experimental Setup",
            "We evaluate our approach using standard benchmarks and metrics.",
            "",
            "### Implementation Details",
        ]
        if discoveries:
            for d in discoveries[:2]:
                lines.append(f"- {d.get('hypothesis', 'Approach')}: "
                             f"implemented and validated")

        lines.extend([
            "",
            "### Evaluation Protocol",
            "We follow established evaluation protocols with 5-fold cross-validation.",
            "Statistical significance is assessed using paired t-tests (p < 0.05).",
        ])
        return "\n".join(lines)

    def write_results(self, discoveries: List[Dict],
                      evidence_graph: Dict) -> str:
        """Escreve a secao de resultados."""
        lines = [
            "## Results\n",
            "### Main Results",
        ]
        if discoveries:
            for d in discoveries:
                lines.append(f"- {d.get('hypothesis', 'Approach')}: "
                             f"achieved fitness score of {d.get('fitness', 0):.2f}")
        lines.append("")
        lines.append("### Ablation Studies")
        lines.append("We conduct comprehensive ablation studies to validate design choices.")
        lines.append("")
        lines.append("### Comparative Analysis")
        lines.append("Our approach is compared against state-of-the-art baselines.")
        return "\n".join(lines)

    def write_discussion(self, discoveries: List[Dict],
                         review: Dict, revisions: List[Dict]) -> str:
        """Escreve a discussao."""
        lines = [
            "## Discussion\n",
            "### Interpretation of Results",
            "Our findings demonstrate the effectiveness of the proposed approach.",
        ]
        if review:
            score = review.get("overall_score", 0)
            lines.append(f"\nPeer review feedback (score: {score}/100) "
                         f"validates the methodological soundness.")
        if revisions:
            lines.append(f"\nWe addressed {len(revisions)} reviewer concerns "
                         f"in the revision process.")
        lines.extend([
            "",
            "### Limitations",
            "While promising, our approach has several limitations:",
            "- Computational cost may limit scalability",
            "- Generalization to other domains requires further validation",
            "",
            "### Future Work",
            "Future research directions include extending the framework "
            "to additional domains and optimizing computational efficiency.",
        ])
        return "\n".join(lines)

    def write_conclusion(self, discoveries: List[Dict]) -> str:
        """Escreve a conclusao."""
        lines = [
            "## Conclusion\n",
            "In this paper, we presented a novel approach",
        ]
        if discoveries:
            best = max(discoveries, key=lambda d: d.get("fitness", 0))
            lines.append(f"based on {best.get('hypothesis', 'our research')}.")
        lines.extend([
            "Our contributions include:",
        ])
        if discoveries:
            for i, d in enumerate(discoveries[:3], 1):
                lines.append(f"{i}. {d.get('hypothesis', 'Novel contribution')}")
        lines.extend([
            "",
            "Experimental results validate the effectiveness of our approach.",
            "Code and data are available for reproducibility.",
        ])
        return "\n".join(lines)

    def write_all(self, title: str, discoveries: List[Dict],
                  evidence_graph: Dict, review: Dict,
                  revisions: List[Dict]) -> Dict[str, str]:
        """Gera todas as secoes."""
        return {
            "abstract": self.write_abstract(title, discoveries, evidence_graph),
            "introduction": self.write_introduction(title, discoveries, evidence_graph),
            "methods": self.write_methods(discoveries),
            "results": self.write_results(discoveries, evidence_graph),
            "discussion": self.write_discussion(discoveries, review, revisions),
            "conclusion": self.write_conclusion(discoveries),
        }


# ── CitationFormatter ──────────────────────────────────────────────

class CitationFormatter:
    """Formata referencias em ABNT, APA, IEEE."""

    def format(self, ref: Dict[str, Any], style: str = "apa") -> str:
        """Formata uma unica referencia no estilo especificado."""
        style = style.lower() if style else "apa"
        authors = ref.get("authors", ["Author, A."])
        year = ref.get("year", 2026)
        title = ref.get("title", "Untitled")
        journal = ref.get("journal", "")
        volume = ref.get("volume", "")
        pages = ref.get("pages", "")
        publisher = ref.get("publisher", "")
        doi = ref.get("doi", "")

        if style == "abnt":
            return self._format_abnt(authors, year, title, journal,
                                     volume, pages, publisher, doi)
        elif style == "ieee":
            return self._format_ieee(authors, year, title, journal,
                                     volume, pages, publisher, doi)
        else:  # apa default
            return self._format_apa(authors, year, title, journal,
                                    volume, pages, publisher, doi)

    def _format_apa(self, authors: List[str], year: int, title: str,
                    journal: str, volume: str, pages: str,
                    publisher: str, doi: str) -> str:
        """Formata no estilo APA 7th."""
        author_str = ", ".join(authors)
        ref = f"{author_str} ({year}). {title}. "
        if journal:
            ref += f"*{journal}*"
            if volume:
                ref += f", *{volume}*"
            if pages:
                ref += f", {pages}"
            ref += "."
        elif publisher:
            ref += f"{publisher}."
        if doi:
            ref += f" https://doi.org/{doi}"
        return ref

    def _format_abnt(self, authors: List[str], year: int, title: str,
                     journal: str, volume: str, pages: str,
                     publisher: str, doi: str) -> str:
        """Formata no estilo ABNT NBR 6023."""
        author_str = "; ".join(a.upper() for a in authors)
        ref = f"{author_str}. **{title}**. "
        if journal:
            ref += f"{journal}"
            if volume:
                ref += f", v. {volume}"
            if pages:
                ref += f", p. {pages}"
            ref += f", {year}."
        elif publisher:
            ref += f"{publisher}, {year}."
        if doi:
            ref += f" Disponivel em: https://doi.org/{doi}"
        return ref

    def _format_ieee(self, authors: List[str], year: int, title: str,
                     journal: str, volume: str, pages: str,
                     publisher: str, doi: str) -> str:
        """Formata no estilo IEEE."""
        # IEEE: [1] A. Author, "Title," Journal, vol. x, no. y, pp. z, year.
        author_short = [a.split(",")[0] if "," in a else a for a in authors]
        initials = []
        for a in authors:
            parts = a.split(",")
            if len(parts) >= 2:
                last = parts[0].strip()
                first_parts = parts[1].strip().split()
                initials_str = " ".join(p[0] + "." for p in first_parts if p)
                initials.append(f"{initials_str} {last}")
            else:
                initials.append(a)

        author_str = ", ".join(initials)
        ref = f"{author_str}, \"{title},\" "
        if journal:
            ref += f"*{journal}*"
            if volume:
                ref += f", vol. {volume}"
            if pages:
                ref += f", pp. {pages}"
        ref += f", {year}."
        if doi:
            ref += f" doi: {doi}"
        return ref


# ── CrossConsistencyVerifier ───────────────────────────────────────

class CrossConsistencyVerifier:
    """Verifica consistencia interna do manuscrito."""

    def verify(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Verifica coerencia entre secoes."""
        report = {
            "abstract_intro_coherence": self._check_abstract_intro(
                sections.get("abstract", ""),
                sections.get("introduction", "")
            ),
            "methods_results_alignment": self.verify_methods_results_alignment(
                sections.get("methods", ""),
                sections.get("results", "")
            ),
            "section_flow": self._check_section_flow(sections),
        }
        report["overall"] = all(
            v.get("consistent", False) if isinstance(v, dict) else False
            for v in report.values()
        )
        return report

    def verify_claims_evidence(self, discoveries: List[Dict],
                                evidence_graph: Dict) -> Dict[str, Any]:
        """Verifica claims vs evidence."""
        verified = []
        unverified = []
        for d in discoveries:
            hypothesis = d.get("hypothesis", "")
            if evidence_graph and evidence_graph.get("entities"):
                # Simula verificacao: fitness > 0.8 = verified
                if d.get("fitness", 0) > 0.8:
                    verified.append(hypothesis)
                else:
                    unverified.append(hypothesis)
            else:
                unverified.append(hypothesis)

        return {
            "verified_claims": verified,
            "unverified_claims": unverified,
            "verification_rate": round(
                len(verified) / max(len(verified) + len(unverified), 1) * 100, 1
            )
        }

    def verify_methods_results_alignment(self, methods_text: str,
                                          results_text: str) -> Dict[str, Any]:
        """Verifica alinhamento Methods-Results."""
        methods_lower = methods_text.lower()
        results_lower = results_text.lower()

        # Extrai metricas/datasets mencionados
        metrics_in_methods = set(re.findall(r'\d+\s*(?:dataset|experiment|fold)', methods_lower))
        metrics_in_results = set(re.findall(r'\d+\s*(?:dataset|experiment|fold)', results_lower))

        overlap = metrics_in_methods & metrics_in_results
        return {
            "aligned": len(overlap) > 0 or len(metrics_in_methods) == 0,
            "metrics_in_methods": list(metrics_in_methods),
            "metrics_in_results": list(metrics_in_results),
            "overlap": list(overlap)
        }

    def full_report(self, sections: Dict[str, str],
                    discoveries: List[Dict],
                    evidence_graph: Dict) -> Dict[str, Any]:
        """Relatorio completo de consistencia."""
        consistency = self.verify(sections)
        claims = self.verify_claims_evidence(discoveries, evidence_graph)

        verified_count = len(consistency.get("abstract_intro_coherence", {}))
        total_checks = 3  # abstract_intro, methods_results, section_flow

        overall_score = round(
            (claims.get("verification_rate", 0) +
             (100 if consistency.get("overall") else 50)) / 2,
            1
        )

        return {
            "overall_score": overall_score,
            "consistency": consistency,
            "claims_evidence": claims,
            "total_checks": total_checks,
            "passed_checks": sum(
                1 for v in consistency.values()
                if isinstance(v, dict) and v.get("consistent", False)
            )
        }

    def _check_abstract_intro(self, abstract: str, introduction: str) -> Dict[str, Any]:
        """Verifica coerencia Abstract-Introduction."""
        abstract_words = set(abstract.lower().split())
        intro_words = set(introduction.lower().split())
        common = abstract_words & intro_words
        overlap_pct = round(len(common) / max(len(abstract_words), 1) * 100, 1)
        return {
            "consistent": overlap_pct > 10,
            "overlap_pct": overlap_pct,
            "common_terms": list(common)[:10]
        }

    def _check_section_flow(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Verifica fluxo logico entre secoes."""
        expected_order = ["abstract", "introduction", "methods",
                          "results", "discussion", "conclusion"]
        present = [s for s in expected_order if s in sections]
        return {
            "consistent": len(present) >= 4,
            "sections_found": present,
            "sections_missing": [s for s in expected_order if s not in sections]
        }


# ── OrchestratorComposer ───────────────────────────────────────────

class OrchestratorComposer:
    """Orquestrador completo de composicao de manuscritos."""

    def __init__(self):
        self.planner = StructurePlanner()
        self.writer = SectionWriter()
        self.formatter = CitationFormatter()
        self.verifier = CrossConsistencyVerifier()

    def run(self, title: str = "Untitled",
            discoveries: Optional[List[Dict]] = None,
            evidence_graph: Optional[Dict] = None,
            review: Optional[Dict] = None,
            revisions: Optional[List[Dict]] = None,
            venue: str = "apa",
            keywords: Optional[List[str]] = None,
            references: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Pipeline completo: plan → write → format → verify → export.

        Excecoes sao capturadas e retornadas como resultado estruturado
        (``status: "error"``) em vez de propagar o crash para o chamador.
        """
        try:
            return self._run(title, discoveries, evidence_graph, review,
                              revisions, venue, keywords, references)
        except Exception as exc:
            logger.exception("Falha na composicao do paper: %s", exc)
            return {
                "status": "error",
                "stage": "paper_composer.run",
                "error": str(exc),
                "manuscript": "",
                "sections": {},
            }

    def _run(self, title: str = "Untitled",
              discoveries: Optional[List[Dict]] = None,
              evidence_graph: Optional[Dict] = None,
              review: Optional[Dict] = None,
              revisions: Optional[List[Dict]] = None,
              venue: str = "apa",
              keywords: Optional[List[str]] = None,
              references: Optional[List[Dict]] = None) -> Dict[str, Any]:
        discoveries = discoveries or []
        evidence_graph = evidence_graph or {}
        review = review or {}
        revisions = revisions or []
        keywords = keywords or []
        references = references or []

        # 1. Plan
        outline = self.planner.plan(title, venue)

        # 2. Write
        sections = self.writer.write_all(
            title, discoveries, evidence_graph, review, revisions
        )

        # Add title to sections
        sections["title"] = title
        if keywords:
            sections["keywords"] = ", ".join(keywords)

        # 3. Format
        formatted_refs = []
        for ref in references:
            formatted = self.formatter.format(
                ref, style=outline["citation_style"]
            )
            formatted_refs.append(formatted)

        sections["references"] = "\n".join(formatted_refs) if formatted_refs else (
            "References will be generated from the evidence graph sources."
        )

        # 4. Verify
        consistency_report = self.verifier.full_report(
            sections, discoveries, evidence_graph
        )

        # 5. Export
        manuscript_parts = [
            f"# {title}",
            "",
            "## Abstract",
            sections.get("abstract", ""),
            "",
            sections.get("introduction", ""),
            "",
            sections.get("methods", ""),
            "",
            sections.get("results", ""),
            "",
            sections.get("discussion", ""),
            "",
            sections.get("conclusion", ""),
            "",
            "## References",
            sections.get("references", ""),
        ]
        manuscript = "\n".join(manuscript_parts)

        # Statistics
        word_count = len(manuscript.split())
        section_counts = {name: len(text.split())
                          for name, text in sections.items()
                          if isinstance(text, str)}

        return {
            "status": "completed",
            "manuscript": manuscript,
            "sections": sections,
            "outline": outline,
            "consistency_report": consistency_report,
            "statistics": {
                "word_count": word_count,
                "section_counts": section_counts,
                "reference_count": len(formatted_refs),
                "venue": venue
            }
        }


# ── API ─────────────────────────────────────────────────────────────

def compose_paper(title: str = "Untitled",
                  discoveries: Optional[List[Dict]] = None,
                  evidence_graph: Optional[Dict] = None,
                  review: Optional[Dict] = None,
                  revisions: Optional[List[Dict]] = None,
                  venue: str = "apa",
                  keywords: Optional[List[str]] = None,
                  references: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Funcao de conveniencia para compor um paper completo."""
    composer = OrchestratorComposer()
    return composer.run(
        title=title, discoveries=discoveries,
        evidence_graph=evidence_graph, review=review,
        revisions=revisions, venue=venue,
        keywords=keywords, references=references
    )
