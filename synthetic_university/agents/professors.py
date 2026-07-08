"""Registro de Professores da Universidade Sintética.

Cria um corpo docente diversificado com especialistas de todas as áreas.
"""

from __future__ import annotations
from typing import List, Dict
from synthetic_university.agents.professor_base import Professor

# =========================================================================
# Catálogo de Professores
# =========================================================================

PROFESSOR_REGISTRY: List[Professor] = []


def _p(id_, nome, title, faculty, specialties, interests, pubs=20, h_idx=8):
    """Helper para criar professor."""
    return Professor(
        professor_id=id_,
        nome=nome,
        title=title,
        faculty_id=faculty,
        specialties=specialties,
        research_interests=interests,
        publications=pubs,
        h_index=h_idx,
    )


def create_all_professors() -> List[Professor]:
    """Cria e retorna todos os professores da universidade."""
    global PROFESSOR_REGISTRY
    if PROFESSOR_REGISTRY:
        return PROFESSOR_REGISTRY
    
    professors = [
        # ========== CIÊNCIAS HUMANAS ==========
        _p("prof_hum_01", "Helena Arendt", "PhD", "human_sciences",
           ["Fenomenologia", "Ética", "Filosofia da Mente", "Hermenêutica"],
           ["consciência", "intencionalidade", "subjetividade", "alteridade"],
           pubs=45, h_idx=22),
        _p("prof_hum_02", "Miguel Bourdieu", "PhD", "human_sciences",
           ["Sociologia do Conhecimento", "Teoria Crítica", "Antropologia Social"],
           ["poder", "discurso", "habitus", "campo social", "capital simbólico"],
           pubs=38, h_idx=18),
        _p("prof_hum_03", "Sofia Freud", "Livre-Docente", "human_sciences",
           ["Psicanálise", "Psicologia Profunda", "Teoria do Inconsciente"],
           ["inconsciente", "desejo", "sintoma", "transferência", "recalque"],
           pubs=52, h_idx=25),
        _p("prof_hum_04", "Lucas Vygotsky", "PhD", "human_sciences",
           ["Psicologia Cognitiva", "Desenvolvimento Humano", "Aprendizagem"],
           ["mediação", "zona de desenvolvimento proximal", "linguagem", "cognição"],
           pubs=30, h_idx=15),
        
        # ========== CIÊNCIAS SOCIAIS ==========
        _p("prof_soc_01", "Amartya Rawls", "PhD", "social_sciences",
           ["Economia Política", "Teoria da Justiça", "Desenvolvimento"],
           ["justiça distributiva", "equidade", "desenvolvimento", "instituições"],
           pubs=55, h_idx=28),
        _p("prof_soc_02", "Clara Habermas", "PhD", "social_sciences",
           ["Teoria Política", "Comunicação", "Esfera Pública", "Democracia"],
           ["esfera pública", "ação comunicativa", "deliberação", "consenso"],
           pubs=42, h_idx=20),
        _p("prof_soc_03", "Roberto Keynes", "PhD", "social_sciences",
           ["Macroeconomia", "Política Fiscal", "Desenvolvimento Econômico"],
           ["PIB", "inflação", "emprego", "política monetária", "crescimento"],
           pubs=48, h_idx=24),
        _p("prof_soc_04", "Maria Foucault", "Livre-Docente", "social_sciences",
           ["Direito", "Teoria do Estado", "Biopolítica", "Governamentalidade"],
           ["poder disciplinar", "biopolítica", "governamentalidade", "norma"],
           pubs=35, h_idx=17),
        
        # ========== ENGENHARIA ==========
        _p("prof_eng_01", "Alan Turing Jr.", "PhD", "engineering",
           ["Engenharia de Software", "Sistemas Distribuídos", "Computabilidade"],
           ["algoritmo", "máquina de Turing", "complexidade", "sistemas"],
           pubs=60, h_idx=30),
        _p("prof_eng_02", "Grace Hopper", "PhD", "engineering",
           ["Arquitetura de Software", "Linguagens de Programação", "Compiladores"],
           ["compilador", "linguagem", "sistema", "abstração", "interface"],
           pubs=40, h_idx=19),
        _p("prof_eng_03", "Nikola Tesla Jr.", "PhD", "engineering",
           ["Engenharia de Sistemas", "IoT", "Sistemas Embarcados", "Tempo Real"],
           ["sistema embarcado", "tempo real", "IoT", "sensor", "malha"],
           pubs=33, h_idx=16),
        _p("prof_eng_04", "Margaret Hamilton", "PhD", "engineering",
           ["Engenharia de Confiabilidade", "Sistemas Críticos", "Testes"],
           ["confiabilidade", "tolerância a falhas", "verificação", "validação"],
           pubs=28, h_idx=14),
        
        # ========== LETRAS & LINGUÍSTICA ==========
        _p("prof_let_01", "Ferdinand Saussure", "PhD", "literary_linguistic",
           ["Linguística Estrutural", "Semiótica", "Teoria do Signo"],
           ["signo", "significante", "significado", "língua", "fala", "sincronia"],
           pubs=35, h_idx=21),
        _p("prof_let_02", "Jorge Borges", "PhD", "literary_linguistic",
           ["Teoria Literária", "Literatura Comparada", "Narratologia"],
           ["narrativa", "intertextualidade", "metáfora", "tempo narrativo"],
           pubs=50, h_idx=26),
        _p("prof_let_03", "Noam Chomsky Jr.", "PhD", "literary_linguistic",
           ["Linguística Gerativa", "Sintaxe", "Gramática Universal"],
           ["gramática universal", "sintaxe", "competência", "gerativismo"],
           pubs=70, h_idx=35),
        _p("prof_let_04", "Érica Bakhtin", "Livre-Docente", "literary_linguistic",
           ["Análise do Discurso", "Sociolinguística", "Dialogismo"],
           ["dialogismo", "polifonia", "enunciado", "gênero discursivo"],
           pubs=32, h_idx=15),
        
        # ========== HISTÓRIA ==========
        _p("prof_his_01", "Fernand Bloch", "PhD", "historical",
           ["História Social", "Escola dos Annales", "Longa Duração"],
           ["longa duração", "estrutura", "conjuntura", "civilização"],
           pubs=40, h_idx=23),
        _p("prof_his_02", "Euclides Cunha", "PhD", "historical",
           ["História do Brasil", "História Cultural", "Formação Social"],
           ["nação", "identidade", "cultura", "mestiçagem", "sertão"],
           pubs=25, h_idx=12),
        _p("prof_his_03", "Carlo Ginzburg", "PhD", "historical",
           ["Micro-história", "História das Mentalidades", "Paradigma Indiciário"],
           ["micro-história", "indício", "cultura popular", "narrativa histórica"],
           pubs=30, h_idx=18),
        _p("prof_his_04", "Dona Haraway", "PhD", "historical",
           ["História Digital", "Humanidades Digitais", "História Ambiental"],
           ["big data histórico", "arquivo digital", "antropoceno", "história digital"],
           pubs=22, h_idx=11),
        
        # ========== QUÂNTICA ==========
        _p("prof_qua_01", "Richard Feynman II", "PhD", "quantum",
           ["Computação Quântica", "QED", "Simulação Quântica"],
           ["qubit", "superposição", "emaranhamento", "simulação quântica"],
           pubs=65, h_idx=32),
        _p("prof_qua_02", "Niels Bohr Jr.", "PhD", "quantum",
           ["Informação Quântica", "Criptografia Quântica", "Fundamentos"],
           ["complementaridade", "medida", "decoerência", "interpretação"],
           pubs=45, h_idx=22),
        _p("prof_qua_03", "Shor Grover", "PhD", "quantum",
           ["Algoritmos Quânticos", "Qiskit", "Correção de Erros"],
           ["algoritmo de Shor", "algoritmo de Grover", "QEC", "circuito quântico"],
           pubs=38, h_idx=19),
        _p("prof_qua_04", "Ada Lovelace Quantum", "PhD", "quantum",
           ["QML", "TensorFlow Quantum", "PennyLane", "VQE"],
           ["quantum ML", "VQE", "QAOA", "quantum kernel", "Cirq"],
           pubs=30, h_idx=15),
        
        # ========== CIÊNCIAS EXATAS ==========
        _p("prof_exa_01", "Leonhard Euler Jr.", "PhD", "exact_sciences",
           ["Matemática Pura", "Teoria dos Números", "Análise Complexa"],
           ["número", "função", "equação", "teorema", "prova"],
           pubs=80, h_idx=40),
        _p("prof_exa_02", "Marie Curie", "PhD", "exact_sciences",
           ["Física Experimental", "Radioatividade", "Espectroscopia"],
           ["átomo", "radiação", "espectro", "decaimento"],
           pubs=55, h_idx=28),
        _p("prof_exa_03", "Albert Einstein II", "PhD", "exact_sciences",
           ["Física Teórica", "Relatividade", "Cosmologia"],
           ["relatividade", "espaço-tempo", "gravidade", "cosmologia"],
           pubs=72, h_idx=36),
        _p("prof_exa_04", "Rosalind Franklin", "PhD", "exact_sciences",
           ["Química Estrutural", "Cristalografia", "Biofísica"],
           ["estrutura", "cristal", "difração", "biomolécula"],
           pubs=33, h_idx=17),
        
        # ========== ESTATÍSTICA & DATA SCIENCE ==========
        _p("prof_est_01", "Ronald Fisher Jr.", "PhD", "statistics_ds",
           ["Inferência Estatística", "Delineamento Experimental", "Genética"],
           ["teste de hipótese", "ANOVA", "p-valor", "delineamento"],
           pubs=58, h_idx=29),
        _p("prof_est_02", "Thomas Bayes Jr.", "PhD", "statistics_ds",
           ["Estatística Bayesiana", "MCMC", "Modelagem Hierárquica"],
           ["bayesiano", "posterior", "MCMC", "prior", "verossimilhança"],
           pubs=42, h_idx=21),
        _p("prof_est_03", "Geoffrey Hinton", "PhD", "statistics_ds",
           ["Deep Learning", "Redes Neurais", "Aprendizagem por Representação"],
           ["deep learning", "backpropagation", "rede neural", "representação"],
           pubs=90, h_idx=45),
        _p("prof_est_04", "Fei-Fei Li", "PhD", "statistics_ds",
           ["Visão Computacional", "Aprendizagem Supervisionada", "Datasets"],
           ["CNN", "classificação", "dataset", "visão computacional"],
           pubs=48, h_idx=24),
        
        # ========== PROGRAMAÇÃO ==========
        _p("prof_prog_01", "Edsger Dijkstra II", "PhD", "programming",
           ["Linguagens Formais", "Verificação Formal", "Teoria dos Tipos"],
           ["algoritmo", "prova formal", "tipo", "lambda calculus", "correção"],
           pubs=45, h_idx=23),
        _p("prof_prog_02", "Barbara Liskov", "PhD", "programming",
           ["Linguagens de Programação", "Sistemas de Tipos", "Programação Funcional"],
           ["tipo", "subtipo", "abstração", "composição", "herança"],
           pubs=40, h_idx=20),
        _p("prof_prog_03", "Rob Pike", "PhD", "programming",
           ["Programação Concorrente", "Sistemas Operacionais", "Linguagem Go"],
           ["concorrência", "goroutine", "canal", "CSP", "comunicação"],
           pubs=35, h_idx=18),
        _p("prof_prog_04", "Simon Peyton Jones", "PhD", "programming",
           ["Programação Funcional", "Compiladores", "Haskell", "Teoria dos Tipos"],
           ["monada", "functor", "Haskell", "GHC", "lazy evaluation"],
           pubs=50, h_idx=25),
        
        # ========== INTERDISCIPLINAR ==========
        _p("prof_int_01", "Edgar Morin Jr.", "PhD", "interdisciplinary",
           ["Complexidade", "Pensamento Sistêmico", "Transdisciplinaridade"],
           ["complexidade", "auto-organização", "emergência", "sistema"],
           pubs=40, h_idx=22),
        _p("prof_int_02", "Donna Haraway", "PhD", "interdisciplinary",
           ["STS", "Ciência e Tecnologia", "Epistemologia Feminista"],
           ["saberes localizados", "natureza-cultura", "tecno-ciência"],
           pubs=35, h_idx=19),
        _p("prof_int_03", "Thomas Kuhn Jr.", "PhD", "interdisciplinary",
           ["Filosofia da Ciência", "Metaciência", "História da Ciência"],
           ["paradigma", "revolução científica", "ciência normal", "incomensurabilidade"],
           pubs=30, h_idx=16),
        _p("prof_int_04", "Elon Musk Academia", "PhD", "interdisciplinary",
           ["Inovação", "Design Science", "Futurismo", "Tecnologia Social"],
           ["inovação disruptiva", "design", "futuro", "tecnologia social"],
           pubs=20, h_idx=10),
        
        # ========== EXTRA — Mestres Transversais ==========
        _p("prof_master_01", "Leonardo Da Vinci IA", "Doutor Honoris Causa", "interdisciplinary",
           ["Arte", "Ciência", "Engenharia", "Anatomia", "Invenção"],
           ["analogia", "observação", "natureza", "inovação", "criação"],
           pubs=100, h_idx=50),
        _p("prof_master_02", "Nikola Tesla Visão", "Doutor Honoris Causa", "engineering",
           ["Eletromagnetismo", "Energia", "Frequências", "Ressonância"],
           ["ressonância", "campo", "frequência", "energia livre", "invenção"],
           pubs=65, h_idx=30),
    ]
    
    PROFESSOR_REGISTRY = professors
    return professors


def get_professors_by_faculty(faculty_id: str) -> List[Professor]:
    """Retorna todos os professores de uma faculdade."""
    if not PROFESSOR_REGISTRY:
        create_all_professors()
    return [p for p in PROFESSOR_REGISTRY if p.faculty_id == faculty_id]
