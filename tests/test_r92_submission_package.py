"""Testes TDD para Submission Package Generator (SPEC-935 R92)."""

import os
import json
import pytest
from unittest.mock import patch
from synthetic_university.submission_package import (
    SubmissionPackage,
    ComplianceChecker,
    MetadataGenerator,
    JOURNAL_REQUIREMENTS,
)


class TestR92SubmissionPackage:
    """Testes para geracao de pacote de submissao Qualis A1."""

    @pytest.fixture
    def thesis(self):
        return {
            "thesis_id": "thesis_001",
            "title": "Quantum Ethics: A Framework for Moral AI Systems",
            "authors": ["Marcelo Claro", "Alan Turing"],
            "abstract": "This thesis proposes a novel framework for AI ethics using quantum principles.",
            "keywords": ["quantum ethics", "AI", "formal verification"],
            "faculties_involved": ["engineering", "human_sciences"],
            "composite_score": 0.92,
        }

    @pytest.fixture
    def package(self, tmp_path):
        return SubmissionPackage(output_dir=str(tmp_path / "submission"))

    def test_package_creates(self, package):
        """R92: SubmissionPackage e criado."""
        assert package is not None

    def test_compliance_check(self, package, thesis):
        """R92: Verificacao de conformidade com periodicos Qualis A1."""
        with patch.object(package.compliance, '_check_format') as mock_fmt:
            mock_fmt.return_value = True
            with patch.object(package.compliance, '_check_sections') as mock_sec:
                mock_sec.return_value = True

                results = package.compliance.check(thesis)

        assert isinstance(results, dict)
        for journal in JOURNAL_REQUIREMENTS:
            assert journal in results

    def test_metadata_generation(self, package, thesis):
        """R92: Geracao de metadados da submissao."""
        metadata = package.metadata.generate(thesis)
        assert "title" in metadata
        assert "authors" in metadata
        assert "keywords" in metadata
        assert "abstract" in metadata
        assert len(metadata["authors"]) == 2

    def test_cover_letter(self, package, thesis):
        """R92: Cover letter personalizada para periodico."""
        letter = package.generate_cover_letter(thesis, "Journal of AI Ethics")
        assert "Journal of AI Ethics" in letter
        assert thesis["title"] in letter
        assert len(letter) > 200

    def test_package_structure(self, package, thesis):
        """R92: Estrutura de diretorios do pacote."""
        pkg_path = package.build(thesis, "Journal of AI Ethics")
        assert os.path.exists(pkg_path)

        expected_dirs = ["manuscript", "figures", "metadata", "reviews"]
        for d in expected_dirs:
            assert os.path.exists(os.path.join(pkg_path, d)), f"Missing: {d}"

    def test_checklist(self, package, thesis):
        """R92: Checklist de submissao completo."""
        checklist = package.checklist(thesis)
        assert len(checklist) > 5
        assert all("status" in item for item in checklist)
        assert all("name" in item for item in checklist)

    def test_manuscript_content(self, package, thesis):
        """R92: Manuscript gerado com conteudo basico."""
        pkg = package.build(thesis, "AI & Society")
        manuscript_path = os.path.join(pkg, "manuscript", "manuscript.md")
        assert os.path.exists(manuscript_path)
        with open(manuscript_path) as f:
            content = f.read()
        assert thesis["title"] in content
        assert thesis["abstract"] in content

    def test_journal_requirements(self):
        """R92: Requisitos de periodicos sao validos."""
        for jname, req in JOURNAL_REQUIREMENTS.items():
            assert "max_words" in req
            assert "format" in req
            assert "sections" in req
            assert req["max_words"] > 0

    def test_multiple_journals(self, package, thesis):
        """R92: Gera pacotes para multiplos periodicos."""
        journals = ["Journal of AI Ethics", "Nature Machine Intelligence", "AI & Society"]
        packages = []
        for j in journals:
            p = package.build(thesis, j)
            packages.append(p)
            assert os.path.exists(p)

        assert len(packages) == 3

    def test_response_to_reviewers(self, package, thesis):
        """R92: Gera template de resposta aos revisores."""
        response = package.generate_response_template(thesis)
        assert "Response to Reviewers" in response or "Resposta" in response
        assert "Comment" in response or "Comentario" in response
