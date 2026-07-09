<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Template - Validacao Analitica

## Finalidade

Este arquivo documenta a validacao tecnica do plano de analise, dos testes aplicados, dos pressupostos, dos reportes numericos e dos limites inferenciais.

## Cabecalho

```md
# Validacao Analitica

[Projeto]
[Versao avaliada]
[Data]
[Responsavel principal]
[Revisor cruzado]
```

## Bloco 1 - Compatibilidade entre pergunta e metodo

```md
| Hipotese/objetivo | Tipo de dado | Analise proposta | Analise adequada? | Observacao |
|---|---|---|---|---|
| H1 | Contínuo | t de Student | Sim | Dados e comparacao compatveis |
| H2 | Categórico | Regressao linear | Nao | Trocar por regressao logistica ou outro modelo adequado |
```

## Bloco 2 - Pressupostos

```md
| Analise | Pressuposto | Verificacao | Status | Impacto | Acao |
|---|---|---|---|---|---|
| ANOVA | Homogeneidade | Levene | OK | - | - |
| Regressao | Multicolinearidade | VIF | PENDENTE | Risco medio | Verificar antes do reporte final |
```

## Bloco 3 - Reporte dos resultados

```md
| Resultado | Estatistica | gl | p | IC95% | Efeito | Reporte completo? | Problema |
|---|---|---|---|---|---|---|---|
| R1 | t = 3,21 | 48 | 0,002 | [0,20; 0,66] | d = 0,91 | Sim | - |
| R2 | F = 5,11 | 2,45 | 0,011 | - | - | Nao | Falta IC e efeito |
```

## Bloco 4 - Limites inferenciais

```md
### Pontos de overclaim detectados
- ...

### Pontos em que a discussao excede o desenho
- ...

### Ajustes obrigatorios de linguagem
- ...
```

## Bloco 5 - Parecer tecnico

```md
[Status]
- APTO
- APTO COM RESSALVAS
- BLOQUEADO

[Razao principal]
- ...

[Correcoes obrigatorias]
- ...
```




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
