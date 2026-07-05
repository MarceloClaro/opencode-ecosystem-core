# SPEC-081: Research Skills Implementation Framework — Módulos Python para Habilidades de Pesquisa

**Status:** Active
**Versão:** 1.0.0
**Data:** 2026-07-03
**Categoria:** Implementação / Pesquisa
**Dimensão:** multi (teoria_jogos, temporalidade, populacao, paradigmas, metodos, raciocinio, niveis_analise)
**Palavras-chave:** research-skills, game-theory, temporal-population, theoretical-empirical, logical-multiscale, python-modules

---

## 1. Problema

O R35 (SPEC-080) criou a ponte semântica entre skills e scanners, tornando 58/58 oportunidades epistêmicas viáveis. No entanto, as **16 skills de pesquisa existentes** possuíam apenas `SKILL.md` descritivos — **nenhuma implementação Python executável**. Quatro das dimensões mais estratégicas para a redução de HI e aumento da cobertura noológica permaneciam sem código-fonte:

| Dimensão | Skills Relacionadas | Cobertura Noológica |
|:---------|:--------------------|:-------------------:|
| `teoria_jogos` | game-theory | 100% (1/1) |
| `temporalidade` | temporal-population | 50% (1/2) |
| `populacao` | temporal-population | 33% (1/3) |
| `raciocinio` | logical-multiscale | 50% (1/2) |
| `niveis_analise` | logical-multiscale | 38% (3/8) |
| `paradigmas` | theoretical-empirical | 25% (1/4) |
| `metodos` | theoretical-empirical | 20% (1/5) |

## 2. Solução

Implementar **4 módulos Python** com funcionalidades de pesquisa reais, cobertos por **26 CTs** (Casos de Teste), mapeados para as dimensões acima.

### 2.1 Arquitetura dos Módulos

```
skills/research/
├── game-theory/
│   ├── SKILL.md
│   └── game_theory.py          # Nash equilibrium, payoff matrix, Pareto
├── temporal-population/
│   ├── SKILL.md
│   └── temporal_population.py  # TimeSeries, Longitudinal, Sampling
├── theoretical-empirical/
│   ├── SKILL.md
│   └── theoretical_empirical.py # Epistemologia, Confiabilidade, Efeito
└── logical-multiscale/
    ├── SKILL.md
    └── logical_multiscale.py   # Inferência, Argumentação, Multiescala
```

### 2.2 Game Theory (`teoria_jogos`)

```python
# game_theory.py — 152 lines, 6 tests

PayoffMatrix          # Matriz de payoffs 2×2 com jogadores/estratégias
NashEquilibrium       # Detecção de equilíbrio de Nash em estratégias puras
ParetoOptimality      # Verificação de optimalidade de Pareto
GameAnalyzer          # 4 jogos: Prisoner's Dilemma, Battle of Sexes, Stag Hunt, Chicken
```

**Funcionalidades:**
- `find_pure_nash()` — itera sobre pares de estratégias e detecta desvios unilaterais
- `is_pareto_optimal()` — verifica se existe alocação alternativa que melhore ambos
- `prisoners_dilemma()`, `battle_of_sexes()`, `stag_hunt()`, `chicken()` — jogos pré-definidos

### 2.3 Temporal Population (`temporalidade` + `populacao`)

```python
# temporal_population.py — 222 lines, 7 tests

TimeSeriesAnalyzer        # Média móvel, tendência, sazonalidade
LongitudinalAnalyzer      # Modelos mistos, ANOVA de medidas repetidas
SampleSizeCalculator      # Tamanho amostral (Cohen d, proporção)
PopulationGeneralizer     # Estratificação populacional
```

**Funcionalidades:**
- `moving_average()` — suavização temporal
- `detect_trend()` — regressão linear sobre índices
- `mixed_model_analysis()` — interceptos aleatórios (simplificado)
- `sample_size_t_test()` — poder estatístico via scipy.stats
- `stratified_weights()` — pesos amostrais

### 2.4 Theoretical Empirical (`paradigmas` + `metodos`)

```python
# theoretical_empirical.py — 220 lines, 6 tests

EpistemologicalClassifier   # 5 epistemologias (positivismo a pragmatismo)
ReliabilityAnalyzer         # Alpha de Cronbach
EffectSizeCalculator        # d de Cohen, r de correlação
```

**Funcionalidades:**
- `classify_by_keywords()` — classifica textos em paradigmas
- `cronbach_alpha()` — consistência interna (clamp em [0.0, 1.0])
- `cohens_d()` — tamanho de efeito entre dois grupos
- `correlation_effect_size()` — r a partir de d

### 2.5 Logical Multiscale (`raciocinio` + `niveis_analise`)

```python
# logical_multiscale.py — 265 lines, 7 tests

InferenceEngine             # Dedução, Indução, Abdução
ArgumentationValidator      # 8 tipos de falácia
MultiScaleAnalyzer          # 3 níveis: micro, meso, macro
```

**Funcionalidades:**
- `deduce()`, `induce()`, `abduce()` — inferência lógica
- `validate_argument()` — detecção de falácias (ad hominem, espantalho, etc.)
- `analyze_at_level()` — análise multi-nível

## 3. Referenciais Teóricos

| Ref | Fonte | Ano | Contribuição |
|:----|:------|:---:|:-------------|
| Nash — Equilibrium points in n-person games | *PNAS* 10.1073/pnas.36.1.48 | 1950 | Conceito de equilíbrio em teoria dos jogos |
| Cohen — Statistical power analysis | *Academic Press* | 1988 | d de Cohen e tamanho de efeito |
| Cronbach — Coefficient alpha | *Psychometrika* 10.1007/BF02310555 | 1951 | Alpha como medida de consistência interna |
| Peirce — Collected Papers (CP 5.189) | Harvard UP | 1931-1958 | Abdução, dedução e indução como modos de inferência |
| Walton — Argumentation Schemes | Cambridge UP | 2008 | Taxonomia de falácias e esquemas argumentativos |
| Kuhn — Structure of Scientific Revolutions | Chicago UP | 1962 | Paradigmas científicos e mudança epistêmica |
| Akbari et al. — Large language models and game theory | arXiv:2402.10200 | 2024 | Aplicação de LLMs em jogos estratégicos |

## 4. CTs (Casos de Teste)

### 4.1 Principal (SPEC-080 — 10 CTs)

| CT | Descrição | Resultado |
|:--:|:----------|:---------:|
| CT-01 | `paradigm_analysis` via keyword "paradigma" | ✅ |
| CT-02 | `methodology_design` via keyword "metodo" | ✅ |
| CT-03 | `interdisciplinary_synthesis` via keyword "dominio" | ✅ |
| CT-04 | `reasoning_engine` via keyword "raciocinio" | ✅ |
| CT-05 | `data_collection` via keyword "dados" | ✅ |
| CT-06 | `theoretical_integration` via keyword "teoria" | ✅ |
| CT-07 | `multi_scale_analysis` via keyword "nivel" | ✅ |
| CT-08 | `temporal_modeling` via keyword "temporal" | ✅ |
| CT-09 | `population_generalization` via keyword "populacao" | ✅ |
| CT-10 | `game_theory_modeling` via keyword "jogo" | ✅ |

### 4.2 Research Skills (26 CTs)

| CT | Módulo | Descrição | Resultado |
|:--:|:-------|:----------|:---------:|
| CT-11 | game_theory | PayoffMatrix: criação 2×2 | ✅ |
| CT-12 | game_theory | PayoffMatrix: acesso por jogador | ✅ |
| CT-13 | game_theory | NashEquilibrium: prisoners dilemma | ✅ |
| CT-14 | game_theory | NashEquilibrium: sem equilíbrio | ✅ |
| CT-15 | game_theory | ParetoOptimality: verificação | ✅ |
| CT-16 | game_theory | GameAnalyzer: jogos pré-definidos | ✅ |
| CT-17 | temporal_population | TimeSeriesAnalyzer: moving average | ✅ |
| CT-18 | temporal_population | TimeSeriesAnalyzer: detect trend | ✅ |
| CT-19 | temporal_population | LongitudinalAnalyzer: mixed model | ✅ |
| CT-20 | temporal_population | SampleSizeCalculator: t-test | ✅ |
| CT-21 | temporal_population | PopulationGeneralizer: stratified | ✅ |
| CT-22 | temporal_population | Integração sample → generalizer | ✅ |
| CT-23 | temporal_population | Dataset integrado com missing data | ✅ |
| CT-24 | theoretical_empirical | EpistemologicalClassifier: keywords | ✅ |
| CT-25 | theoretical_empirical | ReliabilityAnalyzer: cronbach alpha | ✅ |
| CT-26 | theoretical_empirical | EffectSizeCalculator: cohens d | ✅ |
| CT-27 | theoretical_empirical | EffectSizeCalculator: correlation r | ✅ |
| CT-28 | theoretical_empirical | EpistemologicalClassifier: vazio | ✅ |
| CT-29 | theoretical_empirical | ReliabilityAnalyzer: casos extremos | ✅ |
| CT-30 | logical_multiscale | InferenceEngine: deduce | ✅ |
| CT-31 | logical_multiscale | InferenceEngine: induce | ✅ |
| CT-32 | logical_multiscale | InferenceEngine: abduce | ✅ |
| CT-33 | logical_multiscale | ArgumentationValidator: validar | ✅ |
| CT-34 | logical_multiscale | ArgumentationValidator: falácias | ✅ |
| CT-35 | logical_multiscale | MultiScaleAnalyzer: analyze | ✅ |
| CT-36 | logical_multiscale | InferenceEngine: modus tollens | ✅ |

## 5. Integração com o Ecossistema

### 5.1 Cadeia de Dependências

```
PotentialityScanner           # Lê KEYWORD_TO_CAPABILITY (SPEC-080)
    │
    ▼
4 Research Skills Modules     # Implementam as funcionalidades (SPEC-081)
    │
    ▼
CognitiveDiversityScanner    # Injeta artefatos de diversidade cognitiva
    │
    ▼
NoologicalScanner             # Valida cobertura das 10 dimensões
    │
    ▼
EpistemicTopologyMapper       # Projeta ilhas, buracos e pontes epistêmicas
```

### 5.2 Skills Registry

As 4 skills foram registradas em `nexus/skills_registry.json` (20 skills de pesquisa registradas, 148 skills totais).

| Nome | Caminho | Categoria | Tests |
|:-----|:--------|:----------|:-----:|
| `game-theory` | `skills/research/game-theory/` | research | 6 |
| `temporal-population` | `skills/research/temporal-population/` | research | 7 |
| `theoretical-empirical` | `skills/research/theoretical-empirical/` | research | 6 |
| `logical-multiscale` | `skills/research/logical-multiscale/` | research | 7 |
| **Total** | | | **26** |

## 6. KPIs

| Métrica | Antes (R34) | Depois (SPEC-080) | Depois (SPEC-081) |
|:--------|:-----------:|:------------------:|:------------------:|
| Oportunidades viáveis | 0 | 58/58 | 58/58 |
| Testes total | 418 | 428 | **464** |
| Skills registradas | 16 | 16 | **20** |
| Skills totais | 144 | 144 | **148** |
| Módulos Python | — | — | **4** |
| LOC Python | — | — | **859** |
| Keywords capability | 36 | 123 | **123** |
| HI | 0.6847 | 0.6196 | 0.7326* |
| ADRs | 10 | 10 | **12** |

*HI calculado com 40 artefatos do CognitiveDiversityInjector; refino intra-injector necessário para <0.50.

## 7. Próximos Passos

1. **R36**: Diversificar CognitiveDiversityInjector para reduzir HI < 0.50
2. **R37**: Expandir cobertura noológica de 38% para > 50%
3. **SPEC-082**: Formalizar rotas de pesquisa baseadas em EPS ranking (3 rotas)
4. **CI/CD**: Integrar `test_r35_research_skills.py` ao pipeline de teste principal
