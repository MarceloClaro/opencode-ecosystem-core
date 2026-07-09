<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Kit de Templates do Pipeline

## Finalidade

Este diretorio contem templates concretos para os artefatos centrais do fluxo multiagente. O objetivo e reduzir ambiguidade de formato, aumentar comparabilidade entre entregas e manter rigor Qualis A1 ao longo de todo o pipeline.

## Como usar

- cada agente deve preencher os templates correspondentes aos seus artefatos obrigatorios;
- o template nao substitui os criterios do `SKILL.md`, dos prompts em `agents/` ou dos documentos em `references/`;
- o template serve como molde minimo obrigatorio, nao como teto de detalhamento.

## Templates disponiveis

1. `TEMPLATE_MATRIZ_EVIDENCIAS.md`
2. `TEMPLATE_RELATORIO_ABNT.md`
3. `TEMPLATE_AUDITORIA_FINAL_QUALIS.md`
4. `TEMPLATE_MANIFESTO_PACOTE_FINAL.md`
5. `TEMPLATE_LOG_BUSCA.md`
6. `TEMPLATE_TRIAGEM_FONTES.md`
7. `TEMPLATE_MAPA_CITACOES.md`
8. `TEMPLATE_RELATORIO_CONSISTENCIA.md`
9. `TEMPLATE_VALIDACAO_ANALITICA.md`
10. `TEMPLATE_MANIFESTO_REPRODUTIBILIDADE.md`
11. `TEMPLATE_AMBIENTE_EXECUCAO.md`
12. `TEMPLATE_CATALOGO_DATASETS.md`
13. `TEMPLATE_CODEBOOK_DADOS.md`
14. `TEMPLATE_AUDITORIA_CODIGO.md`
15. `TEMPLATE_AUDITORIA_FORMULAS.md`
16. `TEMPLATE_REGISTRO_EXPERIMENTOS.md`
17. `TEMPLATE_RELATORIO_BENCHMARK_ROBUSTEZ.md`
18. `TEMPLATE_PLANO_INFERENCIA_AVANCADA.md`
19. `TEMPLATE_ANEXO_MATEMATICA_APLICADA.md`
20. `TEMPLATE_PIPELINE_VISAO_MULTIMODAL.md`

## Regra central

Preencher um template nao significa aprovar a entrega.

A aprovacao continua dependente de:

- revisao cruzada;
- handoff valido;
- decisao formal do `Editor-Chefe PhD / Gerente de Qualis A1`.

## Responsabilidade por template

- `templates/TEMPLATE_LOG_BUSCA.md` -> `Agente de Busca e Curadoria`
- `templates/TEMPLATE_TRIAGEM_FONTES.md` -> `Agente de Busca e Curadoria`
- `templates/TEMPLATE_MATRIZ_EVIDENCIAS.md` -> `Agente de Evidencias e Citacoes`
- `templates/TEMPLATE_MAPA_CITACOES.md` -> `Agente de Evidencias e Citacoes`
- `templates/TEMPLATE_VALIDACAO_ANALITICA.md` -> `Agente de Estatistica e Analise`
- `templates/TEMPLATE_MANIFESTO_REPRODUTIBILIDADE.md` -> `Agente de Framework Reprodutivel e Ambientes`
- `templates/TEMPLATE_AMBIENTE_EXECUCAO.md` -> `Agente de Framework Reprodutivel e Ambientes`
- `templates/TEMPLATE_CATALOGO_DATASETS.md` -> `Agente de Engenharia de Dados, Datasets e Proveniencia`
- `templates/TEMPLATE_CODEBOOK_DADOS.md` -> `Agente de Engenharia de Dados, Datasets e Proveniencia`
- `templates/TEMPLATE_AUDITORIA_CODIGO.md` -> `Agente de Auditoria de Codigo e Documentacao Tecnica`
- `templates/TEMPLATE_AUDITORIA_FORMULAS.md` -> `Agente de Matematica Aplicada e Modelagem Formal`
- `templates/TEMPLATE_REGISTRO_EXPERIMENTOS.md` -> agentes analiticos especializados e de benchmark
- `templates/TEMPLATE_RELATORIO_BENCHMARK_ROBUSTEZ.md` -> `Agente de Benchmarking, Ablacao e Robustez`
- `templates/TEMPLATE_PLANO_INFERENCIA_AVANCADA.md` -> `Agente de Estatistica Avancada e Inferencia`
- `templates/TEMPLATE_ANEXO_MATEMATICA_APLICADA.md` -> `Agente de Matematica Aplicada e Modelagem Formal`
- `templates/TEMPLATE_PIPELINE_VISAO_MULTIMODAL.md` -> `Agente de Visao Computacional e Multimodalidade`
- `templates/TEMPLATE_RELATORIO_CONSISTENCIA.md` -> `Agente de Consistencia Interna`
- `templates/TEMPLATE_RELATORIO_ABNT.md` -> `Agente de Auditoria Bibliografica e ABNT`
- `templates/TEMPLATE_AUDITORIA_FINAL_QUALIS.md` -> `Agente de QA Qualis A1`
- `templates/TEMPLATE_MANIFESTO_PACOTE_FINAL.md` -> `Agente de Integracao Editorial e DOCX`




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
