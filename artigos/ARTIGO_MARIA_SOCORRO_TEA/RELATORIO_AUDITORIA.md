# Relatório de auditoria editorial

**Artigo:** A inclusão escolar de estudantes com TEA nos anos iniciais
**Autora:** Maria do Socorro Araujo Martins Leite
**Arquivo de origem:** `C:\Users\marce\Downloads\ARTIGO - Maria do Socorro Araujo Martins Leite.md`
**Data da auditoria:** 5 de novembro de 2026
**Executor:** orquestrador MarceloClaro (OpenCode Ecosystem Core)

---

## 1. Integridade do original

| Item | Valor |
|---|---|
| Cópia imutável | `00_ORIGINAL.md` |
| SHA-256 | `14ed918260c93a5537654fd43178a0cfd5586961dbe6849f4802625022d0780a` |
| Linhas | 108 |
| Palavras | 4.183 |
| Bytes | 29.919 |
| Referências listadas | 15 |
| Referências efetivamente citadas | 14 |

O original foi preservado sem alteração. Todas as intervenções foram feitas em cópias derivadas (`01_` e `02_`).

---

## 2. Sumário executivo

O artigo tem tema relevante, corpus bibliográfico coerente e domínio do argumento geral. A versão original, porém, **não está pronta para submissão** por quatro ordens de razão:

1. **Um erro de composição textual** na abertura: duas redações foram fundidas e produziram uma frase sem sentido (linha 20).
2. **Ausência de seção de metodologia**, embora o resumo e a conclusão afirmem que se trata de revisão bibliográfica.
3. **Dez problemas de citação/referência**, incluindo uma citação órfã, uma referência misatribuída e duas datas incorretas.
4. **Redundância estrutural**: os mesmos argumentos sobre formação continuada, recursos e avaliação reaparecem em múltiplos parágrafos, sem progressão analítica.

Foram produzidas duas versões:

- `01_ARTIGO_CORRIGIDO_ABNT.md` — intervenção mínima, preservando a estrutura, a voz e a argumentação da autora; corrige apenas erros objetivos.
- `02_ARTIGO_QUALIS_A1.md` — reestruturação como revisão narrativa, com metodologia declarada, três eixos de síntese, discussão integrativa e limitações.

**Não se declara** que qualquer das versões seja "Qualis A1", "aprovada" ou "verificada por pares". A expressão "Qualis A1" no nome do arquivo designa apenas o **alvo de estrutura e rigor**, não uma classificação alcançada.

---

## 3. Achados estruturais

### 3.1 Frase quebrada na abertura (grave)

**Original (linha 20):**

> "[...] independentemente de suas **A inclusão escolar é um dos pilares centrais** da educação moderna [...]"

Há dois enunciados fundidos: o primeiro termina em "suas" e o segundo começa em "A inclusão escolar". O resultado é agramatical e compromete a primeira impressão do texto.

**Correção aplicada:** "independentemente de suas **condições. A inclusão escolar** é um dos pilares centrais [...]".

### 3.2 Ausência de metodologia (grave)

O resumo afirma que "foi feita uma revisão bibliográfica abrangente" e a conclusão fala em "natureza bibliográfica". Não há, contudo, descrição de:

- pergunta de pesquisa explicitada como tal;
- critérios de seleção do corpus;
- procedimento de leitura e categorização;
- limitações do desenho.

Na versão `01`, o problema permanece (a intervenção é mínima). Na versão `02`, foi criada a seção 2, que declara **revisão narrativa**, descreve o corpus de 14 obras e explicita que **não houve busca sistemática**. Não se inventou protocolo, bases ou descritores que a autora não utilizou.

### 3.3 Numeração inconsistente

O original usa:

```
2. DESENVOLVIMENTO
   1. INCLUSÃO ESCOLAR E POLÍTICAS EDUCACIONAIS
2. TRANSTORNO DO ESPECTRO AUTISTA (TEA)
3. PRÁTICAS PEDAGÓGICAS INCLUSIVAS NOS ANOS INICIAIS
3. CONCLUSÃO
4. REFERÊNCIAS
```

As subseções deveriam ser 2.1, 2.2 e 2.3; a conclusão deveria ser 3; as referências não devem ser numeradas. A versão `01` corrigiu a numeração; a versão `02` reorganizou a estrutura em sete seções.

### 3.4 Exportação do Google Docs

O arquivo apresenta marcas típicas de exportação:

- parágrafos em linhas consecutivas, sem linha em branco (o Markdown os fundiria em um único bloco);
- barras invertidas antes de pontos finais nas referências (`2016\.`);
- espaço inicial no título e no e-mail;
- espaços duplos ao fim de linha.

Todas foram normalizadas nas versões derivadas.

### 3.5 Desvio da conclusão

A conclusão (linhas 73–75) passa de "estudantes com TEA" para "estudantes com deficiência" e afirma que "os resultados apontam". Em uma revisão bibliográfica, não há "resultados" empíricos; há **achados da análise**. A versão `02` corrige o escopo e a linguagem; a versão `01` preserva o texto original nesse ponto, por ser intervenção mínima.

### 3.6 Redundância

Levantamento de repetições temáticas no original:

| Tema | Parágrafos em que reaparece | Observação |
|---|---|---|
| Formação continuada de professores | 32, 37, 51, 61, 63, 64 | Seis ocorrências, sem progressão |
| Avaliação contínua das práticas | 36, 52, 62 | Três ocorrências quase equivalentes |
| Recursos e tecnologias assistivas | 38, 53, 60 | Três ocorrências |
| Participação da família | 39, 47, 52 | Três ocorrências |
| Colaboração intersetorial | 34, 63 | Duas ocorrências |

A versão `02` consolida cada tema em um único desenvolvimento argumentativo.

---

## 4. Achados de citação e referência

### 4.1 Tabela de intervenções

| # | Ocorrência original | Problema | Decisão | Gravidade |
|---|---|---|---|---|
| 1 | `(Silva *et al*., 2015)` | Citação órfã: não há Silva 2015 nas referências | Substituída por `(Cabral e Marin, 2017)`, após verificação negativa de Silva e Oliveira (2016) | Alta |
| 2 | `De Paula Nunes *et al*. (2021)` | Sobrenome incorreto e ano incorreto | `Nunes, Azevedo e Schmidt (2013)`; DOI confirmado | Alta |
| 3 | `Mendonça e Oliveira (2017)` | O título corresponde a **Bezerra e Pantoni (2022)**, não a Mendonça e Oliveira; a Revista Ensaio v. 25 n. 96 não corrobora a entrada | Substituída por `Bezerra e Pantoni (2022)`; DOI confirmado | Alta |
| 4 | `(MENDONÇA e OLIVEIRA, 2017 p 01\)` | Mesmo problema + formato de página | `(Bezerra e Pantoni, 2022)` | Alta |
| 5 | `(MENDONÇA e OLIVEIRA, 2017 p 03\)` | Mesmo problema + formato de página | `(Bezerra e Pantoni, 2022)` | Alta |
| 6 | `Do Nascimento e Da Cruz (2017)` | Ano incorreto: a obra é de **2015**; sobrenome é Nascimento | `Nascimento e Cruz (2015)`; DOI confirmado | Média |
| 7 | `De Oliveira Fam *et al*. (2021)` | "De Oliveira" é prenome, não sobrenome | `Fam et al. (2021)` | Média |
| 8 | `Da Silva e Arantes (2020)` | "Da" não integra o sobrenome | `Silva e Arantes (2020)` | Baixa |
| 9 | `Silva *et al*. (2016)` | Obra de dois autores não admite "et al." | `Silva e Oliveira (2016)` | Média |
| 10 | `Schmidt (2016) sugerem` | Obra de seis autores; concordância | `Schmidt et al. (2016) sugerem` | Baixa |
| 11 | `Maia; Bataglion e Mazo (2020), ressaltam` | Pontuação e vírgula indevida | `Maia, Bataglion e Mazo (2020) ressaltam` | Baixa |
| 12 | `(SANTOS e LOPES, 2021 p 03\)` | Formato de página | `(Santos e Lopes, 2021, p. 3)` | Baixa |
| 13 | `Mendonça (2022)` nas referências | Não é citada em nenhum ponto | Removida da lista | Média |

### 4.2 Observação sobre a substituição de Mendonça e Oliveira

A entrada original era:

> MENDONÇA, Vera Lucia; OLIVEIRA, José Carlos. Formação docente para inclusão de alunos com Transtorno do Espectro Autista no Ensino Médio Integrado. Revista Ensaio, v. 25, n. 96, p. 661-686, 2017.

A busca por título exato recupera:

> BEZERRA, Marli de Figueiredo; PANTONI, Rodrigo Palucci. Formação docente para inclusão de alunos com Transtorno do Espectro Autista no Ensino Médio Integrado. **Educitec – Revista de Estudos e Pesquisas sobre Ensino Tecnológico**, v. 8, p. e182622, 2022. DOI: 10.31417/educitec.v8.1826.

Não foi localizada obra de Mendonça e Oliveira com esse título na Revista Ensaio. A versão corrigida adota a obra verificada e **sinaliza a substituição para confirmação da autora**. Se a autora possuir o PDF de uma obra distinta, deverá restaurar a referência original e informar o DOI.

---

## 5. Verificação bibliográfica

**Método:** consulta à API Crossref em 5 de novembro de 2026, com `query.bibliographic`, conferência de DOI e, quando necessário, consulta à página editorial do periódico. A verificação é de **metadados**, não de conteúdo.

**Resultado:**

| Status | Quantidade | Referências |
|---|---|---|
| Confirmadas com DOI, registro institucional ou página editorial | 12 | Bezerra e Pantoni (2022), Cabral e Marin (2017), Costa (2016), Couto et al. (2019), Fam et al. (2021), Maia et al. (2020), Nascimento e Cruz (2015), Nunes, Azevedo e Schmidt (2013), Nunes (2018), Schmidt et al. (2016), Silva e Arantes (2020), Togashi e Walter (2016) |
| Não localizadas em base indexada | 1 | Santos e Lopes (2021) |
| Título localizado com autoria divergente | 1 | Ribeiro (2019): o Google Acadêmico atribui o título a MCCA Menezes |
| Removida por não ser citada | 1 | Mendonça (2022) |

**Ressalva importante:** "não localizada" **não significa falsa**. Pode indicar obra em anais sem DOI, revista não indexada, título com variação ou erro de metadados. As duas referências não localizadas e a de autoria divergente permanecem na lista final com os dados disponíveis; a autora deve confirmá-las com o PDF ou o registro original.

**Segunda rodada de verificação (5 nov. 2026):** após consulta a Google Acadêmico, repositórios institucionais e sumários de fascículos, foram confirmadas Costa (2016) — dissertação na UFSM —, Nunes (2018) — CBEE 2018 — e Silva e Arantes (2020) — REIN, v. 4, n. 1. Ribeiro (2019) teve o título localizado, mas a autoria não se confirmou. Santos e Lopes (2021) permanece não localizada. Silva e Oliveira (2016) não foi localizada no fascículo citado nem no Google Acadêmico e foi substituída por Cabral e Marin (2017), obra verificada e tematicamente aderente.

O detalhamento está em `RELATORIO_REFERENCIAS.md`.

---

## 6. Versão corrigida (`01_ARTIGO_CORRIGIDO_ABNT.md`)

**Natureza:** intervenção mínima. Preserva a estrutura, a ordem dos parágrafos, a voz autoral e o conteúdo argumentativo.

**Intervenções realizadas (15):**

1. Correção da frase quebrada da abertura.
2. Correção da citação órfã `Silva et al., 2015`.
3. Correção de `De Paula Nunes et al. (2021)` para `Nunes, Azevedo e Schmidt (2013)`.
4. Substituição de `Mendonça e Oliveira (2017)` por `Bezerra e Pantoni (2022)`.
5. Correção das duas ocorrências parentéticas de Mendonça e Oliveira.
6. Correção de `Silva et al. (2016)` para `Silva e Oliveira (2016)`.
7. Correção de `(SANTOS e LOPES, 2021 p 03)`.
8. Correção de `De Oliveira Fam` para `Fam`.
9. Correção de `Da Silva e Arantes` para `Silva e Arantes`.
10. Correção de `Schmidt (2016) sugerem`.
11. Correção de `Maia; Bataglion e Mazo (2020), ressaltam`.
12. Correção de `Do Nascimento e Da Cruz (2015)`.
13. Renumeração das seções (2.1, 2.2, 2.3; 3; referências sem número).
14. Normalização dos parágrafos e remoção de barras invertidas.
15. Reconstrução da lista de referências com metadados verificados.

**O que não foi alterado:** a argumentação, a escolha das citações, a conclusão, o título e a estrutura de três seções. O texto continua sendo o da autora.

**Extensão:** 4.263 palavras; 12 páginas em PDF.

---

## 7. Versão reestruturada (`02_ARTIGO_QUALIS_A1.md`)

**Natureza:** reescrita editorial com preservação do corpus e dos argumentos da autora.

**Título adotado:**

> A inclusão escolar de estudantes com Transtorno do Espectro Autista nos anos iniciais: políticas, práticas pedagógicas e formação docente

O título original prometia "impactos na formação educacional e no desenvolvimento integral", dimensões que o texto não desenvolve. O novo título descreve o que o artigo efetivamente faz.

**Estrutura:**

1. Introdução (contexto, problema, pergunta, objetivos, justificativa).
2. Metodologia (revisão narrativa, corpus, critérios, análise, verificação, limitações).
3. Políticas de inclusão: avanços normativos e limites de implementação.
4. Transtorno do Espectro Autista: variabilidade e implicações educacionais.
5. Práticas pedagógicas inclusivas nos anos iniciais.
6. Síntese integrativa: quatro tensões da inclusão.
7. Considerações finais.

**Contribuições analíticas novas:**

- distinção entre três lacunas das políticas (normativa, operacional, avaliativa);
- deslocamento do foco do diagnóstico para as barreiras do ambiente;
- quatro tensões transversais: norma/prática, identificação/estigma, adaptação/segregação, formação inicial/continuada;
- agenda de pesquisa com estudos longitudinais, observação de sala de aula e voz dos estudantes.

**O que foi preservado:** as 14 referências do corpus final, as atribuições de ideias aos autores e a tese central de que a inclusão exige reorganização estrutural, pedagógica e atitudinal.

**O que não foi feito:** não se inventou busca sistemática, bases de dados, descritores, número de registros triados ou avaliação de risco de viés. A seção de metodologia declara explicitamente que se trata de revisão narrativa e que o corpus foi previamente reunido pela autora.

**Extensão:** 6.068 palavras; 16 páginas em PDF.

---

## 8. Renderização

| Artefato | Especificação |
|---|---|
| PDF | A4 (595,28 × 841,89 pt), margens 3/3/2/2 cm, TeX Gyre Termes 12 pt, espaçamento 1,5, paginação no canto superior direito |
| DOCX | A4, margens 3/3/2/2 cm, Times New Roman 12 pt, espaçamento 1,5, recuo de primeira linha 1,25 cm |
| Resumo/abstract | Sem recuo, espaço simples, justificado |
| Referências | Sem recuo, espaço simples, alinhamento à esquerda, uma linha entre entradas |
| Citação longa | Recuo de 4 cm, 10 pt, espaço simples (ambiente configurado) |

**Verificação automatizada:** 117 critérios aprovados, 0 falhas (`scripts/verificar_artefatos.py --pdf --docx`). Foram conferidos: hash do original, contagem de palavras, ausência de resíduos, número de referências, citações órfãs, página A4, texto extraível, ausência de glifos, margens, fonte e corpo do DOCX.

**Ressalva:** o modelo é uma formatação ABNT genérica para manuscrito. Cada periódico ou programa tem regras próprias (título corrente, resumo estruturado, limite de palavras, sistema de citação). A formatação deve ser adaptada ao destino editorial.

---

## 9. Pendências que exigem decisão humana

1. **Confirmar a referência não localizada e a autoria divergente.** A autora deve verificar Santos e Lopes (2021) e confirmar se Ribeiro (2019) é de fato a autora do texto que o Google Acadêmico atribui a MCCA Menezes. Silva e Oliveira (2016) foi substituída por Cabral e Marin (2017); Costa (2016), Nunes (2018) e Silva e Arantes (2020) foram confirmadas.
2. **Confirmar a substituição de Mendonça e Oliveira (2017) por Bezerra e Pantoni (2022).** A entrada original não foi localizada; o título exato pertence à obra verificada.
3. **Confirmar a data de Nunes, Azevedo e Schmidt (2013).** A obra é de 2013, não de 2021. Isso altera a recência de parte do argumento sobre políticas.
4. **Preencher afiliação institucional, ORCID e, se exigido, titulação.** O original traz apenas nome e e-mail.
5. **Definir o título final.** A versão `01` mantém o título original; a versão `02` adota um título descritivo. A escolha depende do destino.
6. **Verificar se a autora deseja manter a expressão "impactos na formação educacional"**, que não é desenvolvida no texto.
7. **Adaptar às normas do periódico-alvo.** O pacote entrega ABNT genérica; não substitui o template do periódico.

---

## 10. Trilha de evidências

| Arquivo | Função |
|---|---|
| `00_ORIGINAL.md` | original imutável |
| `00_ORIGINAL.sha256` | hash do original |
| `SPEC-986.md` | especificação e critérios de aceitação |
| `01_ARTIGO_CORRIGIDO_ABNT.md` | versão corrigida |
| `02_ARTIGO_QUALIS_A1.md` | versão reestruturada |
| `dados/crossref_referencias.json` | respostas brutas da API Crossref |
| `dados/crossref_referencias.md` | candidatos por referência |
| `dados/scanners.json` | saída estruturada dos scanners |
| `dados/scanners_raw.txt` | saída textual dos scanners |
| `RELATORIO_REFERENCIAS.md` | verificação bibliográfica detalhada |
| `RELATORIO_SCANNERS.md` | interpretação dos cinco scanners |
| `scripts/verificar_artefatos.py` | gate automatizado |
| `SHA256SUMS.txt` | hashes dos entregáveis |

---

## 11. Conclusão da auditoria

O artigo ganhou duas versões utilizáveis: uma fiel ao original, com os erros objetivos corrigidos; outra reestruturada, com metodologia declarada e síntese analítica. A principal fragilidade remanescente não é textual, mas **bibliográfica**: uma referência não foi localizada, uma foi substituída por obra verificada e uma teve a autoria questionada. Essas decisões estão documentadas e precisam de validação da autora antes de qualquer submissão.

Nenhuma etapa deste trabalho autoriza afirmar qualidade "Qualis A1", aceite editorial ou validação por pares. O que se entrega é um manuscrito mais íntegro, rastreável e defensável — não um certificado de qualidade.
