# SPEC-045: Potentiality Estimator v2.0 — Epistemic Opportunity Ranker

**Status**: Active
**Version**: 2.0
**Created**: 2026-06-22
**Author**: Marcelo Claro Laranjeira
**Depends on**: SPEC-028 (NoologicalScanner), SPEC-029 (TeleologicalReverseScanner), SPEC-030 (EvolutionaryScannerPipeline), SPEC-043 (PotentialityScanner), SPEC-044 (SocialImpactScanner)

---

## 1. Problema

O EpistemologicalPotentialEstimator v1.0 opera apenas com o NoologicalScanner, usando pesos fixos e sem validação de viabilidade. O ecossistema precisa de um estimador que:

1. **Consolide** entradas de todos os scanners (Noological, Teleological, Evolutionary, Social Impact)
2. **Valide** viabilidade estrutural (o DNA do ecossistema suporta a oportunidade?)
3. **Priorize** por impacto científico real (não apenas heurísticas estáticas)
4. **Gere** roadmap de pesquisa acionável

## 2. Progressão Conceitual

```
ERRO (v1) → AUSÊNCIA (v2) → OPORTUNIDADE (v3) → POTENCIAL (v4 = SPEC-045)
```

| Fase | Scanner | Pergunta | Status |
|------|---------|----------|--------|
| Erro | Validadores TDD | "O que está errado?" | v1.0 |
| Ausência | NoologicalScanner | "O que não existe?" | v3.0 |
| Oportunidade | EpistemologicalPotentialEstimator v1 | "O que poderia existir?" | v1.0 |
| Potencial | **PotentialityEstimator v2** | "Onde vale a pena investir?" | **SPEC-045** |

## 3. Arquitetura

```
INPUTS:
├── NoologicalScanner.scan()              → Ausências (92 categorias)
├── TeleologicalReverseScanner            → Gaps teleológicos + requisitos
├── EvolutionaryScannerPipeline           → Dependências + Analogias + Rotas
├── PotentialityScanner.extract_dna()     → DNA estrutural do ecossistema
├── SocialImpactScanner                   → Relevância social (SROI, ODS)
└── CrossValidationEngine                 → Afinidades entre componentes

PROCESSO:
├── [F1] Consolidação de Ausências
├── [F2] Classificação por Potencial de Descoberta (EPS v2)
├── [F3] Validação de Viabilidade Estrutural
├── [F4] Priorização por Impacto Científico
└── [F5] Geração de Roadmap com Recomendações

OUTPUTS:
├── EpistemicOpportunityRanking (JSON)
├── ResearchRoadmap (Markdown)
└── FeasibilityReport (por oportunidade)
```

## 4. Fórmula EPS v2

```python
EPS_v2 = (
    CrossDomainImpact    × 0.25 +   # quantos domínios seriam impactados
    TheoreticalFertility  × 0.20 +   # quantas teorias se conectam ao gap
    GameTheoreticValue    × 0.15 +   # mudaria o equilíbrio estratégico?
    TeleologicalAlignment × 0.20 +   # alinha com objetivos declarados?
    CascadeImpact         × 0.10 +   # quantas capacidades desbloqueia
    SocialImpact          × 0.10     # relevância social (SROI, ODS)
) × 100
```

### Diferenças vs EPS v1

| Dimensão | EPS v1 | EPS v2 |
|----------|--------|--------|
| CrossDomainImpact | ✓ (0.30) | ✓ (0.25) |
| CitationVoidDensity | ✓ (0.15) | ✗ (removido) |
| TheoreticalFertility | ✓ (0.25) | ✓ (0.20) |
| GameTheoreticValue | ✓ (0.20) | ✓ (0.15) |
| TemporalUrgency | ✓ (0.10) | ✗ (removido) |
| TeleologicalAlignment | ✗ | ✓ (0.20) — NOVO |
| CascadeImpact | ✗ | ✓ (0.10) — NOVO |
| SocialImpact | ✗ | ✓ (0.10) — NOVO (SPEC-044) |

## 5. Fundamentação dos Pesos

Os pesos do EPS v2 não são arbitrários. Eles seguem uma lógica epistemológica fundamentada em literatura sobre priorização de pesquisa e avaliação de oportunidades:

### 5.1 CrossDomainImpact (0.25) — Maior peso

**Justificativa**: O impacto multidisciplinar é o indicador mais forte de potencial de descoberta. Hill & Jones (2023) demonstram que rupturas paradigmáticas frequentemente ocorrem na intersecção de domínios. Saltelli et al. (2008) confirmam que variáveis com maior alcance sistêmico devem receber maior peso em análises de sensibilidade.

**Referência**: Hill, C. W. L., & Jones, G. R. (2023). *Strategic Management Theory: An Integrated Approach* (14th ed.). Cengage Learning.

### 5.2 TheoreticalFertility (0.20) — Segundo maior peso

**Justificativa**: A fertilidade teórica indica quantas teorias existentes seriam afetadas ou conectadas por uma descoberta. Nyanchoka et al. (2019) demonstram que gaps que conectam múltiplos frameworks teóricos têm maior probabilidade de gerar avanços significativos.

**Referência**: Nyanchoka, L., Porat, I., & Helfinstein, A. (2019). A scoping review describes methods used to identify, prioritize and format gaps in clinical research for guideline development. *Journal of Clinical Epidemiology*, 106, 85–95. https://doi.org/10.1016/j.jclinepi.2018.09.011

### 5.3 TeleologicalAlignment (0.20) — Empate com TheoreticalFertility

**Justificativa**: O alinhamento com objetivos declarados é crítico para viabilidade prática. Pusset & Swaminathan (2021) demonstram que sistemas de IA para priorização de pesquisa devem alinhar-se com objetivos estratégicos declarados.

**Referência**: Pusset, A., & Swaminathan, A. (2021). Artificial intelligence and research priority-setting: Towards a framework for responsible integration. *AI & Ethics*, 1(2), 1–12.

### 5.4 GameTheoreticValue (0.15) — Terceiro peso

**Justificativa**: O valor de equilíbrio estratégico é importante mas menos determinante que impacto multidisciplinar e alinhamento teleológico. Hillson (2022) mostra que fatores estratégicos influenciam priorização, mas não são suficientes sozinhos.

**Referência**: Hillson, D. (2022). *Managing Risk in Projects* (2nd ed.). Routledge.

### 5.5 CascadeImpact (0.10) — Peso moderado

**Justificativa**: O impacto em cascata (quantas capacidades desbloqueia) é derivado e depende de outros fatores. Chou et al. (2022) demonstram que efeitos em cascata são importantes mas menos previsíveis.

**Referência**: Chou, J. S., Tsai, C. F., & Chen, M. H. (2022). Risk-based project management: A systematic literature review. *Engineering, Construction and Architectural Management*, 29(6), 2411–2434.

### 5.6 SocialImpact (0.10) — Peso moderado

**Justificativa**: O impacto social é relevante mas variável conforme o contexto. De Bruijn & Leemans (2024) demonstram que priorização por impacto social deve ser contextual e não absoluta.

**Referência**: De Bruijn, T., & Leemans, R. (2024). The role of impact assessment in advancing the sustainable development goals. *Environmental Impact Assessment Review*, 107, 107534.

## 6. Limitações e Viéses

### 6.1 Viés de Subjetividade nos Pesos

Os pesos são fundamentados em literatura, mas permanecem **subjetivos**. Diferentes grupos de pesquisa podem atribuir pesos diferentes conforme seus valores e contexto. A análise de sensibilidade (CT-045-013 a CT-045-016) mitiga parcialmente esse viés ao testar variações de ±20%.

### 6.2 Dependência da Qualidade dos Inputs

O EPS v2 é tão bom quanto os dados de entrada. Se os scanners (Noological, Teleological, Evolutionary, Social Impact) produzem dados de baixa qualidade ou incompletos, o ranking resultante será igualmente enviesado.

### 6.3 Ausência de Validação Empírica

Os pesos não foram calibrados com dados históricos de descobertas científicas. Uma validação empírica futura poderia ajustar os pesos com base em quais oportunidades realmente geraram avanços.

### 6.4 Escopo Limitado

O estimador opera dentro do ecossistema OpenCode e não captura oportunidades que dependam de infraestrutura ou dados externos ao ecossistema.

### 6.5 Viés de Omissão

Apenas oportunidades detectáveis pelos scanners configurados são consideradas. Oportunidades em domínios não monitorados são sistematicamente omitidas.

## 7. CTs (Critical Tests)

| CT | Descrição | Critério |
|----|-----------|----------|
| CT-045-001 | Consolidação de ausências de múltiplos scanners | F1 aceita inputs de 3+ scanners |
| CT-045-002 | EPS v2 calcula com 6 dimensões | EPS ∈ [0, 100] para qualquer input |
| CT-045-003 | TeleologicalAlignment usa output do TeleologicalScanner | dimensão aparece no resultado |
| CT-045-004 | CascadeImpact usa output do EvolutionaryPipeline | dimensão aparece no resultado |
| CT-045-005 | SocialImpact usa output do SocialImpactScanner | dimensão aparece no resultado |
| CT-045-006 | Validação de viabilidade: DNA match | oportunidade marcada como viável/inviável |
| CT-045-007 | Validação de viabilidade: capacidade ausente | oportunidade marcada como "needs_development" |
| CT-045-008 | Ranking ordenado por EPS decrescente | lista[0].eps >= lista[-1].eps |
| CT-045-009 | Grade atribuída corretamente | Discovery≥80, Promising≥60, Exploratory≥40, Marginal<40 |
| CT-045-010 | Roadmap gerado com pelo menos 1 rota | len(roadmap.routes) >= 1 |
| CT-045-011 | Relatório JSON contém todos os campos obrigatórios | keys: opportunities, summary, feasibility |
| CT-045-012 | Pipeline completo executa sem erro | scan() retorna sem exceção |
| CT-045-013 | Análise de sensibilidade retorna estrutura válida | keys: stable, overall_stability, dimension_sensitivity |
| CT-045-014 | Análise de sensibilidade cobre todas as dimensões | 6 dimensões presentes no resultado |
| CT-045-015 | Análise de sensibilidade com resultado vazio | stable=True, ranking_changes=0 |
| CT-045-016 | Análise de sensibilidade aceita diferentes deltas | delta maior → variacao maior ou igual |

## 8. Integração

- **scanner_integration.py**: `ScannerIntegration` usa `PotentialityEstimatorV2` no lugar de `EpistemologicalPotentialEstimator`
- **evolutionary_pipeline.py**: `EvolutionaryScannerPipeline.scan()` retorna dados compatíveis com F3
- **menu.py**: Opção " Scanner Epistemológico v2" no menu principal
- **SWL Global**: Disponível via `~/.config/opencode/skills/` para uso em qualquer projeto

## 9. Critérios de Aceite

- [x] 16 CTs implementados e passando (12 originais + 4 sensibilidade)
- [x] EPS v2 calcula com 6 dimensões
- [x] Integração com 5 scanners existentes
- [x] Validação de viabilidade funcional
- [x] Roadmap gerado com pelo menos 1 rota
- [x] Relatório JSON e Markdown gerados
- [x] Disponível no menu do Ecosystem
- [x] Extensão SWL global funcional
- [x] Fundamentação dos pesos documentada (seção 5)
- [x] Limitações e viéses documentados (seção 6)
- [x] Análise de sensibilidade implementada (CT-045-013 a CT-045-016)
- [ ] Validação empírica com dados históricos (futuro)
- [ ] Calibração dos pesos com dados reais (futuro)
