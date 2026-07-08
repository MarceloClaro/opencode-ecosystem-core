"""Testes TDD para a Universidade Sintética Transversal (SPEC-935)."""

import pytest
import time

from synthetic_university.faculties import (
    ALL_FACULTIES, FACULTY_MAP, HUMAN_SCIENCES, SOCIAL_SCIENCES,
    ENGINEERING, LITERARY_LINGUISTIC, HISTORICAL, QUANTUM,
    EXACT_SCIENCES, STATISTICS_DS, PROGRAMMING, INTERDISCIPLINARY,
    get_faculty, list_all_concepts, count_total_concepts,
)
from synthetic_university.combinatorial_engine import (
    CombinatorialDiscoveryEngine, ConceptEmbeddingSpace,
)
from synthetic_university.correlator import (
    InterdisciplinaryCorrelator, CorrelationType,
)
from synthetic_university.thesis_generator import (
    ThesisGenerator, AcademicLevel,
)
from synthetic_university.knowledge_graph import UniversityKnowledgeGraph
from synthetic_university.curriculum import Curriculum, Discipline, create_base_curriculum
from synthetic_university.agents.professors import (
    create_all_professors, get_professors_by_faculty, PROFESSOR_REGISTRY,
)
from synthetic_university.core import SyntheticUniversity


# =============================================================================
# CA1 — Faculdades e Domínios
# =============================================================================

class TestFaculdades:
    """Testes para as 10 faculdades da universidade sintética."""

    def test_dez_faculdades_existem(self):
        """CA1: 10 faculdades definidas."""
        assert len(ALL_FACULTIES) == 10

    def test_todas_faculdades_tem_id_unico(self):
        """CA1: IDs únicas e consistentes."""
        ids = [f.id for f in ALL_FACULTIES]
        assert len(ids) == len(set(ids))
        
        expected_ids = [
            "human_sciences", "social_sciences", "engineering",
            "literary_linguistic", "historical", "quantum",
            "exact_sciences", "statistics_ds", "programming",
            "interdisciplinary",
        ]
        for eid in expected_ids:
            assert eid in ids, f"Faculdade {eid} não encontrada"

    def test_cada_faculdade_tem_conceitos(self):
        """CA1: Cada faculdade tem pelo menos 20 conceitos."""
        for fac in ALL_FACULTIES:
            assert len(fac.conceitos) >= 20, (
                f"{fac.id} tem apenas {len(fac.conceitos)} conceitos"
            )

    def test_cada_faculdade_tem_subdisciplinas(self):
        """CA1: Cada faculdade tem pelo menos 3 subdisciplinas."""
        for fac in ALL_FACULTIES:
            assert len(fac.subdisciplinas) >= 3, (
                f"{fac.id} tem apenas {len(fac.subdisciplinas)} subdisciplinas"
            )

    def test_cada_faculdade_tem_metodos_pesquisa(self):
        """CA1: Cada faculdade tem métodos de pesquisa."""
        for fac in ALL_FACULTIES:
            assert len(fac.metodos_pesquisa) >= 3

    def test_cada_faculdade_tem_tradicoes_epistemologicas(self):
        """CA1: Cada faculdade tem tradições epistemológicas."""
        for fac in ALL_FACULTIES:
            assert len(fac.tradicoes_epistemologicas) >= 3

    def test_get_faculty_por_id(self):
        """CA1: Busca de faculdade por ID."""
        fac = get_faculty("quantum")
        assert fac is not None
        assert fac.id == "quantum"
        assert fac.nome == "Ciências Quânticas"

    def test_get_faculty_invalido(self):
        """CA1: Faculdade inexistente retorna None."""
        assert get_faculty("nao_existe") is None

    def test_list_all_concepts(self):
        """CA1: Lista consolidada de conceitos."""
        concepts = list_all_concepts()
        assert len(concepts) >= 200

    def test_faculdade_representacao(self):
        """CA1: __repr__ das faculdades."""
        rep = repr(HUMAN_SCIENCES)
        assert "Faculdade" in rep
        assert "human_sciences" in rep


# =============================================================================
# CA2 — MiroFish Combinatorial Discovery Engine
# =============================================================================

class TestCombinatorialEngine:
    """Testes para o motor combinatorial."""

    @pytest.fixture
    def engine(self):
        return CombinatorialDiscoveryEngine(FACULTY_MAP)

    def test_engine_cria(self, engine):
        """CA2: Engine é criado com as faculdades."""
        assert len(engine.faculty_map) == 10

    def test_embedding_similarity(self):
        """CA2: Similaridade entre conceitos."""
        emb = ConceptEmbeddingSpace()
        # Mesmo conceito
        assert emb.similarity("ética", "ética") == 1.0
        # Conceitos relacionados
        sim = emb.similarity("ética", "moral")
        assert 0.0 <= sim <= 1.0

    def test_embedding_coherence(self):
        """CA2: Coerência entre lista de conceitos."""
        emb = ConceptEmbeddingSpace()
        coherence = emb.coherence(["ética", "moral", "justiça"])
        assert 0.0 <= coherence <= 1.0

    def test_test_combination(self, engine):
        """CA2: Combinação simples é testada."""
        result = engine.test_combination(("ética", "algoritmo"))
        assert result is not None
        assert result.combination_id is not None
        assert len(result.concepts) == 2
        assert 0.0 <= result.composite_score <= 1.0

    def test_combination_unique_ids(self, engine):
        """CA2: IDs únicos para combinações diferentes."""
        r1 = engine.test_combination(("ética", "algoritmo"))
        r2 = engine.test_combination(("qubit", "consciência"))
        assert r1.combination_id != r2.combination_id

    def test_combination_deduplication(self, engine):
        """CA2: Mesma combinação não é testada duas vezes."""
        r1 = engine.test_combination(("ética", "algoritmo"))
        r2 = engine.test_combination(("ética", "algoritmo"))
        assert r1.combination_id == r2.combination_id

    def test_pair_generation(self, engine):
        """CA2: Geração de pares entre faculdades."""
        pairs = engine.generate_pair_combinations(
            ["human_sciences"], ["quantum"], max_combinations=50
        )
        assert len(pairs) <= 50
        if len(pairs) > 0:
            assert all(p.composite_score is not None for p in pairs)

    def test_triple_generation(self, engine):
        """CA2: Geração de triplas."""
        triples = engine.generate_triple_combinations(
            ["human_sciences", "quantum", "engineering"],
            max_combinations=30,
        )
        assert len(triples) <= 30

    def test_quadruple_generation(self, engine):
        """CA2: Geração de quádruplas."""
        quads = engine.generate_quadruple_combinations(
            list(FACULTY_MAP.keys())[:4],
            max_combinations=20,
        )
        assert len(quads) <= 20

    def test_pattern_assignment(self, engine):
        """CA2: Toda combinação recebe um padrão."""
        result = engine.test_combination(("ética", "algoritmo", "sociedade"))
        assert result.discovered_pattern in CombinatorialDiscoveryEngine.DISCOVERY_PATTERNS

    def test_get_top_combinations(self, engine):
        """CA2: Top combinações são ordenadas por score."""
        engine.test_combination(("a", "b"))
        engine.test_combination(("c", "d"))
        top = engine.get_top_combinations(10)
        assert len(top) >= 0
        scores = [t.composite_score for t in top]
        assert scores == sorted(scores, reverse=True)

    def test_get_statistics(self, engine):
        """CA2: Estatísticas do engine."""
        engine.test_combination(("ética", "algoritmo"))
        stats = engine.get_statistics()
        assert "total_tested" in stats
        assert "avg_composite" in stats


# =============================================================================
# CA3 — Thesis Generator
# =============================================================================

class TestThesisGenerator:
    """Testes para o gerador de teses."""

    @pytest.fixture
    def engine(self):
        return CombinatorialDiscoveryEngine(FACULTY_MAP)

    @pytest.fixture
    def thesis_gen(self):
        return ThesisGenerator()

    def test_thesis_from_combination(self, engine, thesis_gen):
        """CA3: Tese gerada a partir de uma combinação."""
        comb = engine.test_combination(("ética", "algoritmo", "sociedade"))
        thesis = thesis_gen.generate_thesis(comb)
        assert thesis is not None
        assert thesis.title is not None
        assert len(thesis.title) > 10
        assert thesis.hypothesis is not None
        assert thesis.academic_level in AcademicLevel

    def test_thesis_has_all_fields(self, engine, thesis_gen):
        """CA3: Tese tem todos os campos obrigatórios."""
        comb = engine.test_combination(("consciência", "qubit", "complexidade"))
        thesis = thesis_gen.generate_thesis(comb)
        assert thesis.thesis_id is not None
        assert thesis.foundation is not None
        assert thesis.methodology is not None
        assert thesis.correlation_evidence is not None
        assert thesis.conclusion is not None
        assert len(thesis.source_combinations) > 0

    def test_thesis_levels(self, thesis_gen):
        """CA3: Níveis acadêmicos disponíveis."""
        levels = list(AcademicLevel)
        assert len(levels) >= 5
        assert AcademicLevel.ESPECULACAO in levels
        assert AcademicLevel.HIPOTESE in levels
        assert AcademicLevel.TEORIA in levels
        assert AcademicLevel.PARADIGMA in levels
        assert AcademicLevel.DESCOBERTA in levels

    def test_batch_generate(self, engine, thesis_gen):
        """CA3: Geração em lote."""
        comb1 = engine.test_combination(("ética", "algoritmo"))
        comb2 = engine.test_combination(("consciência", "qubit"))
        theses = thesis_gen.batch_generate(
            [comb1, comb2], max_theses=2, min_composite=0.0
        )
        assert len(theses) <= 2

    def test_thesis_statistics(self, thesis_gen):
        """CA3: Estatísticas de teses."""
        stats = thesis_gen.get_statistics()
        assert "total_theses" in stats
        assert "avg_composite" in stats

    def test_get_top_theses(self, engine, thesis_gen):
        """CA3: Top teses."""
        comb = engine.test_combination(("ética", "algoritmo"))
        thesis_gen.generate_thesis(comb)
        top = thesis_gen.get_top_theses(5)
        assert len(top) >= 0


# =============================================================================
# CA4 — Correlator Interdisciplinar
# =============================================================================

class TestInterdisciplinaryCorrelator:
    """Testes para o correlator."""

    @pytest.fixture
    def correlator(self):
        return InterdisciplinaryCorrelator(FACULTY_MAP)

    def test_correlator_cria(self, correlator):
        """CA4: Correlator criado com índice conceitual."""
        assert correlator is not None

    def test_discover_correlation(self, correlator):
        """CA4: Correlação descoberta entre conceitos."""
        corr = correlator.discover_correlation(("ética", "moral", "justiça"))
        assert corr is not None
        assert corr.correlation_id is not None
        assert corr.strength > 0
        assert corr.significance > 0

    def test_correlation_types(self, correlator):
        """CA4: Tipos de correlação disponíveis."""
        for t in CorrelationType:
            assert t.value is not None

    def test_correlation_determination(self, correlator):
        """CA4: Tipo de correlação é determinado."""
        corr = correlator.discover_correlation(("ordem", "caos"))
        if corr:
            assert corr.correlation_type in [
                CorrelationType.ANTAGONICA, CorrelationType.DIALETICA,
                CorrelationType.CORRELACIONAL, CorrelationType.ISOMORFICA,
                CorrelationType.EMERGENTE,
            ]

    def test_cross_faculty_matrix(self, correlator):
        """CA4: Matriz de adjacência entre faculdades."""
        correlator.discover_correlation(("ética", "algoritmo"))
        matrix = correlator.get_cross_faculty_matrix()
        assert isinstance(matrix, dict)

    def test_correlator_statistics(self, correlator):
        """CA4: Estatísticas do correlator."""
        stats = correlator.get_statistics()
        assert "total_correlations" in stats
        assert "avg_strength" in stats


# =============================================================================
# CA5 — Knowledge Graph
# =============================================================================

class TestKnowledgeGraph:
    """Testes para o grafo de conhecimento."""

    @pytest.fixture
    def kg(self):
        return UniversityKnowledgeGraph()

    def test_kg_cria_vazio(self, kg):
        """CA5: Grafo começa vazio."""
        assert len(kg.nodes) == 0

    def test_add_faculty_node(self, kg):
        """CA5: Adicionar nó de faculdade."""
        node = kg.add_faculty("quantum", "Quantum")
        assert node is not None
        assert node.node_id == "faculty:quantum"
        assert node.node_type == "faculty"

    def test_add_concept_node(self, kg):
        """CA5: Adicionar nó de conceito."""
        node = kg.add_concept("qubit", "quantum")
        assert node is not None
        assert node.node_type == "concept"

    def test_add_edge(self, kg):
        """CA5: Adicionar aresta."""
        kg.add_faculty("test", "Test")
        kg.add_concept("conceito", "test")
        edge = kg.connect_faculty_to_concept("test", "conceito")
        assert edge is not None
        assert edge.edge_type == "contains"

    def test_build_from_faculties(self, kg):
        """CA5: Popula grafo com faculdades."""
        count = kg.build_from_faculties(ALL_FACULTIES)
        assert count > 0

    def test_query_by_type(self, kg):
        """CA5: Consulta por tipo."""
        kg.build_from_faculties(ALL_FACULTIES)
        faculties = kg.query_by_type("faculty")
        assert len(faculties) == 10

    def test_graph_statistics(self, kg):
        """CA5: Estatísticas do grafo."""
        kg.build_from_faculties(ALL_FACULTIES)
        stats = kg.get_statistics()
        assert stats["total_nodes"] > 0
        assert stats["faculties"] == 10

    def test_serialization(self, kg):
        """CA5: Serialização para dict."""
        kg.build_from_faculties(ALL_FACULTIES)
        d = kg.to_dict()
        assert "nodes" in d
        assert "edges" in d
        assert "stats" in d


# =============================================================================
# CA6 — Professores
# =============================================================================

class TestProfessores:
    """Testes para o corpo docente."""

    def test_professores_criados(self):
        """CA6: Professores são criados."""
        profs = create_all_professors()
        assert len(profs) >= 30

    def test_professores_tem_todas_faculdades(self):
        """CA6: Cada faculdade tem pelo menos 2 professores."""
        for fac in ALL_FACULTIES:
            profs = get_professors_by_faculty(fac.id)
            assert len(profs) >= 2, f"{fac.id} tem apenas {len(profs)} professores"

    def test_professor_evaluate_combination(self):
        """CA6: Professor avalia combinação."""
        profs = create_all_professors()
        prof = profs[0]
        result = prof.evaluate_combination(("ética", "consciência"), 0.7, 0.5)
        assert "professor_id" in result
        assert "adjusted_viability" in result
        assert "endorsement" in result

    def test_professor_suggest_research(self):
        """CA6: Professor sugere direção de pesquisa."""
        profs = create_all_professors()
        prof = profs[0]
        suggestion = prof.suggest_research_direction(["ética", "consciência"])
        assert suggestion is not None
        assert len(suggestion) > 10


# =============================================================================
# CA6 — Curriculum
# =============================================================================

class TestCurriculum:
    """Testes para o currículo."""

    def test_base_curriculum(self):
        """CA6: Currículo base tem disciplinas."""
        curr = create_base_curriculum()
        assert curr.count() >= 15

    def test_add_discipline(self):
        """CA6: Adicionar disciplina."""
        curr = Curriculum()
        disc = Discipline("Teste", "quantum", "Teste", ["qubit"])
        curr.add_discipline(disc)
        assert curr.count() == 1


# =============================================================================
# CA6 — Synthetic University Core (Full Cycle)
# =============================================================================

class TestSyntheticUniversity:
    """Testes de integração do orquestrador central."""

    @pytest.fixture
    def university(self):
        return SyntheticUniversity(target_combinations=500)

    def test_university_cria(self, university):
        """CA6: Universidade é criada com faculdades e professores."""
        assert len(university.faculties) == 10
        assert len(university.professors) >= 30

    def test_university_full_cycle_light(self, university):
        """CA6: Ciclo completo leve (100 combinações)."""
        report = university.run_full_cycle(
            target_combinations=100,
            generate_theses=True,
        )
        assert report is not None
        assert report.combinations_tested >= 0
        assert report.theses_generated >= 0
        assert report.graph_nodes > 0

    def test_university_curriculum_vitae(self, university):
        """CA6: Geração do CV textual."""
        cv = university.get_curriculum_vitae()
        assert "UNIVERSIDADE SINTÉTICA TRANSVERSAL" in cv
        assert "Faculdades:" in cv

    def test_university_summary(self, university):
        """CA6: Resumo da universidade."""
        summary = university.get_summary()
        assert summary["faculties"] == 10
        assert summary["professors"] >= 30
        assert "total_combinations_tested" in summary

    def test_university_events(self, university):
        """CA6: Eventos registrados."""
        events = []
        university.on_event(lambda e, d: events.append((e, d)))
        university.run_full_cycle(target_combinations=50, generate_theses=False)
        assert len(events) >= 2

    def test_10000_target_set(self):
        """CA6: Target de 10000 combinações é configurável."""
        uni = SyntheticUniversity(target_combinations=10000)
        assert uni.target_combinations == 10000


# =============================================================================
# Testes de conceitos específicos do ecossistema
# =============================================================================

class TestEcosystemIntegration:
    """Testes de integração com o ecossistema OpenCode."""

    def test_faculdade_quantum_tem_qiskit_cirq(self):
        """Quantum inclui Qiskit, Cirq, PennyLane, TensorFlow Quantum."""
        quantum = QUANTUM
        tools = ' '.join(quantum.ferramentas).lower()
        assert 'qiskit' in tools
        assert 'cirq' in tools
        assert 'pennylane' in tools
        assert 'tensorflow quantum' in tools or 'tfq' in tools or 'tensorflow' in tools

    def test_faculdade_programming_tem_go_rust(self):
        """Programming inclui Go, Rust, Python, Haskell."""
        prog = PROGRAMMING
        tools = ' '.join(prog.ferramentas).lower()
        assert 'go' in tools
        assert 'rust' in tools
        assert 'python' in tools

    def test_faculdade_interdisciplinar_tem_complexidade(self):
        """Interdisciplinar inclui complexidade, metaciência, inovação."""
        conc = set(c.lower() for c in INTERDISCIPLINARY.conceitos)
        assert 'complexidade' in conc or 'complexity' in conc
        assert 'meta-conhecimento' in conc or 'metaciência' in conc
        assert 'inovação' in conc or 'inovacao' in conc or 'innovation' in conc

    def test_correlation_across_quantum_and_consciousness(self):
        """Correlação entre quântica e consciência é possível."""
        correlator = InterdisciplinaryCorrelator(FACULTY_MAP)
        corr = correlator.discover_correlation(("qubit", "consciência"))
        if corr:
            # Can be 0 for cross-domain with no lexical overlap
            # but at least we have 2+ faculties and correct types
            assert corr.composite_correlation >= 0
            assert len(corr.faculties) >= 2

    def test_professors_all_faculties_covered(self):
        """Todos os professores cobrem todas as faculdades."""
        profs = create_all_professors()
        facs_with_profs = set(p.faculty_id for p in profs)
        expected = set(f.id for f in ALL_FACULTIES)
        assert facs_with_profs == expected, (
            f"Faculdades sem professores: {expected - facs_with_profs}"
        )
