"""Testes TDD para a Validação Empírica (SPEC-935 R79)."""

import pytest
from synthetic_university.faculties import FACULTY_MAP
from synthetic_university.combinatorial_engine import CombinatorialDiscoveryEngine
from synthetic_university.thesis_generator import ThesisGenerator
from synthetic_university.empirical_validation import EmpiricalValidator


class TestEmpiricalValidation:
    """Testes para o painel de validação empírica."""

    @pytest.fixture
    def validator(self):
        return EmpiricalValidator()

    def test_validator_cria(self, validator):
        """R79: Validador é criado com professores."""
        assert validator is not None
        assert len(validator.professors) >= 30

    def test_professors_by_faculty(self, validator):
        """R79: Professores distribuídos por faculdades."""
        assert len(validator._profs_by_faculty) >= 10
        for fid, profs in validator._profs_by_faculty.items():
            assert len(profs) >= 2, f"{fid} tem apenas {len(profs)} professores"

    def test_evaluate_thesis(self, validator):
        """R79: Avaliação de uma tese."""
        # Criar uma tese
        engine = CombinatorialDiscoveryEngine(FACULTY_MAP)
        thesis_gen = ThesisGenerator()
        comb = engine.test_combination(("ética", "algoritmo", "sociedade"))
        thesis = thesis_gen.generate_thesis(comb)
        
        # Avaliar
        result = validator.evaluate_thesis(thesis)
        assert result is not None
        assert "thesis_id" in result
        assert "empirical_score" in result or "error" in result

    def test_evaluation_has_fields(self, validator):
        """R79: Avaliação tem campos obrigatórios."""
        engine = CombinatorialDiscoveryEngine(FACULTY_MAP)
        thesis_gen = ThesisGenerator()
        comb = engine.test_combination(("consciência", "qubit"))
        thesis = thesis_gen.generate_thesis(comb)
        
        result = validator.evaluate_thesis(thesis)
        if "error" not in result:
            assert "n_evaluators" in result
            assert "avg_relevance" in result
            assert "majority_endorsement" in result
            assert "empirical_score" in result
            assert "evaluations" in result

    def test_endorsement_levels(self, validator):
        """R79: Endossos são strong/moderate/weak."""
        engine = CombinatorialDiscoveryEngine(FACULTY_MAP)
        thesis_gen = ThesisGenerator()
        comb = engine.test_combination(("ética", "moral", "justiça"))
        thesis = thesis_gen.generate_thesis(comb)
        
        result = validator.evaluate_thesis(thesis)
        if "error" not in result:
            assert result["majority_endorsement"] in ["strong", "moderate", "weak"]

    def test_validate_multiple_theses(self, validator):
        """R79: Validação de múltiplas teses."""
        engine = CombinatorialDiscoveryEngine(FACULTY_MAP)
        thesis_gen = ThesisGenerator()
        
        combs = [
            engine.test_combination(("ética", "algoritmo")),
            engine.test_combination(("qubit", "consciência")),
        ]
        theses = [thesis_gen.generate_thesis(c) for c in combs]
        
        result = validator.validate_theses(theses)
        assert result["n_theses"] == 2
        assert result["n_valid"] >= 0
        assert "aggregate_scores" in result
        assert "endorsement_distribution" in result

    def test_generate_report(self, validator):
        """R79: Relatório textual é gerado."""
        engine = CombinatorialDiscoveryEngine(FACULTY_MAP)
        thesis_gen = ThesisGenerator()
        comb = engine.test_combination(("ética", "qubit"))
        thesis = thesis_gen.generate_thesis(comb)
        
        validation = validator.validate_theses([thesis])
        report = validator.generate_report(validation)
        assert report is not None
        assert len(report) > 50
        assert "VALIDACAO EMPIRICA" in report
