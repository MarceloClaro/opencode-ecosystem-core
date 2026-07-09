<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Template de Handoff Qualis A1

## Finalidade

Este template deve ser usado:

- em toda passagem entre agentes;
- em toda submissao ao `Editor-Chefe PhD / Gerente de Qualis A1`;
- em todo gate de aprovacao, bloqueio, retrabalho ou liberacao parcial.

O objetivo e tornar cada handoff:

- rastreavel;
- comparavel;
- revisavel por terceiro;
- robusto o suficiente para sustentar um fluxo com rigor Qualis A1.

---

## Regra de uso

### Quando o template e obrigatorio

Uso obrigatorio para:

- qualquer saida que alimente outro agente;
- qualquer secao do manuscrito;
- qualquer pacote de referencias, citacoes, visualizacoes ou validacao estatistica;
- qualquer decisao de `PRONTO`, `PRONTO COM RESSALVAS` ou `BLOQUEADO`.

### Quando o template pode ser abreviado

So pode ser abreviado em comunicacoes internas de baixo risco que:

- nao alterem escopo;
- nao movam a entrega para outro gate;
- nao congelem versao;
- nao impliquem aprovacao.

---

## Template completo

```md
[ID do handoff]
[Data e hora]
[Gate atual]
[Etapa macro]
[Agente remetente]
[Agente destinatario]
[Versao da entrega]
[Status sugerido]

[Objetivo desta entrega]
- ...

[Escopo coberto]
- ...

[Escopo explicitamente nao coberto]
- ...

[Entradas recebidas]
- arquivo:
- versao:
- status de confianca:

[Entradas congeladas]
- ...

[Entradas ainda provisórias]
- ...

[Saidas produzidas]
- arquivo:
- versao:
- finalidade:
- status:

[Criterios de aceite prometidos]
- ...

[Criterios de aceite efetivamente atendidos]
- ...

[Criterios ainda nao atendidos]
- ...

[Resumo executivo da entrega]
- ...

[Mapa de evidencias desta entrega]
- afirmacao/decisao:
- fonte/log/matriz/artefato associado:
- localizacao:

[Pendencias abertas]
- id:
- descricao:
- impacto:
- responsavel sugerido:

[Riscos]
- severidade:
- descricao:
- impacto no manuscrito:
- condicao de bloqueio:

[Dependencias para o proximo agente]
- ...

[O que o proximo agente esta autorizado a alterar]
- ...

[O que o proximo agente NAO pode alterar sem escalar]
- ...

[Pontos que exigem validacao cruzada]
- ...

[Checklist Qualis A1 do handoff]
- problema/objetivo coerentes?
- evidencia localizavel?
- citacao/rodape/referencia consistentes?
- metodo/analise compativeis?
- linguagem sem overclaim?
- ABNT preservada?
- **TODOS os parágrafos cumprem a regra de Densidade Máxima (6 frases: Tópico+Base+Citação+Análise+Contraponto+Conexão)?**
- **O fluxo do texto é orgânico, fluido e não-robótico (evitou repetição circular, verbosidade e "encheção de linguiça" apenas para crescer o texto)?**
- **A narrativa é inerentemente autodidática e facilmente compreensível para leitores de outros campos?**
- **A volumetria atual sustenta a meta inegociável de 110 páginas / 45.000 palavras mediante progressão lógica e verticalização técnica da temática?**
- **O texto gerado está estritamente em Português Brasileiro formal?**

[Decisao sugerida]
- PRONTO
- PRONTO COM RESSALVAS
- BLOQUEADO

[Justificativa da decisao]
- ...

[Pedido ao gerente]
- aprovar
- aprovar com ressalvas
- reprovar e devolver
- congelar e escalar
```

---

## Versao minima aceitavel

Quando o handoff for simples, ainda assim ele deve conter no minimo:

```md
[Gate]
[Agente remetente]
[Agente destinatario]
[Objetivo]
[Entradas congeladas]
[Saidas produzidas]
[Pendencias]
[Riscos]
[Decisao sugerida]
```

Se qualquer um desses campos faltar, o handoff nao deve ser considerado valido.

---

## Como preencher cada campo

### `[ID do handoff]`

Use um identificador unico e rastreavel, por exemplo:

```md
H-G2-A2-A3-001
```

Formato recomendado:

- `H` = handoff
- `G2` = gate 2
- `A2-A3` = remetente para destinatario
- `001` = sequencial

### `[Status sugerido]`

Use apenas:

- `PRONTO`
- `PRONTO COM RESSALVAS`
- `BLOQUEADO`

Nunca use estados vagos como:

- quase pronto
- em tese pronto
- pode seguir mais ou menos

### `[Status de confianca]`

Classifique cada entrada recebida como:

- `alta`
- `media`
- `baixa`

Exemplos:

- `alta`: entrada aprovada pelo gerente
- `media`: entrada revisada, mas ainda com ressalvas
- `baixa`: rascunho, exploracao ou dado nao congelado

### `[Mapa de evidencias desta entrega]`

Este campo e obrigatorio em entregas que:

- criam argumento;
- introduzem dado;
- definem conceito;
- justificam metodo;
- resumem literatura;
- produzem interpretacao.

Se nao houver mapa de evidencias, a entrega nao pode sustentar texto de alto rigor.

### `[O que o proximo agente NAO pode alterar sem escalar]`

Use este campo para proteger:

- problema de pesquisa;
- hipotese principal;
- recorte empirico;
- definicoes conceituais ja congeladas;
- resultados aprovados;
- decisoes estatisticas ja validadas.

---

## Escala de risco obrigatoria

Todo handoff deve classificar riscos com uma destas severidades:

- `baixa`
- `media`
- `alta`
- `fatal`

### Exemplos de risco

`baixa`
- repeticao estilistica localizada

`media`
- nota de rodape ainda insuficientemente especifica

`alta`
- afirmacao central ainda sem fonte forte

`fatal`
- secao depende de citacao nao localizada ou interpretacao estatistica indevida

Se houver risco `fatal`, a decisao sugerida nao pode ser `PRONTO`.

---

## Regras de bloqueio automatico

O handoff deve sair como `BLOQUEADO` se ocorrer qualquer um destes casos:

- entrada principal ainda nao aprovada pelo gerente;
- fonte central sem texto integral;
- citacao sem pagina ou localizacao equivalente;
- divergencia estrutural entre objetivo e secao;
- metodo e analise sem compatibilidade demonstrada;
- conclusao com informacao nova;
- referencia no corpo sem cadeia fechada ate a lista final;
- conflito entre agentes ainda nao resolvido.

---

## Checklist de rigor antes de enviar

Antes de enviar qualquer handoff, o agente remetente deve verificar:

- o objetivo desta entrega esta claro em uma frase?
- o proximo agente consegue trabalhar sem depender da minha memoria tacita?
- os riscos foram escritos com honestidade?
- esta claro o que esta congelado e o que ainda esta aberto?
- ha algum ponto que parece pronto, mas ainda depende de validacao?
- a entrega resistiria a uma leitura critica de banca ou parecerista?

Se a resposta for `nao` para qualquer uma dessas perguntas, revise o handoff antes de enviar.

---

## Regra final

Handoff sem granularidade suficiente nao acelera o processo; ele apenas desloca erro para frente.

Neste projeto, cada handoff deve reduzir incerteza, nao redistribui-la silenciosamente.




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
