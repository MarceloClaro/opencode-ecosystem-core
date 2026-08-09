---
spec_id: SPEC-935-R405
title: Molambudos — paridade textual das edições inglesa e chinesa; dois fragmentos ZH que contradiziam o cânone
component: projetos/molambudos/Molambudos_VictoriaRegia, scripts/molambudos_selo.py
status: verified
test_file: tests/test_r399_molambudos_selo_e_capa.py
---

# SPEC-935-R405 — Paridade Textual EN e ZH

**Data:** 2026-08-08
**Motivação:** *"corrija o inglês"* e, em seguida, *"ignore as capas, foque o
texto, deixe pronto para publicação, faça o mesmo com o chinês"*.

## 1. Método: razão de caracteres contra a linha de base da própria edição

Comparar contagem de **linhas** entre idiomas é enganoso — o chinês não usa
espaços e quebra linha de outro modo. A medida usada é a razão de caracteres
por fragmento, avaliada contra a mediana da própria edição, com limite
inferior por IQR (Q1 − 1,5·IQR).

Um extrator ingênuo produziu resultado **errado** na primeira tentativa: ele
descartava o conteúdo dentro de `\textit{}`/`\textbf{}`, que o ZH usa muito
mais que PT/EN, e por isso penalizava o chinês artificialmente — chegou a
apontar DOC-17 como quase vazio quando ele estava correto. Corrigido para
preservar o argumento e remover apenas o nome do comando.

| Edição | Mediana | Interpretação |
|---|---|---|
| EN/PT | 1,01 | paridade — inglês e português têm extensão equivalente |
| ZH/PT | 0,37 | compressão natural do chinês para este texto |

## 2. Edição inglesa: 14 fragmentos fora da faixa → 7

Sete tinham conteúdo genuinamente ausente:

| Fragmento | Antes | O que faltava |
|---|---|---|
| **CONT-03** | 0,68 | a escalada fisiológica inteira: a mão pálida e a circulação periférica, o peso do livro e a fadiga simpática, o canto do quarto com a contagem até 5, e a Escala de Contaminação — Atualização 2 |
| MEM-23 | 0,72 | o medo de ser esquecido no incêndio; o fecho em que Joaquim admite não saber onde termina a fome dele e começa a da criatura |
| LUC-Escolha | 0,81 | Escala de Contaminação — Atualização 1 |
| DOC-23 | 0,82 | a declaração de Edson antes de assinar a demissão, e a nota manuscrita do gerente: *"Ele não estava mentindo."* |
| MEM-27 | 0,83 | Escala de Contaminação — Destruição |
| MEM-21 | 0,77 | a fala da criatura sobre os jornais; a página guardada no colchão |
| MEM-22 | 0,88 | a fala sobre os gritos; *"Eu tampava os ouvidos."* |

CONT-03 era o caso grave: é o fragmento de indução sensorial mais forte da
obra, e o leitor inglês pulava de *"para seu corpo, ela é real"* direto para o
cheiro que se intensifica, sem a sequência corporal no meio.

**Resultado:** razão global EN/PT **1,001**. Os 7 restantes (0,87–0,91) têm
todos os parágrafos presentes — inglês é mais compacto que português para o
mesmo conteúdo.

### 2.1 Limite do detector de parágrafos

O casamento de parágrafos entre idiomas por similaridade de string só funciona
quando há cognatos. Ele apontou CONT-12 e LUC-08 como incompletos, e ambos
estavam corretos. Serviu como **apontador**, não como veredito: cada caso foi
verificado à mão antes de qualquer edição.

## 3. Edição chinesa: dois fragmentos não eram tradução

Oito fragmentos fora da faixa. Seis eram abreviações; **dois eram textos
inteiramente diferentes, contradizendo a cronologia da obra.**

### 3.1 CONT-05 (razão 0,16)

| | Conteúdo |
|---|---|
| PT/EN | laudo que registra **o leitor** como Paciente 1.263, com critérios A a G preenchidos pelo ato da leitura, diagnóstico final, prognóstico e nota final |
| ZH | relatório sobre a internação do Dr. Oliveira, afirmando que ele **morreu em 1989** |

O cânone: Oliveira desapareceu em **13 de junho de 1979** (LUC-07, LUC-14) e
nunca foi encontrado; DOC-25 afirma que *"o paciente 1.261 não desapareceu.
Ele foi guardado para o momento da entrega"*. A data **1989 não aparecia em
nenhum outro arquivo da obra, em nenhum idioma** — indício claro de rascunho
obsoleto.

### 3.2 DOC-26 (razão 0,19)

| | Conteúdo |
|---|---|
| PT/EN | folhas avulsas de junho/1979 a janeiro/2026: a fenda temporal do diário, os saltos de 62 dias, a página 62, e Oliveira entregando o diário no arquivo em 2026 |
| ZH | notas de 1981 sobre o "mecanismo da fome", encerrando com *"nunca mais escreveu"* |

Isso apagava os 45 anos em que Oliveira carrega o diário — precisamente o que
DOC-25 identifica ao reconhecer nele o homem do pano preto.

**Ambos foram retraduzidos integralmente do português.** O texto anterior está
preservado em `_archive/backup_R405_pre_traducao_zh/`.

### 3.3 Demais correções ZH

CONT-03 recebeu a mesma escalada fisiológica que faltava no inglês, mais a
Escala — Atualização 2; LUC-Escolha e MEM-27 receberam suas tabelas de escala.

**Resultado:** 8 fora da faixa → **4** (MEM-23, DOC-03, DOC-23, MEM-21, todos
em 0,27–0,29, com estrutura completa). Razão global ZH/PT **0,363** contra
mediana 0,37.

## 4. Defeito no selo, exposto por este ciclo

Dois fragmentos chineses foram substituídos por inteiro e o
`merkle_root_fragmentos` **não se moveu**: o selo construído no R399 percorria
apenas `fragmentos/` (português).

Um selo que não reage a mudança de conteúdo em duas das três edições
publicadas atesta um terço da obra, não a obra.

Corrigido: `_fragmentos()` percorre as três edições. O selo passou de 84 para
**252 folhas**. Verificado na prática — alterar `zh/fragmentos/cont/CONT-05.tex`
faz `verificar` sair com código 1 apontando o arquivo exato; restaurado, volta
ao verde.

`test_selo_declara_o_numero_real_de_fragmentos` foi substituído por
`test_selo_cobre_os_fragmentos_das_tres_edicoes`, que exige as três raízes.

## 5. Efeito colateral notável

Com o inglês completado, **PT e EN convergiram para 417 páginas cada** (eram
417 e 413). A diferença de paginação era exatamente o conteúdo ausente.

| Edição | Digital | Impressão 160×230 | Lombada |
|---|---|---|---|
| PT | 417 | 435 | 25,93 mm |
| EN | 417 | 431 | 25,69 mm |
| ZH | 395 | 405 | 24,14 mm |
| Trilíngue | 1.073 | 1.125 | 67,07 mm |

## 6. O que este ciclo **não** resolve

1. **Nenhuma tradução passou por revisão nativa.** O que foi corrigido é
   conteúdo ausente, medido por volume, e contradição factual verificável
   contra o cânone. Registro, ritmo e naturalidade são trabalho de revisor
   humano — e num texto que depende de indução, o ritmo carrega metade do
   efeito.
2. **Dois fragmentos ZH foram substituídos por decisão do agente**, com base na
   contradição de cronologia. O texto anterior está arquivado caso fosse
   conteúdo desejado.
3. A arte de capa segue em 163 DPI e a contracapa segue com código de barras
   de teste embutido (fora do escopo deste ciclo por instrução explícita).

## 7. Critérios de aceitação

1. Razão global EN/PT em paridade (≈1,00). ✔ (1,001)
2. Razão global ZH/PT na mediana da própria edição. ✔ (0,363 / 0,37)
3. Nenhum fragmento com omissão estrutural (tabelas, seções inteiras). ✔
4. Nenhum fragmento contradizendo a cronologia do cânone. ✔
5. O selo cobre as três edições e reage a mudança em qualquer uma. ✔
6. Preflight R362 com `--build`: `overall_internal_spec_passed=True`,
   648/648 rotas, zero violações nas cinco edições. ✔
7. As limitações que exigem revisão humana ficam declaradas, não apresentadas
   como resolvidas. ✔
