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
| `Molambudos_VictoriaRegia` | 435 pp, 160×230 mm, PT/EN/ZH, capa, ISBN; PDF canônico `3378f438` |
| `Molambudos_v2` | excluído definitivamente em 2026-11-05; 57 pp, 7 degraus, conteúdo único |
| `Molambudos_v2_Diario` | excluído definitivamente em 2026-11-05; 49 pp, Partes I–II ilustradas |
| `template antigo` | excluído definitivamente em 2026-11-05; 4 capítulos incompletos |

O `book.json` aponta para a edição KDP PT-BR. A escolha da edição canônica é
editorial e pertence ao autor. O PDF antigo `77aabe2e` foi substituído pelo
build corrigido `3378f438` e excluído na limpeza autorizada; o hash permanece
em `reports/r1073/`. Release local:
`literatura/molambudos/release/2026-11-05/`.

Atualização R1074: EPUB de leitura validado localmente; preflight KDP com
**status FAIL** (capa a ~163 DPI, reserva de barras 2,15×0,95 in e posição
inferior esquerda). Não enviar à KDP sem corrigir. Ver `reports/r1074/README.md`.

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
4. **EPUB**: R1074 gerou EPUB de leitura a partir dos 84 fragmentos; falta
   EPUBCheck e revisão humana. O antigo EPUB v1.5 foi excluído.
5. **PDF tagged/acessibilidade**: ausente; tentativa R1074 bloqueada pelo
   toolchain (`luaotfload`/`tagpdf`).
6. **KDP preflight**: R1074 mediu; capa em FAIL (163 DPI e área de barras).
   Ver `reports/r1074/README.md`.

## 9. Limites

- Nenhum texto foi reescrito nesta rodada; apenas metadados e aspas.
- QA técnico não avalia voz, ritmo, verossimilhança, ética ou mérito literário.
- O conteúdo do livro está gitignored; nenhum PDF/manuscrito foi versionado.
- Nenhuma validação externa, publicação ou aprovação de banca.
