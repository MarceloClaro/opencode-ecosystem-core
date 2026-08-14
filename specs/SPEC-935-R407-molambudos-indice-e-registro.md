---
spec_id: SPEC-935-R407
title: Molambudos — Índice de Fragmentos divergente entre edições e oscilação do tratamento ao leitor em chinês
component: scripts/molambudos_indice.py, scripts/molambudos_canone.py, projetos/molambudos/Molambudos_VictoriaRegia
status: verified
test_file: tests/test_r407_molambudos_indice_e_registro.py
---

# SPEC-935-R407 — O Aparato de Navegação e o Pronome

**Data:** 2026-08-08
**Motivação:** *"posso concluir a revisão das 3 edições? todos os pontos estão
corrigidos para partir para o trilíngue?"* — a pergunta obrigou a olhar para o
que a trilíngue herda das três. A resposta foi não, e por dois motivos que
nenhum ciclo anterior tinha examinado.

## 1. O que a pergunta revelou

A trilíngue faz `\input` dos **mesmos** arquivos de fragmento das três edições:
não guarda cópias. Logo, as correções factuais do R405/R406 propagaram
sozinhas. Mas ela mantém **índice e frontmatter próprios** — e é aí que estava
o problema.

### 1.1 O Índice de Fragmentos estava quebrado em três das quatro edições

Mantido à mão em quatro arquivos independentes, divergiu:

| Edição | Entradas | Faltavam |
|---|---|---|
| pt | **84/84** | — |
| en | 73/84 | DOC-20…DOC-27, LUC-13, LUC-14, MEM-27 |
| zh | 83/84 | MEM-27 |
| tri | 77/84 | CONT-08…CONT-13, MEM-27 |

Num livro-hipertexto o índice não é enfeite: é o instrumento com que o leitor
localiza um fragmento pelo nome. O leitor inglês não tinha como achar oito
documentos, entre eles `DOC-25` — *O Homem do Pano Preto*.

Além das ausências, o verificador achou **26 divergências**, incluindo três que
são contradição de cânone sobrevivendo no aparato:

* `DOC-26` rotulado **1981** em zh e tri — o ano que o R406 removeu do corpus
  por matar Oliveira dois anos depois de ele ter desaparecido sem corpo;
* `DOC-09` anunciado como *Escala do 1.261* em en, zh e tri — 1.261 é
  Oliveira; o fragmento é a escala do **1.263**, o leitor;
* `MEM-27` com um título por edição (*A Última Página* / *Joaquim's Epilogue* /
  *循环*), e em português **repetindo o título de MEM-26**.

Somavam-se: contagens declaradas nos cabeçalhos que não batiam com as entradas
listadas (a trilíngue anunciava 7 fragmentos numa parte de 14), duas
transliterações chinesas diferentes para a mesma autora real (Daniela Arbex), e
o rótulo de `DOC-27` reduzido a *档案* ("arquivo") em vez do nome do padre.

### 1.2 MEM-27 não é ``A Última Página''

MEM-26 é a última página, escrita três dias antes da morte. MEM-27 é o **verso
dela**, escrito *depois*: «Eu pensei que ia acabar quando eu morresse.» Não é a
última página — é o que vem depois dela. O título passa a ser **A Página
Seguinte** / *The Next Page* / *下一页*, que é a própria frase do fragmento:
«Eu sou só a primeira página. Você é a página seguinte.»

## 2. O pronome, que é metade do efeito

Em chinês, 您 é o tratamento formal e 你 o íntimo. A medição por família de
fragmentos revelou uma convenção deliberada e boa:

| Família | 您 (formal) | 你 (íntimo) |
|---|---|---|
| CONT — a obra fala com o leitor | **528** | 1 |
| MEM — personagens falam entre si | 83 | **189** |

A obra interpela o leitor com o 您 clínico e cerimonioso de um prontuário; as
personagens conversam em 你. É exatamente o que se quer num livro que se
apresenta como arquivo pericial e transforma o leitor em paciente 1.263.

Só que o **aparato não seguia a própria convenção**: `zh/main_zh.tex`,
`tri/main_tri.tex`, os dois frontmatters e o dossiê acadêmico tratavam o leitor
por 你 — 69 ocorrências. E `CONT-02` tinha duas frases seguidas oscilando:

> 它也已经在**你**体内了。 / **您**只是还没有看见。

Pior: o **dossiê acadêmico citava a obra com o pronome errado**, e afirmava que
«27 dos 84 fragmentos mobilizam 你» quando o marcador real é 您.

70 ocorrências corrigidas no aparato e em CONT-02. Os 189 你 das memórias
ficaram intactos — formalizar a fala das personagens teria estragado o que
estava certo, e há um teste para isso.

## 3. A causa é estrutural, e a correção também

Quatro cópias manuais da mesma informação divergem: é uma questão de tempo.
`scripts/molambudos_indice.py` passa a **derivar** o índice do corpus — ordem e
rótulos vêm do português (edição de referência), títulos são lidos do próprio
fragmento de cada idioma, contagens dos cabeçalhos são calculadas.

```
python3 -m scripts.molambudos_indice verificar   # sai != 0 se divergir
python3 -m scripts.molambudos_indice gerar       # reescreve as quatro
```

### 3.0 Uma segunda cópia do corpus, dois ciclos atrás

A suíte completa reprovou num teste do R384 que exige que
`projetos/molambudos/fragmentos` espelhe a edição. Existe uma **árvore canônica
paralela** — 84 fragmentos em português, fora de qualquer build — e ela divergia
em dois arquivos: `MEM-27` (deste ciclo) e **`DOC-07` (do ciclo anterior)**.

Ou seja: a árvore canônica continuava afirmando que **«Dr. Heitor Oliveira
faleceu em 1981»**, a contradição que o R406 declarou eliminada. A declaração
daquele ciclo — «`1981` desapareceu da obra» — valia só para a edição. A spec do
R406 foi corrigida.

Uma cópia do corpus fora de verificação é uma contradição esperando o momento de
ser usada. A árvore foi sincronizada e entrou na cobertura do verificador, com
checagem própria de divergência (`cópia divergente`), provada por reintrodução.

### 3.1 O verificador de cânone não olhava o aparato

O R406 varria `fragmentos/`, `en/fragmentos/` e `zh/fragmentos/` — e por isso
não viu o `1981` do índice nem o `1.261` do DOC-09. `_aparato()` acrescenta os
76 arquivos restantes (mains, frontmatter, dossiês) à checagem de afirmações
proibidas. Provado por reintrodução: com `1981` de volta no índice chinês, o
verificador acusa `[contradição] … edição aparato → zh/main_zh.tex`. Antes,
passava em silêncio.

## 4. Erro cometido e corrigido no ciclo

A substituição do título chinês de MEM-27 (`循环` → `下一页`) atingiu **três**
ocorrências, não duas: a terceira estava no corpo da nota do editor —
«循环不会闭合：它转移» ("o ciclo não se fecha: transfere-se") — que virou "a
próxima página não se fecha", sem sentido. Pego pela conferência de contagem
antes de seguir, e revertido só naquela ocorrência. O `diff` contra o backup
mostra apenas as duas linhas de título alteradas.

É a quinta vez nesta série de ciclos que uma substituição ampla demais em CJK
produz um defeito; o padrão está registrado no CORRIGENDUM.

## 5. O que este ciclo **não** resolve

Fica um ponto que é decisão do autor, não defeito verificável, e por isso não
foi tocado: **MEM-26 e MEM-27 dizem que Joaquim carregou a criatura por 62
anos, contando da vala de 1915** — o que dá 1977, não 1979. As outras
ocorrências do número fecham (DOC-03 e DOC-10: 62 anos de internação,
1917→1979; DOC-26: ciclo de 62 anos da entidade, 1853→1915). Pode ser
imprecisão deliberada do narrador possuído e moribundo, e o autor decide.

Os três dossiês afirmam que «27 dos 84 fragmentos sustentam o endereçamento em
segunda pessoa», sem declarar o critério. A contagem medida depende do limiar:
54 fragmentos contêm ao menos uma ocorrência de *você*, 29 contêm cinco ou
mais, 23 contêm sete ou mais. O número 27 fica dentro da faixa defensável para
«sustentado», e por isso **não foi alterado** — mas um dossiê acadêmico deveria
declarar o limiar que usa. Fica anotado como lacuna de método, não como erro.

As traduções en/zh continuam de autoria própria e seguem exigindo revisor
nativo. O verificador de índice garante que o índice **corresponde** ao corpus;
não garante que um título traduzido seja o melhor título.

### 5.1 Consequência colateral registrada

A correção do pronome quebrou o preflight: o auditor `audit_r362_pdf_layout.py`
guardava o texto do abre-parte chinês como fixture literal (`污染（你）`), e com
o livro corrigido a página deixou de casar com a lista de exceções de
sangramento — virando `unassigned_full_bleed` na página 289 da edição chinesa.
O fixture foi atualizado para `污染（您）`. A verificação **não** foi afrouxada:
continua exigindo correspondência exata do marcador.

## 6. Critérios de aceitação

1. As quatro edições indexam os 84 fragmentos, na mesma ordem. ✔
2. Todo título do índice bate com o título do próprio fragmento. ✔
3. Nenhum título se repete dentro de uma mesma edição. ✔
4. Contagens dos cabeçalhos batem com as entradas listadas. ✔
5. Nenhum 你 no aparato; nenhum 你 na Contaminação; 你 preservado no diálogo
   das memórias. ✔
6. O verificador de cânone cobre o aparato e acusa contradição reintroduzida
   no índice, nomeando o arquivo. ✔
7. O verificador de índice acusa entrada removida. ✔
