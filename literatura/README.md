# Hub dos projetos literários

**Gerado:** 2026-11-06T02:10:44.080124+00:00  
**Política:** projetos literários físicos em `literatura/`; `projetos/` mantém links de compatibilidade; templates versionados permanecem em `templates/projects`. Conteúdo gitignored.

## Como usar

```bash
cd literatura
cat catalogo.json | python3 -m json.tool | less
cd molambudos/victoria-regia
python3 -m marceloclaro.book_studio status .
python3 -m marceloclaro.book_studio build . --engine latex --timeout 300
```

## Literatura

| ID | Título | Canônico | Estado | Páginas | PDF |
|---|---|:---:|---|---:|---|
| `molambudos-victoria-regia` | Molambudos — O Diário do Paciente 1.260 (KDP PT-BR) | sim | canônico KDP PT-BR; 435 pp; 160×230 mm; PDF 3378f438 | 435 | `literatura/molambudos/Molambudos_VictoriaRegia/main_kdp_pt_160x230mm.pdf` |
| `molambudos-revisada` | Molambudos — O Diário do Paciente 1.260 (edição revista R1075) | — | edição revista e redesenhada; 421 pp; DOC −18,3%; CONT 7; LUC 23; 6 pranchas | 421 | `literatura/molambudos/Molambudos_Revisada_R1075/main_kdp_pt_160x230mm.pdf` |
| `molambudos-print-r1077` | Molambudos — O Diário do Paciente 1.260 (variante print-safe) | — | candidato print-safe; 422 pp; TAC médio 11,7%; imagens ≥300 DPI | 422 | `literatura/molambudos/Molambudos_Print_R1077/main_kdp_print_r1077.pdf` |
| `molambudos-v2` | Molambudos v2.0 — O Prontuário 1.263 (esboço) | — | excluído definitivamente em 2026-11-05; 57 pp; 6×9 in; 112 testes | — | — |
| `molambudos-diario` | Molambudos — Diário 1.260 v2 (Partes I–II) | — | excluído definitivamente em 2026-11-05; 49 pp; 6×9 in; versão ilustrada | — | — |
| `livro-opencode` | Engenharia de Ecossistemas Cognitivos: OpenCode Ecosystem | sim | 478 pp; A4; compilado em templates/projects/livro-opencode | 478 | `templates/projects/livro-opencode/livro-dark.pdf` |
| `livro-volume2` | Volume 2 — Gêmeos Digitais Periodontais: O Framework SUS-Twin | sim | 184 pp; A4; compilado em templates/projects/livro-volume2 | 184 | `templates/projects/livro-volume2/dark.pdf` |
| `livro-gemeos-odontologia` | Gêmeos Digitais Periodontais: O Framework SUS-Twin | sim | 180 pp; A4; compilado em templates/projects/livro-gemeos-odontologia | 180 | `templates/projects/livro-gemeos-odontologia/dark.pdf` |
| `ia-em-odontologia` | IA em Odontologia — livro/template | — | fonte e template; sem PDF compilado no diretório | — | — |

## Podcast

| ID | Título | Estado | Páginas | PDF |
|---|---|---|---:|---|
| `molambudos-podcast` | Molambudos — Podcast (26 episódios + pacote editorial) | 26 episódios + piloto R550; slides, infográficos, feed, trailer e deploy | 15 | `literatura/molambudos/podcast/producao/slides_molambudos.pdf` |

## Release

- `release/2026-11-05/` — PDFs PT/EN/ZH/TRI, capas completas, `metadata.json`, `SHA256SUMS.txt` e `RELEASE_NOTE.md`.
- `release/2026-11-05/epub/` — EPUB de leitura validado localmente (84 fragmentos, 5 partes, 0 links quebrados); fonte e manifesto incluídos.
- `release/2026-11-05/preflight/` — preflight KDP local com **status FAIL**: capa a ~163 DPI, reserva de barras 2,15×0,95 in e posição incorreta para LTR. Não enviar à KDP sem corrigir.
- Edições alternativas, builds antigos e backups foram excluídos definitivamente em 2026-11-05; manifesto e hash por arquivo em `reports/r1073/`.
- Revisão editorial e decisão de acervo: `molambudos/REVISAO_FINAL.md` e `reports/r1073/REVISAO_FINAL.md`.
- EPUB e preflight: `reports/r1074/README.md`.

## Templates literários

| ID | Título | Estado | PDF |
|---|---|---|---|
| `molambudos-template-antigo` | Molambudos — template LaTeX antigo (4 capítulos) | excluído definitivamente em 2026-11-05; 25 pp; template incompleto | — |
| `template-victoria-regia` | Victoria Regia — template clássico LaTeX | template; sem PDF compilado | — |
| `template-livros` | 23_Template_Livros — coleção de templates | coleção de templates; sem PDF único | — |
| `template-livro-opencode` | Template — Livro OpenCode | template com PDF compilado | `templates/projects/livro-opencode/livro-dark.pdf` |
| `template-livro-volume2` | Template — Livro Volume 2 | template com PDF compilado | `templates/projects/livro-volume2/dark.pdf` |
| `template-livro-gemeos` | Template — Livro Gêmeos Odontologia | template com PDF compilado | `templates/projects/livro-gemeos-odontologia/dark.pdf` |
| `template-livro-odontologia-ia` | Template — Livro Odontologia IA | template; sem PDF compilado | — |

## Acadêmicos (contexto, fora do escopo literário)

| ID | Título | Canônico | Estado | Páginas | PDF |
|---|---|:---:|---|---:|---|
| `academico-01-dissertacao-opencode` | Dissertação OpenCode | — | contexto acadêmico; fora do escopo literário | — | — |
| `academico-05-artigo-mit-ia` | Artigo MIT/IA | — | contexto acadêmico; fora do escopo literário | — | — |
| `academico-06-artigos` | Artigos | — | contexto acadêmico; fora do escopo literário | — | — |
| `academico-07-criador-artigo` | Criador de Artigo | — | contexto acadêmico; fora do escopo literário | — | — |
| `academico-08-docs-dissertacao` | Docs da Dissertação | — | contexto acadêmico; fora do escopo literário | — | — |
| `academico-09-md-dissertacao-latex` | Dissertação LaTeX | — | contexto acadêmico; fora do escopo literário | — | — |
| `academico-10-dados-entrada-mestrado` | Dados de Entrada do Mestrado | — | contexto acadêmico; fora do escopo literário | — | — |
| `academico-11-evolve-artigos` | Evolução de Artigos | — | contexto acadêmico; fora do escopo literário | — | — |
| `academico-31-template-ensaio-fichamento` | Template de Ensaio/Fichamento | — | contexto acadêmico; fora do escopo literário | — | — |
| `academico-32-documentos` | Documentos | — | contexto acadêmico; fora do escopo literário | — | — |
| `academico-33-nano` | Nano | — | contexto acadêmico; fora do escopo literário | — | — |
| `academico-34-orchestration` | Orchestration | — | contexto acadêmico; fora do escopo literário | — | — |
| `academico-35-zrm-master` | ZRM Master | — | contexto acadêmico; fora do escopo literário | — | — |

## Templates acadêmicos

| ID | Título | Estado | PDF |
|---|---|---|---|
| `template-academico-12-template-abntex2` | 12 Template ABNTEX2 | template acadêmico; contexto | — |
| `template-academico-13-template-acm` | 13 Template ACM | template acadêmico; contexto | — |
| `template-academico-14-template-artigo` | 14 Template Artigo | template acadêmico; contexto | — |
| `template-academico-15-template-cv-curriculo` | 15 Template CV Curriculo | template acadêmico; contexto | — |
| `template-academico-16-template-dissertacao` | 16 Template Dissertacao | template acadêmico; contexto | — |
| `template-academico-17-template-elsevier` | 17 Template Elsevier | template acadêmico; contexto | — |
| `template-academico-18-template-elsevier-cas` | 18 Template Elsevier CAS | template acadêmico; contexto | — |
| `template-academico-19-template-icmc` | 19 Template ICMC | template acadêmico; contexto | — |
| `template-academico-20-template-ieee` | 20 Template IEEE | template acadêmico; contexto | — |
| `template-academico-21-template-ipleiria` | 21 Template IPLeiria | template acadêmico; contexto | — |
| `template-academico-22-template-koma-script` | 22 Template KOMA Script | template acadêmico; contexto | — |
| `template-academico-24-template-mdpi` | 24 Template MDPI | template acadêmico; contexto | — |
| `template-academico-25-template-nature` | 25 Template Nature | template acadêmico; contexto | — |
| `template-academico-26-template-sbc` | 26 Template SBC | template acadêmico; contexto | — |
| `template-academico-27-template-springer` | 27 Template Springer | template acadêmico; contexto | — |
| `template-academico-28-template-taylor-francis` | 28 Template Taylor Francis | template acadêmico; contexto | — |
| `template-academico-29-template-unb-monografia` | 29 Template UnB Monografia | template acadêmico; contexto | — |
| `template-academico-30-template-usp` | 30 Template USP | template acadêmico; contexto | — |

## Auditoria

- Molambudos: `reports/r1071/README.md`, `reports/r1073/README.md`, `reports/r1074/README.md` e `molambudos/victoria-regia/BOOK_STUDIO_AUDIT.md`.
- Revisão final e decisão de acervo: `molambudos/REVISAO_FINAL.md` e `reports/r1073/REVISAO_FINAL.md`.
- Registro de exclusão definitiva: `reports/r1073/DELETION.md` e `reports/r1073/manifest_quarentena.json`.
- EPUB e preflight KDP: `reports/r1074/README.md`, `epub_manifest.json` e `preflight_kdp.json`.
- O parecer antigo `literatura/molambudos/auditorias/revisao-2026-07.md` descreve a versão de 4 capítulos; não usar para a edição VictoriaRegia.
- Checklist mínimo por obra: metadados, trim, fontes embutidas, TOC/bookmarks, duplicações, aspas/dashes, capa/lombada, EPUB e KDP preflight.

## Limites

- O hub não duplica conteúdo; se um symlink quebrar, o projeto original pode ter sido movido.
- Não há validação editorial automática; QA técnico não substitui leitura humana.
- Nada foi publicado ou enviado à KDP.
