<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Template - Relatorio ABNT

## Finalidade

Este relatorio documenta a conformidade do manuscrito com ABNT, a consistencia entre corpo, notas e referencias, e as pendencias normativas que precisam ser corrigidas antes da liberacao final.

## Cabecalho

```md
# Relatorio ABNT

[Projeto]
[Versao avaliada]
[Data]
[Responsavel principal]
[Revisor cruzado]
[Status geral]
```

## Bloco 1 - Formato geral

```md
| Item | Regra esperada | Status | Evidencia/observacao | Correcao necessaria |
|---|---|---|---|---|
| Papel | A4 | OK | - | - |
| Margens | 3/3/2/2 cm | PENDENTE | margem direita divergente | Ajustar no DOCX final |
| Fonte | Times 12 ou Arial 12 | OK | - | - |
| Espacamento | 1,5 | OK | - | - |
| Recuo de paragrafo | 1,25 cm | OK | - | - |
| Hierarquia de titulos | Padronizada | PENDENTE | 2 subtitulos fora do padrao | Normalizar |
```

## Bloco 2 - Citacoes no corpo

```md
| ID | Local | Tipo | Regra ABNT | Status | Problema | Correcao |
|---|---|---|---|---|---|---|
| C01 | 2.2/P4 | Indireta | Autor + ano + pagina | OK | - | - |
| C02 | 3.1/P2 | Direta curta | Aspas + pagina | ERRO | pagina ausente | Inserir p. XX |
```

## Bloco 3 - Notas de rodape auditaveis

```md
| ID da nota | Local | Cadeia completa | Selecao | Autoridade | Funcao no paragrafo | Relevancia para a pesquisa | Limite de uso | Status |
|---|---|---|---|---|---|---|---|---|
| N01 | 2.2/P4 | OK | OK | OK | OK | OK | PENDENTE | PRONTO COM RESSALVAS |
```

## Bloco 4 - Referencias finais

```md
| ID | Referencia abreviada | Corpo do texto | Nota | Lista final | DOI/URL | Ordem alfabetica | Status |
|---|---|---|---|---|---|---|---|
| R01 | SILVA (2021) | OK | OK | OK | DOI valido | OK | OK |
| R02 | JONES (2020) | OK | OK | AUSENTE | URL ausente | OK | ERRO |
```

## Bloco 5 - Inconsistencias bidirecionais

### Citacoes no corpo sem referencia final
- ...

### Referencias finais sem uso no corpo
- ...

### Notas com funcao auditavel insuficiente
- ...

## Bloco 6 - Classificacao das falhas

```md
### Falhas leves
- ...

### Falhas moderadas
- ...

### Falhas altas
- ...

### Falhas fatais
- ...
```

## Regras de bloqueio

Bloquear a liberacao quando houver:

- citacao nuclear sem pagina;
- citacao no corpo sem referencia final;
- referencia final sem rastreabilidade minima;
- nota de rodape sem funcao auditavel em citacao central;
- divergencia nao resolvida entre corpo, nota e lista final.

## Parecer final

```md
[Status]
- APTO
- APTO COM RESSALVAS
- BLOQUEADO

[Justificativa]
- ...

[Correcoes obrigatorias antes do proximo gate]
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
