# R1073 — Revisão final, release e exclusão definitiva

**Data:** 2026-11-05  
**Status:** executado; quarentena excluída definitivamente por decisão explícita
do autor em 2026-11-05.

## Resultado

- PDF canônico promovido ao build corrigido `3378f438d1124432…` (435 pp).
- PDF antigo `77aabe2e4e055d7f…` excluído com a quarentena; hash preservado.
- `15` itens, `2895` arquivos e
  `511.9 MB` excluídos definitivamente.
- `13` artefatos de teste/auxiliares apagados antes da exclusão.
- Release local preservado em `literatura/molambudos/release/2026-11-05/`.
- Nenhum texto literário canônico foi reescrito.

## Itens excluídos

| Categoria | Item | Arquivos | Tamanho |
|---|---|---:|---:|
| `edicao_alternativa` | `molambudos-v2` | 90 | 2.50 MB |
| `edicao_alternativa` | `molambudos-diario` | 88 | 87.44 MB |
| `arquivo_historico` | `victoria-regia-archive` | 2604 | 318.60 MB |
| `pdf_superado` | `layout-main` | 1 | 13.51 MB |
| `pdf_superado` | `layout-main_en` | 1 | 13.50 MB |
| `pdf_superado` | `layout-main_zh` | 1 | 14.80 MB |
| `pdf_superado` | `layout-main_tri` | 1 | 16.05 MB |
| `pdf_superado` | `layout-miolo_kdp_160x230mm` | 1 | 13.93 MB |
| `build_antigo` | `victoria-regia-build` | 8 | 27.24 MB |
| `backup_editorial` | `canon-backup-r398` | 84 | 0.47 MB |
| `backup_editorial` | `archive-canon-r407` | 2 | 0.01 MB |
| `rascunho` | `rascunho-molambudos.md` | 1 | 0.26 MB |
| `rascunho` | `rascunho-molambudos-1.txt` | 1 | 0.01 MB |
| `rascunho` | `rascunho-molambudos_minha_versao.md.bak` | 1 | 0.05 MB |
| `template_superado` | `molambudos-template-antigo` | 11 | 3.50 MB |

## Preservado

- PDF canônico PT-BR 435 pp e traduções EN/ZH/TRI.
- Capas completas, `metadata.json` e `SHA256SUMS.txt` do release.
- Podcast completo (26 episódios + piloto R550).
- Auditorias, parecer editorial, fontes `.tex`, fragmentos canônicos e figuras.
- Manifesto completo e hash por arquivo em `reports/r1073/`.

## Registros

- `DELETION.md` — autorização, escopo e natureza irreversível.
- `manifest_quarentena.json` — resumo com `state: deleted`.
- `manifest_completo_exclusao.json` — manifesto completo anterior à exclusão.
- `files_excluidos.jsonl` — hash de cada um dos 2.895 arquivos.
- `RELEASE_NOTE.md` — nota do pacote de release.
- `REVISAO_FINAL.md` — parecer editorial completo.
- `specs/SPEC-935-R1073-molambudos-release.md` — requisitos e critérios.
- `tests/test_r1073_molambudos_release.py` — gate de integridade.

## Limite

A exclusão é irreversível. Os hashes provam o que existia e foi removido; não
provam mérito literário, aprovação editorial ou validação externa.

## Atualização R1074

- EPUB de leitura gerado da canônica e validado localmente (84 fragmentos, 5
  partes, 0 links quebrados). Ver `reports/r1074/README.md`.
- Preflight KDP local com **status FAIL**: capa a ~163 DPI, reserva de barras
  2,15×0,95 in e posição inferior esquerda. Não enviar à KDP sem corrigir.
- PDF tagged bloqueado pelo toolchain; nenhum PDF/UA produzido.
- Release atualizado em `literatura/molambudos/release/2026-11-05/` com EPUB e
  preflight.
