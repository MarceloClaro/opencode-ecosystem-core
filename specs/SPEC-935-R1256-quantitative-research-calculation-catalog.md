---
spec_id: SPEC-935-R1256
title: Catálogo de 200 cálculos e primeira fase quantitativa reprodutível
component: research.quantitative_calculators
status: proposed
test_file: tests/test_r1256_quantitative_research.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    AC1:
      - tests/test_r1256_quantitative_research.py::test_catalog_contains_200_unique_typed_calculations_and_fails_closed_for_planned_items
    AC2:
      - tests/test_r1256_quantitative_research.py::test_sample_size_proportion_uses_finite_population_and_documents_variability
      - tests/test_r1256_quantitative_research.py::test_sample_size_mean_uses_standard_deviation_and_finite_correction
      - tests/test_r1256_quantitative_research.py::test_sample_size_rejects_invalid_inputs
      - tests/test_r1256_quantitative_research.py::test_design_experiment_uses_only_explicit_sample_size_parameters
    AC3:
      - tests/test_r1256_quantitative_research.py::test_wilson_interval_and_advanced_biostatistics
      - tests/test_r1256_quantitative_research.py::test_benjamini_hochberg_is_monotone_and_preserves_input_order
    AC4:
      - tests/test_r1256_quantitative_research.py::test_anova_spearman_and_meta_analysis_cochrans_q
      - tests/test_r1256_quantitative_research.py::test_research_csv_pipeline_accepts_anova_spearman_and_cochrans_q
      - tests/test_r1256_quantitative_research.py::test_advanced_methods_are_allowed_by_scientific_core_configuration
    AC5:
      - tests/test_r1256_quantitative_research.py::test_q_exponential_uses_tsallis_limit_and_domain
    AC6:
      - tests/test_r1256_quantitative_research.py::test_financial_calculators_use_explicit_conventions
      - tests/test_r1256_quantitative_research.py::test_irr_reports_multiple_roots_instead_of_selecting_one
    AC7:
      - tests/test_r1256_quantitative_research.py::test_complex_quantum_state_operations_and_born_rule
      - tests/test_r1256_quantitative_research.py::test_quantum_expectation_requires_hermitian_operator_and_normalized_state
    AC8:
      - tests/test_r1256_quantitative_research.py::test_catalog_implemented_entries_resolve_to_their_tested_api
---

# SPEC-935-R1256 — Catálogo de 200 cálculos e primeira fase quantitativa

## Demanda e decisões confirmadas

O usuário autorizou um catálogo de 200 cálculos organizado em fases, priorizando
pesquisa e bioestatística/bioinformática. Confirmou as interpretações:

- “Q-estatística” é Q de Cochran para heterogeneidade em meta-análise;
- “q-exponencial” é a função exponencial de Tsallis;
- nível de confiança frequentista e calibração probabilística são construtos
  distintos;
- “astrofísica-quântica” refere-se a métodos de astrofísica que usam modelos
  quânticos, sem implicar evidência experimental.

## Escopo desta fase

1. Criar catálogo estável com exatamente 200 itens em estatística de pesquisa,
   biostatística, bioinformática/ômicas, meta-análise, finanças, físico-química e
   física/quântica/astrofísica/Monte Carlo. Cada item declara ID, domínio, nome,
   tipo, status e referência de API ou estado de planejamento.
2. Implementar na fase inicial cálculo amostral para proporção e média, correção
   para população finita, efeito do desenho e não resposta; Wilson; ANOVA de uma
   via; correlação de Spearman; Q de Cochran para meta-análise; risco/odds e
   métricas diagnósticas; Benjamini–Hochberg; q-exponencial; calculadoras
   financeiras solicitadas; e operações de estado quântico complexo.
3. Integrar parâmetros amostrais explicitamente fornecidos ao
   `mci.experiment_designer` e métodos ANOVA/Spearman/Q de Cochran ao pipeline
   CSV de pesquisa já existente.
4. Os itens remanescentes ficam no catálogo como `planned`; resolução de item
   planejado falha explicitamente, sem gerar valores fictícios. Próximas fases
   podem cobrir os domínios por specs independentes.

## Especificação estatística do cálculo amostral

Para proporção binária sob amostragem aleatória simples, usa-se

`n0 = Z² p(1-p) / e²` e, se `N` é finita,
`n_fpc = N n0_deff / (N - 1 + n0_deff)`, com `n0_deff = n0 × design_effect`.

O tamanho final é arredondado para cima. A meta de recrutamento ajusta a não
resposta, sem exceder `N`; impossibilidade de alcançar o número previsto deve ser
retornada como limitação explícita. `p=0.5` é um default conservador de máxima
variância, indicado como tal. Para médias, a entrada é o desvio-padrão
populacional e o erro máximo absoluto, com `n0 = (Z σ / e)²`.

O valor `p` representa variabilidade da resposta Bernoulli; não codifica sozinho
heterogeneidade geográfica. Estratos e conglomerados exigem desenho e pesos
explícitos; `design_effect` é ajuste declarado pelo usuário, não inferido. O
cálculo de margem/nível de confiança não é análise de poder baseada em tamanho
de efeito; ambos permanecem separados no desenho experimental.

## Convenções financeiras

- Ponto de equilíbrio: custo fixo / contribuição unitária, exibindo unidades
  exatas e unidades inteiras arredondadas para cima.
- TIR: períodos igualmente espaçados; procurar raízes em intervalo limitado,
  reportar zero/uma/múltiplas raízes; não escolher silenciosamente entre TIRs.
- VPL: fluxo inicial em `t=0`; taxa de desconto estritamente maior que `-1`.
- Markup é calculado sobre o custo; margem-alvo é API distinta.
- CMV = estoque inicial + compras − estoque final.
- ROI = (benefício bruto − investimento) / investimento.
- Custo médio ponderado por quantidade e WACC são funções distintas para
  eliminar ambiguidade.
- Taxas são frações (por exemplo, `0.08` = 8%) e unidades monetárias não são
  convertidas implicitamente.

## Convenções quânticas complexas

Operações numéricas de álgebra linear de dimensão finita: normalização explícita
de estado, produto interno com conjugação, matriz densidade, regra de Born e
valor esperado de operador Hermitiano. Estado não normalizado não é normalizado
silenciosamente pelas funções de probabilidade/valor esperado. A implementação é
local/clássica; não executa QPU, não prova fidelidade experimental nem vantagem
quântica.

## Definições operacionais adicionadas

- Q de Cochran: `Q = Σ wᵢ(yᵢ − ȳw)²`, `wᵢ=1/vᵢ`, `ȳw=Σwᵢyᵢ/Σwᵢ`;
  aproximação nula qui-quadrado com `k−1` graus de liberdade; `I²=max(0,
  (Q−(k−1))/Q)×100`, e `I²=0` quando `Q=0`. Entradas são estimativas e
  variâncias amostrais na mesma escala, não transformadas silenciosamente.
- Q-exponencial: `exp_q(x)=[1+(1−q)x]^(1/(1−q))` para base positiva; no limite
  `q→1`, `exp(x)`. Para `q<1` e base não positiva, usar o corte de suporte zero;
  para `q>1`, base não positiva fica fora do domínio real e gera erro.
- ROI usa retorno bruto total: `(retorno_bruto − investimento)/investimento`.
  Receita/provento incremental precisa ser convertido pelo chamador para retorno
  bruto total, sem interpretação automática.

## Critérios de aceitação executáveis

- `AC1` — catálogo tem exatamente 200 IDs únicos, com categorias/status; itens
  planejados não podem ser executados ou resolvidos como se implementados.
  Cada entrada inclui fórmula ou marcador explícito de formalização pendente,
  entradas, saídas, unidades, pressupostos e API/estado de planejamento.
- `AC2` — cálculos amostrais aceitam N finita ou população não limitada, confiança,
  erro, `p` ou desvio-padrão, design effect e não resposta; expõem arredondamento,
  fórmula, premissas e limitações; integração ao desenho não presume parâmetros
  ausentes.
- `AC3` — intervalos de Wilson e funções bioestatísticas especificadas validam
  contagens/denominadores, declaram método e evitam correções ocultas para células
  zero; BH retorna q-valores ajustados na ordem original.
- `AC4` — ANOVA de uma via, Spearman e Q de Cochran validam dados, informam
  estatística, graus de liberdade, p-valor, pressupostos e tamanho de efeito
  aplicável; ficam acessíveis pelo executor CSV sem busca de resultados.
- `AC5` — q-exponencial implementa limite `q→1` e domínio real com erro explícito
  fora dele.
- `AC6` — calculadoras financeiras incluem ponto de equilíbrio, TIR, markup,
  VPL, CMV, ROI, margem de contribuição, custo médio ponderado por quantidade e
  WACC, com convenções e validação documentadas.
- `AC7` — funções quânticas operam sobre complexos finitos, verificam dimensão,
  normalização e Hermiticidade, e implementam Born/valor esperado corretamente.
- `AC8` — todo item marcado `implemented` resolve para uma API executável com
  testes; a API não afirma operação cloud, aconselhamento financeiro ou conclusão
  científica automática.

## Limites e dependências

- Não implementar as 200 fórmulas nesta fase; itens restantes serão declarados
  planejados e só serão ativados após spec, fonte metodológica e teste próprios.
- Não interpretar resultados sem desenho/dados; calcular N não assegura amostra
  representativa, poder adequado, ausência de viés ou aprovação ética.
- Sem instalação de novas dependências; aproveitar SciPy já usado no pipeline
  estatístico e manter álgebra quântica em Python/stdlib.
- Confiança estatística, calibração de previsões, evidência clínica, relação
  causal, validade biológica e desempenho de hardware permanecem distintos.
