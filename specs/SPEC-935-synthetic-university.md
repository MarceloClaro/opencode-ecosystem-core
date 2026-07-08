# SPEC-935: Universidade Sintética Transversal

## Objetivo
Criar uma **Universidade Sintética** — um meta-subsistema multiagente que simula uma instituição acadêmica transversal completa, capaz de:
- Organizar conhecimento em **10 faculdades** (humanas, sociais, engenharia, literária/linguística, histórica, quântica, exatas, estatística, programação, interdisciplinar)
- Usar **MiroFish** como motor de descoberta combinatorial testando **10.000+ combinações** de conceitos, teorias e métodos
- Gerar **teses PhD-level** com novas correlações, combinações viáveis e descobertas originais

## Critérios de Aceitação

### CA1 — Faculdades e Domínios
- [ ] 10 faculdades implementadas, cada uma com: domínio, professores (agentes especialistas), disciplinas, métodos de pesquisa, tradições epistemológicas
- [ ] Catálogo de 100+ conceitos fundamentais por faculdade
- [ ] Matriz de adjacência interdisciplinar (pontes entre faculdades)

### CA2 — MiroFish Combinatorial Discovery Engine
- [ ] Motor combinatorial testa pares, triplas e quadruplas de conceitos entre faculdades
- [ ] MiroFish Debates para cada combinação promissora
- [ ] Rastreamento de 10.000+ combinações testadas
- [ ] Pontuação de viabilidade, novidade, coerência e impacto

### CA3 — Thesis Generator
- [ ] Gera proposições PhD-level a partir de combinações validadas
- [ ] Estrutura: hipótese → fundamentação → metodologia → correlação → conclusão
- [ ] Atribui nível acadêmico (especulação → hipótese → teoria → paradigma)
- [ ] Cita combinações específicas que levaram à descoberta

### CA4 — Correlator Interdisciplinar
- [ ] Detecta correlações entre conceitos de diferentes faculdades
- [ ] Calcula força de correlação, significância, suporte empírico
- [ ] Classifica correlações: causal, correlacional, analógica, antagônica

### CA5 — Knowledge Graph da Universidade
- [ ] Grafo de conhecimento com nós = conceitos, arestas = correlações
- [ ] Suporta consultas por faculdade, força, tipo, data
- [ ] Exportável para visualização

### CA6 — Integração com Ecossistema
- [ ] Publica eventos no MetaBus (synthetic_university.*)
- [ ] Registra ciclos evolutivos
- [ ] Agentes da universidade registrados no catálogo A2A
- [ ] Orquestrador MarceloClaro aciona universidade via `synthetic_university()`
- [ ] Mapas do ecossistema atualizados com camada `synthetic_university`

## Arquitetura

```
synthetic_university/
├── __init__.py              # Exports públicos
├── core.py                  # SyntheticUniversity orquestrador central
├── faculties.py             # 10 faculdades com conceitos, métodos, agentes
├── combinatorial_engine.py  # MiroFish Combinatorial Discovery Engine
├── correlator.py            # Correlator Interdisciplinar
├── thesis_generator.py      # Gerador de Teses PhD-level
├── knowledge_graph.py       # Grafo de conhecimento da universidade
├── agents/                  # Agentes especialistas (professores)
│   ├── __init__.py
│   ├── professor_base.py    # Classe base Professor
│   └── professors.py        # Implementações de professores por faculdade
└── curriculum.py            # Currículo sintético e disciplinas
```

## Integração com MiroFish
O MiroFish existente será estendido com:
- `MiroFishSwarm.combinatorial_explore(concepts, n_combinations)` — testa N combinações
- `MiroFishSwarm.discover_correlations(domain_a, domain_b)` — debate interdisciplinar
- Pontuação de viabilidade via `CrossValidator` (swarm × Nash × qualis)

## Métricas de Sucesso
- 10.000+ combinações testadas por ciclo
- ≥10 teses PhD-level geradas por ciclo
- ≥50 correlações interdisciplinares descobertas
- Cobertura de 100% das faculdades no grafo de conhecimento
- Testes TDD verdes (≥30 testes)
