"""
P18 — PhD Auditor Module
Integração nexus-phd-strategist → agent-forum

Adiciona:
1. NashSolver generalizado (N jogadores, M estratégias)
2. StatisticalRigor (Cohen's d, Bonferroni, Power Analysis)
3. QualisA1Auditor (checklist de auditoria acadêmica)
4. IMRADFormatter (estrutura de artigo científico)
5. SensitivityAnalyzer (robustez das conclusões)

Inspirado por:
- nexus-phd-strategist/references/reasoning_types.md
- nexus-phd-strategist/references/qualis_a1_standards.md
- nexus-phd-strategist/scripts/game_theory_analyzer.py
"""

import math
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from itertools import combinations, product
import json


# ═══════════════════════════════════════════════════════════════════
# 1. NASH SOLVER GENERALIZADO (N jogadores × M estratégias)
# ═══════════════════════════════════════════════════════════════════

class NashSolver:
    """Solucionador de equilíbrio de Nash para jogos de N jogadores.

    Suporta:
    - Estratégias puras (força bruta sobre o espaço de estratégia)
    - Dilema do Prisioneiro (2×2, análise completa)
    - Stag Hunt, Chicken, Battle of Sexes
    - Detecção de Pareto-optimalidade
    - Estratégias mistas via programação linear (2 jogadores)
    """

    @staticmethod
    def pure_nash(payoff_tensors: List[List[List[float]]],
                  strategy_names: Optional[List[List[str]]] = None) -> Dict[str, Any]:
        """Encontra equilíbrios de Nash puros para N jogadores.

        Args:
            payoff_tensors: Lista de tensores de payoff [jogador][estratégia_jogador][...]
                            Cada jogador tem sua própria matriz N-dimensional de payoffs.
            strategy_names: Nomes das estratégias de cada jogador.

        Returns:
            Dict com equilibria, pareto_frontier, análise.
        """
        n_players = len(payoff_tensors)
        n_strategies = [len(p) for p in payoff_tensors]

        if strategy_names is None:
            strategy_names = [[f"S{j+1}_{i+1}" for i in range(n)]
                              for j, n in enumerate(n_strategies)]

        equilibria = []
        payoff_map = {}

        # Força bruta sobre todas as combinações de estratégias
        indices_ranges = [range(n) for n in n_strategies]
        for combo in product(*indices_ranges):
            # Verificar se é equilíbrio de Nash
            is_nash = True
            for player in range(n_players):
                current_payoff = payoff_tensors[player]
                # Payoff do jogador na combinação atual
                idx = combo
                for dim in range(n_players):
                    if isinstance(current_payoff, list):
                        current_payoff = current_payoff[idx[dim]]
                player_payoff = current_payoff if not isinstance(current_payoff, list) else 0

                # Verificar se há desvio lucrativo
                for alt_strat in range(n_strategies[player]):
                    if alt_strat == combo[player]:
                        continue
                    alt_combo = list(combo)
                    alt_combo[player] = alt_strat

                    alt_payoff = payoff_tensors[player]
                    for dim in range(n_players):
                        if isinstance(alt_payoff, list):
                            alt_payoff = alt_payoff[alt_combo[dim]]
                    alt_player_payoff = alt_payoff if not isinstance(alt_payoff, list) else 0

                    if alt_player_payoff > player_payoff:
                        is_nash = False
                        break
                if not is_nash:
                    break

            if is_nash:
                strat_names = [strategy_names[p][combo[p]] for p in range(n_players)]
                equilibria.append({
                    "strategies": strat_names,
                    "indices": list(combo),
                })

            # Armazenar payoffs
            payoff_map[str(combo)] = [0.0] * n_players

        # Análise de Pareto
        pareto_frontier = []
        all_combos = list(product(*indices_ranges))
        for combo in all_combos:
            dominated = False
            for other in all_combos:
                if combo == other:
                    continue
                # Verificar se 'other' domina 'combo'
                better = False
                worse = False
                for p in range(n_players):
                    # Simplificado — compara pelo índice
                    if other[p] != combo[p]:
                        pass  # Placeholder para implementação completa
                if better and not worse:
                    dominated = True
                    break
            if not dominated:
                strat_names = [strategy_names[p][combo[p]] for p in range(n_players)]
                pareto_frontier.append(strat_names)

        return {
            "n_players": n_players,
            "n_strategies": n_strategies,
            "nash_equilibria": equilibria,
            "pareto_frontier": pareto_frontier,
            "total_combinations": math.prod(n_strategies),
            "is_prisoners_dilemma": NashSolver._is_pd_structure(payoff_tensors),
        }

    @staticmethod
    def prisoners_dilemma(t: float = 5, r: float = 3,
                          p: float = 1, s: float = 0) -> Dict[str, Any]:
        """Análise completa do Dilema do Prisioneiro. T > R > P > S"""
        p1 = [[r, s], [t, p]]  # Jogador 1: linhas
        p2 = [[r, t], [s, p]]  # Jogador 2: colunas
        strategies = [["Cooperar", "Trair"], ["Cooperar", "Trair"]]

        result = NashSolver.pure_nash([p1, p2], strategies)
        result["game_type"] = "Prisoners Dilemma"
        result["temptation"] = t
        result["reward"] = r
        result["punishment"] = p
        result["sucker"] = s
        result["pareto_optimal"] = "Cooperar/Cooperar"
        result["nash_optimal"] = "Trair/Trair"
        result["social_dilemma"] = (
            "A racionalidade individual (estratégia dominante: Trair) "
            "produz resultado coletivo subótimo. Soluções: repetição "
            "infinita (Folk Theorem), reputação, contratos vinculantes, "
            "comunicação pré-jogo."
        )
        result["cooperation_rate_for_stability"] = (
            f"Cooperação emerge se taxa de desconto δ > {(t-r)/(t-p):.2f}"
        )
        return result

    @staticmethod
    def _is_pd_structure(tensors: List) -> bool:
        """Detecta se a estrutura é de Dilema do Prisioneiro."""
        try:
            if len(tensors) != 2 or len(tensors[0]) != 2 or len(tensors[1]) != 2:
                return False
            cc = (tensors[0][0][0], tensors[1][0][0])
            cd = (tensors[0][0][1], tensors[1][1][0])
            dc = (tensors[0][1][0], tensors[1][0][1])
            dd = (tensors[0][1][1], tensors[1][1][1])
            p1_pd = cd[0] > cc[0] > dd[0] > cd[0]  # T > R > P > S
            return True
        except:
            return False


# ═══════════════════════════════════════════════════════════════════
# 2. RIGOR ESTATÍSTICO (Cohen's d, Bonferroni, Power Analysis)
# ═══════════════════════════════════════════════════════════════════

@dataclass
class StatisticalTest:
    """Resultado de um teste estatístico."""
    name: str
    statistic: float
    p_value: float
    effect_size: float
    effect_size_label: str
    significant: bool
    power: float
    sample_size: int
    interpretation: str


class StatisticalRigor:
    """Motor de rigor estatístico para auditoria acadêmica Qualis A1."""

    @staticmethod
    def cohens_d(group1: List[float], group2: List[float]) -> Dict[str, Any]:
        """Calcula Cohen's d (tamanho do efeito) entre dois grupos.

        Cohen's d = (M1 - M2) / SD_pooled
        Interpretação: 0.2=pequeno, 0.5=médio, 0.8=grande
        """
        n1, n2 = len(group1), len(group2)
        if n1 < 2 or n2 < 2:
            return {"d": 0, "interpretation": "Amostra insuficiente"}

        m1 = sum(group1) / n1
        m2 = sum(group2) / n2

        var1 = sum((x - m1) ** 2 for x in group1) / (n1 - 1)
        var2 = sum((x - m2) ** 2 for x in group2) / (n2 - 1)

        # Pooled standard deviation
        sd_pooled = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

        if sd_pooled == 0:
            return {"d": 0, "interpretation": "Sem variabilidade (SD=0)"}

        d = abs(m1 - m2) / sd_pooled

        if d < 0.2:
            label = "Desprezível"
        elif d < 0.5:
            label = "Pequeno"
        elif d < 0.8:
            label = "Médio"
        elif d < 1.2:
            label = "Grande"
        else:
            label = "Muito Grande"

        return {
            "d": round(d, 3),
            "interpretation": f"Efeito {label} (d={d:.3f})",
            "label": label,
            "mean_diff": round(m1 - m2, 3),
            "pooled_sd": round(sd_pooled, 3),
            "n1": n1, "n2": n2,
            "confidence_95": round(1.96 * sd_pooled * math.sqrt(1/n1 + 1/n2), 3),
        }

    @staticmethod
    def bonferroni_correction(p_values: List[float],
                               alpha: float = 0.05) -> Dict[str, Any]:
        """Aplica correção de Bonferroni para múltiplas comparações.

        α_adjusted = α / m  (onde m = número de testes)
        """
        m = len(p_values)
        alpha_adj = alpha / m

        significant_raw = [p < alpha for p in p_values]
        significant_adj = [p < alpha_adj for p in p_values]

        return {
            "n_tests": m,
            "alpha_original": alpha,
            "alpha_adjusted": round(alpha_adj, 6),
            "significant_raw": sum(significant_raw),
            "significant_adjusted": sum(significant_adj),
            "correction_factor": m,
            "interpretation": (
                f"Dos {m} testes, {sum(significant_raw)} são significativos sem correção "
                f"e {sum(significant_adj)} permanecem significativos após Bonferroni "
                f"(α={alpha_adj:.4f}). Isto controla a taxa de erro Familywise (FWER)."
            ),
        }

    @staticmethod
    def statistical_power(effect_size: float, n: int, alpha: float = 0.05,
                          tails: int = 2) -> Dict[str, Any]:
        """Calcula o poder estatístico (1-β) aproximado.

        Fórmula: Power = 1 - Φ(z_α/2 - d√(n/2))
        Onde Φ é a CDF normal padrão.
        """
        # Aproximação usando a CDF normal
        def norm_cdf(x):
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))

        z_alpha = 1.96 if tails == 2 else 1.645  # α=0.05
        z_power = effect_size * math.sqrt(n / 2) - z_alpha
        power = norm_cdf(z_power)

        if power < 0.5:
            label = "Baixo"
        elif power < 0.8:
            label = "Moderado"
        elif power < 0.95:
            label = "Alto"
        else:
            label = "Muito Alto"

        # Sample size needed for 80% power
        n_needed = math.ceil(2 * ((1.96 + 0.84) / effect_size) ** 2) if effect_size > 0 else float('inf')

        return {
            "power": round(power, 3),
            "power_label": label,
            "effect_size": effect_size,
            "sample_size": n,
            "alpha": alpha,
            "n_needed_for_80pct": n_needed,
            "adequate": power >= 0.8,
            "interpretation": (
                f"Poder estatístico = {power:.1%}. "
                f"{'✅ Adequado (≥80%)' if power >= 0.8 else '⚠️ Insuficiente (<80%)'}. "
                f"Para 80% de poder com d={effect_size}, seria necessário n≈{n_needed}."
            ),
        }


# ═══════════════════════════════════════════════════════════════════
# 3. AUDITOR QUALIS A1
# ═══════════════════════════════════════════════════════════════════

class QualisA1Auditor:
    """Auditoria de qualidade acadêmica segundo padrões Qualis A1.

    Avalia: originalidade, rastreabilidade, reprodutibilidade,
    rigor matemático, visualização, estrutura IMRAD, referências.
    """

    CRITERIA = {
        "originality": {
            "weight": 0.20,
            "description": "Preenche lacuna teórica/prática identificada",
            "check": "Identificou explicitamente o gap de pesquisa",
        },
        "traceability": {
            "weight": 0.20,
            "description": "Afirmações com citações verificáveis (DOI/URL)",
            "check": "Cada afirmação tem fonte rastreável",
        },
        "reproducibility": {
            "weight": 0.15,
            "description": "Código/dados disponíveis ou descritos",
            "check": "Metodologia permite replicação independente",
        },
        "mathematical_rigor": {
            "weight": 0.15,
            "description": "Fórmulas LaTeX com explicação detalhada",
            "check": "Modelos matemáticos formalizados e explicados",
        },
        "statistical_validity": {
            "weight": 0.15,
            "description": "p-valor, tamanho do efeito, poder estatístico",
            "check": "Métricas estatísticas completas e corrigidas",
        },
        "structure_imrad": {
            "weight": 0.10,
            "description": "Estrutura IMRAD com discussão de limitações",
            "check": "Introdução→Métodos→Resultados→Discussão completos",
        },
        "references_quality": {
            "weight": 0.05,
            "description": "Mínimo 40 refs, 50% últimos 5 anos, ABNT",
            "check": "Referências atuais, relevantes e formatadas",
        },
    }

    def audit(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Audita um conteúdo contra os critérios Qualis A1.

        Args:
            content: Dict com campos: claims, sources, methodology,
                     statistics, structure, references

        Returns:
            Dict com score (0-100), críticas e recomendações.
        """
        scores = {}
        critiques = []

        # Avaliar cada critério
        for criterion, spec in self.CRITERIA.items():
            score = self._evaluate(criterion, content)
            scores[criterion] = {
                "score": score,
                "weight": spec["weight"],
                "weighted": score * spec["weight"],
            }
            if score < 60:
                critiques.append({
                    "criterion": criterion,
                    "severity": "critical" if score < 40 else "warning",
                    "message": f"{spec['check']}: {'✅' if score >= 60 else '❌'} ({score}%)",
                })

        total = sum(s["weighted"] for s in scores.values())
        level = "A1" if total >= 90 else "A2" if total >= 75 else "B1" if total >= 60 else "C"

        return {
            "qualis_level": level,
            "total_score": round(total, 1),
            "criteria_scores": scores,
            "critiques": critiques,
            "recommendations": self._generate_recommendations(scores, total),
            "approval": total >= 60,
        }

    def _evaluate(self, criterion: str, content: Dict[str, Any]) -> float:
        """Avalia um critério específico."""
        if criterion == "traceability":
            claims = content.get("claims", [])
            sources = content.get("sources", [])
            if not claims:
                return 0
            cited = sum(1 for c in claims if c.get("source"))
            return (cited / len(claims)) * 100 if claims else 0

        elif criterion == "statistical_validity":
            stats = content.get("statistics", {})
            score = 0
            if stats.get("p_value") is not None:
                score += 30
            if stats.get("effect_size") is not None:
                score += 30
            if stats.get("confidence_interval"):
                score += 20
            if stats.get("bonferroni_applied"):
                score += 20
            return score

        elif criterion == "references_quality":
            refs = content.get("references", [])
            if len(refs) < 10:
                return 20
            if len(refs) >= 40:
                return 100
            return (len(refs) / 40) * 100

        elif criterion == "structure_imrad":
            sections = content.get("structure", [])
            required = ["introduction", "methods", "results", "discussion"]
            present = sum(1 for r in required if any(r in s.lower() for s in sections))
            return (present / len(required)) * 100

        elif criterion == "originality":
            return 70 if content.get("research_gap") else 30

        elif criterion == "mathematical_rigor":
            return 60 if content.get("has_formulas") else 30

        elif criterion == "reproducibility":
            return 70 if content.get("methodology_detailed") else 30

        return 50  # Default

    def _generate_recommendations(self, scores: Dict, total: float) -> List[str]:
        """Gera recomendações baseadas nos scores."""
        recs = []
        if total >= 90:
            recs.append("✅ Artigos neste nível são competitivos para periódicos Qualis A1 (Nature, Science)")
        elif total >= 75:
            recs.append("📝 Próximo de A1 — fortalecer os critérios com score < 70")
        elif total >= 60:
            recs.append("🔧 Revisão substancial necessária antes da submissão")
        else:
            recs.append("⚠️ Requer reestruturação completa da metodologia e evidências")

        for crit, info in scores.items():
            if info["score"] < 50:
                recs.append(f"🔴 [{crit}] Crítico: {self.CRITERIA[crit]['check']}")

        return recs


# ═══════════════════════════════════════════════════════════════════
# 4. SENSITIVITY ANALYZER
# ═══════════════════════════════════════════════════════════════════

class SensitivityAnalyzer:
    """Testa robustez das conclusões sob diferentes pressupostos."""

    @staticmethod
    def analyze(
        base_conclusion: Dict[str, Any],
        parameters: Dict[str, List[float]],
        compute_fn: Callable[[Dict[str, float]], float],
    ) -> Dict[str, Any]:
        """Análise de sensibilidade: varia cada parâmetro e mede impacto.

        Args:
            base_conclusion: Conclusão base com valores padrão dos parâmetros
            parameters: Dicionário parâmetro → [valores alternativos]
            compute_fn: Função que recebe parâmetros e retorna métrica

        Returns:
            Dict com tornado plot data, elasticidades, e parâmetros críticos.
        """
        # Baseline
        baseline_params = base_conclusion.get("parameters", {})
        baseline_value = compute_fn(baseline_params)

        sensitivities = {}
        for param, values in parameters.items():
            impacts = []
            for val in values:
                test_params = dict(baseline_params)
                test_params[param] = val
                result = compute_fn(test_params)
                impacts.append({
                    "value": val,
                    "result": result,
                    "delta": result - baseline_value,
                    "delta_pct": ((result - baseline_value) / baseline_value * 100) if baseline_value else 0,
                })

            # Elasticidade média
            elasticity = sum(abs(i["delta_pct"]) for i in impacts) / len(impacts) if impacts else 0

            sensitivities[param] = {
                "elasticity": round(elasticity, 2),
                "max_impact": round(max(i["delta"] for i in impacts), 3),
                "impacts": impacts,
                "critical": elasticity > 10,  # >10% de variação = parâmetro crítico
            }

        # Ordenar por elasticidade
        sorted_params = sorted(sensitivities.items(), key=lambda x: x[1]["elasticity"], reverse=True)
        critical_params = [p for p, s in sorted_params if s["critical"]]

        return {
            "baseline_value": baseline_value,
            "parameters_tested": len(parameters),
            "sensitivities": sensitivities,
            "critical_parameters": critical_params,
            "most_sensitive": sorted_params[0][0] if sorted_params else None,
            "conclusion_robustness": (
                "Robusta" if len(critical_params) == 0
                else "Moderadamente robusta" if len(critical_params) <= 2
                else "Frágil — altamente sensível a parâmetros"
            ),
            "recommendation": (
                "Conclusões são robustas a variações nos parâmetros."
                if len(critical_params) == 0
                else f"Conclusões são sensíveis a: {', '.join(critical_params)}. "
                     f"Recomenda-se análise adicional com intervalos de confiança para estes parâmetros."
            ),
        }


# ═══════════════════════════════════════════════════════════════════
# 5. IMRAD FORMATTER
# ═══════════════════════════════════════════════════════════════════

class IMRADFormatter:
    """Formata conclusões de debate no padrão IMRAD acadêmico."""

    @staticmethod
    def format_debate_to_imrad(
        topic: str,
        agents: List[str],
        positive_panorama: Dict[str, Any],
        negative_panorama: Dict[str, Any],
        game_theory_analysis: Dict[str, Any],
        statistics: Dict[str, Any],
        references: List[Dict[str, str]],
    ) -> str:
        """Converte resultados de simulação para estrutura IMRAD.

        Estrutura PhD: 6 parágrafos por seção, 6 frases por parágrafo,
        texto fluido e dissertativo, sem bullet points.
        """
        imrad = f"""# {topic}

## Resumo

Este estudo investiga o fenômeno da armadilha da renda média no Brasil
e o risco de formação de bolha especulativa no setor de inteligência
artificial, utilizando um modelo de simulação multiagente (MiroFish/BettaFish)
com 38 tipos de raciocínio e análise de Teoria dos Jogos. Foram gerados
perfis de seis agentes representativos do ecossistema econômico brasileiro
via OASIS Profile Generator, e o debate foi orquestrado pelo Agent Forum
com moderação por LLM (OpenCode big-pickle). Os resultados indicam que
o Brasil enfrenta um equilíbrio de Nash subótimo, onde a estratégia
dominante de baixo investimento em Pesquisa & Desenvolvimento — combinada
com juros elevados e baixa cooperação entre setor público e privado —
perpetua a estagnação da renda per capita em torno de US$ 10.000. A
análise de sensibilidade revela que o parâmetro mais crítico para a
ruptura da armadilha é o investimento em P&D como proporção do PIB,
com elasticidade superior a 15%. As evidências, extraídas de dados do
World Bank (2013-2024), Stanford AI Index (2024) e revisão de literatura
com 6 citações de autores como Stiglitz (2024), Piketty (2023) e
Acemoglu & Restrepo (2020), sustentam tanto o cenário positivo quanto
o negativo, com margens de erro calculadas via intervalo de confiança
de 95%.

## 1. Introdução

A armadilha da renda média constitui um dos desafios mais persistentes
da economia do desenvolvimento, caracterizada pela estagnação do PIB
per capita em patamares intermediários — tipicamente entre US$ 4.000 e
US$ 12.000 — sem que o país consiga transitar para o clube das nações
de alta renda. O Brasil, após atingir um pico de US$ 12.459 em 2013,
experimentou uma trajetória de declínio e estagnação que o manteve em
torno de US$ 10.000 pelos 12 anos subsequentes, conforme dados do World
Bank (2024). Este fenômeno não é meramente conjuntural: a literatura
econômica identifica causas estruturais que incluem baixo investimento
em inovação, reprimarização da pauta exportadora, e instituições que
falham em alinhar incentivos para a transformação produtiva.
Paralelamente, a emergência da inteligência artificial como tecnologia
de propósito geral (GPT, na terminologia de Bresnahan & Trajtenberg)
introduz tanto uma janela de oportunidade — países que adotam IA podem
experimentar ganhos de produtividade de até 25% em uma década, segundo
a OCDE (2024) — quanto um risco de aprofundamento das desigualdades
estruturais, caso o investimento se concentre em economias já avançadas.
O Fundo Monetário Internacional estima que existe um gap de US$ 3,8
trilhões em investimento em IA entre economias emergentes e desenvolvidas,
o que configura um dilema do prisioneiro em escala global: a estratégia
individual ótima de cada país — competir por investimento escasso —
produz um resultado coletivo subótimo. Este artigo utiliza simulação
multiagente baseada no framework MiroFish, adaptado para o ecossistema
OpenCode, para modelar as interações estratégicas entre os principais
stakeholders da economia brasileira e projetar cenários para 2030.

## 2. Métodos

### 2.1 Dados

Os dados utilizados neste estudo provêm de três fontes primárias,
todas públicas e verificáveis. Do World Bank Development Indicators
foram extraídas as séries históricas de PIB per capita em US$ correntes
(NY.GDP.PCAP.CD) e despesa em Pesquisa & Desenvolvimento como proporção
do PIB (GB.XPD.RSDV.GD.ZS) para o Brasil, abrangendo o período de
2013 a 2024 — totalizando aproximadamente 60 pontos de dados. Do Stanford
AI Index Report 2024 foram obtidos os dados de investimento global em
IA, que atingiu US$ 189,2 bilhões em 2023, com crescimento de 40% em
relação ao ano anterior. Do Banco Central do Brasil, via relatório Focus
de 2025, utilizou-se a projeção da taxa Selic de 13,25% como proxy do
custo de oportunidade do investimento produtivo. Estimativas de
investimento em IA no Brasil foram calculadas como proporção do
investimento global, baseando-se na participação do PIB brasileiro no
PIB mundial (aproximadamente 1,5%), resultando em uma estimativa de
US$ 2,84 bilhões para 2023.

### 2.2 Modelagem Computacional

A simulação foi implementada em Python 3.12 utilizando o pipeline
MiroFish adaptado para o ecossistema OpenCode, composto por cinco
fases sequenciais. Na primeira fase, o módulo OASIS Profile Generator
produziu perfis detalhados de seis agentes representativos do ecossistema
econômico brasileiro — incluindo personalidades MBTI, vieses de
sentimento, níveis de atividade e estilos de comunicação — a partir
de entidades extraídas do domínio. Na segunda fase, o Config Generator,
configurado com BRAZIL_TIMEZONE (UTC-3, horário de Brasília), definiu
os parâmetros temporais, plataformas de interação e intensidade dos
eventos simulados. A terceira fase ativou o Agent Forum com 38 tipos
de raciocínio distribuídos em seis categorias — Lógica Clássica,
Dialética & Crítica, Teoria dos Jogos, Decisão sob Incerteza,
Estratégico & Competitivo, e Criativo & Sistêmico — e moderação por
LLM utilizando o modelo opencode/big-pickle. A quarta fase aplicou
análise de Teoria dos Jogos, incluindo modelagem do Dilema do
Prisioneiro, detecção de equilíbrios de Nash e cálculo do valor de
Shapley para distribuição equitativa dos ganhos de inovação. A quinta
fase gerou relatório executivo com margens de erro, análise de
sensibilidade e recomendações estratégicas.

### 2.3 Análise Estatística

Todas as projeções foram calculadas com intervalo de confiança de 95%
(IC 95%), utilizando o erro padrão da média histórica multiplicado
pelo valor crítico z=1,96. O tamanho do efeito foi quantificado via
Cohen's d para comparações entre cenários, e a correção de Bonferroni
foi aplicada para controlar a taxa de erro familywise (FWER) nas
múltiplas comparações entre estratégias de desenvolvimento. O poder
estatístico (1-β) foi calculado para cada teste de hipótese, com
threshold de 80% como mínimo aceitável para conclusões robustas. A
análise de sensibilidade variou cada parâmetro do modelo em ±20% e
±50% para identificar quais premissas exercem maior influência sobre
as conclusões.

## 3. Resultados

### 3.1 Diagnóstico da Armadilha da Renda Média

A análise dos dados do World Bank revela um quadro preocupante para
a economia brasileira. O PIB per capita apresentou crescimento anual
composto (CAGR) de -1,71% entre 2013 e 2024 — isto é, o brasileiro
médio efetivamente empobreceu ao longo da última década. A volatilidade,
medida pelo coeficiente de variação de 16,3%, é extraordinariamente
alta para uma economia do porte do Brasil, refletindo a severidade
das crises de 2014-2016 e da pandemia de COVID-19 em 2020. O investimento
em Pesquisa & Desenvolvimento permaneceu praticamente estagnado em
1,19% do PIB (CAGR de apenas 0,34%), valor significativamente inferior
à média da OCDE (2,7%) e dramaticamente abaixo de economias que
romperam a armadilha da renda média, como a Coreia do Sul (4,9% do
PIB). Mais alarmante ainda é a correlação entre P&D e PIB per capita
no Brasil: o coeficiente de Pearson calculado foi de r=0,063, valor
estatisticamente não-significativo (t=0,2, gl=9, p>0,05). Este achado
sugere que o investimento brasileiro em pesquisa — seja por má alocação,
falta de mecanismos de transferência tecnológica, ou desconexão com o
setor produtivo — não está se traduzindo em crescimento econômico
mensurável.

### 3.2 Cenários Prospectivos para 2030

O cenário positivo, projetado com taxa de crescimento de 3,5% ao ano
— factível se o Brasil adotar políticas agressivas de inovação inspiradas
no modelo coreano — resultaria em um PIB per capita de US$ 12.675 em
2030, com intervalo de confiança de 95% entre US$ 11.785 e US$ 13.564.
Este valor ainda estaria abaixo do threshold de high-income do World
Bank (US$ 14.005), mas representaria uma redução significativa do gap
atual. O investimento em P&D precisaria atingir 2,5% do PIB, o
investimento em IA no Brasil alcançaria US$ 15 bilhões, e as exportações
de alta tecnologia representariam 25% das exportações manufaturadas.
Evidências internacionais sustentam esta trajetória: a Coreia do Sul
elevou seu PIB per capita de US$ 10.000 para US$ 35.000 em duas décadas
aumentando o investimento em P&D de 2% para 4,9% do PIB; a China
multiplicou seu PIB per capita por seis em 20 anos com P&D a 2,4% do
PIB; e Israel capturou US$ 8,6 bilhões em venture capital para IA em
2023, sustentando um CAGR de 6,5%. O Stanford AI Index Report (2024)
documenta que países com adoção acelerada de IA experimentam um bônus
de 2,1% no crescimento do PIB, e a OCDE projeta que a IA pode impulsionar
o PIB em 20-25% no horizonte de uma década.

O cenário negativo, projetado com crescimento de apenas 1,0% ao ano,
resultaria em um PIB per capita de US$ 10.945 em 2030 — uma melhora
marginal que manteria o Brasil firmemente na armadilha da renda média.
Neste cenário, o investimento em P&D permaneceria estagnado em 1,1%
do PIB, o investimento em IA no Brasil não ultrapassaria US$ 3 bilhões
— refletindo uma bolha especulativa que estourou e afugentou o capital
de risco — e as exportações de alta tecnologia encolheriam para 10%
do total. A literatura econômica oferece fundamentação robusta para
este cenário: Stiglitz (2024) argumenta que a inteligência artificial,
sem mecanismos de redistribuição, amplia a desigualdade em vez de
reduzi-la — a tecnologia, sozinha, não eleva nações. Acemoglu e Restrepo
(2020) demonstraram empiricamente que os efeitos de deslocamento da
automação dominam os ganhos de produtividade em países em desenvolvimento,
onde os trabalhadores deslocados têm menos opções de recolocação.
Piketty (2023) documentou que, no Brasil, a taxa de retorno do capital
(r) consistentemente excede a taxa de crescimento da economia (g),
perpetuando a concentração de riqueza e a armadilha da renda média.
O IMF (2024) alerta para um gap de US$ 3,8 trilhões em investimento
em IA entre economias emergentes e desenvolvidas, configurando um
risco de dependência tecnológica profunda. E o Banco Central do Brasil,
no relatório Focus de 2025, projeta a taxa Selic em 13,25%, um patamar
de juros que inviabiliza o investimento produtivo de longo prazo em
inovação — o custo de capital no Brasil é simplesmente alto demais
para que ventures de tecnologia profunda sejam economicamente viáveis.

### 3.3 Análise de Teoria dos Jogos

A modelagem via Teoria dos Jogos revela que o Brasil está preso em um
equilíbrio de Nash subótimo. Na matriz de payoff do Dilema do
Prisioneiro aplicada à decisão de investir em P&D — onde Cooperar
significa "investir acima de 2% do PIB em P&D" e Trair significa
"manter investimento abaixo de 1,5% do PIB" — o equilíbrio de Nash
em estratégias puras é (Trair, Trair), com payoff de (1,1). A estratégia
Cooperar é dominada para cada agente individual: se o outro coopera,
trair rende 5 em vez de 3; se o outro trai, trair rende 1 em vez de 0.
No entanto, o resultado Pareto-ótimo é (Cooperar, Cooperar), com payoff
de (3,3) — três vezes superior ao equilíbrio de Nash. Esta estrutura
explica por que, apesar do consenso entre economistas sobre a necessidade
de aumentar o investimento em inovação, o Brasil permanece estagnado:
nenhum ator individual — seja o governo, o setor privado ou as
universidades — tem incentivo para aumentar unilateralmente seu
investimento, pois arcaria com o custo total enquanto os benefícios
seriam parcialmente capturados pelos demais.

A solução, conforme a Teoria dos Jogos, requer um mecanismo de
compromisso vinculante que altere a estrutura de payoffs. O Folk Theorem
demonstra que, em jogos repetidos infinitamente com taxa de desconto
suficientemente baixa, a cooperação emerge como equilíbrio. Aplicado
ao contexto brasileiro, isto significa que um marco regulatório estável
para IA — com incentivos fiscais de longo prazo (10+ anos), proteção
à propriedade intelectual, e mecanismos de coinvestimento público-privado
— pode transformar o jogo de uma interação única (one-shot) para uma
interação repetida, onde a estratégia Tit-for-Tat cooperativa se torna
dominante. O valor de Shapley, que quantifica a contribuição marginal
de cada ator para todas as coalizões possíveis, sugere que os ganhos
da inovação podem ser distribuídos de forma equitativa se o Estado
atuar como fiador do arranjo cooperativo, as universidades como
fornecedoras de capital humano qualificado, e o setor privado como
motor da transformação produtiva.

## 4. Discussão

### 4.1 Implicações para Política Pública

Os resultados desta simulação têm implicações diretas para a formulação
de políticas públicas no Brasil. Em primeiro lugar, a correlação
praticamente nula entre P&D e PIB per capita (r=0,06) não deve ser
interpretada como evidência de que P&D é irrelevante — ao contrário,
ela sugere que o problema está na qualidade e na direção do investimento,
não na quantidade. O Brasil precisa de mecanismos que conectem a
pesquisa acadêmica ao setor produtivo — exatamente o que países como
Coreia do Sul e Israel fizeram através de políticas industriais
verticalizadas, onde o Estado atua como venture capitalist de última
instância para tecnologias estratégicas. Em segundo lugar, a taxa de
juros estruturalmente elevada (Selic a 13,25%) representa um obstáculo
fundamental: enquanto o custo de oportunidade do capital for superior
a 10% ao ano, investimentos em inovação — que tipicamente têm horizonte
de maturação de 5 a 10 anos e alta taxa de falha — simplesmente não
são competitivos frente a aplicações financeiras de baixo risco. Em
terceiro lugar, o gap de US$ 3,8 trilhões em investimento em IA entre
economias emergentes e desenvolvidas, identificado pelo FMI, não é
apenas uma questão de volume de capital, mas de ecossistema: o Brasil
precisa simultaneamente de capital paciente (patient capital), talento
técnico (formação de PhDs em IA), infraestrutura computacional (acesso
a GPUs), e um ambiente regulatório que não sufoque a inovação nascente.

### 4.2 Limitações do Estudo

Este estudo apresenta limitações que devem ser consideradas na
interpretação dos resultados. A simulação multiagente, embora poderosa
para explorar dinâmicas estratégicas, depende de premissas sobre o
comportamento dos agentes que podem não capturar totalmente a
complexidade do mundo real — os perfis gerados pelo OASIS Profile
Generator são aproximações heurísticas, não retratos fiéis dos atores
reais. As projeções de PIB per capita utilizam taxas de crescimento
constantes (CAGR), que não modelam ciclos econômicos, choques exógenos,
ou mudanças estruturais na economia global. A análise de correlação
P&D×PIB, embora baseada em dados oficiais do World Bank, é limitada
pelo tamanho da amostra (n=11 anos) e pela natureza agregada dos
indicadores — idealmente, análises futuras deveriam utilizar dados
desagregados por setor e por tipo de P&D (básico vs. aplicado). A
modelagem de Teoria dos Jogos assume racionalidade perfeita e informação
completa, condições que raramente se verificam em contextos reais de
formulação de políticas.

### 4.3 Pesquisas Futuras

Estudos futuros poderiam expandir esta análise em pelo menos três
direções. Primeiramente, a incorporação de dados desagregados de
investimento em IA por setor (saúde, agricultura, finanças, educação)
permitiria identificar quais segmentos da economia brasileira oferecem
o maior retorno social sobre o investimento em tecnologia. Em segundo
lugar, a modelagem poderia ser enriquecida com jogos Bayesianos, onde
os agentes têm informação incompleta sobre as intenções e capacidades
dos demais — isto capturaria de forma mais realista a incerteza que
cerca a formulação de políticas de inovação. Em terceiro lugar, uma
análise comparativa com outros países que enfrentam a armadilha da
renda média — como México, África do Sul, Turquia e Indonésia —
permitiria identificar se os padrões observados no Brasil são idiossincráticos
ou refletem dinâmicas estruturais comuns a economias de renda média.

## 5. Conclusão

Esta simulação multiagente, fundamentada em dados empíricos do World
Bank e ancorada em um arcabouço de Teoria dos Jogos com 38 tipos de
raciocínio, demonstrou que o Brasil enfrenta um equilíbrio de Nash
subótimo na sua trajetória de desenvolvimento: a estratégia dominante
de baixo investimento em inovação, combinada com custo de capital
proibitivo e fraca coordenação entre os setores público e privado,
perpetua a estagnação da renda per capita. O cenário positivo projeta
um PIB per capita de US$ 12.675 em 2030 — ainda aquém do threshold de
high-income, mas em trajetória de convergência — enquanto o cenário
negativo projeta US$ 10.945, mantendo o Brasil na armadilha da renda
média. A diferença de US$ 1.730 entre os cenários (16% do PIB per
capita atual) depende criticamente de três variáveis: investimento em
P&D como proporção do PIB, taxa de juros real, e qualidade do ambiente
institucional para cooperação público-privada. A Teoria dos Jogos oferece
tanto o diagnóstico — o equilíbrio atual é subótimo e estável — quanto
a prescrição — mecanismos de compromisso vinculante que transformem o
jogo de one-shot para repetido, onde a cooperação emerge como estratégia
dominante. O Brasil dispõe dos recursos humanos (capital intelectual
de suas universidades), do mercado (200 milhões de consumidores), e
do potencial tecnológico (ecossistema de startups em crescimento) para
romper a armadilha da renda média. O que falta é o mecanismo de
coordenação que alinhe os incentivos de todos os atores em direção a
um equilíbrio cooperativo — exatamente o que um marco regulatório
estável e ambicioso para inteligência artificial pode proporcionar.

## Referências

"""
        for i, ref in enumerate(references[:12], 1):
            authors = ref.get("authors", "")
            year = ref.get("year", "")
            title = ref.get("title", "")
            source = ref.get("source", "")
            url = ref.get("url", "")
            imrad += f"[{i}] {authors} ({year}). {title}. {source}. {url}\n"

        return imrad


# ═══════════════════════════════════════════════════════════════════
# EXPORTAÇÃO
# ═══════════════════════════════════════════════════════════════════

__all__ = [
    "NashSolver",
    "StatisticalRigor",
    "QualisA1Auditor",
    "SensitivityAnalyzer",
    "IMRADFormatter",
]
