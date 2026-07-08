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
        # ========== CIÊNCIAS DA SAÚDE ==========
        _p("prof_sau_01", "William Osler Jr.", "PhD", "health_sciences",
           ["Medicina Geral", "Clínica Médica", "Semiologia", "Diagnóstico"],
           ["exame clínico", "anamnese", "diagnóstico diferencial", "terapêutica"],
           pubs=60, h_idx=30),
        _p("prof_sau_02", "Sigmund Freud II", "PhD", "health_sciences",
           ["Psiquiatria", "Psicanálise", "Psicopatologia", "Saúde Mental"],
           ["psiquiatria", "transtorno mental", "saúde mental", "psicopatologia"],
           pubs=70, h_idx=35),
        _p("prof_sau_03", "Alexander Fleming Jr.", "PhD", "health_sciences",
           ["Farmacologia", "Microbiologia", "Antibióticos", "Farmacocinética"],
           ["fármaco", "antibiótico", "farmacocinética", "descoberta de fármacos"],
           pubs=55, h_idx=28),
        _p("prof_sau_04", "Florence Nightingale", "PhD", "health_sciences",
           ["Enfermagem", "Saúde Pública", "Epidemiologia", "Humanização"],
           ["enfermagem", "cuidado", "saúde pública", "epidemiologia"],
           pubs=40, h_idx=20),
        _p("prof_sau_05", "Nise da Silveira", "PhD", "health_sciences",
           ["Psiquiatria", "Terapia Ocupacional", "Reabilitação", "Humanização"],
           ["reabilitação", "arte-terapia", "afeto", "terapia ocupacional"],
           pubs=30, h_idx=15),
        _p("prof_sau_06", "Albert Sabin", "PhD", "health_sciences",
           ["Pediatria", "Imunologia", "Vacinas", "Virologia"],
           ["vacina", "imunização", "pediatria", "prevenção"],
           pubs=50, h_idx=25),
        _p("prof_sau_07", "Ana Nery", "PhD", "health_sciences",
           ["Enfermagem", "Saúde Coletiva", "Atenção Primária", "SUS"],
           ["cuidados de enfermagem", "atenção primária", "saúde coletiva"],
           pubs=25, h_idx=12),
        _p("prof_sau_08", "César Lattes", "PhD", "health_sciences",
           ["Física Médica", "Radiologia", "Imagem Diagnóstica", "Medicina Nuclear"],
           ["diagnóstico por imagem", "radiologia", "medicina nuclear", "radioterapia"],
           pubs=35, h_idx=18),
    ]
    
    # ========== PROFESSORES SINTÉTICOS ADICIONAIS (R82) ==========
    additional = generate_additional_professors()
    professors.extend(additional)
    
    PROFESSOR_REGISTRY = professors
    return professors


def generate_additional_professors() -> List[Professor]:
    """Gera professores sintéticos adicionais para expandir o painel (R82).
    
    Cria ~70 novos professores distribuídos uniformemente pelas 11 faculdades,
    com h-indices variados (5-42) e interesses de pesquisa diversificados.
    """
    import random
    rng = random.Random(82)  # semente fixa para reprodutibilidade
    
    # Templates de especialidades e interesses por faculdade
    faculty_profiles = {
        "human_sciences": {
            "nomes": ["Viktor Frankl", "Rollo May", "Carl Rogers", "William James",
                      "Lev Vygotsky", "Jean Piaget", "Mikhail Bakhtin", "Paul Ricoeur",
                      "Hans Gadamer", "Theodor Adorno"],
            "specialties_pool": [
                ["Psicologia Humanista", "Logoterapia", "Sentido da Vida"],
                ["Psicologia Existencial", "Ansiedade", "Criatividade"],
                ["Abordagem Centrada na Pessoa", "Empatia", "Autoatualização"],
                ["Pragmatismo", "Filosofia Americana", "Psicologia Funcional"],
                ["Psicolinguística", "Aquisição da Linguagem", "Cognição"],
                ["Epistemologia Genética", "Desenvolvimento Cognitivo", "Construtivismo"],
                ["Filosofia da Linguagem", "Dialogismo", "Enunciado Concreto"],
                ["Fenomenologia Hermenêutica", "Interpretação", "Narrativa"],
                ["Hermenêutica Filosófica", "Tradição", "Linguagem"],
                ["Teoria Crítica", "Indústria Cultural", "Estética"],
            ],
            "interests_pool": [
                ["sentido", "sofrimento", "liberdade", "responsabilidade"],
                ["existência", "angústia", "autenticidade", "criação"],
                ["self", "atualização", "aceitação", "crescimento"],
                ["experiência", "consciência", "fluxo", "hábito"],
                ["pensamento", "palavra", "sentido", "desenvolvimento"],
                ["esquema", "assimilação", "acomodação", "equilibração"],
                ["enunciado", "dialogismo", "gênero", "polifonia"],
                ["interpretação", "texto", "círculo hermenêutico", "compreensão"],
                ["fusão de horizontes", "tradição", "linguagem", "ser"],
                ["indústria cultural", "esclarecimento", "mimese", "arte"],
            ],
        },
        "social_sciences": {
            "nomes": ["Max Weber Jr.", "Émile Durkheim", "Karl Polanyi", "Celso Furtado",
                      "Raymond Williams", "Stuart Hall", "Pierre Bourdieu", "Anthony Giddens",
                      "Ulrich Beck", "Manuel Castells"],
            "specialties_pool": [
                ["Sociologia da Religião", "Ação Social", "Burocracia"],
                ["Sociologia do Fato Social", "Solidariedade", "Anomia"],
                ["Economia Substantiva", "Mercados", "Instituições"],
                ["Economia do Desenvolvimento", "Subdesenvolvimento", "Dependência"],
                ["Estudos Culturais", "Cultura Material", "Hegemonia"],
                ["Teoria Pós-Colonial", "Identidade Cultural", "Diáspora"],
                ["Sociologia da Cultura", "Distinção Social", "Capital Cultural"],
                ["Teoria da Estruturação", "Modernidade", "Estado-nação"],
                ["Sociedade de Risco", "Modernização Reflexiva", "Cosmopolitismo"],
                ["Sociedade em Rede", "Comunicação Digital", "Movimentos Sociais"],
            ],
            "interests_pool": [
                ["ação social", "tipo ideal", "racionalização", "desencantamento"],
                ["fato social", "coesão", "consciência coletiva", "representação"],
                ["mercado", "redistribuição", "reciprocidade", "instituição"],
                ["desenvolvimento", "dependência", "centro-periferia", "subdesenvolvimento"],
                ["cultura", "hegemonia", "tradição", "resistência"],
                ["identidade", "diferença", "representação", "hibridismo"],
                ["campo", "habitus", "capital cultural", "distinção"],
                ["estruturação", "modernidade", "reflexividade", "globalização"],
                ["risco", "incerteza", "individualização", "cosmopolitismo"],
                ["rede", "informação", "espaço de fluxos", "movimento social"],
            ],
        },
        "engineering": {
            "nomes": ["Vannevar Bush", "Doug Engelbart", "JCR Licklider", "Tim Berners-Lee",
                      "Ada Lovelace", "Charles Babbage", "John von Neumann", "Claude Shannon",
                      "Norbert Wiener", "Marvin Minsky"],
            "specialties_pool": [
                ["Sistemas de Informação", "Memex", "Hipertexto"],
                ["Interação Humano-Computador", "Augmentação", "Interface"],
                ["Rede Intergaláctica", "Computação Ubíqua", "Sistemas em Rede"],
                ["Web Semântica", "Protocolos Web", "Sistemas Abertos"],
                ["Primeira Programadora", "Máquina Analítica", "Algoritmos"],
                ["Computação Mecânica", "Máquina Diferencial", "Autômatos"],
                ["Arquitetura de Computadores", "Bit", "Lógica Binária"],
                ["Teoria da Informação", "Entropia", "Código", "Canal"],
                ["Cibernética", "Feedback", "Controle", "Homeostase"],
                ["Inteligência Artificial", "Redes Neurais", "Cognição"],
            ],
            "interests_pool": [
                ["hipertexto", "associação", "informação", "conhecimento"],
                ["augmentação", "interface", "simbiose", "ferramenta cognitiva"],
                ["rede", "computação ubíqua", "colaboração", "conectividade"],
                ["web", "dado aberto", "interoperabilidade", "protocolo"],
                ["algoritmo", "máquina", "computação", "lógica"],
                ["mecanismo", "autômato", "engrenagem", "cálculo"],
                ["bit", "binário", "memória", "processador"],
                ["entropia", "informação", "redundância", "código"],
                ["feedback", "cibernética", "controle", "comunicação"],
                ["inteligência", "aprendizagem", "rede neural", "mente"],
            ],
        },
        "quantum": {
            "nomes": ["David Deutsch", "John Bell", "John Wheeler", "Rolf Landauer",
                      "Peter Shor", "Charles Bennett", "Artur Ekert", "David DiVincenzo",
                      "Seth Lloyd", "Michel Devoret"],
            "specialties_pool": [
                ["Universo Quântico", "Muitos Mundos", "Computação Universal"],
                ["Teorema de Bell", "Não-localidade", "Variáveis Ocultas"],
                ["Geometrodinâmica", "Informação Quântica", "Realidade"],
                ["Termodinâmica Quântica", "Princípio de Landauer", "Apagamento"],
                ["Algoritmos Quânticos", "Fatoração", "Criptografia Pós-Quantum"],
                ["Criptografia Quântica", "Teleporte", "Purificação"],
                ["Criptografia Quântica", "BB84", "E91", "QKD"],
                ["Critérios de DiVincenzo", "Hardware Quântico", "Escalabilidade"],
                ["Computador Quântico", "Simulação", "Sistemas Complexos"],
                ["Circuitos Supercondutores", "Qubits", "Ressonância"],
            ],
            "interests_pool": [
                ["multiverso", "universo quântico", "realidade", "computação"],
                ["não-localidade", "entrelaçamento", "medida", "realismo"],
                ["informação quântica", "realidade", "observador", "participação"],
                ["energia", "informação", "termodinâmica", "apagamento"],
                ["algoritmo quântico", "fatoração", "criptografia", "Shor"],
                ["teleporte", "teletransporte", "entrelaçamento", "qbit"],
                ["QKD", "criptografia", "BB84", "E91", "segurança"],
                ["escalabilidade", "decoerência", "correção", "tolerância a falhas"],
                ["simulação quântica", "sistema complexo", "química"],
                ["circuito supercondutor", "qubit", "Josephson", "medição"],
            ],
        },
        "health_sciences": {
            "nomes": ["Carl Sagan", "Gregory Bateson", "Oliver Sacks", "John Eccles",
                      "Candace Pert", "Bruce Lipton", "Deepak Chopra", "Fritjof Capra",
                      "Larry Dossey", "Mae-Wan Ho"],
            "specialties_pool": [
                ["Medicina Psicossomática", "Placebo", "Mente-Corpo"],
                ["Medicina Integrativa", "Sistemas Vivos", "Padrões"],
                ["Neurologia", "Neuropsicologia", "Caso Clínico"],
                ["Neurofisiologia", "Sinapse", "Consciência"],
                ["Psiconeuroimunologia", "Neuropeptídeos", "Emoção"],
                ["Epigenética", "Crença", "Ambiente Celular"],
                ["Medicina Mente-Corpo", "Consciência", "Cura"],
                ["Sistemas Vivos", "Complexidade", "Saúde Integral"],
                ["Medicina Quântica", "Não-localidade", "Intenção"],
                ["Bioeletromagnetismo", "Organismo Vivo", "Energia Vital"],
            ],
            "interests_pool": [
                ["psicossomática", "placebo", "mente-corpo", "cura"],
                ["padrão", "sistema vivo", "saúde integrativa", "complexidade"],
                ["neurologia", "neuropsicologia", "narrativa", "cérebro"],
                ["sinapse", "neurotransmissor", "cérebro", "consciência"],
                ["emoção", "peptídeo", "sistema imunológico", "neurociência"],
                ["epigenética", "ambiente", "crença", "expressão gênica"],
                ["cura", "consciência", "mente", "intenção"],
                ["sistema vivo", "complexidade", "saúde", "rede"],
                ["não-localidade", "quântico", "intenção", "cura"],
                ["bioeletromagnetismo", "campo", "energia", "organismo"],
            ],
        },
    }
    
    # Grupos com menos professores originalmente
    # Mapear areas para faculties existentes: artistic->literary_linguistic,
    # juridical->social_sciences, biological->exact_sciences
    extra_faculty_templates = {
        "exact_sciences": {
            "nomes_prefix": ["Davide", "Sophia", "Alexandre", "Carolina", "Victor"],
            "specialties_extra": [
                ["Topologia", "Geometria Diferencial", "Teoria de Categorias"],
                ["Álgebra Abstrata", "Matemática Discreta", "Combinatória"],
                ["Física Quântica", "Teoria de Campos", "Partículas Elementares"],
                ["Biofísica Molecular", "Mecânica Estatística", "Fenômenos Críticos"],
                ["Matemática Aplicada", "Análise Numérica", "Otimização"],
            ],
            "interests_extra": [
                ["espaço", "forma", "transformação", "invariante"],
                ["grupo", "anel", "corpo", "simetria", "estrutura"],
                ["campo", "partícula", "interação", "feynman"],
                ["proteína", "dobramento", "termodinâmica", "transição"],
                ["algoritmo numérico", "convergência", "estabilidade", "otimização"],
            ],
            "sobrenomes": ["Grossmann", "Kovalevskaya", "Grothendieck", "Hypatia", "Bers"],
        },
        "statistics_ds": {
            "nomes_prefix": ["Francis", "Alicia", "Karl", "Rebecca", "Shakir"],
            "specialties_extra": [
                ["Aprendizagem por Reforço", "Sistemas de Recomendação", "Bandits"],
                ["Processamento de Linguagem Natural", "Transformers", "Word Embeddings"],
                ["Geração Aumentada por Busca", "RAG", "Knowledge Graphs"],
                ["Séries Temporais", "Previsão", "Detecção de Anomalias"],
                ["Inferência Causal", "Experimentos Naturais", "Contrafactuais"],
            ],
            "interests_extra": [
                ["policy gradient", "Q-learning", "exploração", "recompensa"],
                ["PLN", "BERT", "GPT", "token", "atenção"],
                ["recuperação", "geração", "conhecimento", "fonte"],
                ["sazonalidade", "tendência", "previsão", "decomposição"],
                ["causalidade", "confundidor", "tratamento", "contrafatual"],
            ],
            "sobrenomes": ["Galton", "Kohatsu", "Pearson", "Loukina", "Mohamed"],
        },
        "programming": {
            "nomes_prefix": ["Martin", "Yukihiro", "Guido", "Brendan", "Anders"],
            "specialties_extra": [
                ["Programação Orientada a Objetos", "Design Patterns", "Arquitetura"],
                ["Ruby on Rails", "Metaprogramação", "DSL"],
                ["Python", "Scripting", "Automação", "Bibliotecas"],
                ["JavaScript", "Node.js", "Frontend", "EcmaScript"],
                ["C#", ".NET", "Tipos Genéricos", "Assíncrono"],
            ],
            "interests_extra": [
                ["objeto", "classe", "padrão", "herança", "composição"],
                ["DSL", "convenção sobre configuração", "metaprogramação"],
                ["python", "pip", "virtualenv", "biblioteca", "ecossistema"],
                ["javascript", "event loop", "promise", "callback", "ES6"],
                ["tipo genérico", "LINQ", "async", ".NET", "C#"],
            ],
            "sobrenomes": ["Fowler", "Matsumoto", "van Rossum", "Eich", "Hejlsberg"],
        },
        "historical": {
            "nomes_prefix": ["Johan", "Lynn", "Reinhart", "Natalie", "Geoffrey"],
            "specialties_extra": [
                ["História Global", "História Conectada", "História Comparada"],
                ["História das Mulheres", "Gênero", "Feminismo"],
                ["História dos Conceitos", "História Intelectual", "Linguagem Política"],
                ["História da Ciência", "Revolução Científica", "Saberes"],
                ["História Econômica", "Capitalismo", "Trabalho", "Mercado"],
            ],
            "interests_extra": [
                ["global", "conexão", "comparação", "circulação"],
                ["gênero", "mulher", "feminismo", "emancipação"],
                ["conceito", "linguagem política", "temporalidade", "modernidade"],
                ["ciência", "revolução científica", "conhecimento", "experimento"],
                ["capitalismo", "trabalho", "mercado", "classe"],
            ],
            "sobrenomes": ["Huizinga", "Hunt", "Koselleck", "Davis", "Elton"],
        },
        "literary_linguistic": {
            "nomes_prefix": ["Roland", "Jacques", "Walter", "Umberto", "Mikhail"],
            "specialties_extra": [
                ["Semiótica Narrativa", "Estrutura do Conto", "Mitocrítica"],
                ["Filosofia da Linguagem", "Atos de Fala", "Pragmática"],
                ["Poética", "Versificação", "Métrica", "Estilística"],
                ["Tradução", "Transcriação", "Estudos da Tradução"],
                ["Teoria do Romance", "Polifonia", "Dialogismo"],
            ],
            "interests_extra": [
                ["narrativa", "mito", "conto", "estrutura profunda"],
                ["ato de fala", "intenção", "contexto", "perlocução"],
                ["poesia", "verso", "ritmo", "metáfora"],
                ["tradução", "transcriação", "diferença", "equivalência"],
                ["romance", "polifonia", "cronotopo", "dialogismo"],
            ],
            "sobrenomes": ["Barthes", "Derrida", "Benjamin", "Eco", "Bakhtin"],
        },
        # Faculdades adicionais mapeadas para IDs existentes
        "literary_linguistic_art": {  # arte -> literary_linguistic
            "faculty_id": "literary_linguistic",
            "nomes_prefix": ["Aby", "Ernst", "Clement", "Susan", "Marshall"],
            "specialties_extra": [
                ["Teoria da Arte", "Estética", "Filosofia da Arte"],
                ["História da Arte", "Iconografia", "Iconologia"],
                ["Crítica de Arte", "Modernismo", "Vanguarda"],
                ["Performance", "Arte Contemporânea", "Arte Conceitual"],
                ["Curadoria", "Museologia", "Patrimônio"],
            ],
            "interests_extra": [
                ["beleza", "estética", "representação", "mímese"],
                ["imagem", "símbolo", "ícone", "alegoria"],
                ["modernismo", "vanguarda", "originalidade", "ruptura"],
                ["performance", "corpo", "conceito", "instalação"],
                ["curadoria", "museu", "preservação", "exposição"],
            ],
            "sobrenomes": ["Warburg", "Gombrich", "Greenberg", "Sontag", "McLuhan"],
        },
        "social_sciences_jur": {  # direito -> social_sciences
            "faculty_id": "social_sciences",
            "nomes_prefix": ["Hans", "Norberto", "Ronald", "Hebe", "Michel"],
            "specialties_extra": [
                ["Teoria do Direito", "Norma Jurídica", "Sistema Jurídico"],
                ["Teoria da Constituição", "Direitos Fundamentais", "Controle"],
                ["Jurisprudência", "Decisão Judicial", "Argumentação"],
                ["Direito Penal", "Criminologia", "Penalogia"],
                ["Direito Público", "Processo Administrativo", "Acesso à Justiça"],
            ],
            "interests_extra": [
                ["norma", "validade", "eficácia", "Kelsen"],
                ["constituição", "fundamental", "garantia", "controle"],
                ["decisão", "discurso", "motivação", "persuasão"],
                ["pena", "crime", "criminologia", "direito penal"],
                ["administração", "processo", "serviço público", "cidadania"],
            ],
            "sobrenomes": ["Kelsen", "Bobbio", "Dworkin", "Vivacqua", "Foucault"],
        },
        "exact_sciences_bio": {  # biologia -> exact_sciences
            "faculty_id": "exact_sciences",
            "nomes_prefix": ["Charles", "Lynn", "Mendel", "Rosalind", "David"],
            "specialties_extra": [
                ["Biologia Evolutiva", "Seleção Natural", "Especiação"],
                ["Ecologia", "Bioma", "Conservação", "Sustentabilidade"],
                ["Biologia Molecular", "Genética", "Expressão Gênica"],
                ["Genética de Populações", "Evolução Molecular", "Fliogenia"],
                ["Sistemas Complexos", "Auto-organização", "Vida Artificial"],
            ],
            "interests_extra": [
                ["evolução", "seleção", "adaptação", "espécie"],
                ["ecossistema", "bioma", "conservação", "sustentabilidade"],
                ["DNA", "RNA", "proteína", "genoma", "expressão"],
                ["população", "gene", "deriva", "migração", "seleção"],
                ["auto-organização", "emergência", "sistema complexo", "vida"],
            ],
            "sobrenomes": ["Darwin", "Margulis", "Weismann", "Franklin", "Deutsch"],
        },
    }
    
    additional_professors = []
    next_id = 100
    
    # 1) Faculdades com templates detalhados
    for fid, profiles in faculty_profiles.items():
        nomes = profiles["nomes"]
        specs = profiles["specialties_pool"]
        interests = profiles["interests_pool"]
        
        for i, nome in enumerate(nomes):
            sp = specs[i % len(specs)]
            inter = interests[i % len(interests)]
            h = rng.randint(6, 42)
            pubs_local = h * 2 + rng.randint(0, 15)
            
            prof = Professor(
                professor_id=f"prof_syn_{next_id}",
                nome=nome,
                title=rng.choice(["PhD", "PhD", "PhD", "Livre-Docente", "Titular"]),
                faculty_id=fid,
                specialties=sp,
                research_interests=inter,
                publications=pubs_local,
                h_index=h,
            )
            additional_professors.append(prof)
            next_id += 1
    
    # 2) Faculdades com templates extra
    for key, extra in extra_faculty_templates.items():
        fid = extra.get("faculty_id", key)  # usar faculty_id explicito se disponível
        prefixos = extra["nomes_prefix"]
        specs = extra["specialties_extra"]
        interests = extra["interests_extra"]
        sobrenomes = extra["sobrenomes"]
        
        for i in range(len(prefixos)):
            nome = f"{prefixos[i]} {sobrenomes[i]}"
            sp = specs[i % len(specs)]
            inter = interests[i % len(interests)]
            h = rng.randint(5, 38)
            pubs_local = h * 2 + rng.randint(0, 10)
            
            prof = Professor(
                professor_id=f"prof_syn_{next_id}",
                nome=nome,
                title=rng.choice(["PhD", "PhD", "PhD", "Livre-Docente"]),
                faculty_id=fid,
                specialties=sp,
                research_interests=inter,
                publications=pubs_local,
                h_index=h,
            )
            additional_professors.append(prof)
            next_id += 1
    
    # 3) Validar distribuição
    from collections import Counter
    fac_counts = Counter(p.faculty_id for p in additional_professors)
    
    return additional_professors


def get_professors_by_faculty(faculty_id: str) -> List[Professor]:
    """Retorna todos os professores de uma faculdade."""
    if not PROFESSOR_REGISTRY:
        create_all_professors()
    return [p for p in PROFESSOR_REGISTRY if p.faculty_id == faculty_id]
