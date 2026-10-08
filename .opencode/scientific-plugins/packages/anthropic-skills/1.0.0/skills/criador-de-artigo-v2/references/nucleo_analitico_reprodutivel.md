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
