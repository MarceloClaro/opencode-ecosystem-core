"""
Debate Strategies Engine — 38 tipos de raciocínio + Teoria dos Jogos.
Integrado ao Agent Forum (P14) do ecossistema OpenCode.

Inspirado por:
- Axelrod's Evolution of Cooperation (1984)
- Nash Equilibrium & Non-Cooperative Games
- Myerson's Game Theory: Analysis of Conflict
- Kahneman & Tversky's Prospect Theory
- Habermas's Theory of Communicative Action

Cada estratégia é um padrão de raciocínio que o moderador
pode atribuir a agentes ou usar para estruturar o debate.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import random
import math

from mci.metabus import metabus


# ═══════════════════════════════════════════════════════════════════
# 38 ESTRATÉGIAS DE RACIOCÍNIO
# ═══════════════════════════════════════════════════════════════════

class ReasoningType(Enum):
    """Catálogo completo de 38 tipos de raciocínio para debates."""

    # ── LÓGICA CLÁSSICA (1-5) ──
    DEDUCTIVE = auto()           # Dedução: premissas → conclusão necessária
    INDUCTIVE = auto()           # Indução: casos específicos → generalização
    ABDUCTIVE = auto()           # Abdução: melhor explicação para evidências
    ANALOGICAL = auto()          # Analogia: estruturas similares → mesma conclusão
    SYLLOGISTIC = auto()         # Silogismo: 2 premissas → 1 conclusão

    # ── DIALÉTICA & CRÍTICA (6-10) ──
    DIALECTICAL = auto()         # Dialética: tese → antítese → síntese
    SOCRATIC = auto()            # Socrático: perguntas que expõem contradições
    CRITICAL = auto()            # Crítico: identifica falácias e vieses
    DECONSTRUCTIVE = auto()      # Desconstrutivo: expõe pressupostos ocultos
    FALSIFICATIONIST = auto()    # Popperiano: busca falsear, não confirmar

    # ── TEORIA DOS JOGOS (11-20) ──
    NASH_EQUILIBRIUM = auto()    # Equilíbrio de Nash: estratégia ótima dado oponente
    PRISONERS_DILEMMA = auto()   # Dilema do Prisioneiro: cooperação vs traição
    ZERO_SUM = auto()            # Jogo de soma zero: ganho de um = perda do outro
    TIT_FOR_TAT = auto()         # Olho por olho: coopera se cooperam, pune se traem
    STACKELBERG = auto()         # Líder-seguidor: first-mover advantage
    BARGAINING = auto()          # Barganha: divisão de recursos escassos
    COALITIONAL = auto()         # Coalizões: formação de alianças estratégicas
    EVOLUTIONARY_STABLE = auto() # ESS: estratégia que resiste a invasões
    SIGNALING = auto()           # Jogo de sinalização: informação assimétrica
    MECHANISM_DESIGN = auto()    # Design de mecanismos: regras que induzem verdade

    # ── DECISÃO SOB INCERTEZA (21-25) ──
    BAYESIAN = auto()            # Bayesiano: atualiza crenças com evidências
    MINIMAX = auto()             # Minimax: minimiza perda máxima
    EXPECTED_UTILITY = auto()    # Utilidade esperada: maximiza valor esperado
    PROSPECT_THEORY = auto()     # Prospect Theory: aversão à perda, framing
    REAL_OPTIONS = auto()        # Opções reais: valor da flexibilidade

    # ── ESTRATÉGICO & COMPETITIVO (26-30) ──
    COMPETITIVE = auto()         # Competitivo: maximiza vantagem própria
    COOPERATIVE = auto()         # Cooperativo: busca ganho mútuo
    ADVERSARIAL = auto()         # Adversarial: testa robustez do argumento oposto
    STAKEHOLDER = auto()         # Stakeholder: considera impacto em todos
    PARETO_OPTIMAL = auto()      # Pareto-ótimo: melhora sem piorar ninguém

    # ── CRIATIVO & SISTÊMICO (31-38) ──
    SYSTEMS_THINKING = auto()    # Pensamento sistêmico: interconexões e feedback
    SCENARIO_PLANNING = auto()   # Cenários: múltiplos futuros possíveis
    LATERAL = auto()             # Lateral: abordagens não-óbvias
    COUNTERFACTUAL = auto()      # Contrafactual: "e se fosse diferente?"
    FIRST_PRINCIPLES = auto()    # Primeiros princípios: reduz ao fundamental
    DESIGN_THINKING = auto()     # Design thinking: empatia → definição → ideação
    PRECAUTIONARY = auto()       # Precaução: ônus da prova no proponente
    ETHICAL = auto()             # Ético: princípios morais como constraints


# ═══════════════════════════════════════════════════════════════════
# PROMPTS DE CADA ESTRATÉGIA
# ═══════════════════════════════════════════════════════════════════

REASONING_PROMPTS: Dict[ReasoningType, str] = {
    # ── Lógica Clássica ──
    ReasoningType.DEDUCTIVE: """
[RACIOCÍNIO DEDUTIVO]
Você está usando raciocínio dedutivo. Siga estas regras:
1. Comece com premissas claras e aceitas por todos
2. Aplique regras lógicas rigorosas
3. Se as premissas são verdadeiras, a conclusão DEVE ser verdadeira
4. Explicite cada passo da cadeia lógica
5. Use estruturas "Se A → B, e B → C, então A → C"
""",

    ReasoningType.INDUCTIVE: """
[RACIOCÍNIO INDUTIVO]
Você está usando raciocínio indutivo. Siga estas regras:
1. Apresente múltiplos casos/evidências específicas
2. Identifique o padrão comum entre os casos
3. Generalize com cautela — a conclusão é provável, não certa
4. Reconheça as limitações da amostra
5. Use linguagem probabilística ("tende a", "provavelmente", "sugere que")
""",

    ReasoningType.ABDUCTIVE: """
[RACIOCÍNIO ABDUTIVO]
Você está usando raciocínio abdutivo (inferência para a melhor explicação).
1. Liste as evidências disponíveis
2. Gere múltiplas hipóteses que explicariam as evidências
3. Avalie cada hipótese por: simplicidade, poder explicativo, consistência
4. Selecione a melhor explicação (não necessariamente a única)
5. Reconheça que é uma inferência, não uma prova
""",

    ReasoningType.ANALOGICAL: """
[RACIOCÍNIO ANALÓGICO]
Você está usando raciocínio por analogia.
1. Identifique um domínio-fonte bem compreendido
2. Mapeie as similaridades estruturais com o domínio-alvo
3. Transfira insights do domínio-fonte para o alvo
4. Verifique se as diferenças não invalidam a analogia
5. Use a analogia como heurística, não como prova
""",

    ReasoningType.SYLLOGISTIC: """
[RACIOCÍNIO SILOGÍSTICO]
Você está usando silogismos.
1. Apresente uma premissa maior (universal)
2. Apresente uma premissa menor (particular)
3. Deduza a conclusão necessária
4. Verifique validade formal (não apenas verdade material)
5. Exemplo: "Todo A é B. X é A. Logo, X é B."
""",

    # ── Dialética & Crítica ──
    ReasoningType.DIALECTICAL: """
[RACIOCÍNIO DIALÉTICO]
Você está usando o método dialético (Tese → Antítese → Síntese).
1. Apresente a TESE (posição atual)
2. Desenvolva a ANTÍTESE (contradição interna ou oposição externa)
3. Proponha a SÍNTESE (superação que incorpora elementos de ambas)
4. Mostre como a síntese resolve as contradições
5. A síntese pode se tornar nova tese para próxima iteração
""",

    ReasoningType.SOCRATIC: """
[MÉTODO SOCRÁTICO]
Você está usando questionamento socrático.
1. Faça perguntas que exponham pressupostos não examinados
2. Questione definições: "O que exatamente você quer dizer com X?"
3. Busque evidências: "Quais evidências sustentam essa afirmação?"
4. Explore consequências: "Se isso for verdade, o que mais seria verdade?"
5. Examine perspectivas alternativas: "Alguém poderia ver isso de forma diferente?"
""",

    ReasoningType.CRITICAL: """
[RACIOCÍNIO CRÍTICO]
Você está usando pensamento crítico.
1. Identifique a afirmação central sendo avaliada
2. Examine as evidências apresentadas (quantidade, qualidade, relevância)
3. Detecte falácias lógicas (ad hominem, straw man, false dichotomy, etc.)
4. Avalie vieses cognitivos (confirmação, ancoragem, disponibilidade)
5. Determine o grau de confiança justificado pela evidência
""",

    ReasoningType.DECONSTRUCTIVE: """
[RACIOCÍNIO DESCONSTRUTIVO]
Você está usando análise desconstrutiva.
1. Identifique as oposições binárias no discurso (bem/mal, natural/artificial)
2. Mostre como um termo da oposição é privilegiado sobre o outro
3. Exponha os pressupostos metafísicos que sustentam a hierarquia
4. Revele como o termo "inferior" é na verdade constitutivo do "superior"
5. Proponha uma leitura que subverta a hierarquia original
""",

    ReasoningType.FALSIFICATIONIST: """
[RACIOCÍNIO FALSIFICACIONISTA]
Você está usando a abordagem de Popper.
1. Reformule a afirmação em termos falseáveis
2. Projete um teste que poderia refutar a afirmação
3. Busque ativamente contraexemplos
4. Se a afirmação resiste à falsificação, ganha corroboração (não verificação)
5. Distinga entre o que é científico (falseável) e o que não é
""",

    # ── TEORIA DOS JOGOS ──
    ReasoningType.NASH_EQUILIBRIUM: """
[TEORIA DOS JOGOS: EQUILÍBRIO DE NASH]
Você está analisando via Equilíbrio de Nash.
1. Identifique os JOGADORES e suas ESTRATÉGIAS disponíveis
2. Mapeie a MATRIZ DE PAYOFFS para cada combinação de estratégias
3. Encontre o equilíbrio: onde nenhum jogador se beneficia mudando unilateralmente
4. Analise se o equilíbrio é Pareto-eficiente ou subótimo
5. Discuta: existem múltiplos equilíbrios? Estratégias mistas?
""",

    ReasoningType.PRISONERS_DILEMMA: """
[TEORIA DOS JOGOS: DILEMA DO PRISIONEIRO]
Você está analisando via Dilema do Prisioneiro.
1. Identifique a estrutura: tentação de trair > recompensa mútua > punição mútua > custo do otário
2. Mostre por que a estratégia dominante individual leva a resultado pior para todos
3. Explore condições que promovem cooperação: repetição, reputação, comunicação
4. Analise cenários reais com estrutura similar (corrida armamentista, tragédia dos comuns)
5. Proponha mecanismos para alinhar incentivos individuais e coletivos
""",

    ReasoningType.ZERO_SUM: """
[TEORIA DOS JOGOS: SOMA ZERO]
Você está analisando como jogo de soma zero.
1. Determine se o conflito é realmente soma zero ou se há possibilidade de ganho mútuo
2. Se soma zero: identifique a estratégia minimax ótima
3. Analise o valor do jogo para cada jogador
4. Questione: o enquadramento soma zero é preciso ou há oportunidades de enlargar o bolo?
5. Se não é soma zero: reformule como jogo cooperativo ou de soma variável
""",

    ReasoningType.TIT_FOR_TAT: """
[TEORIA DOS JOGOS: TIT-FOR-TAT]
Você está analisando via estratégia Tit-for-Tat (Axelrod).
1. Comece cooperando (nice)
2. Copie a jogada anterior do oponente (retaliatory)
3. Perdoe imediatamente se o oponente voltar a cooperar (forgiving)
4. Seja previsível e transparente (clear)
5. Analise: esta estratégia funciona em interações repetidas? Há risco de espiral de retaliação?
""",

    ReasoningType.STACKELBERG: """
[TEORIA DOS JOGOS: COMPETIÇÃO DE STACKELBERG]
Você está analisando via modelo Stackelberg (líder-seguidor).
1. Identifique quem é o LÍDER (first mover) e quem é o SEGUIDOR
2. O líder antecipa a reação ótima do seguidor e otimiza sua estratégia
3. Calcule o equilíbrio de Stackelberg (indução retroativa)
4. Compare com o equilíbrio de Nash simétrico — há vantagem do primeiro movimento?
5. Discuta: o que acontece se ambos tentam ser líderes?
""",

    ReasoningType.BARGAINING: """
[TEORIA DOS JOGOS: BARGANHA]
Você está analisando via teoria da barganha (Nash, Rubinstein).
1. Identifique o excedente a ser dividido e os pontos de desacordo (BATNA)
2. A solução de Nash: maximiza o produto dos ganhos (axiomas: Pareto, simetria, invariância)
3. Considere efeitos de paciência/impaciência (fator de desconto)
4. Analise o poder de barganha relativo: opções externas, custos de atraso
5. Proponha uma divisão que satisfaça os axiomas de justiça
""",

    ReasoningType.COALITIONAL: """
[TEORIA DOS JOGOS: FORMAÇÃO DE COALIZÕES]
Você está analisando via teoria das coalizões.
1. Identifique todos os jogadores e suas contribuições marginais
2. Calcule o valor de Shapley para cada jogador (contribuição marginal média)
3. Analise o core do jogo: quais coalizões são estáveis?
4. Examine poder de voto (índice de Shapley-Shubik, Banzhaf)
5. Discuta: quais coalizões são prováveis? Há incentivos para deserção?
""",

    ReasoningType.EVOLUTIONARY_STABLE: """
[TEORIA DOS JOGOS: ESTRATÉGIA EVOLUTIVAMENTE ESTÁVEL]
Você está analisando via teoria dos jogos evolutiva (Maynard Smith).
1. Defina a população e as estratégias em competição
2. Uma estratégia é ESS se: (a) é equilíbrio de Nash, E (b) resiste a invasão de mutantes
3. Modele a dinâmica do replicador: estratégias com maior payoff crescem na população
4. Identifique atratores evolutivos e pontos de bifurcação
5. Discuta: quais estratégias sobreviveriam no longo prazo?
""",

    ReasoningType.SIGNALING: """
[TEORIA DOS JOGOS: SINALIZAÇÃO]
Você está analisando via jogos de sinalização (Spence).
1. Identifique a assimetria de informação: quem sabe o quê?
2. O jogador informado escolhe um SINAL (custoso ou não)
3. O jogador desinformado atualiza crenças e age
4. Analise equilíbrios separadores vs. agregadores (pooling)
5. Discuta: os sinais são honestos? Quais as condições para separating equilibrium?
""",

    ReasoningType.MECHANISM_DESIGN: """
[TEORIA DOS JOGOS: DESIGN DE MECANISMOS]
Você está analisando via design de mecanismos (inverso da teoria dos jogos).
1. Defina o OBJETIVO SOCIAL desejado (eficiência, equidade, receita)
2. Modele os agentes com informações privadas e preferências
3. Projete regras que satisfaçam: compatibilidade de incentivos (truth-telling é ótimo)
4. Garanta racionalidade individual (participação voluntária)
5. Verifique: o mecanismo implementa o objetivo em equilíbrio?
""",

    # ── Decisão sob Incerteza ──
    ReasoningType.BAYESIAN: """
[RACIOCÍNIO BAYESIANO]
Você está usando inferência bayesiana.
1. Declare sua PROBABILIDADE PRÉVIA (prior) para cada hipótese
2. Apresente novas EVIDÊNCIAS e sua verossimilhança sob cada hipótese
3. Atualize para a PROBABILIDADE POSTERIOR usando o Teorema de Bayes
4. Quantifique a força da evidência (fator de Bayes)
5. Reconheça a dependência do prior — diferentes priors levam a diferentes conclusões
""",

    ReasoningType.MINIMAX: """
[RACIOCÍNIO MINIMAX]
Você está usando estratégia minimax.
1. Identifique o pior cenário possível para cada curso de ação
2. Escolha a ação que MINIMIZA a PERDA MÁXIMA (minimax)
3. Esta é uma estratégia conservadora — prioriza segurança sobre oportunidade
4. Compare com estratégias alternativas: maximax (otimista), Hurwicz (ponderada)
5. Discuta: em que contextos o minimax é apropriado? (segurança, irreversibilidade)
""",

    ReasoningType.EXPECTED_UTILITY: """
[RACIOCÍNIO POR UTILIDADE ESPERADA]
Você está usando teoria da utilidade esperada (von Neumann-Morgenstern).
1. Enumere os possíveis RESULTADOS de cada ação
2. Atribua PROBABILIDADES a cada resultado
3. Atribua UTILIDADES (valor subjetivo) a cada resultado
4. Calcule a utilidade esperada = Σ(probabilidade × utilidade)
5. Escolha a ação com maior utilidade esperada
""",

    ReasoningType.PROSPECT_THEORY: """
[PROSPECT THEORY - KAHNEMAN & TVERSKY]
Você está analisando via Prospect Theory.
1. Identifique o PONTO DE REFERÊNCIA (framing do problema)
2. As pessoas são AVESSAS À PERDA: perdas doem ~2.25× mais que ganhos equivalentes
3. As pessoas são AVESSAS AO RISCO em ganhos, mas BUSCAM RISCO em perdas
4. Efeito certeza: pessoas supervalorizam resultados certos vs. prováveis
5. Efeito framing: a forma como o problema é apresentado altera a decisão
""",

    ReasoningType.REAL_OPTIONS: """
[RACIOCÍNIO POR OPÇÕES REAIS]
Você está analisando via teoria de opções reais.
1. Identifique a FLEXIBILIDADE disponível (adiar, expandir, abandonar)
2. A incerteza + flexibilidade = VALOR DA OPÇÃO
3. Calcule o valor de esperar vs. agir agora
4. Considere irreversibilidade: se a decisão é irreversível, a opção de esperar tem mais valor
5. Discuta: qual o custo de manter a opção aberta?
""",

    # ── Estratégico & Competitivo ──
    ReasoningType.COMPETITIVE: """
[RACIOCÍNIO COMPETITIVO]
Você está advogando uma posição competitiva.
1. Defina claramente seu objetivo e o que constitui "vitória"
2. Antecipe os movimentos do oponente e prepare contra-argumentos
3. Identifique suas vantagens comparativas e explore-as
4. Use comprometimento estratégico (burning bridges) quando apropriado
5. Reconheça os limites da competição: quando a cooperação seria melhor?
""",

    ReasoningType.COOPERATIVE: """
[RACIOCÍNIO COOPERATIVO]
Você está buscando solução cooperativa.
1. Identifique interesses COMUNS além das posições divergentes
2. Busque ganhos MÚTUOS (enlarge the pie antes de dividir)
3. Proponha critérios OBJETIVOS para divisão justa
4. Use concessões recíprocas: "se você ceder em X, cedo em Y"
5. Construa confiança através de pequenos acordos incrementais
""",

    ReasoningType.ADVERSARIAL: """
[RACIOCÍNIO ADVERSARIAL]
Você está no papel de adversário (devil's advocate).
1. Busque a fraqueza MAIS FORTE do argumento oposto
2. Ataque premissas, não pessoas (ad rem, não ad hominem)
3. Teste limites: "em que condições este argumento falharia?"
4. Proponha o MELHOR contra-argumento possível, não um espantalho
5. Seu objetivo é FORTALECER o debate, não vencer a qualquer custo
""",

    ReasoningType.STAKEHOLDER: """
[RACIOCÍNIO POR STAKEHOLDERS]
Você está analisando via perspectiva dos stakeholders.
1. Mapeie TODOS os stakeholders afetados (diretos e indiretos)
2. Para cada stakeholder: interesses, poder, legitimidade, urgência
3. Considere stakeholders sem voz (futuras gerações, natureza)
4. Analise trade-offs entre stakeholders — quem ganha, quem perde?
5. Busque soluções que equilibrem interesses legítimos
""",

    ReasoningType.PARETO_OPTIMAL: """
[RACIOCÍNIO PARETO-ÓTIMO]
Você está buscando eficiência de Pareto.
1. Identifique o conjunto de resultados POSSÍVEIS
2. Um resultado é Pareto-ótimo se não é possível melhorar alguém sem piorar outro
3. Distinga Pareto-ótimo de "justo" ou "desejável" — é apenas eficiência
4. Busque melhorias de Pareto: mudanças que beneficiam alguém sem prejudicar ninguém
5. Se há conflito, use critérios adicionais (Kaldor-Hicks, Rawls)
""",

    # ── Criativo & Sistêmico ──
    ReasoningType.SYSTEMS_THINKING: """
[PENSAMENTO SISTÊMICO]
Você está usando pensamento sistêmico.
1. Mapeie o SISTEMA: elementos, interconexões, propósito
2. Identifique ciclos de FEEDBACK (reforçador e balanceador)
3. Localize ALAVANCAS: pontos onde pequenas mudanças produzem grandes efeitos
4. Cuidado com: consequências não-intencionais, demoras temporais, resistência a políticas
5. O comportamento do sistema emerge das interações, não das partes isoladas
""",

    ReasoningType.SCENARIO_PLANNING: """
[PLANEJAMENTO POR CENÁRIOS]
Você está usando planejamento de cenários.
1. Identifique as INCERTEZAS CRÍTICAS (fatores de alto impacto e alta incerteza)
2. Construa uma MATRIZ 2×2 com dois eixos de incerteza
3. Desenvolva 4 CENÁRIOS distintos e internamente consistentes
4. Para cada cenário: implicações, sinais antecipatórios, respostas robustas
5. Identifique estratégias ROBUSTAS (funcionam em todos os cenários)
""",

    ReasoningType.LATERAL: """
[PENSAMENTO LATERAL]
Você está usando pensamento lateral (de Bono).
1. Questione pressupostos fundamentais que todos aceitam
2. Gere alternativas NÃO-ÓBVIAS (quantidade antes de qualidade)
3. Use provocações (PO): ideias impossíveis que forçam novas perspectivas
4. Faça conexões entre domínios APARENTEMENTE não-relacionados
5. Suspenda julgamento durante a geração — avalie depois
""",

    ReasoningType.COUNTERFACTUAL: """
[RACIOCÍNIO CONTRAFACTUAL]
Você está usando análise contrafactual.
1. Defina claramente o evento histórico e o contrafactual alternativo
2. Especifique a intervenção MÍNIMA necessária para mudar o resultado
3. Trace a cadeia causal do contrafactual até o resultado alternativo
4. Avalie a PLAUSIBILIDADE do contrafactual (não é fantasia)
5. Use o contrafactual para extrair lições sobre causalidade
""",

    ReasoningType.FIRST_PRINCIPLES: """
[RACIOCÍNIO POR PRIMEIROS PRINCÍPIOS]
Você está usando primeiros princípios (Aristóteles, Elon Musk).
1. Reduza o problema aos seus elementos MAIS FUNDAMENTAIS
2. Questione TODOS os pressupostos — "o que sabemos com certeza?"
3. Reconstrua a solução a partir dos fundamentos, não por analogia
4. Separe FATO de CONVENÇÃO — muito do que fazemos é "porque sempre foi assim"
5. Aplique: "Se partíssemos do zero hoje, faríamos assim?"
""",

    ReasoningType.DESIGN_THINKING: """
[DESIGN THINKING]
Você está usando design thinking.
1. EMPATIA: entenda profundamente as necessidades dos afetados
2. DEFINIÇÃO: sintetize o problema central em uma frase clara
3. IDEAÇÃO: gere o máximo de soluções possíveis (brainstorm sem julgamento)
4. PROTOTIPAGEM: crie versões simplificadas para teste rápido
5. TESTE: colete feedback real e itere rapidamente
""",

    ReasoningType.PRECAUTIONARY: """
[PRINCÍPIO DA PRECAUÇÃO]
Você está aplicando o princípio da precaução.
1. Quando há ameaça de dano SÉRIO ou IRREVERSÍVEL...
2. A AUSÊNCIA de certeza científica completa NÃO justifica adiar medidas
3. O ÔNUS DA PROVA recai sobre o proponente da atividade
4. Considere alternativas MAIS SEGURAS disponíveis
5. A precaução não é paralisia — é gestão de risco sob incerteza radical
""",

    ReasoningType.ETHICAL: """
[RACIOCÍNIO ÉTICO]
Você está usando raciocínio ético.
1. Identifique o DILEMA ÉTICO central
2. Considere múltiplas perspectivas éticas:
   - Deontológica (deveres, regras, Kant)
   - Consequencialista (resultados, utilidade, Bentham/Mill)
   - Virtudes (caráter, excelência, Aristóteles)
   - Contratualista (acordo social, Rawls)
3. Aplique o teste da UNIVERSALIZAÇÃO: "e se todos fizessem isso?"
4. Considere o véu da ignorância: que regras você escolheria sem saber sua posição?
5. Justifique sua posição com princípios, não apenas intuições
""",
}


# ═══════════════════════════════════════════════════════════════════
# GAME THEORY ENGINE
# ═══════════════════════════════════════════════════════════════════

@dataclass
class PayoffMatrix:
    """Matriz de payoffs para jogos 2×2."""
    player1_strategies: List[str] = field(default_factory=lambda: ["Cooperar", "Trair"])
    player2_strategies: List[str] = field(default_factory=lambda: ["Cooperar", "Trair"])
    payoff_matrix: Dict[str, Dict[str, tuple[float, float]]] = field(default_factory=dict)

    @classmethod
    def prisoners_dilemma(cls, reward: float = 3, temptation: float = 5,
                          sucker: float = 0, punishment: float = 1) -> "PayoffMatrix":
        """Cria matriz do Dilema do Prisioneiro. T > R > P > S"""
        return cls(
            payoff_matrix={
                "Cooperar": {"Cooperar": (reward, reward), "Trair": (sucker, temptation)},
                "Trair": {"Cooperar": (temptation, sucker), "Trair": (punishment, punishment)},
            }
        )

    @classmethod
    def stag_hunt(cls, stag: float = 4, hare: float = 2) -> "PayoffMatrix":
        """Jogo Stag Hunt: coordenação com risco."""
        return cls(
            payoff_matrix={
                "Cooperar": {"Cooperar": (stag, stag), "Trair": (0, hare)},
                "Trair": {"Cooperar": (hare, 0), "Trair": (hare, hare)},
            }
        )

    def find_nash_equilibria(self) -> List[tuple[str, str]]:
        """Encontra equilíbrios de Nash puros."""
        equilibria = []
        for s1 in self.player1_strategies:
            for s2 in self.player2_strategies:
                p1, p2 = self.payoff_matrix[s1][s2]

                # Verifica se jogador 1 tem incentivo para desviar
                best_p1 = max(self.payoff_matrix[alt][s2][0] for alt in self.player1_strategies)
                best_p2 = max(self.payoff_matrix[s1][alt][1] for alt in self.player2_strategies)

                if p1 == best_p1 and p2 == best_p2:
                    equilibria.append((s1, s2))
        metabus.publish_subsystem_event(
            "gametheory",
            "nash.computed",
            {"equilibria": equilibria, "players": 2},
            source_agent="gametheory",
        )
        metabus.memory.upsert_semantic_topic(
            "gametheory.nash",
            lesson=f"Equilíbrios de Nash calculados: {equilibria}.",
            metadata={"last_equilibria": equilibria},
        )
        return equilibria


@dataclass
class ShapleyValue:
    """Calcula valor de Shapley para jogos cooperativos."""

    @staticmethod
    def calculate(players: List[str], characteristic_function: Callable[[List[str]], float]) -> Dict[str, float]:
        """Calcula o valor de Shapley para cada jogador."""
        n = len(players)
        shapley = {p: 0.0 for p in players}

        import itertools
        for player in players:
            others = [p for p in players if p != player]
            for r in range(n):
                for coalition in itertools.combinations(others, r):
                    coalition_list = list(coalition)
                    without_player = characteristic_function(coalition_list)
                    with_player = characteristic_function(coalition_list + [player])
                    marginal = with_player - without_player

                    # Número de ordens em que esta coalizão aparece
                    weight = (math.factorial(len(coalition_list)) *
                              math.factorial(n - len(coalition_list) - 1)) / math.factorial(n)
                    shapley[player] += weight * marginal

        return shapley


# ═══════════════════════════════════════════════════════════════════
# ESTRATÉGIAS DE DEBATE (AXELROD-STYLE TOURNAMENT)
# ═══════════════════════════════════════════════════════════════════

class DebateStrategy:
    """Estratégia de debate — padrão comportamental do agente."""

    def __init__(self, name: str, reasoning_types: List[ReasoningType]):
        self.name = name
        self.reasoning_types = reasoning_types
        self.cooperation_history: List[bool] = []
        self.opponent_history: List[bool] = []

    def decide_cooperation(self) -> bool:
        """Decide se coopera baseado na estratégia e histórico."""
        return True  # Default: cooperar

    def get_prompt(self, context: Dict[str, Any]) -> str:
        """Gera o prompt de raciocínio combinando os tipos."""
        prompts = [REASONING_PROMPTS.get(rt, "") for rt in self.reasoning_types]
        combined = "\n---\n".join(p for p in prompts if p)
        return f"""
[ESTRATÉGIA: {self.name}]
Contexto do debate: {context.get('topic', 'Não especificado')}
Seu papel: {context.get('role', 'Participante')}

{combined}

Com base nos tipos de raciocínio acima, contribua para o debate.
"""


class TitForTatStrategy(DebateStrategy):
    """Olho por olho com perdão."""

    def decide_cooperation(self) -> bool:
        if not self.opponent_history:
            return True
        return self.opponent_history[-1]


class GenerousTitForTatStrategy(DebateStrategy):
    """Tit-for-tat generoso: perdoa ~10% das traições."""

    def decide_cooperation(self) -> bool:
        if not self.opponent_history:
            return True
        if self.opponent_history[-1]:
            return True
        return random.random() < 0.1  # 10% de chance de perdoar


class GrimTriggerStrategy(DebateStrategy):
    """Gatilho implacável: coopera até a primeira traição, depois nunca mais."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._triggered = False

    def decide_cooperation(self) -> bool:
        if self._triggered:
            return False
        if self.opponent_history and not self.opponent_history[-1]:
            self._triggered = True
            return False
        return True


# ═══════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES PRÉ-DEFINIDAS
# ═══════════════════════════════════════════════════════════════════

# Perfis de debate com combinações de estratégias de raciocínio
DEBATE_PROFILES: Dict[str, List[ReasoningType]] = {
    "LOGICO_RIGOROSO": [
        ReasoningType.DEDUCTIVE, ReasoningType.SYLLOGISTIC,
        ReasoningType.FIRST_PRINCIPLES, ReasoningType.CRITICAL,
        ReasoningType.FALSIFICATIONIST,
    ],
    "ESTRATEGISTA": [
        ReasoningType.NASH_EQUILIBRIUM, ReasoningType.ZERO_SUM,
        ReasoningType.STACKELBERG, ReasoningType.COMPETITIVE,
        ReasoningType.MINIMAX, ReasoningType.BAYESIAN,
    ],
    "DIPLOMATA_COOPERATIVO": [
        ReasoningType.TIT_FOR_TAT, ReasoningType.COOPERATIVE,
        ReasoningType.BARGAINING, ReasoningType.PARETO_OPTIMAL,
        ReasoningType.STAKEHOLDER, ReasoningType.COALITIONAL,
    ],
    "CIENTISTA_SOCIAL": [
        ReasoningType.INDUCTIVE, ReasoningType.EVOLUTIONARY_STABLE,
        ReasoningType.SIGNALING, ReasoningType.SYSTEMS_THINKING,
        ReasoningType.SCENARIO_PLANNING, ReasoningType.MECHANISM_DESIGN,
    ],
    "FILOSOFO_DIALETICO": [
        ReasoningType.DIALECTICAL, ReasoningType.SOCRATIC,
        ReasoningType.DECONSTRUCTIVE, ReasoningType.ETHICAL,
        ReasoningType.COUNTERFACTUAL, ReasoningType.PRECAUTIONARY,
    ],
    "INOVADOR_DISRUPTIVO": [
        ReasoningType.LATERAL, ReasoningType.DESIGN_THINKING,
        ReasoningType.FIRST_PRINCIPLES, ReasoningType.REAL_OPTIONS,
        ReasoningType.ABDUCTIVE, ReasoningType.ANALOGICAL,
    ],
    "ECONOMISTA_COMPORTAMENTAL": [
        ReasoningType.PROSPECT_THEORY, ReasoningType.EXPECTED_UTILITY,
        ReasoningType.PRISONERS_DILEMMA, ReasoningType.BAYESIAN,
        ReasoningType.MECHANISM_DESIGN, ReasoningType.REAL_OPTIONS,
    ],
    "ADVOGADO_DO_DIABO": [
        ReasoningType.ADVERSARIAL, ReasoningType.CRITICAL,
        ReasoningType.FALSIFICATIONIST, ReasoningType.MINIMAX,
        ReasoningType.DECONSTRUCTIVE, ReasoningType.ZERO_SUM,
    ],
}

# Axelrod-style torneio de estratégias
TOURNAMENT_STRATEGIES: Dict[str, Callable[[], DebateStrategy]] = {
    "TitForTat": lambda: TitForTatStrategy("TitForTat", [
        ReasoningType.TIT_FOR_TAT, ReasoningType.COOPERATIVE, ReasoningType.NASH_EQUILIBRIUM
    ]),
    "GenerousTitForTat": lambda: GenerousTitForTatStrategy("GenerousTFT", [
        ReasoningType.TIT_FOR_TAT, ReasoningType.COOPERATIVE, ReasoningType.EVOLUTIONARY_STABLE
    ]),
    "GrimTrigger": lambda: GrimTriggerStrategy("GrimTrigger", [
        ReasoningType.ZERO_SUM, ReasoningType.COMPETITIVE, ReasoningType.MINIMAX
    ]),
    "AlwaysCooperate": lambda: DebateStrategy("AlwaysCooperate", [
        ReasoningType.COOPERATIVE, ReasoningType.PARETO_OPTIMAL, ReasoningType.STAKEHOLDER
    ]),
    "AlwaysDefect": lambda: DebateStrategy("AlwaysDefect", [
        ReasoningType.COMPETITIVE, ReasoningType.ZERO_SUM, ReasoningType.ADVERSARIAL
    ]),
    "RandomStrategy": lambda: DebateStrategy("Random", [
        ReasoningType.LATERAL, ReasoningType.SCENARIO_PLANNING
    ]),
}


# ═══════════════════════════════════════════════════════════════════
# META-REASONING: COMBINAÇÃO DE ESTRATÉGIAS
# ═══════════════════════════════════════════════════════════════════

class MetaReasoner:
    """Meta-raciocinador que seleciona e combina estratégias dinamicamente."""

    def __init__(self):
        self.all_types = list(ReasoningType)
        self.game_theory_types = [
            rt for rt in ReasoningType
            if rt.value >= ReasoningType.NASH_EQUILIBRIUM.value
            and rt.value <= ReasoningType.MECHANISM_DESIGN.value
        ]

    def select_for_context(self, context: Dict[str, Any]) -> List[ReasoningType]:
        """Seleciona estratégias apropriadas para o contexto."""
        selected = []

        topic = context.get("topic", "").lower()

        # Raciocínios fundamentais (sempre presentes)
        selected.append(ReasoningType.CRITICAL)
        selected.append(ReasoningType.FIRST_PRINCIPLES)

        # Contexto de conflito → Teoria dos Jogos
        if any(w in topic for w in ["conflito", "competição", "guerra", "disputa",
                                     "negociação", "acordo", "tratado"]):
            selected.append(ReasoningType.NASH_EQUILIBRIUM)
            selected.append(ReasoningType.TIT_FOR_TAT)
            selected.append(ReasoningType.BARGAINING)
            selected.append(ReasoningType.ZERO_SUM)

        # Contexto de cooperação
        if any(w in topic for w in ["cooperação", "aliança", "parceria", "colaboração",
                                     "comunidade", "coletivo"]):
            selected.append(ReasoningType.COOPERATIVE)
            selected.append(ReasoningType.COALITIONAL)
            selected.append(ReasoningType.PARETO_OPTIMAL)
            selected.append(ReasoningType.EVOLUTIONARY_STABLE)

        # Contexto de incerteza
        if any(w in topic for w in ["futuro", "previsão", "cenário", "tendência",
                                     "risco", "incerteza"]):
            selected.append(ReasoningType.BAYESIAN)
            selected.append(ReasoningType.SCENARIO_PLANNING)
            selected.append(ReasoningType.REAL_OPTIONS)
            selected.append(ReasoningType.PRECAUTIONARY)

        # Contexto ético/social
        if any(w in topic for w in ["ética", "moral", "justiça", "direitos",
                                     "dever", "responsabilidade"]):
            selected.append(ReasoningType.ETHICAL)
            selected.append(ReasoningType.STAKEHOLDER)
            selected.append(ReasoningType.SYSTEMS_THINKING)
            selected.append(ReasoningType.DIALECTICAL)

        # Contexto de inovação
        if any(w in topic for w in ["inovação", "tecnologia", "disrupção",
                                     "criatividade", "design"]):
            selected.append(ReasoningType.LATERAL)
            selected.append(ReasoningType.DESIGN_THINKING)
            selected.append(ReasoningType.ABDUCTIVE)
            selected.append(ReasoningType.REAL_OPTIONS)

        # Contexto econômico
        if any(w in topic for w in ["economia", "mercado", "financeiro", "investimento",
                                     "orçamento", "custo"]):
            selected.append(ReasoningType.EXPECTED_UTILITY)
            selected.append(ReasoningType.PROSPECT_THEORY)
            selected.append(ReasoningType.MECHANISM_DESIGN)
            selected.append(ReasoningType.STACKELBERG)

        # Garantir game theory (obrigatório)
        if not any(rt in self.game_theory_types for rt in selected):
            selected.append(ReasoningType.PRISONERS_DILEMMA)
            selected.append(ReasoningType.NASH_EQUILIBRIUM)

        selected_unique = list(dict.fromkeys(selected))  # dedup mantendo ordem
        metabus.publish_subsystem_event(
            "gametheory",
            "meta_reason.selected",
            {
                "topic": context.get("topic", ""),
                "strategies": [s.name for s in selected_unique],
            },
            source_agent="gametheory",
        )
        return selected_unique
