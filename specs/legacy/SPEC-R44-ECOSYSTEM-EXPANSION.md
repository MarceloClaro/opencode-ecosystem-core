# SPEC-R44 — Ecosystem Expansion: Epistemic Diversity Injection + Topology Mapping

**Ciclo:** R44  
**Versao:** 1.0.0  
**Status:** SDD (Spec-Driven Development)  
**Fundamentacao:** Scanner Noológico (SPEC-031), Topologia Epistêmica (SPEC-054), Rupture Potential (SPEC-055), Potentiality Estimator v2 (SPEC-045)  
**CTs Planejados:** 18  
**Total Ecossistema apos R44:** 477 CTs (459 + 18)

---

## Sumario Executivo

O Scanner Noológico revelou que o ecossistema possui **cobertura epistêmica de apenas 38%** (nota C), com **57 categorias ausentes** em 10 dimensões. Simultaneamente, a Topologia Epistêmica identificou **1 ilha com alto isolamento** (0.75) e **0 buracos**, enquanto o Rupture Potential Index (RPI = 40.5) posiciona o ecossistema no quadrante de **melhoria incremental**.

Este ciclo combina **2 tracks paralelas** cujas saídas se alimentam mutuamente:

| Track | Foco | Scanner Base | Meta |
|-------|------|-------------|------|
| **Track 1 — Injeção** | Injetar artefatos epistêmicos nas 57 categorias ausentes | Noológico + Potentiality v2 | Cobertura 38% → 50%+ |
| **Track 2 — Topologia** | Mapear topologia, pontes e potencial de ruptura | SPEC-054 + SPEC-055 | RPI 40.5 → 60+ (ruptura segura) |
| **Integração** | Usar topologia para priorizar injeção e vice-versa | Ambos | Pipeline retroalimentado |

### Diagnostico Atual

| Metrica | Valor | Alvo R44 | 
|---------|-------|----------|
| Cobertura Noológica | 38% | 50%+ |
| Homogeneidade Cognitiva (HI) | 0.57 | < 0.55 |
| RPI (Rupture Potential) | 40.5 | 60+ |
| Ilhas Epistêmicas | 1 (isolamento 0.75) | 0 (conectadas) |
| Pontes Potenciais | 4 (skills 0.87, specs 0.77, agentes 0.76, mcps 0.66) | Todas ≥ 0.80 |
| Oportunidades Promising | 16 | 20+ |
| Oportunidades Exploratory | 35 | 25 (convertidas) |
| Oportunidades Marginais | 7 | 0 (eliminadas ou elevadas) |

---

## Track 1: Injeção de Diversidade Epistêmica

### 1.1 Pipeline de Injeção

```
Scanner Noológico (lacunas)
    → PotentialityEstimator v2 (viabilidade)
    → EpistemicArtifactInjector (geração de artefatos)
    → CognitiveDiversityScanner (verificação HI)
    → NoologicalScanner (verificação cobertura)
    → Feedback Loop
```

### 1.2 Prioridades de Injeção (baseadas no EPS)

| Prioridade | Dimensão | Cobertura Atual | Cobertura Alvo | Categorias | EPS Médio |
|:----------:|----------|:---------------:|:--------------:|:----------:|:---------:|
| 1 | dominios | 10% | 40% | Psic. clínica, Neurociências, Sociologia, Antropologia, Eco. comportamental, Filosofia mente, Psicofarmacologia, Educação, IA/Tecnologia | 62.8 |
| 2 | metodos | 20% | 40% | Qualitativo fenomenológico, Grounded theory, Misto sequencial, Misto convergente, Revisão sistemática, Meta-análise, Estudo de caso, Pesquisa-ação | 57.8 |
| 3 | paradigmas | 25% | 40% | Positivista, Interpretativista, Pragmatista, Fenomenológico, Construtivista, Pós-estruturalista | 64.6 |
| 4 | raciocinio | 50% | 70% | Dialético, Probabilístico, Abdutivo, Sistêmico, Metacognitivo | 53.0 |
| 5 | dados | 25% | 40% | Neurobiológicos, Qualitativos, Observacionais, Epidemiológicos, Cross-culturais, Metadados | 49.5 |
| 6+ | demais | 25-50% | 50%+ | Níveis análise, Temporalidade, População, Teorias | 40.9 |

### 1.3 Estrutura do Artefato Epistêmico

Cada artefato injetado deve conter:

```python
@dataclass
class EpistemicArtifact:
    dimension: str              # ex: "dominios"
    category: str               # ex: "Neurociências"
    artifact_type: str          # "reasoning_pattern" | "reference" | "method" | "paradigm"
    content: str                # descrição semântica do artefato
    source_scanner: str         # "noological" | "evolutionary" | "potentiality"
    eps_score: float            # 0-100
    cross_domain_impact: float  # 0-10
    theoretical_fertility: float # 0-10
    injected_at: str            # timestamp ISO
    ttl_days: int               # dias até expirar (default: 365)
```

---

## Track 2: Topologia Epistêmica + Rupture Potential

### 2.1 Mapeamento Topológico

Estado atual do grafo epistêmico:
- **4 pontos**: skills, mcps, specs, agentes
- **1 ilha**: (skills, mcps, specs) com isolamento 0.75
- **4 pontes potenciais**: skills (0.87), specs (0.77), agentes (0.76), mcps (0.66)
- **0 buracos**: sem vazios desconectados

**Ações**:
1. Conectar ilha via skills (ponte mais forte: 0.87)
2. Elevar bridge potential de specs para ≥ 0.85
3. Elevar bridge potential de agentes para ≥ 0.85
4. Elevar bridge potential de mcps para ≥ 0.75

### 2.2 Portfólio EPS × RPI

O Potentiality v2 mapeou 58 oportunidades no grid EPS×RPI:
- **Melhoria incremental** (RPI < 50, EPS médio-alto): 16 oportunidades
- **Rotina** (RPI < 50, EPS baixo): 14 oportunidades  
- **Ruptura segura** (RPI ≥ 50, EPS alto): 0 (alvo: criar 3+)
- **Ruptura especulativa** (RPI ≥ 50, EPS baixo): 0

**Estratégia**: Converter 3 oportunidades "Promising" em ruptura segura via injeção
de artefatos de alto impacto cross-domínio.

---

## Integração Cross-Track

### 3.1 Ciclo de Retroalimentação

```
Track 2 (Topologia)
    → identifica ilha (skills/mcps/specs) 
    → sugere injeção em dominios (conexão cross-cluster)
    → Track 1 injeta artefatos em dominios
    → Track 2 re-escaneia topologia
    → verifica redução de isolamento
    → loop até HI < 0.55 e RPI ≥ 60
```

### 3.2 Métricas de Sucesso Integradas

| Metrica | Track | Atual | Alvo | Peso |
|---------|:-----:|:----:|:----:|:----:|
| Cobertura Noológica | 1 | 38% | 50%+ | 30% |
| Homogeneidade Cognitiva | 1 | 0.57 | < 0.55 | 20% |
| RPI | 2 | 40.5 | 60+ | 25% |
| Ilhas Conectadas | 2 | 1 → 0 | 0 | 15% |
| Oportunidades Promising | 1+2 | 16 | 20+ | 10% |

---

## Casos de Teste (18 CTs)

### Track 1 — Injeção (9 CTs)

| CT | Nome | Descricao | Prioridade |
|:--:|------|-----------|:----------:|
| 01 | `test_injector_imports` | Módulo injector importa sem erros | Alta |
| 02 | `test_artifact_dataclass` | EpistemicArtifact tem todos os campos obrigatórios | Alta |
| 03 | `test_inject_single_artifact` | Injeção de 1 artefato em dimensão válida | Alta |
| 04 | `test_inject_batch_artifacts` | Injeção de lote (10+) em dimensões variadas | Alta |
| 05 | `test_injection_persistence` | Artefatos persistem em JSON e são recuperáveis | Alta |
| 06 | `test_injection_duplicate_detection` | Mesmo artifact não pode ser injetado duas vezes | Média |
| 07 | `test_injection_priority_order` | Injeção respeita ordem de prioridade (dominios > metodos > ...) | Média |
| 08 | `test_coverage_improvement` | Após injeção, cobertura noológica aumenta | Alta |
| 09 | `test_hi_reduction` | Após injeção, HI diminui | Média |

### Track 2 — Topologia (5 CTs)

| CT | Nome | Descricao | Prioridade |
|:--:|------|-----------|:----------:|
| 10 | `test_topology_mapper_imports` | Módulo topologia importa sem erros | Alta |
| 11 | `test_topology_scan_runs` | Escaneamento topológico retorna estrutura válida | Alta |
| 12 | `test_bridge_potential_improvement` | Injeção melhora bridge potential de specs | Alta |
| 13 | `test_island_connectivity` | Ilha é conectada via ponte mais forte | Média |
| 14 | `test_rpi_calculation` | RPI recalcula corretamente após injeção | Alta |

### Integração (4 CTs)

| CT | Nome | Descricao | Prioridade |
|:--:|------|-----------|:----------:|
| 15 | `test_cross_track_pipeline` | Pipeline completo Track1→Track2 funciona | Alta |
| 16 | `test_feedback_loop` | Loop de retroalimentação converge em ≤ 3 iterações | Média |
| 17 | `test_all_metrics_improve` | Todas as métricas melhoram após pipeline completo | Alta |
| 18 | `test_ecosystem_state_update` | ecosystem-state.json atualizado corretamente | Alta |

---

## Arquivos do Ciclo

| Arquivo | Funcao |
|---------|--------|
| `specs/SPEC-R44-ECOSYSTEM-EXPANSION.md` | Este documento — SDD |
| `tests/test_r44_ecosystem_expansion.py` | 18 CTs TDD |
| `nexus/epistemic_injector.py` | Track 1 — EpistemicArtifactInjector |
| `nexus/topology_integrator.py` | Track 2 + Integração |
| `nexus/artifacts/` | Artefatos epistêmicos injetados (persistência) |
| `ecosystem-state.json` | Atualização de versão |

---

## Referencias

- Scanner Noológico SPEC-031: `specs/scanner/SPEC-031-NOOLOGICAL-SCANNER.md`
- Potentiality Estimator v2 SPEC-045: `specs/SPEC-045-POTENTIALITY-ESTIMATOR-V2.md`
- Topologia Epistêmica SPEC-054: `specs/scanner/SPEC-054-EPISTEMIC-TOPOLOGY.md`
- Rupture Potential SPEC-055: `specs/scanner/SPEC-055-RUPTURE-POTENTIAL.md`
- Cognitive Diversity SPEC-053: `specs/scanner/SPEC-053-COGNITIVE-DIVERSITY.md`
