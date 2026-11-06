> **Nota de escopo — Book Studio, 2026-11-05:** este parecer analisa a versão
> incompleta de 4 capítulos em `templates/livro/molambudos` e **não** descreve a
> edição atual `projetos/molambudos/Molambudos_VictoriaRegia` (435 pp, 84
> fragmentos, 216 rotas). Os achados de "obra incompleta" e "capítulos
> duplicados" não se aplicam à edição VictoriaRegia. A auditoria atual está em
> `projetos/molambudos/Molambudos_VictoriaRegia/BOOK_STUDIO_AUDIT.md`.

# Revisão Crítica: *Molambudos* — Diário do Paciente 1.260

**Autor:** Marcelo Dias de Carvalho Filho  
**Revisão:** OpenCode Ecosystem Core — Análise Estrutural, Metacognitiva e Narrativa  
**Data:** 10 de julho de 2026  
**Base:** Arquivos LaTeX em `templates/livro/molambudos/` + índice completo em `referencias.bib`

---

## Sumário da Revisão

1. [Macroestrutura: O Abismo Entre Promessa e Entrega](#1-macroestrutura)
2. [Redundâncias Críticas](#2-redundâncias)
3. [Inconsistências Estruturais e Narrativas](#3-inconsistencias)
4. [Escalada de Horror: Onde o Visceral É Abandonado](#4-escalada)
5. [Sequência Investigativa: Furos na Lógica](#5-investigacao)
6. [Problemas de Personagem e Voz](#6-personagem)
7. [Diagnóstico Consolidado](#7-diagnostico)
8. [Recomendações Cirúrgicas](#8-recomendacoes)

---

<a name="1-macroestrutura"></a>
## 1. Macroestrutura: O Abismo Entre Promessa e Entrega

### O índice promete uma catedral. O que existe são fragmentos de um alicerce.

O `referencias.bib` lista **100+ fragmentos** organizados em 4 eixos:

| Eixo | Código | Qtd. | Páginas |
|------|--------|------|---------|
| Memórias de Joaquim (Paciente 1.260) | MEM | 34 | 1–126 |
| Documentos oficiais e laudos | DOC | 28 | 138–204 |
| Investigação forense de Dra. Lúcia | LUC | 12+ | 215–250+ |
| Contaminação do leitor | CONT | 26 | 258–319 |

São **~320 páginas** de obra.  
O que existe nos arquivos LaTeX corresponde a **menos de 5%** disso:

| Capítulo | Conteúdo Real | Páginas no PDF |
|----------|--------------|----------------|
| 1 — Leitura Linear | Metalinguagem (instruções de leitura) + MEM-01 | ~vi, 1 |
| 2 — Exame Externo | Laudo necroscópico parcial + seções 3 e 4 | ~146 |
| 3 — Exame Interno | Laudo necroscópico (continuação) + Exumação | ~147 |
| 4 — Achados Especiais | Exumação (REPETIDA) + Rotas de Leitura | ~147–149 |

**Problema nº 1, gravíssimo:** o índice anuncia 34 memórias (MEM-01 a MEM-34), 28 documentos, dezenas de fragmentos LUC e CONT — mas **apenas MEM-01 está integralmente presente** nos capítulos. Os outros 33 fragmentos MEM, 27 DOC, todos os LUC e todos os CONT **existem apenas como títulos no índice**.

### Isso não é um problema de formatação LaTeX. É um problema de **obra incompleta no repositório**.

Se os arquivos `.tex` contêm apenas o que foi extraído do PDF original, então o PDF de origem já estava truncado — e a revisão precisa considerar se isso é:
- (a) Um artefato da extração (pdf2latex falhou em capturar o resto) → **recuperável**
- (b) A obra de fato só tem esses fragmentos → **problema estrutural grave, pois o índice mente**

**Recomendação 1.A:** Verificar o PDF original `MOLAMBUDOS.pdf`. Se ele tem 320 páginas, reextrair com `pdf2latex` ajustando páginas. Se ele só tem essas ~10 páginas, **remova ou reduza drasticamente o índice** — ele promete o que não entrega.

---

<a name="2-redundancias"></a>
## 2. Redundâncias Críticas

### 2.1 Capítulos 3 e 4 — Duplicação Quase Idêntica

Compare os arquivos:

```
capitulo_03_exame_interno.tex    → 111 linhas
capitulo_04_achados_especiais.tex → 115 linhas
```

Ambos **começam com o mesmo texto**:

> Exumação — 14 de junho de 1979 (48 horas após o óbito, por solicitação  
> da direção do Hospital Colônia para liberação do leito)

Ambos contêm:
- O depoimento do coveiro Genésio Barbosa (idêntico)
- A pele íntegra, coloração escurecida (idêntico)
- O globo ocular com luminescência residual (idêntico)
- O caderno/diário sobre o tórax (idêntico)
- "5. DESTINAÇÃO DOS RESTOS MORTAIS" (idêntico)
- As mesmas 2 figuras
- As mesmas 2 tabelas

A única diferença: o capítulo 4 acrescenta o parágrafo do Dr. Álvaro Torres (CRM-MG 3.117) e as "Rotas de Leitura". De resto, é um **Crtl+C / Ctrl+V** do capítulo 3.

**Impacto:** Um leitor que chega ao capítulo 4 tem um `déjà vu` paralisante. A obra perde toda credibilidade.

### 2.2 Causa Mortis Duplicada

A "Causa Mortis: Parada cardiorrespiratória..." aparece em **2 lugares**:

1. **Final do capítulo 2** (linhas 36–49) — dentro da seção "3. EXAME INTERNO", aninhada dentro do capítulo "EXAME EXTERNO"
2. **Início do capítulo 3** (linhas 1–16) — como o próprio capítulo "EXAME INTERNO"

### 2.3 Tabelas Repetidas 4× Cada

| Tabela | Aparece em |
|--------|-----------|
| Questionário de Contaminação (Pontos & Diagnóstico) | Caps. 1, 2, 3, 4 |
| Tabela de Incidentes (1920–1979) | Caps. 1, 2, 3, 4 |

A tabela de incidentes **idêntica** — mesmos dados, mesma formatação — aparece **quatro vezes** no livro. Duas delas no mesmo contexto narrativo (caps. 3 e 4 são o mesmo laudo). Isso é **ruído puro**.

### 2.4 Figuras Repetidas 4×

As figuras `img-000.png` e `img-001.png` são incluídas em **todos os 4 capítulos**. Se são as mesmas imagens, devem ser incluídas uma única vez no local adequado.

---

<a name="3-inconsistencias"></a>
## 3. Inconsistências Estruturais e Narrativas

### 3.1 Numeração de Páginas — Salto Abissal

| Capítulo | Número(s) de página |
|----------|---------------------|
| 1 — Leitura Linear | vi, 1 |
| 2 — Exame Externo | 146 |
| 3 — Exame Interno | 147 |
| 4 — Achados Especiais | 147, 148, 149 |

**Salto:** Da página **1 → 146**. O que acontece nas páginas 2–145?

Pelo índice, sabemos: MEM-02 a MEM-34 (págs. 4–126) + DOC-01 e DOC-02 (págs. 138–143). Ou seja, **145 páginas de conteúdo simplesmente não estão nos capítulos**.

### 3.2 Voz Narrativa — Conflito de Gêneros

O livro tem **três vozes narrativas distintas** que coexistem sem costura:

| Voz | Onde aparece | Tom |
|-----|-------------|-----|
| **Narrador-criança** (Joaquim) | MEM-01 | Poético, sensorial, primeira pessoa: *"Meu pai dizia que a terra tinha um jeito de avisar"* |
| **Laudo técnico** (Legista) | Caps. 2–4 | Clínico, impessoal, terceira pessoa: *"Peso: 42 kg / Estatura: 1,62 m"* |
| **Metalinguagem** (Arquivista/Autor Implícito) | Abertura do cap. 1 + Rotas de Leitura + referências | Expositivo, instrutivo: *"Escolha seu próprio percurso"* |

O **problema não é ter múltiplas vozes** — a estrutura de romance fragmentado (MEM/DOC/LUC/CONT) sugere que isso é intencional. O problema é que **não há transição, não há contraste, não há conflito entre elas**. Elas apenas se alternam abruptamente.

**Exemplo:** O capítulo 1 termina em um fluxo de consciência infantil sobre a seca ("Meu pai mudou primeiro..."). O capítulo 2 abre com "Peso: 42 kg". O leitor sofre um **whiplash narrativo** sem qualquer mediação.

### 3.3 O Paciente 1.260 vs. 1.263 — Relação Obscura

No início (cap. 1), o leitor é informado:

> "Ao final, você será o Paciente 1.263."

O laudo (caps. 2–4) é sobre o Paciente 1.260 (Joaquim). A Dra. Lúcia seria a 1.262, o Dr. Oliveira o 1.261.

**Problema:** A progressão do ciclo (1.260 → 1.261 → 1.262 → 1.263) é explicada APENAS nas referências bibliográficas (metadados), NUNCA no corpo do texto. O leitor que lê apenas os capítulos não sabe:
- Quem é 1.261 (Oliveira)
- Quem é 1.262 (Lúcia)
- Como a contaminação passa de um para o outro
- Por que o leitor se torna 1.263

### 3.4 A Rasga Mortalha — O Fio Mais Solto

A **Rasga Mortalha** é uma figura do folclore cearense — uma entidade feminina que anuncia mortes com seu canto. No livro, ela aparece **UMA ÚNICA VEZ**:

> Set/1945 — Episódio de vocalização incontrolável (alega que 'a Rasga Mortalha' está falando através dele)

Isso é **TUDO**. Uma menção numa tabela de incidentes. Nunca mais retorna.

Considerando que:
- MEM-12 chama-se "A Rasga Mortalha" (página 80)
- A entidade é folclórica, feminina, associada à morte noturna
- O Paciente 1.260 alega possessão por ela

...a Rasga Mortalha deveria ser um dos **pilares do horror sobrenatural** da obra. Em vez disso, é um **fio solto jogado fora**.

### 3.5 O Diário — O MacGuffin Que Nunca Aparece

O diário de Joaquim é:
- A primeira palavra após 7 anos de mutismo: *"O diário"* (1956)
- Encontrado sobre o tórax do cadáver na exumação
- Retido pelo IML para análise
- A fonte de todos os fragmentos MEM

**Problema:** O diário é o centro gravitacional da obra, mas no material disponível **nunca lemos o diário de fato**. Temos MEM-01 (que seria parte do diário), mas é uma memória de infância, não o diário como objeto narrativo. O diário enquanto **artefato contaminante** (com poder de transmitir o ciclo) nunca é materializado.

---

<a name="4-escalada"></a>
## 4. Escalada de Horror: Onde o Visceral É Abandonado

### 4.1 O Potencial de MEM-01

MEM-01 é **excelente**. Tem uma progressão interna poderosa:

1. **O gado morre** → horror da natureza em colapso
2. **O rio seca** → horror da paisagem que se desfaz
3. **As pessoas mudam** → horror psicológico
4. **O pai na soleira** → horror doméstico, silencioso
5. **A mãe pergunta** → corte abrupto (a página é cortada no meio da frase)

A prosa é sensorial e precisa: *"O leito parecia uma estrada de osso branco"*. Há uma **escalada visceral real** em 4 estágios dentro de um único fragmento.

### 4.2 O Abismo Pós-MEM-01

Depois de MEM-01, o livro **muda completamente de natureza**:

| Antes (MEM-01) | Depois (Caps. 2–4) |
|----------------|-------------------|
| Carne apodrecendo | Laudo clínico |
| Rio secando | Tabela de incidentes |
| Pai catatônico | Exame de estômago vazio |
| Calor, sede, fome | Peso do cérebro (1.120g) |
| Narrador-criança vulnerável | Voz institucional do legista |

Não há **ponte emocional**. O horror visceral da seca e da fome é substituído por **horror burocrático** (laudos, tabelas, números) — que pode ser igualmente poderoso, mas a transição é brusca demais.

### 4.3 Onde Está a Escalada?

Uma obra de terror psicológico precisa de uma **progressão em 3 atos**:

```
[Visceral] → [Psicológico] → [Metafísico]
   (corpo)      (mente)        (realidade)
```

Em *Molambudos*, o que temos:

```
[Ato 1: Visceral]  →  MEM-01 (seca, fome, morte do gado) ✓
[Ato 2: Psicológico] → ???
[Ato 3: Metafísico]  → ???
```

O laudo necroscópico (caps. 2–4) contém **elementos do horror metafísico** (olho que brilha, corpo que não se decompõe, diário que aparece magicamente) — mas eles são **apresentados como fato, não como revelação**.

O terror psicológico exige:
- **Dúvida** → O leitor deve questionar o que é real
- **Paranoia** → O leitor deve desconfiar das fontes
- **Invasão** → O horror deve penetrar a psique do leitor

Nada disso ocorre no material disponível. O laudo é apresentado com **autoridade médica inquestionável**. Não há narrador não-confiável, não há versões conflitantes, não há ambiguidade.

### 4.4 A "Contaminação do Leitor" É Anunciada, Não Executada

A tabela de "Pontos & Diagnóstico" que aparece em todos os capítulos diz ao leitor:

> 0-2: Leitor resiliente. A contaminação não pegou.  
> 3-5: Leitor exposto. Sintomas iniciais.  
> 6-8: Leitor contaminado. O olho amarelo aparecerá em breve.  
> 9-10: Paciente 1.263. Bem-vindo. A criatura agradece sua atenção.

Isso é **meta-horror** de altíssimo potencial — o livro diagnosticando o leitor. Mas para funcionar, precisa ser **sentido**, não apenas descrito. O leitor precisa EXPERIMENTAR:
- O cheiro adocicado (mencionado no ciclo)
- Os sonhos com a vala
- A sensação de estar sendo observado
- O olho amarelo no canto da página

No material atual, a tabela é apenas um **gadget repetitivo**, não uma **experiência**.

---

<a name="5-investigacao"></a>
## 5. Sequência Investigativa: Furos na Lógica

### 5.1 A Estrutura Promete Investigação

O livro se apresenta como um **arquivo forense**:
- DOC → Documentos oficiais
- LUC → Investigação de Lúcia
- CONT → Contaminação do leitor

Isso sugere que o leitor é um **investigador** montando um quebra-cabeça.

### 5.2 O Que o Leitor Pode Descobrir (Com o Material Disponível)

| Pergunta | Resposta nos capítulos |
|----------|----------------------|
| Quem foi Joaquim? | Uma criança na seca de 1915 que virou paciente do Colônia |
| Do que ele morreu? | Desnutrição + parada cardíaca |
| O que há de estranho no corpo? | Olho direito amarelo, corpo conservado, diário no peito |
| O que é a criatura? | Não há resposta |
| Como funciona o ciclo? | Não há resposta |
| O que é a Rasga Mortalha? | Menção única numa tabela |
| Quem é Lúcia? | Não aparece |
| Quem é Oliveira? | Sessões em 1979 (mencionado na tabela) |

### 5.3 Furos Investigativos

1. **O Diário é a chave, mas está ausente.** A primeira palavra de Joaquim após 7 anos é "O diário". O diário é encontrado no cadáver. O diário é retido pelo IML. Mas **nunca lemos o diário**. É um MacGuffin que não se materializa.

2. **A exumação contradiz o laudo.** O legista diz que não há explicação médica para os fenômenos. O coveiro vê o olho brilhando. Mas **nenhuma investigação adicional é feita**. O laudo simplesmente encerra com "não há explicação". Isso não é mistério — é **omissão narrativa**.

3. **O ciclo 1.260 → 1.263 é explicado apenas nos metadados.** Quem lê só os capítulos não sabe o que significa ser 1.263. A informação crucial está nas referências bibliográficas (que o leitor comum não lê).

4. **A Rasga Mortalha é introduzida e abandonada.** Um fio narrativo com potencial imenso é jogado fora.

5. **A Dra. Lúcia não é introduzida.** Ela tem 12 fragmentos no índice (LUC-01 a LUC-12), mas no material disponível ela não existe como personagem.

---

<a name="6-personagem"></a>
## 6. Problemas de Personagem e Voz

### 6.1 Joaquim Antônio Correia

**Nomeado** nas referências como "Joaquim Antônio Correia", mas **nunca nomeado** no texto dos capítulos. O leitor descobre o nome do protagonista APENAS se ler as referências bibliográficas.

**Idade:** Na MEM-01 (1914–1915), a voz é de uma criança. Na tabela de incidentes, o paciente comete homicídios em 1920 (já adulto). **Não há transição da infância para a idade adulta** nos fragmentos disponíveis.

### 6.2 Dr. Heitor Oliveira

Mencionado 2×:
- Na tabela: "1979 — Sessões com Dr. Heitor Oliveira"
- Na referência: "descrito por Dr. Heitor Oliveira como uma psicose induzida"

**Nunca aparece como personagem.** É apenas uma assinatura em documentos.

### 6.3 Dra. Lúcia

A investigadora forense que deveria ser o **ponto de entrada do leitor** no mistério. Tem 12 fragmentos no índice. **Não existe no texto disponível.**

### 6.4 Genésio Barbosa, o Coveiro

O único personagem secundário com **voz própria** — e é excelente:
- Funcionário há 22 anos
- Relata o corpo conservado
- Descreve a luminescência como *"um brilho fraco, como vaga-lume"*
- Usa linguagem simples, não técnica

Genésio é a **única ponte entre o horror institucional (laudo) e o horror humano**. Deveria ter mais espaço.

---

<a name="7-diagnostico"></a>
## 7. Diagnóstico Consolidado

### Urgência Cirúrgica — O Que Mata a Obra Agora

| Prioridade | Problema | Impacto |
|-----------|----------|---------|
| 🔴 **Crítico** | Capítulos 3 e 4 são duplicatas | Leitor perde confiança na obra |
| 🔴 **Crítico** | Índice promete 320 páginas, existem ~10 | Mente para o leitor |
| 🔴 **Crítico** | Causa Mortis duplicada entre caps. 2 e 3 | Erro técnico inexplicável |
| 🟠 **Alto** | Tabelas e figuras repetidas 4× | Ruído narrativo |
| 🟠 **Alto** | Rasga Mortalha introduzida e abandonada | Fio solto narrativo |
| 🟠 **Alto** | Diário (centro da obra) não aparece | MacGuffin sem materialização |
| 🟡 **Médio** | Transição MEM-01 → laudo é brutal | Sem costura narrativa |
| 🟡 **Médio** | Nomes dos personagens só nas referências | Leitor não sabe quem é quem |
| 🟡 **Médio** | Progressão 1.260→1.263 não é explicada | Ciclo incompreensível |
| 🟢 **Baixo** | Numeração de páginas salta 1→146 | Confusão na navegação |

---

<a name="8-recomendacoes"></a>
## 8. Recomendações Cirúrgicas

### 8.1 Imediatas (Fazer Antes de Qualquer Outra Coisa)

1. **Fundir capítulos 3 e 4** — eliminar a duplicação. O conteúdo de "Achados Especiais" (Dr. Álvaro Torres + Rotas de Leitura) deve ser anexado ao final do capítulo 3, ou o capítulo 4 virar um apêndice curto com conteúdo **exclusivo**.

2. **Eliminar 3 das 4 repetições de cada tabela.** A tabela de contaminação (Pontos & Diagnóstico) deve aparecer UMA vez — no final (como "diagnóstico final do leitor"). A tabela de incidentes deve aparecer UMA vez — no laudo (cap. 2 ou 3).

3. **Remover figuras duplicadas.** Cada figura deve ser incluída UMA vez.

4. **Corrigir a Causa Mortis.** Remover do capítulo 2 (onde está intrusa) e manter apenas no capítulo 3.

### 8.2 Estruturais (A Obra Precisa Delas)

5. **Se a obra está incompleta, assuma isso.** Substitua o índice gigante por um sumário enxuto com APENAS o que existe. Ou complete a obra.

6. **Criar uma transição entre MEM-01 e o laudo.** Uma página de "Arquivo" ou "Nota do Organizador" que prepare o leitor para a mudança de voz narrativa. Exemplo:

   > *O relato abaixo foi encontrado nos arquivos do Hospital Colônia de Barbacena. É o laudo de necropsia do Paciente 1.260. As marcas d'água e rasuras são originais.*

7. **Materializar o diário.** Se o diário é o centro, o leitor precisa ler pelo menos UM fragmento que seja explicitamente o diário (com data, com caligrafia descrita, com sujeira nas bordas, com marcas de contaminação).

### 8.3 Para a Escalada de Horror (O Salto Qualitativo)

8. **Criar a progressão Visceral → Psicológico → Metafísico:**
   - Começar com 3 fragmentos MEM de horror visceral (seca, fome, morte) — OK
   - Transição para DOC com horror burocrático (laudos frios que insinuam o anormal) — parcialmente OK
   - Introduzir LUC com horror psicológico (Lúcia questionando a própria sanidade) — **PRECISA SER CRIADO**
   - Culminar com CONT — horror metafísico (o leitor começa a manifestar sintomas) — **PRECISA SER CRIADO**

9. **Expandir Genésio Barbosa.** O coveiro é o único personagem secundário com voz humana. Use-o como **testemunha** que reaparece em múltiplos fragmentos, cada vez mais perturbado.

10. **A Rasga Mortalha precisa voltar.** Sugestão: criar um fragmento MEM ou DOC onde Joaquim transcreve o canto da Rasga Mortalha. Incluir a partitura ou a letra. Deixar o leitor com a sensação de que ouviu algo que não deveria.

11. **O olho amarelo precisa contaminar a diagramação.** Sugestão:
    - No fragmento MEM-05 ("O Olho Amarelo"), a palavra "olho" aparece em amarelo
    - Nos fragmentos CONT, o olho amarelo aparece progressivamente nas margens, nas letras, até ocupar a página inteira no fragmento final
    - A tabela "Pontos & Diagnóstico" deve ser interativa (o leitor soma seus próprios pontos)

12. **Criar ambiguidade investigativa.** Sugestão: dois fragmentos que se contradizem — o laudo oficial (DOC) diz uma coisa, as anotações de Lúcia (LUC) dizem outra. O leitor precisa decidir em quem confiar.

### 8.4 De Personagem

13. **Nomear Joaquim no texto**, não apenas nas referências. A primeira aparição do nome deve ser na MEM-01 ou no DOC-02 (Prontuário).

14. **Apresentar Lúcia antes de seu arquivo.** Incluir um fragmento LUC-00 — talvez um e-mail ou carta-convite que explique como ela chegou ao caso.

15. **Oliveira precisa ter voz.** Um relatório de sessão (DOC-04 ou DOC-05) transcrito com as palavras do próprio Oliveira, onde ele já parece contaminado.

---

## Nota Final

> *Molambudos* tem uma **premissa poderosa**: a fusão do horror real da seca nordestina e do horror institucional do Hospital Colônia com uma camada de horror sobrenatural (contaminação, ciclo, Rasga Mortalha). A prosa de MEM-01 é genuinamente boa — sensorial, precisa, emocionante.
>
> **Mas a obra atual não é um romance. É o esqueleto de um romance — com vários ossos no lugar errado.**
>
> As redundâncias (caps. 3=4, tabelas 4×) são erros técnicos que precisam ser corrigidos **hoje**. A ausência dos fragmentos prometidos no índice é um problema de verdade que precisa de uma decisão clara: ou a obra existe integralmente (e precisa ser recuperada/reescrita) ou o índice precisa ser podado.
>
> O potencial para uma obra de terror psicológico genuinamente brasileira — que use a estrutura de diário/arquivo/laudo como *House of Leaves* encontra *Vidas Secas* — está aqui. Mas precisa de cirurgia. Muita cirurgia.
>
> — *MarceloClaro, Orquestrador Central Metacognitivo*

---

**Arquivos afetados:**
- `templates/livro/molambudos/capitulos/capitulo_03_exame_interno.tex`
- `templates/livro/molambudos/capitulos/capitulo_04_achados_especiais.tex`
- `templates/livro/molambudos/capitulos/capitulo_02_exame_externo.tex`
- `templates/livro/molambudos/capitulos/capitulo_01_leitura_linear.tex`
- `templates/livro/molambudos/main.tex`
