# R1071 — Book Studio e auditoria do Molambudos

**Status:** implementado e validado localmente. Nenhuma publicação, envio à KDP
ou validação externa.

## 1. Book Studio

O Core agora mantém um projeto de livro com `book.json`, build PDF/EPUB e QA
físico do PDF.

```bash
python3 -m marceloclaro.book_studio status
python3 -m marceloclaro.book_studio init <root> --title ... --author ...
python3 -m marceloclaro.book_studio build <root> --engine typst
python3 -m marceloclaro.book_studio build <root> --engine latex --source main.tex
python3 -m marceloclaro.book_studio qa <pdf> --trim 6x9in
```

Motores: Typst 0.15.1 (padrão), Pandoc 3.7, WeasyPrint 67, LaTeX/latexmk.
Scribus, Vivliostyle e CaSILE permanecem externos; nenhum código GPL/AGPL foi
copiado.

## 2. Molambudos — versões

| Versão | Estado |
|---|---|
| `Molambudos_VictoriaRegia` | 435 pp, 160×230 mm, PT/EN/ZH, capa, ISBN |
| `Molambudos_v2` | 57 pp, 7 degraus, esboço linear |
| `Molambudos_v2_Diario` | 49 pp, Parte I–II ilustrada |
| `literatura/templates/molambudos-antigo` | 4 capítulos incompletos; objeto do parecer antigo |

O `book.json` aponta para a edição KDP PT-BR. A escolha da edição canônica é
editorial e pertence ao autor.

## 3. QA técnico do KDP

- 435 páginas; 453,543 × 651,968 pts = **160 × 230 mm**.
- 15 fontes, **todas embutidas**.
- Metadados corrigidos: **Title, Author, Subject, Keywords**.
- `pdfinfo`: PDF 1.7, sem criptografia, `Tagged: no`.
- QA do Book Studio: **zero issues técnicos**.
- PDF novo: SHA-256 `3378f438d1124432b1b67fdf29161363e28276bb4a754c2a070bf5b054d56f4b`.
- PDF antigo: SHA-256 `77aabe2e4e055d7f53fbef17dd3857e561f50f556a94f92da0d3ff039f4ea66f`.

## 4. Auditoria textual

- 84 arquivos de fragmento + `EPI-01` no epílogo.
- MEM 27; DOC 27; LUC 17; CONT 13; 85 `\fragdef`.
- 55.447 palavras; ~326.677 caracteres extraídos.
- **0 grupos de parágrafos duplicados** (≥200 caracteres).
- 12 aspas retas → curly quotes no `main.tex`; nova extração: **0 aspas retas**.
- 117 `...` e 166 `,→` são marcadores estilísticos intencionais.
- 1 overfull hbox de 0,32 pt (negligenciável).
- 50 underfull hbox e 272 underfull vbox: exigem inspeção de galerada; não são
  erro de conteúdo por si.
- `Tagged: no`: gap de acessibilidade digital, não bloqueio de impressão.

### Motivos

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

Esses números são **indicadores para leitura editorial**, não veredito de
saturação. O parecer antigo recomendava no máximo três usos para símbolos
fortes; a edição atual tem 35 usos de "olho amarelo". A decisão exige leitura
corrida e não deve ser automatizada.

## 5. Capa e impressão

- Capa completa recompilada: **13,871 × 9,305 in**.
- Lombada calculada para 435 pp em cor premium: **1,021 in**.
- `lombada.pdf` isolado tem 1,404 in e é de outro projeto (capa dura); **não
  usar** como lombada desta brochura.
- O Book Studio não certifica PDF/X, sangria, barcode ou aprovação KDP.

## 6. Correções aplicadas

1. `main.tex`: `\hypersetup` com Title/Author/Subject/Keywords.
2. `main.tex`: 12 aspas retas `\textquotedbl{}` → curly quotes.
3. `book.json`: manifesto do projeto KDP.
4. `REVISAO_MOLAMBUDOS.md`: nota de escopo — o parecer antigo não descreve a
   edição VictoriaRegia.
5. `BOOK_STUDIO_AUDIT.md`: auditoria local detalhada (gitignored).

## 7. Testes

```text
tests/test_r1071_book_studio.py
tests/test_r1069_production_center.py
tests/test_r1069_video_qa.py
tests/test_r1069_imagegen.py
tests/test_r640_ecosystem_surface.py
tests/test_transformer.py
tests/test_r212_attention_blackboard.py
tests/test_r640_autonomous.py
tests/test_r644_autonomous_health.py
tests/test_r886_metacognitive_loop.py
tests/test_r1050_metacognitive_gate.py
tests/test_metacognitive_superhuman.py
119 passed
```

## 8. Gaps e prioridades

1. **Galerada humana**: underfull boxes, viúvas/órfãs, aberturas e imagens.
2. **Edição de voz**: revalidar DOC/CONT no texto atual de 84 fragmentos.
3. **Saturação de motivos**: decisão editorial, não automática.
4. **EPUB corrente**: a edição VictoriaRegia não tem EPUB atual; o arquivo no
   `_archive` é v1.5. Gerar um novo exige fonte única e validação.
5. **PDF tagged/acessibilidade**: ausente; relevante para edição digital.
6. **KDP preflight**: capa, barcode, bleed, ISBN e página final.

## 9. Limites

- Nenhum texto foi reescrito nesta rodada; apenas metadados e aspas.
- QA técnico não avalia voz, ritmo, verossimilhança, ética ou mérito literário.
- O conteúdo do livro está gitignored; nenhum PDF/manuscrito foi versionado.
- Nenhuma validação externa, publicação ou aprovação de banca.
