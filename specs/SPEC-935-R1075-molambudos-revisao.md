# SPEC-935-R1075 — Edição revisada do Molambudos

**Status:** em implementação.  
**Objetivo:** produzir uma edição revista do romance, preservando a edição
canônica e aplicando seis mudanças editoriais autorizadas: poda do bloco DOC,
redução do bloco CONT, arco de Lúcia, linha ontológica disciplinada, dosagem do
motivo 62 e variação sintática.

## 1. Decisões editoriais

| ID | Decisão | Critério |
|---|---|---|
| D1 | Bloco DOC cortado em 15–20% | De 18.316 para ≤15.600 palavras; foco em DOC-03, DOC-08, DOC-26/27 e DOC-06 |
| D2 | CONT reduzido de 13 para 7 fragmentos | Manter CONT-01, 03, 04, 05, 07, 09, 13; remover 02, 06, 08, 10, 11, 12 |
| D3 | Lúcia ganha arco próprio | 6 fragmentos novos (LUC-15 a LUC-20): desejo, culpa, família, medo, conivência e escolha |
| D4 | Linha ontológica | Diegese psicológica (trauma, sugestão, contágio narrativo); o único elemento sobrenatural é o ato de leitura do leitor |
| D5 | Motivo 62 dosado | Manter 62 anos/62 dias/62 segundos e a página 62 como assinatura; remover o “manual” de 276 saltos e a explicação mecânica |
| D6 | Sintaxe variada | Reduzir “Não é X. É Y.” nas seções reescritas; usar cena, elipse, silêncio e variação de período |
| D7 | 84 fragmentos preservados | Remover 6 CONT e acrescentar 6 LUC; total permanece 84 |

## 2. Técnicas de imersão

As técnicas abaixo são **retórica narrativa**, não tratamento clínico nem
“controle mental”. Não há alegação de eficácia terapêutica ou científica.

| Técnica | Uso |
|---|---|
| Ancoragem sensorial | Cheiro, temperatura, textura e som recorrentes, em doses controladas |
| Pacing | Períodos curtos, quebras de linha e silêncio para modular velocidade |
| Endereçamento direto | Segunda pessoa restrita a 7 fragmentos CONT |
| Presupposição | “Quando você terminar…”, “depois que você ler…” sem coerção |
| Interrupção de padrão | Documento/laudo quebra a cena e devolve o leitor ao presente |
| Future pacing | O leitor imagina os efeitos pós-leitura; usado com parcimônia |
| Ambiguidade disciplinada | Dentro do livro, explicação psicológica; fora, o ato de ler é o resíduo inexplicável |

## 3. Estrutura revisada

- MEM: 27 fragmentos (sem alteração de contagem).
- DOC: 27 fragmentos, com 5 reescritos/abreviados.
- LUC: 23 fragmentos (17 existentes + 6 novos).
- CONT: 7 fragmentos.
- Total: 84 fragmentos + EPI-01.

## 4. Entregáveis

| Caminho | Papel |
|---|---|
| `literatura/molambudos/Molambudos_Revisada_R1075/` | projeto revisado (fonte LaTeX) |
| `.../build/molambudos_revisado.pdf` | PDF revisado 160×230 mm |
| `.../release/Molambudos_PT_revisado.epub` | EPUB revisado |
| `reports/r1075/README.md` | relatório de mudanças e técnicas |
| `reports/r1075/revision_manifest.json` | contagens antes/depois, hashes e mudanças |
| `tests/test_r1075_molambudos_revision.py` | gate estrutural da revisão |

## 5. Aceitação

1. Canônico `Molambudos_VictoriaRegia` permanece intacto.
2. Projeto revisado compila em PDF 160×230 mm, com fontes embutidas.
3. EPUB revisado tem 84 seções, 5 partes, TOC íntegro e 0 LaTeX cru.
4. DOC revisado ≤15.600 palavras; CONT com 7 fragmentos; LUC com 23.
5. Nenhum fragmento removido aparece no `main.tex` revisado.
6. Relatório declara: sem nova ISBN, sem validação externa, capa/lombada a
   recalcular, traduções não atualizadas.
7. Teste R1075 passa (com skip quando o conteúdo gitignored não existe).

## 6. Fora de escopo

- Publicação, upload à KDP ou distribuição.
- Nova capa em 300 DPI ou novo ISBN.
- Revisão das traduções EN/ZH/TRI.
- Validação por banca externa, leitura beta ou parecer profissional.
- Alegação de que as técnicas de imersão têm eficácia clínica.
