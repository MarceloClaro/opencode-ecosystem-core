"""Classe base para Professores da Universidade Sintética."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable


@dataclass
class Professor:
    """Um professor/pesquisador na universidade sintética.
    
    Cada professor tem especialidade, faculdade de origem,
    e pode avaliar combinações, gerar insights, etc.
    """
    professor_id: str
    nome: str
    title: str  # e.g., "PhD", "Livre-Docente", "Titular"
    faculty_id: str
    specialties: List[str] = field(default_factory=list)
    research_interests: List[str] = field(default_factory=list)
    publications: int = 0
    h_index: int = field(default=0)
    trust_score: float = 0.8
    
    def evaluate_combination(
        self, concepts: tuple, viability: float, novelty: float
    ) -> Dict:
        """Avalia uma combinação de conceitos segundo a perspectiva do professor."""
        specialty_overlap = sum(
            1 for c in concepts
            if any(s.lower() in c.lower() or c.lower() in s.lower()
                   for s in self.specialties)
        )
        
        interest_overlap = sum(
            1 for c in concepts
            if any(i.lower() in c.lower() or c.lower() in i.lower()
                   for i in self.research_interests)
        )
        
        return {
            "professor_id": self.professor_id,
            "nome": self.nome,
            "faculty_id": self.faculty_id,
            "specialty_relevance": min(1.0, specialty_overlap / max(1, len(concepts))),
            "interest_relevance": min(1.0, interest_overlap / max(1, len(concepts))),
            "adjusted_viability": viability * (0.7 + 0.3 * specialty_overlap),
            "endorsement": "strong" if specialty_overlap >= 2 else (
                "moderate" if specialty_overlap >= 1 else "weak"
            ),
        }
    
    def suggest_research_direction(
        self, concepts: List[str]
    ) -> str:
        """Sugere direção de pesquisa com base na especialidade."""
        if not concepts:
            return f"{self.nome} aguarda propostas de pesquisa."
        
        relevant = [c for c in concepts 
                   if any(s.lower() in c.lower() for s in self.specialties)]
        
        if relevant:
            return (f"{self.nome} sugere investigar a correlação entre "
                    f"{' e '.join(relevant[:3])} sob a perspectiva da "
                    f"{self.specialties[0] if self.specialties else 'pesquisa'}.")
        else:
            return (f"{self.nome} reconhece a proposta mas recomenda "
                    f"explorar conexões com {self.specialties[0]} "
                    f"para maior profundidade teórica.")
    
    def __repr__(self) -> str:
        return (f"<Prof. {self.nome} ({self.title}) — "
                f"{self.faculty_id}, h={self.h_index}>")
