# SPEC-935-R1073 — Revisão final, release e quarentena do Molambudos

**Status:** implementado e validado localmente; nenhuma publicação, envio à KDP
ou validação externa.
**Objetivo:** concluir o projeto Molambudos separando a edição canônica das
edições alternativas e dos builds superados, com release local verificável e
quarentena reversível.

## 1. Requisitos

| ID | Requisito | Critério de aceitação |
|---|---|---|
| R1 | Promover o PDF canônico corrigido | `main_kdp_pt_160x230mm.pdf` com SHA-256 `3378f438d1124432b1b67fdf29161363e28276bb4a754c2a070bf5b054d56f4b`, 435 pp, 160×230 mm, metadados completos |
| R2 | Preservar o PDF antigo | SHA-256 `77aabe2e4e055d7f53fbef17dd3857e561f50f556a94f92da0d3ff039f4ea66f` em `_descarte/2026-11-05/`, não no caminho canônico |
| R3 | Criar release local | `release/2026-11-05/` com PDFs PT/EN/ZH/TRI, capas, `metadata.json`, `SHA256SUMS.txt` e `RELEASE_NOTE.md` |
| R4 | Quarentena reversível | `Molambudos_v2`, `Molambudos_v2_Diario`, `_archive`, layouts antigos, build, backups, rascunhos e template antigo com manifesto e hash por arquivo |
| R5 | Não apagar conteúdo único | v2, Diário, EPUB v1.5, backups e template permanecem recuperáveis; exclusão definitiva exige decisão editorial |
| R6 | Atualizar catálogo | entradas de v2, Diário e template com `archived: true`, status de quarentena e caminho em `_descarte` |
| R7 | Registrar parecer | `REVISAO_FINAL.md` com método, achados, riscos e decisão de acervo |
| R8 | Gate verificável | `tests/test_r1073_molambudos_release.py` valida manifesto, catálogo e release local (com skip quando o conteúdo gitignored não existe) |

## 2. Entregáveis

| Caminho | Papel |
|---|---|
| `literatura/molambudos/REVISAO_FINAL.md` | parecer editorial e decisão de acervo |
| `literatura/molambudos/release/2026-11-05/` | pacote local de release |
| `literatura/molambudos/_descarte/2026-11-05/` | quarentena reversível + `manifest.json` + `files.jsonl` |
| `reports/r1073/README.md` | relatório versionado da operação |
| `reports/r1073/manifest_quarentena.json` | resumo versionado com hashes de árvore |
| `reports/r1073/RELEASE_NOTE.md` | nota do release |
| `reports/r1072/catalogo.json` | catálogo atualizado |
| `tests/test_r1073_molambudos_release.py` | gate de integridade |

## 3. Decisões editoriais

- A canônica é a única edição com arco completo (435 pp, 84 fragmentos +
  `EPI-01`) e aparato de publicação.
- `Molambudos_v2` (57 pp) e `Molambudos_v2_Diario` (49 pp) não são cópias
  literais da canônica: a similaridade parágrafo a parágrafo é baixa e ambas
  têm conteúdo único (sete degraus/ensaio; ilustrações e capas).
- Por isso vão para quarentena, não para exclusão permanente.
- O template de 25 pp é superado e vai para quarentena.
- Builds antigos, layouts não-KDP e backups vão para quarentena por proveniência.
- Apenas artefatos de teste e auxiliares regeneráveis foram apagados.

## 4. Fora de escopo

- Publicação, upload à KDP ou distribuição.
- EPUB corrente, PDF tagged e preflight KDP.
- Leitura humana integral, banca, leitura beta ou validação externa.
- Exclusão definitiva da quarentena.

## 5. Limites

O gate verifica integridade de arquivos e consistência de catálogo. Ele não
avalia mérito literário, qualidade de voz, ética da representação ou adequação
comercial. Essas decisões permanecem humanas.
