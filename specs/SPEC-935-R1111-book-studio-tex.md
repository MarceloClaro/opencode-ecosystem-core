# SPEC-935-R1111 — Book Studio Universal: TeX, tipografia e revisão rigorosa

**Status:** fase TeX + revisão implementada e verificada (R1111)
**Data:** 2026-11-12
**Base:** R1071 (Book Studio) e R1078 (Book Studio Universal, fase 0)
**Objetivo:** tornar o Book Studio um editor universal de livros: diagramação
TeX de qualidade editorial, compilação PDF reproduzível, QA técnico nativo e
gate de revisão literária rigorosa (PT-BR), sem publicar e sem declarar
qualidade que não foi verificada.

## 1. Não objetivos

- Não publicar, enviar à KDP, distribuir ou vender.
- Não declarar PDF/X, PDF/UA pleno, Qualis, nota ou aceite editorial.
- Não substituir revisão humana, prova de página ou leitura de galerada.
- Não embutir código GPL/AGPL no Core; TeX Live, LanguageTool e afins são
  ferramentas externas invocadas por CLI/HTTP.
- Não reescrever a edição canônica do Molambudos nem variantes existentes.
- Não usar `shell-escape` em compilação de manuscrito não confiável.

## 2. Contexto e lacuna

O Book Studio já possui manifesto (`book.json`), contratos, calculadora KDP,
design tokens, gate de licença, EPUB e CLI (`status`, `init`, `build`, `qa`).
O diagnóstico de 2026-11-12 mostrou `status=blocked`: nenhum motor Typst,
Pandoc, WeasyPrint, LaTeX ou ferramenta de QA (`pdfinfo`, `pdffonts`) estava
instalado. A fase R1078 permaneceu em contratos e evidências externas.

Decisão do operador: instalar **TinyTeX** em espaço de usuário (sem `sudo`) e
**LanguageTool** com JRE em espaço de usuário. O Core não incorpora os
binários; apenas os orquestra.

## 3. Requisitos

| ID | Requisito | Critério de aceitação |
|---|---|---|
| R1 | Design tokens de livro | `BookDesign` versionado com página (trim, margens espelhadas, bleed), tipografia (famílias, corpo, entrelinha, grid), títulos, legendas, tabelas, figuras e cores; serializa para JSON e para LaTeX/Typst |
| R2 | Classe/template TeX | Template `memoir` + LuaLaTeX com `fontspec`, `microtype`, `babel` pt-BR, `biblatex`/`biber`, `hyperref`, `booktabs`, `graphicx`, `tikz`, `makeidx`; capitulares, running heads, folios e controle de viúvas/órfãs |
| R3 | Build reproduzível | `book build --engine latex` chama `latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build`; falha com mensagem acionável se o motor faltar; sem rede e sem shell-escape |
| R4 | QA de PDF nativo | Fallback com `pypdf` para páginas, trim, metadados, fontes embutidas e texto; usa `pdfinfo`/`pdffonts`/`qpdf`/`gs` quando existirem; nunca converte QA em aprovação editorial |
| R5 | QA de log TeX | Detecta `Overfull/Underfull \\hbox`, referências/citações ausentes, fontes não encontradas e erros de `biber`; reporta arquivo/linha e trecho |
| R6 | Gate literário nativo | Regras PT-BR: aspas/travessão/reticências, pontuação de diálogo, repetições, muletas, frases longas, consistência de nomes/timeline/POV e legibilidade; cada achado tem trecho, regra, severidade e confiança |
| R7 | LanguageTool externo | Cliente HTTP local (`http://127.0.0.1:8081/v2/check`) com idioma `pt-BR`; se o servidor não estiver ativo, o relatório declara indisponibilidade e continua com o gate nativo |
| R8 | Proveniência | SHA-256 de manuscrito, template, tokens e PDF; versões de motor/ferramentas; `ReleaseManifest`; nenhum segredo no relatório |
| R9 | Testes | Testes unitários de tokens, escape LaTeX, geração de template, QA com PDF sintético e regras de revisão; teste de integração compila um livro de 3 capítulos quando `latexmk` existe, e é `skip` explícito quando não existe |
| R10 | Anti-overclaim | Todo relatório declara limites: QA técnico não avalia estética, voz ou adequação editorial; PDF/UA e PDF/X exigem validação externa |

## 4. Design editorial padrão

- Trim: **160 × 230 mm** (KDP-friendly), bleed 3 mm quando impressão.
- Margens espelhadas: interna maior que externa; superior/inferior com folga
  para running head e folio.
- Grid: corpo 10,5–11 pt, entrelinha 14–15 pt, baseline grid consistente.
- Fontes: Libertinus Serif (corpo), Libertinus Sans (títulos) e
  Libertinus Mono (código), com fallback para TeX Gyre/EB Garamond.
- Figuras: `Numbers=OldStyle`, `Ligatures=TeX`, `SmallCapsFont`; microtype com
  protrusão e expansão; hifenização pt-BR.
- Títulos de capítulo em página ímpar, sem cabeça; running heads com título do
  livro (verso) e capítulo (reto); folios externos.
- Tabelas com `booktabs`; legendas com `caption`; figuras com `graphicx`.
- Metadados PDF: Title, Author, Subject, Keywords, Creator, Language.
- Acessibilidade: estrutura de livro, idioma `pt-BR`, alt text quando houver
  figura; PDF/UA somente com validador externo.

## 5. Arquitetura

```
marceloclaro/bookstudio/
  design.py     # BookDesign, tokens de página/tipografia, export JSON/TeX/Typst
  tex.py        # geração do projeto LaTeX (classe, preâmbulo, chapters)
  qa.py         # QA nativo (pypdf) + externos opcionais + log TeX
  review.py     # gate literário nativo + cliente LanguageTool
  cli.py        # comandos book design/init/build/qa/review
marceloclaro/book_studio.py  # build existente, integração com design/QA
publishing/templates/book/   # template canônico e exemplo
tests/test_r1111_*.py        # unitários e integração
```

## 6. Critérios de aceitação

1. `python3 -m pytest tests/test_r1111_book_design.py -q` passa.
2. `book status` deixa de retornar `blocked` quando `latexmk`/`lualatex`
   estão no PATH; retorna versões e caminho.
3. `book build <projeto> --engine latex` produz PDF com trim 160×230 mm,
   páginas > 0, texto extraível e fontes embutidas.
4. `book qa <pdf> --trim 160x230mm` retorna `issues` vazios para o demo e
   lista limitações explicitamente.
5. `book review <manuscrito>` retorna achados nativos; com LanguageTool ativo,
   acrescenta achados gramaticais e declara a versão do servidor.
6. Nenhum relatório usa "aprovado", "10/10", "PDF/UA certificado" ou
   "publicável" sem validação externa.

## 7. Riscos

| Risco | Mitigação |
|---|---|
| TinyTeX não cobre pacote usado | `tlmgr install` explícito; teste de compilação no CI |
| Fonte ausente no sistema | usar fontes do TeX Live; fallback documentado |
| LanguageTool pesado/instável | servidor local opcional; gate nativo continua |
| Falso positivo gramatical | trecho + confiança + revisão humana obrigatória |
| PDF/UA incompleto | declarar limite; validador externo separado |
| Vazamento de token em log | nunca logar headers; chaves só em env |

## 8. Definição de pronto

A fase está pronta quando o demo de 3 capítulos compila em PDF 160×230 mm com
fontes embutidas, o QA nativo reporta sem issues, o gate nativo encontra e
explica achados em um texto de teste, e a suíte R1111 passa — sem publicação,
sem certificação e com limites declarados.

## 9. Evidência da implementação (2026-11-12)

| Item | Resultado |
|---|---|
| TinyTeX | TeX Live 2026, LuaHBTeX 1.24.0, latexmk 4.89 e biber 2.22 em `~/.TinyTeX` |
| Fontes | Libertinus Serif/Sans/Mono OTF instaladas; fallback TeX Gyre/Latin Modern disponível |
| Template | `memoir` + LuaLaTeX + `fontspec` + `microtype` + `babel` pt-BR; `biblatex`/`biber` e `makeidx` opcionais |
| Demo de fumaça | 10 páginas, 160×230 mm, 2 fontes embutidas, 441 caracteres, QA sem issues |
| Demo via CLI | 6 páginas, 160×230 mm, fontes embutidas, QA sem issues |
| Testes | 15/15 em `tests/test_r1111_book_design.py`; 36 passed + 3 skipped na regressão R1071/R1078 |
| LanguageTool | 6.6, pt-BR, servidor local em `127.0.0.1:8081`; amostra com 1 erro, 6 avisos e 7 informativos |
| QA | `pypdf` 6.14.2 nativo; `pdfinfo`/`pdffonts` ausentes, fallback exercitado |
| Limites | QA não é aprovação editorial; LanguageTool é externo; PDF/UA e PDF/X não certificados |

Comandos verificados:

```bash
python3 -m marceloclaro.book_studio design /tmp/livro --title "Livro" --author "Autor"
python3 -m marceloclaro.book_studio tex /tmp/livro --clean
python3 -m marceloclaro.book_studio review /tmp/texto.txt --languagetool
```

