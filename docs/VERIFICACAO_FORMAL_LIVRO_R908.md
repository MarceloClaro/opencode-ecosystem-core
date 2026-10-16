# Verificação formal do livro — R908

A pendência matemática é tratada por demonstrações explícitas em Lean 4/Mathlib, executadas no compilador fixado. O aceite é o recibo `docs/verification-book-lean-r908.json`, vinculado aos hashes das fontes. Uma instalação, um teste Python ou o antigo fallback `syntax_verified` não atendem a esse contrato.

O inventário independente localizou28 famílias nos módulos:27 contêm matemática ou definições de modelos; uma conserva observações empíricas fora da alegação de prova. A tabela associa cada família a enunciados, premissas e fontes. Não se anuncia “100% de validade científica”: a formalização prova somente as proposições traduzidas sob suas hipóteses. Declarações auxiliares também são auditadas, embora a tabela cite as proposições principais.

## Reexecução local

Lean 4.34.1, commit 5045d0056413266e57c625dcd7c365b10e377c52; Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612. O diretório `livro-core/lean/` contém toolchain, configuração e lockfile com todas as revisões transitivas. Com Elan/Lake instalado, a preparação inicial baixa as dependências; nenhuma fonte do livro é enviada a um serviço. A execução das provas é local.

```sh
cd livro-core/lean
lake exe cache get
cd ../..
python3 scripts/verify_book_lean.py --project livro-core/lean
python3 -m pytest tests/test_r908_book_lean.py -q
```

Os logs e o recibo reexecutado ficam em `outputs/core-r908/lean/`. Caches previamente obtidos podem ser reaproveitados quando todas as revisões e árvores rastreadas estão íntegras; a configuração da prova continua sendo a pasta versionada do livro. A ferramenta verifica toolchain, revisões transitivas, estado dos arquivos rastreados e hashes das configurações. O recibo inclui o hash do binário efetivo do Lean. Reprodutibilidade ainda confia no compilador, no kernel e nas dependências compiladas; não se declara construção de bootstrap independente.

## Gate e controles negativos

Cada fonte é compilada com `#print axioms` para **cada** declaração. O gate aceita apenas os fundamentos `propext`, `Classical.choice` e `Quot.sound`; nenhum axioma de aplicação é acrescentado. Ausência/duplicação de auditoria, declaração fora do formato suportado, `sorry`, `admit`, `sorryAx`, `unsafe`, `native_decide` ou comando de execução embutido impedem o aceite. O formato de fonte é deliberadamente restrito; esta ferramenta não é uma sandbox para Lean fornecido por terceiros.

O controle verdadeiro 2+3=5 deve passar. 2+3=6 e a mutaçãoEMA 31/50→32/50 devem ser recusados pelo compilador. Prova aberta e axioma inventado são recusados antes de compilar. Mudanças nas fontes Lean, no TeX, nos geradores, na matriz ou no verificador invalidam a custódia. A auditoria independente reproduziu e motivou duas regressões específicas: sobrescrita de auditoria duplicada e declaração omitida pelo extrator. As correções foram verificadas com RED e GREEN reais.

## Matriz enunciado–hipóteses–provas

### F01 — Probabilidade complementar e independência conjunta

Tipo: `formal_model`. Espaço de probabilidade; eventos mensuráveis conjuntamente independentes com mesma massa p. A independência não foi medida no Core.

Fontes: `livro-core/mod-01-fundacoes.tex`, `livro-core/mod-15-epilogo-reproducao.tex`.

Proposições principais: `BookFoundations.independent_equal_event_intersection`, `BookFoundations.independent_error_probability`, `BookFoundations.error_union_is_complement`, `BookAlgebra.complement_probability_bounds`.

### F02 — Potências e arredondamento do risco

Tipo: `exact_and_interval`. Racionais99/100 e999/1000, N=216; exemplos didáticos, não taxa de erro observada.

Fontes: `livro-core/mod-01-fundacoes.tex`, `livro-core/mod-15-epilogo-reproducao.tex`.

Proposições principais: `BookAlgebra.independent_error_216_tight_interval`, `BookAlgebra.independent_error_216_high_accuracy_interval`.

### F03 — Série do logaritmo, resto e retorno exponencial

Tipo: `exact_and_interval`. |u|<1 na série; base positiva no retorno exp(log p); dois termos deixam erro≤1/990000.

Fontes: `livro-core/mod-01-fundacoes.tex`.

Proposições principais: `BookFoundations.log_099_hasSum`, `BookFoundations.log_099_taylor_error`, `BookFoundations.log_099_taylor_interval`, `BookFoundations.logarithm_power_identity`, `BookFoundations.exponential_probability_example`.

### F04 — PPV e contagem de verdadeiros/falsos positivos

Tipo: `formal_model`. Razão préviaR; taxaα e poder1-β válidos; denominador positivo. Modelo sem viés explícito, não probabilidade de acerto de software.

Fontes: `livro-core/mod-00b-jornada-leitor.tex`, `livro-core/mod-09a-comparada.tex`, `livro-core/mod-15-epilogo-reproducao.tex`.

Proposições principais: `BookAlgebra.ppv_from_counts`, `BookAlgebra.ppv_denominator_expansion`, `BookAlgebra.ppv_bounds`, `BookAlgebra.ppv_low_power_exact`, `BookAlgebra.ppv_high_power_exact`, `BookAlgebra.ppv_equal_odds_exact`, `BookModels.ppv_eight_thirteenths_complement`, `BookModels.ppv_complement_percentage_bounds`.

### F05 — Proporções, percentuais e quocientes históricos

Tipo: `exact_and_interval`. Denominador>0; intervalo[0,1] somente quando numerador≤denominador. Razões teste/spec não são cobertura funcional. Números históricos são entradas.

Fontes: `livro-core/mod-01-fundacoes.tex`, `livro-core/mod-01b-historia.tex`, `livro-core/mod-06-ciencia.tex`, `livro-core/mod-11-apendices.tex`.

Proposições principais: `BookAlgebra.percent_unscale`, `BookAlgebra.coverage_fraction_bounds`, `BookAlgebra.weighted_coverage_bounds`, `BookAlgebra.historical_coverage_interval`, `BookModels.test_spec_ratio_rounds_0701`, `BookModels.series_spec_ratio_rounds_0768`, `BookModels.tests_per_series_spec_rounds_091`, `BookModels.specs_per_cycle_rounds_0815`, `BookModels.cycles_per_day_rounds_66`, `BookModels.one_eleventh_rounds_0091`, `BookModels.two_thirds_bounds`.

### F06 — Gate crítico e conjunção de critérios

Tipo: `formal_model`. Definição booleana de aceite condicionada ao critério crítico; não equivalência integral com o código de governança.

Fontes: `livro-core/mod-06-ciencia.tex`, `livro-core/mod-14-lote-categorias.tex`.

Proposições principais: `BookAlgebra.critical_gate_rejects`, `BookAlgebra.critical_gate_acceptance_requires_critical`.

### F07 — Reconciliação de catálogo e identidade de conjuntos

Tipo: `exact_and_interval`. 99+213=312 e81+18=99 conferem contagem. Conjuntos distintos podem ter a mesma cardinalidade; igualdade de IDs exige inspeção própria.

Fontes: `livro-core/mod-10-catalogo.tex`, `livro-core/mod-14-lote-categorias.tex`.

Proposições principais: `BookAlgebra.catalog_reconciliation`, `BookAlgebra.catalog_largest_categories`, `BookModels.equal_cardinality_not_equal_sets`, `BookModels.cardinality_equality_insufficient`.

### F08 — Média e concentração

Tipo: `exact_and_interval`. Contagens dadas, total>0; média não descreve dispersão. Exemplo[1,1,1,9] tem média3.

Fontes: `livro-core/mod-10-catalogo.tex`, `livro-core/mod-11-apendices.tex`.

Proposições principais: `BookAlgebra.catalog_concentration_exact`, `BookAlgebra.catalog_concentration_interval`, `BookAlgebra.catalog_mean_interval`, `BookModels.reference_counts_sum`, `BookModels.reference_counts_mean`.

### F09 — Redução estrutural M/k

Tipo: `formal_model`. M≥0,k≥1 para 0≤M/k≤M; M≥k para razão≥1.40/5=8 não é ganho medido em tokens/latência.

Fontes: `livro-core/mod-02-orquestracao.tex`.

Proposições principais: `BookModels.reduction_ratio_nonnegative_le_total`, `BookModels.reduction_ratio_at_least_one`, `BookModels.reduction_example_40_5`.

### F10 — Seleção restrita e elegibilidade

Tipo: `formal_model`. Conjunto finito não vazio e custos reais; empate requer seletor. Disponibilidade e capacidades são condições formais, não inferência executada.

Fontes: `livro-core/mod-02-orquestracao.tex`, `livro-core/mod-13-ativacao-agentes.tex`.

Proposições principais: `BookAttention.eligible_minimum_exists`, `BookAttention.excluded_cannot_be_chosen`, `BookAttention.contract_example_c2_minimizes`, `BookAttention.eligible_pool_membership`, `BookAttention.unavailable_not_eligible`, `BookAttention.missing_capability_not_eligible`.

### F11 — EMA e domínio da confiança

Tipo: `formal_model`. Confiança e escore em[0,1] garantem faixa; escore fora da faixa pode romper limite. Não prova calibração ou validação do parâmetro na API.

Fontes: `livro-core/mod-03-memoria-mci.tex`.

Proposições principais: `BookAlgebra.ema_70_30_bounds`, `BookAlgebra.ema_70_30_example`, `BookAlgebra.ema_moves_toward_score`, `BookAlgebra.ema_out_of_range_counterexample`.

### F12 — Lei de Amdahl e limite assintótico

Tipo: `formal_model`. Modelo ideal de carga fixa:0<s≤1,N>0; limite n→∞ com s≠0. Não estima speedup de motores heterogêneos. Exato65/17, arredondado3,8.

Fontes: `livro-core/mod-05-raciocinio.tex`.

Proposições principais: `BookAlgebra.amdahl_time_positive`, `BookAlgebra.amdahl_speedup_ceiling`, `BookAlgebra.amdahl_limit`, `BookAlgebra.amdahl_natural_executor_limit`, `BookAlgebra.amdahl_thirteen_exact`, `BookAlgebra.amdahl_thirteen_interval`, `BookAlgebra.amdahl_four_exact`, `BookAlgebra.amdahl_eight_exact`.

### F13 — Contabilidade PRISMA

Tipo: `formal_model`. Partições disjuntas e sem perdas; registros/relatórios/estudos são unidades distintas. Aritmética não valida triagem bibliográfica.

Fontes: `livro-core/mod-06-ciencia.tex`.

Proposições principais: `BookAlgebra.prisma_conservation`, `BookAlgebra.partition_cardinality`, `BookAlgebra.prisma_included_le_identified`.

### F14 — Staking, slashing e taxa por blocos

Tipo: `formal_model`. Quantidades e percentuais nas faixas declaradas; divisão inteira em blocos de10. Regras contábeis locais, sem inferência de valor econômico.

Fontes: `livro-core/mod-08-ecossistema.tex`.

Proposições principais: `BookAlgebra.staking_reward_formula`, `BookAlgebra.staking_reward_example`, `BookAlgebra.slashing_bounds`, `BookAlgebra.slashing_example`, `BookAlgebra.congestion_below_first_block`, `BookAlgebra.congestion_first_block`, `BookAlgebra.normal_fee_example`, `BookAlgebra.high_priority_fee_example`.

### F15 — Produto de quatro indicadores

Tipo: `formal_model`. Cada indicador deve pertencer a{0,1}. O produto vale1 se e somente se todos valem1; não inventa observações dos indicadores.

Fontes: `livro-core/mod-01c-instalacao.tex`.

Proposições principais: `BookFoundations.four_binary_indicators`, `BookFoundations.four_binary_indicators_percent`.

### F16 — Tempos consecutivos e duração total

Tipo: `formal_model`. Mesma unidade e timestamps consecutivos/ordenados; somar durações de ramos sobrepostos não mede tempo de parede.

Fontes: `livro-core/mod-07-integracoes.tex`.

Proposições principais: `BookFoundations.five_consecutive_intervals`, `BookFoundations.consecutive_duration_nonnegative`.

### F17 — Custo esperado de duas rotas

Tipo: `formal_model`. Distribuição finita de duas possibilidades,0≤p≤1, custo fixo c≥0 quando ativa, zero na outra. Não prova que a frequência real seja p.

Fontes: `livro-core/mod-13-ativacao-agentes.tex`.

Proposições principais: `BookModels.bernoulli_mass_normalized`, `BookModels.bernoulli_mass_nonnegative`, `BookModels.bernoulli_finite_cost_equals_product`, `BookModels.bernoulli_cost_bounds`, `BookModels.bernoulli_example_02_2`, `BookModels.bernoulli_exercise_05_2`.

### F18 — Unidades de armazenamento e guardas

Tipo: `exact_and_interval`. MiB=2^20bytes,MB=10^6bytes.1240>1000e1180>25 são comparações sobre valores informados, não uma leitura do disco.

Fontes: `livro-core/mod-09-infra.tex`.

Proposições principais: `BookFoundations.mebibyte_bytes`, `BookFoundations.megabyte_bytes`, `BookFoundations.mebibyte_megabyte_difference`, `BookFoundations.directory_weight_guard_rejects_example`, `BookFoundations.file_weight_guard_rejects_example`.

### F19 — Similaridade de Jaccard

Tipo: `formal_model`. Conjuntos finitos; união não vazia para quociente interpretável. Vazio exige convenção explícita; similaridade lexical não mede competência.

Fontes: `livro-core/mod-13-ativacao-agentes.tex`, `livro-core/mod-17-e1e7-para-leigos.tex`.

Proposições principais: `BookAttention.jaccard_mem_unit`, `BookAttention.jaccard_symmetric`, `BookAttention.jaccard_identical`, `BookAttention.jaccard_disjoint`, `BookAttention.jaccard_example_half`, `BookAttention.jaccard_example_third`, `BookAttention.jaccard_example_three_fifths`.

### F20 — Softmax matricial e escala didática

Tipo: `exact_and_interval`. Normalização linha a linha em reais, escores dados[4,0]/sqrt4=[2,0]. Não afirma que o Core execute QKᵀV nessa rota.

Fontes: `livro-core/mod-00b-jornada-leitor.tex`, `livro-core/mod-15-epilogo-reproducao.tex`.

Proposições principais: `BookModels.attention_dimension_sqrt_four`, `BookModels.attention_dimension_scaled_four`, `BookAttention.two_row_softmax_sum`, `BookAttention.two_row_reversed`, `BookAttention.two_row_tie`, `BookAttention.exp_two_rational_bounds`, `BookAttention.softmax_2_0_rational_bounds`, `BookAttention.softmax_0_2_rational_bounds`.

### F21 — Utilidade, normalização e ordenação

Tipo: `formal_model`. Critérios em[0,1], pesos0,30/0,35/0,25/0,10; conjunto não vazio; temperaturas positivas. Calibração e segurança IEEE-754 não demonstradas.

Fontes: `livro-core/mod-15-epilogo-reproducao.tex`, `livro-core/mod-02-orquestracao.tex`.

Proposições principais: `BookAttention.head_weights_sum_one`, `BookAttention.utility_mem_unit`, `BookAttention.utility_example_075`, `BookAttention.utility_example_064`, `BookAttention.utility_softmax_075_064_bounds`, `BookAttention.utility_softmax_064_075_bounds`, `BookAttention.softmax_soma_um`, `BookAttention.softmax_invariante_max`, `BookAttention.softmax_mem_Ioo`, `BookAttention.softmax_peso_total_singleton`, `BookAttention.softmax_same_pool_order`, `BookAttention.peso_cresce_com_escore`, `BookAttention.temperatura_aguca_maximo`, `BookAttention.exp_apos_subtrair_majorante_le_um`, `BookAttention.roteamento_guloso_otimo`, `BookAttention.topk_dominam_resto`, `BookAttention.combinacao_convexa_limitada`, `BookAttention.combinacao_convexa_limitada_baixo`.

### F22 — Álgebra elementar

Tipo: `exact_and_interval`. Domínio real;2x+1=5↔x=2; x²−1=(x−1)(x+1);2+3=5. Não comprova disponibilidade de SymPy/Z3.

Fontes: `livro-core/mod-05-raciocinio.tex`, `livro-core/mod-07-integracoes.tex`.

Proposições principais: `BookFoundations.linear_equation_iff`, `BookFoundations.difference_of_squares_factorization`, `BookFoundations.simple_sum_exact`.

### F23 — Primitiva do seno

Tipo: `formal_model`. Derivada de−cos(x)+C é sin(x), para reais x e constante C. Não prova execução de um integrador externo.

Fontes: `livro-core/mod-07-integracoes.tex`.

Proposições principais: `BookFoundations.sine_antiderivative`.

### F24 — Modus ponens

Tipo: `formal_model`. Das premissas P e P→Q segue Q. A verdade empírica de P e da implicação não é estabelecida pela regra.

Fontes: `livro-core/mod-05-raciocinio.tex`.

Proposições principais: `BookFoundations.modus_ponens`.

### F25 — Decomposição aditiva de custo

Tipo: `definition_model`. Ctotal=Cessencial+Cacidental é definição do modelo; mesma unidade. Não lei empírica universal sobre projetos.

Fontes: `livro-core/mod-04-qualidade-sdd.tex`.

Proposições principais: `BookModels.additive_cost_identity`, `BookModels.additive_cost_lower_bound`, `BookModels.reducing_accidental_reduces_total`.

### F26 — Discrepância entre observado e esperado

Tipo: `definition_model`. D=O−E, grandezas comparáveis. D=0 não prova identidade de dados ou correção de previsão.

Fontes: `livro-core/mod-14-lote-categorias.tex`.

Proposições principais: `BookModels.discrepancy_reconstructs_observed`, `BookModels.discrepancy_zero_iff`, `BookModels.discrepancy_reversed`.

### F27 — Observações científicas e de execução

Tipo: `empirical_not_formalized`. Pearson/Welch/Iris, duração, histórico de execução, contagens e hashes exigem dados/logs próprios. Não são promovidos a teorema por substituição numérica; adequação estatística e revisão externa não estão certificadas.

Fontes: `livro-core/mod-06-ciencia.tex`, `livro-core/mod-09a-comparada.tex`, `livro-core/mod-07-integracoes.tex`.

Sem alegação de prova sobre os dados observados. Permanecem exigidos artefatos da execução e julgamento científico.

### F28 — Completude de metadados e itens FAIR

Tipo: `formal_model`. 1−6/78=12/13; contagem2+2+2+2=8. Proporções de preenchimento não constituem conformidade FAIR nem mérito epistemológico.

Fontes: `livro-core/mod-12-fichas-nucleo.tex`, `livro-core/mod-06-ciencia.tex`.

Proposições principais: `BookAlgebra.unit_coverage_complement_exact`, `BookAlgebra.fair_item_accounting`, `BookModels.four_sixths_equals_two_thirds`, `BookModels.four_sixths_bounds`.

## Correções feitas no texto

- Logaritmo e potência: igualdade substituída por aproximação nos passos truncados; resto explícito e intervalo racional final.
- Amdahl: valor exato 65/17;0,0615 e0,2615 tratados como aproximações.
- Completude:1−6/78=12/13≈0,923, sem igualdade falsa com decimal truncado.
- PPV:5/13≈38,5%de falsos positivos no cenário 8/13; removida a inferência incorreta de que viés entra apenas no denominador.
- Modelo de Ioannidis não apresentado como medição da taxa de erro do Core ou verdade individual.
- Seleção: conjunto finito não vazio, possibilidade de empate e ausência de elegíveis explicitadas.
- Seeds controlam uma fonte de aleatoriedade; não garantem determinismo de toda execução.
-3,39/12 é amortização de **uma** execução compartilhada por 12 tarefas.

## Limites que acompanham a conclusão

O teorema de exponencial após subtrair o máximo limita um número real a 1. Ele não modela arredondamento, subnormais ou overflow IEEE-754. Similarmente, pesos normalizados não são probabilidades calibradas de acerto. As provas das políticas são modelos explícitos, sem alegar equivalência integral com o código Python. Catálogo, ensaios científicos, qualidade editorial e revisão externa conservam verificações próprias. A correção da tradução do texto para o formalismo recebe revisão humana e permanece uma obrigação de manutenção.

Fundamentos: [documentação oficial de Lean — Axioms and Computation](https://lean-lang.org/theorem_proving_in_lean4/Axioms-and-Computation/) e [Mathlib4](https://github.com/leanprover-community/mathlib4).

A ampliação R909 do prefácio discute autoria como tese interpretativa. Ela não
acrescenta fórmula nem é apresentada como teorema Lean; sua fundamentação
bibliográfica e seus limites estão em `docs/PREFACIO_ASSINATURA_COGNITIVA_R909.md`.
A custódia é reexecutada para os novos bytes do livro, mantendo as 158 provas
matemáticas no mesmo alcance.


## Exposição local R910

O inventário originalR908 de158declarações foi ampliado na revisãoR910. Consulte
o recibo vivo para a contagem aceita atual, sem atribuir ao PDF histórico as fontes
posteriores. Os capítulos agora ligam fórmulas a hipóteses, passos, lemas e nomes Lean;
as dependências fundamentais aparecem por declaração, geradas de auditoria real.
A matriz passou a28famílias matemáticas e uma observacional. O método e os limites
estão em `docs/DEDUCOES_LOCAIS_LIVRO_R910.md`, e a edição atual em
`docs/verification-book-r910.json`. A prova continua distinta de validade empírica.
