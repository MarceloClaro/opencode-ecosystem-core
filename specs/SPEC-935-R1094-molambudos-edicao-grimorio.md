# SPEC-935-R1094 — Molambudos, Edição Grimório (RPG)

**Objeto:** nova edição visual `literatura/molambudos/Molambudos_Grimorio_R1094/`,
derivada da R1075. Não altera a R1075, a R1077, a canônica ou o EPUB.

**Objetivo:** aplicar tipografia e design de RPG/grimório ao romance, preservando
o texto, a ordem dos 84 fragmentos, o epílogo e a ética dos paratextos. O
aparato de mesa é opcional e não substitui a leitura.

**Não objetivo:** criar um RPG jogável, um sistema de regras, nova ISBN, nova
narrativa, publicação ou certificação KDP. Não reescrever cenas para acomodar
dados, fichas ou bestiário.

## Critérios de aceitação

1. **Fonte preservada.** 84 `\fragdef` e 84 `\fragtitle`; o texto dos fragmentos
   é o da R1075; a R1075 permanece intacta (PDF `bd78c8…` e “223 rotas”).
2. **Camada tipográfica.** `yfonts` para iniciais, numerais e título; EB Garamond
   no corpo; paleta preto/dourado/sangue/papel; capitulares góticas; filetes;
   selos; ícone de d20; `tcolorbox`; abertura de parte em página preta.
3. **Aparato de mesa.** Ficha do Paciente 1.263, Protocolo de Mesa, Tabela de
   Rotas d20, verbete da criatura e handouts iconográficos. Todo aparato é
   declarado opcional; não acrescenta fatos novos ao canon.
4. **Ética.** Aviso ao leitor, CVV/CAPS, Nota Histórica e a distinção
   ficção/instituição histórica permanecem. A ficha diz “sem valor clínico”.
   O bestiário é um verbete ficcional, não um stat block jogável.
5. **PDF.** 160 × 230 mm; 380–410 pp; fontes embutidas; texto extraível com
   “PROTOCOLO DE MESA”, “FICHA DO PACIENTE”, “TABELA DE ROTAS”, “A CRIATURA”,
   “PROVA 01” e “EDIÇÃO GRIMÓRIO”; sem `> **↪ Rotas:`; sem “um dos 60 mil”;
   sem o ISBN falso; overfull máximo tolerado de 2 pt.
6. **Capa.** `capa/capa_grimorio.pdf`, 1 página, 160 × 230 mm; arte da capa
   escolhida; título gótico; “EDIÇÃO GRIMÓRIO”; sem ISBN falso e sem “62 anos”
   debaixo da terra. Capa frontal, sem lombada.
7. **Testes.** `tests/test_r1094_molambudos_grimorio.py` passa; o relatório
   `reports/r1094/README.md` registra decisões, páginas de amostra e limites.
8. **Sem overclaim.** O relatório não declara 10/10, qualidade literária
   certificada, aprovação KDP ou prova física.

## Limites

- É uma edição visual/design, não um manual de jogo. As fichas e tabelas são
  aparato de leitura, não um sistema testado em mesa.
- A R1075 continua sendo a edição de leitura/canônica do ciclo; esta edição não
  a substitui.
- A capa é frontal, sem orelhas, lombada ou contracapa; não é um pacote KDP.
- Não houve prova física, revisão tipográfica humana externa ou validação de
  vendas.
