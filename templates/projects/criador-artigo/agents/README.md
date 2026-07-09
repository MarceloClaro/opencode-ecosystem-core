<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

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
45. `44_agente_correcao_textual_qualis.md`
46. `45_agente_refinamento_argumentacao.md`
47. `DISPATCHER_ATIVACAO.md`

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
- `Agente de Correção Textual e Densidade Qualis` -> `log_correcao_iterativa.md`
- `Agente de Refinamento de Argumentação` -> `mapa_debate_teorico_corrigido.md`

## Estado de cada entrega

- `PRONTO`
- `PRONTO COM RESSALVAS`
- `BLOQUEADO`

So o `Editor-Chefe PhD / Gerente de Qualis A1` pode converter uma entrega em `APROVADA PARA PROXIMA ETAPA`.

---
> ⚠️ **DIRETIVA GLOBAL DE SINCRONIZAÇÃO MASWOS (ECOSSISTEMA V4.0)** ⚠️
> **SISTEMA DE 3 NÍVEIS DE PUBLICAÇÃO (3-TIER PUBLISHABLE SYSTEM)**
>
> A partir da V4, o ecossistema processa demandas em três malhas de profundidade distintas. Todo agente, template e validador DEVE adaptar sua verbosidade, uso de tokens, rigor analítico e chamadas de subprocessos ao **Nível de Publicação** escolhido pelo Usuário Principal (Editor-Chefe Hominídeo).
> 
> 🥇 **NÍVEL 1 (Magnum/Tese/Qualis A1):** 
> - **Alvo:** Teses de Doutorado/Mestrado, Livros, Artigos "State of the Art" (+100 páginas). 
> - **Sincronização:** Ativação em Cascada Total (45 Agentes - Ecossistema V4 Iterativo). Exige Loop de Correção Ativa (A44/A45) até atingir nota 10/10, Apêndices Recursivos, Provas Matemáticas Exaustivas (GMM, etc.), Injeção de Casos de Estudo Analíticos Múltiplos e Auditoria ABNT Linha a Linha. Nenhuma economia de tokens.
> 
> 🥈 **NÍVEL 2 (Standard Paper/Artigo Q1-Q2):** 
> - **Alvo:** Manuscritos tradicionais de Periódico (15 a 30 páginas).
> - **Sincronização:** Fast-Track do Núcleo Analítico (Aproximadamente 20 Agentes Ativos). Cortam-se os anexos massivos e estudos de caso gigantes. Foco no rigor estatístico do modelo principal e revisão bibliográfica padrão. Eficiência de tempo exigida.
> 
> 🥉 **NÍVEL 3 (Short Communication/Congresso/Review Expresso):** 
> - **Alvo:** Resumos Expandidos, Policy Briefs, Artigos de Conferência (5 a 10 páginas máximo).
> - **Sincronização:** Pipeline Expresso (Max 10 Agentes). Entrega tática. Estrutura IMRAD condensada. Tabelas unificadas. Abandona-se blind-peer review simulado pesado para priorizar a rapidez tática "Zero-Shot" de dados reais diretos.
---
