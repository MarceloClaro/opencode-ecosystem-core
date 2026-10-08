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
