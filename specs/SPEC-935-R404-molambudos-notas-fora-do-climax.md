---
spec_id: SPEC-935-R404
title: Molambudos — notas do editor saem do clímax de contaminação; substância protetiva migra para o paratexto
component: projetos/molambudos/Molambudos_VictoriaRegia
status: verified
test_file: tests/test_r384_molambudos_extended_regen_editorial_notes.py
---

# SPEC-935-R404 — Notas Fora do Clímax

**Data:** 2026-08-07
**Motivação:** *"remova a nota do editor que está quebrando o clímax de terror
psicológico, a gradual experiência sensorial e dinamismo frenético; corrija
para imergir um desconforto e sensações já propostas na ideia do projeto"*.

## 1. Por que agora foi possível e no R398 não foi

O R397 §4.2 identificou o problema e recomendou a relocação. O R398
implementou e **reverteu**: as notas de MEM-06 e MEM-26 estão sob cadeia de
proveniência de tradução com SHA-256, num artefato selado do R362, e fazê-las
sair exigiria reescrever `new_sha256` de outro ciclo.

Antes de agir desta vez, os fragmentos rastreados foram levantados:

> DOC-02, DOC-05, DOC-08, DOC-15, DOC-17, DOC-18, LUC-01, LUC-10,
> MEM-02, MEM-04, MEM-06, MEM-12, MEM-26

**A família CONT não está entre eles.** Como o pedido do autor é
especificamente sobre o clímax --- e o clímax é a família CONT --- o caminho
estava livre sem tocar em nenhum registro selado.

## 2. As notas não eram todas a mesma coisa

Remover as 19 notas de CONT em bloco teria custado conteúdo. Classificadas
por natureza:

| Classe | Notas | O que fazem | Destino |
|---|---|---|---|
| **Explicam a técnica** | CONT-02, CONT-10, CONT-13 | análise crítica dentro da ficção, enquanto o dispositivo opera | removidas |
| **Ressalvas de proteção** | CONT-03, CONT-04, CONT-07 | substância no papel, sonhos/sono, códigos CID | migradas ao aviso |
| **Híbrida com desescalada** | CONT-01 | manda *"feche o livro por 60 segundos"* no auge sensorial | removida |
| **Diegética** | CONT-11 | o arquivista relata um lápis de marca inexistente em 1979 | **mantida** |

### 2.1 O caso mais grave

CONT-02 informava que *"o uso da segunda pessoa neste fragmento não é apenas
um recurso estilístico --- é um dispositivo formal de contaminação"*. É
crítica literária impressa dentro da ficção, desmontando o efeito no instante
em que ele acontece. Esse material já existe, e no lugar certo: o dossiê de
estudo do R403 analisa exatamente esse procedimento.

### 2.2 A exceção que fica

CONT-11 é **diegética**: quem fala é o arquivista, relatando que a página foi
escrita a lápis de uma marca que não existia em 1979 e que decidiu incluí-la
*"por fidelidade ao conjunto do arquivo, sem atribuir autoria"*. Não sai da
ficção para explicá-la --- aprofunda o horror. Removê-la seria perder
conteúdo, não ganhar imersão.

## 3. A substância protetiva não se perdeu

O que as ressalvas afirmavam migrou para `aviso_ao_leitor.tex`, nos três
idiomas. O aviso é **paratexto anterior à ficção**: o leitor ainda não entrou
no quadro, logo o custo de imersão é zero.

Já constava do aviso: nenhuma instrução produz efeito físico, químico ou
biológico; a contaminação é dispositivo narrativo; o papel não recebeu
substância alguma; o leitor pode interromper a qualquer momento.

Acrescentado no R404:

> **Sobre sonhos, sono e sintomas:** não há evidência de que a leitura
deste livro induza sonhos específicos, altere o ciclo sono-vigília ou produza
qualquer sintoma físico.

> **Sobre os códigos e escalas clínicas:** os protocolos diagnósticos,
códigos CID e escalas de avaliação que aparecem na parte ficcional são
construção literária. **Este livro não diagnostica o leitor**: ele simula
um diagnóstico, como dispositivo de ficção.

## 4. Efeito no clímax

| Fragmento | Antes | Depois |
|---|---|---|
| CONT-03 | *"Para seu corpo, ela é real."* → nota informando que a contaminação é textual | *"Para seu corpo, ela é real."* → a página segue |
| CONT-04 | *"Obrigado, paciente 1.263. O ciclo continua."* → nota informando que o padrão onírico é dispositivo | *"Obrigado, paciente 1.263. O ciclo continua."* → rotas |

Nos dois casos o último som passa a ser o do texto, não o do editor pedindo
licença.

## 5. Balanço

| Edição | Notas antes | Depois | Em CONT |
|---|---|---|---|
| PT | 13 | 9 | 0 |
| EN | 17 | 10 | 1 (CONT-11) |
| ZH | 16 | 10 | 1 (CONT-11) |

As notas de MEM e DOC permanecem: são de natureza documental/arquivística,
não caem no clímax, e várias estão sob proveniência.

> **Ressalva.** A assimetria entre idiomas (PT tinha 4 notas em CONT, EN 8,
> ZH 7) é mais um caso da divergência trilíngue registrada como limitação
> aberta desde o R398.

## 6. Guarda

`test_r384` foi reescrito. O teste antigo fixava a **presença** da nota em
CONT-03 --- exatamente o que este ciclo remove. Os dois novos travam a
política:

1. `test_cont03_conserva_a_substancia_da_nota_fora_do_climax` --- CONT-03 não
   pode ter `\NE`, tem de conservar o fecho da indução, e o aviso tem de
   conter a substância migrada.
2. `test_nenhum_fragmento_de_contaminacao_interrompe_a_imersao` --- nenhum
   fragmento CONT, nos três idiomas, pode carregar nota, com CONT-11
   registrada como exceção diegética explícita.

## 7. Critérios de aceitação

1. Nenhuma nota do editor interrompe a família CONT, salvo a diegética de
   CONT-11. ✔
2. A substância protetiva removida está integralmente no aviso, nos três
   idiomas. ✔
3. Nenhum fragmento sob proveniência foi tocado; testes R360/R384 verdes. ✔
4. Preflight R362 com `--build`: `overall_internal_spec_passed=True`,
   648/648 rotas, zero violações nas cinco edições. ✔
5. Paginação e lombadas atualizadas após a mudança de extensão do aviso. ✔
