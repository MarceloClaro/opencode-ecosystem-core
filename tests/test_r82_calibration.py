"""Testes TDD para a Calibração do Painel (SPEC-935 R82)."""

import pytest
from synthetic_university.faculties import FACULTY_MAP
from synthetic_university.agents.professors import create_all_professors, PROFESSOR_REGISTRY
from synthetic_university.agents.professor_base import Professor
from synthetic_university.empirical_validation import EmpiricalValidator
from synthetic_university.combinatorial_engine import CombinatorialDiscoveryEngine
from synthetic_university.thesis_generator import ThesisGenerator


class TestR82ProfessorExpansion:
    """Testes para expansão do painel para 100+ professores."""

    def test_pool_expanded_to_100_plus(self):
        """R82: Pool de professores expandido para 100+."""
        profs = create_all_professors()
        assert len(profs) >= 100, f"Pool tem {len(profs)} professores (esperado >= 100)"

    def test_every_faculty_has_enough_professors(self):
        """R82: Cada faculdade tem pelo menos 5 professores."""
        from collections import Counter
        profs = create_all_professors()
        fac_counts = Counter(p.faculty_id for p in profs)
        for fid in FACULTY_MAP:
            assert fac_counts[fid] >= 5, f"{fid} tem {fac_counts[fid]} profs (min 5)"

    def test_h_index_distribution(self):
        """R82: h-indices variam entre 1 e 50."""
        profs = create_all_professors()
        h_indices = [p.h_index for p in profs]
        assert min(h_indices) >= 1
        assert max(h_indices) <= 80  # Doutor Honoris Causa tem 50
        # Pelo menos 10 professores com h_index >= 20
        senior = sum(1 for h in h_indices if h >= 20)
        assert senior >= 10, f"Apenas {senior} professores com h>=20"

    def test_all_professors_have_unique_ids(self):
        """R82: Todos os professores têm IDs únicos."""
        profs = create_all_professors()
        ids = [p.professor_id for p in profs]
        assert len(ids) == len(set(ids))


class TestR82CalibratedEndorsement:
    """Testes para o novo sistema de endosso calibrado."""

    @pytest.fixture
    def validator(self):
        return EmpiricalValidator()

    def test_validator_uses_expanded_pool(self, validator):
        """R82: Validador usa pool expandido de 100+ professores."""
        assert len(validator.professors) >= 100

    def test_endorsement_thresholds_fire_strong(self, validator):
        """R82: Endosso 'strong' é possível com alta relevância + convergência."""
        evals = [
            {"confidence": 0.75, "composite_relevance": 0.55, "endorsement": "strong",
             "adjusted_viability": 0.7}
            for _ in range(5)
        ]
        result = validator._calibrate_endorsement(
            weighted_relevance=0.55,
            convergence_rate=0.80,
            evaluations=evals,
        )
        assert result == "strong"

    def test_endorsement_strong_needs_convergence(self, validator):
        """R82: Strong exige convergência ≥ 60%."""
        evals = [
            {"confidence": 0.6, "composite_relevance": 0.50, "endorsement": "moderate",
             "adjusted_viability": 0.6}
            for _ in range(5)
        ]
        # Baixa convergência (40% — apenas 2 de 5)
        result = validator._calibrate_endorsement(
            weighted_relevance=0.50,
            convergence_rate=0.40,
            evaluations=evals,
        )
        assert result == "moderate"  # cai para moderate

    def test_endorsement_weak_with_low_relevance(self, validator):
        """R82: Weak quando relevância é muito baixa."""
        evals = [
            {"confidence": 0.4, "composite_relevance": 0.10, "endorsement": "weak",
             "adjusted_viability": 0.3}
            for _ in range(3)
        ]
        result = validator._calibrate_endorsement(
            weighted_relevance=0.10,
            convergence_rate=0.30,
            evaluations=evals,
        )
        assert result == "weak"

    def test_confidence_calculation(self, validator):
        """R82: Confidence score baseado em h-index."""
        # Professor com h-index alto deve ter confidence maior
        prof_high = Professor("h", "High", "PhD", "quantum",
                              ["Quantum"], ["qubit"], h_index=40)
        prof_low = Professor("l", "Low", "PhD", "quantum",
                             ["Quantum"], ["qubit"], h_index=2)
        
        from synthetic_university.empirical_validation import STRONG_CONFIDENCE_THRESHOLD
        
        # Testar via validação
        env = validator
        # Simular avaliação
        high_conf = env._professor_evaluate_thesis(
            prof_high, 
            type('MockThesis', (), {
                'source_combinations': ['qubit'], 
                'title': 'test',
                'hypothesis': 'quantum hypothesis',
                'feasibility_score': 0.7
            })()
        )
        low_conf = env._professor_evaluate_thesis(
            prof_low,
            type('MockThesis', (), {
                'source_combinations': ['qubit'],
                'title': 'test',
                'hypothesis': 'quantum hypothesis',
                'feasibility_score': 0.7
            })()
        )
        
        assert high_conf['confidence'] > low_conf['confidence']

    def test_full_validation_includes_calibration(self, validator):
        """R82: Validação completa inclui calibrated_endorsement."""
        engine = CombinatorialDiscoveryEngine(FACULTY_MAP)
        thesis_gen = ThesisGenerator()
        comb = engine.test_combination(("ética", "qubit"))
        thesis = thesis_gen.generate_thesis(comb)
        
        result = validator.evaluate_thesis(thesis)
        assert "calibrated_endorsement" in result
        assert "convergence_rate" in result
        assert result["calibrated_endorsement"] in ("strong", "moderate", "weak")

    def test_batch_validation_shows_calibrated_distribution(self, validator):
        """R82: Validação em lote mostra distribuição calibrada."""
        engine = CombinatorialDiscoveryEngine(FACULTY_MAP)
        thesis_gen = ThesisGenerator()
        
        combs = [
            engine.test_combination(("ética", "qubit")),
            engine.test_combination(("consciência", "algoritmo")),
            engine.test_combination(("dado", "saúde")),
        ]
        theses = [thesis_gen.generate_thesis(c) for c in combs]
        
        validation = validator.validate_theses(theses)
        assert "calibrated_endorsement_distribution" in validation
        dist = validation["calibrated_endorsement_distribution"]
        total = sum(dist.values())
        # Apenas teses válidas contam
        assert total == validation["n_valid"]
        assert total > 0
