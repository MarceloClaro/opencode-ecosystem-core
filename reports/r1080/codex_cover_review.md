# Codex — revisão do script de capa gerado

**Status:** execução concluída; script **não executado**.
**Não é arte final, não é upload KDP e não é validação de impressão.**

## 1. Execução

| Item | Valor |
|---|---|
| Ferramenta | `ecosystem_run` com executor `codex` |
| Spec textual | `TSPEC-43c399c2` |
| Tarefa | `task-ce22a7df` |
| Resultado | `success: true`, `status: completed` |
| Duração | ~86 s |
| Modo | `cli-read-only-windows-interop` |
| Passos | 1 |

O Codex devolveu um script Python completo, sem executar a edição. O script
propõe:

- ReportLab + svglib para compor a capa;
- PyMuPDF (`fitz`) para rasterizar a frente e a prévia;
- PDF de impressão e PDF de guias separados;
- `contain` para a contracapa;
- manifesto e `SHA256SUMS.txt`;
- validação de SVG contra `<text>`, `<image>`, `<script>` e referências externas.

## 2. Por que não foi executado

1. **`svglib` não está instalado.** O script falharia no import.
2. **PyMuPDF é AGPL-3.0.** O Core evita essa dependência; a política é usar
   `pypdf`/`pdfplumber`/`cairosvg`/`pdftoppm`.
3. **O script rejeita `<text>`.** A frente tem 22 elementos `<text>` e a
   contracapa tem 89. O script falharia antes de renderizar.
4. **Fontes TTF obrigatórias.** O script exige `--font-title` e `--font-author`;
   nenhuma foi fornecida.
5. **`contain` deixa faixas brancas.** A contracapa atual tem proporção 0,553;
   o painel é 0,696. O `contain` preserva a arte, mas não resolve o re-layout.
6. **Sem CMYK/PDF-X.** O script não faz preflight de cor nem de tinta.

## 3. Decisão

- Codex é útil para **gerar e revisar código**, não para substituir o motor de
  composição.
- A capa de produção continua no **template WeasyPrint** já validado
  (`molambudos_cover_template_422pp.pdf`), com fontes embutidas e guias.
- A versão reprodutível segura está em `build_cover.py`, que usa
  **WeasyPrint + cairosvg + pypdf + pdftoppm**, sem AGPL.
- O script do Codex fica registrado como **rascunho de referência**, não como
  entrega.

## 4. O que o Codex acertou

- Separar PDF de impressão e PDF de guias.
- Calcular SHA-256 e manifesto.
- Recusar `DOCTYPE`, `ENTITY`, `script`, `foreignObject` e referências externas.
- Explicitar que a contracapa precisa de re-layout.
- Não fingir que `contain` resolve a proporção.

## 5. Próximo passo

1. Rodar `build_cover.py` para gerar o PDF sem guias e a prévia.
2. Verificar página, fontes, dimensões e hash.
3. Re-layout da contracapa em 6,299 × 9,055 in.
4. Remover o barcode antigo e reservar a área KDP de 2 × 1,2 in.
5. Só então pensar em prova física e upload.
