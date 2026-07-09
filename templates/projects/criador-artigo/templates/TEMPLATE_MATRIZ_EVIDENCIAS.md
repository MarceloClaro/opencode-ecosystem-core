<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Template - Matriz de Evidencias

## Finalidade

Este arquivo mapeia cada afirmacao relevante do manuscrito a uma evidencia verificavel, localizada e funcional. Ele deve ser preenchido antes da redacao final de cada secao substantiva.

## Regras de preenchimento

- uma linha por afirmacao verificavel;
- nao agrupar afirmacoes distintas na mesma linha;
- toda afirmacao central deve ter fonte principal;
- toda afirmacao controversa deve ter, quando possivel, fonte de contraste;
- toda localizacao deve ser precisa;
- todo limite de uso deve ser explicitado.

## Cabecalho do arquivo

```md
# Matriz de Evidencias

[Projeto]
[Versao]
[Data]
[Responsavel principal]
[Revisor cruzado]
[Gate]
[Secao(s) coberta(s)]
```

## Tabela principal

```md
| ID da afirmacao | Secao/paragrafo | Tipo de afirmacao | Texto resumido da afirmacao | Fonte principal | Fonte de contraste | Localizacao exata | Funcao da citacao | O que a fonte sustenta | O que a fonte nao sustenta | Risco | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A01 | 2.1/P3 | Definicao | X e definido como... | AUTOR (2019) | AUTOR (2021) | p. 14-16 | Delimitar conceito | Definicao teorica | Nao valida uso empirico direto | Medio | PRONTO |
| A02 | 3.2/P4 | Metodo | O instrumento Y apresenta consistencia adequada | AUTOR (2022) | - | p. 55; Tabela 2 | Justificar instrumento | Alfa e contexto de validacao | Nao generaliza para toda populacao | Medio | PRONTO COM RESSALVAS |
```

## Tipos de afirmacao permitidos

- `Definicao`
- `Dado contextual`
- `Hipotese`
- `Lacuna`
- `Metodo`
- `Resultado`
- `Contraste`
- `Limitacao`
- `Interpretacao`
- `Implicacao`

## Checkpoint por secao

```md
## Checkpoint - [Secao]

- Quantidade de afirmacoes mapeadas:
- Quantidade de afirmacoes sem contraste quando necessario:
- Quantidade de afirmacoes com risco alto:
- Quantidade de afirmacoes bloqueadas:

### Pendencias criticas
- ...

### Observacoes do revisor cruzado
- ...
```

## Regras de bloqueio

Marcar `Status = BLOQUEADO` quando:

- a fonte principal nao tiver texto integral lido;
- a localizacao for imprecisa;
- a afirmacao exceder o que a fonte sustenta;
- o tipo de afirmacao exigir contraste e nao houver contraponto minimamente plausivel;
- a mesma fonte estiver sendo reutilizada indevidamente para conclusoes diferentes sem nova localizacao.

## Checklist de fechamento

```md
□ Toda afirmacao substantiva da secao aparece na matriz?
□ Toda afirmacao possui fonte principal localizada?
□ Toda afirmacao controversa possui fonte de contraste ou justificativa de ausencia?
□ Todo limite de uso foi explicitado?
□ O revisor cruzado marcou os riscos altos?
□ O gerente pode entender a cadeia de prova sem depender da memoria do agente?
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
