# R1072 — Hub dos projetos literários

**Status:** Molambudos concluído em release local; edições alternativas e
builds antigos excluídos definitivamente em 2026-11-05, por decisão do autor.
`literatura/` e `projetos/` são gitignored, então o conteúdo das obras permanece
fora do versionamento.
**Objetivo:** organizar Molambudos — livro, podcast e auditorias — e os demais
projetos literários em uma única entrada para revisão, build e QA.

## 1. Estrutura

```text
literatura/
├── README.md
├── catalogo.json
├── CHECKLIST_AUDITORIA.md
├── molambudos/
│   ├── victoria-regia      -> edição KDP PT-BR, 435 pp
│   ├── podcast/producao    -> 26 episódios + piloto R550, pacotes, slides, feed e deploy
│   ├── auditorias          -> revisão, banca, cultural-episteme, Book Studio
│   ├── capas               -> frente e contracapa corrigidas
│   ├── scripts/ specs/     -> links para fontes versionadas
│   ├── release/2026-11-05  -> PDFs PT/EN/ZH/TRI, capas, metadados e checksums
│   ├── v2, Diário, template -> excluídos em 2026-11-05; hashes em reports/r1073
│   └── README.md           -> mapa do projeto
├── livros/
│   ├── livro-opencode-*    -> fonte + compilado
│   ├── livro-volume2-*     -> fonte + compilado
│   ├── livro-gemeos-*      -> fonte + compilado
│   └── ia-odontologia-*    -> fonte + template
├── templates/              -> Victoria Regia, Template Livros e templates
├── academicos/             -> contexto acadêmico, fora do escopo literário
└── templates-academicos/   -> templates 12–30, contexto
```

Os projetos literários foram **movidos fisicamente** para `literatura/`.
`projetos/` mantém symlinks de compatibilidade para os caminhos antigos. Os
templates versionados em `templates/projects/livro-*` permanecem no lugar; o
caminho `literatura/livros/.../compilado` aponta para eles por symlink. O podcast
está em `literatura/molambudos/podcast/producao`; `research/producao_real` é o
symlink de compatibilidade.

## 2. Obras canônicas

| ID | Obra | Páginas | PDF |
|---|---|---:|---|
| `molambudos-victoria-regia` | Molambudos — O Diário do Paciente 1.260 (KDP PT-BR) | 435 | `literatura/molambudos/Molambudos_VictoriaRegia/main_kdp_pt_160x230mm.pdf` |
| `livro-opencode` | Engenharia de Ecossistemas Cognitivos: OpenCode Ecosystem | 478 | `templates/projects/livro-opencode/livro-dark.pdf` |
| `livro-volume2` | Volume 2 — Gêmeos Digitais Periodontais: O Framework SUS-Twin | 184 | `templates/projects/livro-volume2/dark.pdf` |
| `livro-gemeos-odontologia` | Gêmeos Digitais Periodontais: O Framework SUS-Twin | 180 | `templates/projects/livro-gemeos-odontologia/dark.pdf` |

As demais entradas são templates, contexto acadêmico ou registros históricos de
edições excluídas. A escolha da edição canônica é editorial e pertence ao autor.

### Release e exclusões

- `literatura/molambudos/release/2026-11-05/` — pacote local com PDFs PT/EN/ZH/TRI,
  capas completas, `metadata.json`, `SHA256SUMS.txt` e `RELEASE_NOTE.md`.
- `Molambudos_v2`, `Molambudos_v2_Diario`, `_archive` do VictoriaRegia, layouts
  antigos, build, backups canônicos, rascunhos e template de 25 pp foram
  **excluídos definitivamente** em 2026-11-05, por decisão explícita do autor.
- Registro completo: `reports/r1073/DELETION.md`,
  `manifest_completo_exclusao.json` e `files_excluidos.jsonl` (hash por arquivo).
- Resumo versionado: `reports/r1073/manifest_quarentena.json` (`state: deleted`).
- Parecer editorial: `literatura/molambudos/REVISAO_FINAL.md` e
  `reports/r1073/REVISAO_FINAL.md`.
- A exclusão é irreversível; o release e o PDF canônico não dependem dos itens
  excluídos.

### Podcast

`Molambudos — Podcast (26 episódios + pacote editorial)`:

- 26/26 episódios `.m4a` + `podcast_R550.m4a` (piloto) em `literatura/molambudos/podcast/producao/audio/`.
- Pacotes editoriais, slides (15 pp), infográficos, mapa mental, feed, trailer
  e deploy em `literatura/molambudos/podcast/producao/`.
- Produção NotebookLM; EP26 inclui MEM-26 + material de epílogo.
- Nenhuma publicação automática; deploy exige autorização.

## 3. Como usar

```bash
cd literatura
cat catalogo.json | python3 -m json.tool | less

cd molambudos/victoria-regia
python3 -m marceloclaro.book_studio status .
python3 -m marceloclaro.book_studio build . --engine latex --timeout 300
```

Regenerar o hub após mover/adicionar projetos:

```bash
python3 scripts/build_literary_hub.py
```

## 4. Auditoria

Checklist versionado: `reports/r1072/CHECKLIST_AUDITORIA.md`.

Ordem mínima por obra:

1. identidade e metadados;
2. trim e contagem de páginas;
3. fontes embutidas;
4. sumário/bookmarks/estrutura;
5. duplicações, aspas/dashes, viúvas/órfãs;
6. imagens, sangria e legendas;
7. capa/lombada/barcode/ISBN;
8. EPUB e acessibilidade;
9. preflight (PDF/X quando exigido);
10. leitura humana de galerada.

## 5. Molambudos

- Edição canônica: `molambudos/victoria-regia` (435 pp, 160×230 mm).
- Book Studio: `book.json`, `engine=latex`, `source=main_kdp_pt_160x230mm.tex`.
- PDF canônico promovido em 2026-11-05: SHA-256
  `3378f438d1124432b1b67fdf29161363e28276bb4a754c2a070bf5b054d56f4b`
  (435 pp, metadados completos, 15 fontes embutidas).
- PDF antigo `77aabe2e4e055d7f53fbef17dd3857e561f50f556a94f92da0d3ff039f4ea66f`
  excluído definitivamente; hash preservado em `reports/r1073/`.
- Auditoria: `reports/r1071/README.md`, `reports/r1073/README.md` e
  `BOOK_STUDIO_AUDIT.md` local.
- Revisão editorial e decisão de acervo: `REVISAO_FINAL.md`.
- O parecer antigo `REVISAO_MOLAMBUDOS.md` descreve a versão incompleta de 4
  capítulos; não vale para a edição VictoriaRegia.
- `lombada.pdf` isolado é de outro projeto (capa dura); a capa completa atual
  calcula 1,021 in de lombada para 435 pp.
- O podcast está em `literatura/molambudos/podcast/producao/`; `research/producao_real`
  é mantido como symlink de compatibilidade.
- Release local: `literatura/molambudos/release/2026-11-05/`.

## 6. Catálogo

`reports/r1072/catalogo.json` contém 46 registros (43 ativos + 3 excluídos)
com:

- `id`, `title`, `category`, `scope`, `canonical`, `status`;
- `source`, `compiled`, `pdf`, `pdf_pages`, `pdf_page_size`;
- `pdf_sha256`, `pdf_bytes`;
- `links` (symlinks do hub);
- `archived` (fora do acervo ativo);
- `deleted` (exclusão definitiva autorizada, quando aplicável);
- `audit`, `notes`.

Categorias: `livro`, `podcast`, `template`, `academico`, `template-academico`.
Escopos: `literario`, `academico`.

## 7. Limites

- O hub não copia conteúdo; não substitui backup.
- O catálogo é um índice, não uma aprovação editorial.
- QA técnico não avalia voz, ritmo, ética ou mérito literário.
- Nenhuma publicação, envio à KDP ou validação externa.
- O conteúdo literário não é versionado.
- A exclusão foi definitiva e autorizada; os hashes permanecem em
  `reports/r1073/`. Não há restauração dos itens excluídos.
