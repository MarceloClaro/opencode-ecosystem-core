"""Universidade Sintética Transversal — SPEC-935.

Meta-subsistema multiagente que simula uma instituição acadêmica completa,
organizando conhecimento em 10 faculdades e usando MiroFish para descobrir
10.000+ combinações interdisciplinares, gerando teses PhD-level.
"""

from synthetic_university.faculties import (
    Faculdade,
    HUMAN_SCIENCES,
    SOCIAL_SCIENCES,
    ENGINEERING,
    LITERARY_LINGUISTIC,
    HISTORICAL,
    QUANTUM,
    EXACT_SCIENCES,
    STATISTICS_DS,
    PROGRAMMING,
    INTERDISCIPLINARY,
    ALL_FACULTIES,
    FACULTY_MAP,
    get_faculty,
    list_all_concepts,
)

from synthetic_university.core import SyntheticUniversity

from synthetic_university.combinatorial_engine import (
    CombinatorialDiscoveryEngine,
    CombinationResult,
)

from synthetic_university.correlator import (
    InterdisciplinaryCorrelator,
    Correlation,
    CorrelationType,
)

from synthetic_university.thesis_generator import (
    ThesisGenerator,
    Thesis,
    AcademicLevel,
)

from synthetic_university.knowledge_graph import (
    UniversityKnowledgeGraph,
)

from synthetic_university.curriculum import (
    Curriculum,
    Discipline,
    create_base_curriculum,
)

from synthetic_university.agents.professor_base import Professor
from synthetic_university.agents.professors import (
    create_all_professors,
    get_professors_by_faculty,
    PROFESSOR_REGISTRY,
)

__all__ = [
    # Faculdades
    "Faculdade", "HUMAN_SCIENCES", "SOCIAL_SCIENCES", "ENGINEERING",
    "LITERARY_LINGUISTIC", "HISTORICAL", "QUANTUM", "EXACT_SCIENCES",
    "STATISTICS_DS", "PROGRAMMING", "INTERDISCIPLINARY", "ALL_FACULTIES",
    "FACULTY_MAP", "get_faculty", "list_all_concepts",
    # Core
    "SyntheticUniversity",
    # Engine
    "CombinatorialDiscoveryEngine", "CombinationResult",
    # Correlator
    "InterdisciplinaryCorrelator", "Correlation", "CorrelationType",
    # Thesis
    "ThesisGenerator", "Thesis", "AcademicLevel",
    # Knowledge Graph
    "UniversityKnowledgeGraph",
    # Curriculum
    "Curriculum", "Discipline", "create_base_curriculum",
    # Agents
    "Professor", "create_all_professors", "get_professors_by_faculty",
    "PROFESSOR_REGISTRY",
]
