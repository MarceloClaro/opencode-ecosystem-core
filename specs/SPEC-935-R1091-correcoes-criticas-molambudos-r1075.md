# SPEC-935-R1091 — Correções críticas do miolo Molambudos R1075

**Objeto:** `literatura/molambudos/Molambudos_Revisada_R1075/`, a partir do
parecer R1089. Correção editorial do miolo, sem reescrever a voz do romance.

**Objetivo:** remover contradições factuais, anacronismos documentais e defeitos
de navegação que impedem uma leitura crítica de alto nível. O alvo é uma edição
que possa ser avaliada perto do topo de uma rubrica crítica, não uma nota
certificada.

**Não objetivo:** declarar 10/10, Qualis, aceite editorial ou validação
clínica/histórica; reescrever cenas por gosto; regenerar capa/EPUB sem
verificação; substituir leitura humana independente.

## Critérios de aceitação

1. **Cluster dos 62.** Nenhuma passagem do miolo afirma que o diário ficou 62
   anos debaixo da terra. `DOC-01` situa a cova em 1979 e o sepultamento em 62
   dias; `DOC-21` usa “poucos dias”; `CONT-01` usa 62 dias; `MEM-26` usa 64
   anos de posse; `DOC-26` marca o 62 como assinatura, não calendário.
2. **Linha de Lúcia.** O desaparecimento público é 13/05; os retornos de julho
   e setembro são declarados como movimentação sigilosa. A custódia
   2019 → maio → julho → setembro fica explícita em `DOC-20`, `LUC-06`,
   `LUC-12` e `LUC-14`.
3. **Moldura documental.** `DOC-19` não insere Joaquim entre os 60 mil e não
   alega “transcrição autorizada” sem prova; `DOC-05` não usa PTSD em 1979;
   `DOC-07` não usa Eixos DSM nem “cronologia ficcional”; `DOC-12` não cita
   artigos dos anos 80; `DOC-27` não data a anotação em 1916; `DOC-06` corrige
   a dose; `DOC-13` corrige a nota; `DOC-24` uniformiza páginas/fólios.
4. **Navegação.** As 12 linhas de rota em Markdown viram `\rota{}`; o total é
   223; `main.tex` e `como_ler.tex` declaram 223; o Mapa 3 declara Lúcia 26 e
   Contaminação 7; os três grafos são regerados a partir dos 84 fragmentos
   incluídos + epílogo, sem CONT removidos.
5. **Notas de margem.** Nenhuma `\margnota` no modo KDP; a nota de `LUC-13`
   vira nota de rodapé; `main.tex` descreve as anotações como incorporadas aos
   documentos e às notas, não como margens impressas.
6. **Paratextos.** Cuidado oferece saída; Ficha Beta é opcional e sem valor
   clínico; Nota Histórica distingue versão narrativa e instituição histórica;
   Nota do Arquivista separa dor histórica de prontuário ficcional; Glossário
   diz “narrado”; Nota Editorial é posterior a setembro e explica a moldura
   DOC; Ficha Catalográfica usa 2. ed.; Epílogo não fala em diagnóstico
   confirmado e acomoda leitura em tela.
7. **Miolo.** O PDF não inclui capa nem contracapa; o miolo abre na folha de
   rosto e fecha em colofão; o ISBN exibido é `979-8-18-917049-2`; o ISBN
   `978-65-01-23456-7` não aparece no PDF.
8. **Compilação.** `pdflatex` conclui duas passadas sem erro; o PDF tem
   160 × 230 mm, fontes embutidas, texto extraível e nenhuma linha
   `> **↪ Rotas:**`.
9. **Relatório.** `reports/r1091/avaliacao_critica_pos_correcao.md` registra
   rubrica de 10 critérios, evidência antes/depois, o que foi preservado e os
   limites. Não declara nota externa certificada.
10. **Testes.** `tests/test_r1091_molambudos_corrections.py` passa; o teste de
    cobertura R1089 continua passando; os manifestos de PDF são atualizados;
    as regressões de Molambudos passam ou têm falha preexistente documentada.

## Limites

- A correção é editorial e textual; não prova valor literário, venda, prêmio ou
  adequação a uma banca específica.
- A capa é um asset separado; este ciclo corrige o miolo e o colofão, não
  redesenha a capa.
- O EPUB não é regenerado neste ciclo; se o texto mudar, o EPUB fica defasado
  até nova compilação e validação.
- Números históricos continuam atribuídos à bibliografia; não há nova pesquisa
  histórica primária.
