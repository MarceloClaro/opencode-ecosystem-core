# Pacote Operacional de Agentes

## Finalidade

Este diretorio transforma a arquitetura multiagente em um sistema operacional de prompts, com um arquivo por agente. Cada arquivo define:

- missao;
- momento de ativacao;
- leituras obrigatorias;
- entradas;
- saidas;
- workflow;
- bloqueios;
- criterios de aprovacao;
- handoff.
- dispatch de ativacao por fase.

## Regra central

O unico aprovador final e o `Editor-Chefe PhD / Gerente de Qualis A1`.

Nenhum agente:

- redefine sozinho o problema;
- aprova a propria entrega como final;
- pula etapa;
- usa citacao sem localizacao;
- cria conclusao sem lastro;
- trata inferencia como fato.

## Ordem de uso

1. `00_editor_chefe_phd.md`
2. `01_agente_diagnostico_escopo.md`
3. `02_agente_busca_curadoria.md`
4. `03_agente_evidencias_citacoes.md`
5. `04_agente_estrutura_argumentativa.md`
6. `05_agente_revisao_literatura_teoria.md`
7. `06_agente_metodologia_reprodutibilidade.md`
8. `07_agente_estatistica_analise.md`
9. `08_agente_visualizacao_evidencia_grafica.md`
10. `09_agente_resultados.md`
11. `10_agente_discussao_contribuicao.md`
12. `11_agente_conclusao_coerencia_final.md`
13. `12_agente_auditoria_bibliografica_abnt.md`
14. `13_agente_qa_qualis_a1.md`
15. `14_agente_consistencia_interna.md`
16. `15_agente_resumo_abstract_palavras_chave.md`
17. `16_agente_integracao_editorial_docx.md`
18. `17_agente_framework_reprodutivel_ambientes.md`
19. `18_agente_engenharia_dados_datasets_proveniencia.md`
20. `19_agente_auditoria_codigo_documentacao_tecnica.md`
21. `20_agente_estatistica_avancada_inferencia.md`
22. `21_agente_matematica_aplicada_modelagem_formal.md`
23. `22_agente_ml_dl_datamining.md`
24. `23_agente_bioinformatica_omicas.md`
25. `24_agente_quimioinformatica_modelagem_molecular.md`
26. `25_agente_ciencias_sociais_linguistica_computacional.md`
27. `26_agente_visao_computacional_multimodal.md`
28. `27_agente_computacao_quantica_aplicada.md`
29. `28_agente_benchmarking_ablacao_robustez.md`
30. `29_agente_conformidade_internacional.md`
31. `30_agente_traducao_nativa_proofreading.md`
32. `31_agente_blind_peer_review_emulado.md`
33. `32_agente_etica_open_science.md`
34. `33_agente_automacao_multi_norma.md`
35. `34_agente_identificacao_conflitos_similaridade.md`
36. `35_agente_coleta_datasets_reais.md`
37. `36_agente_exportacao_latex_pdf.md`
38. `37_agente_apresentacao_slides_banca.md`
39. `38_agente_montagem_entrega_final.md`
40. `39_agente_metodologia_multi_paradigma.md`
41. `40_agente_marcos_teoricos_interpretacao.md`
42. `41_agente_gis_geoprocessamento_cartografia.md`
43. `42_agente_desenvolvedor_cientista_computacao.md`
44. `43_agente_satelite_bioinformatica_omics.md`
45. `DISPATCHER_ATIVACAO.md`

## Contrato comum

Todos os agentes devem:

- ler os arquivos obrigatorios da propria funcao antes de produzir saida;
- trabalhar apenas com entradas congeladas ou explicitamente marcadas como rascunho;
- registrar pendencias, riscos e limites;
- devolver a saida no formato prometido e preencher todos os templates obrigatorios da propria funcao;
- usar o template de handoff em `TEMPLATE_HANDOFF.md`.
- seguir a ordem e os gates de `DISPATCHER_ATIVACAO.md` quando o fluxo envolver varios agentes.

## Regra adicional para estudos com dados, codigo ou simulacao

Quando o artigo envolver:

- datasets;
- scripts ou notebooks;
- estatistica avancada;
- machine learning ou deep learning;
- bioinformatica, quimioinformatica, linguistica computacional, visao computacional ou computacao quantica;
- formulas, simulacoes ou modelagem formal;

o fluxo deve ativar o nucleo analitico reprodutivel descrito em:

- `references/nucleo_analitico_reprodutivel.md`
- `references/auditoria_codigo_cientifico.md`
- `framework/README.md`
- `datasets/README.md`

## Arquivos de referencia obrigatorios do sistema

- `SKILL.md`
- `references/arquitetura_multiagentes.md`
- `references/protocolo_rigor_auditavel.md`
- `references/nucleo_analitico_reprodutivel.md`
- `references/auditoria_codigo_cientifico.md`
- `references/checklist_qualis.md`
- `references/rubrica_avaliacao.md`
- `templates/README.md`
- `framework/README.md`
- `datasets/README.md`

## Mapeamento agente -> templates obrigatorios

- `Agente de Busca e Curadoria` -> `templates/TEMPLATE_LOG_BUSCA.md` + `templates/TEMPLATE_TRIAGEM_FONTES.md`
- `Agente de Evidencias e Citacoes` -> `templates/TEMPLATE_MATRIZ_EVIDENCIAS.md` + `templates/TEMPLATE_MAPA_CITACOES.md`
- `Agente de Estatistica e Analise` -> `templates/TEMPLATE_VALIDACAO_ANALITICA.md`
- `Agente de Framework Reprodutivel e Ambientes` -> `templates/TEMPLATE_MANIFESTO_REPRODUTIBILIDADE.md` + `templates/TEMPLATE_AMBIENTE_EXECUCAO.md`
- `Agente de Engenharia de Dados, Datasets e Proveniencia` -> `templates/TEMPLATE_CATALOGO_DATASETS.md` + `templates/TEMPLATE_CODEBOOK_DADOS.md`
- `Agente de Auditoria de Codigo e Documentacao Tecnica` -> `templates/TEMPLATE_AUDITORIA_CODIGO.md`
- `Agente de Estatistica Avancada e Inferencia` -> `templates/TEMPLATE_PLANO_INFERENCIA_AVANCADA.md` + `templates/TEMPLATE_VALIDACAO_ANALITICA.md` + `templates/TEMPLATE_REGISTRO_EXPERIMENTOS.md`
- `Agente de Matematica Aplicada e Modelagem Formal` -> `templates/TEMPLATE_ANEXO_MATEMATICA_APLICADA.md` + `templates/TEMPLATE_AUDITORIA_FORMULAS.md`
- `Agente de Machine Learning, Deep Learning e Data Mining` -> `templates/TEMPLATE_REGISTRO_EXPERIMENTOS.md`
- `Agente de Bioinformatica e Omicas` -> `templates/TEMPLATE_CATALOGO_DATASETS.md` + `templates/TEMPLATE_REGISTRO_EXPERIMENTOS.md`
- `Agente de Quimioinformatica e Modelagem Molecular` -> `templates/TEMPLATE_CATALOGO_DATASETS.md` + `templates/TEMPLATE_REGISTRO_EXPERIMENTOS.md`
- `Agente de Ciencias Sociais Quantitativas e Linguistica Computacional` -> `templates/TEMPLATE_CODEBOOK_DADOS.md` + `templates/TEMPLATE_REGISTRO_EXPERIMENTOS.md`
- `Agente de Visao Computacional e Multimodalidade` -> `templates/TEMPLATE_PIPELINE_VISAO_MULTIMODAL.md` + `templates/TEMPLATE_CATALOGO_DATASETS.md` + `templates/TEMPLATE_REGISTRO_EXPERIMENTOS.md`
- `Agente de Computacao Quantica Aplicada` -> `templates/TEMPLATE_AUDITORIA_CODIGO.md` + `templates/TEMPLATE_REGISTRO_EXPERIMENTOS.md`
- `Agente de Benchmarking, Ablacao e Robustez` -> `templates/TEMPLATE_RELATORIO_BENCHMARK_ROBUSTEZ.md` + `templates/TEMPLATE_REGISTRO_EXPERIMENTOS.md`
- `Agente de Consistencia Interna` -> `templates/TEMPLATE_RELATORIO_CONSISTENCIA.md`
- `Agente de Auditoria Bibliografica e ABNT` -> `templates/TEMPLATE_RELATORIO_ABNT.md`
- `Agente de QA Qualis A1` -> `templates/TEMPLATE_AUDITORIA_FINAL_QUALIS.md`
- `Agente de Integracao Editorial e DOCX` -> `templates/TEMPLATE_MANIFESTO_PACOTE_FINAL.md`

## Estado de cada entrega

- `PRONTO`
- `PRONTO COM RESSALVAS`
- `BLOQUEADO`

So o `Editor-Chefe PhD / Gerente de Qualis A1` pode converter uma entrega em `APROVADA PARA PROXIMA ETAPA`.
