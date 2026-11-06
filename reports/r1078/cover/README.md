# R1078 — Capa KDP, lombada e 300 DPI

**Status:** template e especificações gerados; **arte final não aprovada**.
**Não é upload KDP, não é nova ISBN e não é validação externa.**

## 1. Achado principal

As capas existentes são **SVG vetorial**, sem imagem raster embutida:

- `Molambudos_Capa_Frente_Corrigida.svg` — 1050 × 1485 px;
- `Molambudos_Contracapa_Corrigida.svg` — 1050 × 1900 px.

O “163 DPI” não é uma limitação da arte: é o resultado de exportar o SVG em
1050 px. A frente pode ser re-renderizada em 300 DPI sem upscale. Foi gerada uma
prova em **1890 × 2717 px** (6,299 × 9,055 in a 300 DPI) a partir do SVG.

A contracapa, porém, tem proporção **0,553** (1050/1900), incompatível com o
trim **0,696** (6,299/9,055). Ela precisa de **re-layout**, não de upscale.

## 2. Especificações KDP calculadas

Trim 160 × 230 mm; papel branco; tinta premium color; bleed 0,125 in.

| Páginas | Lombada | Capa completa (in) | Pixels a 300 DPI |
|---:|---:|---:|---:|
| 421 | 0,9881 in | 13,8365 × 9,3051 | 4151 × 2792 |
| **422** | **0,9904 in** | **13,8389 × 9,3051** | **4152 × 2792** |
| 435 | 1,0209 in | 13,8694 × 9,3051 | 4161 × 2792 |

Fórmula: `lombada = páginas × espessura`; `capa = 2 × bleed + 2 × trim + lombada`.
A espessura usada é 0,002347 in/página (premium color, papel branco).

## 3. Template

`molambudos_cover_template_422pp.pdf` — 13,8389 × 9,3051 in, uma página, com:

- frente, lombada e contracapa posicionadas;
- guias de trim em vermelho tracejado;
- margem de segurança de 0,25 in em verde pontilhado;
- área de código de barras de 2 × 1,2 in no canto inferior direito da contracapa;
- rótulo “TEMPLATE — NÃO É ARTE FINAL”.

O template tem **todas as fontes embutidas** (Noto Serif, IPAMincho, Liberation
Serif, DejaVu Sans). A rasterização a 300 DPI resultou em **4152 × 2792 px**.

## 4. Bloqueios reais

1. **Contracapa fora de proporção.** O SVG atual não foi desenhado para
   6,299 × 9,055 in; é preciso re-layout.
2. **Código de barras duplicado.** A contracapa atual traz um ISBN/barcode no
   canto inferior esquerdo; a KDP reserva 2 × 1,2 in no canto inferior direito.
   O código antigo deve sair e a área KDP deve ser respeitada.
3. **Trim 160 × 230 mm não está na lista conservadora de trims KDP.** É preciso
   confirmar no previewer; se a KDP rejeitar, reflow para 6 × 9 in ou 6,14 × 9,21 in.
4. **Arte final e prova física.** O template não substitui a arte aprovada, a
   prova de cor e a conferência de sangria.
5. **ISBN.** Sem nova ISBN para a edição impressa.

## 5. Próximo passo de design

1. Re-layout da contracapa em 6,299 × 9,055 in (ou 6 × 9 in, se o trim mudar).
2. Remover o barcode antigo e reservar a área KDP de 2 × 1,2 in.
3. Exportar a capa completa em PDF vetorial ou 300 DPI (4152 × 2792 px).
4. Rodar preflight de capa: trim, bleed, fontes, imagens, barcode, spine.
5. Só então considerar upload — com nova ISBN e prova física.

## 6. Build reprodutível

O script seguro usa **WeasyPrint + cairosvg + pypdf + pdftoppm**, sem PyMuPDF e
sem svglib:

```bash
python3 reports/r1078/cover/build_cover.py \
  --outdir reports/r1078/cover/build_422 \
  --pages 422
```

Resultado em `build_422/`:

| Artefato | Resultado |
|---|---|
| `molambudos_cover_422pp.pdf` | 13,8389 × 9,3051 in; 1 página; 8 fontes embutidas |
| `molambudos_cover_422pp_guides.pdf` | mesma capa com guias de trim/safe/barcode |
| `front_300dpi.png` | 1890 × 2717 px (300 DPI) |
| `cover_preview_150dpi.png` | prévia de revisão |
| `manifest.json` | especificação, hashes e warnings |
| `SHA256SUMS.txt` | checksums de todos os artefatos |

O PDF de impressão **não** tem guias; o PDF de guias é separado. A contracapa
continua com `contain` e precisa de re-layout; o barcode antigo segue visível no
canto inferior esquerdo.

> O Codex foi acionado para gerar um script alternativo. A revisão está em
> `reports/r1080/codex_cover_review.md`: o rascunho não foi executado porque
> depende de `svglib` (ausente), PyMuPDF (AGPL) e rejeita os `<text>` dos SVGs.

## 7. Arquivos

| Caminho | Conteúdo |
|---|---|
| `kdp_specs.json` | cálculos para 421, 422 e 435 pp |
| `cover/build_cover.py` | build reprodutível com WeasyPrint/cairosvg |
| `cover/build_422/` | PDF de impressão, PDF de guias, frente 300 DPI, prévia e manifesto |
| `cover/molambudos_cover_template_422pp.pdf` | template antigo com guias |
| `/tmp/opencode/molambudos_front_300dpi.png` | prova avulsa da frente em 300 DPI |
