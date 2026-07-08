"""Currículo Sintético — SPEC-935.

Disciplinas, cursos e grades curriculares geradas a partir das
descobertas da universidade.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


NivelDisciplina = Enum(
    "NivelDisciplina",
    ["INTRODUCAO", "INTERMEDIARIO", "AVANCADO", "POS_GRADUACAO", "PESQUISA"],
)


@dataclass
class Discipline:
    """Uma disciplina ofertada pela universidade sintética."""
    name: str
    faculty: str
    description: str = ""
    concepts: List[str] = field(default_factory=list)
    level: str = "POS_GRADUACAO"
    workload_h: int = 60
    professor_id: Optional[str] = None
    semester: str = "2026.2"


class Curriculum:
    """Grade curricular da universidade, com disciplinas por faculdade."""
    
    def __init__(self):
        self._disciplines: List[Discipline] = []
        self._disciplines_by_faculty: dict = {}
    
    def add_discipline(self, discipline: Discipline):
        """Adiciona disciplina ao currículo."""
        self._disciplines.append(discipline)
        if discipline.faculty not in self._disciplines_by_faculty:
            self._disciplines_by_faculty[discipline.faculty] = []
        self._disciplines_by_faculty[discipline.faculty].append(discipline)
    
    def get_disciplines(self, faculty: Optional[str] = None) -> List[Discipline]:
        """Retorna disciplinas, opcionalmente filtradas por faculdade."""
        if faculty:
            return self._disciplines_by_faculty.get(faculty, [])
        return self._disciplines
    
    def count(self) -> int:
        return len(self._disciplines)


# =========================================================================
# Currículo base inicial
# =========================================================================

def create_base_curriculum() -> Curriculum:
    """Cria o currículo base com disciplinas fundamentais."""
    curr = Curriculum()
    
    # Disciplinas base por faculdade
    base_disciplines = [
        Discipline("Fenomenologia da Percepção", "human_sciences",
                   "Estudo da intencionalidade e da experiência vivida",
                   ["consciência", "percepção", "intencionalidade", "corpo"]),
        Discipline("Ética Aplicada à Pesquisa", "human_sciences",
                   "Fundamentos éticos para a produção de conhecimento",
                   ["ética", "moral", "responsabilidade", "dignidade"]),
        Discipline("Teoria da Justiça Distributiva", "social_sciences",
                   "Modelos de equidade e alocação de recursos",
                   ["justiça", "equidade", "distribuição", "direitos"]),
        Discipline("Economia Comportamental e Decisão", "social_sciences",
                   "Intersecção entre psicologia e economia",
                   ["decisão", "heurística", "viés", "preferência"]),
        Discipline("Arquitetura de Sistemas Complexos", "engineering",
                   "Projeto e análise de sistemas com múltiplos componentes",
                   ["sistema", "arquitetura", "complexidade", "emergência"]),
        Discipline("Verificação Formal de Software", "engineering",
                   "Métodos formais para correção de programas",
                   ["prova formal", "model checking", "correção", "especificação"]),
        Discipline("Semiótica e Linguagem", "literary_linguistic",
                   "Teoria dos signos e sistemas de significação",
                   ["signo", "símbolo", "interpretação", "código"]),
        Discipline("Narratologia Transmidiática", "literary_linguistic",
                   "Estruturas narrativas em múltiplas mídias",
                   ["narrativa", "enredo", "discurso", "mídia"]),
        Discipline("História Global Comparada", "historical",
                   "Conexões e paralelos entre civilizações",
                   ["global", "comparação", "civilização", "conexão"]),
        Discipline("Arqueologia Digital e Patrimônio", "historical",
                   "Métodos digitais para pesquisa arqueológica",
                   ["arqueologia", "digital", "patrimônio", "dados"]),
        Discipline("Algoritmos Quânticos Avançados", "quantum",
                   "Implementação de algoritmos quânticos em Qiskit e Cirq",
                   ["qubit", "circuito quântico", "Qiskit", "Cirq", "algoritmo"]),
        Discipline("QML — Quantum Machine Learning", "quantum",
                   "Aplicações de aprendizado de máquina em computadores quânticos",
                   ["quantum ML", "VQE", "kernel quântico", "PennyLane", "TFQ"]),
        Discipline("Teoria de Grupos e Simetrias", "exact_sciences",
                   "Fundamentos matemáticos das simetrias na natureza",
                   ["grupo", "simetria", "invariância", "transformação"]),
        Discipline("Cosmologia e Formação de Estruturas", "exact_sciences",
                   "Origem e evolução do universo em larga escala",
                   ["big bang", "cosmologia", "matéria escura", "galáxia"]),
        Discipline("Inferência Causal e Do-Calculus", "statistics_ds",
                   "Métodos para inferir causalidade a partir de dados",
                   ["causalidade", "Do-calculus", "DAG", "confundidor"]),
        Discipline("Deep Learning: Fundamentos e Arquiteturas", "statistics_ds",
                   "Redes neurais profundas, CNNs, RNNs, Transformers",
                   ["deep learning", "CNN", "transformer", "atenção", "backprop"]),
        Discipline("Teoria dos Tipos e Lambda Calculus", "programming",
                   "Fundamentos formais da programação funcional",
                   ["tipo", "lambda calculus", "Curry-Howard", "monada"]),
        Discipline("Programação Concorrente em Go e Rust", "programming",
                   "Modelos de concorrência: goroutines, canais, ownership",
                   ["concorrência", "goroutine", "ownership", "Go", "Rust"]),
        Discipline("Complexidade e Sistemas Adaptativos", "interdisciplinary",
                   "Emergência, auto-organização e evolução em sistemas complexos",
                   ["complexidade", "emergência", "auto-organização", "caos"]),
        Discipline("Metaciência: a Ciência da Ciência", "interdisciplinary",
                   "Análise da produção, validação e evolução do conhecimento",
                   ["metaciência", "paradigma", "replicação", "ciência aberta"]),
        # ========== CIÊNCIAS DA SAÚDE ==========
        Discipline("Anatomia e Fisiologia Humana", "health_sciences",
                   "Estudo da estrutura e funcionamento do corpo humano",
                   ["sistema nervoso", "coração", "homeostase", "órgão"]),
        Discipline("Psiquiatria e Saúde Mental", "health_sciences",
                   "Transtornos mentais, diagnóstico e abordagens terapêuticas",
                   ["depressão", "ansiedade", "esquizofrenia", "psicofármaco"]),
        Discipline("Farmacologia Geral e Clínica", "health_sciences",
                   "Princípios da ação de fármacos no organismo humano",
                   ["farmacocinética", "receptor", "dose", "interação medicamentosa"]),
        Discipline("Epidemiologia e Saúde Pública", "health_sciences",
                   "Distribuição e determinantes de doenças na população",
                   ["incidência", "prevalência", "fator de risco", "vigilância"]),
        Discipline("Bioética e Medicina Legal", "health_sciences",
                   "Princípios éticos na prática médica e perícias",
                   ["autonomia", "beneficência", "consentimento", "sigilo médico"]),
    ]
    
    for disc in base_disciplines:
        curr.add_discipline(disc)
    
    return curr
