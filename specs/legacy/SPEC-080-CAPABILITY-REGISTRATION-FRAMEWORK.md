# SPEC-080: Capability Registration Framework — Ponte Semântica Skills → Scanners

**Status:** Active
**Versão:** 1.0.0
**Data:** 2026-07-03
**Categoria:** Infraestrutura / Metadados
**Dimensão:** multi (infraestrutura de capabilities)
**Palavras-chave:** capability, keyword, mapeamento, registro, ontologia, feasibility

---

## 1. Problema

O Potentiality Scanner (SPEC-028) avalia a **viabilidade (feasibility)** de cada oportunidade epistêmica verificando se as capacidades necessárias estão registradas no `capability_map` do ecossistema. Atualmente, **100% das 58 oportunidades** (incluindo 16 Promising com EPS ≥ 60) retornam `feasibility="unviable"` com `capabilities_present=[]`.

**Causa raiz:** O `KEYWORD_TO_CAPABILITY` no `potentiality_scanner.py` mapeia apenas 36 keywords técnicas (ex: "test", "git", "agent", "mcp"). As **16 skills de pesquisa** (paradigmas, métodos, domínios, dados) não possuem keywords correspondentes, logo suas capacidades (`paradigm_analysis`, `methodology_design`, `data_collection`, `interdisciplinary_synthesis`, etc.) jamais são registradas.

**Impacto:** Todo o pipeline de priorização (EPS ranking, roadmap) é prejudicado, pois oportunidades de alto potencial são artificialmente marcadas como inviáveis.

## 2. Solução

Expandir o `KEYWORD_TO_CAPABILITY` para cobrir as 10 dimensões do scanner noológico, mapeando as skills de pesquisa existentes (16 skills, 79 SPECs, 418 CTs) para suas capacidades correspondentes.

### 2.1 Arquitetura da Ponte Semântica

```
Skills de Pesquisa (16)         KEYWORD_TO_CAPABILITY           Dimensões Scanner
─────────────────────────       ─────────────────────           ─────────────────
fenomenologico-paradigma   ──►  "fenomenologico" →              paradigmas
psicologia-clinica         ──►  "psicologia" →                  dominios
dados-qualitativos         ──►  "qualitativ" →                  dados
meta-analise               ──►  "meta-analise" →                metodos
...                        ──►  ...                             ...
```

### 2.2 Mapeamento por Dimensão

| Dimensão | Capacidade Requerida | Keywords para Mapping |
|:---------|:---------------------|:----------------------|
| `paradigmas` | `paradigm_analysis`, `theoretical_framework` | paradigma, epistemologia, fenomenologia, positivismo, construtivismo |
| `metodos` | `methodology_design`, `empirical_validation` | metodo, metodologia, qualitativ, quantitativ, misto, revisao, meta |
| `dominios` | `interdisciplinary_synthesis`, `cross_domain_mapping` | dominio, psicologia, neurociencias, sociologia, educacao |
| `raciocinio` | `reasoning_engine`, `logical_inference` | raciocinio, logica, inferencia, argumentacao, deducao |
| `dados` | `data_collection`, `statistical_analysis` | dados, coleta, entrevista, observacao, estatistica |
| `teorias` | `theoretical_integration`, `literature_synthesis` | teoria, framework, referencial, sintese, revisao |
| `niveis_analise` | `multi_scale_analysis`, `hierarchical_modeling` | nivel, escala, analise, intra, inter, multi |
| `temporalidade` | `temporal_modeling`, `longitudinal_analysis` | temporal, longitudinal, transversal, historico |
| `populacao` | `population_generalization`, `sampling_design` | populacao, amostra, contexto, clinico, comunitar |
| `teoria_jogos` | `game_theory_modeling`, `equilibrium_analysis` | jogo, nash, equilibrio, estrategia, cooperativo |

## 3. Referenciais Teóricos

| Ref | Fonte | Ano | Contribuição |
|:----|:------|:---:|:-------------|
| Gaudet et al. — Gene Ontology primer | arXiv:1602.01876 | 2016 | Framework de catalogação funcional hierárquica |
| Chen & Dai — Ontology-guided embedding | *Data & Knowledge Engineering* 10.1016/j.datak.2026.102597 | 2026 | Embedding semântico para completude de knowledge graph |
| Kessel & Atkinson — Morescient GAI for SE | arXiv:2406.04710 | 2024 | Mapeamento de capacidades em ecossistemas de software |
| Chen & Liu — Multi-agent KG framework | ICKG 10.1109/ickg63256.2024.00010 | 2024 | Framework colaborativo multiagente para construção de KGs |
| OASys Ontology for Autonomous Systems | KEOD 10.5220/0003634600470058 | 2011 | Ontologia para sistemas autônomos |
| Efeoglu — GraphMatcher Ontology Matching | arXiv:2404.14450 | 2024 | Aprendizado de representação para matching ontológico |

## 4. Definição do Artefato de Capacidade

```python
@dataclass
class CapabilityRegistration:
    """Registro de capacidade mapeada por keyword."""
    dimension: str          # ex: "paradigmas"
    capability: str         # ex: "paradigm_analysis"
    keywords: list[str]     # ex: ["paradigma", "epistemologia", "fenomenologia"]
    registered_skills: list[str] = field(default_factory=list)  # skills que implementam
    match_count: int = 0    # skills correspondentes encontradas
```

## 5. CTs (Casos de Teste)

| CT | Descrição | Critério |
|:--:|:----------|:---------|
| CT-01 | `paradigm_analysis` registrada via keyword "paradigma" | keyword in mapping |
| CT-02 | `methodology_design` registrada via keyword "metodo" | keyword in mapping |
| CT-03 | `interdisciplinary_synthesis` registrada via keyword "dominio" | keyword in mapping |
| CT-04 | `data_collection` registrada via keyword "dados" | keyword in mapping |
| CT-05 | `reasoning_engine` registrada via keyword "raciocinio" | keyword in mapping |
| CT-06 | Pelo menos 2 skills mapeadas para `paradigm_analysis` | match_count >= 2 |
| CT-07 | Pelo menos 2 skills mapeadas para `methodology_design` | match_count >= 2 |
| CT-08 | Oportunidade "Psicologia clínica" (EPS 62.8) muda de "unviable" para "needs_development" ou "viable" | feasibility != "unviable" |
| CT-09 | `theoretical_integration` registrada via keyword "teoria" | keyword in mapping |
| CT-10 | Pelo menos 50% das 10 dimensões têm ≥1 skill mapeada | >= 5 dimensões |

## 6. Integração com Scanners

- **Potentiality v2**: `_get_related_capabilities()` encontrará capacidades no `cap_map`, mudando feasibility de "unviable" para "needs_development" ou "viable"
- **Evolutionary Scanner**: Bottlenecks podem ser resolvidos quando capacidades forem detectadas
- **Cognitive Diversity**: HI indiretamente afetado pelo reconhecimento correto de skills
- **Noological**: Permanece inalterado (categorias fixas de 92)

## 7. Risco e Mitigação

| Risco | Probabilidade | Mitigação |
|:------|:-------------:|:----------|
| Falsos positivos (keyword genérica demais) | Média | Usar keywords específicas (ex: "raciocinio" em vez de "logica") |
| Skills não encontradas no registry | Baixa | Skills estão em `ecosystem-state.json` → migrar para `skills_registry.json` |
| Overmapping (mesma skill em múltiplas capacities) | Média | Aceitável — skills polivalentes são desejáveis |
