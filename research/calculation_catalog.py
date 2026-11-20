"""Catálogo versionado de exatamente 200 cálculos — SPEC-935-R1256.

Itens planejados são metadados, não calculadoras: ``resolve_calculator`` falha
fechado para eles. Cada item futuro exige especificação de fórmula, fontes e
testes antes de mudar para ``implemented``.
"""
from __future__ import annotations

from copy import deepcopy
from importlib import import_module


_GROUPS = [
    {
        "domain": "statistics", "code": "STAT",
        "names": """
            Cálculo amostral para proporção
            Cálculo amostral para média
            Intervalo de Wilson para proporção
            ANOVA de uma via
            Correlação de Spearman
            Correlação de Pearson
            Teste t de Welch
            Estatística descritiva
            Análise de poder estatístico
            Cálculo amostral para diferença entre médias
            Cálculo amostral para dados pareados
            Teste U de Mann–Whitney
            Teste de postos sinalizados de Wilcoxon
            Teste de Kruskal–Wallis
            Teste de Friedman
            Qui-quadrado de independência
            Teste exato de Fisher
            Teste de McNemar
            Covariância amostral
            Correlação parcial
            Regressão linear múltipla
            Regressão logística binária
            Regressão de Poisson
            Regressão binomial negativa
            Regressão quantílica
            Regressão robusta
            Fator de inflação da variância
            Diagnóstico de resíduos
            Intervalo bootstrap
            Teste de permutação
            Erro-padrão bootstrap
            d de Cohen
            g de Hedges
            V de Cramér
            Kappa de Cohen
            Correlação intraclasse
            Concordância intraclasse
            Imputação múltipla de dados faltantes
            Tamanho de efeito detectável
            Erro-padrão robusto por conglomerado
        """,
        "inputs": "observações e parâmetros do método (por exemplo, alpha, confiança, grupos)",
        "outputs": "estimativa, estatística/intervalo e diagnósticos aplicáveis",
        "units": "unidade da variável de entrada ou adimensional, conforme o método",
    },
    {
        "domain": "biostatistics", "code": "BIO",
        "names": """
            Acurácia de teste diagnóstico
            Razão de riscos
            Razão de chances em tabela 2 por 2
            Estimador de Kaplan–Meier
            Modelo de riscos proporcionais de Cox
            Teste de log-rank
            Taxa de incidência
            Prevalência pontual
            Redução absoluta do risco
            Número necessário para tratar
            Razão de riscos instantâneos
            Mediana de sobrevida
            Densidade de incidência
            Fração atribuível populacional
            Padronização direta por idade
            Padronização indireta por idade
            Risco atribuível
            Diferença de prevalências
            Razão de prevalências
            Intervalo de confiança de incidência
            Teste de Hardy–Weinberg
            Frequência alélica
            Frequência genotípica
            Desequilíbrio de ligação
            Herdabilidade em sentido amplo
            Herdabilidade em sentido restrito
            Coeficiente de consanguinidade
            Risco relativo genético
            NNT para desfecho contínuo
            Número necessário para causar dano
            Sobrevida livre de evento
            Tempo médio de sobrevida restrito
            Risco competitivo cumulativo
            Regressão logística condicional
            Tamanho amostral para ensaio clínico
        """,
        "inputs": "contagens clínicas/genéticas, tempos, estados de evento e desenho declarado",
        "outputs": "medida bioestatística, intervalo/teste aplicável e pressupostos",
        "units": "proporção, razão, taxa por tempo ou unidade temporal, conforme o cálculo",
    },
    {
        "domain": "bioinformatics", "code": "OMICS",
        "names": """
            Ajuste Benjamini–Hochberg para FDR
            Contagem por milhão (CPM)
            Fragmentos por quilobase por milhão (FPKM)
            Transcritos por milhão (TPM)
            Fator de normalização por tamanho de biblioteca
            Normalização por quantis
            Mudança de expressão em escala log2
            Variação de expressão diferencial
            Componente principal de expressão
            Distância de Bray–Curtis
            Índice de Jaccard para comunidades
            Diversidade alfa de Shannon
            Diversidade alfa de Simpson
            Índice de equitabilidade de Pielou
            Diversidade beta UniFrac não ponderada
            Diversidade beta UniFrac ponderada
            Identidade percentual de sequência
            Cobertura de alinhamento
            Conteúdo GC de sequência
            Profundidade média de sequenciamento
            Fração alélica variante
            Escore de qualidade Phred
            N50 de montagem genômica
            L50 de montagem genômica
            Número de variantes por amostra
            Desequilíbrio de ligação D-prime
            Desequilíbrio de ligação r ao quadrado
            Distância genética de Nei
            Distância filogenética patristica
            Entropia de sítios de alinhamento
            Heterozigosidade observada
            Heterozigosidade esperada
            Coeficiente de endogamia FIS
            Taxa de erro de chamada de variantes
            Correlação de expressão gênica
        """,
        "inputs": "matriz ômica/contagens/sequências, metadados e parâmetros de normalização",
        "outputs": "medida ou matriz normalizada, estatística e unidades biológicas declaradas",
        "units": "unidade de contagem, comprimento, proporção ou escore adimensional conforme o método",
    },
    {
        "domain": "meta_analysis", "code": "META",
        "names": """
            Q de Cochran para heterogeneidade
            Tau ao quadrado entre estudos
            I ao quadrado de Higgins–Thompson
            Efeito combinado de efeito fixo
            Efeito combinado de efeitos aleatórios
            Variância inversa de efeito fixo
            Modelo de DerSimonian–Laird
            Estimador REML de tau ao quadrado
            Intervalo de predição de efeito aleatório
            Razão de chances combinada
            Razão de riscos combinada
            Diferença média padronizada combinada
            Diferença média combinada
            Erro-padrão do efeito combinado
            Teste de Egger para assimetria
            Correção trim-and-fill
            Análise leave-one-out
            Meta-regressão de efeitos aleatórios
            Número necessário para informação ótima
            Heterogeneidade explicada por covariável
        """,
        "inputs": "estimativas de estudos independentes na mesma escala e suas variâncias",
        "outputs": "efeito combinado/heterogeneidade/diagnóstico e intervalos aplicáveis",
        "units": "escala do efeito original; heterogeneidade percentual ou adimensional",
    },
    {
        "domain": "finance", "code": "FIN",
        "names": """
            Ponto de equilíbrio
            Taxa interna de retorno (TIR)
            Preço de venda por markup sobre custo
            Valor presente líquido (VPL)
            Custo das mercadorias vendidas (CMV)
            Retorno sobre investimento (ROI)
            Margem de contribuição
            Custo médio ponderado por quantidade
            Custo médio ponderado de capital (WACC)
            Prazo de payback simples
            Prazo de payback descontado
            Valor futuro de fluxo único
            Valor presente de fluxo único
            Anuidade ordinária de valor presente
            Anuidade antecipada de valor presente
            Taxa efetiva anual
            Taxa nominal anual equivalente
            Margem bruta
            Margem operacional
            Alavancagem financeira
        """,
        "inputs": "fluxos, saldos, preços/custos, quantidades e taxas explícitas",
        "outputs": "valor financeiro, taxa, margem, quantidade ou prazo",
        "units": "unidade monetária e periodicidade fornecidas pelo usuário; taxa como fração",
    },
    {
        "domain": "physical_chemistry", "code": "PHCH",
        "names": """
            Concentração molar
            Diluição de solução
            Lei dos gases ideais
            pH de solução ideal
            pOH de solução ideal
            Equação de Henderson–Hasselbalch
            Equação de Arrhenius
            Energia de ativação por dois pontos
            Constante de equilíbrio a partir de Gibbs
            Energia de Gibbs de reação
            Equação de Nernst
            Pressão osmótica ideal
            Elevação ebuliométrica
            Depressão crioscópica
            Lei de Beer–Lambert
            Capacidade calorífica molar
            Calorimetria a pressão constante
            Isoterma de Langmuir
            Isoterma de Freundlich
            Constante de equilíbrio ácido-base
        """,
        "inputs": "quantidades físico-químicas, condições experimentais, unidades e modelo declarados",
        "outputs": "concentração, energia, equilíbrio, potencial ou propriedade termodinâmica",
        "units": "unidades SI ou unidades explicitamente indicadas pelo usuário",
    },
    {
        "domain": "physics_quantum_astrophysics", "code": "QPHYS",
        "names": """
            Normalização de vetor de estado quântico complexo
            Produto interno complexo bra-ket
            Matriz densidade de estado puro
            Probabilidades de Born por amplitude complexa
            Valor esperado de operador Hermitiano
            Exponencial q de Tsallis
            Pureza de matriz densidade
            Entropia de von Neumann
            Fidelidade entre estados puros
            Fase relativa de amplitudes
            Relação de incerteza de posição e momento
            Integral por Monte Carlo
            Erro-padrão de estimativa Monte Carlo
            Aceitação do algoritmo Metropolis
            Função de partição canônica
            Distribuição de Boltzmann
            Lei de Planck de corpo negro
            Lei de deslocamento de Wien
            Luminosidade de Stefan–Boltzmann
            Raio de Schwarzschild
            Relação de Hubble–Lemaître
            Velocidade de escape
            Período orbital de Kepler
            Parâmetro gravitacional padrão
            Comprimento de onda de de Broglie
            Energia de partícula em caixa unidimensional
            Probabilidade de tunelamento WKB
            Níveis do oscilador harmônico quântico
            Função de partição de oscilador harmônico quântico
            Potencial químico em ensemble ideal
        """,
        "inputs": "vetores complexos, operadores, constantes, observáveis e parâmetros físicos explícitos",
        "outputs": "amplitudes/probabilidades/observáveis/estimativas físicas com unidade ou escopo declarado",
        "units": "complexo adimensional ou unidades SI; preservar convenção física explicitada",
    },
]


_IMPLEMENTED = {
    "STAT-001": ("research.quantitative_calculators", "calculate_sample_size_proportion", "n0=Z²p(1-p)/e²; FPC e ajustes explícitos"),
    "STAT-002": ("research.quantitative_calculators", "calculate_sample_size_mean", "n0=(Zσ/e)²; FPC e ajustes explícitos"),
    "STAT-003": ("research.quantitative_calculators", "wilson_interval", "Intervalo de escore de Wilson"),
    "STAT-004": ("research.advanced_statistics", "one_way_anova", "F=MS_between/MS_within; eta²=SS_between/SS_total"),
    "STAT-005": ("research.advanced_statistics", "spearman_correlation", "Correlação de postos de Spearman"),
    "STAT-006": ("research.statistical_methods", "execute_analysis", "Pearson; chamada via execute_analysis(..., method='pearson', ...)"),
    "STAT-007": ("research.statistical_methods", "execute_analysis", "Welch t; chamada via execute_analysis(..., method='welch_t', ...)"),
    "STAT-008": ("research.statistical_methods", "execute_analysis", "Resumo descritivo; chamada via execute_analysis(..., method='descriptive', ...)"),
    "BIO-001": ("research.advanced_statistics", "diagnostic_accuracy", "Sensibilidade, especificidade, valores preditivos e acurácia"),
    "BIO-002": ("research.advanced_statistics", "risk_ratio", "(a/n1)/(c/n0); intervalo log-Wald sem correção de zero"),
    "BIO-003": ("research.advanced_statistics", "odds_ratio", "(a*d)/(b*c); intervalo log-Wald sem correção de zero"),
    "OMICS-001": ("research.advanced_statistics", "benjamini_hochberg", "q_(i)=min_{j≥i}(m*p_(j)/j), limitado a 1"),
    "META-001": ("research.advanced_statistics", "cochrans_q_meta_analysis", "Q=Σw_i(y_i-ȳw)²; w_i=1/v_i"),
    "FIN-001": ("research.quantitative_calculators", "break_even", "custo_fixo/(preço_unitário-custo_variável_unitário)"),
    "FIN-002": ("research.quantitative_calculators", "internal_rate_of_return", "Raízes reais r>-1 de Σ CF_t/(1+r)^t=0"),
    "FIN-003": ("research.quantitative_calculators", "markup_price", "custo*(1+markup sobre custo)"),
    "FIN-004": ("research.quantitative_calculators", "net_present_value", "Σ CF_t/(1+r)^t; CF_0 não descontado"),
    "FIN-005": ("research.quantitative_calculators", "cost_of_goods_sold", "estoque_inicial+compras-estoque_final"),
    "FIN-006": ("research.quantitative_calculators", "return_on_investment", "(retorno_bruto-investimento)/investimento"),
    "FIN-007": ("research.quantitative_calculators", "contribution_margin", "(preço-custo_variável)/preço"),
    "FIN-008": ("research.quantitative_calculators", "weighted_average_cost", "Σ(custo_i*quantidade_i)/Σquantidade_i"),
    "FIN-009": ("research.quantitative_calculators", "weighted_average_cost_of_capital", "E/(D+E)Re + D/(D+E)Rd(1-T)"),
    "QPHYS-001": ("reasoning.quantum", "normalize_state_vector", "|ψ>/sqrt(<ψ|ψ>)"),
    "QPHYS-002": ("reasoning.quantum", "inner_product", "<a|b>=Σ conj(a_i)b_i"),
    "QPHYS-003": ("reasoning.quantum", "density_matrix", "ρ_ij=ψ_i*conj(ψ_j)"),
    "QPHYS-004": ("reasoning.quantum", "born_probabilities", "P_i=|ψ_i|² para estado normalizado"),
    "QPHYS-005": ("reasoning.quantum", "expectation_value", "<ψ|A|ψ>, A Hermitiano"),
    "QPHYS-006": ("research.quantitative_calculators", "q_exponential", "[1+(1-q)x]^(1/(1-q)); limite exp(x) em q=1"),
}


def _calculation_type(name: str) -> str:
    lowered = name.casefold()
    if "amostral" in lowered or "tamanho amostral" in lowered:
        return "sample_size"
    if "intervalo" in lowered:
        return "confidence_interval"
    if any(term in lowered for term in ("teste", "anova", "qui-quadrado", "log-rank", "hardy–weinberg")):
        return "hypothesis_test"
    if "correlação" in lowered:
        return "association_measure"
    if "regressão" in lowered or "modelo" in lowered:
        return "model_estimation"
    return "deterministic_calculation"


def _build_catalog() -> list[dict]:
    items = []
    for group in _GROUPS:
        names = [line.strip() for line in group["names"].strip().splitlines() if line.strip()]
        for index, name in enumerate(names, 1):
            identifier = f"{group['code']}-{index:03d}"
            implementation = _IMPLEMENTED.get(identifier)
            if implementation:
                module, symbol, formula = implementation
                api = f"{module}.{symbol}"
                status = "implemented"
                assumptions = ["Consultar docstring/retorno da API; o cálculo não valida automaticamente os dados ou o desenho."]
            else:
                module = symbol = api = None
                formula = "Pendente: formalizar fórmula e fonte metodológica em spec de fase antes de ativar."
                status = "planned"
                assumptions = ["Não executável. Fórmula, fonte, pressupostos, unidades e testes devem ser aprovados antes da ativação."]
            items.append({
                "id": identifier,
                "domain": group["domain"],
                "name": name,
                "type": _calculation_type(name),
                "status": status,
                "formula": formula,
                "inputs": group["inputs"],
                "outputs": group["outputs"],
                "units": group["units"],
                "assumptions": assumptions,
                "api": api,
                "phase": "R1256-initial" if implementation else "planned",
            })
    if len(items) != 200 or len({item["id"] for item in items}) != 200:
        raise RuntimeError(f"Catálogo R1256 inválido: esperado 200 itens, recebido {len(items)}.")
    if set(_IMPLEMENTED) != {item["id"] for item in items if item["status"] == "implemented"}:
        raise RuntimeError("Mapeamento de APIs implementadas não corresponde ao catálogo.")
    return items


_CATALOG = _build_catalog()
_BY_ID = {item["id"]: item for item in _CATALOG}


def get_calculation_catalog() -> list[dict]:
    """Retorna cópia do catálogo para impedir mutações globais pelo chamador."""
    return deepcopy(_CATALOG)


def get_calculation(calculation_id: str) -> dict:
    if not isinstance(calculation_id, str) or calculation_id not in _BY_ID:
        raise KeyError(f"Cálculo desconhecido: {calculation_id!r}")
    return deepcopy(_BY_ID[calculation_id])


def resolve_calculator(calculation_id: str):
    """Resolve API implementada; entradas planejadas falham sem produzir número."""
    item = get_calculation(calculation_id)
    if item["status"] != "implemented":
        raise NotImplementedError(f"{calculation_id} está planejado e não pode ser executado.")
    module_name, symbol = _IMPLEMENTED[calculation_id][:2]
    calculator = getattr(import_module(module_name), symbol, None)
    if not callable(calculator):
        raise RuntimeError(f"API declarada não está disponível: {module_name}.{symbol}")
    return calculator
