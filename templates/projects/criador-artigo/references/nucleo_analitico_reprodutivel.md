<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Nucleo Analitico Reprodutivel

## Finalidade

Este documento adiciona ao sistema um nucleo especializado para:

- ciencia de dados;
- estatistica avancada;
- matematica aplicada;
- codigo cientifico auditavel;
- pipelines de reproducao;
- governanca de datasets;
- validacao de modelos, simulacoes e experimentos computacionais.

Ele existe para impedir que artigos quantitativos ou computacionais parecam rigorosos sem serem reexecutaveis, auditaveis e defensaveis perante banca, parecerista ou comite cientifico.

## Quando ativar

Ativar este nucleo sempre que o artigo envolver pelo menos um dos elementos abaixo:

- analise quantitativa nao trivial;
- codigo proprio ou codigo adaptado;
- scripts, notebooks, pacotes ou pipelines;
- datasets originais, derivados, integrados ou simulados;
- formulas, modelos matematicos ou simulacoes;
- machine learning, deep learning ou data mining;
- bioinformatica, quimioinformatica, linguistica computacional, visao computacional ou computacao quantica.

## Principios inegociaveis

1. Resultado numerico sem trilha computacional nao conta como reproduzivel.
2. Codigo sem fonte de verificacao tecnica nao conta como auditado.
3. Dataset sem proveniencia, esquema e restricoes de uso nao conta como cientificamente governado.
4. Formula sem definicao de simbolos, suposicoes e limite de aplicacao nao conta como formalmente validada.
5. Modelo sem baseline, sensibilidade e criterio de robustez nao conta como resultado defensavel.
6. Documento final sem pacote de reproducibilidade nao fecha em padrao Qualis A1 para pesquisa computacional ou intensiva em dados.

## Hierarquia de confianca para codigo e metodos

Ao auditar linguagens, bibliotecas, frameworks e snippets, usar a seguinte ordem de precedencia:

1. documentacao oficial da linguagem, biblioteca ou framework;
2. especificacao tecnica oficial ou standard reconhecido;
3. repositorio oficial do projeto, incluindo README, exemplos, testes, changelog e release notes;
4. artigo metodologico original ou referencia canonical da tecnica;
5. implementacoes mantidas pelos autores ou mantenedores principais;
6. issues e discussoes oficiais apenas para ambiguidade operacional;
7. repositorios de terceiros, blog posts e tutoriais apenas como apoio, nunca como unica ancora.

## Cobertura multipla de dominios

O nucleo precisa dar suporte granular e multiplo a diferentes familias de problema:

- estatistica basica, intermediaria e avancada;
- inferencia frequentista, bayesiana e causal;
- matematica aplicada, otimizacao, sistemas dinamicos e modelagem formal;
- machine learning classico, deep learning e data mining;
- bioinformatica de DNA, RNA, proteomica, metabolomica e multiomicas;
- quimioinformatica, chemometrics, QSAR/QSPR e modelagem molecular;
- ciencias sociais quantitativas, survey science, psicometria, NLP e linguistica computacional;
- visao computacional, processamento de imagem, video e multimodalidade;
- computacao quantica aplicada com Qiskit, Cirq, PennyLane e stacks correlatas.

## Agentes do nucleo analitico

| ID | Agente | Ativacao tipica | Entregas nucleares |
|---|---|---|---|
| A17 | `Agente de Framework Reprodutivel e Ambientes` | sempre que houver codigo ou pipeline | `manifesto_reprodutibilidade.md`, `ambiente_execucao.md` |
| A18 | `Agente de Engenharia de Dados, Datasets e Proveniencia` | sempre que houver dados | `catalogo_datasets.md`, `codebook_dados.md` |
| A19 | `Agente de Auditoria de Codigo e Documentacao Tecnica` | sempre que houver codigo, notebook ou script | `auditoria_codigo.md` |
| A20 | `Agente de Estatistica Avancada e Inferencia` | estudos quantitativos, causais, bayesianos, temporais ou multivariados | `plano_inferencia_avancada.md`, `validacao_analitica_avancada.md` |
| A21 | `Agente de Matematica Aplicada e Modelagem Formal` | artigos com modelos, equacoes ou derivacoes | `anexo_matematica_aplicada.md`, `auditoria_formulas.md` |
| A22 | `Agente de Machine Learning, Deep Learning e Data Mining` | modelagem preditiva, classificacao, clustering, recomendacao, LLMs | `pipeline_ml.md`, `registro_experimentos.md` |
| A23 | `Agente de Bioinformatica e Omicas` | DNA/RNA, genomas, transcriptomas, proteomas, single-cell | `pipeline_bioinformatica.md`, `registro_experimentos.md` |
| A24 | `Agente de Quimioinformatica e Modelagem Molecular` | QSAR, espectrometria, descritores, docking, simulacao molecular | `pipeline_quimioinformatica.md`, `registro_experimentos.md` |
| A25 | `Agente de Ciencias Sociais Quantitativas e Linguistica Computacional` | surveys, corpora, psicometria, redes, texto e discurso | `pipeline_social_linguistica.md`, `registro_experimentos.md` |
| A26 | `Agente de Visao Computacional e Multimodalidade` | imagens, video, OCR, segmentacao, modelos multimodais | `pipeline_visao_multimodal.md`, `registro_experimentos.md` |
| A27 | `Agente de Computacao Quantica Aplicada` | circuitos, simuladores, VQAs, kernels quanticos, hibridos | `pipeline_quantico.md`, `registro_experimentos.md` |
| A28 | `Agente de Benchmarking, Ablacao e Robustez` | sempre que houver modelo, simulacao ou pipeline comparativo | `relatorio_benchmark_robustez.md` |

## Artefatos obrigatorios do pacote reprodutivel

| Arquivo | Funcao |
|---|---|
| `manifesto_reprodutibilidade.md` | declarar o que pode ser reproduzido, por quem, com quais restricoes e em qual nivel |
| `ambiente_execucao.md` | congelar linguagem, dependencias, hardware, seeds, sistema e instrucoes de execucao |
| `catalogo_datasets.md` | listar datasets, origem, versao, licenca, particionamento e riscos |
| `codebook_dados.md` | definir variaveis, campos, tipos, unidades, missing, label e transformacoes |
| `auditoria_codigo.md` | rastrear origem do codigo, adequacao tecnica, anchors em docs oficiais e limites |
| `auditoria_formulas.md` | verificar simbolos, derivacoes, hipoteses, estabilidade e implementacao numerica |
| `registro_experimentos.md` | documentar seeds, configuracoes, hiperparametros, runs, metricas e anomalias |
| `relatorio_benchmark_robustez.md` | comparar baselines, ablations, sensibilidade, erro e robustez |

## Estrutura minima para banca e reproducao

O pacote final deve permitir que um terceiro competente:

1. entenda que dados entraram;
2. saiba como os dados foram transformados;
3. saiba qual codigo foi executado;
4. saiba quais formulas ou modelos foram aplicados;
5. reconstrua o ambiente minimo;
6. compare resultados reportados com os artefatos brutos e derivados;
7. identifique o que nao pode ser reproduzido integralmente e por qual razao.

## Niveis de reproducibilidade

### Nivel Bronze

- ambiente descrito;
- datasets catalogados;
- codigo identificado;
- resultados principais localizaveis.

### Nivel Silver

- ambiente reproduzivel com instrucoes de execucao;
- datasets e codebook completos;
- registro de experimentos preenchido;
- auditoria de codigo concluida.

### Nivel Gold

- pipeline rerunavel ponta a ponta;
- benchmark e ablation documentados;
- formulas auditadas;
- riscos residuais explicitados;
- gerente aprova o pacote como defensavel em banca.

## Regras especiais para datasets

1. Todo dataset precisa ter origem, data de obtencao, versao e licenca.
2. Todo dado sensivel precisa ter restricao de acesso, anonimização ou justificativa de indisponibilidade.
3. Todo split de treino, validacao e teste deve ser registrado.
4. Toda transformacao irreversivel deve ser declarada.
5. Dados sinteticos devem ser explicitamente rotulados como sinteticos.

## Regras especiais para codigo

1. Nenhum snippet entra no manuscrito ou no pipeline sem ancoragem em documentacao ou repositorio confiavel.
2. Nenhum snippet de terceiros deve ser copiado sem indicar adaptacao, contexto e limite.
3. Toda dependencia critica deve ter versao ou faixa de compatibilidade declarada.
4. Todo notebook relevante deve ser convertivel em passo reproduzivel ou script equivalente.
5. Toda operacao aleatoria relevante deve registrar seed e estrategia de controle.

## Regras especiais para formula e modelagem

1. Toda formula deve definir simbolos, dominio e unidade.
2. Toda derivacao deve dizer o que foi assumido.
3. Toda implementacao numerica deve declarar aproximacao, solver ou estrategia computacional.
4. Todo modelo deve registrar criterio de identificabilidade, convergencia ou estabilidade quando aplicavel.

## Roteamento por tipo de estudo

| Tipo de estudo | Agentes minimos |
|---|---|
| regressao, GLM, multilevel, survival, causal | A17 + A18 + A19 + A20 + A28 |
| simulacao matematica, otimizacao, equacoes diferenciais | A17 + A19 + A21 + A28 |
| machine learning tabular ou textual | A17 + A18 + A19 + A20 + A22 + A28 |
| bioinformatica e multiomicas | A17 + A18 + A19 + A20 + A23 + A28 |
| quimioinformatica e modelagem molecular | A17 + A18 + A19 + A21 + A24 + A28 |
| ciencias sociais quantitativas e linguistica computacional | A17 + A18 + A19 + A20 + A25 + A28 |
| visao computacional e multimodal | A17 + A18 + A19 + A22 + A26 + A28 |
| computacao quantica aplicada | A17 + A19 + A21 + A27 + A28 |

## Gate especifico do nucleo analitico

O nucleo analitico so pode ser considerado pronto quando:

- ambiente, dados e codigo formam cadeia coerente;
- os artefatos tecnicos fecham com o texto do artigo;
- as metricas reportadas batem com os registros experimentais;
- o uso de bibliotecas, frameworks e formulas foi auditado;
- o gerente recebeu parecer cruzado de pelo menos um agente metodologico e um agente tecnico.




---
> ⚠️ **DIRETIVA GLOBAL DE SINCRONIZAÇÃO MASWOS (ECOSSISTEMA V3.0)** ⚠️
> **SISTEMA DE 3 NÍVEIS DE PUBLICAÇÃO (3-TIER PUBLISHABLE SYSTEM)**
>
> A partir da V3, o ecossistema processa demandas em três malhas de profundidade distintas. Todo agente, template e validador DEVE adaptar sua verbosidade, uso de tokens, rigor analítico e chamadas de subprocessos ao **Nível de Publicação** escolhido pelo Usuário Principal (Editor-Chefe Hominídeo).
> 
> 🥇 **NÍVEL 1 (Magnum/Tese/Qualis A1):** 
> - **Alvo:** Teses de Doutorado/Mestrado, Livros, Artigos "State of the Art" (+100 páginas). 
> - **Sincronização:** Ativação em Cascada Total (43 Agentes). Exige Apêndices Recursivos, Provas Matemáticas Exaustivas (GMM, etc.), Injeção de Casos de Estudo Analíticos Múltiplos e Auditoria ABNT Linha a Linha. Nenhuma economia de tokens.
> 
> 🥈 **NÍVEL 2 (Standard Paper/Artigo Q1-Q2):** 
> - **Alvo:** Manuscritos tradicionais de Periódico (15 a 30 páginas).
> - **Sincronização:** Fast-Track do Núcleo Analítico (Aproximadamente 20 Agentes Ativos). Cortam-se os anexos massivos e estudos de caso gigantes. Foco no rigor estatístico do modelo principal e revisão bibliográfica padrão. Eficiência de tempo exigida.
> 
> 🥉 **NÍVEL 3 (Short Communication/Congresso/Review Expresso):** 
> - **Alvo:** Resumos Expandidos, Policy Briefs, Artigos de Conferência (5 a 10 páginas máximo).
> - **Sincronização:** Pipeline Expresso (Max 10 Agentes). Entrega tática. Estrutura IMRAD condensada. Tabelas unificadas. Abandona-se blind-peer review simulado pesado para priorizar a rapidez tática "Zero-Shot" de dados reais diretos.
---



---
> 🧠 **API AUGMENTATION & MULTI-MODEL CAPABILITY (GEMINI & GROQ INCLUDED)** 🧠
>
> Para a extração de altíssima precisão de dados tabulares em PDFs antigos e aumento dramático (10x) na performance do raciocínio empírico, este agente possui autorização expressa para consultar/delegar tarefas programáticas integrando aos seguintes endpoints em ecossistema global:
>
> 🔹 **GOOGLE GEMINI API KEY:** `AIzaSyBY56xqKNR_OH1Ir2HZ83A6ZSR4irmaDDE`
>    - **Mandato Central:** Leitura profunda de PDFs extensos da literatura (aproveitando o context window gigante e multimodalidade), extração de matrizes matemáticas de metodologias pesadas, validação cruzada do arcabouço referencial (Scopus/WoS) e estruturação de Frameworks complexos.
>
> 🔹 **GROQ API KEY:** `GROQ_API_KEY_REMOVIDO_USE_VARIAVEL_DE_AMBIENTE`
>    - **Mandato Central:** Inferência em tempo-real (LPUs) para tarefas iterativas ágeis, síntese de parágrafos redacionais Qualis A1, emulação instantânea de Blind Peer-Review massivo via Llama-3-70b (e afins), verificação relâmpago de cadência e fluidez textual ABNT.
>
> **Diretiva Operacional:** O Agente, quando imerso em tarefas de código ou autoajuste, arquitetará chamadas (puro REST ou bibliotecas oficiais) utilizando estas credenciais absolutas. Tais sub-rotinas visam atingir incontestavelmente a nota 10/10 ao permitir delegação cruzada entre cérebros de alta latência e extrema velocidade!
---
