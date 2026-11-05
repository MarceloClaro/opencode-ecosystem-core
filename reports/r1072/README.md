# R1072 — Hub dos projetos literários

**Status:** hub local criado; nenhum original foi movido. `projetos/` é
gitignored, então o conteúdo das obras permanece fora do versionamento.
**Objetivo:** organizar Molambudos e os demais projetos literários em uma única
entrada para auditoria, revisão, build e QA.

## 1. Estrutura

```text
projetos/literarios/
├── README.md
├── catalogo.json
├── CHECKLIST_AUDITORIA.md
├── molambudos/
│   ├── victoria-regia      -> edição KDP PT-BR, 435 pp
│   ├── v2                  -> esboço de 57 pp
│   ├── diario              -> Diário de 49 pp
│   └── template-antigo     -> template de 25 pp
├── livros/
│   ├── livro-opencode-*    -> fonte + compilado
│   ├── livro-volume2-*     -> fonte + compilado
│   ├── livro-gemeos-*      -> fonte + compilado
│   └── ia-odontologia-*    -> fonte + template
├── templates/              -> Victoria Regia, Template Livros e templates de livro
├── academicos/             -> contexto acadêmico, fora do escopo literário
└── templates-academicos/   -> templates 12–30, contexto
```

O hub usa **symlinks relativos**. Se um link quebrar, o projeto original pode
ter sido movido; o catálogo indica o caminho de origem.

## 2. Obras canônicas

| ID | Obra | Páginas | PDF |
|---|---|---:|---|
| `molambudos-victoria-regia` | Molambudos — O Diário do Paciente 1.260 (KDP PT-BR) | 435 | `projetos/molambudos/Molambudos_VictoriaRegia/main_kdp_pt_160x230mm.pdf` |
| `livro-opencode` | Engenharia de Ecossistemas Cognitivos: OpenCode Ecosystem | 478 | `templates/projects/livro-opencode/livro-dark.pdf` |
| `livro-volume2` | Volume 2 — Gêmeos Digitais Periodontais: O Framework SUS-Twin | 184 | `templates/projects/livro-volume2/dark.pdf` |
| `livro-gemeos-odontologia` | Gêmeos Digitais Periodontais: O Framework SUS-Twin | 180 | `templates/projects/livro-gemeos-odontologia/dark.pdf` |

As demais entradas são versões alternativas, templates ou contexto acadêmico.
A escolha da edição canônica é editorial e pertence ao autor.

## 3. Como usar

```bash
cd projetos/literarios
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
- Auditoria: `reports/r1071/README.md` e `BOOK_STUDIO_AUDIT.md` local.
- O parecer antigo `REVISAO_MOLAMBUDOS.md` descreve a versão incompleta de 4
  capítulos; não vale para a edição VictoriaRegia.
- `lombada.pdf` isolado é de outro projeto (capa dura); a capa completa atual
  calcula 1,021 in de lombada para 435 pp.

## 6. Catálogo

`reports/r1072/catalogo.json` contém 45 obras com:

- `id`, `title`, `category`, `scope`, `canonical`, `status`;
- `source`, `compiled`, `pdf`, `pdf_pages`, `pdf_page_size`;
- `pdf_sha256`, `pdf_bytes`;
- `links` (symlinks do hub);
- `audit`, `notes`.

Categorias: `livro`, `template`, `academico`, `template-academico`.
Escopos: `literario`, `academico`.

## 7. Limites

- O hub não copia conteúdo; não substitui backup.
- O catálogo é um índice, não uma aprovação editorial.
- QA técnico não avalia voz, ritmo, ética ou mérito literário.
- Nenhuma publicação, envio à KDP ou validação externa.
- O conteúdo literário não é versionado.
