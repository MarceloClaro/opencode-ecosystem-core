# Molambudos — auditoria do Book Studio

**Data:** 2026-11-05  
**Edição auditada:** `Molambudos_VictoriaRegia`, wrapper KDP PT-BR 160×230 mm  
**Natureza:** auditoria técnica e editorial assistida; não é validação externa,
parecer profissional independente ou aprovação de publicação.

## 1. Versões

| Versão | Estado | Observação |
|---|---|---|
| `Molambudos_VictoriaRegia` | 435 pp, 160×230 mm, PT/EN/ZH, capa, ISBN | edição madura; usada como referência |
| `Molambudos_v2` | 57 pp, 7 degraus | esboço linear distinto, com 112 testes |
| `Molambudos_v2_Diario` | 49 pp | Parte I–II ilustrada |
| `templates/livro/molambudos` | 4 capítulos incompletos | objeto do parecer antigo; não é a edição atual |

A decisão de qual edição é canônica é editorial e pertence ao autor. O
`book.json` do Book Studio aponta para a edição KDP PT-BR.

## 2. QA técnico

- 435 páginas; 453,543 × 651,968 pts = 160 × 230 mm.
- 15 fontes, todas embutidas.
- PDF 1.7; sem criptografia; sem issues técnicos no QA.
- Metadados corrigidos: Title, Author, Subject e Keywords.
- SHA-256 do PDF novo: `3378f438d1124432b1b67fdf29161363e28276bb4a754c2a070bf5b054d56f4b`.
- SHA-256 do PDF antigo: `77aabe2e4e055d7f53fbef17dd3857e561f50f556a94f92da0d3ff039f4ea66f`.

## 3. Estrutura e texto

- 84 arquivos de fragmento + `\fragdef{EPI-01}` para o epílogo.
- MEM: 27; DOC: 27; LUC: 17; CONT: 13.
- 85 `\fragdef` no total; nenhum arquivo de fragmento órfão.
- 55.447 palavras; ~326.677 caracteres extraídos.
- 0 grupos de parágrafos duplicados (≥200 caracteres) no PDF atual.
- 117 ocorrências de `...` (elipses dialógicas; decisão estilística).
- 166 ocorrências de `,→` (marcador de rota; intencional).
- 12 aspas retas corrigidas para curly quotes no `main.tex`; nova extração: 0.
- 1 overfull hbox de 0,32 pt (negligenciável).
- 50 underfull hbox e 272 underfull vbox: exigem inspeção visual de galerada;
  não são, por si, erro de conteúdo.
- `Tagged: no`: PDF não é tagged; isso é um gap de acessibilidade digital,
  não um bloqueio de impressão KDP.

## 4. Motivos e saturação

Contagens no texto atual (case-insensitive):

| Motivo | Ocorrências |
|---|---:|
| cheiro | 162 |
| vala | 123 |
| fome | 103 |
| o ciclo | 82 |
| contamina | 49 |
| olho amarelo | 35 |
| paciente 1.263 | 27 |
| 3:14 | 24 |
| Rasga Mortalha | 15 |

Esses números não são veredito. Eles indicam onde uma leitura editorial deve
decidir se o motivo é condução ou saturação. O parecer antigo recomendava no
máximo três usos para símbolos fortes; a edição atual tem 35 usos de "olho
amarelo". A decisão exige leitura corrida e não deve ser automatizada.

## 5. Capa e impressão

- Capa completa recompilada: 13,871 × 9,305 in.
- Lombada calculada para 435 pp em cor premium: 1,021 in.
- O PDF `lombada.pdf` isolado tem 1,404 in e é de outro projeto (capa dura);
  **não usar** como lombada desta brochura.
- O template KDP deve ser conferido no preflight oficial; o Book Studio não
  certifica PDF/X, sangria ou código de barras.

## 6. Gaps e prioridades

1. **Galerada humana**: revisar underfull vbox, viúvas/órfãs, abertura de
   páginas e ilustrações em resolução integral.
2. **Edição de voz documental**: revalidar o parecer antigo contra os 84
   fragmentos atuais, especialmente DOC e CONT; não cortar por contagem cega.
3. **Saturação de motivos**: decisão editorial, não automática.
4. **EPUB atual**: a edição VictoriaRegia não tem EPUB corrente; o arquivo no
   `_archive` é v1.5. Gerar um EPUB novo exige fonte única e validação.
5. **PDF tagged/acessibilidade**: ausente; relevante para edição digital.
6. **KDP preflight**: confirmar capa, barcode, bleed, ISBN e página final.

## 7. Limites

- QA técnico não avalia voz, ritmo, verossimilhança, ética ou mérito literário.
- Nenhum texto foi reescrito nesta rodada; apenas metadados e aspas.
- O conteúdo do livro está gitignored; esta auditoria é local.
- Nenhuma validação externa, publicação ou aprovação de banca.
