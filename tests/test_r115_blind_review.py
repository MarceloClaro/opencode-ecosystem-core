# -*- coding: utf-8 -*-
"""
Testes R115 — Revisão às Cegas Real (Double-Blind) no R103
=============================================================
Testa agentic_science_v2/blind_review.py (BlindReviewAnonymizer,
BlindReviewReport) e a integração real em
agentic_science_v2/review_agent.py::OrchestratorReviewer.

Requisitos (R115):
  - Sem author_names/author_affiliations, o comportamento anterior é
    preservado (blind_review.applied=False, gate inalterado)
  - Com author_names/author_affiliations, nome/afiliação são
    redigidos do título/abstract/seções ANTES de qualquer crítico ver
  - Verificação pós-hoc detecta vazamento real (não apenas confia na
    redação)
  - Conflito de interesse (revisor com mesma afiliação de um autor)
    reprova o export_gate_passed
"""

import pytest

from agentic_science_v2.blind_review import BlindReviewAnonymizer, BlindReviewReport
from agentic_science_v2.review_agent import OrchestratorReviewer


class TestBlindReviewAnonymizer:
    def test_no_identifiers_no_redaction(self):
        anon = BlindReviewAnonymizer()
        paper = {"title": "T", "abstract": "A", "sections": ["S1"]}
        result, redactions = anon.anonymize(paper)
        assert redactions == 0
        assert result is paper  # retorna o mesmo objeto quando nao ha nada a ocultar

    def test_redacts_author_name_from_title_and_abstract(self):
        anon = BlindReviewAnonymizer()
        paper = {
            "title": "Estudo de Maria Souza",
            "abstract": "Maria Souza propõe um método.",
            "sections": ["Introdução por Maria Souza"],
            "author_names": ["Maria Souza"],
        }
        result, redactions = anon.anonymize(paper)
        assert redactions == 3
        assert "Maria Souza" not in result["title"]
        assert "Maria Souza" not in result["abstract"]
        assert "Maria Souza" not in result["sections"][0]
        assert anon.REDACTED_AUTHOR in result["title"]

    def test_redacts_affiliation(self):
        anon = BlindReviewAnonymizer()
        paper = {
            "title": "T", "abstract": "Pesquisa feita na Universidade Federal X.",
            "sections": [], "author_affiliations": ["Universidade Federal X"],
        }
        result, redactions = anon.anonymize(paper)
        assert redactions == 1
        assert "Universidade Federal X" not in result["abstract"]

    def test_original_paper_is_not_mutated(self):
        anon = BlindReviewAnonymizer()
        paper = {"title": "Estudo de João", "abstract": "", "sections": [],
                  "author_names": ["João"]}
        anon.anonymize(paper)
        assert paper["title"] == "Estudo de João"  # original intacto

    def test_detect_leaks_finds_name_in_generated_text(self):
        anon = BlindReviewAnonymizer()
        paper = {"author_names": ["Ana Costa"], "author_affiliations": []}
        leaks = anon.detect_leaks("A crítica menciona Ana Costa diretamente.", paper)
        assert leaks == ["Ana Costa"]

    def test_detect_leaks_clean_when_no_identifiers_present(self):
        anon = BlindReviewAnonymizer()
        paper = {"author_names": ["Ana Costa"], "author_affiliations": []}
        leaks = anon.detect_leaks("Uma crítica genérica sem nomes.", paper)
        assert leaks == []

    def test_conflict_of_interest_detected(self):
        anon = BlindReviewAnonymizer()
        paper = {"author_affiliations": ["Instituto Y"]}
        conflicts = anon.check_conflict_of_interest(paper, {"ethics": "Instituto Y"})
        assert len(conflicts) == 1
        assert "Instituto Y" in conflicts[0]

    def test_no_conflict_when_affiliations_differ(self):
        anon = BlindReviewAnonymizer()
        paper = {"author_affiliations": ["Instituto Y"]}
        conflicts = anon.check_conflict_of_interest(paper, {"ethics": "Instituto Z"})
        assert conflicts == []

    def test_no_reviewer_affiliations_means_no_conflict_check(self):
        anon = BlindReviewAnonymizer()
        paper = {"author_affiliations": ["Instituto Y"]}
        assert anon.check_conflict_of_interest(paper, None) == []


class TestBlindReviewReport:
    def test_passed_true_when_no_leaks_or_conflicts(self):
        report = BlindReviewReport(applied=True, redactions_made=2)
        assert report.passed is True

    def test_passed_false_when_leak_detected(self):
        report = BlindReviewReport(applied=True, leaks_detected=["Nome Vazado"])
        assert report.passed is False

    def test_passed_false_when_conflict_detected(self):
        report = BlindReviewReport(applied=True, conflicts_of_interest=["conflito"])
        assert report.passed is False


class TestOrchestratorReviewerIntegration:
    def _paper_sem_autor(self):
        return {
            "title": "Um Estudo Qualquer",
            "abstract": "Resumo do estudo com metodologia e resultados discutidos.",
            "sections": ["Introduction", "Methods", "Results", "Discussion"],
        }

    def _paper_com_autor(self):
        return {
            "title": "Estudo de João Pereira",
            "abstract": "João Pereira, da Universidade ABC, propõe um novo método experimental.",
            "sections": ["Introduction sobre João Pereira", "Methods", "Results", "Discussion"],
            "author_names": ["João Pereira"],
            "author_affiliations": ["Universidade ABC"],
        }

    def test_backward_compatible_without_author_info(self):
        """Sem author_names/affiliations, blind_review.applied=False mas
        nao bloqueia o gate por si so (comportamento anterior preservado)."""
        pkg = OrchestratorReviewer().review(self._paper_sem_autor())
        assert pkg.blind_review["applied"] is False
        assert pkg.blind_review["passed"] is True

    def test_author_identifiers_never_reach_critiques(self):
        pkg = OrchestratorReviewer().review(self._paper_com_autor())
        assert pkg.blind_review["applied"] is True
        assert pkg.blind_review["redactions_made"] >= 1
        assert pkg.blind_review["leaks_detected"] == []
        assert "João Pereira" not in pkg.paper_title

    def test_conflict_of_interest_fails_export_gate(self):
        pkg = OrchestratorReviewer(min_traceability=0.0, min_coverage=0.0).review(
            self._paper_com_autor(),
            reviewer_affiliations={"methodology": "Universidade ABC"},
        )
        assert pkg.blind_review["conflicts_of_interest"] != []
        assert pkg.export_gate_passed is False

    def test_no_conflict_allows_gate_to_pass_on_merit(self):
        """Sem conflito, o gate depende só de traceability/coverage
        (thresholds zerados aqui só para isolar o efeito do blind review)."""
        pkg = OrchestratorReviewer(min_traceability=0.0, min_coverage=0.0).review(
            self._paper_com_autor(),
            reviewer_affiliations={"methodology": "Outra Universidade"},
        )
        assert pkg.blind_review["conflicts_of_interest"] == []
        assert pkg.export_gate_passed is True

    def test_to_dict_includes_blind_review(self):
        pkg = OrchestratorReviewer().review(self._paper_com_autor())
        d = pkg.to_dict()
        assert "blind_review" in d
