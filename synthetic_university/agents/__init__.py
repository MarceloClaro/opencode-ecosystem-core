"""Agentes especialistas (professores) da Universidade Sintética."""
from synthetic_university.agents.professor_base import Professor
from synthetic_university.agents.professors import (
    create_all_professors,
    get_professors_by_faculty,
    PROFESSOR_REGISTRY,
)

__all__ = [
    "Professor",
    "create_all_professors",
    "get_professors_by_faculty",
    "PROFESSOR_REGISTRY",
]
