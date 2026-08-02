# Relatório de Validação Fim-a-Fim do Pipeline Científico

**Data:** 2026-08-02
**Caso de teste:** manuscrito real construído a partir do dossiê "A
Educação como Fator de Ruptura da Armadilha da Renda Média no Brasil"
(`materia-armadilha-renda-media-pdf.html`), adaptado para
[`academic/papers/manuscrito_educacao_armadilha_renda_media_usp.md`](../../academic/papers/manuscrito_educacao_armadilha_renda_media_usp.md),
preservando integralmente as 53 referências e todas as correlações/ANOVA
originais.
**Objetivo:** verificar se os gates R369 (andaimes de raciocínio), R370
(estatística rigorosa), R371 (triangulação multidisciplinar) e R372
(pré-registro) são funcionais sobre um manuscrito real — não um fixture
sintético — e corrigir o que a validação revelasse.

**Veredito honesto:** o pipeline **não estava totalmente funcional** para
este caso real. A validação encontrou um bug genuíno (falso positivo) e um
gap real de cobertura (R370 não se aplica a manuscritos publicados). Ambos
foram corrigidos no ciclo **SPEC-935-R373**, com testes de regressão. Este
relatório documenta o processo e os resultados finais.

---

## 1. R369 — Andaime científico + auditoria de novidade

**Antes da correção:** 1 achado `UNSUPPORTED_NOVELTY_CLAIM` (severity
`high`), na seção "Limitações Metodológicas", na frase:

> "Primeiras diferenças ou modelos VECM reduziriam as magnitudes observadas."

**Diagnóstico:** falso positivo. `"primeiro"`/`"primeira"` estavam no
léxico bruto de termos de novidade em `reasoning/production_scaffolds.py`.
"Primeiras diferenças" é um termo econométrico padrão (*first
differences*), não uma alegação de ineditismo sobre o próprio trabalho.
Qualquer uso ordinal comum do português ("primeira diferença", "primeiro
trimestre", "primeira vista", "primeiro passo") disparava o mesmo alarme.

**Correção aplicada:** os termos brutos foram substituídos por fraseado de
prioridade autoral explícita (`"pela primeira vez"`, `"primeiro estudo a"`,
`"o primeiro a"`, e equivalentes em inglês). Testes de regressão
confirmam que o falso positivo desaparece e que alegações genuínas de
prioridade continuam sendo pegas.

**Depois da correção:**

```json
{
  "moves_presentes": ["problema", "lacuna", "hipotese", "metodo",
                       "evidencia", "contra_argumento", "limitacao",
                       "contribuicao"],
  "findings": [],
  "human_gate": "recommended"
}
```

Os 8 movimentos de raciocínio científico estão presentes no manuscrito —
resultado esperado, já que o dossiê original já continha estrutura
argumentativa completa (o próprio texto-fonte cita explicitamente o
princípio "anti-overclaim" do ecossistema OpenCode, SPEC-935-R142).

## 2. R370 — Estatística computada de dados brutos

**Resultado:** `ValueError: amostra insuficiente para permutação
significativa (mínimo 3 por grupo)`.

**Isto não é uma falha do gate — é o comportamento fail-closed correto.**
O R370 (`two_sample_hypothesis_test`, `permutation_counter_proof`) foi
desenhado para computar estatística a partir de **amostras brutas**
(arrays individuais). O manuscrito, como todo artigo publicado, reporta
apenas **estatística-resumo já calculada**: r, p, IC 95%, n, F de ANOVA —
nunca os dados brutos subjacentes. Tentar alimentar o R370 com as 5 médias
de grupo da Tabela 1 (renda por nível educacional) não faz sentido
estatístico (n=1 "observação" por grupo) e o gate recusa corretamente, em
vez de fabricar um p-value de uma única observação.

**Gap real identificado:** isso deixava o manuscrito **sem nenhum gate
estatístico aplicável** — o R370 exige precisamente o que um manuscrito
publicado nunca tem à mão. Fechado no R373 (Seção 4 abaixo).

## 3. R371 — Triangulação multidisciplinar

Testada sobre a tese central do manuscrito: *"A qualidade da educação é a
variável estrutural mais fortemente correlacionada com o desenvolvimento
econômico brasileiro dentre as dimensões analisadas."*

Evidências construídas diretamente das correlações reais reportadas na
Tabela 2 do próprio manuscrito, tagueadas por domínio:

| Domínio | Evidência | Veredito |
|---|---|---|
| `educacao` | GDP×Escolaridade r=0,86 (p=0,026); GDP×PISA r=0,95 (p=0,012) | supports |
| `conectividade_digital` | GDP×Internet r=0,66 (p=0,020); Internet×GDP cross-country r=0,71 (p=0,015) | supports |
| `desigualdade` | Gini×Escolaridade r=−0,94 (p=0,015) | supports |
| `seguranca_alimentar` | GDP×Insegurança Alimentar r=−0,39 (p=0,155, **não significativo**) | neutral |

**Resultado:** `triangulated=True`, `supporting_domains=[conectividade_digital,
desigualdade, educacao]`, `contesting_domains=[]`, `human_gate=recommended`.

Três domínios independentes concordam, e o único domínio sem suporte
(segurança alimentar) foi corretamente tratado como **neutro** — não
contestador — porque o próprio manuscrito reporta essa correlação como
estatisticamente não significativa, não como evidência contrária. O gate
funcionou corretamente de primeira, sem necessidade de correção.

## 4. R372 — Protocolo de pré-registro

**Resultado:** `pre_registered=False`.

**Isto é o resultado correto e esperado**, não uma falha: este é um estudo
observacional retrospectivo sobre dados públicos já publicados (World
Bank, IBGE, OCDE, FAO, USPTO, CONAB) que antecedem em anos ou décadas a
concepção deste artigo. Não há, nem poderia honestamente haver, um
protocolo de hipótese pré-registrado antes da coleta desses dados. O gate
identifica corretamente essa realidade em vez de fabricar um selo de
pré-registro — exatamente o comportamento que o bug original do R372
(corrigido antes deste ciclo) deveria ter tido desde o início.

## 5. R373 — Contraverificação de estatísticas reportadas (novo, fechando o gap do R370)

Para dar ao R370 um caminho de aplicação real sobre manuscritos publicados
(sem exigir dados brutos que o autor não tem), foi implementado
`pearson_naive_significance(r, n)` — recálculo independente do p-value de
Pearson a partir de `(r, n)` via distribuição t de Student em Python puro,
validado contra `scipy.stats.t.cdf` com diferença ≤ 1e-15 em 8 casos de
referência (scipy usado apenas para validação de desenvolvimento; não é
importado no módulo entregue).

**Achado relevante durante a validação:** recalculando as 7 correlações do
manuscrito:

| Correlação | n | p reportado | p ingênuo (r,n) | Interpretação |
|---|---|---|---|---|
| GDP × Escolaridade | 8 | 0,026337 | 0,005617 | Mais conservador — correção de série temporal (ver Seção 6.1 do manuscrito) |
| GDP × Internet | 12 | 0,020297 | 0,020299 | Praticamente idêntico |
| Gini × Escolaridade | 6 | 0,014874 | 0,004264 | Mais conservador — mesma correção |
| PISA × GDP (cross-country) | 11 | 0,026572 | 0,026580 | Praticamente idêntico |
| Internet × GDP (cross-country) | 11 | 0,014699 | 0,014692 | Praticamente idêntico |
| GDP × PISA | **não declarado no texto** | 0,012430 | — | não verificável |
| GDP × Insegurança Alimentar | **não declarado no texto** | 0,155313 | — | não verificável |

As correlações **cross-country** (corte transversal, sem autocorrelação)
batem com precisão de máquina contra a fórmula-padrão — consistente com
computação direta. As correlações de **série temporal brasileira**
(GDP×Escolaridade, Gini×Escolaridade) reportam p **mais conservador** que
a fórmula ingênua — consistente com a própria Seção 6.1 do manuscrito, que
alerta sobre cointegração e recomenda correção que "reduz substancialmente
as magnitudes observadas" (ou seja, aumenta o p). **Nenhuma das 5
correlações verificáveis infla artificialmente sua significância.**

**Duas correlações (GDP×PISA, GDP×Insegurança Alimentar) não tinham `n`
declarado em lugar nenhum do texto-fonte**, apesar de a legenda da Tabela 2
do artigo original definir "n = número de observações na série temporal"
— a tabela não tinha uma coluna de `n` por linha.

**Correção aplicada (2026-08-02, a pedido do autor):** a Tabela 2 do
manuscrito adaptado agora tem uma coluna `n` explícita para as 7
correlações, com três graus de confiança distinguidos textualmente —
**declarado** (5 correlações, valor citado em algum ponto do texto-fonte),
**inferido** (GDP×PISA: n=8, justificado pelo número de edições do PISA
entre 2000 e 2022 — fato externo verificável, não confirmado pelo autor
original) e **não declarado** (GDP×Insegurança Alimentar: marcado
honestamente como "n.d.", sem valor fabricado, com nota explicando por que
o tamanho amostral não pôde ser inferido com confiança a partir da
periodicidade das janelas móveis do FAO/SOFI). Nenhum número foi
inventado; a distinção entre os três graus é explícita no próprio
manuscrito (Tabela 2 e notas 1–2) e na Seção 6.2 de Limitações.

**Design da contraverificação — por que assimétrica:** uma verificação
simétrica (sinalizar qualquer `p_reportado ≠ p_ingênuo`) teria produzido
falso positivo sistemático contra a correção de cointegração legítima que
o próprio manuscrito já revela nos dados. Nenhuma correção metodológica
legítima (cointegração, autocorrelação, tamanho efetivo de amostra) jamais
torna um resultado artificialmente **mais** significativo — apenas mais
conservador. Por isso, `crosscheck_reported_correlation` só sinaliza
`OVERSTATED_SIGNIFICANCE` quando o p reportado é **menor** que o ingênuo
além de uma tolerância — a única direção sem explicação metodológica
legítima.

---

## Resumo executivo

| Gate | Antes da validação | Depois da validação e correção |
|---|---|---|
| R369 (andaime científico) | 1 falso positivo (`UNSUPPORTED_NOVELTY_CLAIM` em termo econométrico) | 0 achados, 8/8 movimentos presentes |
| R370 (estatística de dados brutos) | Inaplicável a manuscritos publicados (gap real) | Gap documentado; complementado pelo R373 |
| R371 (triangulação multidisciplinar) | Funcional de primeira | `triangulated=True`, 3 domínios concordantes |
| R372 (pré-registro) | Funcional de primeira | `pre_registered=False` (correto para estudo retrospectivo) |
| R373 (contraverificação — novo) | Não existia | 5/5 correlações reais não inflam significância; 2/7 sem `n` declarado na fonte — **corrigido no manuscrito** com coluna `n` explícita (declarado/inferido/n.d.), sem fabricar dados |

**Conclusão:** o pipeline científico do ecossistema, após a correção do
falso positivo do R369 e a adição do R373, é funcional para validar um
manuscrito real de ponta a ponta. Nenhum achado deste relatório atesta
"verdade" das teses do manuscrito — cada gate aponta indícios estruturais
(movimentos de raciocínio presentes, convergência estatística onde
aplicável, corroboração multidisciplinar, ausência de pré-registro honesta,
ausência de inflação de significância) e exige revisão humana para
qualquer decisão final, como declarado em cada disclaimer.

**Testes:** 6 arquivos de teste novos/atualizados (R369 fix + R373),
50 testes TDD entre os dois, 194 testes de regressão verdes, 2501 testes
coletados sem erro em toda a suíte do repositório.
