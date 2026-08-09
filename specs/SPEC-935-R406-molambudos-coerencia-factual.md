---
spec_id: SPEC-935-R406
title: Molambudos — contradição de cânone na edição de referência e verificador de coerência factual
component: scripts/molambudos_canone.py, projetos/molambudos/Molambudos_VictoriaRegia
status: verified
test_file: tests/test_r406_molambudos_coerencia_factual.py
---

# SPEC-935-R406 — Coerência Factual entre as Três Edições

**Data:** 2026-08-08
**Motivação:** perguntado se os miolos estavam publicáveis com o rigor de uma
obra literária, o diagnóstico foi que a verificação até então era **reativa** —
as contradições apareciam por acaso, ao medir outra coisa. Uma varredura
sistemática foi então executada, e achou mais uma. Em seguida: *"corrija com
precisão todas as contradições e incoerências das três edições"*.

## 1. A contradição estava na edição de referência

`fragmentos/doc/DOC-07.tex` encerrava com:

> *P.S.: Dr. Heitor Oliveira faleceu em 1981, dois anos após assinar este
> laudo. A causa oficial foi infarto.*

Isso colide com quatro pontos do cânone:

| Fonte | Afirma |
|---|---|
| LUC-07, LUC-14 | desapareceu em **13 de junho de 1979**; o carro foi achado três semanas depois; nunca localizado |
| DOC-25 | *"O paciente 1.261 não desapareceu. Ele foi **guardado** para o momento da entrega."* |
| DOC-26 | escrevendo até **janeiro de 2026**; entrega o diário no arquivo aos 81 anos |
| DOC-07 (o próprio) | o laudo é de **14 de abril de 1979** — o sumiço foi dois *meses* depois, não dois anos |

O elo quebrado é o central: Oliveira é a ponte entre Joaquim e Lúcia. Se ele
morre em 1981, o diário não chega em 2026 e o ciclo não fecha.

**Agravante:** o P.S. existia **apenas em português**. As três edições
contavam finais diferentes para o mesmo personagem.

### 1.1 Correção

O P.S. foi reescrito preservando o que nele era bom — a anotação do colega na
margem, que é temática: num livro em que a criatura **é** a fome, deixar de
senti-la é o sinal de que ela já tomou o corpo.

> *P.S.: Dr. Heitor Oliveira desapareceu em 13 de junho de 1979, dois meses
> após assinar este laudo. O processo de desaparecimento nunca foi encerrado.
> Na ficha funcional do hospital, um colega anotou, à mão, na margem: "Ele
> parou de comer três semanas antes. Dizia que não sentia mais fome — e isso,
> disse ele, era o pior sintoma de todos."*

O P.S. equivalente foi acrescentado às edições inglesa e chinesa, que não o
tinham. `1981` desapareceu da obra.

## 2. O problema de método, e o que o substitui

Ter contradições não era o defeito principal — o defeito era **só encontrá-las
por acaso**. A de 1989 na edição chinesa apareceu enquanto se mediam razões de
caracteres; a de 1981 apareceu numa varredura feita porque o autor perguntou
sobre rigor.

`scripts/molambudos_canone.py` substitui a sorte por verificação:

```
python3 -m scripts.molambudos_canone          # relatório; sai != 0 se houver problema
python3 -m scripts.molambudos_canone --json   # saída estruturada
```

Três eixos:

1. **14 fatos-âncora afirmados** — cada um tem de aparecer nas três edições:
   origem em 1853; Joaquim nasce em 1907, entra no Colônia em 1917, morre em
   1979 aos 72; Colônia fecha em 1980; ciclo de 62; Oliveira desaparece (não
   morre) em 13/jun/1979 e entrega o diário aos 81; investigação em 2026;
   leitor é 1.263; os três CRM.
2. **4 afirmações proibidas** — Oliveira morto em 1981; Oliveira morto em
   1989; leitor tratado pelo número de Oliveira; Lúcia com registro de
   psicóloga (CRP).
3. **Paridade de datas** — um ano citado numa edição tem de existir nas
   outras. Mais a checagem de que nenhum CRM fora do conjunto canônico
   aparece.

### 2.1 A armadilha do `\b` em CJK, documentada no código

Em chinês o ano vem colado ao caractere 年, que o módulo `re` trata como
caractere de palavra. Um `\b` no fim do padrão **nunca casa**, e foi assim que
uma medição anterior "perdeu" 17 anos na edição chinesa e quase levou a
corrigir fragmentos íntegros. `ANO_RE` usa `(?<!\d)…(?!\d)`, e o motivo está
escrito no código para não se repetir.

### 2.2 O verificador foi provado, não apenas escrito

Cada contradição corrigida foi **reintroduzida** e o verificador teve de
acusá-la:

| Injetado | Resultado |
|---|---|
| `faleceu em 1981` em PT | contradição em pt + data sem paridade em en,zh |
| `1989年去世` em ZH | contradição em zh + data sem paridade em pt,en |
| `CRP-MG 4.152` em EN | contradição em en |

Restaurados os arquivos, volta ao verde. Um verificador que não falha quando
o defeito volta é decoração.

## 3. Estado após o ciclo

| Métrica | Valor |
|---|---|
| Fragmentos por edição | 84 / 84 / 84 |
| Anos distintos, todos com paridade | 45 |
| Contradições | **0** |
| Registros CRM | Lúcia 28.391 · Oliveira 4.892 · Torres 3.117 |
| Cadeia de pacientes | 1.259 → 1.263, íntegra |
| Chaves LaTeX desbalanceadas | 0 |
| Selo | 252 folhas (as três edições) |

## 4. O que este ciclo **não** resolve

O verificador cobre **fatos**, não prosa. Continuidade factual passa a ter
guarda automatizada; registro, ritmo e naturalidade das traduções continuam
exigindo revisor nativo — e num texto que depende de indução, o ritmo carrega
metade do efeito.

O conjunto de âncoras é finito e escrito à mão: ele prova a ausência das
contradições que conhece, não a ausência de todas. Cada nova contradição
encontrada deve virar uma linha em `AFIRMADOS` ou `PROIBIDOS`.

## 5. Critérios de aceitação

1. Nenhuma afirmação contradizendo o cânone em nenhuma das três edições. ✔
2. O P.S. de DOC-07 existe nas três edições, com a mesma informação. ✔
3. Todos os anos citados têm paridade entre edições. ✔
4. Nenhum CRM fora do conjunto canônico. ✔
5. O verificador acusa cada contradição reintroduzida, apontando edição e
   arquivo. ✔
6. O limite do método fica declarado: verifica fatos, não qualidade de
   tradução. ✔
