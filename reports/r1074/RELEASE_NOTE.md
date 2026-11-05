# Molambudos — release local 2026-11-05

Pacote local de revisão e entrega. **Não é upload à KDP, não é publicação e não
substitui o preflight oficial.**

## Conteúdo

- `pdf/Molambudos_PT_160x230mm.pdf` — edição canônica PT-BR, 435 pp.
- `pdf/Molambudos_EN_160x230mm.pdf` — edição EN, 431 pp.
- `pdf/Molambudos_ZH_160x230mm.pdf` — edição ZH, 405 pp.
- `pdf/Molambudos_TRI_160x230mm.pdf` — edição trilingue, 1127 pp.
- `covers/` — capas completas PT, EN e ZH.
- `epub/Molambudos_PT.epub` — edição de leitura, 84 fragmentos + epílogo.
- `epub/source/` — Markdown e CSS usados na geração.
- `epub/EPUB_MANIFEST.json` — metadados, hashes e validação estrutural.
- `preflight/` — relatório local de KDP e resumo das falhas.
- `metadata.json` — metadados e hashes.
- `SHA256SUMS.txt` — checksums de todos os arquivos.

## Status

### EPUB

- 84 seções de fragmento, 84 links de fragmento no TOC, 5 partes.
- 105 links no TOC; 0 quebrados; 7 imagens; 0 ausentes.
- 0 comandos LaTeX crus; 0 referências não resolvidas.
- 54.663 palavras (96,9% da extração do PDF canônico).
- SHA-256: `9f7a5ea58f6c1c72cc870e423412843173f004d374644f068a6e1d11b898aabe`.
- Validação estrutural local; **EPUBCheck não está instalado**.

### Impressão KDP

**Status: FAIL — não enviar à KDP ainda.**

Falhas:

1. **Resolução da capa**: arte principal a ~163 DPI; o KDP exige mínimo de
   300 DPI para a capa.
2. **Área de barras**: reserva de 2,15×0,95 in; o requisito adotado é
   2,0×1,2 in.
3. **Posição da área de barras**: reserva no canto inferior esquerdo da
   contracapa; para conteúdo LTR, o KDP posiciona o código no canto inferior
   direito.

Avisos:

- A arte da contracapa contém um código/ISBN fictício
  (`978-65-01-23456-7`); a caixa branca o cobre, mas o elemento deve ser
  removido da arte de origem.
- Páginas 1 e 435 usam imagem de página inteira sem `BleedBox`; confirmar
  sangria ou inserir a arte dentro da área segura.
- 12 imagens do miolo abaixo de 300 DPI (páginas 1, 37, 79, 145, 257, 286, 287,
  288, 299, 339, 361, 435).
- PDF não é tagged (`Tagged: no`); gap de acessibilidade digital.
- Página 435 é branca; confirmar no previewer.

Passes:

- Trim personalizado 160×230 mm aceito pela KDP (faixa 4–8,5 × 6–11,69 in).
- 435 páginas; margens mínimas ≥19,34 pt; 0 violações de 18 pt.
- Fontes do miolo e da capa embutidas; PDF 1.7 sem criptografia.
- Capa 13,8706×9,3051 in; lombada 1,0222 in; sangria 0,125 in.
- ISBN 9798189170492 consistente entre capa e miolo.

### PDF tagged

**Bloqueado pelo toolchain.** LuaLaTeX não carrega `luaotfload-main`; o
pdfLaTeX com `tagpdf` aborta na mudança de versão PDF (2.0→2.6). Nenhum PDF
tagged foi produzido. O EPUB é a entrega de acessibilidade digital desta
rodada. Ver `reports/r1074/tagged_pdf_status.json`.

## Caminho de correção da capa

1. Reexportar a arte da capa e da contracapa a **300 DPI** (ou vetor).
   A maior arte ativa é 1046×1504 px; não há fonte em 300 DPI no projeto.
   Os painéis maiores estavam no `_archive` excluído em 2026-11-05. Se existir
   cópia externa, usá-la; caso contrário, a capa precisa ser recriada.
   Um candidato parcial com a arte limpa e a reserva correta foi gerado em
   `Molambudos_VictoriaRegia/kdp_candidate/`; ele ainda falha a 137 DPI.
2. Remover o código/ISBN fictício de `contracapa.png`.
3. Mover a reserva para o canto inferior direito da contracapa, com
   **2,0×1,2 in**, a 0,25 in das bordas de corte.
4. Recompilar a capa, rodar novamente o preflight e conferir no previewer KDP.
5. Solicitar prova digital e prova física antes de publicar.

## Não incluído

- EPUB com validação EPUBCheck.
- PDF tagged / PDF/UA.
- Certificado de preflight KDP, PDF/X, sangria ou código de barras.
- Validação externa, banca, leitura beta ou parecer profissional independente.
- Publicação, upload ou distribuição.

## Edições alternativas

`Molambudos_v2`, `Molambudos_v2_Diario`, o arquivo histórico, os builds antigos e
o template de 25 pp foram **excluídos definitivamente** em 2026-11-05, por
decisão explícita do autor. O registro de hashes está em
`reports/r1073/DELETION.md`, `manifest_completo_exclusao.json` e
`files_excluidos.jsonl`.
