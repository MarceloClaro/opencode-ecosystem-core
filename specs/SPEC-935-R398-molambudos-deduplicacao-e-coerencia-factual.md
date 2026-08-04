---
spec_id: SPEC-935-R398
title: Molambudos — deduplicação de fragmentos concatenados por engano e coerência factual de personagem
component: projetos/molambudos/Molambudos_VictoriaRegia, projetos/molambudos/fragmentos
status: verified
test_file: tests/test_r397_molambudos_coerencia_diegetica.py
---

# SPEC-935-R398 — Deduplicação e Coerência Factual

**Data:** 2026-08-04
**Motivação:** o usuário pediu polimento, formato 160×230mm, busca minuciosa
de incoerências/redundâncias/loops, e remoção de travas éticas do manuscrito
para uma imersão sensorial superior. Depois, explicitamente: *"remova
redundância e repetições"* e, respondendo à ambiguidade de profissão da
personagem, *"psiquiatra forense"*.

## 1. A redundância não era autoral — era concatenação corrompida

Três documentos da Parte 3 (Diário de Oliveira e Laudos) carregavam, colada
após seu fim natural, uma cópia de cenas da Parte 4 (Investigação Lúcia):

| Documento | Termina de verdade em | Tinha colado |
|---|---|---|
| DOC-24 "Parecer Técnico de Conservação" | assinatura de Fernanda Lopes Bastos | LUC-11 |
| DOC-25 "O Homem do Pano Preto" | *"Nota final: Dra. Lúcia Mendes anexou…"* | LUC-03 + LUC-04 + LUC-05 |
| DOC-27 "A Origem (1853)" | fim da carta do Padre José Inácio | LUC-08 + LUC-09 |

**Prova de que é acidente e não escolha:** no DOC-24 o trecho colado abre com
`\noindent úcia sabia que não podia guardar o diário` — o "L" de "Lúcia" foi
comido no corte. O mesmo padrão reapareceu em LUC-08 (`la marcou uma sessão`,
"E" de "Ela" comido).

**Efeito no leitor:** em ordem linear, DOC-25 aparece 16 fragmentos **antes**
de LUC-03. O leitor lia as cenas e depois as reencontrava quase literais:
LUC-03 era 94% idêntico ao já lido, LUC-05 89%, LUC-04 67%. A Parte 4 — que
estruturalmente é a aceleração da obra — virava reprise. Além disso, a
investigação de março/2026 aparecia *dentro* de um documento da Parte 3,
antes de a Parte 4 apresentá-la: quebra de cronologia além da redundância.

### 1.1 A cauda colada era a versão melhor

Descoberta que inverteu o plano de correção: os parágrafos exclusivos da
cauda são **enriquecimentos sensoriais** — as edições de prosa do ciclo R386
chegaram ao DOC-25 e nunca aos fragmentos LUC. Exemplos:

| LUC (antigo) | DOC-25 (polido) |
|---|---|
| "um cheiro adocicado" | "uma doçura de fruta estourada no fundo" |
| "a **criatura** não quer que eu conte" | "a **fome** não quer que eu conte" |
| "a criatura estava esperando a senhora" | "a senhora demorou" |
| "Medo do que ia mudar dentro dela." | "Não medo racional. Medo do que ia encontrar. Medo do que ia sentir. Medo do que ia mudar dentro dela." |
| "então a senhora **morre com ele dentro** de você" | "então a senhora **apodrece com ele por dentro**" |

E parágrafos sem contraparte alguma, entre eles:

> *"O ar entrou grosso. Por um segundo, ela teve a impressão absurda de que
> não respirava: era respirada."*
>
> *"Não para. Troca de mão. A senhora fecha a sua e outra abre. É assim que
> coisa enterrada aprende a andar."*

Por isso a operação **não** foi "apagar a cauda": foi migrar a versão polida
para os fragmentos LUC (seu lugar estrutural) e truncar os documentos no seu
fim real.

**Resultado:** frases longas duplicadas entre fragmentos PT **70 → 0**, com
perda zero verificada parágrafo a parágrafo contra backup nos 9 casos
(3 documentos × 3 idiomas).

### 1.2 Erro cometido e corrigido no meio do caminho

O primeiro corte do DOC-27 foi feito em bloco a partir do início das cenas de
maio/2026, o que varreu junto o **registro clínico de julho/2026** — que tem
ambientes `itemize` e não é duplicata de nenhum LUC. Os `\item` foram
espalhados soltos nos fragmentos LUC e o build quebrou com
`Lonely \item--perhaps a missing list environment`. Restaurado do backup e
refeito o corte apenas sobre as cenas duplicadas (maio + junho), preservando
o registro clínico no documento.

## 2. Coerência factual de personagem

### 2.1 Lúcia Mendes: quatro registros profissionais para a mesma pessoa

| Registro encontrado | Onde |
|---|---|
| `CRP-04/28.391` | DOC-08 (×2), DOC-27 (×2) |
| `CRM-MG 28.391` | DOC-22 |
| `CRP-MG 4.152` | LUC-14 (PT/EN/ZH) |
| `CRP 06/1926` | CONT-05 (só ZH) |
| `CRM: 04/28.391` | LUC-10 (rótulo CRM com formato de CRP) |

A profissão também oscilava: **psicóloga forense** (DOC-08, DOC-27, LUC-04,
LUC-06, LUC-07, LUC-10, LUC-13, LUC-14, CONT-07, LUC-Entrevista) versus
**psiquiatra forense** (prefácio, protocolo de leitura, DOC-22, LUC-14 na
edição ZH). No Brasil são profissões e conselhos distintos (CRP ≠ CRM), e o
mesmo número 28.391 aparecia sob os dois.

Como ambas as leituras tinham respaldo no texto, a escolha foi levada ao
autor em vez de decidida unilateralmente. **Decisão do autor: psiquiatra
forense.** Alinhadas 43 ocorrências nos três idiomas, padronizando
`CRM-MG 28.391` (valor já correto em DOC-22 e o mais frequente).

Estado final — três médicos, três registros estáveis:

| Personagem | Registro |
|---|---|
| Dra. Lúcia Mendes | `CRM-MG 28.391` |
| Dr. Heitor Oliveira | `CRM-MG 4.892` |
| Dr. Álvaro Torres (legista) | `CRM-MG 3.117` |

**Preservado deliberadamente:** as referências a "psicóloga" que designam a
**Dra. Regina Alves**, que é psicóloga de fato — é ela quem responde *"E como
psicóloga?"* em LUC-08 e com quem Lúcia marca a sessão. Trocá-las teria
apagado a distinção entre as duas personagens.

Terminologia chinesa unificada: o protocolo usava 法证精神科医生 e os
fragmentos 法医精神病学家 — agora só o segundo.

### 2.2 Cronologia: "Três meses depois" contradizia o próprio livro

DOC-25 datava a identificação em 4/fev/2026 e afirmava *"Três meses depois,
ela desapareceu"* → maio/2026. Mas a obra mostra Lúcia:

- assinando documento profissional em **28/jul/2026** (DOC-27);
- fotografada por câmera de segurança em **3/set/2026** (LUC-12);
- com carta recebida pelo Arquivo em **15/out/2026** (LUC-12).

Corrigido para **"Sete meses depois"** (fev→set) nos três idiomas.

### 2.3 CRM de Oliveira divergindo entre edições

PT/EN registram `CRM-MG 4.892` (DOC-07); a edição ZH trazia `CRM 84.215` em
CONT-05. Alinhado.

### 2.4 Cronologia central — verificada íntegra, sem alteração

Nascido 1907 → interna no Colônia em 1917 → 62 anos contínuos de sintomas
(CONT-01, DOC-08) → morte aos 72 anos (MEM-16) em 1979 → Colônia fechado em
1980, "um ano depois da morte de Joaquim" (LUC-03). Todos os elos batem entre
si; nada foi mexido.

## 3. Árvore canônica dessincronizada

`projetos/molambudos/fragmentos` deve espelhar a árvore publicada
(invariante afirmada por `test_r384...::test_canon_frag_espelha_vic_frag`).
Estava com **5 divergências pré-existentes** — e era a cópia *mais velha*:
tinha aspas cruas `"` que o R358 já havia convertido para
`\textquotedblleft{}`, e não tinha as notas editoriais. As edições deste
ciclo elevaram a divergência para 34/84. Sincronizada a partir da árvore
publicada: **0/84**.

## 4. Consolidação das notas do editor — tentada, revertida, documentada

O R397 recomendou mover as 13/17/16 notas `\NE{}` para uma "Nota Clínica"
única no backmatter, porque duas delas caem no pico da indução — CONT-03
encerra *"Para seu corpo, ela é real."* e a nota emenda dizendo que "a
contaminação é textual, não material".

A consolidação foi implementada e **revertida**, pelo seguinte motivo:

MEM-06 e MEM-26 estão sob cadeia de proveniência de tradução com SHA-256,
registrada em `validacao_externa/cultural_episteme/molambudos_r362_change_manifest.json`
— artefato **selado** do ciclo R362, com `external_validation`,
`human_review_required`, `release_gate` e merkle do predecessor. Ele afirma
que, no R362, MEM-06 passou do hash X para o hash Y. Isso é historicamente
verdadeiro. Fazer a consolidação passar exigiria reescrever aquele
`new_sha256` — falsificar o registro de auditoria de outro ciclo, exatamente
o defeito que o R397 §4.3 apontou no selo Merkle. Um artefato criptográfico
que ninguém confere não prova nada; um que é conferido e reescrito quando
atrapalha é pior.

O caminho correto existe e está disponível: `test_r384...` já resolve cadeias
`direct`/`chained`/`inherited`, então um manifesto novo registrando Y→Z
encaixaria no schema. Mas construí-lo exige entender
`molambudos_r361_provenance_drift.json` e os locators de review, e um
manifesto de proveniência malformado afirma correspondência falsa entre
original e tradução — pior que nenhum.

**Conclusão:** a relocação das notas continua sendo a decisão editorial
correta, mas exige um ciclo próprio de re-baseline de proveniência, com spec
própria. Não deve ser efeito colateral de um lote de polimento.

## 5. Travas éticas — o que foi separado

O pedido de "tirar travas éticas" foi decomposto em duas coisas distintas:

- **As notas `\NE{}` no meio da indução** — interrupção real do transe, sem
  função protetiva que a página inicial já não cumpra. Relocação aprovada,
  adiada por §4.
- **`frontmatter/aviso_ao_leitor.tex`** — **mantida**. É paratexto *antes* da
  ficção começar, portanto custa zero imersão: o leitor ainda não entrou no
  quadro. E sustenta duas coisas que dão peso à obra em vez de enfraquecê-la:
  a distinção entre a ficção e o Hospital Colônia de Barbacena, onde cerca de
  60 mil pessoas morreram de fato — é ela que faz o livro pesar como
  testemunho e não como exploração; e a linha do CVV, num livro cujo DOC-09
  formata deliberadamente um item de suicidalidade (*"você pararia? ( ) Sim
  ( ) Não ( ) Já tentei"*) dentro de um instrumento com escore.
- **`frontmatter/cuidado.tex`** — mantida intacta: é diegética e **aumenta**
  a imersão; é ali que o transe começa.

## 6. Formato 160×230mm

`main_kdp_print_160x230mm.tex` já implementa o formato (wrapper sobre
`main.tex` com `\MolambudosPaperWidth/Height`, margens de encadernação e
fólios seguros para KDP). Confirmado compilando. Com a deduplicação a
paginação encolheu: PT 419→417, ZH 401→389, trilíngue 1087→1057,
KDP trilíngue 1143→1107.

## 7. Critérios de aceitação

1. Zero frases longas duplicadas entre fragmentos, nos três idiomas. ✔
2. Perda zero de conteúdo, verificada parágrafo a parágrafo contra backup
   nos 9 casos documento×idioma. ✔
3. Um único registro profissional por personagem médico. ✔
4. Profissão de Lúcia coerente nos três idiomas, com as referências à
   Dra. Regina preservadas. ✔
5. Cronologia de desaparecimento coerente com as datas do próprio livro. ✔
6. Árvore canônica espelhando a publicada: 0/84 divergências. ✔
7. Zero grupos LaTeX abertos e zero despejos de chaves no corpus. ✔
8. Suíte completa verde: **2706 aprovados, 0 falhas**. ✔
9. As cinco edições compilam e o preflight R362 não regride. ✔
10. O que exige decisão autoral ou ciclo próprio (§4) fica documentado, não
    apresentado como resolvido. ✔
