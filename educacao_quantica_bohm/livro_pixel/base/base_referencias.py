#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base de referências com DOI/URL e mapa conceito → evidência.

Os DOIs foram verificados via Crossref/DataCite quando possível. O script
`scripts/verificar_dois.py` refaz a checagem e grava o relatório. Nenhum DOI é
inventado: quando não há DOI estável, usamos URL oficial e marcamos o tipo.
"""
from __future__ import annotations


def R(autores, ano, titulo, veiculo, *, doi="", url="", tipo="artigo", forca="B", nota=""):
    return {
        "autores": autores,
        "ano": ano,
        "titulo": titulo,
        "veiculo": veiculo,
        "doi": doi,
        "url": url,
        "tipo": tipo,
        "forca": forca,
        "nota": nota,
    }


REFERENCIAS = {
    "shannon": R("SHANNON, C. E.", "1948", "A Mathematical Theory of Communication",
                 "Bell System Technical Journal", doi="10.1002/j.1538-7305.1948.tb01338.x",
                 forca="A", nota="Origem da medida de informação em bits."),
    "nielsen": R("NIELSEN, M. A.; CHUANG, I. L.", "2010",
                 "Quantum Computation and Quantum Information", "Cambridge University Press",
                 doi="10.1017/CBO9780511976667", tipo="livro", forca="A",
                 nota="Texto de referência para informação quântica."),
    "preskill": R("PRESKILL, J.", "2018", "Quantum Computing in the NISQ era and beyond",
                  "Quantum", doi="10.22331/q-2018-08-06-79", forca="A",
                  nota="Panorama da era NISQ e dos limites do ruído."),
    "cerezo": R("CEREZO, M. et al.", "2021", "Variational Quantum Algorithms",
                "Nature Reviews Physics", doi="10.1038/s42254-021-00348-9", forca="A",
                nota="Revisão de VQCs, paisagens de perda e ruído."),
    "havlicek": R("HAVLÍČEK, V. et al.", "2019",
                  "Supervised Learning with Quantum-Enhanced Feature Spaces", "Nature",
                  doi="10.1038/s41586-019-0980-2", forca="B",
                  nota="Experimento de classificação com kernel quântico."),
    "schuld": R("SCHULD, M. et al.", "2019", "Evaluating Analytic Gradients on Quantum Hardware",
                "Physical Review A", doi="10.1103/PhysRevA.99.032331", forca="B",
                nota="Gradientes analíticos e ruído em hardware."),
    "akiba": R("AKIBA, T. et al.", "2019", "Optuna: A Next-generation Hyperparameter Optimization Framework",
               "KDD", doi="10.1145/3292500.3330701", forca="A",
               nota="TPE e otimização bayesiana de hiperparâmetros."),
    "bell": R("BELL, J. S.", "1964", "On the Einstein Podolsky Rosen paradox",
              "Physics Physique Fizika", doi="10.1103/PhysicsPhysiqueFizika.1.195", forca="A",
              nota="Desigualdade que separa correlações locais de quânticas."),
    "bohm1952": R("BOHM, D.", "1952",
                  "A Suggested Interpretation of the Quantum Theory in Terms of Hidden Variables",
                  "Physical Review", doi="10.1103/PhysRev.85.166", forca="C",
                  nota="Ontologia da onda piloto; interpretação, não consenso."),
    "aspect": R("ASPECT, A.; DALIBARD, J.; ROGER, G.", "1982",
                "Experimental Test of Bell's Inequalities Using Time-Varying Analyzers",
                "Physical Review Letters", doi="10.1103/PhysRevLett.49.1804", forca="A",
                nota="Teste de Bell com analisadores variáveis."),
    "clauser": R("CLAUSER, J. F.; HORNE, M. A.; SHIMONY, A.; HOLT, R. A.", "1969",
                 "Proposed Experiment to Test Local Hidden-Variable Theories",
                 "Physical Review Letters", doi="10.1103/PhysRevLett.23.880", forca="A",
                 nota="Forma CHSH da desigualdade de Bell."),
    "zurek": R("ZUREK, W. H.", "2003", "Decoherence, einselection, and the quantum origins of the classical",
               "Reviews of Modern Physics", doi="10.1103/RevModPhys.75.715", forca="A",
               nota="Decoerência e o surgimento do clássico."),
    "grover": R("GROVER, L. K.", "1996", "A fast quantum mechanical algorithm for database search",
                "STOC", doi="10.1145/237814.237866", forca="A",
                nota="Busca quântica com ganho quadrático."),
    "shor": R("SHOR, P. W.", "1997", "Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms",
              "SIAM Journal on Computing", doi="10.1137/S0097539795293172", forca="A",
              nota="Algoritmos de fatoração e logaritmo discreto."),
    "lloyd": R("LLOYD, S.", "1996", "Universal Quantum Simulators", "Science",
               doi="10.1126/science.273.5278.1073", forca="A",
               nota="Simulação de sistemas físicos com qubits."),
    "raussendorf": R("RAUSSENDORF, R.; BRIEGEL, H. J.", "2001", "A One-Way Quantum Computer",
                     "Physical Review Letters", doi="10.1103/PhysRevLett.86.5188", forca="A",
                     nota="Computação por medição e estados cluster."),
    "arute": R("ARUTE, F. et al.", "2019", "Quantum supremacy using a programmable superconducting processor",
               "Nature", doi="10.1038/s41586-019-1666-5", forca="B",
               nota="Demonstração de supremacia quântica em circuito aleatório."),
    "ibm": R("KIM, Y. et al.", "2023", "Evidence for the utility of quantum computing before fault tolerance",
             "Nature", doi="10.1038/s41586-023-06096-3", forca="B",
             nota="Utilidade de circuitos rasos com mitigação de erro."),
    "biamonte": R("BIAMONTE, J. et al.", "2017", "Quantum machine learning", "Nature",
                  doi="10.1038/nature23474", forca="A",
                  nota="Panorama de aprendizado de máquina quântico."),
    "fowler": R("FOWLER, A. G. et al.", "2012", "Surface codes: Towards practical large-scale quantum computation",
                "Physical Review A", doi="10.1103/PhysRevA.86.032324", forca="A",
                nota="Códigos de superfície e correção de erro."),
    "giovannetti": R("GIOVANNETTI, V.; LLOYD, S.; MACCONE, L.", "2011", "Advances in quantum metrology",
                     "Nature Photonics", doi="10.1038/nphoton.2011.35", forca="A",
                     nota="Limites e ganhos de metrologia quântica."),
    "gisin": R("GISIN, N.; RIBORDY, G.; TITTEL, W.; ZBINDEN, H.", "2002", "Quantum cryptography",
               "Reviews of Modern Physics", doi="10.1103/RevModPhys.74.145", forca="A",
               nota="Fundamentos e práticas de criptografia quântica."),
    "bennett1993": R("BENNETT, C. H. et al.", "1993", "Teleporting an unknown quantum state via dual classical and Einstein-Podolsky-Rosen channels",
                     "Physical Review Letters", doi="10.1103/PhysRevLett.70.1895", forca="A",
                     nota="Protocolo de teleportação quântica."),
    "bennett1992": R("BENNETT, C. H.; WIESNER, S. J.", "1992", "Communication via one- and two-particle operators on Einstein-Podolsky-Rosen states",
                     "Physical Review Letters", doi="10.1103/PhysRevLett.69.2881", forca="A",
                     nota="Codificação densa."),
    "hensen": R("HENSEN, B. et al.", "2015", "Loophole-free Bell inequality violation using electron spins separated by 1.3 kilometres",
                "Nature", doi="10.1038/nature15759", forca="A",
                nota="Teste de Bell sem loopholes principais."),
    "feynman": R("FEYNMAN, R. P.", "1982", "Simulating physics with computers",
                 "International Journal of Theoretical Physics", doi="10.1007/BF02650179",
                 forca="A", nota="Motivação original para simuladores quânticos."),
    "aharonov": R("AHARONOV, Y.; DAVIDOVICH, L.; ZAGURY, N.", "1993", "Quantum random walks",
                  "Physical Review A", doi="10.1103/PhysRevA.48.1687", forca="A",
                  nota="Caminhadas aleatórias quânticas."),
    "mcclean": R("MCCLEAN, J. R. et al.", "2018", "Barren plateaus in quantum neural network training landscapes",
                 "Nature Communications", doi="10.1038/s41467-018-07090-4", forca="A",
                 nota="Planaltos estéreis em paisagens de treino."),
    "wang": R("WANG, S. et al.", "2021", "Noise-induced barren plateaus in variational quantum algorithms",
              "Nature Communications", doi="10.1038/s41467-021-27045-6", forca="A",
              nota="Ruído pode induzir planaltos e limitar VQCs."),
    "temme": R("TEMME, K.; BRAYVI, S.; GAMBETTA, J. M.", "2017", "Error Mitigation for Short-Depth Quantum Circuits",
               "Physical Review Letters", doi="10.1103/PhysRevLett.119.180509", forca="A",
               nota="Mitigação de erro em circuitos rasos."),
    "emerson": R("EMERSON, J.; ALLEGRA, M.; GROISMAN, D.", "2005", "Scalable noise estimation with random unitary operators",
                 "Journal of Optics B", doi="10.1088/1464-4266/7/10/021", forca="A",
                 nota="Randomized benchmarking e estimativa de ruído."),
    "krijtenburg": R("KRIJTENBURG-LEWERISSA, K.; POL, H. J.; BRINKMAN, A.; VAN JOOLINGEN, W. R.", "2017",
                     "Insights into teaching quantum mechanics in secondary and lower undergraduate education",
                     "Physical Review Physics Education Research", doi="10.1103/PhysRevPhysEducRes.13.010109",
                     forca="A", nota="Revisão de ensino de mecânica quântica na escola."),
    "freeman": R("FREEMAN, S. et al.", "2014", "Active learning increases student performance in science, engineering, and mathematics",
                 "PNAS", doi="10.1073/pnas.1319030111", forca="A",
                 nota="Meta-análise de aprendizagem ativa."),
    "deslauriers": R("DESLAURIERS, L. et al.", "2019", "Measuring actual learning versus feeling of learning in response to being actively engaged in the classroom",
                     "PNAS", doi="10.1073/pnas.1821936116", forca="A",
                     nota="Aprendizagem ativa vs sensação de aprendizagem."),
    "roediger": R("ROEDIGER, H. L.; KARPICKE, J. D.", "2006", "Test-Enhanced Learning",
                  "Psychological Science", doi="10.1111/j.1467-9280.2006.01693.x", forca="A",
                  nota="Prática de recuperação e retenção."),
    "cepeda": R("CEPEDA, N. J. et al.", "2006", "Distributed practice in verbal recall tasks: A review and quantitative synthesis",
                "Psychological Bulletin", doi="10.1037/0033-2909.132.3.354", forca="A",
                nota="Prática distribuída e intervalos."),
    "hattie": R("HATTIE, J.; TIMPERLEY, H.", "2007", "The Power of Feedback",
                "Review of Educational Research", doi="10.3102/003465430298487", forca="A",
                nota="Feedback eficaz: meta, evidência e próximo passo."),
    "jobin": R("JOBIN, A.; IENCA, M.; VAYENA, E.", "2019", "The global landscape of AI ethics guidelines",
               "Nature Machine Intelligence", doi="10.1038/s42256-019-0088-2", forca="B",
               nota="Mapa de princípios éticos em IA."),
    "mittelstadt": R("MITTELSTADT, B. D. et al.", "2016", "The ethics of algorithms: Mapping the debate",
                     "Big Data & Society", doi="10.1177/2053951716679679", forca="B",
                     nota="Debate sobre opacidade, viés e responsabilidade."),
    "fair": R("WILKINSON, M. D. et al.", "2016", "The FAIR Guiding Principles for scientific data management and stewardship",
              "Scientific Data", doi="10.1038/sdata.2016.18", forca="A",
              nota="Dados encontráveis, acessíveis, interoperáveis e reutilizáveis."),
    "osc": R("OPEN SCIENCE COLLABORATION", "2015", "Estimating the reproducibility of psychological science",
             "Science", doi="10.1126/science.aac4716", forca="A",
             nota="Estudo de replicabilidade e poder estatístico."),
    "wasserstein": R("WASSERSTEIN, R. L.; LAZAR, N. A.", "2016", "The ASA Statement on p-Values: Context, Process, and Purpose",
                     "The American Statistician", doi="10.1080/00031305.2016.1154108", forca="A",
                     nota="Limites do valor de p e da significância."),
    "ioannidis": R("IOANNIDIS, J. P. A.", "2005", "Why Most Published Research Findings Are False",
                   "PLOS Medicine", doi="10.1371/journal.pmed.0020124", forca="A",
                   nota="Poder, viés e multiplicidade de testes."),
    "qiskit": R("QISKIT DEVELOPMENT TEAM", "2024", "Qiskit: An Open-Source Framework for Quantum Computing",
                "Zenodo", doi="10.5281/zenodo.2573505", url="https://qiskit.org",
                tipo="software", forca="B", nota="Framework usado nos experimentos."),
    "pennylane": R("BERGHOLM, V. et al.", "2018", "PennyLane: Automatic differentiation of hybrid quantum-classical computations",
                   "arXiv", url="https://arxiv.org/abs/1811.04968", tipo="preprint", forca="B",
                   nota="Diferenciação automática de circuitos."),
    "cirq": R("GOOGLE QUANTUM AI", "2024", "Cirq: A Python framework for creating, editing, and invoking quantum circuits",
              "GitHub", url="https://github.com/quantumlib/Cirq", tipo="software", forca="B",
              nota="Framework com foco em hardware supercondutor."),
    "tiangong": R("TIANGONG / CETC-ICQ", "2026", "Quantum Computing Platform User Guide",
                  "Tiangong", url="https://tiangongqs.com/cloud/circuit", tipo="documentação",
                  forca="B", nota="Console e editor QASM usados no livro."),
    "ciquanta": R("CIQUANTA", "2026", "Centro Internacional de Computação e Tecnologias Quânticas",
                  "CIQuanta", url="https://cloudciquanta.secties.pb.gov.br", tipo="documentação",
                  forca="B", nota="Infraestrutura pública de computação quântica."),
    "lgpd": R("BRASIL", "2018", "Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018)",
              "Diário Oficial da União", url="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm",
              tipo="legislação", forca="A", nota="Base legal, finalidade e direitos dos titulares."),
}

POR_PARTE = {
    1: ["shannon", "nielsen", "bell"],
    2: ["bohm1952", "bell", "nielsen"],
    3: ["nielsen", "qiskit", "grover"],
    4: ["qiskit", "pennylane", "cirq"],
    5: ["preskill", "zurek", "ibm"],
    6: ["cerezo", "havlicek", "schuld"],
    7: ["nielsen", "cerezo", "feynman"],
    8: ["krijtenburg", "freeman", "roediger", "cepeda", "hattie"],
    9: ["jobin", "mittelstadt", "fair", "lgpd"],
    10: ["osc", "ioannidis", "wasserstein", "fair"],
}

GRAU_PARTE = {
    1: ("A", "Definições e testes de Bell consolidados; interpretações seguem em debate."),
    2: ("C", "Interpretação de Bohm: coerente, mas não é consenso nem teste decisivo."),
    3: ("A", "Circuitos e algoritmos com tratamento textbook; implementação depende do backend."),
    4: ("B", "Ferramentas documentadas; resultados variam com versão e convenção."),
    5: ("B", "Hardware e nuvem: evidência experimental, mas calibração e fila mudam."),
    6: ("C", "VQC e ruído: resultados promissores, amostras pequenas; não generaliza."),
    7: ("A", "Matemática estabelecida; notação e convenções variam."),
    8: ("A", "Pedagogia: evidência moderada a forte; contexto importa."),
    9: ("C", "Ética: normativa; não há teste experimental único."),
    10: ("B", "Métodos de pesquisa: evidência metodológica, não resultado empírico."),
}

OVERRIDES = {
    "bit": ["shannon", "nielsen"],
    "qubit": ["nielsen", "preskill"],
    "bell": ["bell", "clauser", "aspect"],
    "emaranhamento": ["bell", "aspect", "hensen"],
    "ghz": ["nielsen", "raussendorf"],
    "qasm": ["qiskit", "nielsen"],
    "transpilacao": ["qiskit", "preskill"],
    "vqc_xor": ["cerezo", "havlicek", "schuld"],
    "ruido_benefico": ["cerezo", "mcclean", "wang"],
    "ghz_real": ["arute", "ibm", "preskill"],
    "phase_damping": ["zurek", "preskill"],
    "depolarizing": ["zurek", "temme"],
    "ciquanta": ["ciquanta", "preskill"],
    "tiangong": ["tiangong", "preskill"],
    "lgpd": ["lgpd", "fair"],
    "acesso": ["lgpd", "jobin"],
    "privacidade": ["lgpd", "mittelstadt"],
    "desinformacao": ["osc", "ioannidis"],
    "consenso": ["osc", "ioannidis"],
    "replicacao": ["osc", "ioannidis"],
    "evidencia": ["wasserstein", "ioannidis"],
    "limite": ["wasserstein", "ioannidis"],
}


def refs_conceito(c: dict) -> list[str]:
    return OVERRIDES.get(c["id"], POR_PARTE[c["parte"]])


def ref(nome: str) -> dict:
    return REFERENCIAS[nome]


def abnt(nome: str) -> str:
    r = REFERENCIAS[nome]
    autores = r["autores"].rstrip(".")
    base = f"{autores}. <em>{r['titulo']}</em>. {r['veiculo']}, {r['ano']}."
    if r.get("doi"):
        return base + f' DOI: <a href="https://doi.org/{r["doi"]}">{r["doi"]}</a>.'
    if r.get("url"):
        return base + f' Disponível em: <a href="{r["url"]}">{r["url"]}</a>. Acesso em: 7 nov. 2026.'
    return base


def link(nome: str) -> str:
    r = REFERENCIAS[nome]
    if r.get("doi"):
        return f"https://doi.org/{r['doi']}"
    return r.get("url", "")