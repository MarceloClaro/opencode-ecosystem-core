# evo-52 — R421: Exportação DOCX do artigo RBEP

## Objetivo

Atender ao pedido do usuário de compilar o artigo em DOCX, com formatação
ABNT adequada ao periódico-alvo (RBEP) e auditabilidade de artefato.

## Mudanças

1. **Script `scripts/export_docx_rbep.py`** com fluxo reprodutível:
   - gera `reference_abnt.docx` a partir do default do pandoc, com margens
     ABNT (esq/sup 3 cm; dir/inf 2 cm), página A4, Times New Roman 12 e
     espaçamento 1,5;
   - converte o MD canônico com `pandoc --reference-doc` + TOC (2 níveis);
   - pós-processa com python-docx (margens garantidas, fontes dos estilos,
     bordas "Table Grid" em todas as tabelas);
   - escreve `MANIFEST.json` com sha256 do MD, DOCX e reference.
2. **Artefato** `outputs/docx/ARTIGO_RBEP_SUBMISSAO.docx`:
   - margens ABNT verificadas (3,0/3,0/2,0/2,0 cm);
   - 14 tabelas com bordas (11 do corpo + 3 do glossário A.1/A.2/A.3);
   - conteúdo crítico presente (Apêndice A, códigos WDI, ρ 0,751/0,146,
     Δ 0,604, LOOCV, GroupKFold).
3. **Testes R421** (11): existência do script/DOCX/MANIFEST, sha256 do
   manifest, margens, A4, nº de tabelas, Tabela 8 (Brasil), tabelas do
   glossário, conteúdo crítico, apêndice após referências.

## Verificação

- Suíte R408–R421: **334 testes passed** (R421: 11).
- DOCX: 30 KiB, 108 parágrafos, 14 tabelas, margens ABNT confirmadas.
- Doctor: 10/12 pass, 0 failed (warns pré-existentes).

## Lições

- Pandoc + reference.docx + pós-processamento python-docx é suficiente para
  DOCX ABNT sem depender de LibreOffice; o `--print-default-data-file
  reference.docx` permite personalizar estilos de forma idempotente.
- O MANIFEST com sha256 fecha a cadeia de proveniência também para o
  artefato de submissão Word.
