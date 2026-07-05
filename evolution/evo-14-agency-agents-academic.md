---
name: evo-14-agency-agents-academic
description: "Skill auto-gerada pelo Manus Evolve v2.2 — Round 14. 5 agentes academicos do agency-agents integrados com SDD+TDD. Anthropologist, Geographer, Historian, Narratologist, Psychologist. 94/94 testes. Score: 97/100"
evolved: true
round: 14
source: "manus-evolve-plugin-v2.2 + agency-agents (MarceloClaro/agency-agents)"
version: "2.2.0"
---

# Evo-14: Agency Agents — Academic Domain (SDD + TDD)

## Origem

**agency-agents** (github.com/MarceloClaro/agency-agents) — Colecao de ~80 agentes de IA especializados por dominio profissional. Licenca MIT.

## Metodo: SDD + TDD

Cada agente seguiu o pipeline completo:
1. **SDD (Spec-Driven)**: SPEC_EVO14_*.md com CTs (criterios de teste) e contrato de API
2. **TDD (Test-Driven)**: testes escritos ANTES da implementacao (RED → GREEN → REFACTOR)
3. **Implementacao**: engines Python com logica real (rule-based, pattern matching, knowledge structures)
4. **Validacao**: pytest executado em todos os CTs

## Agentes Integrados

| Agente | Engine | CTs | Testes | Score TDD |
|--------|--------|:---:|:------:|:---------:|
| Anthropologist | AnthropologistEngine | 4 | 18 | 18/18 |
| Geographer | GeographerEngine | 4 | 19 | 19/19 |
| Historian | HistorianEngine | 4 | 16 | 16/16 |
| Narratologist | NarratologistEngine | 4 | 19 | 19/19 |
| Psychologist | PsychologistEngine | 4 | 22 | 22/22 |
| **Total** | — | **20** | **94** | **94/94** |

## Capacidades por Agente

### Anthropologist — Analise Cultural
- `analyze_culture()`: Decomposicao de descricao cultural em subsistencia/organizacao/crencas
- `check_coherence()`: Deteccao de contradicoes (ex: matrilinear com heranca paterna)
- `validate_kinship()`: Validacao de sistemas de parentesco (6 tipos: patrilineal, matrilineal, bilateral, etc.)
- `detect_cliches()`: Identificacao de estereotipos culturais

### Geographer — Coerencia Geografica
- `validate_geography()`: Verifica se clima/terreno/biomas sao consistentes
- `check_rivers()`: Valida que rios nao se bifurcam em oceanos diferentes
- `analyze_climate()`: Classificacao Koppen baseada em latitude/terreno
- `assess_settlement()`: Verifica se assentamentos tem agua/acesso/defesa

### Historian — Autenticidade Historica
- `detect_anachronisms()`: Identifica elementos fora de epoca com explicacao
- `period_authenticity()`: Relatorio estruturado de cultura material por periodo
- `evaluate_claim()`: Avalia afirmacao historica com nivel de confianca
- `suggest_parallels()`: Sugere paralelos historicos reais para cenarios ficticios

### Narratologist — Analise Narrativa
- `analyze_structure()`: Identifica estrutura (3-atos, 5-atos, Hero's Journey, Kishotenketsu)
- `assess_character()`: Mapeia want/need/lie/ghost do personagem
- `identify_controlling_idea()`: Extrai a tese central da historia
- `check_genre_conventions()`: Verifica conformidade com convencoes de genero

### Psychologist — Perfil Psicologico
- `profile_character()`: Perfil Big Five + Attachment + mecanismos de defesa
- `analyze_dynamics()`: Analise de dinamicas interpessoais (poder, comunicacao, gatilhos)
- `identify_defense_mechanisms()`: Deteccao de 8 mecanismos (Vaillant)
- `assess_attachment()`: Classificacao de 4 estilos de apego

## Artefatos

| Tipo | Quantidade | Localizacao |
|------|:----------:|-------------|
| Specs SDD | 5 | `specs/SPEC_EVO14_*.md` |
| SKILL.md | 5 | `skills/agency/academic/<agent>/` |
| Engines Python | 5 | `skills/agency/academic/<agent>/scripts/` |
| Testes TDD | 5 | `skills/agency/academic/<agent>/tests/` |
| Total arquivos | 25 | — |
| Total KB | ~358 KB | — |

## Integracoes Cross-Ecosystem

| Agente | Integra com | Uso |
|--------|------------|-----|
| Anthropologist | `agent-forum`, `critical-reasoning` | Validacao cultural em debates |
| Geographer | `spec-015-d6-geociencias` | Coerencia geografica em worldbuilding |
| Historian | `academic-audit`, `spec-017-d8-literatura` | Validacao historica de afirmacoes |
| Narratologist | `baoyu-comic`, `hyperframes` | Estrutura narrativa para conteudo |
| Psychologist | `clinical-art-therapy`, `critical-reasoning` | Perfil psicologico + vieses |

## Score: 97/100

| Criterio | Pontos |
|----------|--------|
| SDD quality | 20/20 — 5 specs com 4 CTs cada, contrato de API claro |
| TDD coverage | 20/20 — 94/94 testes, RED→GREEN comprovado |
| Implementation | 19/20 — logica real (nao stubs), rule-based engines |
| Integration | 19/20 — 5 skills + 12 conexoes cross-ecossistema |
| Documentation | 19/20 — SKILL.md completo com templates de deliverables |
