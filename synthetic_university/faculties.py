"""10 Faculdades da Universidade Sintética Transversal.

Cada faculdade contém: domínio, subdisciplinas, conceitos fundamentais,
métodos de pesquisa, tradições epistemológicas e ferramentas-chave.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Faculdade:
    """Uma faculdade/unidade acadêmica na universidade sintética."""
    id: str
    nome: str
    nome_en: str
    descricao: str
    subdisciplinas: List[str] = field(default_factory=list)
    conceitos: List[str] = field(default_factory=list)
    metodos_pesquisa: List[str] = field(default_factory=list)
    tradicoes_epistemologicas: List[str] = field(default_factory=list)
    ferramentas: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Ensure conceitos are deduplicated and lowercased
        seen = set()
        deduped = []
        for c in self.conceitos:
            key = c.lower().strip()
            if key not in seen:
                seen.add(key)
                deduped.append(c.strip())
        self.conceitos = deduped

    def __len__(self) -> int:
        return len(self.conceitos)

    def __repr__(self) -> str:
        return f"<Faculdade {self.id}: {self.nome} ({len(self.conceitos)} conceitos)>"


# =============================================================================
# 1. CIÊNCIAS HUMANAS (Human Sciences)
# =============================================================================
HUMAN_SCIENCES = Faculdade(
    id="human_sciences",
    nome="Ciências Humanas",
    nome_en="Human Sciences",
    descricao="Filosofia, psicologia, sociologia, antropologia e educação — "
               "o estudo da condição humana em suas dimensões subjetiva, social e cultural.",
    subdisciplinas=[
        "Filosofia", "Psicologia", "Sociologia", "Antropologia",
        "Educação", "Teologia", "Ética", "Estética", "Fenomenologia",
        "Psicanálise", "Teoria Crítica", "Hermenêutica",
    ],
    conceitos=[
        "consciência", "ser", "existência", "liberdade", "ética", "moral",
        "justiça", "verdade", "conhecimento", "crença", "dúvida", "certeza",
        "sujeito", "objeto", "fenômeno", "noumeno", "transcendental",
        "dialética", "alteridade", "reconhecimento", "poder", "discurso",
        "estrutura", "agência", "habitus", "campo", "capital simbólico",
        "inconsciente", "recalque", "transferência", "sintoma", "desejo",
        "identidade", "diferença", "gênero", "raça", "classe", "ideologia",
        "hegemonia", "biopolítica", "governamentalidade", "disciplina",
        "normalização", "resistência", "emancipação", "autonomia",
        "intersubjetividade", "intencionalidade", "corpo", "afeto",
        "emoção", "razão", "intuição", "imaginação", "memória",
        "percepção", "linguagem", "símbolo", "mito", "rito",
        "sagrado", "profano", "experiência", "sentido", "valor",
        "norma", "lei", "contrato social", "vontade geral",
        "reificação", "alienação", "fetiche", "mais-valia",
        "indivíduo", "comunidade", "sociedade civil", "estado",
        "espaço público", "esfera pública", "opinião pública",
        "civilização", "cultura", "natureza", "técnica", "humanismo",
        "pós-humanismo", "transumanismo", "animalidade",
        "vulnerabilidade", "cuidado", "responsabilidade","dignidade",
    ],
    metodos_pesquisa=[
        "Análise conceitual", "Fenomenologia descritiva", "Hermenêutica",
        "Dialética", "Genealogia", "Arqueologia do saber",
        "Etnografia", "Observação participante", "Entrevista profunda",
        "Estudo de caso qualitativo", "Análise do discurso",
        "Psicanálise clínica", "Experimentação psicológica",
        "Pesquisa-ação", "Teoria fundamentada",
    ],
    tradicoes_epistemologicas=[
        "Racionalismo", "Empirismo", "Idealismo alemão",
        "Fenomenologia", "Existencialismo", "Estruturalismo",
        "Pós-estruturalismo", "Teoria Crítica", "Pragmatismo",
        "Filosofia Analítica", "Hermenêutica", "Pós-modernismo",
    ],
    ferramentas=[
        "NVivo", "ATLAS.ti", "MAXQDA", "SPSS", "R (análise qualitativa)",
        "Análise de conteúdo", "Análise temática", "Análise narrativa",
    ],
)

# =============================================================================
# 2. CIÊNCIAS SOCIAIS (Social Sciences)
# =============================================================================
SOCIAL_SCIENCES = Faculdade(
    id="social_sciences",
    nome="Ciências Sociais Aplicadas",
    nome_en="Social Sciences",
    descricao="Economia, política, direito, comunicação e relações internacionais — "
               "o estudo das estruturas, processos e instituições que organizam a vida coletiva.",
    subdisciplinas=[
        "Economia", "Ciência Política", "Direito", "Comunicação Social",
        "Relações Internacionais", "Administração", "Contabilidade",
        "Serviço Social", "Demografia", "Urbanismo",
    ],
    conceitos=[
        "mercado", "oferta", "demanda", "preço", "valor", "moeda", "crédito",
        "inflação", "juros", "câmbio", "PIB", "desenvolvimento", "crescimento",
        "capitalismo", "socialismo", "neoliberalismo", "keynesianismo",
        "estado", "governo", "soberania", "democracia", "república",
        "cidadania", "direitos humanos", "direitos fundamentais",
        "constituição", "lei", "norma jurídica", "jurisprudência",
        "devido processo legal", "ampla defesa", "contraditório",
        "propriedade", "contrato", "responsabilidade civil",
        "opinião pública", "mídia", "esfera pública", "agenda-setting",
        "enquadramento", "propaganda", "persuasão", "espiral do silêncio",
        "poder", "autoridade", "legitimidade", "representação",
        "participação", "movimentos sociais", "sociedade civil organizada",
        "globalização", "multilateralismo", "supranacionalidade",
        "diplomacia", "conflito", "cooperação", "integração regional",
        "bloco econômico", "comércio internacional", "protecionismo",
        "livre comércio", "vantagem comparativa", "cadeias globais de valor",
        "desigualdade", "pobreza", "exclusão social", "mobilidade social",
        "políticas públicas", "bem-estar social", "estado de direito",
        "accountability", "transparência", "governança", "corrupção",
        "desenvolvimento sustentável", "ESG", "externalidades",
        "bens públicos", "recursos comuns", "tragédia dos comuns",
    ],
    metodos_pesquisa=[
        "Econometria", "Séries temporais", "Dados em painel",
        "Experimentos aleatorizados", "Quase-experimentos",
        "Diferenças-em-diferenças", "Variável instrumental",
        "Regressão descontínua", "Pesquisa eleitoral", "Survey",
        "Análise de redes sociais", "Análise de conteúdo",
        "Jurimetria", "Análise documental", "Estudo comparativo",
    ],
    tradicoes_epistemologicas=[
        "Positivismo", "Behaviorismo", "Institucionalismo",
        "Escolha Racional", "Marxismo", "Estruturalismo",
        "Pós-positivismo", "Construtivismo social",
        "Teoria Crítica", "Feminismo", "Pós-colonialismo",
        "Economia Comportamental", "Teoria dos Jogos",
    ],
    ferramentas=[
        "Stata", "R", "Python (pandas, statsmodels)", "SPSS",
        "EViews", "Gretl", "QGIS", "Gephi", "NodeXL",
        "LaTeX", "Zotero", "Mendeley",
    ],
)

# =============================================================================
# 3. ENGENHARIA (Engineering)
# =============================================================================
ENGINEERING = Faculdade(
    id="engineering",
    nome="Engenharia",
    nome_en="Engineering",
    descricao="Engenharia de software, sistemas, elétrica, mecânica e computação — "
               "a arte e ciência de projetar, construir e otimizar sistemas tecnológicos.",
    subdisciplinas=[
        "Engenharia de Software", "Engenharia de Sistemas", "Engenharia Elétrica",
        "Engenharia Mecânica", "Engenharia de Computação", "Engenharia Civil",
        "Engenharia de Produção", "Engenharia Química", "Engenharia Aeroespacial",
        "Engenharia Biomédica", "Engenharia Ambiental", "Engenharia de Materiais",
    ],
    conceitos=[
        "sistema", "arquitetura", "componente", "módulo", "interface",
        "requisito", "especificação", "design", "implementação",
        "teste", "validação", "verificação", "manutenção",
        "refatoração", "padrão de projeto", "anti-pattern",
        "acoplamento", "coesão", "encapsulamento", "abstração",
        "herança", "polimorfismo", "composição", "delegação",
        "concorrência", "paralelismo", "assincronia", "distribuição",
        "tolerância a falhas", "resiliência", "disponibilidade",
        "escalabilidade", "desempenho", "latência", "throughput",
        "segurança", "privacidade", "autenticação", "autorização",
        "criptografia", "protocolo", "API", "middleware",
        "container", "orquestração", "microserviço", "monolito",
        "DevOps", "CI/CD", "infraestrutura como código",
        "observabilidade", "monitoramento", "logging", "métrica",
        "alerta", "SLA", "SLO", "SLI", "confiabilidade",
        "malha", "grade", "nuvem", "edge computing", "IoT",
        "sistema embarcado", "tempo real", "sistema crítico",
        "modelagem", "simulação", "protótipo", "MVP",
        "qualidade", "métrica de software", "dívida técnica",
        "processo", "metodologia ágil", "Scrum", "Kanban",
        "lean", "seis sigma", "TQM", "PDCA", "melhoria contínua",
    ],
    metodos_pesquisa=[
        "Engenharia experimental", "A/B testing", "Testes de hipótese",
        "Análise de falhas", "Análise de modos de falha (FMEA)",
        "Análise de causa raiz", "Design of Experiments (DoE)",
        "Análise de sensibilidade", "Simulação Monte Carlo",
        "Modelagem matemática", "Otimização", "Teoria das filas",
    ],
    tradicoes_epistemologicas=[
        "Positivismo engenharia", "Pragmatismo tecnológico",
        "Racionalismo aplicado", "Empirismo experimental",
        "Construtivismo sociotécnico", "Design Thinking",
        "Systems Thinking", "Cibernética", "Teoria Geral de Sistemas",
    ],
    ferramentas=[
        "Python", "Go", "Rust", "Java", "C++", "TypeScript",
        "Docker", "Kubernetes", "Terraform", "Ansible",
        "Jenkins", "GitHub Actions", "GitLab CI", "ArgoCD",
        "Prometheus", "Grafana", "ELK Stack", "Datadog",
        "VS Code", "JetBrains", "Vim", "Git", "Linux",
    ],
)

# =============================================================================
# 4. LETRAS & LINGUÍSTICA (Literary & Linguistic)
# =============================================================================
LITERARY_LINGUISTIC = Faculdade(
    id="literary_linguistic",
    nome="Letras e Linguística",
    nome_en="Literary and Linguistic Studies",
    descricao="Literatura, linguística, filologia, semiótica e tradução — "
               "o estudo da linguagem humana em suas dimensões estética, estrutural, histórica e cognitiva.",
    subdisciplinas=[
        "Literatura", "Linguística", "Filologia", "Semiótica",
        "Tradução", "Letras Clássicas", "Letras Modernas",
        "Teoria Literária", "Literatura Comparada", "Poética",
        "Retórica", "Estilística", "Fonética", "Fonologia",
        "Morfologia", "Sintaxe", "Semântica", "Pragmática",
        "Sociolinguística", "Psicolinguística", "Neurolinguística",
        "Linguística Computacional", "Análise do Discurso",
    ],
    conceitos=[
        "signo", "significante", "significado", "referente",
        "símbolo", "ícone", "índice", "código", "mensagem",
        "canal", "emissor", "receptor", "ruído", "redundância",
        "entropia", "informação", "língua", "fala", "linguagem",
        "discurso", "texto", "contexto", "intertextualidade",
        "metáfora", "metonímia", "sinédoque", "ironia", "paradoxo",
        "narrativa", "enredo", "personagem", "narrador", "foco narrativo",
        "tempo", "espaço", "trama", "conflito", "clímax", "desfecho",
        "gênero literário", "épico", "lírico", "dramático", "romance",
        "conto", "poesia", "ensaio", "crônica", "epopeia", "tragédia",
        "comédia", "sátira", "utopia", "distopia", "realismo",
        "modernismo", "pós-modernismo", "barroco", "romantismo",
        "classicismo", "naturalismo", "simbolismo", "vanguardas",
        "morfema", "fonema", "alofone", "alomorfe", "léxico",
        "sintagma", "paradigma", "sincronia", "diacronia",
        "competência", "desempenho", "gramática universal",
        "ato de fala", "implicatura", "pressuposição", "inferência",
        "polissemia", "homonímia", "sinonímia", "antonímia", "hiperonímia",
        "coerência", "coesão", "progressão referencial", "tema", "rema",
        "tradução", "transcriação", "equivalência", "fidelidade", "estrangeirização",
        "domesticação", "intraduzibilidade", "retextualização",
    ],
    metodos_pesquisa=[
        "Análise literária", "Close reading", "Crítica textual",
        "Análise do discurso", "Análise de conteúdo", "Análise narrativa",
        "Estudo filológico", "Análise contrastiva", "Estudo de corpus",
        "Etnografia da fala", "Experimentos psicolinguísticos",
        "Análise fonética acústica", "Análise de erros",
        "Pesquisa-ação em linguística aplicada",
    ],
    tradicoes_epistemologicas=[
        "Estruturalismo", "Gerativismo", "Funcionalismo",
        "Formalismo Russo", "New Criticism", "Estética da Recepção",
        "Pós-estruturalismo", "Desconstrução", "Teoria do Discurso",
        "Linguística Cognitiva", "Análise Dialógica do Discurso",
        "Semiótica Peirceana", "Semiótica Greimasiana",
    ],
    ferramentas=[
        "Praat", "ELAN", "AntConc", "Sketch Engine", "CorpusLoader",
        "NLTK", "spaCy", "Stanza", "Python", "R",
        "Zotero", "LaTeX", "TEI XML", "Voyant Tools",
    ],
)

# =============================================================================
# 5. HISTÓRIA (Historical Studies)
# =============================================================================
HISTORICAL = Faculdade(
    id="historical",
    nome="História",
    nome_en="Historical Studies",
    descricao="História, arqueologia, historiografia e patrimônio — "
               "o estudo do tempo humano, das civilizações e da memória coletiva.",
    subdisciplinas=[
        "História Antiga", "História Medieval", "História Moderna",
        "História Contemporânea", "História do Brasil", "História da América",
        "História da África", "História da Ásia", "História Global",
        "Arqueologia", "Pré-história", "Historiografia",
        "História Cultural", "História Social", "História Econômica",
        "História Política", "História das Ideias", "História Intelectual",
        "História Digital", "História Pública", "Arquivologia",
        "Museologia", "História Oral", "Patrimônio Cultural",
    ],
    conceitos=[
        "tempo", "temporalidade", "periodização", "cronologia",
        "história", "memória", "esquecimento", "arquivo", "documento",
        "fonte histórica", "evidência", "testemunho", "rastro",
        "narrativa histórica", "interpretação", "explicação histórica",
        "causa", "consequência", "contingência", "necessidade",
        "progresso", "decadência", "ciclo", "ruptura", "continuidade",
        "evento", "estrutura", "conjuntura", "longa duração",
        "civilização", "império", "nação", "estado-nação", "nacionalismo",
        "colonialismo", "imperialismo", "pós-colonialismo", "descolonização",
        "revolução", "reforma", "rebelião", "guerra", "paz",
        "escravidão", "servidão", "trabalho", "classe", "casta",
        "gênero", "família", "parentesco", "geração", "infância",
        "cultura material", "cultura imaterial", "patrimônio",
        "arqueologia", "estratigrafia", "sítio arqueológico", "artefato",
        "pré-história", "paleolítico", "neolítico", "idade dos metais",
        "antiguidade", "medievo", "modernidade", "contemporaneidade",
        "renascimento", "iluminismo", "romantismo", "positivismo",
        "historicismo", "presentismo", "anacronismo",
        "micro-história", "história vista de baixo", "história das mentalidades",
        "história dos conceitos", "história do tempo presente",
        "patrimônio cultural", "preservação", "conservação", "restauração",
        "história digital", "big data histórico", "humanidades digitais",
    ],
    metodos_pesquisa=[
        "Análise documental", "Crítica de fontes", "Método histórico",
        "História comparada", "Análise serial", "Prosopografia",
        "História oral", "História de vida", "Análise de redes históricas",
        "Arqueologia experimental", "Análise estratigráfica",
        "Datação por carbono-14", "Paleografia", "Diplomática",
        "Análise quantitativa histórica", "Modelagem histórica",
    ],
    tradicoes_epistemologicas=[
        "Historicismo alemão", "Positivismo histórico", "Escola dos Annales",
        "Marxismo histórico", "Micro-história italiana", "História Cultural",
        "História Global", "Pós-modernismo histórico", "História Digital",
        "História Ambiental", "História Transnacional",
    ],
    ferramentas=[
        "NVivo", "ATLAS.ti", "Zotero", "Tropy", "Omeka",
        "Python (pandas, matplotlib)", "Gephi", "Palladio",
        "QGIS", "ArcGIS", "Tableau", "Git", "Markdown",
        "TEI XML", "JSON", "LaTeX", "Scrivener",
    ],
)

# =============================================================================
# 6. QUÂNTICA (Quantum Studies)
# =============================================================================
QUANTUM = Faculdade(
    id="quantum",
    nome="Ciências Quânticas",
    nome_en="Quantum Sciences",
    descricao="Computação quântica, informação quântica, tecnologias quânticas — "
               "o estudo e aplicação da mecânica quântica para computação, comunicação e simulação.",
    subdisciplinas=[
        "Computação Quântica", "Informação Quântica", "Criptografia Quântica",
        "Simulação Quântica", "Sensoriamento Quântico", "Comunicação Quântica",
        "Emaranhamento Quântico", "Correção de Erros Quânticos",
        "Algoritmos Quânticos", "Machine Learning Quântico",
        "Óptica Quântica", "Matéria Condensada Quântica",
        "Termodinâmica Quântica", "Teoria Quântica de Campos",
    ],
    conceitos=[
        "qubit", "superposição", "emaranhamento", "interferência quântica",
        "decoerência", "medida quântica", "colapso da função de onda",
        "operador", "hamiltoniano", "evolução unitária", "porta quântica",
        "circuito quântico", "algoritmo quântico", "transformada de Fourier quântica",
        "busca de Grover", "fatoração de Shor", "simulação quântica",
        "teletransporte quântico", "criptografia quântica", "BB84", "E91",
        "distribuição quântica de chaves", "QKD", "entropia de von Neumann",
        "informação mútua quântica", "fidelidade quântica", "traço parcial",
        "estado de Bell", "estado GHZ", "estado W", "cluster state",
        "código corretor quântico", "código de Shor", "código de superfície",
        "código estabilizador", "computação quântica topológica",
        "anyons", "computação quântica adiabática", "annealing quântico",
        "QAOA", "VQE", "algoritmo variacional", "QML", "quantum kernel",
        "quantum neural network", "tensor network", "MPS", "PEPS",
        "Qiskit", "Cirq", "PennyLane", "TensorFlow Quantum", "Braket",
        "supremacia quântica", "vantagem quântica", "ruído quântico",
        "NISQ", "computação quântica fault-tolerant",
        "emaranhamento multipartite", "desigualdade de Bell", "CHSH",
        "contextualidade quântica", "teorema de Kochen-Specker",
        "interpretações da mecânica quântica", "Copenhague", "Many Worlds",
        "variáveis ocultas", "Bohm", "QBismo", "de Broglie-Bohm",
    ],
    metodos_pesquisa=[
        "Simulação quântica em computadores clássicos",
        "Execução em hardware quântico real", "Experimentação em óptica quântica",
        "Análise de circuitos quânticos", "Tomografia quântica",
        "Randomized benchmarking", "Process tomography",
        "Quantum state tomography", "Análise de ruído e decoerência",
        "Teste de desigualdades de Bell", "Quantum error correction benchmarking",
    ],
    tradicoes_epistemologicas=[
        "Interpretação de Copenhague", "Interpretação de Many-Worlds",
        "Teoria de de Broglie-Bohm", "QBismo", "Interpretação Relacional",
        "Princípio Antrópico Quântico", "Pós-seleção",
        "Transacionalismo", "Teoria Quântica de Campos",
    ],
    ferramentas=[
        "Qiskit", "Cirq", "PennyLane", "TensorFlow Quantum",
        "Amazon Braket", "QuTiP", "ProjectQ", "Strawberry Fields",
        "Q#", "Python", "Jupyter", "LaTeX", "IBM Quantum Experience",
    ],
)

# =============================================================================
# 7. CIÊNCIAS EXATAS (Exact Sciences)
# =============================================================================
EXACT_SCIENCES = Faculdade(
    id="exact_sciences",
    nome="Ciências Exatas e da Terra",
    nome_en="Exact and Earth Sciences",
    descricao="Matemática, física, química e astronomia — "
               "o estudo das leis fundamentais da natureza e das estruturas abstratas do universo.",
    subdisciplinas=[
        "Matemática Pura", "Matemática Aplicada", "Física Teórica",
        "Física Experimental", "Física de Partículas", "Astrofísica",
        "Cosmologia", "Química Orgânica", "Química Inorgânica",
        "Química Física", "Bioquímica", "Geociências", "Oceanografia",
        "Meteorologia", "Astronomia Observacional", "Astrobiologia",
    ],
    conceitos=[
        "número", "conjunto", "função", "limite", "derivada", "integral",
        "equação", "variável", "constante", "parâmetro", "espaço vetorial",
        "matriz", "transformação linear", "autovalor", "autovetor",
        "grupo", "anel", "corpo", "métrica", "topologia", "variedade",
        "simetria", "invariância", "conservação", "lei física",
        "força", "energia", "momento", "campo", "onda", "partícula",
        "espaço", "tempo", "espaço-tempo", "relatividade", "gravidade",
        "eletromagnetismo", "termodinâmica", "entropia", "flecha do tempo",
        "mecânica quântica", "constante de Planck", "átomo", "elétron",
        "próton", "nêutron", "fóton", "quark", "glúon", "bóson de Higgs",
        "força fundamental", "gravidade", "eletromagnetismo", "força nuclear forte",
        "força nuclear fraca", "modelo padrão", "supersimetria", "cordas",
        "átomo", "molécula", "reação química", "ligação química",
        "elemento", "composto", "mol", "estequiometria", "equilíbrio químico",
        "catálise", "cinética química", "termodinâmica química",
        "estrela", "planeta", "galáxia", "nebulosa", "buraco negro",
        "supernova", "estrela de nêutrons", "big bang", "cosmologia",
        "matéria escura", "energia escura", "radiação cósmica de fundo",
        "exoplaneta", "habitabilidade", "zona habitável",
        "teoria do caos", "sistema dinâmico", "atrator", "bifurcação",
        "fractal", "auto-similaridade", "dimensão fractal", "criticalidade",
    ],
    metodos_pesquisa=[
        "Método científico", "Experimentação controlada", "Modelagem matemática",
        "Simulação computacional", "Análise estatística", "Inferência bayesiana",
        "Análise de erro", "Propagação de incerteza", "Análise dimensional",
        "Teoria de grupos", "Métodos numéricos", "Elementos finitos",
        "Espectroscopia", "Cromatografia", "Microscopia", "Difração de raios-X",
    ],
    tradicoes_epistemologicas=[
        "Realismo científico", "Empirismo lógico", "Racionalismo crítico",
        "Positivismo lógico", "Instrumentalismo", "Platonismo matemático",
        "Intuicionismo", "Formalismo", "Estruturalismo matemático",
        "Falsificacionismo popperiano", "Paradigmas kuhnianos",
    ],
    ferramentas=[
        "Python", "Julia", "MATLAB", "Mathematica", "Maple",
        "COMSOL", "ANSYS", "GROMACS", "Gaussian", "VASP",
        "LaTeX", "Git", "Jupyter", "NumPy", "SciPy", "SymPy",
        "TensorFlow", "PyTorch", "ROOT", "Geant4",
    ],
)

# =============================================================================
# 8. ESTATÍSTICA & DATA SCIENCE (Statistics & Data Science)
# =============================================================================
STATISTICS_DS = Faculdade(
    id="statistics_ds",
    nome="Estatística e Ciência de Dados",
    nome_en="Statistics and Data Science",
    descricao="Estatística, probabilidade, machine learning e ciência de dados — "
               "a ciência de extrair conhecimento, padrões e previsões a partir de dados.",
    subdisciplinas=[
        "Estatística Teórica", "Estatística Aplicada", "Probabilidade",
        "Inferência Estatística", "Machine Learning", "Deep Learning",
        "Mineração de Dados", "Análise de Séries Temporais",
        "Estatística Bayesiana", "Estatística Não-paramétrica",
        "Bioestatística", "Econometria", "Pesquisa Operacional",
        "Otimização", "Teoria da Informação", "Aprendizagem por Reforço",
        "Processamento de Linguagem Natural", "Visão Computacional",
    ],
    conceitos=[
        "probabilidade", "variável aleatória", "distribuição", "esperança",
        "variância", "covariância", "correlação", "independência",
        "teorema central do limite", "lei dos grandes números",
        "inferência", "estimação", "estimador", "viés", "consistência",
        "eficiência", "intervalo de confiança", "teste de hipótese",
        "p-valor", "erro tipo I", "erro tipo II", "poder estatístico",
        "tamanho de efeito", "teste t", "ANOVA", "qui-quadrado",
        "regressão linear", "regressão logística", "GLM",
        "modelo misto", "efeitos aleatórios", "efeitos fixos",
        "bayesiano", "prior", "verossimilhança", "posterior",
        "MCMC", "Gibbs sampling", "Metropolis-Hastings",
        "série temporal", "estacionariedade", "ARIMA", "suavização",
        "machine learning", "aprendizagem supervisionada", "classificação",
        "regressão", "aprendizagem não-supervisionada", "clusterização",
        "dimensionalidade", "PCA", "t-SNE", "UMAP", "autoencoder",
        "árvore de decisão", "random forest", "gradient boosting",
        "XGBoost", "LightGBM", "CatBoost", "SVM", "k-NN",
        "rede neural", "deep learning", "CNN", "RNN", "LSTM", "Transformer",
        "atenção", "self-attention", "BERT", "GPT", "difusão",
        "aprendizagem por reforço", "Q-learning", "policy gradient",
        "DQN", "PPO", "SARSA", "bandit", "exploração vs explotação",
        "overfitting", "underfitting", "regularização", "Lasso", "Ridge",
        "validação cruzada", "bootstrap", "bagging", "boosting",
        "métrica", "acurácia", "precisão", "recall", "F1", "AUC",
        "curva ROC", "matriz de confusão", "curva de aprendizado",
        "entropia", "entropia cruzada", "divergência KL", "mutual information",
        "causalidade", "inferência causal", "Do-calculus", "DAG causal",
        "viés", "fairness", "equidade algorítmica", "explicabilidade",
        "interpretabilidade", "SHAP", "LIME", "feature importance",
    ],
    metodos_pesquisa=[
        "Delineamento experimental", "Pesquisa observacional",
        "Ensaio clínico randomizado", "Estudo de coorte", "Caso-controle",
        "Análise de sobrevivência", "Meta-análise", "Revisão sistemática",
        "Análise de poder", "Análise de sensibilidade", "Bootstrapping",
        "Testes permutacionais", "Análise bayesiana de dados",
        "Modelagem preditiva", "Análise de séries temporais",
    ],
    tradicoes_epistemologicas=[
        "Frequentismo", "Bayesianismo", "Empirismo estatístico",
        "Racionalismo inferencial", "Pragmatismo preditivo",
        "Criticalismo popperiano", "Empiricismo de machine learning",
    ],
    ferramentas=[
        "R", "Python", "Julia", "SAS", "SPSS", "Stata",
        "scikit-learn", "TensorFlow", "PyTorch", "JAX",
        "XGBoost", "LightGBM", "CatBoost", "Statsmodels",
        "Stan", "PyMC", "brms", "lme4", "caret", "tidymodels",
        "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn", "Plotly",
        "D3.js", "Tableau", "Power BI", "Jupyter", "RStudio",
        "MLflow", "DVC", "Weights & Biases", "Neptune",
    ],
)

# =============================================================================
# 9. PROGRAMAÇÃO (Programming & Formal Languages)
# =============================================================================
PROGRAMMING = Faculdade(
    id="programming",
    nome="Programação e Linguagens Formais",
    nome_en="Programming and Formal Languages",
    descricao="Linguagens de programação, compiladores, sistemas formais e paradigmas — "
               "a arte e ciência da expressão computacional em múltiplos paradigmas.",
    subdisciplinas=[
        "Linguagens de Programação", "Compiladores", "Paradigmas de Programação",
        "Programação Funcional", "Programação Orientada a Objetos",
        "Programação Lógica", "Programação Concorrente", "Teoria dos Tipos",
        "Linguagens Formais", "Autômatos", "Computabilidade",
        "Sistemas de Tipos", "Análise de Programas", "Verificação Formal",
        "Metaprogramação", "DSL", "Linguagens Esotéricas",
    ],
    conceitos=[
        "linguagem de programação", "sintaxe", "semântica", "pragmática",
        "gramática formal", "BNF", "EBNF", "AST", "parser",
        "compilador", "interpretador", "transpilador", "JIT", "AOT",
        "tipo", "tipo estático", "tipo dinâmico", "inferência de tipos",
        "tipo dependente", "tipo algébrico", "GADT", "tipo existencial",
        "classe", "objeto", "herança", "composição", "mixim", "trait",
        "interface", "protocolo", "abstração", "encapsulamento",
        "função", "lambda", "closure", "currying", "aplicação parcial",
        "monada", "functor", "aplicativo", "category theory",
        "efeito colateral", "pureza", "imutabilidade", "transparência referencial",
        "recursão", "recursão de cauda", "iteração", "ponto fixo",
        "continuação", "corrotina", "gerador", "async", "await",
        "fibra", "thread", "processo", "Green thread", "Goroutine",
        "canal", "ator", "CSP", "memória compartilhada", "mutex",
        "semáforo", "transação de memória", "STM", "lock-free",
        "padrão de design", "GoF", "arquitetura hexagonal", "clean architecture",
        "DDD", "CQRS", "Event Sourcing", "arquitetura orientada a eventos",
        "sistema de tipos", "soundness", "completude", "decidibilidade",
        "lambda calculus", "sistema F", "CoC", "provas como programas",
        "Curry-Howard", "isomorfismo de Curry-Howard", "lógica linear",
        "autômato", "máquina de Turing", "equivalência de Turing",
        "problema da parada", "indecidibilidade", "NP-completude",
        "redução", "classe de complexidade", "P", "NP", "EXP",
        "memória", "stack", "heap", "GC", "ARC", "cópia", "movimento",
        "ponteiro", "referência", "borrowing", "lifetime", "ownership",
        "Go", "Rust", "Python", "Julia", "Haskell", "OCaml",
        "Erlang", "Elixir", "Clojure", "Scheme", "Racket",
        "Prolog", "C", "C++", "Zig", "Nim", "TypeScript",
    ],
    metodos_pesquisa=[
        "Análise estática de programas", "Prova formal de correção",
        "Model checking", "Teste de software", "Property-based testing",
        "Benchmarking experimental", "Análise de complexidade",
        "Prova de teoremas", "Síntese de programas",
        "Estudo comparativo de linguagens", "Análise de segurança",
    ],
    tradicoes_epistemologicas=[
        "Racionalismo computacional", "Empirismo de software",
        "Formalismo matemático", "Pragmatismo de engenharia",
        "Platonismo computacional", "Construtivismo algorítmico",
        "Funcionalismo lógico", "Pós-modernismo de software",
    ],
    ferramentas=[
        "Python", "Go", "Rust", "Julia", "Haskell", "OCaml",
        "Coq", "Agda", "Idris", "Lean", "Z3", "ProVerif",
        "LLVM", "GCC", "Clang", "SML", "ANTLR", "Happy", "Alex",
        "Git", "GitHub", "GitLab", "Linux", "VS Code", "Emacs", "Vim",
        "Jupyter", "Docker", "Podman", "QEMU", "GDB", "Perf",
    ],
)

# =============================================================================
# 10. INTERDISCIPLINAR (Transversal / Metaciência)
# =============================================================================
INTERDISCIPLINARY = Faculdade(
    id="interdisciplinary",
    nome="Estudos Interdisciplinares e Transversais",
    nome_en="Interdisciplinary and Transversal Studies",
    descricao="Metaciência, complexidade, teoria de sistemas, inovação e neurociência — "
               "o estudo da própria produção de conhecimento, das conexões entre disciplinas "
               "e dos fenômenos emergentes que transcendem fronteiras disciplinares.",
    subdisciplinas=[
        "Metaciência", "Complexidade", "Teoria de Sistemas", "Cibernética",
        "Innovation Studies", "Neurociência", "Ciência Cognitiva",
        "Estudos de Ciência e Tecnologia (STS)", "Transdisciplinaridade",
        "Futurismo", "Epistemologia", "Filosofia da Ciência",
        "Ética em Pesquisa", "Open Science", "Responsible Research",
        "Teoria das Redes", "Ciência das Redes", "Tecnologia Social",
        "Design Science", "Pesquisa-Desenvolvimento-Inovação",
    ],
    conceitos=[
        "complexidade", "emergência", "auto-organização", "caos",
        "sistema adaptativo complexo", "rede", "grafo", "hub",
        "conectividade", "small world", "scale-free", "resiliência",
        "robustez", "fragilidade", "antifragilidade", "cisne negro",
        "meta-conhecimento", "conhecimento do conhecimento", "episteme",
        "paradigma", "revolução científica", "programa de pesquisa",
        "crise", "anomalia", "ciência normal", "ciência extraordinária",
        "interdisciplinaridade", "multidisciplinaridade", "transdisciplinaridade",
        "boundary object", "tradução", "mediação", "hibridização",
        "conhecimento tácito", "conhecimento explícito", "SECI",
        "inovação", "invenção", "difusão", "tecnologia disruptiva",
        "paradigma tecnológico", "trajetória tecnológica", "regime tecnológico",
        "sistema de inovação", "hélice tríplice", "hélice quádrupla",
        "modo 1 de produção de conhecimento", "modo 2", "ciência pós-acadêmica",
        "análise de redes sociais", "homofilia", "força dos laços fracos",
        "embeddedness", "capital social", "confiança", "cooperação",
        "cognição", "mente", "consciência", "percepção", "atenção",
        "memória de trabalho", "memória de longo prazo", "aprendizagem",
        "plasticidade neural", "neuroplasticidade", "neurônio", "sinapse",
        "neurotransmissor", "circuito neural", "mapa cognitivo",
        "modelo mental", "esquema", "heuristic", "viés cognitivo",
        "raciocínio", "tomada de decisão", "resolução de problemas",
        "criatividade", "insight", "flow", "expertise", "deliberação",
        "ciência aberta", "reprodutibilidade", "replicabilidade",
        "pré-registro", "registro de ensaio clínico", "dados abertos",
        "crise de replicação", "p-hacking", "HARKing", "viés de publicação",
        "meta-análise", "revisão sistemática", "evidência", "certeza",
        "incerteza", "ignorância", "epistemologia da ignorância",
        "estudos de futuro", "cenário", "prospecção", "backcasting",
        "antecipação", "dinâmica de sistemas", "ciclo de feedback",
        "causalidade circular", "alavancagem", "ponto de inflexão",
        "problema wicked", "problema super wicked", "poli-crise",
        "grande desafio", "transição sociotécnica", "sustentabilidade",
        "limites planetários", "antropoceno", "capitaloceno",
        "responsabilidade social da ciência", "engajamento público",
        "ciência cidadã", "pesquisa participativa", "co-criação",
    ],
    metodos_pesquisa=[
        "Meta-pesquisa", "Meta-análise", "Revisão sistemática da literatura",
        "Análise de redes", "Modelagem de sistemas dinâmicos",
        "Método de cenários", "Delphi", "Análise de stakeholders",
        "Pesquisa-ação", "Design Science Research", "Mixed methods",
        "Análise bibliométrica", "Cienciometria", "Análise de co-palavras",
        "Análise de co-citação", "Análise longitudinal de paradigmas",
    ],
    tradicoes_epistemologicas=[
        "Complexidade e Caos", "Cibernética de 2ª ordem",
        "Pensamento Sistêmico", "Pragmatismo epistemológico",
        "Naturalismo metodológico", "Construtivismo radical",
        "Realismo crítico", "Relativismo epistemológico",
        "Anarquismo metodológico", "Open Science movement",
        "Post-normal science", "Responsible Research and Innovation (RRI)",
    ],
    ferramentas=[
        "Python", "R", "Gephi", "NodeXL", "NetLogo", "Vensim",
        "Stella", "Cytoscape", "VOSviewer", "Bibliometrix",
        "Zotero", "LaTeX", "Jupyter", "NVivo", "MAXQDA",
        "GitHub", "Zenodo", "OSF", "Figshare",
    ],
)


# =========================================================================
# Agrupamentos
# =========================================================================

ALL_FACULTIES: List[Faculdade] = [
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
]

FACULTY_MAP: Dict[str, Faculdade] = {f.id: f for f in ALL_FACULTIES}


def get_faculty(faculty_id: str) -> Optional[Faculdade]:
    """Retorna faculdade pelo ID."""
    return FACULTY_MAP.get(faculty_id)


def list_all_concepts() -> List[str]:
    """Retorna todos os conceitos de todas as faculdades."""
    result = []
    for fac in ALL_FACULTIES:
        result.extend(fac.conceitos)
    return result


def count_total_concepts() -> int:
    """Conta total de conceitos únicos em todas as faculdades."""
    return len(set(list_all_concepts()))
