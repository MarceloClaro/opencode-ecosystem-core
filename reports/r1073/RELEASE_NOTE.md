# Molambudos — release local 2026-11-05

Pacote local de revisão e entrega. **Não é upload à KDP, não é publicação e não
substitui o preflight oficial.**

## Conteúdo

- `pdf/Molambudos_PT_160x230mm.pdf` — edição canônica PT-BR, 435 pp.
- `pdf/Molambudos_EN_160x230mm.pdf` — edição EN, 431 pp.
- `pdf/Molambudos_ZH_160x230mm.pdf` — edição ZH, 405 pp.
- `pdf/Molambudos_TRI_160x230mm.pdf` — edição trilingue, 1127 pp.
- `covers/` — capas completas PT, EN e ZH.
- `metadata.json` — metadados e hashes.
- `SHA256SUMS.txt` — checksums.

## QA registrado

- 435 pp; 453,543 × 651,968 pts = 160 × 230 mm.
- 15 fontes, todas embutidas.
- Metadados completos: Title, Author, Subject, Keywords.
- 84 fragmentos + `EPI-01`; 0 grupos de parágrafos duplicados (≥200 caracteres).
- PDF canônico: SHA-256 `3378f438d1124432b1b67fdf29161363e28276bb4a754c2a070bf5b054d56f4b`.

## Não incluído

- EPUB corrente: o único EPUB existente (v1.5) foi excluído na limpeza de
  2026-11-05; não há EPUB corrente.
- PDF tagged / acessibilidade digital.
- Certificado de preflight KDP, PDF/X, sangria ou código de barras.
- Validação externa, banca, leitura beta ou parecer profissional independente.

## Edições alternativas

`Molambudos_v2`, `Molambudos_v2_Diario`, o arquivo histórico, os builds antigos e
o template de 25 pp foram **excluídos definitivamente** em 2026-11-05, por
decisão explícita do autor. O release não depende deles. O registro de hashes
está em `reports/r1073/DELETION.md`, `manifest_completo_exclusao.json` e
`files_excluidos.jsonl`.
